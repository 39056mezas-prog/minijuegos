"""TEST_DATABASE_URL=postgresql://user@host/postgres python3 -m unittest test_app

Creates its own throwaway database on that server and drops it afterwards; it never touches existing data.
"""
import base64, http.cookiejar, io, json, os, re, secrets, sys, threading, unittest, urllib.error, urllib.parse, urllib.request
import psycopg

SERVER = os.environ["TEST_DATABASE_URL"]
NAME = "store_test_" + secrets.token_hex(4)
with psycopg.connect(SERVER, autocommit=True) as s: s.execute(f"CREATE DATABASE {NAME}")
os.environ["DATABASE_URL"] = psycopg.conninfo.make_conninfo(SERVER, dbname=NAME)
os.environ["PAYMENT_DETAILS"] = "Bank of Test, acct 123"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app

def tearDownModule():
    C.close()
    with psycopg.connect(SERVER, autocommit=True) as s: s.execute(f"DROP DATABASE {NAME} WITH (FORCE)")

app.init()
C = app.db()
def user(uid): return C.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
def stock(pid): return C.execute("SELECT stock FROM products WHERE id=?", (pid,)).fetchone()["stock"]
def product(sku, public, member, qty, members_only=0):
    with C:
        return C.execute("INSERT INTO products(sku,name,retail_cents,wholesale_cents,stock,wholesale_only) VALUES(?,?,?,?,?,?) RETURNING id",
                         (sku, sku.title(), public, member, qty, members_only)).fetchone()["id"]

PENDING = app.create_user(C, "pending@x.com", "password123", "Pete", "+1 619 555 0101", "1 Main St", biz_status="pending")
MEMBER = app.create_user(C, "member@x.com", "password123", "Sam", "+1 619 555 0102", "2 Main St", biz_status="approved")
STAFF = app.create_user(C, "staff@x.com", "password123", "Stella", "+1 619 555 0103", role="staff")
with C: DRIVER = C.execute("INSERT INTO drivers(name,phone) VALUES('Dan','+52 646 123 4567') RETURNING id").fetchone()["id"]
ADDR = ("Name", "+1 619 555 0199", "9 Elm St, San Diego")
JPEG = "data:image/jpeg;base64," + base64.b64encode(b"\xff\xd8\xff\xe0" + b"0" * 64).decode()  # magic bytes are what the server checks


