# Thumbnail Creator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `thumbnail-creator` skill plus its companion Node tool so the user can generate three production-ready 1280×720 YouTube thumbnail variants for any hyper-frames video, iterate on them in the browser, and export PNGs ready for YouTube's A/B test feature.

**Architecture:** Two artifacts. `tools/thumbnail-render/` is a brand-agnostic Node project that turns HTML into PNG via Playwright headless Chrome. `.claude/skills/thumbnail-creator/` is a Claude skill (markdown + HTML/CSS templates) that owns the channel's locked visual signature and the per-video judgment (text rephrasing, accent words, icon picking, iteration loop). The split mirrors the existing `tools/narration-map/` + `script-writer` skill pattern in this repo.

**Tech Stack:** Node 20+ (uses `node:test`, native `fetch`), Playwright (headless Chrome for screenshots), `lucide` npm package (icon SVG bodies, version-pinned). No build step; all `.mjs` ESM, run directly.

**Spec:** `docs/superpowers/specs/2026-05-08-thumbnail-creator-design.md`

---

## Pre-flight notes

- **Not a git repo.** This project has no `.git` directory. Commit steps are omitted from each task. If the user later runs `git init`, they can commit the whole tree at once.
- **Node 20+ required.** Confirms with `node --version`. If the user has an older Node, they need to upgrade before Task 2.
- **Playwright browser install** runs once after `pnpm install` in Task 1: `npx playwright install chromium` (~150 MB download). The tool README documents this.
- **Visual signature is already locked** (see spec §4). Constants are baked into `templates/styles.css` in Task 7. There is no separate "design exercise" task — that work happened during brainstorming.

---

## File structure

### Created files

```
tools/thumbnail-render/
├── package.json
├── README.md
├── .gitignore
├── bin/
│   └── render.mjs                          # CLI wrapper (single + --variants modes)
├── src/
│   └── render.mjs                          # core renderHtmlToPng()
├── scripts/
│   └── sync-icons.mjs                      # rebuild icons/lucide.json from npm `lucide`
├── icons/
│   └── lucide.json                         # version-pinned cache of SVG bodies
└── tests/
    ├── render.test.mjs                     # node:test for renderHtmlToPng()
    └── fixtures/
        └── basic.html                      # tiny fixture HTML for the test

.claude/skills/thumbnail-creator/
├── SKILL.md
├── templates/
│   ├── styles.css                          # LOCKED visual signature (B)
│   ├── variant.html                        # single-variant template
│   └── contact-sheet.html                  # 3-up review page
└── reference/
    ├── visual-signature.md
    ├── text-rephrase-recipes.md
    ├── red-word-recipes.md
    ├── icon-picking.md
    └── iteration-recipes.md
```

### Modified files

None. This is all greenfield.

### Deferred to a follow-up plan

`tools/thumbnail-render/bin/serve.mjs` (auto-refresh dev server). The spec marks it optional. The contact sheet works fine via `file://` URL in v1; defer the server until the iteration loop proves it's needed.

---

## Task 1: Initialize the Node tool package

**Files:**
- Create: `tools/thumbnail-render/package.json`
- Create: `tools/thumbnail-render/.gitignore`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render/{bin,src,scripts,icons,tests/fixtures}
```

- [ ] **Step 2: Write `package.json`**

```json
{
  "name": "@hyper-frames/thumbnail-render",
  "version": "0.1.0",
  "description": "Render hyper-frames thumbnail HTML to 1280x720 PNG via Playwright. Brand-agnostic; the channel's visual signature lives in the thumbnail-creator skill, not here.",
  "type": "module",
  "private": true,
  "engines": { "node": ">=20" },
  "scripts": {
    "test": "node --test tests/",
    "sync-icons": "node scripts/sync-icons.mjs"
  },
  "dependencies": {
    "playwright": "1.49.1",
    "lucide": "0.462.0"
  }
}
```

The two pinned versions are deliberate: Playwright API is stable but installs the matching browser binaries; Lucide icon glyphs evolve and we don't want silent visual drift.

- [ ] **Step 3: Write `.gitignore`**

```
node_modules/
*.log
.DS_Store
```

- [ ] **Step 4: Install dependencies**

Run from inside `tools/thumbnail-render/`:

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render && npm install
```

Expected: `node_modules/` populated, no errors. Then install the Chromium binary:

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render && npx playwright install chromium
```

Expected: "chromium 131.x downloaded" or similar; takes ~30s.

---

## Task 2: Write the test fixture

**Files:**
- Create: `tools/thumbnail-render/tests/fixtures/basic.html`

- [ ] **Step 1: Write the fixture**

Minimal HTML at 1280×720 with one visible element, used to verify the renderer wires together correctly. Keep it tiny so the test isn't sensitive to font loading or layout.

```html
<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    html, body { margin: 0; padding: 0; }
    body { width: 1280px; height: 720px; background: #1A1410; color: #F5E6D3;
           font-family: system-ui, sans-serif; display: flex;
           align-items: center; justify-content: center; }
    h1 { font-size: 80px; margin: 0; }
  </style>
</head>
<body>
  <h1>RENDERER OK</h1>
</body>
</html>
```

---

## Task 3: Write the failing test for `renderHtmlToPng()`

**Files:**
- Create: `tools/thumbnail-render/tests/render.test.mjs`

- [ ] **Step 1: Write the test**

```javascript
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, existsSync, statSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderHtmlToPng } from '../src/render.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const fixture = path.join(__dirname, 'fixtures', 'basic.html');

