# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

- **Visitors:** anyone who lands on the site. They see a free mini games portal and play in the browser, on phones as much as desktops. No account needed.
- **Members:** customers of a small distribution business in the San Diego / Baja California area. They log in, pay a one-time membership by bank transfer, get approved by staff, then browse products and order for delivery, paying the driver on delivery.
- **Staff:** run approvals, orders, driver handoffs over WhatsApp, products, receipts and CSV exports from `/admin`, mostly on a desktop during the working day.

## Product Purpose

One app with three areas: a public games portal, a members' shop behind login, and a staff admin. Visitors only ever see the games; the shop exists only for logged-in users. Success is a portal that feels like a real games site, a shop members can order from quickly, and an admin staff can run the day from.

## Positioning

Owner's choice (2026-10-24): the public front is a games portal; nothing about the shop is visible before login. (Inferred from the request; not a public claim.)

## Operating Context

- Deployed on Vercel from GitHub; Postgres on Supabase. Static files in `public/` are served by Vercel's CDN.
- Orders are dispatched to drivers by WhatsApp; addresses may be in the US or Mexico.
- Staff check ID before approving members; sign-up requires confirming 21+.

## Capabilities and Constraints

- Two games today, both open-source and shipped unmodified apart from small integration edits: 2048 (MIT) and Clumsy Bird (GPL-3.0, keep its license and source link).
- No player accounts, scores, friends, notifications or bookmarks. "Continue playing" lives in the visitor's own browser.
- Server-rendered pages from one Python file, one small script at `/app.js`, strict CSP (scripts from self and the pinned Leaflet build only).
- Site name comes from `STORE_NAME` (confirmed: no separate site name).
- Undecided: whether Join stays public or staff create every login; Spanish or bilingual copy (today all text is English).

## Brand Commitments

- Visual reference pinned by the owner: a dark games portal in the manner of crazygames.com (top bar with search, left icon rail, "Continue playing" row, big tile grid). Follow the layout and feel; never use that site's name, logo, mascot or art.
- The whole platform (games, shop, account, admin) shares the portal's look (confirmed).

## Evidence on Hand

- Game art and code in `public/games/2048/` and `public/games/clumsy-bird/`; gameplay clips and posters recorded from the games themselves.
- No logo, testimonials, player counts or ratings exist. Do not invent any.

## Product Principles

1. The games come first for visitors; the shop never leaks before login.
2. Only real affordances: every icon and button does something today.
3. Fast on a phone: heavy media loads only when someone asks for it.
4. Staff screens stay scannable; the portal look never costs them speed.