class Rules(unittest.TestCase):
    def tearDown(self): C.conn.rollback()

    def test_cents(self):
        self.assertEqual(app.cents("12.5"), 1250)
        self.assertEqual(app.cents("$0.01"), 1)
        for bad in ("abc", "-1", "NaN", ""):
            with self.assertRaises(ValueError): app.cents(bad)

    def test_only_approved_members_order(self):
        pub, members_only = product("charger", 2999, 1800, 10), product("restricted-a", 1000, 500, 10, 1)
        self.assertNotIn(members_only, [p["id"] for p in app.visible_products(C, user(PENDING))])
        for pid in (pub, members_only):  # registered + deposit pending is not enough
            with self.assertRaises(ValueError): app.place_order(C, user(PENDING), {pid: 1}, *ADDR)
        oid = app.place_order(C, user(MEMBER), {pub: 3, members_only: 4}, *ADDR)
        self.assertEqual(C.execute("SELECT total_cents FROM orders WHERE id=?", (oid,)).fetchone()["total_cents"], 3 * 1800 + 4 * 500)
        self.assertEqual((stock(pub), stock(members_only)), (7, 6))

    def test_oversell_rolls_back_whole_order(self):
        a, b = product("a", 100, 50, 5), product("b", 100, 50, 1)
        with self.assertRaises(ValueError): app.place_order(C, user(MEMBER), {a: 2, b: 2}, *ADDR)
        self.assertEqual((stock(a), stock(b)), (5, 1))

    def test_cancel_restocks_once_and_is_final(self):
        a = product("c", 100, 50, 5)
        oid = app.place_order(C, user(MEMBER), {a: 3}, *ADDR)
        app.update_order(C, STAFF, oid, DRIVER, "cancelled", "due_on_delivery", 0)
        self.assertEqual(stock(a), 5)
        with self.assertRaises(ValueError): app.update_order(C, STAFF, oid, DRIVER, "cancelled", "due_on_delivery", 0)
        self.assertEqual(stock(a), 5)

    def test_pay_on_delivery(self):
        oid = app.place_order(C, user(MEMBER), {product("f", 700, 400, 5): 2}, *ADDR)
        o = C.execute("SELECT payment, collect_cents FROM orders WHERE id=?", (oid,)).fetchone()
        self.assertEqual(tuple(o.values()), ("due_on_delivery", 800))
        with self.assertRaises(ValueError): app.update_order(C, STAFF, oid, DRIVER, "delivered", "due_on_delivery", 800)
        with self.assertRaises(ValueError): app.update_order(C, STAFF, oid, DRIVER, "assigned", "due_on_delivery", 801)
        app.update_order(C, STAFF, oid, DRIVER, "delivered", "paid_transfer", 800)

    def test_delivery_pin(self):
        p = product("pin", 1000, 500, 10)
        oid = app.place_order(C, user(MEMBER), {p: 1}, *ADDR, "", 32.715736, -117.161087)
        o = C.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone()
        self.assertEqual((round(o["lat"], 6), round(o["lng"], 6)), (32.715736, -117.161087))
        self.assertIn("Maps: https://www.google.com/maps/search/?api=1&query=32.715736%2C-117.161087", app.dispatch_text(o, []))
        no_pin = app.place_order(C, user(MEMBER), {p: 1}, *ADDR)  # pin is optional; typed address is used
        self.assertIn("query=9%20Elm%20St", app.dispatch_text(C.execute("SELECT * FROM orders WHERE id=?", (no_pin,)).fetchone(), []))
        for bad in ((95.0, 10.0), (10.0, 200.0), (10.0, None)):
            with self.assertRaises(ValueError): app.place_order(C, user(MEMBER), {p: 1}, *ADDR, "", *bad)
        self.assertEqual(stock(p), 8)  # rejected orders took no stock

    def test_typed_and_map_address_both_kept(self):
        p = product("two-addr", 1000, 500, 10)
        oid = app.place_order(C, user(MEMBER), {p: 1}, "Sam", "+1 619 555 0102", "245 Market St, back gate, apt 4", "",
                              32.7, -117.1, "245 Market Street, San Diego, California 92101")
        o = C.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone()
        text = app.dispatch_text(o, [])
        self.assertIn("Address: 245 Market St, back gate, apt 4", text)
        self.assertIn("Map pin address: 245 Market Street, San Diego, California 92101", text)
        same = app.place_order(C, user(MEMBER), {p: 1}, "Sam", "+1", "1 Elm St", "", 32.7, -117.1, "1 elm st ")
        self.assertNotIn("Map pin address", app.dispatch_text(C.execute("SELECT * FROM orders WHERE id=?", (same,)).fetchone(), []))
        no_pin = app.place_order(C, user(MEMBER), {p: 1}, "Sam", "+1", "1 Elm St", "", None, None, "ignored without a pin")
        self.assertIsNone(C.execute("SELECT pin_address FROM orders WHERE id=?", (no_pin,)).fetchone()["pin_address"])

    def test_driver_message(self):
        oid = app.place_order(C, user(MEMBER), {product("e", 1500, 900, 5): 2}, *ADDR, "Gate code 12")
        o = C.execute("SELECT * FROM orders WHERE id=?", (oid,)).fetchone()
        text = app.dispatch_text(o, C.execute("SELECT * FROM order_items WHERE order_id=?", (oid,)).fetchall())
        for want in (f"#ORD-{oid}", "2 x E", "Gate code 12", "Collect: $18.00", "9 Elm St"): self.assertIn(want, text)
        link = app.wa_link("+52 (646) 123-4567", text)
        self.assertTrue(link.startswith("https://wa.me/526461234567?text="))
        self.assertEqual(urllib.parse.unquote(link.split("text=")[1]), text)
        with self.assertRaises(ValueError): app.wa_link("555", text)
        paid = app.dispatch_text({**o, "payment": "paid_cash"}, [])
        self.assertIn("Collect: nothing", paid); self.assertNotIn("Collect: $", paid)


