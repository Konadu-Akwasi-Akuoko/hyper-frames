# Thumbnail-creator vertical variant — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a 1080×1920 vertical (Shorts/TikTok) output mode to the `thumbnail-creator` skill without disturbing the existing 1280×720 horizontal flow.

**Architecture:** Approach B from the spec — a new `reference/vertical-mode.md` "delta doc" holds vertical-specific overrides; the existing `SKILL.md` gets minimal additions to detect mode and load the delta. The Playwright renderer becomes orientation-aware via a parametric dimensions table. The CSS uses a `.thumbnail.vertical` wrapper class so a single template HTML works for both orientations.

**Tech Stack:** Node.js (ESM), Playwright (Chromium), the `node:test` runner; the skill content is markdown + HTML/CSS templates.

**Spec:** `docs/superpowers/specs/2026-05-08-thumbnail-vertical-variant-design.md`

---

## File map

**Create:**
- `.claude/skills/thumbnail-creator/reference/vertical-mode.md` — delta doc. Captures every override the skill applies when in vertical mode (canvas, layout, rephrase rhythms, accent placement, icon size, round folder, filenames, contact sheet, render invocation).
- `.claude/skills/thumbnail-creator/reference/text-rephrase-vertical.md` — worked examples for the three vertical rhythm patterns (wide-recap A, stacked-staccato B, headline-kicker C).
- `tools/thumbnail-render/tests/fixtures/vertical-basic.html` — minimal 1080×1920 fixture HTML for the renderer's vertical snapshot test. Self-contained (no template imports), mirrors `basic.html`.

**Modify:**
- `tools/thumbnail-render/src/render.mjs` — replace `THUMBNAIL_WIDTH`/`THUMBNAIL_HEIGHT` constants with an `ORIENTATION_DIMS` table; `renderHtmlToPng` takes an `orientation` parameter (default `'horizontal'`).
- `tools/thumbnail-render/bin/render.mjs` — accept `--orientation` flag, pass it to `renderHtmlToPng`, prefix vertical output filenames with `thumbnail-vertical-`, and validate the round-folder suffix matches the orientation flag.
- `tools/thumbnail-render/tests/render.test.mjs` — add tests for the new orientation parameter and PNG dimension assertions.
- `.claude/skills/thumbnail-creator/templates/variant.html` — add a `THUMBNAIL_CLASS` token rendered into the wrapper `<div>`'s class list.
- `.claude/skills/thumbnail-creator/templates/styles.css` — append a `.thumbnail.vertical` block that overrides canvas dims, repositions `.thumbnail-text` (bottom-anchored) and `.thumbnail-icon` (top-centered, 720×720), defines `.thumbnail-row.kicker` at 0.6em, and adds two grid-overlay extensions (TikTok bottom-band marker, profile-grid square-crop outline).
- `.claude/skills/thumbnail-creator/SKILL.md` — extend Step 1 with mode detection; add `THUMBNAIL_CLASS` to the Step 7 token reference; document the vertical per-variant contact-sheet block; add the `--orientation vertical` invocation in Step 10.

**Untouched:** all other `reference/*.md` files, `templates/contact-sheet.html` itself (the per-variant block is built by the skill at substitution time, not stored as a separate template), the `videos/` folders, the icon resolution tooling.

---

## Task 1: Make the renderer orientation-aware (`src/render.mjs`)

**Files:**
- Modify: `tools/thumbnail-render/src/render.mjs`
- Test: `tools/thumbnail-render/tests/render.test.mjs`
- Create: `tools/thumbnail-render/tests/fixtures/vertical-basic.html`

- [ ] **Step 1: Create the vertical fixture HTML**

Create `tools/thumbnail-render/tests/fixtures/vertical-basic.html`:

```html
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    html, body { margin: 0; padding: 0; }
    body { width: 1080px; height: 1920px; background: #1A1410; color: #F5E6D3;
           font-family: system-ui, sans-serif; display: flex;
           align-items: center; justify-content: center; }
    h1 { font-size: 120px; margin: 0; }
  </style>
</head>
<body>
  <h1>VERTICAL OK</h1>
</body>
</html>
```

- [ ] **Step 2: Add a tiny PNG dimension reader to the test file**

The tests need to assert PNG width/height. PNG stores width at bytes 16–19 and height at bytes 20–23 of the IHDR chunk (big-endian uint32, after the 8-byte signature). Add this helper at the top of `tools/thumbnail-render/tests/render.test.mjs` (after the imports, before the first `test(...)` call):

```js
import { readFileSync } from 'node:fs';

function readPngDims(pngPath) {
  const buf = readFileSync(pngPath);
  // PNG signature: 8 bytes; IHDR chunk: 4 length + 4 type ('IHDR') + 13 data
  // width = bytes 16-19, height = bytes 20-23 (big-endian uint32)
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}
```

- [ ] **Step 3: Write the failing tests for orientation support**

Append to `tools/thumbnail-render/tests/render.test.mjs`:

