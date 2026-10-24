---
name: Store
description: A dark arcade games portal whose shell also carries the members' shop and the staff admin.
colors:
  ink: "#0d0e17"
  ink-1: "#161724"
  ink-2: "#212335"
  ink-3: "#2d3048"
  ink-4: "#383b58"
  line: "#2a2c42"
  fg: "#f4f4fb"
  fg-2: "#a6a8c4"
  violet: "#6c4cff"
  violet-deep: "#5a3af0"
  violet-hi: "#9c87ff"
  bad: "#ff6b81"
  good: "#46d6a0"
typography:
  display:
    fontFamily: "Nunito, ui-rounded, Segoe UI, system-ui, sans-serif"
    fontSize: "1.75rem"
    fontWeight: 900
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  headline:
    fontFamily: "Nunito, ui-rounded, Segoe UI, system-ui, sans-serif"
    fontSize: "1.3rem"
    fontWeight: 900
    lineHeight: 1.15
    letterSpacing: "-0.01em"
  title:
    fontFamily: "Nunito, ui-rounded, Segoe UI, system-ui, sans-serif"
    fontSize: "1.1rem"
    fontWeight: 900
  brand:
    fontFamily: "Nunito, ui-rounded, Segoe UI, system-ui, sans-serif"
    fontSize: "1.25rem"
    fontWeight: 900
    letterSpacing: "-0.02em"
  body:
    fontFamily: "Nunito, ui-rounded, Segoe UI, system-ui, sans-serif"
    fontSize: "16px"
    fontWeight: 600
    lineHeight: 1.5
  label:
    fontFamily: "Nunito, ui-rounded, Segoe UI, system-ui, sans-serif"
    fontSize: "0.95rem"
    fontWeight: 800
  label-sm:
    fontFamily: "Nunito, ui-rounded, Segoe UI, system-ui, sans-serif"
    fontSize: "0.85rem"
    fontWeight: 800
  caption:
    fontFamily: "Nunito, ui-rounded, Segoe UI, system-ui, sans-serif"
    fontSize: "0.7rem"
    fontWeight: 800
  mono:
    fontFamily: "ui-monospace, monospace"
    fontSize: "13px"
    lineHeight: 1.45
rounded:
  check: "6px"
  tip: "8px"
  field: "10px"
  rail-item: "12px"
  media: "14px"
  pill: "999px"
spacing:
  xs: "6px"
  sm: "10px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  bar: "64px"
  rail: "76px"
  rail-wide: "220px"
components:
  button-primary:
    backgroundColor: "{colors.violet}"
    textColor: "{colors.fg}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "9px 18px"
  button-primary-hover:
    backgroundColor: "{colors.violet-deep}"
  button-secondary:
    backgroundColor: "{colors.ink-3}"
    textColor: "{colors.fg}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "9px 18px"
  button-secondary-hover:
    backgroundColor: "{colors.ink-4}"
  pill-bar:
    backgroundColor: "{colors.violet}"
    textColor: "{colors.fg}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    height: "40px"
    padding: "0 18px"
  round-button:
    backgroundColor: "{colors.ink-3}"
    textColor: "{colors.fg}"
    rounded: "{rounded.pill}"
    size: "40px"
  input-search:
    backgroundColor: "{colors.ink-3}"
    textColor: "{colors.fg}"
    rounded: "{rounded.pill}"
    height: "44px"
    padding: "0 52px 0 22px"
  input-field:
    backgroundColor: "{colors.ink-2}"
    textColor: "{colors.fg}"
    rounded: "{rounded.field}"
    padding: "9px 12px"
  rail-item:
    textColor: "{colors.violet-hi}"
    rounded: "{rounded.rail-item}"
    size: "48px"
  rail-item-active:
    backgroundColor: "{colors.ink-3}"
    textColor: "{colors.fg}"
  chip-tab:
    backgroundColor: "{colors.ink-2}"
    textColor: "{colors.fg-2}"
    rounded: "{rounded.pill}"
    padding: "6px 14px"
  chip-tab-active:
    backgroundColor: "{colors.violet}"
    textColor: "{colors.fg}"
  game-tile:
    backgroundColor: "{colors.ink-2}"
    textColor: "{colors.fg}"
    rounded: "{rounded.media}"
  thumb:
    rounded: "{rounded.media}"
    size: "112px"
  card:
    backgroundColor: "{colors.ink-1}"
    rounded: "{rounded.media}"
    padding: "10px 14px 14px"