class Wsgi(unittest.TestCase):
    def call(self, method, path, body=b"", cookie="", country=""):
        got = {}
        env = {"REQUEST_METHOD": method, "PATH_INFO": path.split("?")[0], "QUERY_STRING": path.partition("?")[2],
               "CONTENT_LENGTH": str(len(body)), "wsgi.input": io.BytesIO(body), "HTTP_COOKIE": cookie}
        if country: env["HTTP_X_VERCEL_IP_COUNTRY"] = country
        out = b"".join(app.app(env, lambda status, headers: got.update(status=status, headers=headers)))
        return got["status"], dict(got["headers"]), out.decode(errors="replace")

    def test_vercel_entry_point(self):
        status, _, body = self.call("GET", "/register")
        self.assertEqual(status, "200 OK"); self.assertIn("Create account", body)
        status, headers, _ = self.call("POST", "/login", b"email=member%40x.com&password=password123")
        self.assertEqual(status, "303 See Other")
        sid = headers["Set-Cookie"].split(";")[0]
        self.assertIn("Member prices shown", self.call("GET", "/", cookie=sid)[2])
        self.assertEqual(self.call("GET", "/admin", cookie=sid)[0], "403 Forbidden")

    def test_ads_target_countries_and_stay_off_the_shop(self):
        try:
            banner = app.save_ad(C, STAFF, None, {"name": "Toy promo", "placement": "top", "image_data": JPEG, "link": "https://example.com/aff?id=7",
                                                  "hide_countries": "us", "active": "on"})
            casino = app.save_ad(C, STAFF, None, {"name": "Casino", "placement": "top", "image_data": JPEG, "link": "https://example.com/casino",
                                                  "gambling": "on", "active": "on"})
            net = app.save_ad(C, STAFF, None, {"name": "Network", "placement": "side", "code": "<script>parent.document.title='x'</script>", "active": "on"})
            mx = app.save_ad(C, STAFF, None, {"name": "Mexico only", "placement": "grid", "image_data": JPEG, "link": "https://example.com/mx",
                                              "countries": "MX", "active": "on"})
            img = C.execute("SELECT image_id FROM ads WHERE id=?", (banner,)).fetchone()["image_id"]
            for _ in range(8):  # gambling ads are held off the all-ages games pages, whatever the rotation picks
                self.assertNotIn(f'/ad/{casino}"', self.call("GET", "/", country="BR")[2])
            home = self.call("GET", "/", country="BR")[2]
            self.assertIn(f'href="/ad/{banner}"', home); self.assertIn('<span class="ad-label">Ad</span>', home)
            self.assertIn(f'src="/ad/{net}/frame"', home); self.assertIn('sandbox="allow-scripts allow-popups', home)
            self.assertNotIn("parent.document", home)  # network code never runs in the page itself
            self.assertNotIn(f'/ad/{mx}"', home)  # Mexico-only ad hidden in Brazil
            self.assertIn(f'/ad/{mx}"', self.call("GET", "/games", country="MX")[2])
            self.assertNotIn(f'/ad/{banner}"', self.call("GET", "/", country="US")[2])  # hidden-country rule
            status, headers, _ = self.call("GET", f"/ad/{banner}")
            self.assertEqual((status, headers["Location"]), ("303 See Other", "https://example.com/aff?id=7"))
            C.conn.rollback(); self.assertEqual(C.execute("SELECT clicks FROM ads WHERE id=?", (banner,)).fetchone()["clicks"], 1)
            status, headers, body = self.call("GET", f"/ad/{net}/frame")
            self.assertTrue(headers["Content-Security-Policy"].startswith("sandbox allow-scripts")); self.assertIn("parent.document", body)
            self.assertEqual(self.call("GET", f"/img/{img}")[0], "200 OK")  # banners are public, unlike product photos
            sid = self.call("POST", "/login", b"email=member%40x.com&password=password123")[1]["Set-Cookie"].split(";")[0]
            for page in ("/", "/account"): self.assertNotIn("/ad/", self.call("GET", page, cookie=sid, country="BR")[2], page)  # never in the shop
            with self.assertRaises(ValueError): app.save_ad(C, STAFF, None, {"name": "x", "placement": "top", "image_data": JPEG, "link": "http://plain.example"})
            with self.assertRaises(ValueError): app.save_ad(C, STAFF, None, {"name": "x", "placement": "top", "image_data": JPEG, "link": "https://a.b", "code": "<b>"})
            self.assertEqual(self.call("GET", "/play/2048")[1]["Location"], "/games/2048/index.html")  # no pre-game ad: straight to the game
            app.save_ad(C, STAFF, None, {"name": "Pre", "placement": "pregame", "image_data": JPEG, "link": "https://example.com/p", "active": "on"})
            body = self.call("GET", "/play/2048")[2]
            self.assertIn('id="skip" href="/games/2048/index.html" data-wait="5"', body); self.assertIn('href="/ad/', body)
            self.assertEqual(self.call("GET", "/play/nope")[0], "404 Not Found")
            app.ADS_ON = False  # the module switch: no ads anywhere, games unaffected
            self.assertNotIn("/ad/", self.call("GET", "/", country="BR")[2])
            self.assertEqual(self.call("GET", "/play/2048")[1]["Location"], "/games/2048/index.html")
            C.conn.rollback(); self.assertIn("ad.save", C.execute("SELECT string_agg(action, ' ') AS a FROM audit").fetchone()["a"])
        finally:
            app.ADS_ON = True
            with C: C.execute("UPDATE ads SET active=0")

    def test_staff_upload_is_not_cut_short(self):
        sid = self.call("POST", "/login", b"email=staff%40x.com&password=password123")[1]["Set-Cookie"].split(";")[0]
        csrf = re.search(r'name="csrf" value="([^"]+)"', self.call("GET", "/admin", cookie=sid)[2]).group(1)
        photo = "data:image/jpeg;base64," + base64.b64encode(b"\xff\xd8\xff\xe0" + os.urandom(300_000)).decode()  # a real phone photo is this big
        body = urllib.parse.urlencode({"csrf": csrf, "sku": "big-pic", "name": "Big", "retail": "1", "wholesale": "1",
                                       "stock": "1", "active": "on", "image_data": photo}).encode()
        self.assertEqual(self.call("POST", "/admin/products", body, cookie=sid)[0], "303 See Other")
        C.conn.rollback()
        self.assertTrue(C.execute("SELECT image_id FROM products WHERE sku='big-pic'").fetchone()["image_id"])