```js
const verticalFixture = path.join(__dirname, 'fixtures', 'vertical-basic.html');

test('renderHtmlToPng with orientation=horizontal produces 1280x720 PNG', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'tnr-'));
  const out = path.join(dir, 'h.png');
  try {
    await renderHtmlToPng(fixture, out, 'horizontal');
    const { width, height } = readPngDims(out);
    assert.equal(width, 1280);
    assert.equal(height, 720);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('renderHtmlToPng with orientation=vertical produces 1080x1920 PNG', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'tnr-'));
  const out = path.join(dir, 'v.png');
  try {
    await renderHtmlToPng(verticalFixture, out, 'vertical');
    const { width, height } = readPngDims(out);
    assert.equal(width, 1080);
    assert.equal(height, 1920);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('renderHtmlToPng defaults to horizontal when orientation omitted', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'tnr-'));
  const out = path.join(dir, 'd.png');
  try {
    await renderHtmlToPng(fixture, out);
    const { width, height } = readPngDims(out);
    assert.equal(width, 1280);
    assert.equal(height, 720);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('renderHtmlToPng throws on unknown orientation', async () => {
  await assert.rejects(
    () => renderHtmlToPng(fixture, '/tmp/nowhere.png', 'square'),
    /unknown orientation|orientation.*square/i
  );
});
```

- [ ] **Step 4: Run the new tests and confirm they fail**

Run: `cd tools/thumbnail-render && npm test`

Expected: the four new tests fail. The vertical-PNG-dims test should fail with a width assertion mismatch (renderer still produces 1280×720). The unknown-orientation test should fail because no validation is in place yet.

- [ ] **Step 5: Update `src/render.mjs` to support orientation**

Replace the entire contents of `tools/thumbnail-render/src/render.mjs` with:

```js
import { chromium } from 'playwright';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export const ORIENTATION_DIMS = {
  horizontal: { width: 1280, height: 720 },
  vertical:   { width: 1080, height: 1920 },
};

// Backwards-compat exports for any caller that imported the constants
// directly (these always reflect the horizontal mode).
export const THUMBNAIL_WIDTH = ORIENTATION_DIMS.horizontal.width;
export const THUMBNAIL_HEIGHT = ORIENTATION_DIMS.horizontal.height;

/**
 * Render an HTML file to a PNG at the requested orientation's dimensions.
 *
 * Waits for `document.fonts.ready` before screenshotting — without this,
 * web-font requests resolve after the screenshot fires and the PNG shows
 * the browser's fallback font instead of the intended one.
 *
 * @param {string} htmlPath - absolute path to the input HTML file
 * @param {string} outPngPath - absolute path where the PNG will be written
 * @param {'horizontal'|'vertical'} [orientation='horizontal']
 * @returns {Promise<void>}
 */
export async function renderHtmlToPng(htmlPath, outPngPath, orientation = 'horizontal') {
  const dims = ORIENTATION_DIMS[orientation];
  if (!dims) {
    throw new Error(`unknown orientation: ${orientation} (expected one of: ${Object.keys(ORIENTATION_DIMS).join(', ')})`);
  }
  if (!existsSync(htmlPath)) {
    throw new Error(`Input HTML not found: ${htmlPath} (ENOENT)`);
  }

  const { width, height } = dims;
  const browser = await chromium.launch();
  try {
    const context = await browser.newContext({
      viewport: { width, height },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    const fileUrl = pathToFileURL(path.resolve(htmlPath)).href;
    await page.goto(fileUrl, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({
      path: outPngPath,
      type: 'png',
      clip: { x: 0, y: 0, width, height },
    });
  } finally {
    await browser.close();
  }
}
```

- [ ] **Step 6: Run all tests and confirm they pass**

Run: `cd tools/thumbnail-render && npm test`

Expected: all six tests pass (the two original tests plus the four new ones).

- [ ] **Step 7: Commit**

```bash
git add tools/thumbnail-render/src/render.mjs \
        tools/thumbnail-render/tests/render.test.mjs \
        tools/thumbnail-render/tests/fixtures/vertical-basic.html
git commit -m "feat(thumbnail-render): orientation-aware renderHtmlToPng

Adds an ORIENTATION_DIMS table and an orientation parameter to
renderHtmlToPng. Vertical produces 1080x1920; horizontal stays at
1280x720 and remains the default for backwards compatibility."
```

---

## Task 2: Wire `--orientation` into the renderer CLI (`bin/render.mjs`)

**Files:**
- Modify: `tools/thumbnail-render/bin/render.mjs`

This task does not add automated tests. The renderer's HTTP-free Playwright invocation is exercised via Task 1's test suite; the CLI is a thin wrapper. We rely on a manual smoke test at the end.

- [ ] **Step 1: Replace `bin/render.mjs` with the orientation-aware version**

Replace the entire contents of `tools/thumbnail-render/bin/render.mjs` with:

```js
#!/usr/bin/env node
import path from 'node:path';
import { existsSync, statSync } from 'node:fs';
import { renderHtmlToPng, ORIENTATION_DIMS } from '../src/render.mjs';

function usage() {
  console.error(`Usage:
  render.mjs <html-path> --out <png-path> [--orientation horizontal|vertical]
  render.mjs <round-dir> --variants --out-dir <video-folder> [--orientation horizontal|vertical]

