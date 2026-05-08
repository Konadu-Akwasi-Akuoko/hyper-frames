# Thumbnail-creator — vertical variant (Shorts / TikTok cover) design

**Status:** approved
**Date:** 2026-05-08
**Owner:** akwasi
**Related:** `docs/superpowers/specs/2026-05-08-thumbnail-creator-design.md`,
`docs/superpowers/specs/2026-05-08-thumbnail-iteration-design.md`

## Goal

Add a vertical (1080×1920, 9:16) output mode to the existing
`thumbnail-creator` skill so it can produce YouTube Shorts and TikTok
cover thumbnails using the same locked visual signature, the same
A/B/C iteration loop, and the same renderer. The default behavior of
the skill (1280×720 horizontal YouTube thumbnails) is unchanged.

## Non-goals

- A separate skill. Vertical mode lives inside `thumbnail-creator`.
- Producing horizontal and vertical in the same round. Each round is one
  orientation; users invoke twice if they want both.
- Square (1:1), banner, or other aspect ratios. Vertical-only for now.
- Animated / video covers. PNG output only.
- Auto-cropping a horizontal thumbnail into a vertical one. Layouts are
  authored per orientation.

## Architecture — Approach B (delta doc)

The vertical mode is captured as a single new reference file,
`reference/vertical-mode.md`, containing only the *deltas* relative to
the existing horizontal flow. `SKILL.md` gains a single sentence at
Step 1 telling future Claude to load the delta doc when in vertical
mode. The rest of `SKILL.md` is unchanged. Anything not mentioned in
the delta doc carries over verbatim — including the hard rules,
visual signature constants, accent caps, and rephrase direction triad.

This keeps the existing horizontal flow untouched, reuses the existing
reference-file pattern (`red-word-recipes.md`, `icon-picking.md`,
etc.), and contains the new feature to one new file plus targeted
edits to templates, styles, the renderer, and SKILL.md Step 1.

Rejected: inline branching (would double the cognitive load of every
SKILL.md step) and full per-orientation parameterization (heavy
refactor for a hypothetical third orientation that hasn't been asked
for).

## Mode invocation

Step 1 is extended to also resolve **orientation mode** alongside the
target video folder.

Detection — first match wins:

1. Explicit user keyword in the invoking message (case-insensitive):
   any of `vertical`, `portrait`, `tiktok`, `shorts`, `reels`, `9:16`,
   `1080x1920` → vertical mode.
2. Otherwise → horizontal mode (current behavior).

The skill prints a one-line confirmation: `Mode: vertical (1080×1920)
— Shorts/TikTok cover.` or `Mode: horizontal (1280×720) — YouTube
thumbnail.`

Round folders are mode-tagged so they don't collide:

- `thumbnails/round-N/` — horizontal (current convention preserved)
- `thumbnails/round-N-vertical/` — vertical

The "next round" computation in Step 7 is mode-scoped: in vertical
mode, scan only `round-*-vertical` directories; in horizontal mode,
scan only un-suffixed `round-*` directories. Modes have independent
counters.

## Vertical canvas and layout

**Canvas:** 1080×1920. New CSS overrides scoped to a `.thumbnail.vertical`
wrapper class:

```css
.thumbnail.vertical {
  --canvas-w: 1080px;
  --canvas-h: 1920px;
}
```

**Zones (icon top, text bottom):**

```
y=0    ┌─────────────────────┐
       │      (padding 120)  │
y=120  │   ┌─────────────┐   │
       │   │             │   │
       │   │    ICON     │   │  720×720, centered
       │   │   720×720   │   │
       │   │             │   │
       │   └─────────────┘   │
y=840  │      (gap 120)      │
y=960  │ ─── visual midline  │
y=1000 │                     │
       │   TEXT ROW 1        │  text zone:
       │   TEXT ROW 2        │  920 px wide,
       │   TEXT ROW 3..N     │  bottom-anchored,
       │                     │  centered horizontally
y=1720 │      (padding 120)  │
y=1840 │  [TT-UI-safe band]  │  marker only (?grid)
y=1920 └─────────────────────┘
```

