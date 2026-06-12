# Vertical mode — portrait Specimen (1080×1920 Shorts/TikTok cover)

Loaded by `SKILL.md` Step 1 when the user invokes the skill with any of the
vertical keywords: `vertical`, `portrait`, `tiktok`, `shorts`, `reels`, `9:16`,
`1080x1920` (case-insensitive). The skill prints
`Mode: vertical (1080×1920) — Shorts/TikTok cover.` after detection.

This file lists the **deltas** between vertical mode and the default horizontal
Specimen flow. The locked signature still holds in full — base
(`specimen-signature.md`), headline structure (`headline-recipes.md`), accent
palette + the 2-accent / one-punch-row rules (`accent-recipes.md`), the
inline-SVG annotation kit (`annotation-kit.md`), the compositing recipe
(`compositing.md`), the YouTube title pairing (`title-engine.md` +
`title-engine.md`), the iteration recipes, the pre-flight signature
check, and the HARD COMPATIBILITY CONTRACT. Anything not overridden here is
unchanged: **if a horizontal rule isn't contradicted below, it applies.**

The portrait *rhythm slots* (Variant A wide-recap, B stacked-staccato, C
headline+kicker) used to live in `text-rephrase-vertical.md`; that file is folded
into §3 here. The horizontal headline recipe still governs direction, the punch
row, the accent rules, and the mono tell — §3 only adjusts row count, character
budget, and the kicker.

This mirrors `video-director/reference/portrait-mode.md` for compositions: same
1080×1920 canvas, same phone-UI safe-area thinking, same "layout reflows, the
signature does not" principle.

## 1. When this doc applies

Loaded only when mode = vertical. Mode resolution lives in `SKILL.md` Step 1.
Modes are fully independent: a video can carry both a horizontal `round-3/` and a
vertical `round-1-vertical/` at once (§6).

## 2. Canvas + layout overrides (Step 7)

- **Canvas: 1080×1920.** Driven by a single class — the `.thumbnail` `<div>` gets
  an additional `vertical` class via the `THUMBNAIL_CLASS` token. The CSS block
  under `.thumbnail.vertical` in `templates/styles.css` flips `--canvas-w` /
  `--canvas-h` and reflows the face + headline. No literal-dimension edits — set
  the class and let the cascade do the rest.
- **Body-size override (single-file render fix).** `styles.css` sizes
  `html, body` from `:root` (1280×720) and `.thumbnail.vertical` only overrides
  the canvas vars on *itself* — so the body stays 720px tall and the single-file
  renderer clips everything below y=720. Add
  `<style>html, body { width: 1080px; height: 1920px; }</style>` in each variant's
  `<head>`, right after the `STYLES_HREF` link. (Until the shared template bakes
  this in, every `a/b/c.html` needs it.)
- **Face — centered, upper-biased.** Horizontal bleeds the still off the right
  edge; portrait centers it. `.thumbnail.vertical .face-wrap` resolves to
  `right: 50%; transform: translateX(50%); height: 1100px`, anchored to the
  bottom by the shared `.face-wrap { bottom: 0 }`. The taller cutout (1100px vs
  the horizontal 760px) fills the upper two-thirds of the frame and bleeds down
  behind the bottom-anchored headline. The `.face-glow` disc and the cool grade
  carry over unchanged; `.thumbnail.warm` still kills the disc for warm/blonde
  subjects. Same user-supplied + defringed source (`compositing.md`).
- **Headline — bottom-anchored, centered.** `.thumbnail.vertical .thumbnail-text`
  resolves to `top: auto; bottom: 150px; left: 72px; right: 72px; transform:
  none; text-align: center; align-items: center`. The headline reads up from the
  bottom band instead of left-aligned beside the face. The 2-tone structure is
  identical — white flanking rows + ONE `.punch.accent` row + the `.mono-tell`
  (now `text-align: center`).
- **Font formula (flanking row size).** The centered column is
  920px wide (`1080 − 72 − 72 ≈ 936`, budget 920):
  `ROW_FONT_SIZE_PX = floor(920 / (longest_row_chars * 0.6))`, capped at 220,
  floored at 90. A computed size below 90px is a **hard reject** — rephrase
  shorter, never shrink past the floor (small type loses on a phone screen).
  Remember `.punch` renders at `1.7em` of this base, so the punch row is usually
  the row that decides the fit — run the formula against the longest *effective*
  row at its rendered size.