Single-file mode renders one HTML to one PNG at the orientation's
dimensions (horizontal=1280x720, vertical=1080x1920).

Variants mode renders a.html, b.html, c.html from <round-dir> to:
  - thumbnail-{a,b,c}.png            (horizontal, default)
  - thumbnail-vertical-{a,b,c}.png   (vertical)
in <video-folder>.

In variants mode, the round-dir suffix and the --orientation flag must
agree: a directory ending in '-vertical' requires --orientation vertical,
and any other directory requires --orientation horizontal.`);
  process.exit(2);
}

function parseArgs(argv) {
  const args = { positional: [], flags: { orientation: 'horizontal' } };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--variants')        { args.flags.variants    = true; }
    else if (a === '--out')        { args.flags.out         = argv[++i]; }
    else if (a === '--out-dir')    { args.flags.outDir      = argv[++i]; }
    else if (a === '--orientation'){ args.flags.orientation = argv[++i]; }
    else if (a.startsWith('--'))   { console.error(`Unknown flag: ${a}`); usage(); }
    else                           { args.positional.push(a); }
  }
  if (!ORIENTATION_DIMS[args.flags.orientation]) {
    console.error(`Unknown orientation: ${args.flags.orientation} (expected one of: ${Object.keys(ORIENTATION_DIMS).join(', ')})`);
    usage();
  }
  return args;
}

async function renderSingle(htmlPath, outPath, orientation) {
  const absHtml = path.resolve(htmlPath);
  const absOut = path.resolve(outPath);
  console.log(`render (${orientation}): ${absHtml} -> ${absOut}`);
  await renderHtmlToPng(absHtml, absOut, orientation);
  console.log(`done: ${absOut}`);
}

async function renderVariants(roundDir, outDir, orientation) {
  const absRound = path.resolve(roundDir);
  const absOut = path.resolve(outDir);
  if (!existsSync(absRound) || !statSync(absRound).isDirectory()) {
    throw new Error(`round-dir not found or not a directory: ${absRound}`);
  }
  if (!existsSync(absOut) || !statSync(absOut).isDirectory()) {
    throw new Error(`out-dir not found or not a directory: ${absOut}`);
  }
  const dirIsVertical = absRound.endsWith('-vertical');
  if (dirIsVertical !== (orientation === 'vertical')) {
    throw new Error(`round-dir suffix and --orientation disagree: roundDir=${absRound} orientation=${orientation}. Vertical rounds must end in '-vertical' and pass --orientation vertical.`);
  }
  const prefix = orientation === 'vertical' ? 'thumbnail-vertical-' : 'thumbnail-';
  for (const letter of ['a', 'b', 'c']) {
    const html = path.join(absRound, `${letter}.html`);
    if (!existsSync(html)) {
      throw new Error(`missing variant HTML: ${html}`);
    }
    const png = path.join(absOut, `${prefix}${letter}.png`);
    console.log(`render (${orientation}): ${html} -> ${png}`);
    await renderHtmlToPng(html, png, orientation);
  }
  console.log(`done: ${prefix}{a,b,c}.png in ${absOut}`);
}

const args = parseArgs(process.argv.slice(2));

try {
  if (args.flags.variants) {
    if (args.positional.length !== 1 || !args.flags.outDir) usage();
    await renderVariants(args.positional[0], args.flags.outDir, args.flags.orientation);
  } else {
    if (args.positional.length !== 1 || !args.flags.out) usage();
    await renderSingle(args.positional[0], args.flags.out, args.flags.orientation);
  }
} catch (err) {
  console.error(`error: ${err.message}`);
  process.exit(1);
}
```

- [ ] **Step 2: Smoke-test the CLI in horizontal mode (backwards compat)**

Run from the repo root:

```bash
cd tools/thumbnail-render
node bin/render.mjs tests/fixtures/basic.html --out /tmp/cli-h.png
```

Expected: prints `render (horizontal): ... -> /tmp/cli-h.png` then `done: ...`. Verify the file exists with `ls -la /tmp/cli-h.png` (should be > 1KB).

- [ ] **Step 3: Smoke-test the CLI in vertical mode**

Run from `tools/thumbnail-render`:

```bash
node bin/render.mjs tests/fixtures/vertical-basic.html --out /tmp/cli-v.png --orientation vertical
```

Expected: prints `render (vertical): ... -> /tmp/cli-v.png`. Verify file dimensions are 1080×1920:

```bash
node -e "const fs=require('node:fs');const b=fs.readFileSync('/tmp/cli-v.png');console.log({w:b.readUInt32BE(16),h:b.readUInt32BE(20)});"
```

Expected output: `{ w: 1080, h: 1920 }`.

- [ ] **Step 4: Smoke-test the round-suffix mismatch validation**

Run:

```bash
mkdir -p /tmp/round-1-vertical
echo "<html><body>x</body></html>" > /tmp/round-1-vertical/a.html
echo "<html><body>x</body></html>" > /tmp/round-1-vertical/b.html
echo "<html><body>x</body></html>" > /tmp/round-1-vertical/c.html
node bin/render.mjs /tmp/round-1-vertical --variants --out-dir /tmp --orientation horizontal
```