**Text column:** 920 px wide (1080 − 80 padding each side). The icon
no longer steals horizontal room.

**Font sizing formula (rhythm-aware):**

```
ROW_FONT_SIZE_PX = floor(920 / (longest_row_chars * 0.6))
                   capped at 220
                   floor at 90 (reject below)
```

Higher cap (220 vs 140 horizontal) because vertical row heights can
absorb it. Floor of 90 maintains the same hard-fail principle as
horizontal: never silently shrink past legibility.

**Safe-area markers (visible only with `?grid`, never in rendered PNG):**

- TikTok bottom UI band: y=1440 to y=1920 (bottom 25%) — text MUST
  end above this line.
- Profile-grid square crop boundary: dashed square outline from y=420
  to y=1500, showing what TikTok's profile-grid 1:1 crop will display.
  Layout doesn't have to obey it; it's a judgment aid for the user.

## Text rephrase rhythms (A / B / C)

In horizontal mode, the three variants differ on *direction* (direct
upgrade / sweeping reframe / punchy declarative). In vertical mode,
they additionally differ on *rhythm* — each variant slot has a fixed
rhythm, and the rephrase recipes target that rhythm.

### Variant A — "wide recap"

- 3 rows, 3–6 words each, 9–14 chars each.
- Reads like the horizontal sibling: complete phrase, comma-rhythm.
- Font size: ~110–135 px in the 920 px column.
- Direction: direct upgrade of the working title.

### Variant B — "stacked staccato"

- 4–5 rows, 1–2 words each, 4–9 chars each.
- Reads like a poster — punch one beat per row.
- Font size: ~150–180 px.
- Direction: punchy declarative reframe; the most tabloid-feeling of
  the three.

### Variant C — "headline + kicker"

- Exactly 3 rows in a 2-huge-then-1-small hierarchy.
- Rows 1–2: 1–3 words each, 5–8 chars, font 200–220 px.
- Row 3: 3–6 words, 14–18 chars, font ≈ 60% of rows 1–2 — implemented
  via a `.kicker` class on row 3.
- Row 3 is the qualifier / domain anchor (where the searchable noun
  usually lives).
- Direction: sweeping reframe; the headline does the emotional work,
  the kicker grounds it.

### Hard constraints (across all three rhythms)

- ALL CAPS, no question marks / ellipses / colons / parentheses /
  emoji.
- Max 2 accent regions per variant (unchanged from horizontal).
- Same icon across all 3 variants in a round (unchanged).
- The `longest_row_chars` rule still governs the dominant font size.
  For Variant C, the formula is run on rows 1–2 only (the kicker
  inherits 0.6em from CSS — see Templates section). The kicker's
  computed pixel size (`0.6 × dominant`) must still clear the 90 px
  floor; if it doesn't, rephrase the kicker shorter or drop the row.
- Floor at 90 px → reject and rephrase if the formula falls below.

A new file, `reference/text-rephrase-vertical.md`, documents these
three patterns with worked examples drawn from
`videos/why-text-is-hard-2026-05-07/`. The horizontal
`reference/text-rephrase-recipes.md` is untouched.

## The delta doc — `reference/vertical-mode.md`

Single new file capturing every vertical-mode override. Outline:

1. **When this doc applies** — loaded only when mode = vertical (Step
   1 detection); overrides take precedence over `SKILL.md` for the
   steps it names.
2. **Canvas + layout overrides (Step 7)** — dimensions, zones, font
   formula, the `.thumbnail.vertical` wrapper class.
3. **Text rephrase rhythms (Step 3)** — A/B/C rhythm specs, pointer
   to `reference/text-rephrase-vertical.md` for worked examples.