- **Variant C kicker.** Row 3 inherits `font-size: 0.6em` from
  `.thumbnail.vertical .thumbnail-row.kicker`. Size rows 1–2 with the formula; the
  computed kicker pixel size (0.6 × dominant) must still clear the 90px floor.
- **Variant B extra rows.** Stacked staccato uses 4–5 rows via the `TITLE_ROW_4`
  and `TITLE_ROW_5` tokens. Variants A and C leave them `""`; the
  `.thumbnail-row:empty` rule hides unused spans.
- **Safe areas (mirror `portrait-mode.md`).** Keep payoff content out of the
  phone-UI danger zones — top ~220px (clock/status + "Shorts" label), bottom
  ~320px (title + like/share rail + the native Subscribe button), right ~120px
  gutter (action rail). The bottom-anchored headline at `bottom: 150px` already
  sits above the worst of the bottom band, but verify against the `?grid` overlay
  before shipping — the renderer grades portrait legibility harder because the
  delivery surface is a phone. Decorative bleed (face, grid, glow) into the
  danger zones is fine; the punch word and mono tell must stay legible.

## 3. Text rephrase rhythms (Step 3) — folds in `text-rephrase-vertical.md`

In vertical mode each variant slot is **locked to a rhythm pattern** in addition
to the headline direction triad. This is the portrait replacement for the
horizontal worked examples in `headline-recipes.md` — the direction moves
(softer→harder, question→declarative, narrow→sweeping, adjective upgrade), the
one-punch-row rule, the accent rules, and the mono tell all carry over unchanged;
only row count, per-row character budget, and the kicker differ.

The user judges the round on **which rhythm pulls them in**, not just which
words. Do not make the three texts paraphrase one beat with different line breaks
— that defeats the differentiation. Each variant is a different cover for a
different audience: A reads like an article headline, B like a TikTok meme cover,
C like a magazine front.

### Shared constraints (apply across A, B, C)

- ALL CAPS for the headline. Always.
- Exactly ONE `.punch.accent` row per variant — never zero, never two. Accent is
  a ROW CLASS (`punch accent`), never an inner `<span>`.
- Max 2 accent regions per variant (the punch row + at most one mono `.stat`).
- No question marks, ellipses, colons, parentheses, emoji, scribble arrows.
- The mono tell carries a concrete searchable/authority number when the topic has
  one; omit it (`MONO_TELL=""`) rather than ship filler.
- The text column is 920px wide; the font formula and 90px floor in §2 apply.

### Variant A — wide recap (direction: direct upgrade)