Expected: exits non-zero with `error: round-dir suffix and --orientation disagree: ...`.

Clean up: `rm -rf /tmp/round-1-vertical /tmp/cli-h.png /tmp/cli-v.png`.

- [ ] **Step 5: Commit**

```bash
git add tools/thumbnail-render/bin/render.mjs
git commit -m "feat(thumbnail-render): add --orientation flag to CLI

Variants mode prefixes vertical output as thumbnail-vertical-{a,b,c}.png
and validates that the round-dir suffix matches the orientation flag.
Horizontal remains the default; existing invocations are unaffected."
```

---

## Task 3: Add `THUMBNAIL_CLASS` and `ROW_3_CLASS` tokens to the variant template

**Files:**
- Modify: `.claude/skills/thumbnail-creator/templates/variant.html`

- [ ] **Step 1: Update the leading documentation comment**

In `.claude/skills/thumbnail-creator/templates/variant.html`, locate the block comment that starts with `<!--` at the top. Replace the entire comment with:

```html
<!--
  Tokens substituted by the thumbnail-creator skill. Names are listed
  WITHOUT brace syntax to avoid colliding with first-occurrence string
  replacement. The skill must use global replacement (e.g. /g in JS,
  re.sub in Python) when substituting.

  Required:
    STYLES_HREF       absolute file:// URL to templates/styles.css
    TITLE_PLAIN       plain text title (for <title>)
    ROW_FONT_SIZE_PX  integer pixel size, autosized per variant
    TITLE_ROW_1..3    row HTML with accent <span> markup
    ICON_SVG_BODY     SVG body (children of <svg>); from Lucide cache
                      or Iconify on-demand fetch (never hand-coded)

  Required (added for brand exception):
    ICON_VIEWBOX      e.g. "0 0 24 24" for Lucide / Simple Icons,
                      "0 0 256 417" for logos:jenkins, etc.
    ICON_CLASS        "" for default line icons,
                      "brand-silhouette" for simple-icons:*,
                      "brand-silhouette accent" for accent-tinted brand,
                      "brand-color" for logos:* / devicon:* multi-color

  Required (added for vertical mode):
    THUMBNAIL_CLASS   "" for horizontal (1280x720),
                      "vertical" for 1080x1920 Shorts/TikTok cover.
                      Drives layout via class-scoped CSS in styles.css.
    ROW_3_CLASS       "" for horizontal mode and for vertical Variants
                      A/B. "kicker" for vertical Variant C — scales
                      row 3 to 0.6em via the .kicker CSS rule. See
                      the thumbnail-creator skill's
                      reference/vertical-mode.md for the rhythm spec.
-->
```

- [ ] **Step 2: Update the wrapper `<div>` to include `THUMBNAIL_CLASS`**

Find the line:

```html
  <div class="thumbnail">
```

Replace with:

```html
  <div class="thumbnail {{THUMBNAIL_CLASS}}">
```

- [ ] **Step 3: Update row 3's `<span>` to include `ROW_3_CLASS`**

Find the line:

```html
      <span class="thumbnail-row">{{TITLE_ROW_3}}</span>
```

Replace with:

```html
      <span class="thumbnail-row {{ROW_3_CLASS}}">{{TITLE_ROW_3}}</span>
```

Rows 1 and 2 are unchanged — no rhythm pattern currently needs a per-row class on them.

- [ ] **Step 4: Verify the file is well-formed**

Open the file in your editor and visually confirm: one `<!doctype html>`, one `<html>`, one `<body>`, the `.thumbnail` `<div>` now has both classes, row 3's `<span>` has both classes, and rows 1 and 2 are unchanged.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/thumbnail-creator/templates/variant.html
git commit -m "feat(thumbnail-creator): add THUMBNAIL_CLASS and ROW_3_CLASS tokens

THUMBNAIL_CLASS: empty for horizontal (preserves existing rendering),
'vertical' for 1080x1920 Shorts/TikTok mode. ROW_3_CLASS: empty by
default, 'kicker' for vertical Variant C to scale row 3 to 0.6em.
Layout is driven by class-scoped CSS added in a follow-up commit."
```

---

## Task 4: Add the vertical CSS overrides to `styles.css`

**Files:**
- Modify: `.claude/skills/thumbnail-creator/templates/styles.css`

- [ ] **Step 1: Append the vertical override block**

Append the following block to the very end of `.claude/skills/thumbnail-creator/templates/styles.css` (after the existing grid-overlay rules):

```css
/* ---- Vertical mode (1080x1920 Shorts/TikTok cover) ----
 * Activated by adding `vertical` to the .thumbnail wrapper class.
 * Layout: icon top-centered (720x720), text bottom-anchored, three to
 * five rows. Variant C gets a `.kicker` modifier on row 3 that scales
 * the kicker to 0.6em of the dominant size. See the thumbnail-creator
 * skill's reference/vertical-mode.md for the full layout spec.
 */
.thumbnail.vertical {
  --canvas-w: 1080px;
  --canvas-h: 1920px;
  width: var(--canvas-w);
  height: var(--canvas-h);
}

