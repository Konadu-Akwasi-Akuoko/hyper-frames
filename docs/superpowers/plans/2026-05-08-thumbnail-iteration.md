# Thumbnail Creator — Iteration 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an Iconify fallback for icons (replacing the hand-coded SVG path), a `?grid` URL-toggled design overlay on every variant, and fix the underlying composition so thumbnails fill the canvas instead of leaving a 320 px void at the bottom.

**Architecture:** One new module + one new CLI in `tools/thumbnail-render/` for Iconify (on-demand fetch with a committed JSON cache). Pure CSS + a one-line inline script for the grid overlay. Layout fix is a 4-line CSS edit plus a font-size formula recompute in `SKILL.md`.

**Tech Stack:** Node 20+ native `fetch`, `node:test`, no new dependencies. Iconify public API at `api.iconify.design` (free, unauthenticated).

**Spec:** `docs/superpowers/specs/2026-05-08-thumbnail-iteration-design.md`

---

## Pre-flight notes

- **Not a git repo.** No commit steps. If the user later runs `git init`, the whole tree commits at once.
- **No new dependencies.** `package.json` does not change. Native `fetch` is available in Node 20+ and we use it directly.
- **The v1 thumbnail-creator was just shipped in this session.** Files referenced in this plan exist on disk; this plan modifies and extends them.
- **Existing tests must keep passing.** `tests/render.test.mjs` is not touched. New test file `tests/iconify.test.mjs` added.

---

## File structure

### Modified files

```
.claude/skills/thumbnail-creator/templates/styles.css      (layout fix + grid CSS)
.claude/skills/thumbnail-creator/templates/variant.html    (grid markup + script)
.claude/skills/thumbnail-creator/templates/contact-sheet.html (.variant-links CSS)
.claude/skills/thumbnail-creator/SKILL.md                  (Steps 3, 5, 6, 7 updates)
.claude/skills/thumbnail-creator/reference/icon-picking.md (rewrite Iconify section)
.claude/skills/thumbnail-creator/reference/visual-signature.md (icon row)
videos/why-text-is-hard-2026-05-07/thumbnails/round-1/{a,b,c}.html   (regenerated)
videos/why-text-is-hard-2026-05-07/thumbnails/round-1/contact-sheet.html (regenerated)
videos/why-text-is-hard-2026-05-07/thumbnail-{a,b,c}.png   (re-rendered)
```

### Created files

```
tools/thumbnail-render/src/iconify.mjs                     (getIconifyBody)
tools/thumbnail-render/bin/icon.mjs                        (CLI wrapper)
tools/thumbnail-render/icons/iconify-cache.json            (initially "{}")
tools/thumbnail-render/tests/iconify.test.mjs              (4 cases)
```

### Untouched

- `tools/thumbnail-render/src/render.mjs`
- `tools/thumbnail-render/bin/render.mjs`
- `tools/thumbnail-render/scripts/sync-icons.mjs` (Lucide sync stays separate)
- `tools/thumbnail-render/tests/render.test.mjs`
- `tools/thumbnail-render/icons/lucide.json`
- `.claude/skills/thumbnail-creator/reference/{text-rephrase-recipes,red-word-recipes,iteration-recipes}.md`

---

## Task 1: Write the failing test for `getIconifyBody`

**Files:**
- Create: `tools/thumbnail-render/tests/iconify.test.mjs`

The tests use a temp cache file and a mock `fetcher` parameter so they make no real network calls.

- [ ] **Step 1: Write the test file**

```javascript
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { getIconifyBody } from '../src/iconify.mjs';

const SVG_RESPONSE = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M2 2h20v20H2z" /></svg>';
const EXPECTED_BODY = '<path d="M2 2h20v20H2z" />';

function makeCache() {
  const dir = mkdtempSync(path.join(tmpdir(), 'iconify-test-'));
  const file = path.join(dir, 'iconify-cache.json');
  writeFileSync(file, '{}\n');
  return { dir, file };
}

test('getIconifyBody returns cached body without network', async () => {
  const { dir, file } = makeCache();
  try {
    writeFileSync(file, JSON.stringify({ 'ph:test-icon': '<rect />' }) + '\n');
    let fetchCalled = false;
    const fetcher = async () => { fetchCalled = true; throw new Error('should not fetch'); };
    const body = await getIconifyBody('ph:test-icon', { cachePath: file, fetcher });
    assert.equal(body, '<rect />');
    assert.equal(fetchCalled, false);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('getIconifyBody fetches and caches on miss', async () => {
  const { dir, file } = makeCache();
  try {
    let fetchCount = 0;
    const fetcher = async (url) => {
      fetchCount++;
      assert.match(url, /\/ph\/cursor-click\.svg$/);
      return { ok: true, status: 200, text: async () => SVG_RESPONSE };
    };
    const body1 = await getIconifyBody('ph:cursor-click', { cachePath: file, fetcher });
    assert.equal(body1, EXPECTED_BODY);
    assert.equal(fetchCount, 1);

    const cached = JSON.parse(readFileSync(file, 'utf8'));
    assert.equal(cached['ph:cursor-click'], EXPECTED_BODY);

    const body2 = await getIconifyBody('ph:cursor-click', { cachePath: file, fetcher });
    assert.equal(body2, EXPECTED_BODY);
    assert.equal(fetchCount, 1, 'second call should hit cache');
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('getIconifyBody throws on invalid name', async () => {
  const { dir, file } = makeCache();
  try {
    const fetcher = async () => { throw new Error('should not fetch'); };
    await assert.rejects(
      () => getIconifyBody('not a name', { cachePath: file, fetcher }),
      /invalid Iconify name/i
    );
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('getIconifyBody throws on HTTP failure and leaves cache unchanged', async () => {
  const { dir, file } = makeCache();
  try {
    const fetcher = async () => ({ ok: false, status: 404, text: async () => 'Not Found' });
    await assert.rejects(
      () => getIconifyBody('ph:does-not-exist', { cachePath: file, fetcher }),
      /Iconify fetch failed.*404/i
    );
    const cached = JSON.parse(readFileSync(file, 'utf8'));
    assert.deepEqual(cached, {});
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
```