- Rows: exactly 3 (one is the `.punch.accent` row).
- Words/row: 3–6. Chars/row incl. spaces: 9–14.
- Reads top-to-bottom as one complete phrase with comma rhythm.
- Punch row = the **topic noun** (Variant A's default punch word). Anchors search
  intent. Expected dominant punch size ≈ 110–135px after the 1.7em multiplier.

Worked example — working title *"Why text is hard"*:

```
STOP GUESSING          (white)
AT HOW TEXT            (white)
GETS RENDERED          (punch accent — or punch the topic noun TEXT on row 2)
```

Mono tell: `// 1,114 scripts in Unicode`.

### Variant B — stacked staccato (direction: punchy declarative)

- Rows: 4–5 (the most tabloid rhythm; one is the `.punch.accent` row).
- Words/row: 1–2. Chars/row: 4–9.
- Poster / sticker tone — one beat per row, each row stands alone.
- Punch row = the **tension verb or payoff word**. Expected dominant punch size ≈
  150–180px.

Worked example — working title *"Why text is hard"*:

```
TEXT                   (white)
IS                     (white)
HARDER                 (punch accent)
THAN                   (white)
YOU THINK              (white)
```

Mono tell: `// 0 pixels are where you think`. (Keep the topic noun present in a
white row when the punch is a verb — searchable-noun discipline still applies.)

### Variant C — headline + kicker (direction: sweeping reframe)

- Rows: exactly 3. Rows 1–2 carry the emotional claim; row 3 is the **kicker**
  that grounds it (`.kicker`, rendered at 0.6em).
- Rows 1–2: 1–3 words each, 4–9 chars each. Dominant punch size ≈ 170–220px
  (4 chars hits the 220px cap; 9 chars lands ≈ 170px).
- Row 3 (kicker): 3–6 words, 14–18 chars. The computed kicker size (0.6 ×
  dominant) must clear the 90px floor — shorten the kicker or drop the row if not.
- Punch row = the **reframed-stakes word** on row 1 or 2.

Worked example — working title *"Why text is hard"*:

```
TEXT                   (white)
RENDERING              (punch accent)
THE LAYER NOBODY SEES  (kicker — grounds, stays unaccented here)
```

Mono tell: `// 100,000+ glyphs to place`.

**Variant C accent placement.** By default the punch (accent) lands on row 1 or
2 and the kicker stays a quiet white anchor. **Alternative:** accent row 1 *plus*
a single word inside the kicker when the kicker carries the surprise rather than
grounding — but pick ONE accent strategy per variant, never mix, and the 2-accent
cap still holds (a kicker accent counts against it). The accent stays a ROW CLASS
on the kicker row, never an inner span — localization re-fills the row.

## 4. Accent + annotation (Steps 5, 8)

Both inherit the horizontal references unchanged: the accent palette and the
default-cool / red-reserved rule from `accent-recipes.md` + `specimen-signature.md`,
and the inline-SVG annotation kit (precision pointer / bracket / ring / underline
/ callout, stroke inheriting `var(--accent)`) from `annotation-kit.md`. No
portrait-specific accent or annotation behavior — the same `acc-*` class, the
same per-video-hue logic, the same "place endpoints by reading the `?grid`
overlay" discipline. The grid overlay's axis labels and the safe-area / crop
markers auto-switch to 1080×1920 when `.thumbnail` carries `vertical` (the
`cg-init` snippet in `variant.html` reads the class).

## 5. Brand chip (Step 7)

The optional `.chip` carries over unchanged — same `--chip-bg` / `--chip-ink`
overrides, same "keep it visually distinct from the accent" rule. Position it for
the portrait layout via its inline `left`/`top`/`width`/`height` (read the `?grid`
overlay); a common spot is tucked beside the face's lower edge, clear of the
bottom safe band.

**Faceless brand covers — the logo IS the focal mark.** When a vertical cover is
*faceless* (no face still — the parent shipped faceless, or the topic has no
creator face) **and** the topic IS a nameable brand, promote the brand's real
logo from a corner chip to the **focal mark**: place it in the upper third (the
slot a face would occupy), ~240–300px, clear of the top ~220px Shorts-UI safe
zone, above the centered headline. With no face, the logo is what carries brand
recognition at feed scale — this is the vertical equivalent of "the face is the
subject."

- Source via the icon CLI (`logos:*` for native-color marks — WhatsApp, Slack,
  Firefox; `simple-icons:*` for monochrome), drop the `body` verbatim into an
  inline `<svg>`. **Never mutate the body to recolor** — `logos:*` keeps native
  brand colors.
- Position it **absolutely, NOT inside a `thumbnail-row`** (same contract as the
  chip): `left:50%; transform:translateX(-50%); top:≈300px`.
- Give it a soft `drop-shadow` glow in the accent hue so it harmonizes with the
  punch row, and nudge the headline block down (e.g. `top:54%`) so logo +
  headline read as one column with the bottom safe band clear.
- **Face-present** vertical covers keep the small corner chip (above) — the face
  is still the subject. Faceless + brand → focal logo; face-present → corner chip.

## 6. Round folder + filenames (Steps 7, 10)

- Round folder: `<video-dir>/thumbnails/round-N-vertical/`.
  - "Next round" is **mode-scoped**: scan only entries matching
    `round-(\d+)-vertical` and pick `max + 1`. The horizontal and vertical
    counters are independent (a video can have `round-3/` and `round-1-vertical/`
    simultaneously).
- Variant files inside the round folder keep their names: `a.html`, `b.html`,
  `c.html`, `contact-sheet.html`. The `vertical` wrapper class differentiates
  them, not the filename — part of the HARD COMPATIBILITY CONTRACT.
- Render output filenames: `<video-dir>/thumbnail-vertical-a.png`,
  `thumbnail-vertical-b.png`, `thumbnail-vertical-c.png`.

## 7. Contact sheet additions (Step 7)

The contact sheet's `{{VARIANTS_HTML}}` slot is filled with three copies of the
**vertical** per-variant block (instead of the horizontal block from `SKILL.md`
Step 7). It keeps the `variant-letter` / `variant-text` / `variant-yt-text`
spans that `create-srt` `extract_titles.py` parses — never rename or drop them:

```html
<div class="variant variant-vertical">
  <div class="variant-header">
    <span class="variant-letter">{{LETTER_UPPER}}</span>
    <span class="variant-text">{{TITLE_PLAIN}}</span>
  </div>
  <div class="variant-yt-title">
    <span class="variant-yt-label">YouTube title</span>
    <span class="variant-yt-text">{{YOUTUBE_TITLE}}</span>
  </div>
  <div class="row vertical-row">
    <div>
      <div class="row-label">Full size (1080×1920 @ 25%)</div>
      <div class="full-wrap-vertical">{{THUMBNAIL_DIV}}</div>
    </div>
    <div>
      <div class="row-label">Shorts feed (~140×248)</div>
      <div class="shorts-wrap">{{THUMBNAIL_DIV}}</div>
    </div>
    <div>
      <div class="row-label">TikTok profile grid (1:1 crop, ~180×180)</div>
      <div class="profile-grid-wrap">{{THUMBNAIL_DIV}}</div>
    </div>
  </div>
  <div class="variant-links">
    <a href="{{LETTER_LOWER}}.html">view full</a> ·
    <a href="{{LETTER_LOWER}}.html?grid">view with grid</a>
  </div>
</div>
```

`{{THUMBNAIL_DIV}}` is the same `.thumbnail.vertical` markup used in `a.html` /
`b.html` / `c.html`, inlined three times. The three wrap classes CSS-scale the
inner thumbnail to simulate each delivery surface:

- `full-wrap-vertical` — scales the 1080×1920 thumbnail to 25% (~270×480).
- `shorts-wrap` — scales further (~140×248) to simulate the YouTube Shorts feed
  grid cell — the size that actually decides the click.
- `profile-grid-wrap` — exactly 180×180, centering the inner thumbnail so only
  the `y=420–1500` band is visible: the TikTok profile-grid 1:1 crop.

### Profile-grid crop caveat (always surface to the user)

The portrait layout puts the face in the upper two-thirds and bottom-anchors the
headline. The TikTok profile-grid 1:1 crop is centered at `y=420–1500`, so it
catches the face but clips the bottom-anchored headline — no single centered
1080-tall crop captures both the face *and* a low headline.

This is a layout/surface trade-off, not a bug. When presenting the round, tell
the user which variant survives the crop:

- **Variant A (3 rows, wide recap):** the headline sits low; most of it falls
  below the TikTok profile crop. Reads fully on the YouTube Shorts feed (which
  shows the whole 9:16 frame), but on a TikTok profile grid most of the rephrase
  is invisible.
- **Variant B (4–5 rows, stacked staccato):** the taller stack pushes more rows
  up into the centered 1:1 crop. **Best variant for TikTok profile-grid
  legibility** — surface this when the user is posting to TikTok rather than
  YouTube Shorts.
- **Variant C (3 rows + kicker):** same constraint as A; the punch row may be
  partially visible but the kicker falls below the crop.

The `profile-grid-wrap` preview exists specifically to surface this — always
include all three wraps so the user can judge legibility per-surface before
shipping.

## 8. Renderer invocation (Step 10)

```bash
node <repo-root>/tools/thumbnail-render/bin/render.mjs \
  <video-dir>/thumbnails/round-N-vertical \
  --variants \
  --orientation vertical \
  --out-dir <video-dir>
```

Writes `thumbnail-vertical-{a,b,c}.png` into `<video-dir>`. The renderer
validates that the round-dir `-vertical` suffix and the `--orientation vertical`
flag agree, and strips `?grid` so the coordinate overlay never reaches the PNG.
