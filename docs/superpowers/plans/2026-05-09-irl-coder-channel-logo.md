# IRL Coder Channel Logo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the `branding/logo/iceberg.svg` source plus rasterized PNGs at 800/176/96/48/24 px so the channel can replace its current pixel-art YouTube avatar.

**Architecture:** A canonical 800×800 SVG (espresso disk + amber-stroke iceberg + cream waterline + translucent amber underwater fill) is rasterized to five square PNG sizes by a new tiny `tools/branding-render/` Playwright-based renderer. The renderer takes an SVG path and a size, inlines the SVG into a wrapper HTML page so the browser scales it to viewport, and screenshots with transparent background. A multi-size build script renders all five sizes in one run.

**Tech Stack:** Node.js ≥20, Playwright (chromium), pure-stdlib `node:test` for tests. No new top-level dependencies — Playwright is already pinned in the sibling `tools/thumbnail-render/` package.

**Spec:** `docs/superpowers/specs/2026-05-09-irl-coder-channel-logo-design.md`

---

## File Structure

**New files:**
- `branding/logo/iceberg.svg` — canonical source, 800×800 viewBox, transparent corners
- `branding/logo/iceberg-{800,176,96,48,24}.png` — rasterized outputs, committed
- `branding/logo/README.md` — what each file is for, how to rebuild
- `tools/branding-render/package.json` — tool manifest (name, deps, scripts)
- `tools/branding-render/src/render.mjs` — `renderSvgToPng(svgPath, outPng, size)` core
- `tools/branding-render/bin/render.mjs` — CLI binary
- `tools/branding-render/scripts/build-logo-pngs.mjs` — multi-size build helper
- `tools/branding-render/tests/render.test.mjs` — `node:test` suite
- `tools/branding-render/tests/fixtures/square.svg` — minimal test fixture (a red square)
- `tools/branding-render/.gitignore` — ignores `node_modules/`

**Modified files:** none.

**Why this layout:** mirrors the established `tools/thumbnail-render/` shape (`bin/`, `src/`, `scripts/`, `tests/fixtures/`) so anyone who already knows the thumbnail tool can read this one without ramp-up. Keeps logo concerns out of the thumbnail tool, which is intentionally brand-agnostic per its own `package.json` description.

---

## Task 1: Author the canonical SVG

**Files:**
- Create: `branding/logo/iceberg.svg`

This task produces static content; no tests.

- [ ] **Step 1: Create the directory and write the SVG**

```bash
mkdir -p branding/logo
```

Write `branding/logo/iceberg.svg` with this exact content:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="800" height="800">
  <!-- Espresso disk backdrop. Corners outside the disk stay transparent. -->
  <circle cx="400" cy="400" r="400" fill="#1A1410"/>

  <!-- Iceberg drawn in its native 24-unit space, rendered into a 560x560
       inner area centered on the disk (70% of the circle's diameter). -->
  <svg x="120" y="120" width="560" height="560" viewBox="2 2 20 20">
    <defs>
      <clipPath id="below-water">
        <rect x="0" y="10" width="24" height="14"/>
      </clipPath>
    </defs>

    <!-- Submerged mass: translucent amber, clipped below the waterline. -->
    <path
      d="m19 10l-2 9l-4 3l-3-5l-3-1l-2-6l2-5l3-2l3 3l4 1z"
      fill="#FFB627"
      fill-opacity="0.35"
      stroke="none"
      clip-path="url(#below-water)"/>

    <!-- Iceberg outline: amber stroke around the full body. -->
    <path
      d="m19 10l-2 9l-4 3l-3-5l-3-1l-2-6l2-5l3-2l3 3l4 1z"
      fill="none"
      stroke="#FFB627"
      stroke-width="1.5"
      stroke-linecap="round"
      stroke-linejoin="round"/>

    <!-- Waterline: cream stroke. The only cream element in the mark. -->
    <path
      d="M3 10h18"
      fill="none"
      stroke="#F5E6D3"
      stroke-width="1.5"
      stroke-linecap="round"
      stroke-linejoin="round"/>
  </svg>
</svg>
```

- [ ] **Step 2: Visually verify the SVG opens correctly**

Run: `open branding/logo/iceberg.svg`

Expected: Espresso-brown circle with an amber iceberg silhouette inside; the underwater portion shows a translucent amber wash; a cream horizontal line marks the waterline. The four corners of the SVG square are transparent (no espresso square — only a disk).

- [ ] **Step 3: Commit the SVG only**

```bash
git add branding/logo/iceberg.svg
git commit -m "feat(branding): add canonical IRL Coder logo SVG"
```

---

## Task 2: Scaffold the branding-render tool

**Files:**
- Create: `tools/branding-render/package.json`
- Create: `tools/branding-render/.gitignore`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p tools/branding-render/{bin,src,scripts,tests/fixtures}
```

- [ ] **Step 2: Write `tools/branding-render/package.json`**

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
    "build:logo": "node scripts/build-logo-pngs.mjs"
  },
  "dependencies": {
    "playwright": "1.49.1"
  }
}
```

- [ ] **Step 3: Write `tools/branding-render/.gitignore`**

```
node_modules/
```

- [ ] **Step 4: Install dependencies**

```bash
cd tools/branding-render && npm install
```

Expected: `playwright@1.49.1` installs without errors. The Chromium browser is reused from the sibling `tools/thumbnail-render` install if already present; otherwise Playwright will download it on first `chromium.launch()` call.

- [ ] **Step 5: Commit the scaffold**

```bash
git add tools/branding-render/package.json tools/branding-render/.gitignore tools/branding-render/package-lock.json
git commit -m "feat(branding-render): scaffold tool package"
```

---

## Task 3: TDD `renderSvgToPng`

**Files:**
- Create: `tools/branding-render/tests/fixtures/square.svg`
- Create: `tools/branding-render/tests/render.test.mjs`
- Create: `tools/branding-render/src/render.mjs`

- [ ] **Step 1: Write the test fixture (a red 100×100 SVG)**

Write `tools/branding-render/tests/fixtures/square.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
  <rect x="0" y="0" width="100" height="100" fill="#ff0000"/>
