# Thumbnail Creator — Iteration 2 Design

> Predecessor: `2026-05-08-thumbnail-creator-design.md` (the v1 spec). This document amends v1 with three changes: an Iconify fallback for icons, a grid overlay for layout review, and a fix to the underlying composition. Sections of v1 not mentioned here remain in force.

## 1. Why this iteration exists

The v1 implementation shipped, but the rendered thumbnails revealed three problems that don't resolve themselves through "iterate per video":

1. **The hand-coded SVG fallback produces ambiguous icons.** The `Aa` glyph used in the smoke test reads as a brand mark or title fragment, not as an icon naming the topic. Letting Claude hand-code SVGs when no Lucide icon fits is a gun-to-the-foot.
2. **There is no review surface for "is the layout balanced".** The skill says "open the contact sheet" but offers no positional guide, so layout problems hide in plain sight until export.
3. **The default layout produces ~320px of dead space at the bottom of every thumbnail.** Text is top-anchored (`top: 100px`); icon is vertically centered. They don't share an axis, and the bottom of the canvas is empty brown.

This spec resolves all three in one cut.

## 2. Scope

### In scope

- New Iconify fallback module + CLI in `tools/thumbnail-render/`.
- Iconify cache file (`icons/iconify-cache.json`) committed alongside the existing `lucide.json`.
- Grid overlay markup, CSS, and `?grid` URL toggle inside `templates/variant.html`.
- Layout fix in `templates/styles.css`: vertically center text, scale icon to 320px, tighten right padding.
- SKILL.md updates: font-size formula recomputation, icon-picking workflow update, grid-toggle documentation.
- Reference doc updates: rewrite `icon-picking.md`, refresh `visual-signature.md` icon-size note.
- One regenerated round-1 sample at `videos/why-text-is-hard-2026-05-07/thumbnails/round-1/` so the fresh visual reference is in place.

### Out of scope

- Changing the locked color/font/accent constants (those are the brand).
- The "3 rows always" / "7–11 words" / "2 accent regions max" constraints.
- A serve.mjs auto-refresh dev server (still deferred from v1).
- Any non-thumbnail UI work.

## 3. Icon system — Lucide-first, Iconify-fallback, no hand-coded

### 3.1 Resolution order

The skill resolves an icon in this order:

1. **Lucide.** If the topic has an entry in the `icon-picking.md` lookup table (or the user/skill picks a Lucide name), the body is read from `tools/thumbnail-render/icons/lucide.json` (already exists).
2. **Iconify.** If Lucide doesn't fit, the skill picks an Iconify qualified name `<set>:<icon>` (e.g. `ph:cursor-click`, `tabler:typography`, `mynaui:cube`). The body is fetched on-demand from `https://api.iconify.design/<set>/<icon>.svg`, parsed, and cached.
3. **Stop.** If neither fits, the skill asks the user for an alternate icon name. Hand-coded SVG is no longer a documented option.

### 3.2 How the skill picks an Iconify name

There is no Iconify lookup table baked into the skill — Iconify has ~200k icons and the right pick is a small judgment call per topic, not a static map. The skill picks a name by:

1. Identifying the topic noun (same way it does today for Lucide — "the word the viewer is choosing the video for").
2. Forming a qualified name `<set>:<icon-noun>` against the search order in §3.2.1, picking the first set whose conventional naming matches the topic. (The skill knows these sets' naming conventions: `ph:cursor-click`, `tabler:typography`, `mynaui:cube`, `heroicons:document-text`, etc.)
3. Verifying the body via `node bin/icon.mjs <name>` before writing it into the variant. If the CLI throws (404, network), the skill picks a different set or asks the user.

### 3.2.1 Iconify icon-set search order

When the skill needs to pick an Iconify name and isn't given one, it tries sets in this order — all are line-icon sets compatible with the locked aesthetic:

1. `lucide` (Iconify-mirrored — only used here when the local Lucide cache is missing the icon for some reason; rare)
2. `ph` (Phosphor Regular)
3. `tabler`
4. `mynaui`
5. `heroicons` (outline variant)
6. `lineicons`

The skill never picks from filled, multi-color, or pictographic sets (`fluent-color`, `noto`, `twemoji`, `flat-color-icons` etc.) because they break visual consistency with Lucide.

### 3.3 New module — `src/iconify.mjs`

Exports:

```js
export async function getIconifyBody(qualifiedName)
```

Behavior:

1. Validate `qualifiedName` matches `/^[a-z0-9-]+:[a-z0-9-]+$/`. Throw on miss with `invalid Iconify name: "${name}"`.
2. Read `tools/thumbnail-render/icons/iconify-cache.json` (create empty `{}` file if missing).
3. If `cache[qualifiedName]` exists, return it.
4. Otherwise:
   - Fetch `https://api.iconify.design/<set>/<icon>.svg` (using native `fetch`).
   - On non-2xx response: throw `Iconify fetch failed for "${name}": HTTP ${status}`.
   - Parse the response body. Strip the outer `<svg ...>` opening tag and `</svg>` closing tag. Return the children verbatim as a string. (Iconify returns clean SVG with attributes like `width`, `height`, `viewBox`, `fill="currentColor"` on the root — we drop the root and keep the body.)
   - Write the body to `cache[qualifiedName]`, persist the JSON file (sorted keys, 2-space indent, trailing newline) so commits diff cleanly.
   - Return the body.

Network failure handling: any thrown error propagates to the caller; the CLI prints the error message and exits non-zero.

### 3.4 New CLI — `bin/icon.mjs`

```bash
node tools/thumbnail-render/bin/icon.mjs <qualified-name>
```

Prints the resolved SVG body to stdout. Used by the skill at icon-resolution time:

- Skill computes the qualified name (e.g. `tabler:typography`).
- Runs the CLI.
- Captures stdout as the `{{ICON_SVG_BODY}}` token value for the variant template.

The CLI is also useful manually: `node bin/icon.mjs ph:cursor-click | head` to preview a body before deciding to use it.

### 3.5 Tests

`tests/iconify.test.mjs` (new):

- `getIconifyBody returns cached body without network` — pre-populate the cache, ensure no fetch happens (mock global fetch to throw).
- `getIconifyBody fetches and caches on miss` — point cache to a temp file, mock `fetch` to return a known SVG, call once, verify body returned and cache file written; call again, verify no second fetch.
- `getIconifyBody throws on invalid name` — pass `not a name`, expect throw.
- `getIconifyBody throws on HTTP failure` — mock fetch to return 404, expect throw, verify cache unchanged.

The existing `tests/render.test.mjs` is not affected.

### 3.6 Banning hand-coded SVG

`reference/icon-picking.md` is rewritten:

- The "Fallback — hand-coded SVG" section is replaced with "Fallback — Iconify".
- The Aa example is removed.
- New section: "How to pick an Iconify name" — short rules. (Use the topic noun; pick a line-style set in the documented order; verify the body in `bin/icon.mjs` before committing.)
- The "Source of icons — Lucide first" section stays; its lookup table stays.
- The visual signature constraint — single accent region — still applies. Iconify bodies arrive with `fill="currentColor"` and use `stroke="currentColor"`; the skill or the CSS sets these via the parent `<svg>` defaults (already in place from the v1 fix). To accent one detail, the skill can wrap a specific element of the body in a `<g class="accent-fill">` or directly add `stroke="#FFB627"` to one element. The mechanics are documented in the rewritten `icon-picking.md`.

## 4. Grid overlay

### 4.1 Toggle mechanism

A single inline script at the bottom of `<body>` in `templates/variant.html`:

```html
<script>
  if (location.search.includes('grid')) {
    document.querySelector('.thumbnail').classList.add('with-grid');
  }
</script>
```

CSS in `templates/styles.css`:

```css
.grid-overlay { display: none; }
.thumbnail.with-grid .grid-overlay { display: grid; /* full overlay rules */ }
```

The renderer (`bin/render.mjs`) opens the variant via `pathToFileURL`, which has no query string. PNG exports are therefore always clean — there is no path by which the grid leaks into a final render.

### 4.2 Markup

Inside the `.thumbnail` div, after `.thumbnail-text` and `.thumbnail-icon`:

```html
<div class="grid-overlay" aria-hidden="true">
  <div class="grid-cell">1</div>
  <div class="grid-cell">2</div>
  <!-- ... cells 3..12 ... -->
  <div class="grid-cell">12</div>
  <div class="grid-safe-area"></div>
  <div class="grid-duration-badge"></div>
</div>
```

12 numbered cells in a 4×3 CSS grid. The number renders in the top-left of each cell, semi-transparent red, ~24px sans-serif, with a 6px inset.

### 4.3 Markers

- **Cell grid lines:** 1px solid `rgba(255, 64, 64, 0.45)`, on cell borders. The outer canvas border is the thumbnail edge.
- **Mobile safe-area outline:** dashed `rgba(255, 64, 64, 0.6)`, 88% center-cropped (76px inset top/bottom/left/right). Marks the area that survives YouTube's mobile feed cropping.
- **Duration-badge corner:** solid `rgba(255, 64, 64, 0.6)`, anchored bottom-right, 140×40px, 12px inset from the bottom-right corner. Marks where YouTube renders `15:32` style overlays.

All markers are display-none unless `.thumbnail.with-grid` is on the parent.

### 4.4 Workflow integration

`SKILL.md`'s Step 7 message gets a single extra line:

> "Add `?grid` to any variant URL (e.g. `file://.../a.html?grid`) to overlay the design grid for layout checks. Remove `?grid` to view it clean."

The contact sheet (`templates/contact-sheet.html`) does not change in markup, but two small links appear under each variant card in the rendered output:

```html
<div class="variant-links">
  <a href="a.html">view full</a> ·
  <a href="a.html?grid">view with grid</a>
</div>
```

The skill builds these links when generating `contact-sheet.html` for each round.

## 5. Layout fix

### 5.1 CSS changes in `templates/styles.css`

```css
.thumbnail-text {
  position: absolute;
  left: 80px;
  top: 50%;                          /* was: top: 100px */
  transform: translateY(-50%);       /* new */
  right: 420px;                      /* was: 380px */
  /* font-weight: 800, line-height: 1.05, letter-spacing, text-transform,
     display: flex, flex-direction: column, gap, white-space — unchanged */
}

.thumbnail-icon {
  position: absolute;
  right: 80px;                       /* was: 110px */
  top: 50%;
  transform: translateY(-50%);       /* unchanged */
  width: 320px;                      /* was: 220px */
  height: 320px;                     /* was: 220px */
  display: flex;
  align-items: center;
  justify-content: center;
}
.thumbnail-icon svg {
  width: 320px;                      /* was: 220px */
  height: 320px;                     /* was: 220px */
  /* parent-SVG defaults from v1 fix unchanged */
}
```

The existing `.stroke`, `.accent-fill`, `.accent-stroke` classes are unchanged.

### 5.2 Font-size formula in `SKILL.md` Step 3

The text column shrinks from ~820px to ~780px (left:80 + right:420 means a 780px-wide column on a 1280px canvas).

Updated formula:

```
ROW_FONT_SIZE_PX = floor(780 / (longest_row_chars * 0.6))
                   capped at 140
```

Updated examples table:

| Chars | New px | Old px |
|---|---|---|
| 13 | 100 | 105 |
| 14 |  92 |  97 |
| 15 |  86 |  91 |
| 16 |  81 |  85 |
| 17 |  76 (rejects, < 80) |  80 |

The 80px reject threshold and behavior stay.

### 5.3 `reference/visual-signature.md` icon-size note

The "Icons" row in the constants table updates from:

> Lucide line icons, stroke-width 8 in 24×24 viewBox; accent-color fill on exactly one detail

to:

> Lucide line icons (or Iconify line set), 320×320px display, parent-SVG default stroke-width 2 in 24×24 viewBox; accent on exactly one detail

(Note: the v1 styles.css already replaced the spec's misstated `stroke-width: 8` default with `stroke-width: 2` because Lucide's native sizing is 2/24. This iteration aligns the doc with what the CSS actually does.)

## 6. File diff list

### Modified files

- `tools/thumbnail-render/package.json` — no new deps (uses native `fetch`); no version bump unless we publish.
- `.claude/skills/thumbnail-creator/templates/variant.html` — add grid markup + toggle script.
- `.claude/skills/thumbnail-creator/templates/styles.css` — layout fix + grid overlay CSS.
- `.claude/skills/thumbnail-creator/templates/contact-sheet.html` — add `view full · view with grid` links to each variant card.
- `.claude/skills/thumbnail-creator/SKILL.md` — Step 5 (icon picking) updated for Iconify; Step 3 formula updated; Step 7 message gets the `?grid` line.
- `.claude/skills/thumbnail-creator/reference/icon-picking.md` — rewrite Iconify section, remove hand-coded fallback + Aa example.
- `.claude/skills/thumbnail-creator/reference/visual-signature.md` — icon-size row updated.

### New files

- `tools/thumbnail-render/src/iconify.mjs` — `getIconifyBody()`.
- `tools/thumbnail-render/bin/icon.mjs` — CLI wrapper.
- `tools/thumbnail-render/icons/iconify-cache.json` — starts as `{}`; grows over time.
- `tools/thumbnail-render/tests/iconify.test.mjs` — four tests covering cache hit, cache miss, invalid name, HTTP failure.

### Regenerated artifacts

- `videos/why-text-is-hard-2026-05-07/thumbnails/round-1/{a,b,c}.html` — refreshed with new layout; icon swapped from hand-coded `Aa` to a real Iconify icon (e.g. `ph:text-aa` if it exists, otherwise `tabler:typography`).
- `videos/why-text-is-hard-2026-05-07/thumbnails/round-1/contact-sheet.html` — regenerated with new variant-link markup.
- `videos/why-text-is-hard-2026-05-07/thumbnail-{a,b,c}.png` — re-rendered for the visual reference.

### Unchanged files

- `tools/thumbnail-render/src/render.mjs`
- `tools/thumbnail-render/bin/render.mjs`
- `tools/thumbnail-render/scripts/sync-icons.mjs` (Lucide sync stays separate from Iconify on-demand)
- `tools/thumbnail-render/tests/render.test.mjs`
- All other `reference/*.md` files (text-rephrase, red-word, iteration recipes don't depend on icon source or layout).

## 7. Hard rules carried over from v1 (unchanged)

- Exactly 7–11 words per variant, exactly 3 rows, ALL CAPS.
- Maximum 2 accent regions per variant.
- No question marks, ellipses, colons, parentheses, emoji, arrows, drop shadows, or gradients.
- The icon names the topic statically.
- The visual signature constants do not change per video.
- Never pick a winner from the three variants.
- Termination: loop ends only on explicit user approval.

## 8. Testing posture

- Existing `npm test` continues to pass (the renderer test is unaffected).
- New `iconify.test.mjs` covers cache + network paths with `fetch` mocked; no real network calls in the test suite.
- Manual smoke: regenerate the existing round-1 with a real Iconify icon, render to PNG, confirm at 1280×720 that (a) text is vertically centered, (b) icon is ~25% canvas width, (c) opening the variant HTML with `?grid` shows the overlay, (d) the rendered PNG does not contain the grid.

## 9. Footguns and notes

- **Iconify API is unauthenticated and free**, but reasonable hosts get rate-limited. The cache makes this a non-issue in practice — first fetch is the only one that needs network.
- **`fetch` returns the SVG with a UTF-8 BOM in some cases.** The body parser strips a leading BOM if present.
- **The cache file is committed.** This is deliberate: every icon ever used is reviewable in git, and a fresh clone has no first-fetch latency for icons that were used in past videos.
- **`?grid` is a query-string sniff, not a strict parser** — `?grid`, `?grid=1`, `?foo&grid` all work. Intentionally permissive.
- **The grid overlay is z-indexed above text and icon** so it sits visually on top. Set `z-index: 10` on `.grid-overlay` (no other element has z-index in the locked CSS).