---

# Design System: Store

## Overview

**Creative North Star: "The Arcade After Dark"**

A games portal at night: an ink-navy ground that steps up in quiet surface levels, the games' own art and moving footage as the only bright colour on the page, and chrome that recedes until it is needed. One electric violet marks what you can do; everything else is ink, white heavy type, and rounded media. The shell is shared by every area of the site, so the members' shop and the staff admin wear the same material in a calmer, denser register.

Density is relaxed on the games home (big tiles, a 112px "Continue playing" shelf) and tight in the staff pages (tables at 10px cell padding, pill tabs). Nothing is bordered for decoration: surfaces separate by tone, and the only hairlines are table rules, field strokes and the phone bottom bar's top edge. Motion is short and springy, and it always answers a pointer or focus; nothing animates by itself.

**Key Characteristics:**
- Dark ink ground with three surface steps (ink-1 bars, ink-2 wells, ink-3 controls) and no decorative borders.
- One violet for action, selection, the brand mark and the focus ring.
- Nunito throughout, heavy: body at 600, labels at 800, headings at 900.
- Pills for every control; 14px rounded media for every picture.
- Live tiles: a silent gameplay clip crossfades over the poster on hover or keyboard focus.

## Colors

A near-black blue-violet ink in four steps, one saturated violet with a lighter and a deeper partner, and two status tints.

### Primary
- **Arcade Violet** (violet): the action colour. Primary buttons and pills, the selected staff tab, the active rail marker bar, checked checkboxes, the signed-in avatar, text selection, the brand mark's square.
- **Pressed Violet** (violet-deep): hover state of every violet button. It is a literal in the stylesheet, not a custom property.
- **Lit Violet** (violet-hi): the light violet for focus outlines, the hover ring on tiles and thumbs, links, the caret, and resting rail icons.

### Neutral
- **Night Ink** (ink): the page ground and the html scrollbar track.
- **Bar Ink** (ink-1): top bar, icon rail, product cards, empty states.
- **Well Ink** (ink-2): form fields, staff tab chips, tile placeholders before the poster loads, preformatted blocks.
- **Control Ink** (ink-3): search field, ghost pills, round icon buttons, the active rail item's tile, tooltips, the file button.
- **Raised Ink** (ink-4): hover state of ink-3 controls. A literal in the stylesheet, like violet-deep.
- **Hairline** (line): table rules, field strokes, rail divider, the phone bottom bar's top edge.
- **Paper White** (fg): all primary text, and the text on violet.
- **Mist** (fg-2): secondary text, placeholders, table headers, field labels, inactive tabs, struck-through prices.

### Tertiary
- **Alert Rose** (bad): error notes (as an 8% tint with a 33% stroke) and destructive staff buttons (rose text with a rose inset ring, no fill).
- **Mint** (good): success notes, as a 7% tint with a 30% stroke.

### Named Rules
**The One Violet Rule.** Violet means "you can act here" or "you are here". It never fills a surface, a section or a card, and no second accent hue joins it.

**The Art Brings the Colour Rule.** The game posters and clips are the only full-colour content on the page. The interface stays in ink and violet so the games read first.

## Typography

**Display Font:** Nunito, self-hosted variable woff2 (200–1000), with ui-rounded, Segoe UI, system-ui fallbacks
**Body Font:** Nunito (same file)
**Label/Mono Font:** ui-monospace, only for the read-only driver message boxes in staff pages

**Character:** One rounded humanist face set heavy from top to bottom, so the portal reads friendly and game-like without a second display face.

### Hierarchy
- **Display** (900, 1.75rem, 1.15, -0.01em): page titles, and the featured tile's game name (shrinks to 1.3rem on phones).
- **Headline** (900, 1.3rem, 1.15): section heads such as "Continue playing", "Play now", "Add product".
- **Title** (900, 1.1rem): game names on standard tiles (1.05rem on phones); product prices at 1.05rem.
- **Brand** (900, 1.25rem, -0.02em): the store name beside the mark (1.1rem on phones).
- **Body** (600, 16px, 1.5): all running text, table cells and inputs. Notes cap at 72ch.
- **Label** (800, 0.95rem): buttons, pills and staff tabs (0.9rem).
- **Small label** (800, 0.85rem): table headers, shelf captions, rail tooltips.
- **Caption** (800, 0.7rem): bottom-bar labels on phones only.

