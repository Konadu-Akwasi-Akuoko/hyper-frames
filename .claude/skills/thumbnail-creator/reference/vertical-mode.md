# Vertical mode — delta doc

Loaded by `SKILL.md` Step 1 when the user invokes the skill with any of
the vertical keywords: `vertical`, `portrait`, `tiktok`, `shorts`,
`reels`, `9:16`, `1080x1920` (case-insensitive).

This file lists the **deltas** between vertical mode and the default
horizontal flow documented in `SKILL.md`. Anything not mentioned here
is unchanged: the hard rules, locked visual signature, accent count
cap, the rephrase direction triad of upgrade/reframe/declarative, the
icon-picking rules and brand exception, the iteration recipes, the
pre-flight signature check, the per-round folder convention, and so
on. If a future reader is unsure whether a horizontal rule applies in
vertical mode, the answer is "yes, unless this doc explicitly
overrides it."

## 1. When this doc applies

Loaded only when mode = vertical. Mode resolution lives in `SKILL.md`
Step 1. The skill prints `Mode: vertical (1080×1920) — Shorts/TikTok
cover.` after detection.

## 2. Canvas + layout overrides (Step 7)

- Canvas: 1080×1920.
- Wrapper: the `.thumbnail` `<div>` gets an additional `vertical`
  class, supplied via the `THUMBNAIL_CLASS` template token. CSS
  overrides in `templates/styles.css` (under `.thumbnail.vertical`)
  drive every layout difference.
- Icon zone: top-centered, 720×720, with 120 px top padding.
- Text zone: bottom-anchored, 920 px wide (1080 − 80 padding each
  side), 120 px bottom padding, content centered horizontally.
- Font formula:
  `ROW_FONT_SIZE_PX = floor(920 / (longest_row_chars * 0.6))`
  capped at 220, floor at 90 (reject below).
- For Variant C, run the formula on rows 1-2 only. Row 3 inherits
  `font-size: 0.6em` from the `.kicker` CSS class. The computed
  kicker pixel size must still clear the 90 px floor.

## 3. Text rephrase rhythms (Step 3)

In vertical mode, each variant slot is locked to a rhythm pattern —
this is in addition to the direction triad. Slot mapping:

- Variant A — wide recap (3 rows, 3-6 words/row, 9-14 chars/row).
  Direction skew: direct upgrade.
- Variant B — stacked staccato (4-5 rows, 1-2 words/row, 4-9
  chars/row). Direction skew: punchy declarative.
- Variant C — headline + kicker (rows 1-2 huge, row 3 small at
  0.6em). Direction skew: sweeping reframe.

Worked examples and per-rhythm rules live in
`reference/text-rephrase-vertical.md`. The horizontal
`reference/text-rephrase-recipes.md` is NOT applied.

## 4. Accent placement (Step 5)

Inherit `red-word-recipes.md` unchanged for variants A and B. The
2-accent cap still applies.

Variant C special case: the kicker row (row 3) takes accent on the
topic noun by default; rows 1-2 take accent on the verb/adjective.
The "alternative accent" pattern (row 1 + one word in the kicker) is
allowed when the kicker carries the surprise rather than serving as a
quiet anchor. Pick one strategy per variant — do not mix.

## 5. Icon picking (Step 6)

Inherit `icon-picking.md` unchanged. The same Lucide → Iconify
line-icon → brand-exception resolution order applies. Same
`ICON_CLASS` mapping. The icon's display size is 720×720 instead of
320×320 — handled entirely by the CSS wrapper class, no token change.

## 6. Round folder + filenames (Steps 7, 10)

- Round folder: `<video-dir>/thumbnails/round-N-vertical/`.
  - The "next round" computation is mode-scoped: scan only entries
    matching `round-(\d+)-vertical` and pick `max + 1`. Modes have
    independent counters, so a video can have both `round-3/`
    (horizontal) and `round-1-vertical/` simultaneously.
- Variant files inside the round folder are unchanged in name:
  `a.html`, `b.html`, `c.html`, `contact-sheet.html`. The wrapper
  class differentiates them, not the filename.
- Render output filenames:
  `<video-dir>/thumbnail-vertical-a.png`,
  `<video-dir>/thumbnail-vertical-b.png`,
  `<video-dir>/thumbnail-vertical-c.png`.

## 7. Contact sheet additions (Step 7)

The contact sheet's `{{VARIANTS_HTML}}` slot is filled with three
copies of the **vertical** per-variant block (instead of the
horizontal block from `SKILL.md` Step 7):

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

`{{THUMBNAIL_DIV}}` is the same `.thumbnail.vertical` markup used in
`a.html` / `b.html` / `c.html`, inlined three times. The wrap classes
(`full-wrap-vertical`, `shorts-wrap`, `profile-grid-wrap`) CSS-scale
the inner thumbnail and, for the profile-grid wrap, crop to a centered
1:1 region so the user can judge what TikTok will display on a profile
grid.

The `full-wrap-vertical` scales the 1080×1920 thumbnail to 25%
(displayed ~270×480). The `shorts-wrap` scales further (~140×248) to
simulate the YouTube Shorts feed grid size. The `profile-grid-wrap` is
exactly 180×180 and centers the inner thumbnail so only the y=420-1500
region is visible — that's the TikTok profile-grid 1:1 crop.

## 8. Renderer invocation (Step 10)

```bash
node <repo-root>/tools/thumbnail-render/bin/render.mjs \
  <video-dir>/thumbnails/round-N-vertical \
  --variants \
  --orientation vertical \
  --out-dir <video-dir>
```

Writes `thumbnail-vertical-{a,b,c}.png` into `<video-dir>`. The
renderer validates that the round-dir suffix and the orientation flag
agree.
