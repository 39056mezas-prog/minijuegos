# Membership store + WhatsApp dispatch

Building on this? Start with `CLAUDE.md`.

One Python file (`app.py`) on Postgres, deployed on Vercel. The database is Supabase, in the project conectando-ensenada. Two dependencies: `psycopg` (Postgres driver) and `tzdata`.

## Deploy (GitHub + Vercel + Supabase)

The database is already set up in the Supabase project **conectando-ensenada**:

- The tables live in their own schema, `store`, separate from that project's tables.
- They have their own database login, `store_app`, which can only reach `store`.
- Supabase's public API can't see them.

1. **GitHub.** Push this folder to a new repository.
2. **Connection string.** In Supabase, open conectando-ensenada, click **Connect** and choose **Transaction pooler**. Copy the URI, then change two things in it:
   - the user `postgres.pdoznhmckwovmrerlcro` becomes `store_app.pdoznhmckwovmrerlcro`
   - `[YOUR-PASSWORD]` becomes the store_app password (given to you separately; never commit it)
   ```
   postgresql://store_app.pdoznhmckwovmrerlcro:STORE_APP_PASSWORD@aws-…-us-west-1.pooler.supabase.com:6543/postgres
   ```
3. **Vercel.** Click **Add New → Project** and import the repo. Add the environment variables below and deploy.
4. **Log in.** Use the first staff login that was created for you, then change its password under **Members → your name → Set a new password**.

| Environment variable | Example | Notes |
|---|---|---|
| `DATABASE_URL` | see step 2 | Required. Transaction pooler, port 6543, user `store_app.<project ref>`. |
| `STORE_NAME` | `Acme Supply` | Shown in the header |
| `MEMBERSHIP_FEE` | `$500` | Shown on the join and pay pages |
| `PAYMENT_DETAILS` | `Bank: …  Account: …  Routing: …` | Where members send the deposit. Shown exactly as written. |
| `STORE_TZ` | `America/Los_Angeles` | Default; used for order times and exports |
| `RECEIPT_DAYS` | `90` | Default; transfer receipts older than this are deleted automatically |
| `MAP_CENTER` | `32.7157,-117.1611` | Default (San Diego); where the delivery map opens before a member sets a pin |
| `ADS_ENABLED` | `1` | Default. Set to `0` to switch every ad off; the games keep working. |

`vercel.json` sets the security headers for the games, which Vercel serves straight from `public/`. Cookies are marked secure automatically on Vercel. More staff logins: create them in the app under **Members → Give someone a login**.

**Rotating the database password.** In Supabase's SQL editor, run `ALTER ROLE store_app PASSWORD 'new-long-random-password';`. Then update `DATABASE_URL` in Vercel and redeploy.

**Fresh database elsewhere?** `schema.sql` creates the same tables in any Postgres. Every table gets row-level security with no policies, so a REST API in front of the database can't read them; the app connects as the tables' owner.

## Run locally / test

```bash
DATABASE_URL=… python3 app.py setup     # tables (same as schema.sql)
DATABASE_URL=… python3 app.py add-staff you@company.com "Your Name" "+1 619 555 0100"
DATABASE_URL=… python3 app.py           # http://127.0.0.1:8000
TEST_DATABASE_URL=postgresql://user@localhost/postgres python3 -m unittest test_app
```

The tests create their own throwaway database on that server and drop it afterwards. Never point them at a server you can't create databases on.

## What it does

| Who | Can |
|---|---|
| Visitor | Play the mini games (2048, Clumsy Bird). The shop isn't shown until they log in. |
| Joined, not yet paid | Log in, browse public products and prices, and see how to pay the one-time membership (amount, your account details, their APP number for the memo) |
| Premium member | Member prices, members-only products, placing orders, order history |
| Staff (`/admin`) | Dashboard, orders, members, products, drivers, audit log |

**Admin dashboard (`/admin`)**

- **Sign-ups waiting for approval.** Type the deposit reference and click approve, or reject.
- **Recent orders.** Each order has a **Copy** button that puts the driver message (customer, phone, address, map link, items, amount to collect) on your clipboard for WhatsApp.

**Other admin pages**

- **Members.** Everyone who signed up. Here you can:
  - create logins yourself (a premium member, e.g. someone who paid in person, or a staff login)
  - approve, reject or revoke a member
  - set a new password for a member (this logs them out everywhere)
- **Order page.** Assign a driver, set the status and payment, copy the message, or open WhatsApp straight to the driver.

**Ads (`/admin/ads`)**