### Named Rules
**The Heavy Default Rule.** Nothing ships lighter than 600. Hierarchy comes from size and the 600 / 800 / 900 steps, not from thin weights or uppercase tracking.

**The Legible-Over-Art Rule.** Text set on game art sits on a bottom-up ink gradient (72% to 0) and carries a soft dark text shadow, so the art keeps its colours and the name still reads.

## Layout

A fixed app shell: a sticky 64px top bar (menu toggle, brand, a centred pill search up to 760px, account actions on the right) and a fixed 76px icon rail on the left. The menu toggle widens the rail to 220px with labels; the choice is remembered in the browser. Content sits in `main` beside the rail, padded 32px on the sides, capped at 1500px wide.

The games home leads with a "Play now" row of two tiles split 3fr / 2fr, the featured game on the left; further tiles fill an auto grid with a 400px minimum track and 16px gaps. Each tile keeps its art's own aspect ratio (square, or 3:2 for wide art), so nothing is cropped. "Continue playing" is a horizontal scroll-snapped shelf of 112px thumbs with 14px gaps, shown only when this browser has history. Shop products use a 190px-minimum card grid.

At 720px and below the rail becomes a fixed bottom bar with icon-and-caption items, the search drops to its own full-width row under the brand, tiles stack in one column at 12px gaps, the product grid becomes two columns, and main reserves 96px plus the safe-area inset at the bottom. At 700px and below, staff tables reflow into stacked cards.

Spacing rhythm: 6 / 10 / 16 / 24 / 32px, with 12 and 14px used inside controls and tiles.

## Elevation & Depth

Flat, layered by tone. Surfaces sit on the ground as lighter ink steps (ink, then ink-1, ink-2, ink-3) with no resting shadows. Shadow appears only as a response to pointer or focus, and only on media.

### Shadow Vocabulary
- **Lit ring** (`box-shadow: 0 0 0 3px var(--violet-hi)`): hover and focus on Continue-playing thumbs.
- **Lifted tile** (`box-shadow: 0 0 0 3px var(--violet-hi), 0 16px 32px -12px #000d`): hover and focus on game tiles, together with a 4px rise.
- **Field focus halo** (`box-shadow: 0 0 0 3px #6c4cff55`): focused inputs, with the stroke turning violet-hi.
- **Label shadow** (`text-shadow: 0 1px 3px #000c, 0 0 12px #0009`): game names on art.

### Named Rules
**The Flat-At-Rest Rule.** Nothing casts a shadow until someone points at it or tabs to it. Depth at rest is tone alone.

## Shapes

Everything is rounded and nothing is sharp. Interactive controls are full pills (999px): buttons, search, staff tabs, the file picker button, round icon buttons. Media and containers share one 14px radius: game tiles, thumbs, product cards, empty states, the map. Fields, notes, preformatted blocks, receipt and product thumbnails use 10px; rail items 12px; tooltips 8px; checkboxes 6px. The brand mark is a 34px violet square at 10px radius with a white play triangle. Media is clipped to its radius and carries no border.

## Components

### Buttons
Soft, heavy and pill-shaped.
- **Shape:** full pill (999px).
- **Primary:** violet fill, white 800-weight label, 9px 18px padding (40px tall in the top bar and on tiles).
- **Hover / Focus:** fill deepens to violet-deep over 0.2s; focus shows the global 2px violet-hi outline at 2px offset.
- **Secondary / Ghost:** ink-3 fill with white text, hover to ink-4. Used for "Join" and secondary form actions.
- **Destructive:** no fill, rose text and a 1px rose inset ring (reject, revoke).
- **Text link button:** no fill, violet-hi underlined text.
- **Round icon button:** a 40px ink-3 circle holding a 22px icon (menu, log out); the signed-in avatar is the same circle in violet with the user's initial.

