# thumbnail-render

Brand-agnostic Node tool that turns thumbnail HTML into 1280×720 PNG via
Playwright headless Chrome. Used by the `thumbnail-and-title-generator` Claude skill;
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