- Add a banner (image plus your affiliate link) or paste an ad network's code, and pick where it shows: top banner, in the game grid, right column (wide screens), or before a game (with a skip button after 5 seconds).
- Ads show only on the games pages, never in the shop, account or admin, and always carry an "Ad" label.
- Ads marked "Gambling ad" are held and never shown: the games pages are for all ages, and the product spec keeps gambling ads off them until there is an age-checked adult area and an approval (FR-008, FR-018).
- Country rules use the visitor's country from Vercel: show an ad only in some countries, or never in others. New ads start hidden in the US; online casino ads are illegal to show in most US states. Clear it only after legal advice.
- Banner clicks are counted; network ads report in the network's own dashboard. Pasted network code runs boxed in, so it can't read your pages or logins.

**Photos, receipts and storage**

- **Product photos.** The shop is a photo grid. Staff add one photo per product. Phone photos are shrunk in the browser before upload (a 3,000-pixel photo is stored as about 30 KB), and replacing a photo deletes the old one. Photos are only served to logged-in users, and members-only product photos only to members and staff.
- **Transfer receipts.** When the driver sends the customer's transfer screenshot on WhatsApp, staff add it on the order page. If the order was still due, it is marked *paid by transfer*. Only staff can see receipts.
- **Automatic cleanup.** Each order keeps only its latest receipt, and receipts are deleted `RECEIPT_DAYS` after upload (90 by default). Cleanup runs whenever staff open the dashboard or the Export page; there's nothing to schedule. Orders, payments and the audit log are never deleted, and each deleted receipt is noted in the audit log.
- **Export (`/admin/export`).** CSV downloads that open in Excel: orders, order lines, members, products and the audit log. The page also shows how much space images use.
  - Password hashes and images are never included.
  - Cells that would run as Excel formulas are neutralised.
  - Phone numbers show exactly as typed.
  - Each download is logged.

**Delivery map**

- On the order form, members drag the pin (or tap the map, or press **Use my current location**). The pin is optional; without one, the typed address is used.
- **Address style.** The map writes the address in the local style. In Mexico the colonia is included and the street comes before the number: "Avenida Juárez 123, Col. Zona Centro, Ensenada, Baja California 22800". In the US: "245 Market Street, Gaslamp Quarter, San Diego, California 92101". The map isn't limited to one country.
- **Two addresses.**
  - The map's address appears under the map as "Map address: …".
  - The delivery address box is the member's own wording. The pin fills it in only while it's empty or still matches the map. Once they've edited it, moving the pin never overwrites their text.
  - Both are saved. When they differ, both are shown to the member (order history), to staff (order page, orders table) and to the driver (WhatsApp message), and both appear in the orders export.
- The exact pin is saved with the order. The driver's WhatsApp message and the staff order page link to that spot in Google Maps. The next order starts at the member's last pin.
- The map is OpenStreetMap (free, no key). Two outside services are involved:
  - **The map library (Leaflet 1.9.4)** loads from unpkg, pinned to an exact version and locked with a fingerprint, so a tampered copy is refused.
  - **The address lookup** uses OpenStreetMap's free Nominatim service. Only the pin's coordinates are sent, once per placement. That service is meant for light use, which suits order volume.
- If the map can't load, the form falls back to typing the address.

**Rules the app enforces**

- **Server-side enforcement.** Prices and visibility are decided on the server. Members-only products are never sent to anyone who isn't an approved member, and only approved members can order. Revoking takes effect immediately.
- **Stock.** It can't oversell: a failed order rolls back completely. Cancelling returns stock, and cancelled orders are final.
- **Payment at delivery.** Every order is due on delivery and the amount to collect is the full total. The customer pays the driver in cash or by transfer, and staff record which. An order can't be marked delivered until that's recorded.
- **Audit log.** Sign-ups, approvals (with deposit reference), logins created, password resets, orders, status/payment changes, price/stock edits and WhatsApp handoffs are all recorded with who did it.

## More context

- `CLAUDE.md`: builder's brief (code map, rules that must not break, gotchas, how to change things). Read it before editing.
- `docs/DECISIONS.md`: why it's built this way, including the owner's choices.
- `docs/DATABASE.md`: tables, the live Supabase setup and migrations, and how to apply changes.
- `docs/BACKLOG.md`: what to verify after deploying, what was cut on purpose, open questions and risks.

## Before selling anything restricted

Mark regulated products **Members only** and add them only after your lawyer and customs broker confirm each exact product is FDA-authorized and lawful to sell where you deliver. Approve members only after checking ID (and the license, for businesses). The software enforces who sees what, but it does not make a product legal to sell.