.thumbnail.vertical .thumbnail-text {
  top: auto;
  bottom: 120px;
  left: 80px;
  right: 80px;
  transform: none;
  text-align: center;
  align-items: center;
  white-space: normal;
}

.thumbnail.vertical .thumbnail-row.kicker {
  font-size: 0.6em;
}

.thumbnail.vertical .thumbnail-icon {
  top: 120px;
  left: 50%;
  right: auto;
  transform: translateX(-50%);
  width: 720px;
  height: 720px;
}

.thumbnail.vertical .thumbnail-icon svg {
  width: 720px;
  height: 720px;
}

/* Vertical-only grid markers: TikTok bottom UI band + profile-grid
 * 1:1 crop outline. Only visible when ?grid is appended to the URL. */
.thumbnail.vertical.with-grid .grid-overlay::before {
  /* TikTok bottom UI band: y=1440 to y=1920 (bottom 25%) */
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  top: 1440px;
  height: 480px;
  border-top: 2px dashed rgba(255, 64, 64, 0.6);
  background: rgba(255, 64, 64, 0.06);
}

.thumbnail.vertical.with-grid .grid-overlay::after {
  /* Profile-grid 1:1 crop: y=420 to y=1500 (centered square) */
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  top: 420px;
  height: 1080px;
  outline: 2px dashed rgba(255, 64, 64, 0.6);
  outline-offset: -1px;
}
```

- [ ] **Step 2: Visual smoke test**

Create a temporary verification HTML at `/tmp/vertical-check.html`:

```bash
cat > /tmp/vertical-check.html <<'EOF'
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Vertical check</title>
  <link rel="stylesheet" href="file:///Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/.claude/skills/thumbnail-creator/templates/styles.css">
</head>
<body>
  <div class="thumbnail vertical">
    <div class="thumbnail-text" style="font-size: 140px;">
      <span class="thumbnail-row">STOP GUESSING</span>
      <span class="thumbnail-row">AT HOW <span class="accent">TEXT</span></span>
      <span class="thumbnail-row">GETS RENDERED</span>
    </div>
    <div class="thumbnail-icon">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10"/>
      </svg>
    </div>
    <div class="grid-overlay" aria-hidden="true">
      <div class="grid-cell">1</div><div class="grid-cell">2</div>
      <div class="grid-cell">3</div><div class="grid-cell">4</div>
      <div class="grid-cell">5</div><div class="grid-cell">6</div>
      <div class="grid-cell">7</div><div class="grid-cell">8</div>
      <div class="grid-cell">9</div><div class="grid-cell">10</div>
      <div class="grid-cell">11</div><div class="grid-cell">12</div>
      <div class="grid-safe-area"></div>
      <div class="grid-duration-badge"></div>
    </div>
  </div>
  <script>
    if (location.search.includes('grid')) {
      document.querySelector('.thumbnail').classList.add('with-grid');
    }
  </script>
</body>
</html>
EOF
open "/tmp/vertical-check.html?grid"
```

Expected (visual check):
- The thumbnail is a tall 1080×1920 rectangle (will overflow most viewports — scroll to verify).
- The icon (a circle) sits in the top portion, roughly 720×720, horizontally centered.
- The three text rows sit in the bottom portion, horizontally centered, with the word "TEXT" in amber.
- With `?grid`: a red dashed square outlines the center 1:1 crop region; a red dashed band marks the bottom 25% (TikTok UI zone).

Then verify horizontal mode still works:

```bash
sed -i.bak 's/class="thumbnail vertical"/class="thumbnail"/' /tmp/vertical-check.html
open "/tmp/vertical-check.html"
```

Expected: standard 1280×720 horizontal layout with text on the left, icon on the right (the existing horizontal styling, unchanged).

Clean up: `rm /tmp/vertical-check.html /tmp/vertical-check.html.bak`.

- [ ] **Step 3: Commit**

```bash
git add .claude/skills/thumbnail-creator/templates/styles.css
git commit -m "feat(thumbnail-creator): vertical layout CSS for Shorts/TikTok cover

Adds a .thumbnail.vertical class-scoped block: 1080x1920 canvas,
top-centered 720x720 icon, bottom-anchored 920px text column, kicker
modifier (0.6em) for Variant C, and grid-overlay extensions marking
the TikTok bottom UI band and profile-grid 1:1 crop region."
```

---

## Task 5: Write `reference/text-rephrase-vertical.md`

**Files:**
- Create: `.claude/skills/thumbnail-creator/reference/text-rephrase-vertical.md`

- [ ] **Step 1: Create the reference file**

Create `.claude/skills/thumbnail-creator/reference/text-rephrase-vertical.md` with this content:

```markdown
# Text rephrase recipes — vertical (Shorts / TikTok)

Loaded by the thumbnail-creator skill at Step 3 when in vertical mode.
The horizontal recipes in `text-rephrase-recipes.md` are NOT applied;
this file replaces them. The general direction triad (direct upgrade,
sweeping reframe, punchy declarative) and all hard rules from
`SKILL.md` still apply — only the row count, character budget, and
font-sizing cap differ.