- [ ] **Step 2: Run the test to verify it fails**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render && npm test
```

Expected: PASS for the existing 2 render tests, FAIL for the 4 new iconify tests with `Cannot find module '../src/iconify.mjs'`.

---

## Task 2: Implement `getIconifyBody`

**Files:**
- Create: `tools/thumbnail-render/src/iconify.mjs`

- [ ] **Step 1: Write the implementation**

```javascript
import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_CACHE_PATH = path.resolve(__dirname, '..', 'icons', 'iconify-cache.json');
const NAME_PATTERN = /^[a-z0-9-]+:[a-z0-9-]+$/;

/**
 * Resolve an Iconify icon body, fetching from the API and caching on miss.
 *
 * @param {string} qualifiedName - "<set>:<icon>", e.g. "ph:cursor-click"
 * @param {object} [opts]
 * @param {string} [opts.cachePath] - path to iconify-cache.json
 * @param {function} [opts.fetcher] - fetch implementation (for testing)
 * @returns {Promise<string>} the SVG body (children of <svg>)
 */
export async function getIconifyBody(qualifiedName, opts = {}) {
  if (!NAME_PATTERN.test(qualifiedName)) {
    throw new Error(`invalid Iconify name: "${qualifiedName}" (expected <set>:<icon>)`);
  }

  const cachePath = opts.cachePath ?? DEFAULT_CACHE_PATH;
  const fetcher = opts.fetcher ?? globalThis.fetch;

  const cache = existsSync(cachePath)
    ? JSON.parse(readFileSync(cachePath, 'utf8'))
    : {};

  if (cache[qualifiedName]) return cache[qualifiedName];

  const [set, icon] = qualifiedName.split(':');
  const url = `https://api.iconify.design/${set}/${icon}.svg`;
  const res = await fetcher(url);
  if (!res.ok) {
    throw new Error(`Iconify fetch failed for "${qualifiedName}": HTTP ${res.status}`);
  }
  const svg = (await res.text()).replace(/^﻿/, '');
  const body = extractBody(svg);

  cache[qualifiedName] = body;
  const sorted = Object.fromEntries(Object.keys(cache).sort().map(k => [k, cache[k]]));
  writeFileSync(cachePath, JSON.stringify(sorted, null, 2) + '\n');

  return body;
}

function extractBody(svg) {
  const open = svg.indexOf('<svg');
  const gt = svg.indexOf('>', open);
  const close = svg.lastIndexOf('</svg>');
  if (open < 0 || gt < 0 || close < 0) {
    throw new Error('cannot parse SVG response — no <svg>...</svg>');
  }
  return svg.slice(gt + 1, close).trim();
}
```

- [ ] **Step 2: Run the test to verify it passes**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render && npm test
```

Expected: all 6 tests PASS (2 render + 4 iconify).

---

## Task 3: Initialize the empty Iconify cache

**Files:**
- Create: `tools/thumbnail-render/icons/iconify-cache.json`

- [ ] **Step 1: Write the file**

```json
{}
```

(File contents: a single line `{}` followed by a newline. The cache will fill in over time as the skill resolves Iconify icons.)

---

## Task 4: Implement `bin/icon.mjs` CLI

**Files:**
- Create: `tools/thumbnail-render/bin/icon.mjs`

- [ ] **Step 1: Write the CLI**

```javascript
#!/usr/bin/env node
import { getIconifyBody } from '../src/iconify.mjs';

const name = process.argv[2];
if (!name) {
  console.error('Usage: icon.mjs <set>:<icon-name>\nExample: icon.mjs ph:cursor-click');
  process.exit(2);
}

try {
  const body = await getIconifyBody(name);
  process.stdout.write(body);
  process.stdout.write('\n');
} catch (err) {
  console.error(`error: ${err.message}`);
  process.exit(1);
}
```

- [ ] **Step 2: Make it executable**

```bash
chmod +x /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render/bin/icon.mjs
```

- [ ] **Step 3: Smoke-test against a real Iconify icon (network required)**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render && \
  node bin/icon.mjs ph:cursor-click | head -c 200 && echo
```

Expected: prints an SVG body string starting with `<path` (Phosphor's cursor-click body). No errors.

- [ ] **Step 4: Verify the cache populated**

```bash
cat /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render/icons/iconify-cache.json
```

Expected: file now contains a key `"ph:cursor-click"` mapped to the body string. The JSON is sorted-keys, 2-space indent.

- [ ] **Step 5: Smoke-test cache hit (no network)**

Disconnect network or simulate offline-ish; either way, second invocation should never throw:

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render && \
  node bin/icon.mjs ph:cursor-click | head -c 50 && echo
```