</svg>
```

- [ ] **Step 2: Write the failing test**

Write `tools/branding-render/tests/render.test.mjs`:

```javascript
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, existsSync, statSync, rmSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderSvgToPng } from '../src/render.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const fixture = path.join(__dirname, 'fixtures', 'square.svg');

function readPngDims(pngPath) {
  const buf = readFileSync(pngPath);
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}

test('renderSvgToPng writes a PNG of the requested size', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'br-'));
  const out = path.join(dir, 'out.png');
  try {
    await renderSvgToPng(fixture, out, 96);
    assert.ok(existsSync(out), 'output PNG should exist');
    assert.ok(statSync(out).size > 100, 'output PNG should be non-empty');
    const dims = readPngDims(out);
    assert.equal(dims.width, 96);
    assert.equal(dims.height, 96);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('renderSvgToPng rejects a missing input', async () => {
  await assert.rejects(
    () => renderSvgToPng('/no/such/file.svg', '/tmp/x.png', 96),
    /not found/i,
  );
});

test('renderSvgToPng rejects a non-positive size', async () => {
  await assert.rejects(
    () => renderSvgToPng(fixture, '/tmp/x.png', 0),
    /positive integer/i,
  );
});
```

- [ ] **Step 3: Run the test — expect failure**

Run: `cd tools/branding-render && npm test`

Expected: All three tests FAIL with `Cannot find module '../src/render.mjs'` or similar.

- [ ] **Step 4: Implement `renderSvgToPng`**

Write `tools/branding-render/src/render.mjs`:

```javascript
import { chromium } from 'playwright';
import { existsSync, readFileSync } from 'node:fs';

/**
 * Render an SVG file to a square PNG at the given pixel size.
 *
 * The SVG is inlined into a minimal HTML wrapper so the browser scales it
 * to fill a `size`×`size` viewport; the screenshot is then taken with
 * transparent background so corners outside any disk in the SVG stay clear.
 *
 * @param {string} svgPath - absolute or relative path to the source SVG
 * @param {string} outPngPath - absolute or relative path for the output PNG
 * @param {number} size - target square size in pixels (positive integer)
 * @returns {Promise<void>}
 */
export async function renderSvgToPng(svgPath, outPngPath, size) {
  if (!existsSync(svgPath)) {
    throw new Error(`Input SVG not found: ${svgPath} (ENOENT)`);
  }
  if (!Number.isInteger(size) || size <= 0) {
    throw new Error(`size must be a positive integer (got ${size})`);
  }

  const svgContent = readFileSync(svgPath, 'utf8');
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
    html, body { margin: 0; padding: 0; background: transparent; }
    body > svg { display: block; width: 100vw; height: 100vh; }
  </style></head><body>${svgContent}</body></html>`;

  const browser = await chromium.launch();
  try {
    const context = await browser.newContext({
      viewport: { width: size, height: size },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    await page.setContent(html, { waitUntil: 'load' });
    await page.screenshot({
      path: outPngPath,
      type: 'png',
      omitBackground: true,
      clip: { x: 0, y: 0, width: size, height: size },
    });
  } finally {
    await browser.close();
  }
}
```

- [ ] **Step 5: Run the test — expect pass**

Run: `cd tools/branding-render && npm test`

Expected: All three tests PASS. The first test takes 2-5s (browser launch); the failure tests are fast.

- [ ] **Step 6: Commit**

```bash
git add tools/branding-render/src/render.mjs \
        tools/branding-render/tests/render.test.mjs \
        tools/branding-render/tests/fixtures/square.svg
git commit -m "feat(branding-render): renderSvgToPng core + tests"
```

---

## Task 4: CLI binary

**Files:**
- Create: `tools/branding-render/bin/render.mjs`

- [ ] **Step 1: Write the CLI**

Write `tools/branding-render/bin/render.mjs`:

```javascript
#!/usr/bin/env node
import path from 'node:path';
import { renderSvgToPng } from '../src/render.mjs';

function usage() {
  console.error(`Usage:
  render.mjs <svg-path> --out <png-path> --size <pixels>

Renders an SVG file to a square PNG of the requested size with transparent
background. Used by scripts/build-logo-pngs.mjs to produce the avatar PNGs
at every size YouTube uses.`);
  process.exit(2);
}

function parseArgs(argv) {
  const args = { positional: [], flags: {} };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--out')         { args.flags.out  = argv[++i]; }
    else if (a === '--size')   { args.flags.size = argv[++i]; }
    else if (a.startsWith('--')) { console.error(`Unknown flag: ${a}`); usage(); }
    else                       { args.positional.push(a); }
  }
  return args;
}

const args = parseArgs(process.argv.slice(2));
if (args.positional.length !== 1 || !args.flags.out || !args.flags.size) usage();

const size = Number.parseInt(args.flags.size, 10);
const svgPath = path.resolve(args.positional[0]);
const outPath = path.resolve(args.flags.out);

try {
  console.log(`render: ${svgPath} -> ${outPath} (${size}x${size})`);
  await renderSvgToPng(svgPath, outPath, size);
  console.log(`done: ${outPath}`);
} catch (err) {
  console.error(`error: ${err.message}`);
  process.exit(1);
}
```

- [ ] **Step 2: Make it executable**

```bash
chmod +x tools/branding-render/bin/render.mjs
```

- [ ] **Step 3: Smoke-test against the real logo**

```bash
node tools/branding-render/bin/render.mjs branding/logo/iceberg.svg --out /tmp/iceberg-test.png --size 96
```

Expected output:
```
render: <abs>/branding/logo/iceberg.svg -> /tmp/iceberg-test.png (96x96)
done: /tmp/iceberg-test.png
```

Then visually confirm: `open /tmp/iceberg-test.png`. The image should match the brainstorm screen's 96 px feed avatar — espresso disk, amber iceberg with translucent submerged mass, cream waterline.

- [ ] **Step 4: Clean up the smoke-test artifact**

```bash
rm /tmp/iceberg-test.png
```

- [ ] **Step 5: Commit**

```bash
git add tools/branding-render/bin/render.mjs
git commit -m "feat(branding-render): CLI binary"
```

---

## Task 5: Build all five PNGs

**Files:**
- Create: `tools/branding-render/scripts/build-logo-pngs.mjs`

- [ ] **Step 1: Write the build script**

Write `tools/branding-render/scripts/build-logo-pngs.mjs`:

```javascript
#!/usr/bin/env node
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderSvgToPng } from '../src/render.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..', '..', '..');
const svgPath = path.join(repoRoot, 'branding', 'logo', 'iceberg.svg');
const outDir = path.join(repoRoot, 'branding', 'logo');

const SIZES = [800, 176, 96, 48, 24];

for (const size of SIZES) {
  const out = path.join(outDir, `iceberg-${size}.png`);
  console.log(`render: ${svgPath} -> ${out} (${size}x${size})`);
  await renderSvgToPng(svgPath, out, size);
}
console.log(`done: ${SIZES.length} PNGs in ${outDir}`);
```

- [ ] **Step 2: Run the build**

```bash
cd tools/branding-render && npm run build:logo
```

Expected: 5 console lines `render: ... -> iceberg-{800,176,96,48,24}.png` followed by `done: 5 PNGs in <abs>/branding/logo`. Total runtime ~10-20 s (one chromium launch per size; could be optimized later, not now).

- [ ] **Step 3: Visually verify all five PNGs**

```bash
open branding/logo/iceberg-800.png \
     branding/logo/iceberg-176.png \
     branding/logo/iceberg-96.png \
     branding/logo/iceberg-48.png \
     branding/logo/iceberg-24.png
```

Expected: All five PNGs render the espresso disk + amber iceberg correctly. The 24 px image should still be readable as an iceberg silhouette (the silhouette test from the brainstorm). The 800 px image is the YouTube source upload.

- [ ] **Step 4: Commit the build script and PNGs**

```bash
git add tools/branding-render/scripts/build-logo-pngs.mjs \
        branding/logo/iceberg-800.png \
        branding/logo/iceberg-176.png \
        branding/logo/iceberg-96.png \
        branding/logo/iceberg-48.png \
        branding/logo/iceberg-24.png
git commit -m "feat(branding): rasterized iceberg PNGs at 800/176/96/48/24px"
```

---

## Task 6: Document the artifacts

**Files:**
- Create: `branding/logo/README.md`

- [ ] **Step 1: Write the README**

Write `branding/logo/README.md`:

````markdown
# IRL Coder channel logo

Channel-level identity assets. Per-video assets live under `videos/<slug>-<date>/`; this directory is for the YouTube channel itself.

## Files

| File              | Use                                              |
|-------------------|--------------------------------------------------|
| `iceberg.svg`     | Canonical source. Edit this; everything else regenerates. |
| `iceberg-800.png` | Upload this to YouTube as the channel avatar.     |
| `iceberg-176.png` | Channel page header avatar size.                  |
| `iceberg-96.png`  | Feed avatar size.                                 |
| `iceberg-48.png`  | Comment thread avatar size.                       |
| `iceberg-24.png`  | Notification badge avatar size.                   |

The PNGs are committed so README badges, social profiles, and external surfaces can reference them at known sizes without re-rastering.

## Design

Espresso disk (`#1A1410`) with an amber-stroke iceberg (`#FFB627`, stroke-width 1.5 in 24-unit space, rounded joins) and a cream waterline (`#F5E6D3`). The portion of the iceberg below the waterline is filled with translucent amber (`fill-opacity: 0.35`) — the visible submerged mass encodes the channel's "iceberg" narrative metaphor (mundane action revealed as unsuspected depth).

Full design rationale: `docs/superpowers/specs/2026-05-09-irl-coder-channel-logo-design.md`.

## Rebuild

If `iceberg.svg` changes, regenerate all five PNGs with:

```bash
cd tools/branding-render && npm run build:logo
```

This rasterizes `branding/logo/iceberg.svg` to PNGs at 800, 176, 96, 48, and 24 px and writes them next to the SVG. Then commit the SVG and all five regenerated PNGs together.

## Don't

- Don't edit the PNGs directly. They regenerate from the SVG.
- Don't add a wordmark inside the avatar circle. The channel name appears next to the avatar in every YouTube surface that matters; reusing 96 px of brand real estate for redundant text is a waste.
- Don't change one color in isolation. The four constants (espresso, cream, amber, transparent corners) are the visual signature; rebranding is a separate exercise.
````

- [ ] **Step 2: Commit**

```bash
git add branding/logo/README.md
git commit -m "docs(branding): document logo files and rebuild step"
```

---

## Final verification

- [ ] **Step 1: Confirm clean working tree**

```bash
git status
```

Expected: `nothing to commit, working tree clean`.

- [ ] **Step 2: Confirm the file inventory**

```bash
ls branding/logo/ && ls tools/branding-render/
```

Expected branding/logo/: `README.md  iceberg-176.png  iceberg-24.png  iceberg-48.png  iceberg-800.png  iceberg-96.png  iceberg.svg`

Expected tools/branding-render/: `bin  node_modules  package-lock.json  package.json  scripts  src  tests`

- [ ] **Step 3: Confirm tests pass**

```bash
cd tools/branding-render && npm test
```

Expected: 3 tests pass.

- [ ] **Step 4: Hand the user the upload path**

Tell the user:

> The 800 px PNG ready for YouTube upload is at `branding/logo/iceberg-800.png` (absolute path: `<repo-root>/branding/logo/iceberg-800.png`). Drag it into YouTube Studio → Customization → Branding → Picture.
