# IRL Coder Channel Banner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the `branding/banner/banner.svg` source and a 2048×1152 PNG suitable for upload as the IRL Coder YouTube channel banner.

**Architecture:** A canonical 2048×1152 SVG carries the espresso backdrop, the cream waterline (broken by the type), the ALL-CAPS manifesto in JetBrains Mono ExtraBold, the cream-stroke iceberg "tip," and 16 amber Lucide icons hand-placed in the lower half. The existing `tools/branding-render/` Playwright renderer is generalized to support rectangular dimensions (it currently only does squares) and to wait for web fonts before screenshotting. A new build script renders the single banner PNG.

**Tech Stack:** Node.js ≥20, Playwright (chromium), `node:test`. JetBrains Mono ExtraBold via Google Fonts CSS @import (matching the thumbnail-creator pattern). No new top-level dependencies.

**Spec:** `docs/superpowers/specs/2026-05-09-irl-coder-channel-banner-design.md`

---

## File Structure

**New files:**
- `branding/banner/banner.svg` — canonical 2048×1152 source
- `branding/banner/banner-2048x1152.png` — rasterized output, committed
- `branding/banner/README.md` — what each file is for, how to rebuild
- `tools/branding-render/scripts/build-banner-png.mjs` — single-file build helper

**Modified files:**
- `tools/branding-render/src/render.mjs` — accept rectangular dims; wait for fonts; load JetBrains Mono in the wrapper HTML
- `tools/branding-render/bin/render.mjs` — add `--width`/`--height` flags alongside `--size`
- `tools/branding-render/tests/render.test.mjs` — add coverage for rectangular dims
- `tools/branding-render/package.json` — add `build:banner` script

**Why this layout:** keeps banner artifacts beside the existing logo artifacts (`branding/logo/` ↔ `branding/banner/`). Renderer changes stay in one tool with backwards-compatible API for the logo callers.

---

## Task 1: Generalize the renderer to rectangular dimensions and font-aware screenshots

**Files:**
- Modify: `tools/branding-render/src/render.mjs`
- Modify: `tools/branding-render/tests/render.test.mjs`

The `renderSvgToPng(svgPath, outPng, size)` function currently only renders square outputs and doesn't wait for fonts. We extend the third parameter to accept `{ width, height }` for rectangles, keep the existing `number → square` shorthand for backward compatibility, load JetBrains Mono in the wrapper HTML, and wait for `document.fonts.ready` before screenshotting.

- [ ] **Step 1: Add the failing rectangular-dims tests**