test('renderHtmlToPng writes a PNG at the requested path', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'tnr-'));
  const out = path.join(dir, 'out.png');
  try {
    await renderHtmlToPng(fixture, out);
    assert.ok(existsSync(out), 'output PNG should exist');
    assert.ok(statSync(out).size > 1000, 'output PNG should be non-trivially sized (>1KB)');
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('renderHtmlToPng throws a useful error when the input file is missing', async () => {
  await assert.rejects(
    () => renderHtmlToPng('/nonexistent/file.html', '/tmp/nowhere.png'),
    /not found|ENOENT/i
  );
});
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render && npm test
```

Expected: FAIL with `Cannot find module '../src/render.mjs'` or similar.

---

## Task 4: Implement `renderHtmlToPng()`

**Files:**
- Create: `tools/thumbnail-render/src/render.mjs`

- [ ] **Step 1: Write the implementation**

```javascript
import { chromium } from 'playwright';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export const THUMBNAIL_WIDTH = 1280;
export const THUMBNAIL_HEIGHT = 720;

/**
 * Render an HTML file to a PNG at exact thumbnail dimensions.
 *
 * Waits for `document.fonts.ready` before screenshotting — without this,
 * web-font requests resolve after the screenshot fires and the PNG shows
 * the browser's fallback font instead of the intended one.
 *
 * @param {string} htmlPath - absolute path to the input HTML file
 * @param {string} outPngPath - absolute path where the PNG will be written
 * @returns {Promise<void>}
 */
export async function renderHtmlToPng(htmlPath, outPngPath) {
  if (!existsSync(htmlPath)) {
    throw new Error(`Input HTML not found: ${htmlPath} (ENOENT)`);
  }

  const browser = await chromium.launch();
  try {
    const context = await browser.newContext({
      viewport: { width: THUMBNAIL_WIDTH, height: THUMBNAIL_HEIGHT },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    const fileUrl = pathToFileURL(path.resolve(htmlPath)).href;
    await page.goto(fileUrl, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({
      path: outPngPath,
      type: 'png',
      clip: { x: 0, y: 0, width: THUMBNAIL_WIDTH, height: THUMBNAIL_HEIGHT },
    });
  } finally {
    await browser.close();
  }
}
```

- [ ] **Step 2: Run the test to verify it passes**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render && npm test
```

Expected: both tests PASS. The first run takes ~3-5s because Chromium starts up.

---

## Task 5: Write the CLI wrapper `bin/render.mjs`

**Files:**
- Create: `tools/thumbnail-render/bin/render.mjs`

The CLI supports two modes:
- Single-file: `render.mjs <html> --out <png>`
- Variants: `render.mjs <round-dir> --variants --out-dir <video-dir>` — renders `a.html`, `b.html`, `c.html` from the round dir, writing `thumbnail-{a,b,c}.png` into `<video-dir>`.

- [ ] **Step 1: Write the CLI**

```javascript
#!/usr/bin/env node
import path from 'node:path';
import { existsSync, statSync } from 'node:fs';
import { renderHtmlToPng } from '../src/render.mjs';

function usage() {
  console.error(`Usage:
  render.mjs <html-path> --out <png-path>
  render.mjs <round-dir> --variants --out-dir <video-folder>

Single-file mode renders one HTML to one PNG at 1280x720.
Variants mode renders a.html, b.html, c.html from <round-dir>
to thumbnail-a.png, thumbnail-b.png, thumbnail-c.png in <video-folder>.`);
  process.exit(2);
}

function parseArgs(argv) {
  const args = { positional: [], flags: {} };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--variants') { args.flags.variants = true; }
    else if (a === '--out')      { args.flags.out      = argv[++i]; }
    else if (a === '--out-dir')  { args.flags.outDir   = argv[++i]; }
    else if (a.startsWith('--')) { console.error(`Unknown flag: ${a}`); usage(); }
    else { args.positional.push(a); }
  }
  return args;
}

async function renderSingle(htmlPath, outPath) {
  const absHtml = path.resolve(htmlPath);
  const absOut = path.resolve(outPath);
  console.log(`render: ${absHtml} -> ${absOut}`);
  await renderHtmlToPng(absHtml, absOut);
  console.log(`done: ${absOut}`);
}

async function renderVariants(roundDir, outDir) {
  const absRound = path.resolve(roundDir);
  const absOut = path.resolve(outDir);
  if (!existsSync(absRound) || !statSync(absRound).isDirectory()) {
    throw new Error(`round-dir not found or not a directory: ${absRound}`);
  }
  if (!existsSync(absOut) || !statSync(absOut).isDirectory()) {
    throw new Error(`out-dir not found or not a directory: ${absOut}`);
  }
  for (const letter of ['a', 'b', 'c']) {
    const html = path.join(absRound, `${letter}.html`);
    if (!existsSync(html)) {
      throw new Error(`missing variant HTML: ${html}`);
    }
    const png = path.join(absOut, `thumbnail-${letter}.png`);
    console.log(`render: ${html} -> ${png}`);
    await renderHtmlToPng(html, png);
  }
  console.log(`done: thumbnail-{a,b,c}.png in ${absOut}`);
}

const args = parseArgs(process.argv.slice(2));

try {
  if (args.flags.variants) {
    if (args.positional.length !== 1 || !args.flags.outDir) usage();
    await renderVariants(args.positional[0], args.flags.outDir);
  } else {
    if (args.positional.length !== 1 || !args.flags.out) usage();
    await renderSingle(args.positional[0], args.flags.out);
  }
} catch (err) {
  console.error(`error: ${err.message}`);
  process.exit(1);
}
```

- [ ] **Step 2: Make it executable**

```bash
chmod +x /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render/bin/render.mjs
```

- [ ] **Step 3: Smoke-test the CLI in single mode**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render && \
  node bin/render.mjs tests/fixtures/basic.html --out /tmp/cli-test.png && \
  ls -la /tmp/cli-test.png
```

Expected: `/tmp/cli-test.png` exists, ~10-30 KB. Open it in Preview to confirm it shows "RENDERER OK" centered on the brown background.

- [ ] **Step 4: Smoke-test the CLI in variants mode**

```bash
mkdir -p /tmp/round-test /tmp/out-test && \
  cp tests/fixtures/basic.html /tmp/round-test/a.html && \
  cp tests/fixtures/basic.html /tmp/round-test/b.html && \
  cp tests/fixtures/basic.html /tmp/round-test/c.html && \
  node bin/render.mjs /tmp/round-test --variants --out-dir /tmp/out-test && \
  ls -la /tmp/out-test/
```

Expected: `thumbnail-a.png`, `thumbnail-b.png`, `thumbnail-c.png` all created.

---

## Task 6: Build the Lucide icon cache

**Files:**
- Create: `tools/thumbnail-render/scripts/sync-icons.mjs`
- Create: `tools/thumbnail-render/icons/lucide.json`

The skill needs a curated set of Lucide icon SVG bodies that it can drop into thumbnails. We don't bundle the full ~1500-icon set — we cache only the topics likely to appear. New topics can be added by updating the list and re-running `npm run sync-icons`.

- [ ] **Step 1: Write `scripts/sync-icons.mjs`**

```javascript
import { writeFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import * as lucide from 'lucide';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT = path.resolve(__dirname, '..', 'icons', 'lucide.json');

// Topics that recur in technical-explainer videos. Add to this list and
// re-run `npm run sync-icons` to expand the cache. Names must match Lucide's
// camelCase exports (Database, FileText, etc., not 'database' / 'file-text').
const TOPICS = [
  'Database', 'Lock', 'Key', 'Code', 'FileText', 'Terminal', 'Cpu',
  'Network', 'Server', 'HardDrive', 'Cloud', 'Globe', 'Shield', 'Layers',
  'GitBranch', 'GitMerge', 'Hash', 'Binary', 'Activity', 'Zap',
  'Dice5', 'KeyRound', 'Fingerprint', 'Eye', 'EyeOff', 'Mouse', 'Keyboard',
  'Image', 'Type', 'Brackets', 'FunctionSquare', 'Workflow',
];

const out = {};
for (const name of TOPICS) {
  const node = lucide[name];
  if (!node) {
    console.warn(`skip: lucide export "${name}" not found`);
    continue;
  }
  // lucide exports each icon as [tag, attrs, children] — render to SVG body
  // (without the outer <svg> tag, so the skill can compose viewBox/styles).
  const [, , children] = node;
  const body = children.map(([tag, attrs]) => {
    const a = Object.entries(attrs).map(([k, v]) => `${k}="${v}"`).join(' ');
    return `<${tag} ${a} />`;
  }).join('');
  out[name] = body;
}

writeFileSync(OUT, JSON.stringify(out, null, 2) + '\n');
console.log(`wrote ${Object.keys(out).length} icons to ${OUT}`);
```

- [ ] **Step 2: Run the sync**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render && npm run sync-icons
```

Expected: `icons/lucide.json` created, ~30 keys, no `skip:` warnings. If a name is wrong, the warning tells you — fix the TOPICS array and re-run.

- [ ] **Step 3: Sanity-check the JSON**

```bash
node -e "const j = require('./tools/thumbnail-render/icons/lucide.json'); console.log(Object.keys(j).length, 'icons:', Object.keys(j).slice(0,5).join(', '), '...')"
```

Expected: prints icon count and first few names.

---

## Task 7: Write the tool's README

**Files:**
- Create: `tools/thumbnail-render/README.md`

- [ ] **Step 1: Write the README**

```markdown
# thumbnail-render

Brand-agnostic Node tool that turns thumbnail HTML into 1280×720 PNG via
Playwright headless Chrome. Used by the `thumbnail-creator` Claude skill;
the channel's visual signature lives in that skill, not here.

## Setup (once)

```bash
cd tools/thumbnail-render
npm install
npx playwright install chromium
```

Chromium is ~150 MB; install once per machine.

## CLI

```bash
# Single file: HTML → one PNG
node bin/render.mjs <html-path> --out <png-path>

# Variants: a.html, b.html, c.html → thumbnail-{a,b,c}.png
node bin/render.mjs <round-dir> --variants --out-dir <video-folder>
```

Both modes accept absolute or relative paths. The renderer always uses
absolute paths internally, so the caller doesn't need to be in any
particular CWD.

## Lucide icon cache

`icons/lucide.json` ships with a curated subset of Lucide icons used by the
skill. To add a new icon, edit the `TOPICS` array in `scripts/sync-icons.mjs`
and run:

```bash
npm run sync-icons
```

The Lucide version is pinned in `package.json` — bumping it can change icon
glyphs, so do it intentionally and review the contact-sheet output.

## Tests

```bash
npm test
```

Uses `node --test`. The render test launches a real Chromium and screenshots
a fixture HTML; it takes ~3-5s.

## Known footguns

- **Web font loading.** The renderer awaits `document.fonts.ready` before
  screenshotting. Without that, web-font requests resolve after the screenshot
  fires and the PNG falls back to the browser's default font. If a thumbnail
  ever shows wrong typography, this is the first thing to check.
- **Lucide drift.** The pinned version + the cached `icons/lucide.json` keep
  glyphs stable. Running `npm run sync-icons` against a new Lucide version may
  silently change icon shapes.
```

---

## Task 8: Write the locked visual signature CSS

**Files:**
- Create: `.claude/skills/thumbnail-creator/templates/styles.css`

This is the LOCKED visual signature B from spec §4. It does not change per video.

- [ ] **Step 1: Create the skill folder structure**

```bash
mkdir -p /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/.claude/skills/thumbnail-creator/{templates,reference}
```

- [ ] **Step 2: Write `styles.css`**

```css
/* thumbnail-creator — LOCKED visual signature (B: Terminal Scholar)
 * Constants are documented in reference/visual-signature.md.
 * Do NOT change these per video. Changing them is a rebrand exercise.
 */

@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@800&display=swap');

:root {
  --bg: #1A1410;        /* espresso brown */
  --text: #F5E6D3;      /* warm off-white */
  --accent: #FFB627;    /* amber */
  --canvas-w: 1280px;
  --canvas-h: 720px;
}

html, body {
  margin: 0;
  padding: 0;
  background: var(--bg);
}

.thumbnail {
  width: var(--canvas-w);
  height: var(--canvas-h);
  background: var(--bg);
  font-family: 'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace;
  position: relative;
  overflow: hidden;
}

.thumbnail-text {
  position: absolute;
  left: 80px;
  top: 100px;
  right: 380px;
  color: var(--text);
  font-weight: 800;
  line-height: 1.05;
  letter-spacing: -0.02em;
  text-transform: uppercase;
  display: flex;
  flex-direction: column;
  gap: 16px;
  white-space: nowrap;
}

.thumbnail-row {
  display: block;
}

.thumbnail-text .accent,
.thumbnail-row.accent {
  color: var(--accent);
}

.thumbnail-icon {
  position: absolute;
  right: 110px;
  top: 50%;
  transform: translateY(-50%);
  width: 220px;
  height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.thumbnail-icon svg {
  width: 220px;
  height: 220px;
}
.thumbnail-icon .stroke {
  stroke: var(--text);
  stroke-width: 8;
  fill: none;
}
.thumbnail-icon .accent-fill {
  fill: var(--accent);
}
.thumbnail-icon .accent-stroke {
  stroke: var(--accent);
  stroke-width: 8;
  fill: none;
}
```

The `.thumbnail-row` font-size is set per-variant (the variant.html template injects it inline) because it's autosized to fit the longest row. See Task 9.

---

## Task 9: Write `templates/variant.html`

**Files:**
- Create: `.claude/skills/thumbnail-creator/templates/variant.html`

This template uses placeholder tokens (e.g., `{{TITLE_ROW_1}}`) that the skill substitutes when rendering each round. It is NOT a build-time template engine — the skill does plain string replacement when generating each `a.html`, `b.html`, `c.html`.

- [ ] **Step 1: Write the template**

The template uses `{{TOKEN}}` placeholders that the skill substitutes at write time via plain string replacement (no template engine). The `{{STYLES_HREF}}` token resolves to the absolute `file://` URL of `templates/styles.css` so the round folder's depth in the tree doesn't matter.

```html
<!--
  Tokens substituted by the thumbnail-creator skill:
    {{STYLES_HREF}}        absolute file:// URL to templates/styles.css
    {{TITLE_PLAIN}}        plain text title (for <title>)
    {{ROW_FONT_SIZE_PX}}   integer pixel size, autosized per variant
    {{TITLE_ROW_1..3}}     row HTML with accent <span> markup
    {{ICON_SVG_BODY}}      SVG body (children of <svg>); Lucide bodies use
                           viewBox 0 0 24 24, hand-coded fallbacks may differ
-->
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{{TITLE_PLAIN}}</title>
  <link rel="stylesheet" href="{{STYLES_HREF}}">
</head>
<body>
  <div class="thumbnail">
    <div class="thumbnail-text" style="font-size: {{ROW_FONT_SIZE_PX}}px;">
      <span class="thumbnail-row">{{TITLE_ROW_1}}</span>
      <span class="thumbnail-row">{{TITLE_ROW_2}}</span>
      <span class="thumbnail-row">{{TITLE_ROW_3}}</span>
    </div>
    <div class="thumbnail-icon">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">{{ICON_SVG_BODY}}</svg>
    </div>
  </div>
</body>
</html>
```

Reference for the values the skill computes:

| Token | Source | Example |
|---|---|---|
| `{{STYLES_HREF}}` | `file://` + absolute path to `<repo-root>/.claude/skills/thumbnail-creator/templates/styles.css` | `file:///Users/.../templates/styles.css` |
| `{{TITLE_PLAIN}}` | rephrased title joined with spaces, no markup | `TEXT RENDERING IS INSANELY DIFFICULT` |
| `{{ROW_FONT_SIZE_PX}}` | computed from the longest row's char count (see Step 3 of skill) | `96` |
| `{{TITLE_ROW_1..3}}` | each row's HTML with `<span class="accent">…</span>` wrapping accent words | `<span class="accent">TEXT</span> RENDERING` |
| `{{ICON_SVG_BODY}}` | SVG body string from `tools/thumbnail-render/icons/lucide.json` (or a hand-coded fallback) | `<rect class="accent-fill" .../><path class="stroke" .../>` |

---

## Task 10: Write `templates/contact-sheet.html`

**Files:**
- Create: `.claude/skills/thumbnail-creator/templates/contact-sheet.html`

The contact sheet is the user's review surface for one round. It shows all three variants at full size *and* at YouTube feed grid size (~210 px) so the user can judge legibility at the size that actually matters.

- [ ] **Step 1: Write the template**

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Round {{ROUND_NUMBER}} — {{VIDEO_SLUG}}</title>
  <link rel="stylesheet" href="{{STYLES_HREF}}">
  <style>
    /* contact-sheet chrome — separate from the thumbnail's locked styles */
    body {
      background: #0a0a0a;
      color: #c0c0c0;
      font-family: ui-sans-serif, system-ui, sans-serif;
      padding: 32px;
    }
    h1 { font-size: 18px; margin: 0 0 4px; color: #fff; font-weight: 600; }
    .meta { font-size: 13px; color: #888; margin-bottom: 32px; }
    .meta code { background: #222; padding: 2px 6px; border-radius: 3px;
                 font-size: 12px; color: #ddd; }

    .variant { margin-bottom: 56px; }
    .variant-header { display: flex; align-items: baseline; gap: 16px;
                      margin-bottom: 12px; padding-bottom: 8px;
                      border-bottom: 1px solid #222; }
    .variant-letter {
      display: inline-flex; align-items: center; justify-content: center;
      width: 32px; height: 32px; border-radius: 4px;
      background: #1A1410; color: #FFB627; font-weight: 700; font-size: 16px;
    }
    .variant-text {
      font-family: ui-monospace, monospace; font-size: 13px; color: #aaa;
    }

    .row { display: flex; gap: 28px; align-items: flex-start; }
    .row-label { font-size: 10px; color: #666; text-transform: uppercase;
                 letter-spacing: 0.08em; margin-bottom: 8px; }

    /* Thumbnails are rendered at 1280x720 internally, then CSS-scaled. */
    .full-wrap { width: 512px; height: 288px; overflow: hidden; }
    .full-wrap .thumbnail { transform: scale(0.4); transform-origin: top left; }
    .grid-wrap { width: 210px; height: 118px; overflow: hidden; }
    .grid-wrap .thumbnail { transform: scale(0.164); transform-origin: top left; }
  </style>
</head>
<body>
  <h1>Round {{ROUND_NUMBER}} — {{VIDEO_SLUG}}</h1>
  <div class="meta">
    Title input: <code>{{TITLE_INPUT}}</code><br>
    Folder: <code>{{ROUND_DIR_ABS}}</code>
  </div>

  {{VARIANTS_HTML}}

</body>
</html>
```

The `{{VARIANTS_HTML}}` token is replaced with three blocks of this shape, one per variant (the skill builds the string by repeating the block):

```html
<div class="variant">
  <div class="variant-header">
    <span class="variant-letter">{{LETTER_UPPER}}</span>
    <span class="variant-text">{{TITLE_PLAIN}}</span>
  </div>
  <div class="row">
    <div>
      <div class="row-label">Full size (40% of 1280×720)</div>
      <div class="full-wrap">
        {{THUMBNAIL_DIV}}
      </div>
    </div>
    <div>
      <div class="row-label">YouTube feed grid (~210px)</div>
      <div class="grid-wrap">
        {{THUMBNAIL_DIV}}
      </div>
    </div>
  </div>
</div>
```

`{{THUMBNAIL_DIV}}` is the same `.thumbnail` markup used in `variant.html` (Task 9), inlined twice (once for full-wrap, once for grid-wrap). The skill builds this string when generating the contact sheet.

Document the tokens in a leading comment:

```html
<!--
  Tokens substituted by the thumbnail-creator skill:
    {{STYLES_HREF}}     absolute file:// URL to templates/styles.css
    {{ROUND_NUMBER}}    integer (1, 2, 3, ...)
    {{VIDEO_SLUG}}      e.g. "why-text-is-hard-2026-05-07"
    {{TITLE_INPUT}}     the working title that drove the rephrases
    {{ROUND_DIR_ABS}}   absolute path to round-N folder
    {{VARIANTS_HTML}}   concatenated HTML for the three variants

  Per-variant tokens (used inside {{VARIANTS_HTML}}):
    {{LETTER_UPPER}}    A | B | C
    {{TITLE_PLAIN}}     the rephrased thumbnail text, plain
    {{THUMBNAIL_DIV}}   the .thumbnail markup, identical for full + grid wraps
-->
```

---

## Task 11: Write `reference/visual-signature.md`

**Files:**
- Create: `.claude/skills/thumbnail-creator/reference/visual-signature.md`

- [ ] **Step 1: Write the file**

```markdown
# Visual signature — locked

The channel's thumbnail brand. These constants do not change per video.
Changing them is a rebrand exercise, not a per-video parameter.

If you ever rebrand: re-run the visual-signature design exercise (propose
3 candidate signatures, pick one, update both this file and
`templates/styles.css`). Do not change one constant in isolation — the four
together are what gives the channel a recognizable silhouette in the feed.

## The constants

| Constant | Value |
|---|---|
| Font | `JetBrains Mono`, weight 800 (ExtraBold) |
| Background | `#1A1410` (espresso brown) |
| Text color | `#F5E6D3` (warm off-white) |
| Accent color | `#FFB627` (amber) |
| Icon style | Lucide line icons, stroke-width 8 in 24×24 viewBox; accent-color fill on exactly one detail |

## Why each constant

**Font — JetBrains Mono ExtraBold.** Monospace evokes terminals and code
without copying Pawel's bitmap font (Press Start 2P-style). ExtraBold
survives at thumbnail grid size (~210 px wide on the YouTube feed) where
thinner weights smudge. JetBrains Mono is widely-loaded enough to be a
recognizable choice without being precious.

**Background — #1A1410 espresso brown.** Differentiates from Pawel's pure
black AND from the cool-blue dark background most tech channels default to.
Warm dark reads as "scholarly" or "lab notebook" rather than "techbro" or
"cyberpunk." A viewer scanning a feed of dark-blue and pure-black thumbnails
notices warm dark immediately.

**Text — #F5E6D3 warm off-white.** Off-white instead of pure white
reinforces the paper/print register and prevents the high-contrast vibration
that pure-white-on-pure-black produces. Subtle, but adds up.

**Accent — #FFB627 amber.** High contrast against espresso. Warm complement
(both colors are in the same temperature family), so they don't fight each
other. Critically: not red. Pawel uses coral red. We use amber so a
side-by-side feed comparison is unambiguous.

**Icons — Lucide line, accent on one detail.** Real SVG icons (not styled
text or bitmap font glyphs). The "one detail" rule is what gives the icon
its accent without overwhelming it: the lock body in amber, but the
shackle in off-white; the second "A" in amber, the first in off-white;
the key bow in amber, the shaft in off-white.

## What we explicitly chose NOT to do

- Pawel's bitmap pixel font. Copying it would put our thumbnails next to
  his in any feed and lose every time on direct comparison.
- Pure black background. Saturated and indistinguishable from every other
  dark-mode tech channel.
- Coral red accent. That's now Pawel's signature; we'd be the imitator.
- White line icons with a red dot. Same reason — that's now him.
- "Explained in N Minutes" formula text. Strongly associated with him.

## Rebrand process (if ever needed)

1. Re-run the candidate-signatures design exercise (see brainstorming
   conversation 2026-05-08 for the format — three candidates, sample
   contact sheets, pick one).
2. Update this file with the new constants and the new "why."
3. Update `templates/styles.css` with the new CSS variable values.
4. Re-render the most recent video's thumbnails to verify the new brand
   reads as intended.
5. Do not retroactively re-render old videos' thumbnails — the brand
   evolution is part of the channel history.
```

---

## Task 12: Write `reference/text-rephrase-recipes.md`

**Files:**
- Create: `.claude/skills/thumbnail-creator/reference/text-rephrase-recipes.md`

- [ ] **Step 1: Write the file**

```markdown
# Text rephrase recipes

Patterns for turning a video's working title into a punchier thumbnail
text. The thumbnail text is **not** the video title — it's a bolder
rewrite per the research's rephrase pattern. The video title carries SEO
keywords; the thumbnail text wins the click.

These recipes are drawn from `research/pawel-code-stuff/analysis/script-patterns.md`
and the rephrase analysis in `research/pawel-code-stuff/analysis/thumbnail-patterns.md` §4.

## Hard constraints (every variant must satisfy)

- 7–11 words total.
- Exactly 3 rows.
- ALL CAPS.
- Fits in JetBrains Mono ExtraBold across 3 rows of ~13–14 monospace
  characters each at the target font size. The renderer does NOT silently
  shrink text to fit. If a rephrase doesn't fit, rewrite shorter or ask
  the user for a shorter wording — never let the renderer hide overflow.
- No question marks, ellipses, colons, parentheses.
- No adverbs except for emphasis ("INSANELY", "BRUTAL", "CATASTROPHIC").

## The rephrase moves

### Move 1 — Softer to harder

Replace softer phrasing with harder phrasing:

- "is intentionally" → "must"
- "can be" → "is"
- "how to make X" → imperative "make X"
- "why X is Y" (question) → "X is Y" (declarative)

**Example:** *"Why Good Password Hashing is Intentionally Slow"* →
**`GOOD PASSWORD / HASHING MUST / BE SLOW`**

### Move 2 — Question to declarative

If the title is a question, drop the question mark and assert the answer.

**Example:** *"Why is rendering text so complicated?"* →
**`TEXT RENDERING / IS INSANELY / DIFFICULT`**

### Move 3 — Narrow to sweeping

Replace a narrow technical claim with a sweeping one:

- "generates secure keys" → "secures the internet"
- "fixes a bug" → "saves your database"

**Example:** *"Why Moving Your Mouse Generates Secure Keys"* →
**`WHY YOUR MOUSE / SECURES THE / INTERNET`**

### Move 4 — Adjective upgrade

Push a soft adjective to a harder one:

- "complicated" → "insanely difficult"
- "fast" → "brutal"
- "important" → "catastrophic"
- "tricky" → "a fight"

The adverb is allowed *only* in upgrade position ("INSANELY", "ABSURDLY",
"DANGEROUSLY") — never as a hedge ("usually", "sort of", "kind of").

## Generating three variants

Each round produces 3 thumbnail-text rephrases. They should differ on
*direction*, not just on word choice — otherwise the user can't make a
real choice between them.

Recommended distribution per round:

1. **Variant A — direct upgrade.** Apply Move 1 + Move 4. Keep the title's
   topic noun front-and-center.
2. **Variant B — sweeping reframe.** Apply Move 3. Make the bigger claim.
3. **Variant C — punchy declarative.** Apply Move 2 + Move 4. Shortest
   wording; declares the surprising fact.

If the user says "all three feel safe", push Move 4 harder (escalate the
adjective) on all three. If "all three are too aggressive", soften Move 4
or drop it.

## Worked examples

### Example 1 — text rendering

- **Working title:** *Why is rendering text so complicated?*
- **Variant A (direct):** `TEXT RENDERING / IS INSANELY / DIFFICULT` (8 words)
- **Variant B (sweeping):** `A LETTER ON / YOUR SCREEN IS / A FIGHT` (8 words)
- **Variant C (punchy):** `YOUR FONT IS / LYING TO / YOU` (6 words — too short, expand to 7+)
  - Fixed: `YOUR FONT IS / LYING TO / YOUR EYES` (7 words)

### Example 2 — password hashing

- **Working title:** *Why good password hashing is intentionally slow*
- **Variant A:** `GOOD PASSWORD / HASHING MUST / BE SLOW` (7 words)
- **Variant B:** `THE FASTEST CODE / IS THE WORST / PASSWORD CODE` (10 words)
- **Variant C:** `HASHING SHOULD / TAKE A / WHOLE SECOND` (7 words)

### Example 3 — mouse keys

- **Working title:** *Why moving your mouse generates secure keys*
- **Variant A:** `YOUR MOUSE / GENERATES / SECURE KEYS` (6 — expand to 7+)
  - Fixed: `WHY YOUR MOUSE / GENERATES / SECURE KEYS` (7 words)
- **Variant B:** `WHY YOUR MOUSE / SECURES THE / INTERNET` (7 words)
- **Variant C:** `MOVE YOUR MOUSE / OR THE INTERNET / FAILS` (8 words)

## Anti-patterns

- "TOPIC EXPLAINED IN N MINUTES" — that's the formula pattern. The research
  shows it works for SEO-heavy topics but loses engagement; reserve it as a
  fallback when the user says "all three are too aggressive, give me one
  that's safer."
- Stacking adjectives ("INSANELY DIFFICULT IMPOSSIBLE") — pick one.
- Filler words ("ACTUALLY", "REALLY", "BASICALLY") — cut them.
- Apologetic framing ("MAYBE", "MIGHT", "PROBABLY") — never.
```

---

## Task 13: Write `reference/red-word-recipes.md`

**Files:**
- Create: `.claude/skills/thumbnail-creator/reference/red-word-recipes.md`

- [ ] **Step 1: Write the file**

```markdown
# Accent-word recipes

Rules for picking which words get the accent color (`#FFB627` amber).
Drawn from `research/pawel-code-stuff/analysis/thumbnail-patterns.md` §5.

(The research file calls these "red words" because Pawel uses red. Our
accent is amber. Same rules apply — same tier system, same cap.)

## The cap

**Maximum 2 accent regions per thumbnail.** Three would dilute the signal
and make the eye not know where to land.

## The tier system

### Tier 1 — always accent

The **topic noun** the viewer doesn't know yet but wants to. This is the
word the viewer is choosing the video for.

Examples: `INDEXES`, `COMPRESSION`, `HASHING`, `MOUSE`, `RENDERING`.

If you only mark one accent region per thumbnail, mark this one.

### Tier 2 — often accent (the second region)

The **verb or adjective creating tension** with the topic noun. This pair
is what makes the viewer's eye land on TWO accent words that don't
normally go together — and that mismatch is the curiosity gap.

Examples:
- `MOUSE` (noun) + `SECURES` (surprising verb)
- `RENDERING` (noun) + `INSANELY DIFFICULT` (surprising adjective)
- `PASSWORD HASHING` (noun) + `MUST BE SLOW` (counterintuitive verb)

### Tier 3 — never accent

Connectors. They carry no curiosity weight; accenting them wastes the cap.

`IS`, `VS`, `IN`, `BE`, `THE`, `A`, `AN`, `EXPLAINED`, `MUST`, `WHY`,
`HOW`, `WHAT`, `YOUR`, `YOU`.

## The three sub-patterns

Pick the pattern that fits the thumbnail's wording:

### Sub-pattern A — Topic-only

One accent region: just the topic noun. The safe default. Use when the
title doesn't have a clear tension verb/adjective.

**Example:** `DATABASE / INDEXES / EXPLAINED`
- accent: `INDEXES`

### Sub-pattern B — Contrast-pair

Two accent regions: both sides of an X-VS-Y comparison. The connector
"VS" stays in the text color. Implicit fight.

**Example:** `AUTO-INCREMENT / VS UUID / EXPLAINED`
- accent: `AUTO-INCREMENT`, `UUID`

### Sub-pattern C — Tension-pair (strongest)

Two accent regions: the topic noun + the surprising verb/adjective. The
viewer's eye lands on two accent words that don't normally go together.

**Example:** `WHY YOUR MOUSE / SECURES THE / INTERNET`
- accent: `MOUSE`, `SECURES`

## How to pick the pattern per variant

The 3 variants in a round can use different sub-patterns — that's part of
the variation. Suggested defaults:

- **Variant A** (direct upgrade text): sub-pattern A or C, whichever fits.
- **Variant B** (sweeping reframe text): sub-pattern C — the sweeping
  verb is exactly the tension word that earns accent.
- **Variant C** (punchy declarative text): sub-pattern A or C.

If a variant has no obvious tension verb/adjective, fall back to
sub-pattern A. Don't force tier 2 onto a connector word.

## When in doubt

Mark only the topic noun (tier 1, sub-pattern A). Under-using accent is
recoverable in the next round; over-using it dilutes the brand.
```

---

## Task 14: Write `reference/icon-picking.md`

**Files:**
- Create: `.claude/skills/thumbnail-creator/reference/icon-picking.md`

- [ ] **Step 1: Write the file**

```markdown
# Icon picking

Rules for choosing the single icon that appears on every variant in a
round.

## The constraints

- **One icon per video.** Same icon across all 3 variants in every round.
  Variation lives in text and accent placement, not the icon.
- **Names the topic statically.** No diagrams, no before/after, no arrows,
  no comparisons. The icon is the period at the end of the headline, not
  the headline itself.
- **One accent detail.** Apply the accent color to exactly one geometric
  region of the icon. Never tint the whole icon. The lock body but not
  the shackle. The key bow but not the shaft. The second "A" but not the
  first.

## Source of icons — Lucide first

Lucide is the primary source. Cached SVG bodies are at
`tools/thumbnail-render/icons/lucide.json` (committed, version-pinned).

To find the right icon: think of the **topic noun**, not the insight.
Then look it up in the cache.

### Lookup table

| Topic noun | Lucide name | Suggested accent region |
|---|---|---|
| Database, table, index | `Database` | top ellipse (the disk's "lid") |
| Password, auth, encryption | `Lock` | the body rectangle |
| Key, secret | `Key` or `KeyRound` | the bow (round end) |
| Code, function, method | `Code` | the angle brackets |
| File, document, format | `FileText` | the corner fold |
| Terminal, shell, CLI | `Terminal` | the prompt `>` |
| CPU, processor | `Cpu` | the central square |
| Network, request | `Network` | one node circle |
| Server, backend | `Server` | the indicator dot |
| Disk, storage | `HardDrive` | the indicator dot |
| Cloud, hosted | `Cloud` | one bump of the cloud |
| URL, web, internet | `Globe` | one meridian line |
| Security, protection | `Shield` | the inner mark |
| Layers, stack | `Layers` | the top layer |
| Branching, git | `GitBranch` | the merge node |
| Hash, identifier | `Hash` | one of the bars |
| Bits, binary | `Binary` | one of the digits |
| Performance, signal | `Activity` | a peak |
| Lightning, speed, power | `Zap` | the bolt body |
| Random, dice | `Dice5` | the center pip |
| Fingerprint, identity | `Fingerprint` | a ridge |
| Eye, observability | `Eye` | the pupil |
| Mouse, input | `Mouse` | the scroll wheel |
| Keyboard, input | `Keyboard` | one key |
| Image, raster | `Image` | the sun (corner circle) |
| Type, text | `Type` | the crossbar of the T |
| Brackets, syntax | `Brackets` | one bracket |
| Function, math | `FunctionSquare` | the f symbol |
| Workflow, pipeline | `Workflow` | one connector |

If a topic isn't in this table, search Lucide's icon set
(https://lucide.dev/icons) for the matching topic noun. If you find a
new one, add it to the `TOPICS` array in
`tools/thumbnail-render/scripts/sync-icons.mjs` and run
`npm run sync-icons` to refresh the cache.

## Fallback — hand-coded SVG

If no Lucide icon fits the topic, write a tiny hand-coded SVG inline.
Keep it simple and geometric — no figurative work, no realistic shading,
no gradients. Match the locked icon style: stroke-width 8, viewBox 24×24
(or larger if the topic needs more detail), stroke color = text color,
one accent-color region.

**Example — the "Aa" glyph for text-rendering videos**, since Lucide has
no letter-pair icon:

```svg
<svg viewBox="0 0 220 220" xmlns="http://www.w3.org/2000/svg">
  <!-- Capital A (left) -->
  <path class="stroke" d="M 18 180 L 60 30 L 102 180 M 35 130 L 85 130"
        stroke-linecap="round" stroke-linejoin="round" />
  <!-- Lowercase a (right, accent) -->
  <circle class="accent-stroke" cx="160" cy="135" r="38" />
  <line class="accent-stroke" x1="198" y1="100" x2="198" y2="180"
        stroke-linecap="round" />
</svg>
```

The hand-coded fallback uses the same `stroke` and `accent-stroke` classes
defined in `templates/styles.css` so it picks up the locked colors
automatically.

## Reuse is encouraged

If two videos share a topic family, share the icon. The research showed
Pawel reuses `Database` across both his database-indexes and
UUID-vs-autoincrement videos. The icon is a category marker, not a unique
identifier.

## When in doubt

Pick the most literal topic noun. "Database indexes" → `Database`. Don't
overthink. The icon's job is to confirm what the text already said, not
to be clever.
```

---

## Task 15: Write `reference/iteration-recipes.md`

**Files:**
- Create: `.claude/skills/thumbnail-creator/reference/iteration-recipes.md`

- [ ] **Step 1: Write the file**

```markdown
# Iteration recipes

How to interpret the user's free-form feedback after a round and decide
what the next round looks like. Default behavior: each invocation creates
a new `round-N/` folder; previous rounds are never overwritten.

## The default — new round, every time

Even when feedback is targeted ("just change DIFFICULT to BRUTAL in
variant A"), the default is to write a new round-N folder. This preserves
history and makes "go back to round 2's variant A" a one-line file copy.

The exception: when the user explicitly says "edit in place" or "just
change X in this round." Then write to the current round folder. The
default is still new round.

## The interpretation table

| User says | Interpretation | Action |
|---|---|---|
| "Done" / "ship it" / "export" / "approved" | Loop terminates | Run final export (Task 9 of skill workflow) |
| "B is good but bolder text" | Keep B, regenerate A and C with bolder rephrases | New round; B's text carried over; A/C regenerated by pushing Move 4 (adjective upgrade) on the rephrase recipes |
| "All three feel safe" | All variants too soft | New round; push Move 4 harder on all three; consider stronger Move 3 (sweeping reframe) on at least one |
| "All three are too aggressive" | Pushed too hard | New round; soften Move 4; consider sub-pattern A (topic-only accent) instead of tension-pair |
| "A's words but B's icon" | Mixed pick | New round; A's text + B's icon as the lead variant; regenerate two more |
| "Round 2's A was best — why did we move on?" | User wants to anchor on a past variant | New round; copy round-2/a.html as new round's A; regenerate B and C as variations of that anchor |
| "Try with PASSWORD as accent instead of HASHING" | Accent placement change | New round; same text and icon; only accent map changes |
| "Use a different icon" | Icon change | New round; same text and accent for each variant; pick different Lucide icon (or hand-code) |
| "Give me a safer option in the mix" | Wants the formula fallback | New round; one variant uses "TOPIC EXPLAINED IN N MINUTES" formula; other two stay rephrase |

## Heuristics for vague feedback

When the user says one word or a short phrase, apply the obvious
interpretation and ship the next round. Don't ask for clarification on
single-word feedback.

| Vague feedback | Action |
|---|---|
| "Punchier" | Push Move 4 (adjective upgrade) one notch on all three |
| "Softer" | Walk back Move 4; consider sub-pattern A on accent |
| "Bolder" | Same as "punchier" plus push Move 3 (sweeping reframe) |
| "Cleaner" | Reduce to sub-pattern A on accent (one accent region only); shorter wording |
| "Try again" / "no" | Regenerate all 3 fresh; don't carry anything from the previous round |

## When to ask vs. guess

Apply the obvious interpretation by default. Ask one short clarifying
question only when the feedback is structurally ambiguous — for example:

- "Make it about X" where X isn't in the title or script → ask "do you
  mean reframe the topic as X, or that the icon should be X?"
- "I want the second one to be more like the first" → ask "do you mean
  the same text shape, or the same accent placement, or both?"

Default: guess and ship the next round. The next round is cheap.

## What the skill never does

- **Picks a winner.** Three variants ship to YouTube; YouTube's A/B
  feature does the actual measurement. The skill never says "I think B
  is best."
- **Declares done unilaterally.** The loop ends only when the user says
  "ship it" or equivalent. The skill never offers "this is good enough,
  shall I export?" — wait for the user to call it.
- **Edits old rounds.** Past rounds are immutable. Even if a round had
  an obvious typo, fix it in a new round, not by editing the old one.
```

---

## Task 16: Write `SKILL.md`

**Files:**
- Create: `.claude/skills/thumbnail-creator/SKILL.md`

- [ ] **Step 1: Write `SKILL.md`**

```markdown
---
name: thumbnail-creator
description: Guided generator that turns a hyper-frames video's working title into three production-ready 1280×720 YouTube thumbnail variants in the channel's locked visual style, with an iterative review loop. Use this skill whenever the user wants to create, draft, generate, design, or A/B test thumbnails for a hyper-frames video — phrases like "make a thumbnail for this video", "I need thumbnails", "generate thumbnail variants", "design a thumbnail", or any request that names a `videos/<slug>-<date>/` folder and asks for a thumbnail. Also triggers when the user runs the skill from inside a video folder after the script is drafted.
---

# thumbnail-creator

You are guiding the user through creating three YouTube thumbnail variants
for a single hyper-frames video. Output: three HTML variants and a
contact-sheet review page per round, then three PNGs ready for YouTube's
native A/B test feature once the user approves.

The visual signature is **locked** (font, background, accent color, text
color, icon style — all in `templates/styles.css` and documented in
`reference/visual-signature.md`). You do not redesign it per video. You
only choose: thumbnail text, accent placement, and icon.

## Pre-flight check

Before doing anything, verify the visual signature is locked: check that
`templates/styles.css` contains real CSS (not placeholder content) and
that `reference/visual-signature.md` exists. If either is missing or
empty, refuse to run with this message:

> "Visual signature not yet locked. Run the visual-signature design
> exercise first — see `reference/visual-signature.md` for the rebrand
> process."

If both are present, continue.

## Workflow

### Step 1 — Resolve the target video folder

Resolve in this order:

1. If the user's message contains a path like `videos/<slug>-<date>/`
   (relative or absolute), use that.
2. If the current working directory matches `**/videos/<slug>-<date>/`,
   use that.
3. Otherwise, ask: "Which video folder should I work in?" — list existing
   `videos/*` directories to make the choice concrete.

Convert the result to an absolute path. Use that absolute path for every
subsequent file read and write — do not depend on CWD after this step.

### Step 2 — Read the title and topic context

From the resolved `<video-dir>`:

- Read `<video-dir>/outline.md`. The H1 is the working title (format:
  `# <topic> — 9-beat outline`). Extract the topic.
- Read `<video-dir>/script.md` for prose body context. Mine candidate
  nouns for icon picking and accent words.

If `outline.md` is missing or its H1 isn't a usable working title, ask
the user for the title and a 2-line topic summary before continuing.

If `script.md` is missing, warn the user but proceed — the rephrase
step works on the title alone; icon and accent picks just have less
context to draw from.

### Step 3 — Generate three thumbnail-text rephrases

Load `reference/text-rephrase-recipes.md`. Apply the recipes to produce
three variant texts that:

- Are 7–11 ALL CAPS words each.
- Break into exactly 3 rows.
- Read as bolder, more declarative claims than the working title.
- Fit cleanly in JetBrains Mono ExtraBold within the available text
  column (~820 px wide).

The three variants must differ on **direction** (direct upgrade /
sweeping reframe / punchy declarative), not just word choice — otherwise
the user can't make a real choice between them.

#### Computing the per-variant font size

JetBrains Mono is monospace, so the longest row determines the maximum
font size. The formula:

```
longest_row_chars   = max character count across the 3 rows
                      (count letters, digits, and spaces; not the
                      <span> markup)
ROW_FONT_SIZE_PX    = floor(820 / (longest_row_chars * 0.6))
                      capped at 140
```

Examples (verified against rendered mockups):
- 13 chars → 105 px
- 14 chars → 97 px (rounds to 96)
- 15 chars → 91 px
- 16 chars → 85 px (visibly small — consider rephrasing shorter)

If the computed size falls below 80 px, reject the rephrase and either
produce a shorter wording or ask the user to choose a shorter title.
The renderer must NOT silently shrink — preview-vs-output drift is the
worst failure mode.

### Step 4 — Pick accent words per variant

Load `reference/red-word-recipes.md`. For each variant, pick the accent
word(s):

- Tier 1 (always accent): the topic noun.
- Tier 2 (often accent): the verb/adjective creating tension with the
  noun.
- Tier 3 (never accent): connectors.
- Cap: 2 accent regions per variant.

### Step 5 — Pick the icon

Load `reference/icon-picking.md`. Pick **one** Lucide icon for the topic
(same icon across all 3 variants in this round). If no Lucide icon fits,
hand-code a tiny SVG using the locked icon style.

The SVG body for Lucide icons comes from
`<repo-root>/tools/thumbnail-render/icons/lucide.json`. Read that file,
look up by Lucide name (e.g. `Lock`, `Database`), and use the body string
verbatim.

### Step 6 — Compute the next round number and write the HTML

Round number `N`:
- List entries in `<video-dir>/thumbnails/`.
- Filter for names matching `round-(\d+)`.
- `N = max(captured numbers) + 1`, or `1` if none exist.
- This handles user-deleted rounds correctly — pick `max + 1`, NOT
  `count + 1`.

Create `<video-dir>/thumbnails/round-N/`. Read the templates from
`templates/variant.html` and `templates/contact-sheet.html`. Substitute
tokens (see those files' leading comments for the token list).

Write:
- `<video-dir>/thumbnails/round-N/a.html`
- `<video-dir>/thumbnails/round-N/b.html`
- `<video-dir>/thumbnails/round-N/c.html`
- `<video-dir>/thumbnails/round-N/contact-sheet.html`

For the `{{STYLES_HREF}}` token, use the absolute file:// URL to
`<repo-root>/.claude/skills/thumbnail-creator/templates/styles.css`. Do
NOT use a relative path; the round folder is deep enough that relative
paths are fragile.

### Step 7 — Print the contact-sheet URL

Tell the user:

> "Round N is ready. Open `file://<absolute-path-to-contact-sheet.html>`
> in your browser. The page shows each variant at full 1280×720 plus a
> small grid-size simulation (~210×118 px) so you can judge legibility
> at the YouTube feed size. Tell me what you want to change."

### Step 8 — Iterate

Receive the user's feedback. Interpret per
`reference/iteration-recipes.md`. Generate the next round (Step 6 again
with the new content). Loop.

The default is always a new round folder. Edit-in-place only when the
user explicitly says so.

### Step 9 — Final export

When the user signals approval ("ship it", "export", "done", "approved"),
run the renderer to produce the final PNGs. Use absolute paths for both
the renderer binary and the round directory:

```bash
node <repo-root>/tools/thumbnail-render/bin/render.mjs \
  <video-dir>/thumbnails/round-N \
  --variants \
  --out-dir <video-dir>
```

This writes:
- `<video-dir>/thumbnail-a.png`
- `<video-dir>/thumbnail-b.png`
- `<video-dir>/thumbnail-c.png`

Print the three absolute paths so the user can drag them into YouTube's
A/B test upload UI.

## Hard rules (always in effect)

- Exactly 7–11 words per variant.
- Exactly 3 rows of text per variant.
- ALL CAPS, always.
- Maximum 2 accent regions per variant.
- No question marks, ellipses, colons, parentheses, emoji, arrows, drop
  shadows, or gradients.
- The icon names the topic statically. Never the insight, never a
  before/after, never a comparison.
- The visual signature constants do not change per video.
- Never pick a winner from the three variants. The user judges; YouTube's
  A/B mechanism measures.
- Termination: the loop ends when the user says "ship it" or equivalent.
  Never declare "this is good enough" on your own.

## Reference files (load on demand)

- `reference/visual-signature.md` — the locked constants and why each was
  chosen. Load when the user asks why something looks the way it does, or
  when discussing rebranding.
- `reference/text-rephrase-recipes.md` — the rephrase patterns. Load at
  Step 3.
- `reference/red-word-recipes.md` — accent placement rules. Load at
  Step 4.
- `reference/icon-picking.md` — Lucide lookup + hand-coded fallback. Load
  at Step 5.
- `reference/iteration-recipes.md` — feedback interpretation. Load at
  Step 8 (every iteration).

## Things this skill does NOT do

- Generate the script. That's the `script-writer` skill (this runs after).
- Pick a winner. The user picks; YouTube measures.
- Upload to YouTube. The user does the upload.
- Render thumbnails for non-hyper-frames content. This skill assumes a
  `videos/<slug>-<date>/` folder structure.
```

---

## Task 17: End-to-end smoke test

**Files:**
- No new files. Verify against the existing `videos/why-text-is-hard-2026-05-07/`.

This task verifies the whole pipeline — skill → templates → renderer → PNG — works end-to-end against a real video folder.

- [ ] **Step 1: Confirm the test video folder has what the skill needs**

```bash
ls /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/videos/why-text-is-hard-2026-05-07/ | head
```

Expected: `outline.md` (or you'll need to create one), `script.md` already present.

If `outline.md` is missing, the skill will ask for the title — that's fine; you can pass the title `Why is rendering text so complicated?` when asked.

- [ ] **Step 2: Invoke the skill from the repo root**

In a Claude conversation, from `/Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames`:

> "Generate thumbnail variants for `videos/why-text-is-hard-2026-05-07/`."

Expected behavior:
1. Skill resolves the absolute path `/.../videos/why-text-is-hard-2026-05-07/`.
2. Reads `outline.md` (or asks for title if missing).
3. Generates three variants per the recipes.
4. Picks an icon (likely the hand-coded `Aa` SVG since "text rendering"
   has no Lucide letter-pair).
5. Writes `videos/why-text-is-hard-2026-05-07/thumbnails/round-1/{a,b,c}.html`
   plus `contact-sheet.html`.
6. Prints the `file://` URL of the contact sheet.

- [ ] **Step 3: Open the contact sheet and inspect**

Open the URL in a browser. Verify:
- Background is espresso brown (`#1A1410`), not pure black.
- Text is JetBrains Mono ExtraBold in warm off-white (`#F5E6D3`).
- Accent words are amber (`#FFB627`), not red.
- Each variant fits 3 rows, no wrapping.
- Icon shows on the right, with one accent-color detail.
- The grid-size simulation (~210 px) is still legible.

- [ ] **Step 4: Drive one iteration**

Tell the skill: "Make B punchier and use a different accent on A."

Expected: a new `round-2/` folder appears with the requested changes.
Open `round-2/contact-sheet.html` to verify.

- [ ] **Step 5: Approve and export**

Tell the skill: "Ship it."

Expected: the renderer runs (Chromium briefly launches), and three PNGs
appear at `videos/why-text-is-hard-2026-05-07/thumbnail-{a,b,c}.png`.
Open each in Preview. Confirm:
- Each is exactly 1280×720 px (right-click → Get Info on Mac).
- Typography matches the contact-sheet preview (JetBrains Mono actually
  loaded, not a fallback). If a thumbnail shows a different font, the
  `document.fonts.ready` await isn't catching the Google Fonts request —
  check `tools/thumbnail-render/src/render.mjs`.
- Colors are correct.

- [ ] **Step 6: Tear down test artifacts (optional)**

If you want to leave the video folder pristine for a real first run:

```bash
rm -rf /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/videos/why-text-is-hard-2026-05-07/thumbnails && \
  rm -f /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/videos/why-text-is-hard-2026-05-07/thumbnail-*.png
```

---

## Self-review notes

The plan covers every section of the spec:

| Spec section | Covered by |
|---|---|
| §1 Purpose | Goal in plan header |
| §2 Scope (in / out) | Tasks 8–17 (in scope); explicitly deferred items called out in pre-flight |
| §3 Inputs / outputs / resolution | Task 16 SKILL.md Steps 1–2 + Step 6 |
| §4 Visual signature | Task 8 (CSS) + Task 11 (visual-signature.md) |
| §5 Architecture (split) | Tasks 1–7 (tool) vs Tasks 8–16 (skill) |
| §6 File layout | "File structure" section + per-task file paths |
| §7 Workflow steps 1–9 | Task 16 SKILL.md mirrors all 9 steps |
| §8 Tool CLI surface | Task 5 (CLI), Task 7 (README) |
| §9 Reference files | Tasks 11–15 |
| §10 Hard rules | Task 16 SKILL.md "Hard rules" section |
| §11 Pre-flight check | Task 16 SKILL.md "Pre-flight check" section |
| §12 Footguns | Task 4 (`document.fonts.ready`); Task 1 (Lucide pin); Task 12 (width-fit constraint); Task 16 (max+1 round number) |
| §13 Out of scope | Pre-flight notes; serve.mjs explicitly deferred |
| §14 Implementation order | Plan tasks follow this exact order |

No placeholders. No "TBD" or "implement appropriate X" steps. Every code
block contains the actual content the engineer needs.