### Chips
- **Style:** staff tabs are 6px 14px pills on ink-2 in Mist text, 800 weight at 0.9rem.
- **State:** hover lifts the text to white; the current tab fills violet with white text.

### Cards / Containers
- **Corner Style:** 14px.
- **Background:** ink-1 for product cards and empty states; ink-2 behind images while they load.
- **Shadow Strategy:** none (see Elevation & Depth).
- **Border:** none.
- **Internal Padding:** 10px 14px 14px in product cards; 40px 24px in empty states.

### Inputs / Fields
- **Style:** ink-2 well, 1px hairline stroke, 10px radius, 9px 12px padding, inherited Nunito 600. Labels sit above in Mist; stacked forms cap fields at 460px.
- **Focus:** the stroke turns violet-hi and a 3px violet halo at 33% appears.
- **Checkbox:** a custom 20px box at 6px radius with a 1.5px Mist stroke; checked fills violet with a white tick.
- **Notes:** error and success notes are 10px-radius tinted boxes with a matching stroke (see Tertiary colours).

### Navigation
- **Top bar:** ink-1, sticky, 64px. The search is a 44px ink-3 pill with a Mist placeholder and a search icon button inside the right end.
- **Icon rail:** ink-1, 48px items at 12px radius holding 22px Lucide icons in violet-hi. Hover gives an ink-3 tile and an ink-3 tooltip label to the right. The current item gets the ink-3 tile, a white icon, and a 4px violet marker bar on the rail's left edge. A hairline divider separates the games entries from the signed-in entries (Shop, Account, Admin).
- **Wide rail:** 220px, icons with their labels inline; same active treatment.
- **Phones:** the rail becomes a bottom bar with icon-over-caption items at 0.7rem; the marker bar is dropped and the active item keeps its ink-3 tile.

### Icons
Lucide paths only, drawn at 24-unit viewBox, 22px, 2px stroke, round caps and joins, currentColor. Every icon stands for a working destination or action.

### Live Game Tile (signature)
The portal's signature. A 14px-radius tile shows the game's real poster frame edge to edge; a muted, looping, inline gameplay clip sits above it at zero opacity. The clip's source is attached only on the first mouse hover or keyboard focus, and it crossfades in over 0.35s once it actually plays; leaving pauses and rewinds it after the fade. At the same moment the tile rises 4px with the lifted-tile ring and shadow, and a violet "Play" pill with a play icon slides up into the bottom-right corner. The name sits bottom-left on the ink gradient; the featured tile adds a one-line description and a larger name. Under reduced motion the clip never loads and transitions are removed. On phones the Play pill and the description are hidden; tapping the tile plays the game.

### Continue Playing Shelf
112px square poster thumbs at 14px radius with a Mist 0.85rem caption beneath. Order comes from the visitor's own browser history (most recent first, up to 12); the section stays hidden when there is none. Hover or focus raises the thumb 3px with the lit ring and turns the caption white.

### Tables (staff)
Full-width, tabular figures, 10px cell padding, a hairline under each row, Mist 0.85rem 800-weight headers. At 700px and below they reflow into stacked cards.

## Do's and Don'ts

### Do:
- **Do** step surfaces by tone (ink, ink-1, ink-2, ink-3) instead of adding borders or resting shadows.
- **Do** keep violet for actions, the current location and focus; reach for ink-3 ghost pills for everything secondary.
- **Do** round every control into a full pill and every picture or container to 14px.
- **Do** use real gameplay frames and clips for game art, loaded only when someone points at or focuses the tile, with a still under reduced motion.
- **Do** set type in Nunito at 600 or heavier, with headings at 900.
- **Do** draw icons from the Lucide set at 22px and a 2px stroke, and only for things that work today.
- **Do** put text that sits on art over the bottom ink gradient with the soft label shadow.

### Don't:
- **Don't** introduce a second accent hue or tint large surfaces violet.
- **Don't** put borders around tiles, thumbs or cards.
- **Don't** autoplay clips or animate anything that a pointer or focus did not ask for.
- **Don't** crop game art into a uniform tile shape; let each tile keep its art's aspect ratio.
- **Don't** set type lighter than 600 or add a second display face.
- **Don't** use the reference portal's name, logo, mascot or art.