Edit `tools/branding-render/tests/render.test.mjs`. Append these tests after the existing three (don't replace them — the existing square tests must continue to pass):

```javascript
test('renderSvgToPng accepts {width, height} for rectangular output', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'br-'));
  const out = path.join(dir, 'rect.png');
  try {
    await renderSvgToPng(fixture, out, { width: 256, height: 128 });
    assert.ok(existsSync(out), 'output PNG should exist');
    const dims = readPngDims(out);
    assert.equal(dims.width, 256);
    assert.equal(dims.height, 128);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('renderSvgToPng rejects {width, height} with non-positive values', async () => {
  await assert.rejects(
    () => renderSvgToPng(fixture, '/tmp/x.png', { width: 0, height: 100 }),
    /positive integer/i,
  );
  await assert.rejects(
    () => renderSvgToPng(fixture, '/tmp/x.png', { width: 100, height: -5 }),
    /positive integer/i,
  );
});

test('renderSvgToPng rejects unrecognized dims', async () => {
  await assert.rejects(
    () => renderSvgToPng(fixture, '/tmp/x.png', 'big'),
    /positive integer or \{width, height\}/i,
  );
});
```

- [ ] **Step 2: Run tests — expect 3 new failures**

Run:

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/branding-render && npm test 2>&1 | tail -20
```

Expected: 3 original tests pass; 3 new tests fail (the function rejects object form with the existing `positive integer` error).

- [ ] **Step 3: Replace `renderSvgToPng` with the generalized version**

Replace the entire contents of `tools/branding-render/src/render.mjs` with:

```javascript
import { chromium } from 'playwright';
import { existsSync, readFileSync } from 'node:fs';

/**
 * Render an SVG file to a PNG at the given pixel dimensions.
 *
 * The SVG is inlined into a minimal HTML wrapper that loads JetBrains Mono
 * ExtraBold via Google Fonts so any text in the SVG renders in the channel
 * font. The browser scales the SVG to fill the viewport, the renderer waits
 * for fonts to load, and the screenshot is taken with transparent background
 * so anything outside an SVG-drawn shape stays clear.
 *
 * @param {string} svgPath - absolute or relative path to the source SVG
 * @param {string} outPngPath - absolute or relative path for the output PNG
 * @param {number | { width: number, height: number }} dims
 *   - A positive integer is treated as a square size.
 *   - `{ width, height }` produces a rectangular output.
 * @returns {Promise<void>}
 */
export async function renderSvgToPng(svgPath, outPngPath, dims) {
  if (!existsSync(svgPath)) {
    throw new Error(`Input SVG not found: ${svgPath} (ENOENT)`);
  }

  let width, height;
  if (typeof dims === 'number') {
    if (!Number.isInteger(dims) || dims <= 0) {
      throw new Error(`size must be a positive integer (got ${dims})`);
    }
    width = height = dims;
  } else if (dims && typeof dims === 'object' && 'width' in dims && 'height' in dims) {
    ({ width, height } = dims);
    if (!Number.isInteger(width) || width <= 0 || !Number.isInteger(height) || height <= 0) {
      throw new Error(`width and height must be positive integers (got width=${width}, height=${height})`);
    }
  } else {
    throw new Error(`dims must be a positive integer or {width, height} object (got ${typeof dims})`);
  }

  const svgContent = readFileSync(svgPath, 'utf8');
  const html = `<!doctype html><html><head><meta charset="utf-8">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@800&display=block" rel="stylesheet">
    <style>
      html, body { margin: 0; padding: 0; background: transparent; }
      body > svg { display: block; width: 100vw; height: 100vh; }
    </style></head><body>${svgContent}</body></html>`;

  const browser = await chromium.launch();
  try {
    const context = await browser.newContext({
      viewport: { width, height },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    await page.setContent(html, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({
      path: outPngPath,
      type: 'png',
      omitBackground: true,
      clip: { x: 0, y: 0, width, height },
    });
  } finally {
    await browser.close();
  }
}
```

- [ ] **Step 4: Run tests — expect all 6 to pass**

Run:

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/branding-render && npm test 2>&1 | tail -15
```

Expected: 6 tests pass. The first run includes a Google Fonts fetch for the font, so the rectangular test may take ~2 s.

- [ ] **Step 5: Smoke-test that the existing logo build still works**

Run:

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/branding-render && npm run build:logo 2>&1 | tail -10
```

Expected: 5 PNGs render successfully. The logo's git status should be clean afterward — re-rendered output matches what's already committed.

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames && git status branding/logo/
```

Expected: `nothing to commit` (or only timestamp-equivalent diffs, which is fine — re-running the build doesn't need to produce a new commit).

- [ ] **Step 6: Commit**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames && \
git add tools/branding-render/src/render.mjs tools/branding-render/tests/render.test.mjs && \
git commit -m "feat(branding-render): rectangular dims + font-aware rendering"
```

---

## Task 2: Update the CLI to accept rectangular flags

**Files:**
- Modify: `tools/branding-render/bin/render.mjs`

The CLI currently only supports `--size N`. Add `--width N --height M` to call the rectangular form. Keep `--size` for backwards compatibility.

- [ ] **Step 1: Replace the CLI**

Replace the entire contents of `tools/branding-render/bin/render.mjs` with:

```javascript
#!/usr/bin/env node
import path from 'node:path';
import { renderSvgToPng } from '../src/render.mjs';

function usage() {
  console.error(`Usage:
  render.mjs <svg-path> --out <png-path> --size <pixels>
  render.mjs <svg-path> --out <png-path> --width <px> --height <px>

Renders an SVG file to a PNG at the requested size with transparent
background. --size is shorthand for a square output. Used by the build
scripts under scripts/ to produce branding artifacts.`);
  process.exit(2);
}

function parseArgs(argv) {
  const args = { positional: [], flags: {} };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--out')          { args.flags.out    = argv[++i]; }
    else if (a === '--size')    { args.flags.size   = argv[++i]; }
    else if (a === '--width')   { args.flags.width  = argv[++i]; }
    else if (a === '--height')  { args.flags.height = argv[++i]; }
    else if (a.startsWith('--')) { console.error(`Unknown flag: ${a}`); usage(); }
    else                        { args.positional.push(a); }
  }
  return args;
}

const args = parseArgs(process.argv.slice(2));
if (args.positional.length !== 1 || !args.flags.out) usage();

let dims;
if (args.flags.size) {
  dims = Number.parseInt(args.flags.size, 10);
} else if (args.flags.width && args.flags.height) {
  dims = {
    width: Number.parseInt(args.flags.width, 10),
    height: Number.parseInt(args.flags.height, 10),
  };
} else {
  usage();
}

const svgPath = path.resolve(args.positional[0]);
const outPath = path.resolve(args.flags.out);

try {
  const dimsLabel = typeof dims === 'number' ? `${dims}x${dims}` : `${dims.width}x${dims.height}`;
  console.log(`render: ${svgPath} -> ${outPath} (${dimsLabel})`);
  await renderSvgToPng(svgPath, outPath, dims);
  console.log(`done: ${outPath}`);
} catch (err) {
  console.error(`error: ${err.message}`);
  process.exit(1);
}
```

- [ ] **Step 2: Smoke-test rectangular CLI invocation**

Run from the repo root:

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames && \
node tools/branding-render/bin/render.mjs tools/branding-render/tests/fixtures/square.svg --out /tmp/rect-cli-test.png --width 320 --height 160
```

Expected output:
```
render: <abs>/tools/branding-render/tests/fixtures/square.svg -> /tmp/rect-cli-test.png (320x160)
done: /tmp/rect-cli-test.png
```

Then verify dimensions:

```bash
node -e 'const fs=require("fs"); const b=fs.readFileSync("/tmp/rect-cli-test.png"); console.log(b.readUInt32BE(16)+"x"+b.readUInt32BE(20))'
```

Expected: `320x160`.

- [ ] **Step 3: Clean up smoke-test artifact and commit**

```bash
rm /tmp/rect-cli-test.png && \
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames && \
git add tools/branding-render/bin/render.mjs && \
git commit -m "feat(branding-render): CLI --width/--height flags"
```

---

## Task 3: Author the canonical banner SVG

**Files:**
- Create: `branding/banner/banner.svg`

This task produces static content; no tests. It's the longest task because the SVG carries the full composition: backdrop, two waterline segments, manifesto, tip icon, and 16 hand-placed submerged icons.

- [ ] **Step 1: Create the directory**

```bash
mkdir -p /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/branding/banner
```

- [ ] **Step 2: Write the SVG**

Write `branding/banner/banner.svg` with this exact content:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2048 1152" width="2048" height="1152">
  <defs>
    <symbol id="ic-type" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16M4 7V5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v2M9 20h6"/></symbol>
    <symbol id="ic-globe" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20a14.5 14.5 0 0 0 0-20M2 12h20"/></g></symbol>
    <symbol id="ic-key" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M2.586 17.414A2 2 0 0 0 2 18.828V21a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h1a1 1 0 0 0 1-1v-1a1 1 0 0 1 1-1h.172a2 2 0 0 0 1.414-.586l.814-.814a6.5 6.5 0 1 0-4-4z"/><circle cx="16.5" cy="7.5" r=".5" fill="currentColor"/></g></symbol>
    <symbol id="ic-database" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14a9 3 0 0 0 18 0V5"/><path d="M3 12a9 3 0 0 0 18 0"/></g></symbol>
    <symbol id="ic-cpu" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M12 20v2m0-20v2m5 16v2m0-20v2M2 12h2m-2 5h2M2 7h2m16 5h2m-2 5h2M20 7h2M7 20v2M7 2v2"/><rect width="16" height="16" x="4" y="4" rx="2"/><rect width="6" height="6" x="9" y="9" rx="1"/></g></symbol>
    <symbol id="ic-image" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15l-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></g></symbol>
    <symbol id="ic-code" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m16 18l6-6l-6-6M8 6l-6 6l6 6"/></symbol>
    <symbol id="ic-cookie" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 2a10 10 0 1 0 10 10a4 4 0 0 1-5-5a4 4 0 0 1-5-5M8.5 8.5v.01M16 15.5v.01M12 12v.01M11 17v.01M7 14v.01"/></symbol>
    <symbol id="ic-terminal" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19h8M4 17l6-6l-6-6"/></symbol>
    <symbol id="ic-wifi" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 20h.01M2 8.82a15 15 0 0 1 20 0M5 12.859a10 10 0 0 1 14 0m-10.5 3.57a5 5 0 0 1 7 0"/></symbol>
    <symbol id="ic-hash" viewBox="0 0 24 24"><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 9h16M4 15h16M10 3L8 21m8-18l-2 18"/></symbol>
    <symbol id="ic-layers" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z"/><path d="M2 12a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 12"/><path d="M2 17a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 17"/></g></symbol>
    <symbol id="ic-git" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M15 6a9 9 0 0 0-9 9V3"/><circle cx="18" cy="6" r="3"/><circle cx="6" cy="18" r="3"/></g></symbol>
    <symbol id="ic-lock" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></g></symbol>
    <symbol id="ic-cog" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><path d="M11 10.27L7 3.34m4 10.39l-4 6.93M12 22v-2m0-18v2m2 8h8m-5 8.66l-1-1.73m1-15.59l-1 1.73M2 12h2m16.66 5l-1.73-1m1.73-9l-1.73 1m-15.59-1l1.73 1m-1.73 9l1.73-1"/><path d="M14 12a2 2 0 1 1-4 0a2 2 0 0 1 4 0"/><circle cx="12" cy="12" r="8"/></g></symbol>
    <symbol id="ic-server" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"><rect width="20" height="8" x="2" y="2" rx="2" ry="2"/><rect width="20" height="8" x="2" y="14" rx="2" ry="2"/><line x1="6" x2="6.01" y1="6" y2="6"/><line x1="6" x2="6.01" y1="18" y2="18"/></g></symbol>
    <symbol id="ic-tip-iceberg" viewBox="2 2 20 20">
      <path d="m19 10l-2 9l-4 3l-3-5l-3-1l-2-6l2-5l3-2l3 3l4 1z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </symbol>
  </defs>

  <!-- Espresso backdrop, full canvas -->
  <rect x="0" y="0" width="2048" height="1152" fill="#1A1410"/>

  <!-- Waterline: two cream segments, broken by the type. Type column spans
       roughly x=412 to x=1636 at 100px JetBrains Mono ExtraBold. Add 32px
       padding either side: line stops at x=380 and resumes at x=1668. -->
  <line x1="0" y1="576" x2="380" y2="576" stroke="#F5E6D3" stroke-width="4" stroke-linecap="round"/>
  <line x1="1668" y1="576" x2="2048" y2="576" stroke="#F5E6D3" stroke-width="4" stroke-linecap="round"/>

  <!-- Tip-of-iceberg icon (cream stroke, no waterline inside): centered at
       (1024, 416) so its bottom edge sits 80px above the waterline. -->
  <use href="#ic-tip-iceberg" x="944" y="336" width="160" height="160" color="#F5E6D3"/>

  <!-- Manifesto: JetBrains Mono ExtraBold 100px, cream, centered, sitting on
       the waterline. dominant-baseline=middle places the visual center on y=576. -->
  <text x="1024" y="576"
        text-anchor="middle"
        dominant-baseline="middle"
        font-family="'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace"
        font-weight="800"
        font-size="100"
        letter-spacing="-2"
        fill="#F5E6D3">BELOW THE WATERLINE.</text>

  <!-- Submerged territory: 16 amber Lucide icons.
       Row A (phone-visible, inside safe-area lower half y=676..745):
       compact icons aligned at cy=710 ±4 with sizes 56-62 to fit the
       69px-tall strip without entering the clear zone above (y=576..676)
       or extending past the safe-area bottom (y=745).
       Rows B & C (desktop/TV only, below the safe area): larger icons
       with looser placement. -->

  <!-- Row A — 7 icons, phone-visible. -->
  <use href="#ic-type"     x="411" y="681" width="58" height="58" color="#FFB627" opacity="0.40"/>
  <use href="#ic-globe"    x="562" y="684" width="56" height="56" color="#FFB627" opacity="0.32"/>
  <use href="#ic-database" x="729" y="677" width="62" height="62" color="#FFB627" opacity="0.42"/>
  <use href="#ic-cpu"      x="911" y="683" width="58" height="58" color="#FFB627" opacity="0.35"/>
  <use href="#ic-image"    x="1079" y="679" width="62" height="62" color="#FFB627" opacity="0.40"/>
  <use href="#ic-wifi"     x="1252" y="680" width="56" height="56" color="#FFB627" opacity="0.30"/>
  <use href="#ic-hash"     x="1421" y="683" width="58" height="58" color="#FFB627" opacity="0.34"/>

  <!-- Row B — 7 icons, desktop/TV only, mid-depth. -->
  <use href="#ic-key"       x="155" y="795" width="110" height="110" color="#FFB627" opacity="0.45"/>
  <use href="#ic-code"      x="390" y="840" width="80" height="80" color="#FFB627" opacity="0.30"/>
  <use href="#ic-cookie"    x="580" y="810" width="120" height="120" color="#FFB627" opacity="0.40"/>
  <use href="#ic-terminal"  x="825" y="875" width="90" height="90" color="#FFB627" opacity="0.35"/>
  <use href="#ic-layers"    x="1035" y="805" width="130" height="130" color="#FFB627" opacity="0.45"/>
  <use href="#ic-git"       x="1296" y="856" width="88" height="88" color="#FFB627" opacity="0.32"/>
  <use href="#ic-lock"      x="1530" y="820" width="100" height="100" color="#FFB627" opacity="0.40"/>

  <!-- Row C — 2 icons, deepest, right-side desktop/TV only. -->
  <use href="#ic-cog"    x="1745" y="885" width="110" height="110" color="#FFB627" opacity="0.32"/>
  <use href="#ic-server" x="1860" y="970" width="80" height="80" color="#FFB627" opacity="0.28"/>
</svg>
```

- [ ] **Step 3: Visually verify the SVG**

```bash
open /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/branding/banner/banner.svg
```

Expected: Espresso banner. Cream waterline runs across the canvas, broken by the centered text "BELOW THE WATERLINE." in monospace. A cream iceberg silhouette sits above the line, centered. Below the line, amber Lucide icons in three rough horizontal bands — compact icons just below the type (visible on the phone-safe strip), larger icons across the bottom half. Total 16 distinct icons.

- [ ] **Step 4: Commit the SVG**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames && \
git add branding/banner/banner.svg && \
git commit -m "feat(branding): add canonical IRL Coder channel banner SVG"
```

---

## Task 4: Add the build script

**Files:**
- Create: `tools/branding-render/scripts/build-banner-png.mjs`
- Modify: `tools/branding-render/package.json`

- [ ] **Step 1: Write the build script**

Write `tools/branding-render/scripts/build-banner-png.mjs`:

```javascript
#!/usr/bin/env node
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderSvgToPng } from '../src/render.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..', '..', '..');
const svgPath = path.join(repoRoot, 'branding', 'banner', 'banner.svg');
const outPath = path.join(repoRoot, 'branding', 'banner', 'banner-2048x1152.png');

console.log(`render: ${svgPath} -> ${outPath} (2048x1152)`);
await renderSvgToPng(svgPath, outPath, { width: 2048, height: 1152 });
console.log(`done: ${outPath}`);
```

- [ ] **Step 2: Add the npm script**

Edit `tools/branding-render/package.json`. Find the `"scripts"` block and add `build:banner` next to `build:logo`:

```json
{
  "name": "@hyper-frames/branding-render",
  "version": "0.1.0",
  "description": "Render branding/logo/iceberg.svg to square PNGs at YouTube avatar sizes via Playwright. Single channel-level tool; visual signature lives in the spec, not here.",
  "type": "module",
  "private": true,
  "engines": { "node": ">=20" },
  "scripts": {
    "test": "node --test tests/*.test.mjs",
    "build:logo": "node scripts/build-logo-pngs.mjs",
    "build:banner": "node scripts/build-banner-png.mjs"
  },
  "dependencies": {
    "playwright": "1.49.1"
  }
}
```

- [ ] **Step 3: Commit the build script and package.json change**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames && \
git add tools/branding-render/scripts/build-banner-png.mjs tools/branding-render/package.json && \
git commit -m "feat(branding-render): build:banner script"
```

---

## Task 5: Render the banner PNG

**Files:**
- Create (rendered): `branding/banner/banner-2048x1152.png`

- [ ] **Step 1: Run the build**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/branding-render && npm run build:banner
```

Expected: one log line `render: <abs>/branding/banner/banner.svg -> <abs>/branding/banner/banner-2048x1152.png (2048x1152)` followed by `done: <abs>...`. Total runtime ~3-6 s (one chromium launch, one font load, one screenshot).

- [ ] **Step 2: Verify the PNG dimensions**

```bash
node -e 'const fs=require("fs"); const b=fs.readFileSync("/Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/branding/banner/banner-2048x1152.png"); console.log(b.readUInt32BE(16)+"x"+b.readUInt32BE(20))'
```

Expected: `2048x1152`.

- [ ] **Step 3: Visually verify the PNG**

```bash
open /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/branding/banner/banner-2048x1152.png
```

Expected: matches the SVG visual — espresso banner, cream waterline broken by the centered manifesto in JetBrains Mono ExtraBold, cream iceberg silhouette above the line, amber Lucide icons scattered below it. The text should render in JetBrains Mono ExtraBold (not the system fallback monospace) — if it looks like generic Menlo or Courier, fonts didn't load and the renderer's font wait failed.

- [ ] **Step 4: Commit the PNG**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames && \
git add branding/banner/banner-2048x1152.png && \
git commit -m "feat(branding): rasterized 2048x1152 channel banner PNG"
```

---

## Task 6: Document the artifacts

**Files:**
- Create: `branding/banner/README.md`

- [ ] **Step 1: Write the README**

Write `branding/banner/README.md`:

````markdown
# IRL Coder channel banner

Channel-level banner asset. Pairs with the avatar in `branding/logo/`. Per-video assets live under `videos/<slug>-<date>/`; this directory is for the YouTube channel itself.

## Files

| File                       | Use                                              |
|----------------------------|--------------------------------------------------|
| `banner.svg`               | Canonical source. Edit this; the PNG regenerates. |
| `banner-2048x1152.png`     | Upload this to YouTube as the channel banner.     |

YouTube downscales the 2048×1152 source for desktop, TV, and phone surfaces automatically — only one PNG size is needed for upload.

## Design

Manifesto-style banner that enacts the channel's iceberg metaphor: the type **is** the waterline. `BELOW THE WATERLINE.` runs across the horizontal centerline of the banner in JetBrains Mono ExtraBold (100 px, cream `#F5E6D3`), with a thin cream waterline extending edge-to-edge on either side of the text. A cream-stroke iceberg silhouette sits above the waterline as the visible "tip"; below it, 16 amber `#FFB627` Lucide line icons are scattered in three loose bands — compact icons inside the 1235×338 phone-safe area (visible on phones), larger icons across the lower half of the canvas (visible only on desktop and TV). The full icon scatter forms the "submerged territory" the manifesto names.

Full design rationale: `docs/superpowers/specs/2026-05-09-irl-coder-channel-banner-design.md`.

## Rebuild

If `banner.svg` changes, regenerate the PNG with:

```bash
cd tools/branding-render && npm run build:banner
```

This rasterizes `branding/banner/banner.svg` to `banner-2048x1152.png` next to it. Then commit the SVG and the regenerated PNG together.

## Don't

- Don't edit the PNG directly. It regenerates from the SVG.
- Don't make the banner promote a specific video. The manifesto is the channel's permanent stance; per-video promo would force a redesign on every upload.
- Don't put critical content outside the 1235×338 centered safe area. Phones crop to the safe area; anything outside it only shows on desktop and TV.
- Don't change one color or the manifesto in isolation. The visual signature is shared with the avatar (`branding/logo/`); rebranding is a separate exercise.
````

- [ ] **Step 2: Commit**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames && \
git add branding/banner/README.md && \
git commit -m "docs(branding): document banner files and rebuild step"
```

---

## Final verification

- [ ] **Step 1: Confirm clean working tree (modulo pre-existing WIP)**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames && git status
```

Expected: only the 3 pre-existing modifications from earlier in the session (`kanban.html`, `tools/thumbnail-render/icons/iconify-cache.json`, `.claude/skills/script-writer/reference/tts-gotchas.md`). All banner work is committed.

- [ ] **Step 2: Confirm the file inventory**

```bash
ls /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/branding/banner/
```

Expected: `README.md  banner-2048x1152.png  banner.svg`.

- [ ] **Step 3: Confirm tests pass**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/branding-render && npm test
```

Expected: 6 tests pass (3 original + 3 new for rectangular dims).

- [ ] **Step 4: Hand the user the upload path**

Tell the user:

> The 2048×1152 PNG ready for YouTube upload is at `branding/banner/banner-2048x1152.png`. Drag it into YouTube Studio → Customization → Branding → Banner image. Use the position/scale tool in YouTube to confirm the 1235×338 safe area shows the manifesto and tip icon clearly on phone preview.