class Http(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = app.ThreadingHTTPServer(("127.0.0.1", 0), app.H)
        cls.base = f"http://127.0.0.1:{cls.srv.server_address[1]}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.secret = product("secret-sku", 1000, 400, 50, 1)

    @classmethod
    def tearDownClass(cls): cls.srv.shutdown()

    def client(self, email=None, pw="password123"):
        op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        if email: self.post(op, "/login", {"email": email, "password": pw})
        return op

    def get(self, op, path):
        try: r = op.open(self.base + path); return r.status, r.read().decode()
        except urllib.error.HTTPError as ex: return ex.code, ex.read().decode()

    def post(self, op, path, data, csrf_from=None):
        if csrf_from: data["csrf"] = re.search(r'name="csrf" value="([^"]+)"', self.get(op, csrf_from)[1]).group(1)
        try: r = op.open(self.base + path, urllib.parse.urlencode(data).encode()); return r.status, r.read().decode()
        except urllib.error.HTTPError as ex: return ex.code, ex.read().decode()

    def test_join_pay_approve_order(self):
        me, staff = self.client(), self.client("staff@x.com")
        body = self.post(me, "/register", {"name": "Nia", "email": "nia@x.com", "password": "password123",
                                           "phone": "+1 619 555 0150", "address": "7 Pine St", "adult": "on"})[1]
        ref = re.search(r"APP-(\d+)", body).group(1)
        self.assertIn("Bank of Test, acct 123", body)  # pay page shown right after joining
        shop = self.get(me, "/")[1]
        self.assertNotIn("Secret-Sku", shop); self.assertNotRegex(shop, r'name="q\d')  # no ordering yet (no quantity fields)
        self.assertIn(f"APP-{ref}", self.get(staff, "/admin")[1])  # shows on dashboard as waiting
        self.assertEqual(self.post(staff, f"/admin/accounts/{ref}", {"action": "approve"}, csrf_from="/admin")[0], 400)
        self.post(staff, f"/admin/accounts/{ref}", {"action": "approve", "deposit_ref": "TX-123", "back": "/admin"}, csrf_from="/admin")
        self.assertIn("Secret-Sku", self.get(me, "/")[1])
        body = self.post(me, "/order", {f"q{self.secret}": "2", "name": "Nia", "phone": "+1 619 555 0150",
                                        "address": "7 Pine St"}, csrf_from="/")[1]
        oid = re.search(r"Order #(\d+) placed", body).group(1)
        dash = self.get(staff, "/admin")[1]
        self.assertIn(f'data-copy="m{oid}"', dash)  # copy button for the driver message
        self.assertIn(f"#ORD-{oid}", dash)
        self.post(staff, f"/admin/accounts/{ref}", {"action": "revoke"}, csrf_from="/admin")
        self.assertNotIn("Secret-Sku", self.get(me, "/")[1])  # access ends immediately
        self.assertIn("deposit TX-123", self.get(staff, f"/admin/accounts/{ref}")[1])

    def test_staff_gives_logins_and_resets_passwords(self):
        staff = self.client("staff@x.com")
        self.post(staff, "/admin/accounts", {"kind": "member", "name": "Walk In", "email": "walkin@x.com", "password": "temppass123",
                                             "phone": "+1 619 555 0160", "deposit_ref": "CASH-1"}, csrf_from="/admin")
        walkin = self.client("walkin@x.com", "temppass123")
        self.assertIn("Secret-Sku", self.get(walkin, "/")[1])  # active immediately
        self.post(staff, "/admin/accounts", {"kind": "staff", "name": "Ed", "email": "ed@x.com", "password": "edpass12345",
                                             "phone": "+1 619 555 0161"}, csrf_from="/admin")
        self.assertEqual(self.get(self.client("ed@x.com", "edpass12345"), "/admin")[0], 200)
        uid = C.execute("SELECT id FROM users WHERE email='walkin@x.com'").fetchone()["id"]
        self.post(staff, f"/admin/accounts/{uid}", {"action": "password", "password": "newpass12345"}, csrf_from="/admin")
        self.assertNotIn("Secret-Sku", self.get(walkin, "/")[1])  # old session ended
        self.assertIn("Secret-Sku", self.get(self.client("walkin@x.com", "newpass12345"), "/")[1])

    def get_raw(self, op, path):
        try: r = op.open(self.base + path); return r.status, r.headers["Content-Type"], r.read()
        except urllib.error.HTTPError as ex: return ex.code, None, b""

    def test_product_photos_follow_product_visibility(self):
        staff, member, visitor = self.client("staff@x.com"), self.client("member@x.com"), self.client()
        pending = self.client("pending@x.com")
        for sku, members_only in (("pic-pub", ""), ("pic-mem", "on")):
            data = {"sku": sku, "name": sku.title(), "retail": "10", "wholesale": "6", "stock": "5", "active": "on", "image_data": JPEG}
            if members_only: data["wholesale_only"] = "on"
            self.post(staff, "/admin/products", data, csrf_from="/admin")
        pub, mem = (C.execute("SELECT image_id FROM products WHERE sku=?", (s,)).fetchone()["image_id"] for s in ("pic-pub", "pic-mem"))
        self.assertTrue(pub and mem)
        self.assertEqual([self.get_raw(visitor, f"/img/{i}")[0] for i in (pub, mem)], [404, 404])  # no shop before login
        self.assertEqual(self.get_raw(pending, f"/img/{pub}")[:2], (200, "image/jpeg"))
        self.assertIn(f'src="/img/{pub}"', self.get(pending, "/")[1])  # shop grid shows it once logged in
        self.assertEqual(self.get_raw(pending, f"/img/{mem}")[0], 404)  # members-only photo stays hidden
        self.assertEqual(self.get_raw(member, f"/img/{mem}")[0], 200)
        pid = C.execute("SELECT id FROM products WHERE sku='pic-pub'").fetchone()["id"]
        self.post(staff, f"/admin/products/{pid}", {"sku": "pic-pub", "name": "Pic-Pub", "retail": "10", "wholesale": "6",
                                                   "stock": "5", "active": "on", "image_data": JPEG}, csrf_from="/admin")
        C.conn.rollback()
        self.assertIsNone(C.execute("SELECT id FROM images WHERE id=?", (pub,)).fetchone())  # replaced photo is deleted
        body = self.post(staff, "/admin/products", {"sku": "bad", "name": "Bad", "retail": "1", "wholesale": "1", "stock": "1",
                                                    "image_data": "data:image/jpeg;base64," + base64.b64encode(b"<svg>").decode()}, csrf_from="/admin")[1]
        self.assertIn("isn&#x27;t a readable image", body)
        C.conn.rollback()

    def test_transfer_receipt_is_staff_only_and_marks_paid(self):
        staff, member = self.client("staff@x.com"), self.client("member@x.com")
        oid = app.place_order(C, user(MEMBER), {self.secret: 1}, *ADDR)
        body = self.post(staff, f"/admin/orders/{oid}/receipt", {"receipt_data": JPEG}, csrf_from="/admin")[1]
        C.conn.rollback()
        o = C.execute("SELECT payment, receipt_image_id FROM orders WHERE id=?", (oid,)).fetchone()
        self.assertEqual(o["payment"], "paid_transfer")
        self.assertIn(f'src="/img/{o["receipt_image_id"]}"', body)
        self.assertEqual(self.get_raw(staff, f"/img/{o['receipt_image_id']}")[0], 200)
        self.assertEqual(self.get_raw(member, f"/img/{o['receipt_image_id']}")[0], 404)
        self.assertEqual(self.get_raw(self.client(), f"/img/{o['receipt_image_id']}")[0], 404)
        self.assertIn("order.receipt", self.get(staff, "/admin/audit")[1])
        C.conn.rollback()

    def test_receipts_keep_latest_and_expire(self):
        staff = self.client("staff@x.com")
        oid = app.place_order(C, user(MEMBER), {self.secret: 1}, *ADDR)
        self.post(staff, f"/admin/orders/{oid}/receipt", {"receipt_data": JPEG}, csrf_from="/admin")
        C.conn.rollback(); first = C.execute("SELECT receipt_image_id AS r FROM orders WHERE id=?", (oid,)).fetchone()["r"]
        self.post(staff, f"/admin/orders/{oid}/receipt", {"receipt_data": JPEG}, csrf_from="/admin")
        C.conn.rollback(); second = C.execute("SELECT receipt_image_id AS r FROM orders WHERE id=?", (oid,)).fetchone()["r"]
        self.assertNotEqual(first, second)
        self.assertIsNone(C.execute("SELECT id FROM images WHERE id=?", (first,)).fetchone())  # replaced one is gone
        with C: C.execute("UPDATE images SET created_at=? WHERE id=?", (app.now() - (app.RECEIPT_DAYS + 1) * 86400, second))
        self.get(staff, "/admin")  # opening the dashboard runs the cleanup
        C.conn.rollback()
        self.assertIsNone(C.execute("SELECT id FROM images WHERE id=?", (second,)).fetchone())
        o = C.execute("SELECT payment, receipt_image_id FROM orders WHERE id=?", (oid,)).fetchone()
        self.assertEqual((o["payment"], o["receipt_image_id"]), ("paid_transfer", None))  # payment record stays
        self.assertIn("receipt deleted after", self.get(staff, "/admin/audit")[1])
        C.conn.rollback()

    def test_csv_exports(self):
        staff = self.client("staff@x.com")
        with C: C.execute("UPDATE users SET name='=HYPERLINK(1)' WHERE id=?", (PENDING,))
        for name in app.EXPORTS:
            status, ctype, raw = self.get_raw(staff, f"/admin/export/{name}.csv")
            self.assertEqual((status, ctype), (200, "text/csv; charset=utf-8"), name)
            self.assertTrue(raw.startswith(b"\xef\xbb\xbf"), name)  # BOM so Excel reads it as UTF-8
        members = self.get_raw(staff, "/admin/export/members.csv")[2].decode("utf-8-sig")
        self.assertIn("'=HYPERLINK(1)", members)  # formula neutralised
        self.assertNotIn(user(MEMBER)["pw"], members)  # password hashes never leave the database
        self.assertNotIn("pw", members.splitlines()[0].split(","))
        self.assertEqual(self.get_raw(self.client("member@x.com"), "/admin/export/orders.csv")[0], 403)
        self.assertIn("Image storage", self.get(staff, "/admin/export")[1])
        with C: C.execute("UPDATE users SET name='Pete' WHERE id=?", (PENDING,))

    def test_order_form_map(self):
        member = self.client("member@x.com")
        r = member.open(self.base + "/"); csp = r.headers["Content-Security-Policy"]; page = r.read().decode()
        for want in ('id="map"', 'integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="', 'name="lat"', 'id="address"'):
            self.assertIn(want, page)
        for want in ("https://tile.openstreetmap.org", "connect-src 'self' https://nominatim.openstreetmap.org", "script-src 'self' https://unpkg.com"):
            self.assertIn(want, csp)
        self.assertNotIn('id="map"', self.get(self.client(), "/")[1])  # visitors don't get the order form
        base = {f"q{self.secret}": "1", "name": "Sam", "phone": "+1 619 555 0102", "address": "2 Main St"}
        body = self.post(member, "/order", {**base, "lat": "abc", "lng": "1"}, csrf_from="/")[1]
        self.assertIn("The map pin is invalid", body)
        body = self.post(member, "/order", {**base, "lat": "32.7", "lng": "-117.1"}, csrf_from="/")[1]
        oid = re.search(r"Order #(\d+) placed", body).group(1)
        C.conn.rollback()
        self.assertEqual(C.execute("SELECT lat FROM orders WHERE id=?", (oid,)).fetchone()["lat"], 32.7)
        self.assertIn('value="32.700000"', self.get(member, "/")[1])  # next order starts at the last pin
        body = self.post(member, "/order", {**base, "address": "2 Main St, side door", "lat": "32.7", "lng": "-117.1",
                                            "pin_address": "2 Main Street, San Diego"}, csrf_from="/")[1]
        self.assertIn("2 Main St, side door", body); self.assertIn("Map: 2 Main Street, San Diego", body)  # member sees both
        C.conn.rollback()

    def test_only_staff_can_send_large_uploads(self):
        big = {"notes": "x" * 200_000}
        self.assertEqual(self.post(self.client("member@x.com"), "/order", big, csrf_from="/")[0], 413)
        self.assertNotEqual(self.post(self.client("staff@x.com"), f"/admin/orders/999999/receipt", big, csrf_from="/admin")[0], 413)

    def test_admin_is_staff_only(self):
        self.assertIn("Log in", self.get(self.client(), "/admin")[1])
        member = self.client("member@x.com")
        self.assertEqual(self.get(member, "/admin")[0], 403)
        self.assertEqual(self.post(member, f"/admin/accounts/{PENDING}", {"action": "approve", "deposit_ref": "x"},
                                   csrf_from="/")[0], 403)

    def test_post_without_csrf_is_rejected(self):
        self.assertEqual(self.post(self.client("member@x.com"), "/order", {f"q{self.secret}": "1"})[0], 403)

    def test_visitors_get_games_not_the_shop(self):
        body = self.get(self.client(), "/")[1]
        for slug, title, *_ in app.GAMES: self.assertIn(f'href="/play/{slug}"', body); self.assertIn(title, body)
        self.assertNotIn("Secret-Sku", body); self.assertNotIn("/img/", body); self.assertNotIn(">Shop<", body)
        member = self.get(self.client("member@x.com"), "/")[1]
        self.assertIn("Secret-Sku", member); self.assertIn('href="/games"', member)  # logged in: the shop, games one click away

    def test_game_search_and_categories(self):
        op = self.client()
        body = self.get(op, "/games?q=bird")[1]
        self.assertIn("Results for “bird”", body); self.assertIn('data-game="clumsy-bird"', body); self.assertNotIn('data-game="2048"', body)
        body = self.get(op, "/games?tag=puzzle")[1]
        self.assertIn("Puzzle games", body); self.assertIn('data-game="2048"', body); self.assertNotIn('data-game="clumsy-bird"', body)
        self.assertIn('aria-current="page"><svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="M15.39', body)  # rail marks Puzzle
        body = self.get(op, "/games?q=%3Cscript%3E")[1]
        self.assertIn("No games match “&lt;script&gt;”", body); self.assertNotIn("<script>", body.split("</title>")[1].split("app.js")[1])
        self.assertIn('href="/play/clumsy-bird"', self.get(op, "/games?tag=nope")[1])  # unknown category: everything

    def test_join_needs_21_plus(self):
        body = self.post(self.client(), "/register", {"name": "Kid", "email": "kid@x.com", "password": "password123",
                                                      "phone": "+1 619 555 0170", "address": "1 Oak St"})[1]
        self.assertIn("21 or older", body)
        C.conn.rollback()
        self.assertIsNone(C.execute("SELECT id FROM users WHERE email='kid@x.com'").fetchone())

    def test_game_files(self):
        op = self.client()
        r = op.open(self.base + "/games/2048/js/game_manager.js")
        self.assertEqual((r.headers["Content-Type"], r.headers["Content-Security-Policy"]), ("text/javascript", app.GAME_CSP))
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "vercel.json")) as f:  # the CDN must send the same policy
            sent = {h["key"]: h["value"] for h in json.load(f)["headers"][0]["headers"]}
        self.assertEqual(sent["Content-Security-Policy"], app.GAME_CSP)
        for slug, *_ in app.GAMES:
            for name in ("index.html", "poster.jpg", "preview.mp4"): self.assertEqual(self.get_raw(op, f"/games/{slug}/{name}")[0], 200, slug + name)
        self.assertTrue(self.get(op, "/games/clumsy-bird")[1].startswith("<!DOCTYPE"))  # folder redirects to its index.html
        self.assertEqual(self.get_raw(op, "/fonts/nunito.woff2")[:2], (200, "font/woff2"))
        for bad in ("/fonts/../app.py", "/games/../app.py", "/games/%2e%2e/app.py", "/games/2048/../../app.py", "/games/nope.js"):
            self.assertEqual(self.get_raw(op, bad)[0], 404, bad)

    def test_every_page_renders(self):
        staff = self.client("staff@x.com")
        for p in ["/", "/account", "/admin", "/admin/orders", "/admin/orders?status=new", "/admin/accounts",
                  f"/admin/accounts/{MEMBER}", "/admin/products", "/admin/drivers", "/admin/ads", "/admin/audit", "/admin/export", "/app.js", "/games"]:
            self.assertEqual(self.get(staff, p)[0], 200, p)
        for p in ["/", "/games", "/register", "/login"]: self.assertEqual(self.get(self.client(), p)[0], 200, p)


if __name__ == "__main__":
    unittest.main()