In vertical mode, each variant slot is locked to a fixed rhythm:
A is the wide-recap, B is the stacked-staccato, C is the headline+kicker.
This is on top of the direction differentiation — A still skews "direct
upgrade", B "punchy declarative", C "sweeping reframe".

---

## Shared constraints (apply across A, B, C)

- ALL CAPS only.
- No question marks, ellipses, colons, parentheses, emoji, arrows.
- Max 2 accent regions per variant.
- Same icon across all 3 variants in a round.
- The text column is 920 px wide. The font formula is:
  `floor(920 / (longest_row_chars * 0.6))`, capped at 220, floor at 90.
- A computed font size below 90 px is a hard reject — rephrase shorter.

## Variant A — wide recap

- Rows: exactly 3.
- Words per row: 3-6.
- Chars per row (incl. spaces): 9-14.
- Direction: direct upgrade of the working title.
- Tone: complete phrase; reads top-to-bottom as one sentence with
  comma rhythm.
- Expected dominant font size: 110-135 px.

Worked example — working title "Why text is hard":

```
STOP GUESSING
AT HOW TEXT
GETS RENDERED
```

Accent: `TEXT` (Tier-1 topic noun) on row 2.

## Variant B — stacked staccato

- Rows: 4-5.
- Words per row: 1-2.
- Chars per row: 4-9.
- Direction: punchy declarative reframe; the most tabloid-feeling.
- Tone: poster / sticker. One beat per row. Each row stands alone.
- Expected dominant font size: 150-180 px.

Worked example — working title "Why text is hard":

```
TEXT
IS
HARDER
THAN
YOU THINK
```

Accent: `TEXT` (row 1) and `HARDER` (row 3). Two accent regions cap.

## Variant C — headline + kicker

- Rows: exactly 3.
- Rows 1-2: 1-3 words each, 5-8 chars each. Dominant font 200-220 px.
- Row 3 (kicker): 3-6 words, 14-18 chars. Rendered at 0.6em of the
  dominant size via the `.kicker` CSS class — the rephrase produces the
  text; the template applies the class.
- Direction: sweeping reframe; the headline carries the emotional claim
  and the kicker grounds it.
- Computed kicker pixel size (0.6 × dominant) must clear the 90 px
  floor; if not, shorten the kicker or drop the row.

Worked example — working title "Why text is hard":

```
TEXT
RENDERING
THE LAYER NOBODY SEES
```

Accent: `RENDERING` (row 2) — the kicker stays unaccented in this case
because its job is to ground, not to emphasize.

Alternative accent: `TEXT` (row 1) + a single word in the kicker
(e.g. `NOBODY`) when the kicker carries the surprise rather than
serving as a quiet anchor. Pick one accent strategy per variant; do
not mix.

## How the three rhythms relate

The user judges the round on which rhythm pulls them in, not just
which words. Don't make the three texts paraphrase the same beat with
different line breaks — that defeats the rhythm differentiation. Each
variant should feel like a different cover for a different audience:

- A reads like an article headline.
- B reads like a TikTok meme cover.
- C reads like a magazine front.
```

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/thumbnail-creator/reference/text-rephrase-vertical.md
git commit -m "feat(thumbnail-creator): vertical-mode text rephrase recipes

Documents the three rhythm patterns (wide-recap, stacked-staccato,
headline+kicker) used by Variants A/B/C in vertical mode. Worked
examples drawn from the why-text-is-hard video."
```

---

## Task 6: Write `reference/vertical-mode.md` (the delta doc)

**Files:**
- Create: `.claude/skills/thumbnail-creator/reference/vertical-mode.md`

- [ ] **Step 1: Create the delta doc**

Create `.claude/skills/thumbnail-creator/reference/vertical-mode.md` with this content:

````markdown
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
````

- [ ] **Step 2: Commit**

```bash
git add .claude/skills/thumbnail-creator/reference/vertical-mode.md
git commit -m "feat(thumbnail-creator): vertical-mode delta doc

Captures every override the skill applies in vertical (1080x1920)
mode: canvas + layout, rephrase rhythms, accent placement, icon
size, round folder + filenames, contact-sheet block, renderer
invocation. Anything not listed inherits from SKILL.md unchanged."
```

---

## Task 7: Wire `SKILL.md` to recognize vertical mode

**Files:**
- Modify: `.claude/skills/thumbnail-creator/SKILL.md`

This task makes three small edits to `SKILL.md`. Apply them in order.

- [ ] **Step 1: Update the description frontmatter to mention vertical**

Find the existing `description:` frontmatter (lines 2-3 of `SKILL.md`). Replace its full text with:

```
description: Guided generator that turns a hyper-frames video's working title into three production-ready YouTube thumbnail variants (1280x720) or Shorts/TikTok cover variants (1080x1920) in the channel's locked visual style, with an iterative review loop. Use this skill whenever the user wants to create, draft, generate, design, or A/B test thumbnails for a hyper-frames video — phrases like "make a thumbnail for this video", "I need thumbnails", "generate thumbnail variants", "design a thumbnail", or any request that names a `videos/<slug>-<date>/` folder and asks for a thumbnail. Vertical/Shorts/TikTok mode activates when the invoking message contains any of: vertical, portrait, tiktok, shorts, reels, 9:16, 1080x1920. Also triggers when the user runs the skill from inside a video folder after the script is drafted.
```