4. **Accent placement (Step 5)** — inherits `red-word-recipes.md`
   unchanged for variants A and B. Variant C special case: the
   kicker row (row 3) takes accent on the topic noun by default;
   rows 1–2 take accent on the verb/adjective.
5. **Icon picking (Step 6)** — inherits `icon-picking.md` unchanged;
   icon size 720×720 instead of 320×320 (CSS handles via the
   wrapper).
6. **Round folder + filenames (Steps 7, 10)** —
   `thumbnails/round-N-vertical/`; variant files
   `a.html`/`b.html`/`c.html`/`contact-sheet.html` (same names — the
   wrapper class differentiates them); render output
   `thumbnail-vertical-a.png` / `-b.png` / `-c.png`.
7. **Contact sheet additions (Step 7)** — per-variant simulations:
   full 1080×1920, Shorts feed crop, TikTok profile-grid 1:1 crop.
8. **Renderer invocation (Step 10)** — `--orientation vertical` flag.

The file is **deltas only**. Anything not mentioned (hard rules from
`SKILL.md`'s "Hard rules" section, accent count cap, locked visual
signature, rephrase direction triad of upgrade/reframe/declarative)
carries over verbatim. If a future reader is unsure whether a rule
applies in vertical mode, the answer is "yes, unless this doc
explicitly overrides it."

## Templates and contact sheet additions

**Strategy:** no new template files. `templates/variant.html` and
`templates/contact-sheet.html` stay; vertical layout is opt-in via a
new `THUMBNAIL_CLASS` token and class-scoped CSS overrides.

### `templates/variant.html`

- New token: `THUMBNAIL_CLASS` — empty string for horizontal,
  `"vertical"` for vertical.
- Rendered as `<div class="thumbnail {{THUMBNAIL_CLASS}}">`.
- New token: `ROW_3_CLASS` — empty string in horizontal mode and for
  Variants A/B in vertical mode. `"kicker"` for Variant C in vertical
  mode. Rendered as
  `<span class="thumbnail-row {{ROW_3_CLASS}}">{{TITLE_ROW_3}}</span>`.
  Rows 1 and 2 have no equivalent token because no current rhythm
  pattern needs a per-row class on them.

### `templates/styles.css`

A single block of vertical overrides scoped to `.thumbnail.vertical`:

- Canvas dims (1080×1920) via `--canvas-w` / `--canvas-h`.
- `.thumbnail.vertical .thumbnail-text`: `top: auto; bottom: 120px;
  left: 80px; right: 80px;` — bottom-anchored, content-centered.
- `.thumbnail.vertical .thumbnail-icon`: `top: 120px; left: 50%;
  transform: translateX(-50%); width: 720px; height: 720px;`.
- `.thumbnail.vertical .thumbnail-icon svg`: `width: 720px; height:
  720px;` (preserves stroke widths via the existing rules).
- `.thumbnail.vertical .thumbnail-row.kicker`: `font-size: 0.6em`.
- Grid overlay extensions: `.thumbnail.vertical .grid-square-crop`
  (dashed square outline y=420–1500) and
  `.thumbnail.vertical .grid-tt-band` (bottom band y=1440–1920). Both
  red, dashed, only visible with `?grid`.

### `templates/contact-sheet.html`

The existing `{{VARIANTS_HTML}}` slot is reused. The skill emits a
different per-variant block depending on mode.

Vertical block per variant:

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

The `profile-grid-wrap` uses `width: 180px; height: 180px;
overflow: hidden;` and centers the inner `.thumbnail` so only the
y=420–1500 region shows — that's exactly what TikTok crops for the
profile grid.

The horizontal block in the contact sheet is unchanged.

### Token substitution updates

The token table in `SKILL.md` Step 7 grows by two entries
(`THUMBNAIL_CLASS` and `ROW_3_CLASS`). All existing tokens behave
identically. Global replace (`/g` flag) is unchanged.

## Renderer changes

