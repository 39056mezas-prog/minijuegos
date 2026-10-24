# Membership store: builder's brief

Read this first. It covers the code, how to change it safely, and what must never break.

| File | What's in it |
|---|---|
| `README.md` | Operating and deploying it |
| `docs/DECISIONS.md` | Why it is built this way |
| `docs/DATABASE.md` | Schema and the live Supabase setup |
| `docs/BACKLOG.md` | What's next, cut on purpose, or unverified |

## What this is

A membership store for a small distribution business in the San Diego / Baja California area.

- **Visitors** see only a mini games site (2048 and Clumsy Bird). No products, prices or photos until they log in.
- **Logged-in users** see the shop: public products at public prices; ordering waits for approval.
- **Members** sign up (confirming they're 21+), pay a one-time fee by bank transfer, and get approved by staff. Then they see members-only products at member prices and order.
- **Orders** are paid on delivery, in cash or by transfer to the driver.
- **Staff** run everything from `/admin`: approvals, orders, a driver message to copy or open in WhatsApp, products with photos, transfer receipts, ads, and CSV exports for Excel.
- **Ads** show only on the games pages (top banner, a tile in the grid, a right column on wide screens, a screen with a skip button before a game). Each is an uploaded banner with a link, or pasted ad-network code, with optional country rules.

## Stack

- `app.py`: the whole app, about 1,000 lines, Python 3.12+.
- **Dependencies:** `psycopg[binary]` (Postgres) and `tzdata`. Nothing else server-side.
- **Hosting:** Vercel runs the WSGI callable `app` at the bottom of `app.py`; `pyproject.toml` sets `tool.vercel.entrypoint = "app:app"`. Locally, `python3 app.py` runs the same handler on `ThreadingHTTPServer`.
- **Database:** Postgres on Supabase, project **conectando-ensenada**, schema `store`, login role `store_app` (see `docs/DATABASE.md`). Any Postgres works.
- **Browser:** plain server-rendered HTML forms, with one small script served at `/app.js`. It handles Copy buttons, shrinks photos before upload, runs the delivery map, keeps the visitor's "Continue playing" list (localStorage), and plays a game tile's clip on hover or keyboard focus.
- **Look:** a dark games-portal shell on every page (top bar with search, icon rail that becomes a bottom bar on phones, staff tabs on `/admin`). Tokens are at the top of `CSS`; the face is Nunito, self-hosted in `public/fonts/` (OFL). Icons are Lucide paths in `ICONS` (ISC). Visual decisions live in `DESIGN.md`; product facts in `PRODUCT.md`.
- **Games:** static files in `public/games/<slug>/`, served by Vercel's CDN with the headers in `vercel.json`. Locally and in tests, `static()` serves the same files with the same CSP (`GAME_CSP`). The games are unmodified upstream code except: a "← All games" link, Clumsy Bird's inline start script moved to `start.js` (the CSP blocks inline scripts), Clumsy Bird centred on upright phones, and 2048's "official site" note removed. Licenses: 2048 is MIT, Clumsy Bird is GPL-3.0 (keep its `LICENSE.md` and source link).
- **Map:** Leaflet 1.9.4 from unpkg, pinned with an SRI hash. Map tiles come from tile.openstreetmap.org, and addresses from Nominatim (OpenStreetMap). No API keys.

## Code map (`app.py`, top to bottom)

1. **Config.** Environment variables: `ADS_ENABLED`, `STORE_NAME`, `STORE_TZ`, `RECEIPT_DAYS`, `MAP_CENTER`, `COOKIE_SECURE`, `MEMBERSHIP_FEE`, `PAYMENT_DETAILS`, `DATABASE_URL`, `HOST`/`PORT` (local only). `PUBLIC`, `GAMES` (slug, title, blurb, category; the first is the featured tile), `CATEGORIES` and `GAME_CSP`. `STATUSES` and `PAYMENTS` are the allowed order states. `LEAFLET` holds the pinned map tags.
2. **`SCHEMA`.** Idempotent DDL (`CREATE … IF NOT EXISTS`, `ADD COLUMN IF NOT EXISTS`), ending with row-level security on for every table. `python3 app.py setup` runs it, and `schema.sql` is generated from it.
3. **Data and business rules.** These are pure functions over a `db` connection:
   - `db`: a small wrapper around psycopg. One connection per request. `with c:` commits, or rolls back on error. Placeholders are written `?`.
   - `create_user`, `is_member`, `visible_products`
   - `place_order`: decides prices and visibility server-side; stock is taken atomically.
   - `update_order`: cancelling returns stock; "delivered" needs a recorded payment.
   - `save_image`, `expire_receipts`
   - `dispatch_text`, `map_address`, `maps_link`, `wa_link`: build the driver message.
   - `country_codes`, `pick_ad` (random active ad for a placement and the visitor's country), `save_ad` (validation, image swap, audit).
   - `order_rows`
4. **HTML helpers.** `CSS`, `note`, `select`, `field`.
5. **`class H`.** Request handling: routing, session, CSRF check, body size limit, security headers (`send`), page shell (`page`), `login_as`.
6. **Customer pages.** `APP_JS`/`app_js`, `image_input`, `image` (serves `/img/<id>` with access checks; login required), `static` (game and font files, local only), `game_tile`, `games` (the visitors' front page, search `?q=` and categories `?tag=`), `ad_html`, `ad_frame` (serves pasted network code under a sandbox CSP), `ad_click` (counts the click, then redirects), `visitor_country`, `with_side`, `play` (the pre-game ad, or straight to the game), `home` (games for visitors; photo grid and order form with map once logged in), `order`, `register*`, `login*`, `logout`, `account`.
7. **Staff pages.**
   - Shared pieces: `orders_table`, `approve_form`, `members_table`
   - Dashboard and orders: `admin_dashboard`, `admin_orders`, `admin_order`, `receipt_section`, `admin_receipt`, `admin_order_update`, `admin_whatsapp`
   - Members: `admin_accounts`, `admin_account_create`, `admin_account`, `admin_account_update`
   - Products: `product_form`, `admin_products`, `admin_product`, `admin_product_save`
   - Export: `EXPORTS`, `excel_safe`, `admin_export`, `admin_export_csv`
   - Ads: `ad_form`, `admin_ads`, `admin_ad`, `admin_ad_save`
   - Drivers and audit log: `admin_drivers`, `admin_driver_save`, `admin_audit`
8. **`ROUTES`.** `(method, regex, handler, access)`, where access is `None`, `"user"` or `"staff"`. The router enforces access before the handler runs.
9. **`app(environ, start_response)`.** The Vercel entry point; it drives `H` without a socket. Below it is the CLI: `setup`, `add-staff`, and serve.

## Run and test

```bash
pip install "psycopg[binary]" tzdata
DATABASE_URL=postgresql://… python3 app.py setup      # create/upgrade tables
DATABASE_URL=postgresql://… python3 app.py add-staff you@x.com "Name" "+1 …"
DATABASE_URL=postgresql://… python3 app.py            # http://127.0.0.1:8000
TEST_DATABASE_URL=postgresql://postgres@localhost/postgres python3 -m unittest test_app
```

**Tests.** `test_app.py` has 26 tests. They create a throwaway database on the `TEST_DATABASE_URL` server and drop it afterwards, so never point them at a server where you can't create databases. They cover:
- business rules
- every HTTP page
- the Vercel entry point
- CSRF and staff-only access
- image visibility
- receipt expiry
- CSV safety
- the map form
- visitors getting games only, the 21+ check, game files and their CSP matching `vercel.json`
- staff uploads larger than 100 KB through the Vercel entry point
- ads: country rules, the sandboxed network frame, click counting, the pre-game screen, and never appearing in the shop or account

**Disposable local Postgres** (Ubuntu paths; initdb refuses to run as root):
```bash
B=/usr/lib/postgresql/16/bin; D=~/.pgtest
$B/initdb -D $D/data -A trust -U postgres && $B/pg_ctl -D $D/data -o "-p 54329 -k $D" -l $D/log start
TEST_DATABASE_URL="postgresql://postgres@/postgres?host=$D&port=54329" python3 -m unittest test_app
```

**Browser checks.** For anything touching `APP_JS`, test in a real browser (Playwright works). Under the page's CSP:
- string predicates like `page.wait_for_function("…")` are blocked; wait on elements instead (`locator(...).wait_for()`).
- with no internet, serve unpkg from `npm pack leaflet@1.9.4` (same bytes, so SRI still passes), and stub the tiles and Nominatim with `context.route`.

## Rules that must not break

- **Server decides access.** Prices, members-only products and their photos, receipts, and admin pages are all checked on the server for every request. Never rely on hiding something in HTML.
- **The shop is invisible before login.** `/` renders games for visitors, and `/img/<id>` refuses every image without a session (so photos are `Cache-Control: private`). Don't add public pages that list products.
- **Only staff approval grants membership.** Registering, depositing or paying never does. `is_member()` is `biz_status == 'approved'`.
- **Every POST from a logged-in session carries the CSRF token** (`h.csrf()` in every form). The router rejects it otherwise.
- **Escape all output** with `e()`, which is `html.escape`. Use double-quoted attributes.
- **Money is integer cents.** Use `cents()` to parse and `money()` to show. Never use floats for money.
- **Stock can't go negative.** There's a DB `CHECK`, and `place_order` uses a conditional `UPDATE … WHERE stock>=?` inside one transaction.
- **Audit everything.** Every staff action and order change writes to `audit` via `log()`. Keep this for new features. Order-related details start with `#<order id> ` and account-related ones with `APP-<id>`; the order and member pages filter on those prefixes.
- **Uploads.** Images arrive as `data:` URLs (the browser has already shrunk them). `save_image` checks the type, the magic bytes and a 3 MB cap. Bodies over 100 KB are refused unless the sender is staff (4 MB).
- **Exports.** Never export password hashes, sessions or image bytes. Pass every cell through `excel_safe`.
- **Ads stay on the games pages and in their box.** Never call `ad_html` from the shop, account or admin pages. Pasted network code only ever runs inside `/ad/<id>/frame`, which has a `sandbox` CSP and a sandboxed iframe, so it can't read the page, the session or the CSRF token. Never put ad code into a page directly or loosen the main CSP for it. Every ad carries the "Ad" label. Gambling ads are never served (`pick_ad` filters `gambling=0`), per the product spec; `ADS_ENABLED=0` turns the whole module off.
- **Game CSP lives in two places:** `GAME_CSP` in `app.py` and `vercel.json`. A test fails if they differ.
- **CSP lives in `H.send`.** If you add an outside resource, add exactly its host there, and pin scripts with an SRI hash.
- **Never commit secrets.** `DATABASE_URL` lives only in Vercel's environment variables.

## Gotchas

- **Python 3.12+ is required** for the nested f-strings with reused quotes (`pyproject.toml` says so).
- **Write SQL with `?`.** The `db` wrapper turns `?` into `%s`, so never put a literal `?` in SQL. Pass `None` (not `()`) when there are no parameters, so `%` isn't parsed.
- **Use `WHERE true`, not `WHERE 1`.** That's Postgres.
- **`prepare_threshold=None`** is required, because the Supabase/Neon transaction poolers can't hold prepared statements.
- **Rows are dicts** (`dict_row`). Use `row["col"]`, never `row[0]`. For counts, alias them: `count(*) AS n`.
- **No `lastrowid`.** Use `INSERT … RETURNING id` and `.fetchone()["id"]`.
- **Vercel has no persistent disk.** All state must live in Postgres: sessions, images, everything.
- **Cleanup piggybacks on page loads.** There's no scheduler: `expire_receipts` runs when staff open `/admin` or `/admin/export`.
- **`APP_JS` is a Python string.** Escape backslashes in JS regexes (`\\.`), or Python warns.
- **Times are Unix seconds** (`BIGINT`), shown in `STORE_TZ` via `when()`.

## How to change things

- **New column or table.**
  1. Add an idempotent statement to `SCHEMA`, and add new tables to the RLS list.
  2. Regenerate `schema.sql`:
     ```bash
     python3 -c "import os,sys;os.environ['DATABASE_URL']='x';sys.path.insert(0,'.');import app;open('schema.sql','w').write('-- Run once …\n'+app.SCHEMA)"
     ```
  3. Apply it to the live database the way `docs/DATABASE.md` shows: as `store_app`, with `SET ROLE store_app; SET search_path = store;`.
  4. Add a test.
- **New page.** Write a handler `def x(h, *groups)`, render it with `h.page(title, body)`, and add a `ROUTES` entry with the right access level. If it's a staff page, add it to `ADMIN_LINKS` (the staff tabs).
- **New game.** Drop its runtime files into `public/games/<slug>/` (no inline scripts; it must run under `GAME_CSP`), add a "← All games" link to `/games`, add it to `GAMES` (and a category to `CATEGORIES` if new), and play it in a browser. Keep its license file. Its tile needs `poster.jpg` (a real gameplay frame) and `preview.mp4` (a 5–7 s silent H.264 loop, about 100–150 KB): record real play with Playwright's video recording, then cut with ffmpeg (`-an -c:v libx264 -preset veryfast -crf 28 -pix_fmt yuv420p -movflags +faststart`). Record the poster's origin with Impeccable's `embed-prompt`.
- **New order state or payment type.** Update `STATUSES`/`PAYMENTS`, check `update_order` and `dispatch_text`, and add a test.
- After any change, run the tests. If it's visual, take a screenshot at 1280 px and 390 px (phone) wide.

## Working style used so far

Smallest change that fully solves the need ("ponytail" style). Push back on features the need doesn't justify, and say what was skipped. Never cut security, validation, accessibility or audit logging. New logic gets a test. A known shortcut gets a code comment of the form `shortcut: <limit>, <when to upgrade>`.