- [ ] **Step 2: Add mode detection to Step 1**

Find the section `### Step 1 — Resolve the target video folder`. Replace the entire section (from the heading through the line "Convert the result to an absolute path. Use that absolute path for every subsequent file read and write — do not depend on CWD after this step.") with:

```markdown
### Step 1 — Resolve the target video folder and orientation mode

Resolve the **target folder** in this order:

1. If the user's message contains a path like `videos/<slug>-<date>/`
   (relative or absolute), use that.
2. If the current working directory matches `**/videos/<slug>-<date>/`,
   use that.
3. Otherwise, ask: "Which video folder should I work in?" — list existing
   `videos/*` directories to make the choice concrete.

Convert the result to an absolute path. Use that absolute path for every
subsequent file read and write — do not depend on CWD after this step.

Resolve the **orientation mode** in this order (case-insensitive):

1. If the invoking message contains any of `vertical`, `portrait`,
   `tiktok`, `shorts`, `reels`, `9:16`, `1080x1920` → **vertical mode**.
2. Otherwise → **horizontal mode** (default).

Print a one-line confirmation:
- Horizontal: `Mode: horizontal (1280×720) — YouTube thumbnail.`
- Vertical: `Mode: vertical (1080×1920) — Shorts/TikTok cover.`

If mode is vertical, **load `reference/vertical-mode.md` now** and
apply its overrides to every subsequent step it names (Steps 3, 5, 7,
10). Anything that doc doesn't override carries over from this file
verbatim.

Round folders are mode-tagged. When computing the next round number in
Step 7:
- Horizontal mode: scan `<video-dir>/thumbnails/round-(\d+)/` entries
  (un-suffixed). The vertical rounds are excluded.
- Vertical mode: scan `<video-dir>/thumbnails/round-(\d+)-vertical/`
  entries. The horizontal rounds are excluded.

Modes have independent counters; a single video can have
`round-3/` (horizontal) and `round-1-vertical/` simultaneously.
```

- [ ] **Step 3: Add `THUMBNAIL_CLASS` and `ROW_3_CLASS` to the Step 7 token reference**

Find the "Token reference (for `variant.html`):" list in Step 7. Add two new entries at the end of the list, after the `ICON_SVG_BODY` entry:

```markdown
- `THUMBNAIL_CLASS` — `""` for horizontal (default); `"vertical"` for
  vertical mode. Determines the `.thumbnail` wrapper class which
  drives layout via class-scoped CSS in `templates/styles.css`. See
  `reference/vertical-mode.md` for the full vertical layout spec.
- `ROW_3_CLASS` — `""` for horizontal and for Variants A/B in vertical
  mode. `"kicker"` for Variant C in vertical mode only. Scales row 3
  to 0.6em via the `.thumbnail.vertical .thumbnail-row.kicker` CSS
  rule. The kicker's computed pixel size (0.6 × dominant font size)
  must clear the 90 px floor; if it doesn't, rephrase shorter.
```

- [ ] **Step 4: Note the vertical contact-sheet block in Step 7**

In Step 7's "The `{{VARIANTS_HTML}}` block shape" subsection, find the line that currently reads:

```
`templates/contact-sheet.html` has a single `{{VARIANTS_HTML}}` slot.
Build it by concatenating three copies of this block (one per variant):
```

Replace with:

```
`templates/contact-sheet.html` has a single `{{VARIANTS_HTML}}` slot.
In horizontal mode, build it by concatenating three copies of this block
(one per variant). In vertical mode, use the alternative block defined
in `reference/vertical-mode.md` §7 instead — same `{{VARIANTS_HTML}}`
slot, different per-variant block shape (three preview wraps: full,
Shorts feed, TikTok profile-grid 1:1 crop).
```

- [ ] **Step 5: Add the vertical render command in Step 10**

Find the bash code block in Step 10 that begins:

```bash
node <repo-root>/tools/thumbnail-render/bin/render.mjs \
  <video-dir>/thumbnails/round-N \
  --variants \
  --out-dir <video-dir>
```

Replace that single bash block with two bash blocks separated by an explanatory line:

````markdown
Horizontal mode:

```bash
node <repo-root>/tools/thumbnail-render/bin/render.mjs \
  <video-dir>/thumbnails/round-N \
  --variants \
  --out-dir <video-dir>
```

Vertical mode:

```bash
node <repo-root>/tools/thumbnail-render/bin/render.mjs \
  <video-dir>/thumbnails/round-N-vertical \
  --variants \
  --orientation vertical \
  --out-dir <video-dir>
```
````

Then find the bullet list immediately after that begins with "This writes:". Replace its entire body with:

```markdown
This writes (horizontal):
- `<video-dir>/thumbnail-a.png`
- `<video-dir>/thumbnail-b.png`
- `<video-dir>/thumbnail-c.png`

Or (vertical):
- `<video-dir>/thumbnail-vertical-a.png`
- `<video-dir>/thumbnail-vertical-b.png`
- `<video-dir>/thumbnail-vertical-c.png`
```

- [ ] **Step 6: Add a reference-file entry for `vertical-mode.md`**

In the "Reference files (load on demand)" section near the bottom of `SKILL.md`, append a new bullet:

```markdown
- `reference/vertical-mode.md` — overrides applied when the user
  invokes vertical mode (Shorts/TikTok cover). Load at Step 1 if mode
  is vertical; not loaded otherwise.
- `reference/text-rephrase-vertical.md` — vertical-mode rephrase
  rhythms (Variants A/B/C correspond to wide-recap / stacked-staccato
  / headline+kicker). Load at Step 3 in vertical mode; the horizontal
  `text-rephrase-recipes.md` is not loaded in vertical mode.
```

- [ ] **Step 7: Verify `SKILL.md` is consistent**

Quick visual scan of `SKILL.md`:
- Step 1 now mentions both folder and orientation resolution.
- Step 7 token reference includes `THUMBNAIL_CLASS`.
- Step 7 `{{VARIANTS_HTML}}` subsection mentions the vertical alternative.
- Step 10 has both horizontal and vertical render commands.
- Reference files section lists the two new files.
- The frontmatter description trigger phrase covers the vertical keywords.

- [ ] **Step 8: Commit**

```bash
git add .claude/skills/thumbnail-creator/SKILL.md
git commit -m "feat(thumbnail-creator): wire SKILL.md to support vertical mode

Step 1 now resolves orientation alongside the target folder and loads
reference/vertical-mode.md when vertical keywords are detected. Step
7 documents the new THUMBNAIL_CLASS token and points to the vertical
contact-sheet block. Step 10 has both horizontal and vertical render
invocations. Description trigger phrase covers Shorts/TikTok keywords."
```

---

## Task 8: End-to-end verification against an existing video

**Files:** none modified. This is a manual verification gate; no commit.

This task is run by the **user** (not the agentic worker) once Tasks 1-7 are merged. The agentic worker should pause here and surface these instructions for the user to run.

- [ ] **Step 1: Verify horizontal mode is unaffected**

Pick the existing canonical video (`videos/why-text-is-hard-2026-05-07/`) and run the skill in horizontal mode. The user invokes the skill conversationally, e.g. "Generate thumbnails for `videos/why-text-is-hard-2026-05-07`". The skill should:

- Print `Mode: horizontal (1280×720) — YouTube thumbnail.`
- Compute the next horizontal round number from `round-(\d+)/` only (ignoring any new vertical rounds).
- Produce `a.html`, `b.html`, `c.html`, `contact-sheet.html` with the existing horizontal layout.
- Final export (on "ship it") writes `thumbnail-{a,b,c}.png` (no `-vertical-` prefix).

- [ ] **Step 2: Verify vertical mode end-to-end**

Run again with a vertical keyword: "Generate **vertical** thumbnails for `videos/why-text-is-hard-2026-05-07`". The skill should:

- Print `Mode: vertical (1080×1920) — Shorts/TikTok cover.`
- Load `reference/vertical-mode.md` and `reference/text-rephrase-vertical.md`.
- Produce three variants whose texts follow the rhythm patterns: A is a 3-row recap, B is 4-5 stacked rows, C is a headline + kicker.
- Each variant HTML includes `<div class="thumbnail vertical">` and the icon zone is centered at the top.
- Variant C's third `<span>` has the `kicker` class.
- The contact sheet shows three preview wraps per variant: full (1080×1920 @ 25%), Shorts feed (~140×248), and TikTok profile grid (180×180 1:1 crop).
- Final export writes `thumbnail-vertical-{a,b,c}.png` into the video folder.

- [ ] **Step 3: Verify the `?grid` overlay markers in vertical mode**

Open one of the vertical variants in the browser with `?grid` appended (the contact sheet has a "view with grid" link per variant). Confirm:

- The 4×3 numbered red grid is visible.
- A red dashed band marks the bottom 25% of the canvas (TikTok UI).
- A red dashed square outlines the center 1:1 crop region (TikTok profile grid).

- [ ] **Step 4: Confirm renderer dimension assertions**

After "ship it", verify the exported PNGs have the expected dimensions:

```bash
node -e "const fs=require('node:fs');for(const f of ['thumbnail-vertical-a.png','thumbnail-vertical-b.png','thumbnail-vertical-c.png']){const b=fs.readFileSync('videos/why-text-is-hard-2026-05-07/'+f);console.log(f, {w:b.readUInt32BE(16),h:b.readUInt32BE(20)});}"
```

Expected: each line reports `{ w: 1080, h: 1920 }`.

- [ ] **Step 5: Confirm renderer tests still pass**

```bash
cd tools/thumbnail-render && npm test
```

Expected: all six tests pass.

---

## Done

After Task 8 verification passes, the feature is complete. The user can now invoke the skill in either mode against any video folder, and the renderer, templates, and reference docs handle both 1280×720 horizontal YouTube thumbnails and 1080×1920 vertical Shorts/TikTok covers.