Expected: same body printed instantly (no fetch latency since it's cached).

---

## Task 5: Update `templates/styles.css` — layout fix

**Files:**
- Modify: `.claude/skills/thumbnail-creator/templates/styles.css`

The current layout has top-anchored text and a 220 px right-side icon, leaving ~320 px of dead space at the bottom. We center the text vertically, scale the icon to 320 px, and tighten the right padding.

- [ ] **Step 1: Replace the `.thumbnail-text` rule**

Find the existing rule (it currently starts with `.thumbnail-text { position: absolute; left: 80px; top: 100px; right: 380px; ...`) and replace its first four declarations.

Old:

```css
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
```

New:

```css
.thumbnail-text {
  position: absolute;
  left: 80px;
  top: 50%;
  transform: translateY(-50%);
  right: 420px;
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
```

- [ ] **Step 2: Replace the `.thumbnail-icon` rule and its `svg` child**

Old:

```css
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
  /* Defaults so unclassed Lucide bodies render correctly. ... */
  stroke: var(--text);
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}
```

New (only `right`, `width`, `height` change; the comment + parent-SVG defaults stay):

```css
.thumbnail-icon {
  position: absolute;
  right: 80px;
  top: 50%;
  transform: translateY(-50%);
  width: 320px;
  height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.thumbnail-icon svg {
  width: 320px;
  height: 320px;
  /* Defaults so unclassed Lucide bodies render correctly. Hand-coded
   * SVGs may opt out by setting class="stroke" / "accent-stroke" /
   * "accent-fill" on individual children. */
  stroke: var(--text);
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
  fill: none;
}
```

- [ ] **Step 3: Verify the file by re-rendering an existing variant**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render && \
  node bin/render.mjs \
    /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/videos/why-text-is-hard-2026-05-07/thumbnails/round-1/a.html \
    --out /tmp/layout-check.png && \
  file /tmp/layout-check.png
```

Expected: PNG written, dimensions still 1280×720. (Visual position will look different from before — text now centered vertically, icon is bigger. The variant file's inline `font-size: 97px` will be slightly oversized for the new column width; that's fine for this verification step. Task 12 regenerates the variant files with the recomputed font sizes.)

---

## Task 6: Update `templates/styles.css` — append grid overlay rules

**Files:**
- Modify: `.claude/skills/thumbnail-creator/templates/styles.css`

The grid overlay is hidden by default. The variant HTML (Task 7) adds a `.with-grid` class to the `.thumbnail` element when the URL contains `?grid`.

- [ ] **Step 1: Append these rules to the bottom of `styles.css`**

```css
/* ---- Design grid overlay ----
 * Toggled by adding ?grid to the variant URL. Hidden by default; never
 * appears in rendered PNG output (the renderer does not pass query params
 * to the file:// URL). 4×3 numbered cells + YouTube safe-area outline +
 * duration-badge corner outline. Numbers + outlines render in red so they
 * stand out against the espresso-brown background.
 */
.grid-overlay {
  display: none;
  position: absolute;
  inset: 0;
  z-index: 10;
  pointer-events: none;
  grid-template-columns: repeat(4, 1fr);
  grid-template-rows: repeat(3, 1fr);
}
.thumbnail.with-grid .grid-overlay {
  display: grid;
}

.grid-cell {
  position: relative;
  border: 1px solid rgba(255, 64, 64, 0.45);
  font-family: ui-sans-serif, system-ui, sans-serif;
  font-size: 24px;
  font-weight: 600;
  color: rgba(255, 64, 64, 0.75);
  padding: 6px 0 0 8px;
  box-sizing: border-box;
}

.grid-safe-area {
  position: absolute;
  top: 76px;
  left: 76px;
  right: 76px;
  bottom: 76px;
  border: 2px dashed rgba(255, 64, 64, 0.6);
  pointer-events: none;
}

.grid-duration-badge {
  position: absolute;
  right: 12px;
  bottom: 12px;
  width: 140px;
  height: 40px;
  border: 2px solid rgba(255, 64, 64, 0.6);
  pointer-events: none;
}
```

- [ ] **Step 2: Verify CSS is syntactically valid**

```bash
node -e "const css = require('node:fs').readFileSync('/Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/.claude/skills/thumbnail-creator/templates/styles.css','utf8'); const opens = (css.match(/\{/g)||[]).length; const closes = (css.match(/\}/g)||[]).length; console.log('opens:', opens, 'closes:', closes); if (opens !== closes) process.exit(1);"
```

Expected: `opens` and `closes` are equal.

---

## Task 7: Update `templates/variant.html` — add grid markup + toggle script

**Files:**
- Modify: `.claude/skills/thumbnail-creator/templates/variant.html`

- [ ] **Step 1: Replace the entire file**

```html
<!--
  Tokens substituted by the thumbnail-creator skill:
    {{STYLES_HREF}}        absolute file:// URL to templates/styles.css
    {{TITLE_PLAIN}}        plain text title (for <title>)
    {{ROW_FONT_SIZE_PX}}   integer pixel size, autosized per variant
    {{TITLE_ROW_1..3}}     row HTML with accent <span> markup
    {{ICON_SVG_BODY}}      SVG body (children of <svg>); from Lucide cache
                           or Iconify on-demand fetch (never hand-coded)
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
    <div class="grid-overlay" aria-hidden="true">
      <div class="grid-cell">1</div>
      <div class="grid-cell">2</div>
      <div class="grid-cell">3</div>
      <div class="grid-cell">4</div>
      <div class="grid-cell">5</div>
      <div class="grid-cell">6</div>
      <div class="grid-cell">7</div>
      <div class="grid-cell">8</div>
      <div class="grid-cell">9</div>
      <div class="grid-cell">10</div>
      <div class="grid-cell">11</div>
      <div class="grid-cell">12</div>
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
```

---

## Task 8: Update `templates/contact-sheet.html` — add `.variant-links` CSS

**Files:**
- Modify: `.claude/skills/thumbnail-creator/templates/contact-sheet.html`

The skill's generated `{{VARIANTS_HTML}}` will start including a `<div class="variant-links">…</div>` block per variant (Task 9). The CSS rule for that class lives in the contact sheet's `<style>` block.

- [ ] **Step 1: Append these rules inside the existing `<style>` block, just before the closing `</style>`**

Find the line `.grid-wrap .thumbnail { transform: scale(0.164); transform-origin: top left; }` near the end of the `<style>` block. Add the following rules immediately after it (still inside `<style>`):

```css
    .variant-links {
      margin-top: 12px;
      font-size: 12px;
      color: #666;
    }
    .variant-links a {
      color: #888;
      text-decoration: none;
      border-bottom: 1px dotted #444;
    }
    .variant-links a:hover { color: #ddd; }
```

- [ ] **Step 2: Update the leading comment's per-variant token list**

Find the leading `<!-- Tokens substituted by the thumbnail-creator skill: ... -->` comment and update the per-variant tokens section to include `{{LETTER_LOWER}}`. The full updated comment:

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
    {{LETTER_LOWER}}    a | b | c   (used in the variant-links hrefs)
    {{TITLE_PLAIN}}     the rephrased thumbnail text, plain
    {{THUMBNAIL_DIV}}   the .thumbnail markup, identical for full + grid wraps
-->
```

---

## Task 9: Update `SKILL.md` — Steps 3, 5, 6, 7

**Files:**
- Modify: `.claude/skills/thumbnail-creator/SKILL.md`

Four edits in one file. Make them in order to keep diffs clean.

- [ ] **Step 1: Replace the Step 3 font-size formula and column-width reference**

Find the section `#### Computing the per-variant font size` inside Step 3.

Old:

```
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
```

New:

````
JetBrains Mono is monospace, so the longest row determines the maximum
font size. The text column is 780 px wide (1280 − 80 left padding − 420
right padding for the 320 px icon). The formula:

```
longest_row_chars   = max character count across the 3 rows
                      (count letters, digits, and spaces; not the
                      <span> markup)
ROW_FONT_SIZE_PX    = floor(780 / (longest_row_chars * 0.6))
                      capped at 140
```

Examples (verified against rendered mockups):
- 13 chars → 100 px
- 14 chars →  92 px
- 15 chars →  86 px
- 16 chars →  81 px (visibly small — consider rephrasing shorter)
- 17 chars →  76 px (rejects, below the 80 px floor)

If the computed size falls below 80 px, reject the rephrase and either
produce a shorter wording or ask the user to choose a shorter title.
The renderer must NOT silently shrink — preview-vs-output drift is the
worst failure mode.
````

- [ ] **Step 2: Update Step 3's earlier mention of column width**

Find the bullet that reads:

```
- Fit cleanly in JetBrains Mono ExtraBold within the available text
  column (~820 px wide).
```

Replace with:

```
- Fit cleanly in JetBrains Mono ExtraBold within the available text
  column (~780 px wide).
```

- [ ] **Step 3: Replace Step 5 entirely**

Find `### Step 5 — Pick the icon` and replace its body.

Old:

```
### Step 5 — Pick the icon

Load `reference/icon-picking.md`. Pick **one** Lucide icon for the topic
(same icon across all 3 variants in this round). If no Lucide icon fits,
hand-code a tiny SVG using the locked icon style.

The SVG body for Lucide icons comes from
`<repo-root>/tools/thumbnail-render/icons/lucide.json`. Read that file,
look up by Lucide name (e.g. `Lock`, `Database`), and use the body string
verbatim.
```

New:

````
### Step 5 — Pick the icon

Load `reference/icon-picking.md`. Pick **one** icon for the topic (same
icon across all 3 variants in this round). Resolution order:

1. **Lucide.** Read
   `<repo-root>/tools/thumbnail-render/icons/lucide.json`. Look up by
   Lucide name (e.g. `Lock`, `Database`). Use the body string verbatim.
2. **Iconify fallback.** If no Lucide entry fits, pick an Iconify name
   in `<set>:<icon>` form (e.g. `ph:cursor-click`, `tabler:typography`).
   Resolve and cache the body via:

   ```bash
   node <repo-root>/tools/thumbnail-render/bin/icon.mjs <name>
   ```

   The CLI prints the SVG body to stdout, fetches from
   `api.iconify.design` on first use, caches to
   `tools/thumbnail-render/icons/iconify-cache.json`. Capture the
   stdout output as the body.
3. **Stop.** If neither Lucide nor any acceptable Iconify set fits,
   ask the user for an alternate icon name. Hand-coded SVG is no
   longer a documented option — the visual signature requires real
   icons from a curated set.

Iconify icon-set search order (line-icon sets only):
`lucide` → `ph` → `tabler` → `mynaui` → `heroicons` (outline) →
`lineicons`. Never pick from filled, multi-color, or pictographic sets
(`fluent-color`, `noto`, `twemoji`, `flat-color-icons`, etc.) — they
break the visual signature.

Apply the accent to one detail by inlining `stroke="#FFB627"` on
exactly one element of the body string (or `fill="#FFB627"` for a
filled detail). See `reference/icon-picking.md` for which element to
accent on common Lucide icons.
````

- [ ] **Step 4: Update Step 6's `{{VARIANTS_HTML}}` block shape to include the variant-links**

Find the section `#### The {{VARIANTS_HTML}} block shape` inside Step 6.

Old:

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

New:

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
  <div class="variant-links">
    <a href="{{LETTER_LOWER}}.html">view full</a> ·
    <a href="{{LETTER_LOWER}}.html?grid">view with grid</a>
  </div>
</div>
```

The new token `{{LETTER_LOWER}}` is `a` | `b` | `c` for variants A | B | C.

- [ ] **Step 5: Update Step 7's user-facing message**

Find the section `### Step 7 — Print the contact-sheet URL`.

Old:

```
> "Round N is ready. Open `file://<absolute-path-to-contact-sheet.html>`
> in your browser. The page shows each variant at full 1280×720 plus a
> small grid-size simulation (~210×118 px) so you can judge legibility
> at the YouTube feed size. Tell me what you want to change."
```

New:

```
> "Round N is ready. Open `file://<absolute-path-to-contact-sheet.html>`
> in your browser. The page shows each variant at full 1280×720 plus a
> small grid-size simulation (~210×118 px) so you can judge legibility
> at the YouTube feed size. Each variant has 'view full · view with
> grid' links — `?grid` overlays a 4×3 numbered grid plus YouTube
> safe-area markers for layout review. Tell me what you want to change."
```

---

## Task 10: Rewrite `reference/icon-picking.md`

**Files:**
- Modify: `.claude/skills/thumbnail-creator/reference/icon-picking.md`

Three changes: (a) replace the "Fallback — hand-coded SVG" section with an "Iconify fallback" section; (b) remove the Aa example; (c) add a short note on accent placement for cached icon bodies.

- [ ] **Step 1: Replace the entire `## Fallback — hand-coded SVG` section through the end of the file**

Find the line `## Fallback — hand-coded SVG` and replace from there to end-of-file with:

````markdown
## Fallback — Iconify

If no Lucide icon in the lookup table fits the topic, fall back to
Iconify. Iconify aggregates ~200 icon sets and ~200,000 icons; we use
only the line-icon sets that match the locked aesthetic.

### Iconify icon-set search order

Try sets in this order. Pick the first one whose conventional naming
matches the topic noun:

1. `lucide` (Iconify-mirrored — only useful when our local cache is
   missing an icon for some reason)
2. `ph` (Phosphor Regular)
3. `tabler`
4. `mynaui`
5. `heroicons` (outline variant)
6. `lineicons`

Never pick from filled, multi-color, or pictographic sets
(`fluent-color`, `noto`, `twemoji`, `flat-color-icons`, etc.). Those
have different visual weight and break the signature.

### Resolving an Iconify body

```bash
node <repo-root>/tools/thumbnail-render/bin/icon.mjs <set>:<icon>
```

The CLI prints the SVG body to stdout. First use fetches from
`api.iconify.design` and writes the body to
`tools/thumbnail-render/icons/iconify-cache.json` (committed —
every Iconify icon ever used is reviewable in git). Subsequent
uses are offline.

Example:

```bash
node tools/thumbnail-render/bin/icon.mjs ph:cursor-click
```

Returns the Phosphor cursor-click body, ready to substitute into
`{{ICON_SVG_BODY}}` in `templates/variant.html`.

### When to ask the user vs. pick yourself

Pick yourself when:
- The topic noun has an obvious Iconify name in one of the listed sets.
- A quick preview via `bin/icon.mjs` shows it reads as the topic at a
  glance.

Ask the user when:
- The topic is abstract enough that multiple plausible icons exist
  ("compression" — Archive? FileMinus? Layers? Box?). List 2–3
  candidates and let them pick.
- The first-pick fetch returns an icon that looks wrong at thumbnail
  size (too busy, too symbolic, multi-element).

### Accent placement on cached bodies

Lucide and Iconify bodies arrive without `class` attributes. To accent
one detail, inline `stroke="#FFB627"` (for stroked elements) or
`fill="#FFB627"` (for filled elements) on exactly one child of the
body. The "Suggested accent region" column in the Lucide lookup table
above tells you which element to accent for common icons. For Iconify
icons, pick the most distinctive geometric region — usually the part
that visually carries the icon's identity (lock body, key bow, the
crossbar of a "T", the disk's lid, etc.).

The locked CSS classes `.stroke`, `.accent-stroke`, `.accent-fill`
remain in `templates/styles.css` for any case where they're useful,
but the default path for cached bodies is inline `stroke="#FFB627"`.

## Reuse is encouraged

If two videos share a topic family, share the icon. The icon is a
category marker, not a unique identifier. Reusing icons across videos
strengthens the channel's visual identity.

## When in doubt

Pick the most literal topic noun. "Database indexes" → Lucide
`Database`. "Cursor click" → `ph:cursor-click`. Don't overthink. The
icon's job is to confirm what the text already said, not to be clever.
````

- [ ] **Step 2: Verify the "Aa" example is gone**

```bash
grep -n "Aa" /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/.claude/skills/thumbnail-creator/reference/icon-picking.md || echo "no Aa references — good"
```

Expected: `no Aa references — good`. If any `Aa` lines come back, find and remove them.

---

## Task 11: Update `reference/visual-signature.md` — icon row

**Files:**
- Modify: `.claude/skills/thumbnail-creator/reference/visual-signature.md`

Two small edits.

- [ ] **Step 1: Update the icon row in the constants table**

Find the row in `## The constants` table:

Old:

```
| Icon style | Lucide line icons, stroke-width 8 in 24×24 viewBox; accent-color fill on exactly one detail |
```

New:

```
| Icon style | Lucide line icons (or Iconify line set), 320×320 px display, parent-SVG default stroke-width 2 in 24×24 viewBox; accent on exactly one detail |
```

- [ ] **Step 2: Update the "Icons — Lucide line, accent on one detail" paragraph**

Find the paragraph in `## Why each constant` that starts `**Icons — Lucide line, accent on one detail.**`.

Old:

```
**Icons — Lucide line, accent on one detail.** Real SVG icons (not styled
text or bitmap font glyphs). The "one detail" rule is what gives the icon
its accent without overwhelming it: the lock body in amber, but the
shackle in off-white; the second "A" in amber, the first in off-white;
the key bow in amber, the shaft in off-white.
```

New:

```
**Icons — Lucide line (Iconify fallback), accent on one detail.** Real
SVG icons from a curated set — Lucide first, then any of the matching
Iconify line sets (Phosphor, Tabler, MynaUI, Heroicons-outline,
Lineicons). Hand-coded SVGs are not allowed; they break visual
consistency. The "one detail" rule is what gives the icon its accent
without overwhelming it: the lock body in amber, but the shackle in
off-white; the disk's lid in amber, but the body in off-white; the
key bow in amber, the shaft in off-white.
```

---

## Task 12: End-to-end smoke test — regenerate round-1 and re-render

**Files:**
- Modify: `videos/why-text-is-hard-2026-05-07/thumbnails/round-1/a.html`
- Modify: `videos/why-text-is-hard-2026-05-07/thumbnails/round-1/b.html`
- Modify: `videos/why-text-is-hard-2026-05-07/thumbnails/round-1/c.html`
- Modify: `videos/why-text-is-hard-2026-05-07/thumbnails/round-1/contact-sheet.html`
- Modify: `videos/why-text-is-hard-2026-05-07/thumbnail-{a,b,c}.png`

The existing round-1 files were written before this iteration's templates existed. Regenerate them with the new layout, the new font sizes, the Lucide `Type` icon (canonical for "text/typography" topic), and the `view full · view with grid` links in the contact sheet.

The Lucide `Type` body is already in the cache (verify with `node -e "console.log(require('/Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render/icons/lucide.json').Type)"`):
```
<polyline points="4 7 4 4 20 4 20 7" /><line x1="9" x2="15" y1="20" y2="20" /><line x1="12" x2="12" y1="4" y2="20" />
```

Accent rule for `Type`: tint the top crossbar (the `polyline` element) — that's the distinctive feature of a "T" glyph. The accented body becomes:

```
<polyline points="4 7 4 4 20 4 20 7" stroke="#FFB627" /><line x1="9" x2="15" y1="20" y2="20" /><line x1="12" x2="12" y1="4" y2="20" />
```

Variant text and accent placements stay the same as before (they're already on-spec). Only the font sizes change — recomputed with the new 780px column.

| Variant | Longest row chars | New font-size |
|---|---|---|
| A: TEXT RENDERING / IS INSANELY / DIFFICULT       | 14 (`TEXT RENDERING`) | 92 px |
| B: A LETTER ON / YOUR SCREEN IS / A FIGHT         | 14 (`YOUR SCREEN IS`) | 92 px |
| C: YOUR FONT IS / LYING TO / YOUR EYES            | 12 (`YOUR FONT IS`)   | 108 px |

- [ ] **Step 1: Replace `round-1/a.html`**

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>TEXT RENDERING IS INSANELY DIFFICULT</title>
  <link rel="stylesheet" href="file:///Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/.claude/skills/thumbnail-creator/templates/styles.css">
</head>
<body>
  <div class="thumbnail">
    <div class="thumbnail-text" style="font-size: 92px;">
      <span class="thumbnail-row">TEXT <span class="accent">RENDERING</span></span>
      <span class="thumbnail-row">IS <span class="accent">INSANELY</span></span>
      <span class="thumbnail-row">DIFFICULT</span>
    </div>
    <div class="thumbnail-icon">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><polyline points="4 7 4 4 20 4 20 7" stroke="#FFB627" /><line x1="9" x2="15" y1="20" y2="20" /><line x1="12" x2="12" y1="4" y2="20" /></svg>
    </div>
    <div class="grid-overlay" aria-hidden="true">
      <div class="grid-cell">1</div>
      <div class="grid-cell">2</div>
      <div class="grid-cell">3</div>
      <div class="grid-cell">4</div>
      <div class="grid-cell">5</div>
      <div class="grid-cell">6</div>
      <div class="grid-cell">7</div>
      <div class="grid-cell">8</div>
      <div class="grid-cell">9</div>
      <div class="grid-cell">10</div>
      <div class="grid-cell">11</div>
      <div class="grid-cell">12</div>
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
```

- [ ] **Step 2: Replace `round-1/b.html`**

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>A LETTER ON YOUR SCREEN IS A FIGHT</title>
  <link rel="stylesheet" href="file:///Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/.claude/skills/thumbnail-creator/templates/styles.css">
</head>
<body>
  <div class="thumbnail">
    <div class="thumbnail-text" style="font-size: 92px;">
      <span class="thumbnail-row">A LETTER ON</span>
      <span class="thumbnail-row">YOUR <span class="accent">SCREEN</span> IS</span>
      <span class="thumbnail-row">A <span class="accent">FIGHT</span></span>
    </div>
    <div class="thumbnail-icon">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><polyline points="4 7 4 4 20 4 20 7" stroke="#FFB627" /><line x1="9" x2="15" y1="20" y2="20" /><line x1="12" x2="12" y1="4" y2="20" /></svg>
    </div>
    <div class="grid-overlay" aria-hidden="true">
      <div class="grid-cell">1</div>
      <div class="grid-cell">2</div>
      <div class="grid-cell">3</div>
      <div class="grid-cell">4</div>
      <div class="grid-cell">5</div>
      <div class="grid-cell">6</div>
      <div class="grid-cell">7</div>
      <div class="grid-cell">8</div>
      <div class="grid-cell">9</div>
      <div class="grid-cell">10</div>
      <div class="grid-cell">11</div>
      <div class="grid-cell">12</div>
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
```

- [ ] **Step 3: Replace `round-1/c.html`**

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>YOUR FONT IS LYING TO YOUR EYES</title>
  <link rel="stylesheet" href="file:///Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/.claude/skills/thumbnail-creator/templates/styles.css">
</head>
<body>
  <div class="thumbnail">
    <div class="thumbnail-text" style="font-size: 108px;">
      <span class="thumbnail-row">YOUR <span class="accent">FONT</span> IS</span>
      <span class="thumbnail-row"><span class="accent">LYING</span> TO</span>
      <span class="thumbnail-row">YOUR EYES</span>
    </div>
    <div class="thumbnail-icon">
      <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><polyline points="4 7 4 4 20 4 20 7" stroke="#FFB627" /><line x1="9" x2="15" y1="20" y2="20" /><line x1="12" x2="12" y1="4" y2="20" /></svg>
    </div>
    <div class="grid-overlay" aria-hidden="true">
      <div class="grid-cell">1</div>
      <div class="grid-cell">2</div>
      <div class="grid-cell">3</div>
      <div class="grid-cell">4</div>
      <div class="grid-cell">5</div>
      <div class="grid-cell">6</div>
      <div class="grid-cell">7</div>
      <div class="grid-cell">8</div>
      <div class="grid-cell">9</div>
      <div class="grid-cell">10</div>
      <div class="grid-cell">11</div>
      <div class="grid-cell">12</div>
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
```

- [ ] **Step 4: Replace `round-1/contact-sheet.html`**

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Round 1 — why-text-is-hard-2026-05-07</title>
  <link rel="stylesheet" href="file:///Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/.claude/skills/thumbnail-creator/templates/styles.css">
  <style>
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
    .full-wrap { width: 512px; height: 288px; overflow: hidden; }
    .full-wrap .thumbnail { transform: scale(0.4); transform-origin: top left; }
    .grid-wrap { width: 210px; height: 118px; overflow: hidden; }
    .grid-wrap .thumbnail { transform: scale(0.164); transform-origin: top left; }
    .variant-links {
      margin-top: 12px;
      font-size: 12px;
      color: #666;
    }
    .variant-links a {
      color: #888;
      text-decoration: none;
      border-bottom: 1px dotted #444;
    }
    .variant-links a:hover { color: #ddd; }
  </style>
</head>
<body>
  <h1>Round 1 — why-text-is-hard-2026-05-07</h1>
  <div class="meta">
    Title input: <code>Why is rendering text so complicated?</code><br>
    Folder: <code>/Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/videos/why-text-is-hard-2026-05-07/thumbnails/round-1</code>
  </div>

  <div class="variant">
    <div class="variant-header">
      <span class="variant-letter">A</span>
      <span class="variant-text">TEXT RENDERING IS INSANELY DIFFICULT</span>
    </div>
    <div class="row">
      <div>
        <div class="row-label">Full size (40% of 1280×720)</div>
        <div class="full-wrap">
          <div class="thumbnail">
            <div class="thumbnail-text" style="font-size: 92px;">
              <span class="thumbnail-row">TEXT <span class="accent">RENDERING</span></span>
              <span class="thumbnail-row">IS <span class="accent">INSANELY</span></span>
              <span class="thumbnail-row">DIFFICULT</span>
            </div>
            <div class="thumbnail-icon">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><polyline points="4 7 4 4 20 4 20 7" stroke="#FFB627" /><line x1="9" x2="15" y1="20" y2="20" /><line x1="12" x2="12" y1="4" y2="20" /></svg>
            </div>
          </div>
        </div>
      </div>
      <div>
        <div class="row-label">YouTube feed grid (~210px)</div>
        <div class="grid-wrap">
          <div class="thumbnail">
            <div class="thumbnail-text" style="font-size: 92px;">
              <span class="thumbnail-row">TEXT <span class="accent">RENDERING</span></span>
              <span class="thumbnail-row">IS <span class="accent">INSANELY</span></span>
              <span class="thumbnail-row">DIFFICULT</span>
            </div>
            <div class="thumbnail-icon">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><polyline points="4 7 4 4 20 4 20 7" stroke="#FFB627" /><line x1="9" x2="15" y1="20" y2="20" /><line x1="12" x2="12" y1="4" y2="20" /></svg>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="variant-links">
      <a href="a.html">view full</a> ·
      <a href="a.html?grid">view with grid</a>
    </div>
  </div>

  <div class="variant">
    <div class="variant-header">
      <span class="variant-letter">B</span>
      <span class="variant-text">A LETTER ON YOUR SCREEN IS A FIGHT</span>
    </div>
    <div class="row">
      <div>
        <div class="row-label">Full size (40% of 1280×720)</div>
        <div class="full-wrap">
          <div class="thumbnail">
            <div class="thumbnail-text" style="font-size: 92px;">
              <span class="thumbnail-row">A LETTER ON</span>
              <span class="thumbnail-row">YOUR <span class="accent">SCREEN</span> IS</span>
              <span class="thumbnail-row">A <span class="accent">FIGHT</span></span>
            </div>
            <div class="thumbnail-icon">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><polyline points="4 7 4 4 20 4 20 7" stroke="#FFB627" /><line x1="9" x2="15" y1="20" y2="20" /><line x1="12" x2="12" y1="4" y2="20" /></svg>
            </div>
          </div>
        </div>
      </div>
      <div>
        <div class="row-label">YouTube feed grid (~210px)</div>
        <div class="grid-wrap">
          <div class="thumbnail">
            <div class="thumbnail-text" style="font-size: 92px;">
              <span class="thumbnail-row">A LETTER ON</span>
              <span class="thumbnail-row">YOUR <span class="accent">SCREEN</span> IS</span>
              <span class="thumbnail-row">A <span class="accent">FIGHT</span></span>
            </div>
            <div class="thumbnail-icon">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><polyline points="4 7 4 4 20 4 20 7" stroke="#FFB627" /><line x1="9" x2="15" y1="20" y2="20" /><line x1="12" x2="12" y1="4" y2="20" /></svg>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="variant-links">
      <a href="b.html">view full</a> ·
      <a href="b.html?grid">view with grid</a>
    </div>
  </div>

  <div class="variant">
    <div class="variant-header">
      <span class="variant-letter">C</span>
      <span class="variant-text">YOUR FONT IS LYING TO YOUR EYES</span>
    </div>
    <div class="row">
      <div>
        <div class="row-label">Full size (40% of 1280×720)</div>
        <div class="full-wrap">
          <div class="thumbnail">
            <div class="thumbnail-text" style="font-size: 108px;">
              <span class="thumbnail-row">YOUR <span class="accent">FONT</span> IS</span>
              <span class="thumbnail-row"><span class="accent">LYING</span> TO</span>
              <span class="thumbnail-row">YOUR EYES</span>
            </div>
            <div class="thumbnail-icon">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><polyline points="4 7 4 4 20 4 20 7" stroke="#FFB627" /><line x1="9" x2="15" y1="20" y2="20" /><line x1="12" x2="12" y1="4" y2="20" /></svg>
            </div>
          </div>
        </div>
      </div>
      <div>
        <div class="row-label">YouTube feed grid (~210px)</div>
        <div class="grid-wrap">
          <div class="thumbnail">
            <div class="thumbnail-text" style="font-size: 108px;">
              <span class="thumbnail-row">YOUR <span class="accent">FONT</span> IS</span>
              <span class="thumbnail-row"><span class="accent">LYING</span> TO</span>
              <span class="thumbnail-row">YOUR EYES</span>
            </div>
            <div class="thumbnail-icon">
              <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><polyline points="4 7 4 4 20 4 20 7" stroke="#FFB627" /><line x1="9" x2="15" y1="20" y2="20" /><line x1="12" x2="12" y1="4" y2="20" /></svg>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="variant-links">
      <a href="c.html">view full</a> ·
      <a href="c.html?grid">view with grid</a>
    </div>
  </div>

</body>
</html>
```

- [ ] **Step 5: Re-render the three PNGs**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render && \
  node bin/render.mjs \
    /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/videos/why-text-is-hard-2026-05-07/thumbnails/round-1 \
    --variants \
    --out-dir /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/videos/why-text-is-hard-2026-05-07
```

Expected: three PNGs written. Each is exactly 1280×720 (`file thumbnail-a.png` reports `1280 x 720`).

- [ ] **Step 6: Visually verify the rendered PNG**

Open `videos/why-text-is-hard-2026-05-07/thumbnail-a.png` (or use Read on it to inspect).

Expected:
- Text block is **vertically centered** (top and bottom margins look roughly equal, ~80–100 px each).
- Icon is bigger than before (~25% of canvas width) and shares vertical center with the text.
- Top crossbar of the "T" icon is amber; the rest of the "T" is warm off-white.
- No grid overlay in the rendered PNG (grid is hidden by default; renderer doesn't pass `?grid`).

- [ ] **Step 7: Manually verify the `?grid` toggle**

```bash
open "file:///Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/videos/why-text-is-hard-2026-05-07/thumbnails/round-1/a.html?grid"
```

Expected (in the browser): same thumbnail, plus 12 numbered red cells, a red dashed safe-area outline, and a red solid box in the bottom-right marking the duration-badge area. Closing the page and re-opening without `?grid` shows the clean version.

- [ ] **Step 8: Run the full test suite one more time**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/thumbnail-render && npm test
```

Expected: all 6 tests PASS.

---

## Self-review notes

The plan covers every section of the spec:

| Spec section | Covered by |
|---|---|
| §1 Why this iteration exists | Goal in plan header |
| §2.1 In scope | Tasks 1–12 |
| §2.2 Out of scope | Pre-flight notes; no tasks for serve.mjs etc. |
| §3.1 Resolution order | SKILL.md Step 5 (Task 9 Step 3); icon-picking.md (Task 10) |
| §3.2 How the skill picks an Iconify name | icon-picking.md (Task 10) |
| §3.2.1 Icon-set search order | SKILL.md (Task 9) + icon-picking.md (Task 10) |
| §3.3 src/iconify.mjs | Task 2 |
| §3.4 bin/icon.mjs | Task 4 |
| §3.5 Tests | Task 1 (4 cases as specified) |
| §3.6 Banning hand-coded SVG | Task 10 (rewrite icon-picking.md, remove Aa) |
| §4 Grid overlay (toggle, markup, markers, workflow) | Tasks 6, 7, 8, 9 |
| §5.1 styles.css layout fix | Task 5 |
| §5.2 Font-size formula | Task 9 Step 1 |
| §5.3 visual-signature.md icon-size note | Task 11 |
| §6 File diff list | "File structure" section + per-task paths |
| §7 Hard rules carried over | Untouched (no SKILL.md edits to that section) |
| §8 Testing posture | Task 1, Task 4 smoke, Task 12 |
| §9 Footguns and notes | iconify.mjs strips BOM, sorted-keys cache write, permissive `?grid` sniff, z-index 10 — all in Task 2/6/7 code |

No placeholders. Every task has complete code blocks. Type and method names are consistent: `getIconifyBody(qualifiedName, opts)` is defined once (Task 2) and matches the test expectations (Task 1) and CLI usage (Task 4). The `LETTER_LOWER` token is introduced in Task 8 and referenced in Task 9.
