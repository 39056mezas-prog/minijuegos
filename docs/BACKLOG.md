# Backlog

Organized by how urgent it is. Move an item to `docs/DECISIONS.md` once it's decided.

## Verify after the first live deploy (never tested against the real services)

The build environment couldn't reach the internet. Everything below was tested locally against Postgres 16 and a real browser with stand-ins, but not live.

- [ ] **Vercel can connect to Supabase as `store_app` through the transaction pooler** (user `store_app.<project ref>`, port 6543). If that fails, Vercel's **Logs** tab shows the error.
- [ ] **Real map tiles and Nominatim address lookups load on the live site, on a phone.** "Use my current location" needs HTTPS, which Vercel provides.
- [ ] **Copy buttons work on the live HTTPS site.** The clipboard needs HTTPS; the fallback opens the preview to copy by hand.
- [ ] **Both games load from Vercel's CDN with the `vercel.json` headers** (open a game, check the response headers in the browser's dev tools), and play on a phone. Clumsy Bird's music starts after the first tap.
- [ ] **The ads table exists on the live database** before deploying this version, or the games pages fail. See `docs/DATABASE.md` → Migrations.
- [ ] **Country rules work live:** Vercel sends `X-Vercel-Ip-Country`. Open the site from a US connection and from a non-US one (or a VPN) and check that US-hidden ads stay hidden.
- [ ] **A real ad-network tag runs inside its frame.** Some networks refuse to run in sandboxed frames or need more permissions; adjust `AD_FRAME_CSP` and the iframe `sandbox` only for what that network documents.
- [ ] **A photo from an iPhone uploads correctly.** Safari normally converts HEIC to JPEG; desktop Chrome can't read HEIC files and says so.

## Do soon (security housekeeping)

- [ ] **Rotate both passwords that were shared in the build chat:** the `store_app` database password and the first staff login. See `docs/DATABASE.md`; staff change their own under **Members → their name**.
- [ ] **Add login rate limiting.** Login has none yet: either a per-email and per-IP attempt counter in the database, or Vercel's firewall rules.
- [ ] **Unrelated to the store:** Supabase's advisor flagged the other app in conectando-ensenada. Several `SECURITY DEFINER` functions can be called by the public API roles, three extensions are installed in `public`, and leaked-password protection is off.

## Cut on purpose (add when a real need shows up)

| Item | What happens today |
|---|---|
| Online card payment | Payment is on delivery, or by manual deposit for the membership. Needs a processor that approves these products in writing. |
| Membership renewal or expiry | The fee is one-time. |
| Price tiers or customer-specific prices | One public price and one member price per product. |
| Inventory movement ledger | Stock is set as a number. *shortcut:* editing stock overwrites any order placed while the form was open; add a "received +N" field if that bites. |
| Driver cash reconciliation report | Export orders and filter by driver and payment in Excel. |
| WhatsApp Business API (automatic sending, delivery receipts) | A prefilled `wa.me` link plus Copy; staff press Send. |
| License or ID document uploads | Staff check documents outside the app before approving. |
| Reports and dashboards beyond counts | Use the CSV exports. |
| Self-service password reset by email | Staff set new passwords from the member's page. Needs an email provider. |
| Typed address → map pin (forward geocoding) | Members place the pin themselves; the typed address is kept regardless. |

## Open questions for the owner

- [ ] **Gambling ads: the spec or the earlier request?** You asked for casino ads (Brazino) "everywhere we can"; the product spec added later forbids gambling ads on general-audience pages without an adult area and approval. They're held until you decide. Serving them means an age-checked adult area (spec Phase 4) and per-market legal sign-off (Gate D).
- [ ] **The spec asks for a repository audit first** (Phase 0) and describes much more than exists: recurring billing, roles beyond customer/staff, driver logins, campaign approvals and scheduling, jurisdiction flags. Decide which of those to build, in what order.

- [ ] **Should anyone be able to Join from the games site?** Today the Join link is public. The alternative is invite-only: staff create every login (already supported under Members), and the Join page is removed.
- [ ] **Should the site have its own name?** The header still shows `STORE_NAME` on the games pages.

- [ ] **Should some public products be hidden from members?** For example, single units shown only to visitors while members see the bulk pack. This would be a three-way visibility per product: everyone, public only, or members only.
- [ ] **Should members see their own transfer receipt?** Today receipts are staff-only, because they can show bank details.
- [ ] **Should the site be in Spanish, or in both languages?** Today all text is in English.
- [ ] **Should staff accounts have limited roles** (for example, a dispatcher who can't approve members)? Today every staff login has full admin access.

## Known risks

- **Games front.** Putting the shop behind a games site doesn't make anything legal that wasn't, and a games site attracts minors. Keep checking ID before approval; the 21+ box at sign-up is only a self-declaration.
- **Clumsy Bird is GPL-3.0.** Keep `public/games/clumsy-bird/LICENSE.md` and the source link in its `index.html`. If you change its code, publish your changes under the same license.
- **Gambling ads on a games site.** See `docs/DECISIONS.md` #22. Children play these games; casino advertising is restricted in the US, Brazil and Mexico; affiliate terms usually ban sites aimed at minors. Get legal advice before running casino ads.
- **Legal.** Selling vapes or other regulated products needs FDA authorization for each product, plus PACT Act and state and local compliance, whatever the membership model. The software only controls visibility. See `docs/DECISIONS.md` #17.
- **Receipts expire after 90 days.** Save any that matter before then. The orders export only records whether a receipt was on file.
- **Nominatim is a free service meant for light use.** At high volume, move address lookup to a paid provider (only the `fetch` in `APP_JS` and the `connect-src` in the CSP change).
- **Addresses come from OpenStreetMap.** Coverage of colonias varies, so members should check the address before ordering.
- **One shared Supabase project.** If the other app's database work ever drops or recreates schemas carelessly, `store` could be affected. Export regularly.