Files: `tools/thumbnail-render/src/render.mjs`,
`tools/thumbnail-render/bin/render.mjs`.

### `src/render.mjs`

Replace the two hardcoded constants with an orientation table:

```js
export const ORIENTATION_DIMS = {
  horizontal: { width: 1280, height: 720 },
  vertical:   { width: 1080, height: 1920 },
};

export async function renderHtmlToPng(htmlPath, outPngPath, orientation = 'horizontal') {
  const { width, height } = ORIENTATION_DIMS[orientation];
  // viewport + clip use width/height; rest unchanged
}
```

The default of `'horizontal'` preserves backward compatibility for any
existing caller.

### `bin/render.mjs`

- Add `--orientation horizontal|vertical` flag (default `horizontal`).
- In variants mode, use orientation to compute the output filename:
  - `horizontal` → `thumbnail-{a,b,c}.png` (unchanged).
  - `vertical` → `thumbnail-vertical-{a,b,c}.png`.
- Validation: error out if the round-folder suffix and the orientation
  flag disagree. Concrete check: `roundDir.endsWith('-vertical') ===
  (orientation === 'vertical')`, otherwise throw.

### `SKILL.md` Step 10 invocation (vertical)

```bash
node <repo-root>/tools/thumbnail-render/bin/render.mjs \
  <video-dir>/thumbnails/round-N-vertical \
  --variants \
  --orientation vertical \
  --out-dir <video-dir>
```

The horizontal invocation in `SKILL.md` is unchanged.

## Tests

`tools/thumbnail-render/tests/` already exists. Add a vertical render
snapshot test that takes a fixed input HTML with the
`.thumbnail.vertical` wrapper class and asserts the output PNG is
exactly 1080×1920 and matches a stored reference image. The horizontal
snapshot test stays untouched.

Skill-level testing is manual:

1. Run vertical mode against
   `videos/why-text-is-hard-2026-05-07/` — verify three vertical
   variants render, contact sheet shows the three previews, and final
   PNGs export with the `thumbnail-vertical-` prefix.
2. Run horizontal mode against the same folder — verify the existing
   flow is unaffected (round counter doesn't bleed across modes,
   horizontal output filenames unchanged).

## Out of scope (deferred)

- Animated MP4 covers (TikTok supports them; not in this design).
- Square (1080×1080) for Instagram feed posts.
- Locale variants (cover image with translated text).
- A `both` mode that produces horizontal + vertical in one round. Run
  the skill twice instead.

## Summary of file changes

New:

- `.claude/skills/thumbnail-creator/reference/vertical-mode.md`
- `.claude/skills/thumbnail-creator/reference/text-rephrase-vertical.md`
- A vertical fixture under `tools/thumbnail-render/tests/fixtures/`
  and a vertical case added to `tools/thumbnail-render/tests/render.test.mjs`

Modified:

- `.claude/skills/thumbnail-creator/SKILL.md` (Step 1 mode detection;
  small note in Step 7 token table; small note in Step 10 invocation)
- `.claude/skills/thumbnail-creator/templates/variant.html`
  (`THUMBNAIL_CLASS` token; kicker row substitution for Variant C)
- `.claude/skills/thumbnail-creator/templates/styles.css` (vertical
  wrapper-class block; grid-overlay extensions)
- `.claude/skills/thumbnail-creator/templates/contact-sheet.html` (no
  edits — but the skill emits a vertical-specific per-variant block in
  vertical mode)
- `tools/thumbnail-render/src/render.mjs` (orientation table;
  `renderHtmlToPng` parameter)
- `tools/thumbnail-render/bin/render.mjs` (`--orientation` flag;
  filename prefix; round-suffix validation)

Untouched:

- `reference/visual-signature.md`, `reference/red-word-recipes.md`,
  `reference/icon-picking.md`, `reference/youtube-title-pairing.md`,
  `reference/iteration-recipes.md`, `reference/text-rephrase-recipes.md`
  (the horizontal recipe doc).
