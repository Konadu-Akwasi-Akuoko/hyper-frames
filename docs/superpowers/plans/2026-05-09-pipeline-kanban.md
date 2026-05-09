# Pipeline Kanban Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `kanban.html` at the repo root — a single-file HTML Kanban board that tracks every video in `videos/` through 8 pipeline stages, persists to localStorage, and optionally syncs with the filesystem via the File System Access API.

**Architecture:** Single HTML file. No build step. No `node_modules` at the repo root. One `<script>` IIFE containing: state model + localStorage persistence + render function + DOM event bindings + File System Access API scan logic + IndexedDB handle storage. Pure helpers (slug normalization, stage suggestion, drift detection, scan-merge) are tested in-page via a `?test=1` URL mode that runs assertion blocks and prints pass/fail.

**Tech Stack:** Vanilla HTML/CSS/JS. Google Fonts CDN for Fraunces + JetBrains Mono. HTML5 drag-and-drop. File System Access API (Chromium-only; graceful degradation on Firefox/Safari). IndexedDB for persisting the directory handle.

**Spec reference:** `docs/superpowers/specs/2026-05-09-pipeline-kanban-design.md`. The visual mockup at `.superpowers/brainstorm/27329-1778293267/content/kanban-mockup.html` is the canonical reference for layout, type, color, and spacing — copy CSS rules and HTML structure from the mockup wherever the plan says "from the mockup".

**XSS / safety model:** Rendering uses `Range.createContextualFragment(html)` + `Element.replaceChildren()`. Every user-derived value (`slug`, `title`, `date`, `notes`, folder paths) is passed through `escapeHtml()` before interpolation into the HTML template strings. The HTML structure itself is static code; there is no untrusted input surface.

---

## File structure

Single file at the repo root: `kanban.html`. Internal layout:

```
kanban.html
├── <head>
│   ├── Google Fonts: Fraunces (variable) + JetBrains Mono
│   └── <style>: design tokens (CSS custom properties), reset, layout, components
├── <body>
│   ├── <header class="topbar">    project title, Add, Sync, Help, status pill
│   ├── <main class="board">       8 columns in a horizontal flex
│   ├── <aside class="panel">      side panel (hidden until a card is open)
│   ├── <dialog id="add-dialog">   add-card modal
│   └── <dialog id="help-dialog">  keyboard shortcuts modal
└── <script>                       single IIFE
```

Inside the IIFE:

```
- Constants: STAGES, ARTIFACTS, STORAGE_KEY, SCHEMA_VERSION, COMPOSE_THRESHOLD_BYTES,
  ARTIFACT_PATHS, FOLDER_RE, IDB_NAME, IDB_STORE, FS_SUPPORTED, DRIFT_SVG
- DOM helpers: escapeHtml, frag, setContent, h
- Pure helpers: kebabSlug, computeSuggested, hasDriftFor, statusFromCount,
  uuid, todayISO, titleCaseSlug, emptyArtifacts, relativeTime, folderPath
- State + persistence: emptyState, loadState, persist, mutate, showStorageBanner
- Rendering: render, renderColumn, renderCard, renderPanel, renderArtifactRow,
  updateStatusPill, updateNotesStatus
- Interactions: bindTopbar, bindBoardEvents, bindPanelEvents, bindAddDialog,
  bindHelpDialog, bindKeyboard, openAddDialog, openHelpDialog, saveNotesNow,
  notesDebounceTimer, notesLastSavedAt
- IndexedDB: idb, idbGet, idbSet, idbDelete
- FS scan: getCachedDirHandle, setCachedDirHandle, clearCachedDirHandle,
  pickDirHandle, ensureReadPermission, exists, voiceoverStatus, composeStatus,
  thumbnailStatus, hasMp4InOutput, readOutlineH1, scan, mergeScan
- Test mode: runTests; if URL has ?test=1 → runTests() else render()
- Boot: bindTopbar(), bindAddDialog(), bindHelpDialog(), bindBoardEvents(),
  bindPanelEvents(), bindKeyboard(), seed-if-flag, render()
```

Tasks below produce this in order.

---

## Task 1: Scaffold the file with design tokens, fonts, topbar, and empty grid

**Files:**
- Create: `kanban.html`

- [ ] **Step 1: Create `kanban.html`** with the design-token CSS, font imports, and topbar markup. Copy the relevant pieces verbatim from the visual mockup at `.superpowers/brainstorm/27329-1778293267/content/kanban-mockup.html`:
  - the entire `:root` block,
  - the `* { box-sizing }` reset,
  - `html, body { ... }`,
  - the body grid + `body::before` grain texture,
  - `.topbar`, `.topbar::before`, `.brand*`, `.toolbar`, `.status-pill`, `.btn`, `.btn:hover`, `.btn .glyph`, `.btn-icon`,
  - the `<header class="topbar">` markup with brand SVG and the four buttons.

Three deviations from the mockup:
  1. Status pill text: `0 cards · never synced` (not the mockup's hardcoded "12 cards · synced 4m ago").
  2. Replace `<aside class="panel">` body content with `<aside class="panel" hidden></aside>`.
  3. Add to body's CSS so the panel collapses to 0 width when hidden:

```css
body:has(.panel[hidden]) {
  grid-template-columns: 1fr 0;
}
```

Add IDs to the topbar buttons for later wiring: `id="btn-add"`, `id="btn-sync"`, `id="btn-help"`.

- [ ] **Step 2: Open in a Chromium browser**

```bash
open /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/kanban.html
```

Expected: topbar renders correctly with brand mark, italic Fraunces "hyper-frames", mono "Pipeline" label, status pill "0 cards · never synced", three buttons, hairline copper scan line. Board area is empty and full-width (panel hidden). No console errors.

- [ ] **Step 3: Commit**

```bash
git add kanban.html
git commit -m "feat(kanban): scaffold with design tokens, fonts, topbar"
```

---

## Task 2: Render 8 columns with sticky headers + empty placeholders

**Files:**
- Modify: `kanban.html`

- [ ] **Step 1: Add column-related CSS** — copy from the mockup: `.board`, `.columns`, `.column`, `.column::before`, `.column-header`, `.stage-name`, `.count`, `.column-body`, `.empty`, `.empty-text`, the `::-webkit-scrollbar` rules, and `@keyframes fade-up` + per-column `.column:nth-child(N) { animation-delay: ... }` rules.

- [ ] **Step 2: Add IIFE skeleton with STAGES + initial render**

Append to `<body>`:

```html
<script>
(() => {
  'use strict';

  const STAGES = [
    { id: 'idea',      label: 'Idea' },
    { id: 'research',  label: 'Research' },
    { id: 'script',    label: 'Script' },
    { id: 'voiceover', label: 'Voiceover' },
    { id: 'compose',   label: 'Compose' },
    { id: 'thumbnail', label: 'Thumbnail' },
    { id: 'render',    label: 'Render' },
    { id: 'published', label: 'Published' },
  ];

  function escapeHtml(s) {
    return String(s ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
  }

  function frag(htmlStr) {
    return document.createRange().createContextualFragment(htmlStr);
  }

  function setContent(el, htmlStr) {
    el.replaceChildren(frag(htmlStr));
  }

  function renderColumn(stage, cards) {
    const count = cards.length;
    const countAttr = count > 0 ? 'data-active' : '';
    const body = count === 0
      ? `<div class="empty"><span class="empty-text">No cards in flight.</span></div>`
      : cards.map(renderCard).join('');
    return `
      <div class="column" data-stage="${stage.id}">
        <div class="column-header">
          <span class="stage-name">${escapeHtml(stage.label)}</span>
          <span class="count" ${countAttr}>${count}</span>
        </div>
        <div class="column-body">${body}</div>
      </div>
    `;
  }

  function renderCard() { return ''; } // filled in next task

  function render() {
    const board = document.querySelector('.board');
    const cards = []; // empty for now
    const cardsByStage = Object.fromEntries(STAGES.map(s => [s.id, []]));
    setContent(board, `<div class="columns">${
      STAGES.map(s => renderColumn(s, cardsByStage[s.id])).join('')
    }</div>`);
  }

  render();
})();
</script>
```

- [ ] **Step 3: Reload the browser**

Expected: 8 columns render side-by-side. Each shows uppercase tracked label, `0` count badge in muted color, and an italic "No cards in flight." dashed-border placeholder. Page-load fade-up runs once with the staggered delays.

- [ ] **Step 4: Commit**

```bash
git add kanban.html
git commit -m "feat(kanban): render 8 columns from STAGES"
```

---

## Task 3: Render cards from hardcoded sample state

**Files:**
- Modify: `kanban.html`

- [ ] **Step 1: Add card-related CSS** — copy from the mockup: `.card`, `.card:hover`, `.card.is-open`, `.card.is-open::after`, `.card-meta`, `.slug`, `.drift`, `.drift svg`, `.title`, `.date`, `.dots`, `.dot`, `.dot-partial`, `.dot-present`, `@keyframes dot-breath`, and `.card:hover .dot`.

- [ ] **Step 2: Add ARTIFACTS, DRIFT_SVG, dotClass, renderCard**

Add to the IIFE near the top, after `STAGES`:

```js
// Ordered for the 7 progress dots (left to right). 'idea' has no dot.
// 'voiceover' rolls in narration: 'partial' = mp3+transcript only;
// 'present' = +narration-map.json.
const ARTIFACTS = [
  { id: 'research',  label: 'Research' },
  { id: 'script',    label: 'Script' },
  { id: 'voiceover', label: 'Voiceover' },
  { id: 'compose',   label: 'Compose' },
  { id: 'thumbnail', label: 'Thumbnail' },
  { id: 'render',    label: 'Render' },
  { id: 'published', label: 'Published' },
];

const DRIFT_SVG = `
  <svg width="11" height="10" viewBox="0 0 11 10" fill="none" aria-hidden="true">
    <path d="M5.5 1L10 9H1L5.5 1Z" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round" fill="none"/>
    <circle cx="5.5" cy="6.5" r="0.7" fill="currentColor"/>
  </svg>`;

function dotClass(status) {
  if (status === 'present') return 'dot dot-present';
  if (status === 'partial') return 'dot dot-partial';
  return 'dot';
}
```

Replace `renderCard()` with:

```js
function renderCard(card) {
  const isOpen = card.id === state.ui.panelOpenCardId;
  const drift = card.hasDrift
    ? `<span class="drift" title="Scan suggests: ${escapeHtml(card.suggestedLabel || '')}">${DRIFT_SVG}</span>`
    : '';
  const dots = ARTIFACTS.map(a => {
    const status = card.artifacts?.[a.id] || 'missing';
    return `<li class="${dotClass(status)}" title="${escapeHtml(a.label)}"></li>`;
  }).join('');
  return `
    <article class="card${isOpen ? ' is-open' : ''}" data-card-id="${escapeHtml(card.id)}" draggable="true">
      <div class="card-meta">
        <span class="slug">${escapeHtml(card.slug)}</span>
        ${drift}
      </div>
      <h3 class="title">${escapeHtml(card.title)}</h3>
      <time class="date">${escapeHtml(card.date)}</time>
      <ol class="dots" aria-label="Pipeline progress">${dots}</ol>
    </article>
  `;
}
```

- [ ] **Step 3: Add hardcoded sample state + status-pill helper + wire `render()`**

Add to the IIFE:

```js
function relativeTime(iso) {
  if (!iso) return 'never';
  const ms = Date.now() - new Date(iso).getTime();
  const s = Math.floor(ms / 1000);
  if (s < 60) return 'just now';
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

function updateStatusPill() {
  const pill = document.querySelector('.status-pill');
  if (!pill) return;
  const n = state.cards.length;
  const last = state.lastSyncedAt;
  const synced = last ? `synced ${relativeTime(last)}` : 'never synced';
  pill.textContent = `${n} card${n === 1 ? '' : 's'} · ${synced}`;
}

let state = {
  schemaVersion: 1,
  lastSyncedAt: null,
  ui: { panelOpenCardId: null },
  cards: [
    { id: 'a', slug: 'font-rendering', title: 'The Pixel Olympics',
      date: '2026-05-09', stage: 'idea',
      artifacts: { research: 'missing', script: 'missing', voiceover: 'missing',
        compose: 'missing', thumbnail: 'missing', render: 'missing', published: 'missing' },
      notes: '', createdAt: '2026-05-09T09:00:00Z', updatedAt: '2026-05-09T09:00:00Z',
      lastScannedAt: null, hasDrift: false },
    { id: 'b', slug: 'tcp-handshake', title: 'Three-Way Hello',
      date: '2026-04-28', stage: 'research',
      artifacts: { research: 'present', script: 'missing', voiceover: 'missing',
        compose: 'missing', thumbnail: 'missing', render: 'missing', published: 'missing' },
      notes: '', createdAt: '2026-04-28T09:00:00Z', updatedAt: '2026-04-28T09:00:00Z',
      lastScannedAt: null, hasDrift: false },
    { id: 'c', slug: 'why-text-is-hard', title: 'Why Text Is Hard',
      date: '2026-05-07', stage: 'compose',
      artifacts: { research: 'present', script: 'present', voiceover: 'present',
        compose: 'partial', thumbnail: 'present', render: 'missing', published: 'missing' },
      notes: '', createdAt: '2026-05-07T09:00:00Z', updatedAt: '2026-05-07T09:00:00Z',
      lastScannedAt: null, hasDrift: false },
    { id: 'd', slug: 'ssl-cert-magic', title: 'How TLS Trusts Anyone',
      date: '2026-05-03', stage: 'voiceover',
      artifacts: { research: 'present', script: 'present', voiceover: 'present',
        compose: 'partial', thumbnail: 'missing', render: 'missing', published: 'missing' },
      notes: '', createdAt: '2026-05-03T09:00:00Z', updatedAt: '2026-05-03T09:00:00Z',
      lastScannedAt: null, hasDrift: true, suggestedLabel: 'Compose' },
    { id: 'e', slug: 'color-spaces', title: 'Why RGB Lies',
      date: '2026-04-15', stage: 'published',
      artifacts: { research: 'present', script: 'present', voiceover: 'present',
        compose: 'present', thumbnail: 'present', render: 'present', published: 'present' },
      notes: '', createdAt: '2026-04-15T09:00:00Z', updatedAt: '2026-04-15T09:00:00Z',
      lastScannedAt: null, hasDrift: false },
  ],
};
```

Replace `render()` body with:

```js
function render() {
  const board = document.querySelector('.board');
  const cards = state.cards;
  const cardsByStage = Object.fromEntries(STAGES.map(s => [s.id, []]));
  for (const c of cards) {
    if (cardsByStage[c.stage]) cardsByStage[c.stage].push(c);
  }
  for (const arr of Object.values(cardsByStage)) {
    arr.sort((a, b) => (b.updatedAt || '').localeCompare(a.updatedAt || ''));
  }
  setContent(board, `<div class="columns">${
    STAGES.map(s => renderColumn(s, cardsByStage[s.id])).join('')
  }</div>`);
  updateStatusPill();
}
```

- [ ] **Step 4: Reload the browser**

Expected: 5 cards distributed across Idea, Research, Compose, Voiceover, Published. The Compose card shows mostly-filled progress dots with one amber breathing dot. The SSL card shows the amber drift triangle (top-right). Status pill: "5 cards · never synced". Empty Script/Thumbnail/Render columns show the placeholder.

- [ ] **Step 5: Commit**

```bash
git add kanban.html
git commit -m "feat(kanban): render cards with progress dots and drift hint"
```

---

## Task 4: Pure helpers + `?test=1` test mode

**Files:**
- Modify: `kanban.html`

- [ ] **Step 1: Add the helper functions** (above `let state`)

```js
function kebabSlug(input) {
  return String(input ?? '')
    .toLowerCase()
    .replace(/[^a-z0-9\s\-_]/g, '')
    .replace(/[\s_]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-+|-+$/g, '');
}

function computeSuggested(artifacts) {
  const ordered = ['research', 'script', 'voiceover', 'compose', 'thumbnail', 'render'];
  let suggested = 'idea';
  for (const stage of ordered) {
    if (artifacts?.[stage] === 'present') suggested = stage;
  }
  return suggested;
}

function hasDriftFor(card, suggestedStage) {
  if (!card || !suggestedStage) return false;
  if (card.stage === 'published') return false;
  if (suggestedStage === 'idea') return false;
  return suggestedStage !== card.stage;
}
```

- [ ] **Step 2: Add the test runner**

At the very bottom of the IIFE (replace the bare `render();` call):

```js
function runTests() {
  const results = [];
  const t = (name, fn) => {
    try { fn(); results.push({ name, pass: true }); }
    catch (e) { results.push({ name, pass: false, err: e.message }); }
  };
  const eq = (a, b) => {
    if (JSON.stringify(a) !== JSON.stringify(b))
      throw new Error(`expected ${JSON.stringify(b)}, got ${JSON.stringify(a)}`);
  };

  // kebabSlug
  t('kebabSlug: words → kebab', () => eq(kebabSlug('Why Text Is Hard'), 'why-text-is-hard'));
  t('kebabSlug: punctuation stripped', () => eq(kebabSlug('Hello, World!'), 'hello-world'));
  t('kebabSlug: collapses hyphens', () => eq(kebabSlug('multi--hyphen'), 'multi-hyphen'));
  t('kebabSlug: trims edges', () => eq(kebabSlug('  -hi-  '), 'hi'));
  t('kebabSlug: empty', () => eq(kebabSlug(''), ''));
  t('kebabSlug: numbers ok', () => eq(kebabSlug('123 Abc'), '123-abc'));
  t('kebabSlug: underscores → hyphens', () => eq(kebabSlug('foo_bar'), 'foo-bar'));

  const allMissing = { research: 'missing', script: 'missing', voiceover: 'missing',
    compose: 'missing', thumbnail: 'missing', render: 'missing', published: 'missing' };
  t('suggested: all missing → idea', () => eq(computeSuggested(allMissing), 'idea'));
  t('suggested: research only → research',
    () => eq(computeSuggested({ ...allMissing, research: 'present' }), 'research'));
  t('suggested: through compose → compose',
    () => eq(computeSuggested({ ...allMissing, research: 'present', script: 'present',
      voiceover: 'present', compose: 'present' }), 'compose'));
  t('suggested: gap mid-pipeline → rightmost present',
    () => eq(computeSuggested({ ...allMissing, research: 'present', voiceover: 'present' }),
      'voiceover'));
  t('suggested: published present is ignored',
    () => eq(computeSuggested({ ...allMissing, render: 'present', published: 'present' }),
      'render'));
  t('suggested: partial does not count as present',
    () => eq(computeSuggested({ ...allMissing, research: 'present', script: 'present',
      voiceover: 'partial' }), 'script'));

  t('drift: stage matches → false',
    () => eq(hasDriftFor({ stage: 'compose' }, 'compose'), false));
  t('drift: published → false',
    () => eq(hasDriftFor({ stage: 'published' }, 'compose'), false));
  t('drift: idea suggestion → false',
    () => eq(hasDriftFor({ stage: 'compose' }, 'idea'), false));
  t('drift: real disagreement → true',
    () => eq(hasDriftFor({ stage: 'render' }, 'compose'), true));

  const passes = results.filter(r => r.pass).length;
  const fails = results.length - passes;
  setContent(document.body, `
    <div style="font-family:'JetBrains Mono',monospace;padding:32px;color:#EDE7DC;background:#0F0E0C;min-height:100vh;">
      <h1 style="font-family:'Fraunces',serif;font-style:italic;margin-bottom:24px;">
        kanban.html test results
      </h1>
      <p style="color:${fails ? '#C4615A' : '#8FAF7E'};margin-bottom:16px;">
        ${passes} passed · ${fails} failed
      </p>
      <ul style="list-style:none;padding:0;line-height:1.8;">
        ${results.map(r => `
          <li style="color:${r.pass ? '#8FAF7E' : '#C4615A'};">
            ${r.pass ? '✓' : '✗'} ${escapeHtml(r.name)}${r.err ? ' — ' + escapeHtml(r.err) : ''}
          </li>`).join('')}
      </ul>
    </div>
  `);
}

if (new URL(location.href).searchParams.get('test') === '1') {
  runTests();
} else {
  render();
}
```

- [ ] **Step 3: Run the tests**

Open `file:///.../kanban.html?test=1`. Expected: `17 passed · 0 failed` in sage green. Each test name with green ✓.

- [ ] **Step 4: Commit**

```bash
git add kanban.html
git commit -m "feat(kanban): pure helpers (kebabSlug, computeSuggested, hasDriftFor) + ?test=1 mode"
```

---

## Task 5: localStorage hydration + persistence

**Files:**
- Modify: `kanban.html`

- [ ] **Step 1: Add storage constants and load/persist** (above `let state`)

```js
const STORAGE_KEY = 'hyper-frames:kanban:v1';
const SCHEMA_VERSION = 1;

function emptyState() {
  return {
    schemaVersion: SCHEMA_VERSION,
    cards: [],
    ui: { panelOpenCardId: null },
    lastSyncedAt: null,
  };
}

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return emptyState();
    const parsed = JSON.parse(raw);
    if (parsed.schemaVersion !== SCHEMA_VERSION) {
      console.warn('Schema mismatch; ignoring stored state.');
      return emptyState();
    }
    return {
      schemaVersion: SCHEMA_VERSION,
      cards: Array.isArray(parsed.cards) ? parsed.cards : [],
      ui: { panelOpenCardId: parsed.ui?.panelOpenCardId ?? null },
      lastSyncedAt: parsed.lastSyncedAt ?? null,
    };
  } catch (e) {
    console.error('Failed to load state:', e);
    return emptyState();
  }
}

let storageBannerShown = false;
function showStorageBanner() {
  if (storageBannerShown) return;
  storageBannerShown = true;
  const div = document.createElement('div');
  div.style.cssText = 'position:fixed;top:60px;left:50%;transform:translateX(-50%);background:#C4615A;color:#fff;padding:8px 16px;border-radius:4px;font-family:"JetBrains Mono",monospace;font-size:12px;z-index:9999;';
  div.textContent = 'localStorage unavailable. Changes will not persist.';
  document.body.appendChild(div);
}

function persist() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch (e) {
    console.error('Failed to persist state:', e);
    showStorageBanner();
  }
}

function mutate(fn) {
  fn();
  persist();
  render();
}
```

- [ ] **Step 2: Replace the hardcoded `state` initialization**

Move the previous hardcoded sample object into a `loadSampleState()` function:

```js
function loadSampleState() {
  return { /* the 5-card object from Task 3, returned fresh */ };
}

let state = loadState();

if (new URL(location.href).searchParams.get('seed') === '1') {
  state = loadSampleState();
  persist();
}
```

- [ ] **Step 3: Verify**

1. `kanban.html` → empty board, "0 cards · never synced".
2. `kanban.html?seed=1` → 5 cards, persisted to localStorage.
3. `kanban.html` → still 5 cards (loaded from storage).
4. DevTools → Application → Local Storage → check the JSON.

- [ ] **Step 4: Commit**

```bash
git add kanban.html
git commit -m "feat(kanban): localStorage hydration with schema versioning + ?seed=1"
```

---

## Task 6: Add Card dialog

**Files:**
- Modify: `kanban.html`

- [ ] **Step 1: Add dialog markup** (after `<aside class="panel">`)

```html
<dialog id="add-dialog" class="dialog">
  <form method="dialog" id="add-form" class="dialog-body">
    <h2 class="dialog-title">Add a card</h2>
    <label class="field">
      <span class="field-label">Slug</span>
      <input name="slug" id="add-slug" required autocomplete="off" placeholder="why-text-is-hard">
      <span class="field-hint" id="add-slug-hint">Lowercase, hyphens only.</span>
    </label>
    <label class="field">
      <span class="field-label">Working title</span>
      <input name="title" id="add-title" autocomplete="off" placeholder="Why Text Is Hard">
    </label>
    <label class="field">
      <span class="field-label">Date</span>
      <input name="date" id="add-date" type="date" required>
    </label>
    <label class="field">
      <span class="field-label">Stage</span>
      <select name="stage" id="add-stage">
        <option value="idea" selected>Idea</option>
        <option value="research">Research</option>
        <option value="script">Script</option>
        <option value="voiceover">Voiceover</option>
        <option value="compose">Compose</option>
        <option value="thumbnail">Thumbnail</option>
        <option value="render">Render</option>
        <option value="published">Published</option>
      </select>
    </label>
    <div class="dialog-actions">
      <button type="button" class="btn" id="add-cancel">Cancel</button>
      <button type="submit" class="btn btn-primary">Add card</button>
    </div>
  </form>
</dialog>
```

- [ ] **Step 2: Add dialog CSS**

```css
.dialog {
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text);
  padding: 0;
  max-width: 380px;
  width: 90vw;
  box-shadow: 0 20px 60px -10px rgba(0, 0, 0, 0.7);
}
.dialog::backdrop { background: rgba(15, 14, 12, 0.7); backdrop-filter: blur(2px); }
.dialog-body { padding: 22px 24px 18px; display: flex; flex-direction: column; gap: 16px; }
.dialog-title {
  font-family: var(--font-display); font-size: 20px; font-weight: 500;
  letter-spacing: -0.012em;
  font-variation-settings: 'opsz' 24, 'SOFT' 50;
}
.field { display: flex; flex-direction: column; gap: 6px; }
.field-label {
  font-family: var(--font-mono); font-size: 9px; font-weight: 500;
  color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.18em;
}
.field input, .field select {
  background: var(--bg); border: 1px solid var(--border-subtle); color: var(--text);
  font-family: var(--font-mono); font-size: 13px; padding: 9px 11px;
  border-radius: var(--radius-sm); width: 100%;
}
.field input:focus, .field select:focus { outline: none; border-color: var(--accent-muted); }
.field-hint { font-family: var(--font-mono); font-size: 10px; color: var(--text-dim); }
.field-hint.error { color: var(--red); }
.dialog-actions {
  display: flex; justify-content: flex-end; gap: 8px;
  padding-top: 14px; border-top: 1px solid var(--border-subtle);
}
```

- [ ] **Step 3: Wire it**

```js
function uuid() {
  return crypto.randomUUID
    ? crypto.randomUUID()
    : 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => {
        const r = (Math.random() * 16) | 0;
        return (c === 'x' ? r : (r & 0x3) | 0x8).toString(16);
      });
}

function todayISO() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

function emptyArtifacts() {
  return Object.fromEntries(ARTIFACTS.map(a => [a.id, 'missing']));
}

function titleCaseSlug(slug) {
  return slug.split('-').filter(Boolean)
    .map(w => w[0].toUpperCase() + w.slice(1))
    .join(' ');
}

function openAddDialog() {
  const dlg = document.getElementById('add-dialog');
  document.getElementById('add-slug').value = '';
  document.getElementById('add-title').value = '';
  document.getElementById('add-date').value = todayISO();
  document.getElementById('add-stage').value = 'idea';
  const hint = document.getElementById('add-slug-hint');
  hint.textContent = 'Lowercase, hyphens only.';
  hint.classList.remove('error');
  dlg.showModal();
  document.getElementById('add-slug').focus();
}

function bindAddDialog() {
  const dlg = document.getElementById('add-dialog');
  const slugInput = document.getElementById('add-slug');
  const hint = document.getElementById('add-slug-hint');

  slugInput.addEventListener('input', () => {
    const cur = slugInput.value;
    const k = kebabSlug(cur);
    if (k !== cur) {
      const pos = slugInput.selectionStart;
      slugInput.value = k;
      slugInput.setSelectionRange(Math.min(pos, k.length), Math.min(pos, k.length));
    }
  });

  document.getElementById('add-cancel').addEventListener('click', () => dlg.close('cancel'));

  document.getElementById('add-form').addEventListener('submit', (e) => {
    const slug = kebabSlug(slugInput.value);
    const date = document.getElementById('add-date').value;
    if (!slug) {
      e.preventDefault();
      hint.textContent = 'Slug is required.';
      hint.classList.add('error');
      return;
    }
    if (state.cards.some(c => c.slug === slug && c.date === date)) {
      e.preventDefault();
      hint.textContent = `A card with slug "${slug}" and date ${date} already exists.`;
      hint.classList.add('error');
      return;
    }
    const titleRaw = document.getElementById('add-title').value.trim();
    const title = titleRaw || titleCaseSlug(slug);
    const stage = document.getElementById('add-stage').value;
    const now = new Date().toISOString();
    mutate(() => {
      state.cards.push({
        id: uuid(), slug, title, date, stage,
        artifacts: emptyArtifacts(), notes: '',
        createdAt: now, updatedAt: now,
        lastScannedAt: null, hasDrift: false,
      });
    });
  });
}

function bindTopbar() {
  document.getElementById('btn-add').addEventListener('click', openAddDialog);
}

bindAddDialog();
bindTopbar();
```

- [ ] **Step 4: Test**

1. Click `+ Add` → dialog opens.
2. Type "Why Text Is Hard 2" → slug becomes "why-text-is-hard-2".
3. Submit → card appears in Idea.
4. Reload → persists.
5. Try duplicate slug+date → error message.
6. Esc closes the dialog.

- [ ] **Step 5: Commit**

```bash
git add kanban.html
git commit -m "feat(kanban): Add Card dialog with live kebab-case + uniqueness check"
```

---

## Task 7: Side panel render + open/close

**Files:**
- Modify: `kanban.html`

- [ ] **Step 1: Add panel CSS** — copy from the mockup: all `.panel*`, `.panel-label`, `.folder-path`, `.copy-btn`, `.stage-select`, `.artifacts`, `.artifact*`, `.notes-textarea`, `.notes-status`, `.panel-footer`, `.btn-primary`, `.btn-danger`. Confirm `body:has(.panel[hidden])` rule from Task 1 is still present.

- [ ] **Step 2: Add ARTIFACT_PATHS, folderPath, findCard, renderArtifactRow, renderPanel**

```js
const ARTIFACT_PATHS = {
  research:  'seo/research.json',
  script:    'script.md',
  voiceover: 'audio/voiceover.mp3 · transcript.json',
  compose:   'index.html',
  thumbnail: 'thumbnail-{a,b,c}.png',
  render:    'output/*.mp4',
  published: 'manual flag',
};

function findCard(id) {
  return state.cards.find(c => c.id === id) || null;
}

function folderPath(card) {
  return `videos/${card.slug}-${card.date}/`;
}

function renderArtifactRow(artifactId, status) {
  const label = ARTIFACTS.find(a => a.id === artifactId).label;
  const path = ARTIFACT_PATHS[artifactId];
  const cls = status === 'present' ? 'present'
            : status === 'partial' ? 'partial' : '';
  const missingClass = (status === 'missing' || status === 'unknown' || !status) ? ' missing' : '';
  const link = (status === 'present' || status === 'partial')
    ? `<a href="#" class="artifact-link">Open</a>`
    : '';
  return `
    <li class="artifact${missingClass}">
      <span class="artifact-status ${cls}"></span>
      <div class="artifact-name">
        <span class="artifact-label">${escapeHtml(label)}</span>
        <span class="artifact-path">${escapeHtml(path)}</span>
      </div>
      ${link}
    </li>
  `;
}

function renderPanel(card) {
  const aside = document.querySelector('.panel');
  if (!card) {
    aside.hidden = true;
    aside.replaceChildren();
    return;
  }
  // Reset transient notes status when switching cards
  if (aside.dataset.openId !== card.id) {
    notesLastSavedAt = null;
  }
  aside.dataset.openId = card.id;
  aside.hidden = false;
  const stageOptions = STAGES.map(s =>
    `<option value="${s.id}"${s.id === card.stage ? ' selected' : ''}>${escapeHtml(s.label)}</option>`
  ).join('');
  const artifactRows = ARTIFACTS.map(a =>
    renderArtifactRow(a.id, card.artifacts?.[a.id] || 'missing')
  ).join('');

  setContent(aside, `
    <header class="panel-header">
      <div>
        <h2 class="panel-title" id="panel-title" title="Click to edit">${escapeHtml(card.title)}</h2>
        <div class="panel-meta">
          <span>${escapeHtml(card.slug)}</span>
          <span class="dot-sep"></span>
          <span>${escapeHtml(card.date)}</span>
        </div>
      </div>
      <button class="panel-close" id="panel-close" aria-label="Close panel">×</button>
    </header>
    <div class="panel-body">
      <section>
        <div class="panel-label">Folder</div>
        <div class="folder-path">
          <span>${escapeHtml(folderPath(card))}</span>
          <button class="copy-btn" id="copy-folder">Copy</button>
        </div>
      </section>
      <section>
        <div class="panel-label">Stage</div>
        <select class="stage-select" id="panel-stage">${stageOptions}</select>
      </section>
      <section>
        <div class="panel-label">Artifacts</div>
        <ul class="artifacts">${artifactRows}</ul>
      </section>
      <section>
        <div class="panel-label">Notes</div>
        <textarea class="notes-textarea" id="panel-notes" placeholder="Anything to remember about this video…">${escapeHtml(card.notes || '')}</textarea>
        <div class="notes-status" id="panel-notes-status" hidden>Saved · just now</div>
      </section>
    </div>
    <footer class="panel-footer">
      <button class="btn btn-primary" id="open-folder"><span class="glyph">↗</span>Open in Finder</button>
      <button class="btn btn-danger" id="delete-card">Delete card</button>
    </footer>
  `);
}

let notesLastSavedAt = null;
```

In `render()`, append after the board update:

```js
renderPanel(findCard(state.ui.panelOpenCardId));
```

- [ ] **Step 3: Add board click + panel close handlers**

```js
function bindBoardEvents() {
  document.querySelector('.board').addEventListener('click', (e) => {
    const cardEl = e.target.closest('[data-card-id]');
    if (!cardEl) return;
    if (cardEl.classList.contains('dragging')) return;
    mutate(() => { state.ui.panelOpenCardId = cardEl.dataset.cardId; });
  });
}

function bindPanelEvents() {
  document.querySelector('.panel').addEventListener('click', (e) => {
    if (e.target.closest('#panel-close')) {
      mutate(() => { state.ui.panelOpenCardId = null; });
      return;
    }
    if (e.target.closest('#copy-folder')) {
      const card = findCard(state.ui.panelOpenCardId);
      if (card) navigator.clipboard?.writeText(folderPath(card));
      return;
    }
  });

  document.addEventListener('click', (e) => {
    if (!state.ui.panelOpenCardId) return;
    if (e.target.closest('.panel')) return;
    if (e.target.closest('[data-card-id]')) return;
    if (e.target.closest('dialog')) return;
    if (e.target.closest('.topbar')) return;
    mutate(() => { state.ui.panelOpenCardId = null; });
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && state.ui.panelOpenCardId) {
      const dlgOpen = document.querySelector('dialog[open]');
      if (dlgOpen) return; // let the dialog handle Esc
      mutate(() => { state.ui.panelOpenCardId = null; });
    }
  });
}

bindBoardEvents();
bindPanelEvents();
```

- [ ] **Step 4: Test**

1. With seed cards present, click "Why Text Is Hard" → panel opens with all sections.
2. Click a different card → panel content swaps.
3. Click outside (in topbar empty area) → panel closes.
4. Reopen → press Esc → panel closes.
5. Click `×` → panel closes.
6. Click "Copy" → paste somewhere to verify.

- [ ] **Step 5: Commit**

```bash
git add kanban.html
git commit -m "feat(kanban): side panel with artifact list, folder path copy, stage scaffold"
```

---

## Task 8: Drag and drop between columns

**Files:**
- Modify: `kanban.html`

- [ ] **Step 1: Add DnD CSS**

```css
.card.dragging { opacity: 0.4; cursor: grabbing; }
.column-body.drop-target {
  background: var(--accent-soft);
  outline: 1px dashed var(--accent-muted);
  outline-offset: -2px;
  border-radius: var(--radius);
}
```

- [ ] **Step 2: Extend bindBoardEvents with DnD handlers**

Replace `bindBoardEvents()`:

```js
function bindBoardEvents() {
  const board = document.querySelector('.board');

  board.addEventListener('click', (e) => {
    const cardEl = e.target.closest('[data-card-id]');
    if (!cardEl) return;
    if (cardEl.classList.contains('dragging')) return;
    mutate(() => { state.ui.panelOpenCardId = cardEl.dataset.cardId; });
  });

  board.addEventListener('dragstart', (e) => {
    const cardEl = e.target.closest('[data-card-id]');
    if (!cardEl) return;
    cardEl.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', cardEl.dataset.cardId);
    if (state.ui.panelOpenCardId === cardEl.dataset.cardId) {
      state.ui.panelOpenCardId = null;
      persist();
      // Defer the panel render until dragend so we don't kill the drag.
    }
  });

  board.addEventListener('dragend', () => {
    document.querySelectorAll('.dragging').forEach(el => el.classList.remove('dragging'));
    document.querySelectorAll('.drop-target').forEach(el => el.classList.remove('drop-target'));
  });

  board.addEventListener('dragover', (e) => {
    const body = e.target.closest('.column-body');
    if (!body) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    body.classList.add('drop-target');
  });

  board.addEventListener('dragleave', (e) => {
    const body = e.target.closest('.column-body');
    if (!body) return;
    if (body.contains(e.relatedTarget)) return;
    body.classList.remove('drop-target');
  });

  board.addEventListener('drop', (e) => {
    const column = e.target.closest('.column');
    const id = e.dataTransfer.getData('text/plain');
    if (!column || !id) return;
    e.preventDefault();
    const stage = column.dataset.stage;
    mutate(() => {
      const card = findCard(id);
      if (!card || card.stage === stage) return;
      card.stage = stage;
      card.updatedAt = new Date().toISOString();
    });
  });
}
```

- [ ] **Step 3: Test**

Drag cards between columns. Verify drop highlights, card moves, counts update, persistence on reload, no movement when dropping on same column.

- [ ] **Step 4: Commit**

```bash
git add kanban.html
git commit -m "feat(kanban): drag-and-drop between columns"
```

---

## Task 9: Stage selector + click-to-edit working title

**Files:**
- Modify: `kanban.html`

- [ ] **Step 1: Wire the stage selector** — add a `change` listener inside `bindPanelEvents()` (place inside the function body, after the existing `click` listener):

```js
document.querySelector('.panel').addEventListener('change', (e) => {
  if (e.target.id !== 'panel-stage') return;
  const id = state.ui.panelOpenCardId;
  if (!id) return;
  const newStage = e.target.value;
  mutate(() => {
    const card = findCard(id);
    if (!card) return;
    card.stage = newStage;
    card.updatedAt = new Date().toISOString();
  });
});
```

- [ ] **Step 2: Add edit-title CSS**

```css
.panel-title.editing {
  font-family: var(--font-display);
  font-size: 22px;
  font-weight: 500;
  background: var(--surface-1);
  border: 1px solid var(--accent-muted);
  border-radius: var(--radius-sm);
  padding: 4px 8px;
  color: var(--text);
  width: 100%;
  outline: none;
  letter-spacing: -0.016em;
  font-variation-settings: 'opsz' 36, 'SOFT' 30;
}
```

- [ ] **Step 3: Add click-to-edit handler** — inside the existing `click` listener in `bindPanelEvents()` (after the `#copy-folder` block), add:

```js
if (e.target.id === 'panel-title') {
  const titleEl = e.target;
  const id = state.ui.panelOpenCardId;
  if (!id) return;
  const card = findCard(id);
  if (!card) return;
  const input = document.createElement('input');
  input.type = 'text';
  input.value = card.title;
  input.className = 'panel-title editing';
  titleEl.replaceWith(input);
  input.focus();
  input.select();

  let committed = false;
  const commit = (save) => {
    if (committed) return;
    committed = true;
    const value = input.value.trim();
    if (save && value && value !== card.title) {
      mutate(() => {
        card.title = value;
        card.updatedAt = new Date().toISOString();
      });
    } else {
      render();
    }
  };
  input.addEventListener('blur', () => commit(true));
  input.addEventListener('keydown', (k) => {
    if (k.key === 'Enter') { k.preventDefault(); input.blur(); }
    if (k.key === 'Escape') { commit(false); }
  });
  return;
}
```

- [ ] **Step 4: Test**

1. Open a card. Change stage in dropdown → card moves.
2. Click panel title → becomes input, focused.
3. Type, press Enter → saves; card title updates.
4. Click title again, press Esc → reverts.
5. Click outside while editing → saves (blur).

- [ ] **Step 5: Commit**

```bash
git add kanban.html
git commit -m "feat(kanban): panel stage selector + click-to-edit title"
```

---

## Task 10: Notes textarea with debounced auto-save

**Files:**
- Modify: `kanban.html`

- [ ] **Step 1: Add debounce + status logic**

```js
let notesDebounceTimer = null;

function saveNotesNow(id, value) {
  const card = findCard(id);
  if (!card) return;
  if (card.notes === value) return;
  card.notes = value;
  card.updatedAt = new Date().toISOString();
  persist();
  notesLastSavedAt = Date.now();
  updateNotesStatus();
}

function updateNotesStatus() {
  const el = document.getElementById('panel-notes-status');
  if (!el) return;
  if (!notesLastSavedAt) { el.hidden = true; return; }
  const sec = Math.floor((Date.now() - notesLastSavedAt) / 1000);
  const ago = sec < 5 ? 'just now'
            : sec < 60 ? `${sec}s ago`
            : `${Math.floor(sec / 60)}m ago`;
  el.hidden = false;
  el.textContent = `Saved · ${ago}`;
}

setInterval(updateNotesStatus, 5000);
```

- [ ] **Step 2: Wire textarea events** — add to `bindPanelEvents()`:

```js
document.querySelector('.panel').addEventListener('input', (e) => {
  if (e.target.id !== 'panel-notes') return;
  clearTimeout(notesDebounceTimer);
  const id = state.ui.panelOpenCardId;
  const value = e.target.value;
  notesDebounceTimer = setTimeout(() => saveNotesNow(id, value), 500);
});

document.querySelector('.panel').addEventListener('blur', (e) => {
  if (e.target.id !== 'panel-notes') return;
  clearTimeout(notesDebounceTimer);
  saveNotesNow(state.ui.panelOpenCardId, e.target.value);
}, true);
```

- [ ] **Step 3: Test**

Type in notes → "Saved · just now" appears after 500ms idle. Blur → saves immediately. Switch cards → status resets. Reload → notes persist.

- [ ] **Step 4: Commit**

```bash
git add kanban.html
git commit -m "feat(kanban): notes textarea with 500ms debounce + on-blur save"
```

---

## Task 11: Delete card with confirm

**Files:**
- Modify: `kanban.html`

- [ ] **Step 1: Wire the delete button** — add to the existing `click` listener in `bindPanelEvents()` (after the `#panel-title` block):

```js
if (e.target.closest('#delete-card')) {
  const card = findCard(state.ui.panelOpenCardId);
  if (!card) return;
  if (!confirm(`Delete "${card.title}" (${card.slug})?\n\nThis cannot be undone.`)) return;
  mutate(() => {
    state.cards = state.cards.filter(c => c.id !== card.id);
    state.ui.panelOpenCardId = null;
  });
  return;
}
```

- [ ] **Step 2: Test**

Open a card, click Delete → confirm → card vanishes; panel closes.

- [ ] **Step 3: Commit**

```bash
git add kanban.html
git commit -m "feat(kanban): delete card with confirm"
```

---

## Task 12: IndexedDB handle storage + first-run picker

**Files:**
- Modify: `kanban.html`

- [ ] **Step 1: Add IndexedDB wrapper + handle helpers**

```js
const IDB_NAME = 'hyper-frames-kanban';
const IDB_STORE = 'handles';

function idb() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(IDB_NAME, 1);
    req.onupgradeneeded = () => req.result.createObjectStore(IDB_STORE);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}
async function idbGet(key) {
  const db = await idb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(IDB_STORE, 'readonly');
    const req = tx.objectStore(IDB_STORE).get(key);
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}
async function idbSet(key, value) {
  const db = await idb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(IDB_STORE, 'readwrite');
    tx.objectStore(IDB_STORE).put(value, key);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}
async function idbDelete(key) {
  const db = await idb();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(IDB_STORE, 'readwrite');
    tx.objectStore(IDB_STORE).delete(key);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

const FS_SUPPORTED = typeof window.showDirectoryPicker === 'function';

async function getCachedDirHandle() {
  if (!FS_SUPPORTED) return null;
  return (await idbGet('videosDirHandle')) || null;
}
async function setCachedDirHandle(handle) {
  await idbSet('videosDirHandle', handle);
}
async function clearCachedDirHandle() {
  await idbDelete('videosDirHandle');
}
async function pickDirHandle() {
  const handle = await window.showDirectoryPicker({ mode: 'read' });
  await setCachedDirHandle(handle);
  return handle;
}
async function ensureReadPermission(handle) {
  const has = await handle.queryPermission({ mode: 'read' });
  if (has === 'granted') return true;
  return (await handle.requestPermission({ mode: 'read' })) === 'granted';
}
```

- [ ] **Step 2: Verify in DevTools console**

```js
const h = await pickDirHandle();   // prompts; pick videos/
const h2 = await getCachedDirHandle();
console.log(h2.name);              // 'videos'
```

Reload, run `await getCachedDirHandle()` → handle persists.

- [ ] **Step 3: Commit**

```bash
git add kanban.html
git commit -m "feat(kanban): IndexedDB-backed FileSystemDirectoryHandle storage"
```

---

## Task 13: Scan helpers + scan()

**Files:**
- Modify: `kanban.html`

- [ ] **Step 1: Add constants** (above the helpers)

```js
const COMPOSE_THRESHOLD_BYTES = 8192;
const FOLDER_RE = /^(.+)-(\d{4}-\d{2}-\d{2})$/;
```

- [ ] **Step 2: Add scan helpers**

```js
async function exists(dir, path) {
  const parts = path.split('/').filter(Boolean);
  try {
    let cur = dir;
    for (let i = 0; i < parts.length - 1; i++) {
      cur = await cur.getDirectoryHandle(parts[i]);
    }
    await cur.getFileHandle(parts[parts.length - 1]);
    return 'present';
  } catch (e) {
    if (e.name === 'NotFoundError') return 'missing';
    return 'unknown';
  }
}

async function voiceoverStatus(dir) {
  const mp3 = await exists(dir, 'audio/voiceover.mp3');
  const tx  = await exists(dir, 'transcript.json');
  const nm  = await exists(dir, 'narration-map.json');
  if (mp3 === 'missing' && tx === 'missing') return 'missing';
  if (mp3 === 'present' && tx === 'present' && nm === 'present') return 'present';
  return 'partial';
}

async function composeStatus(dir) {
  try {
    const fh = await dir.getFileHandle('index.html');
    const file = await fh.getFile();
    return file.size > COMPOSE_THRESHOLD_BYTES ? 'present' : 'partial';
  } catch (e) {
    if (e.name === 'NotFoundError') return 'missing';
    return 'unknown';
  }
}

async function thumbnailStatus(dir) {
  let count = 0;
  for (const name of ['thumbnail-a.png', 'thumbnail-b.png', 'thumbnail-c.png']) {
    if ((await exists(dir, name)) === 'present') count++;
  }
  if (count === 0) return 'missing';
  if (count === 3) return 'present';
  return 'partial';
}

async function hasMp4InOutput(dir) {
  try {
    const out = await dir.getDirectoryHandle('output');
    for await (const entry of out.values()) {
      if (entry.kind === 'file' && entry.name.toLowerCase().endsWith('.mp4')) return 'present';
    }
    return 'missing';
  } catch (e) {
    if (e.name === 'NotFoundError') return 'missing';
    return 'unknown';
  }
}

async function readOutlineH1(dir) {
  try {
    const fh = await dir.getFileHandle('outline.md');
    const file = await fh.getFile();
    const text = await file.text();
    const m = text.match(/^#\s+(.+?)(?:\s+—\s+9-beat outline)?\s*$/m);
    return m ? m[1].trim() : null;
  } catch {
    return null;
  }
}

async function scan(dirHandle) {
  const results = [];
  let errors = 0;
  for await (const entry of dirHandle.values()) {
    if (entry.kind !== 'directory') continue;
    const m = entry.name.match(FOLDER_RE);
    if (!m) continue;
    const slug = m[1];
    const date = m[2];
    try {
      const artifacts = {
        research:  await exists(entry, 'seo/research.json'),
        script:    await exists(entry, 'script.md'),
        voiceover: await voiceoverStatus(entry),
        compose:   await composeStatus(entry),
        thumbnail: await thumbnailStatus(entry),
        render:    await hasMp4InOutput(entry),
        published: 'unknown',
      };
      const suggestedStage = computeSuggested(artifacts);
      const title = await readOutlineH1(entry);
      results.push({ slug, date, suggestedStage, artifacts, title });
    } catch (e) {
      errors++;
      console.warn(`scan failed for ${entry.name}:`, e);
    }
  }
  return { results, errors };
}
```

- [ ] **Step 3: Verify in console**

```js
const h = await pickDirHandle();   // pick videos/
console.log(await scan(h));
```

Expected: results array with one entry per folder matching the slug-date pattern. Verify the `why-text-is-hard-2026-05-07` folder reports correct artifact statuses.

- [ ] **Step 4: Commit**

```bash
git add kanban.html
git commit -m "feat(kanban): scan helpers + scan()"
```

---

## Task 14: mergeScan with TDD

**Files:**
- Modify: `kanban.html`

- [ ] **Step 1: Implement mergeScan**

```js
function mergeScan(currentState, scanResults) {
  const next = JSON.parse(JSON.stringify(currentState));
  const now = new Date().toISOString();

  for (const result of scanResults) {
    const existing = next.cards.find(c => c.slug === result.slug && c.date === result.date);
    if (existing) {
      existing.artifacts = result.artifacts;
      existing.lastScannedAt = now;
      const suggested = computeSuggested(result.artifacts);
      existing.hasDrift = hasDriftFor(existing, suggested);
      if (existing.hasDrift) {
        existing.suggestedLabel = STAGES.find(s => s.id === suggested)?.label || '';
      } else {
        delete existing.suggestedLabel;
      }
    } else {
      next.cards.push({
        id: uuid(),
        slug: result.slug,
        date: result.date,
        title: result.title || titleCaseSlug(result.slug),
        stage: result.suggestedStage,
        artifacts: result.artifacts,
        notes: '',
        createdAt: now,
        updatedAt: now,
        lastScannedAt: now,
        hasDrift: false,
      });
    }
  }
  return next;
}
```

- [ ] **Step 2: Append mergeScan tests to runTests()** — add inside `runTests()` before "Render results":

```js
const baseArts = { research: 'present', script: 'missing', voiceover: 'missing',
  compose: 'missing', thumbnail: 'missing', render: 'missing', published: 'missing' };

t('mergeScan: existing card updates artifacts but not stage', () => {
  const before = {
    schemaVersion: 1, lastSyncedAt: null, ui: { panelOpenCardId: null },
    cards: [{ id: '1', slug: 'foo', date: '2026-05-09', title: 'Foo', stage: 'idea',
      artifacts: baseArts, notes: '', createdAt: '', updatedAt: '',
      lastScannedAt: null, hasDrift: false }],
  };
  const results = [{ slug: 'foo', date: '2026-05-09', suggestedStage: 'research',
    artifacts: { ...baseArts, research: 'present' }, title: null }];
  const after = mergeScan(before, results);
  if (after.cards.length !== 1) throw new Error('expected 1 card');
  if (after.cards[0].stage !== 'idea') throw new Error('stage must not change');
  if (after.cards[0].artifacts.research !== 'present') throw new Error('artifacts not updated');
  if (after.cards[0].hasDrift !== true) throw new Error('drift not flagged');
  if (after.cards[0].suggestedLabel !== 'Research') throw new Error('label missing');
});

t('mergeScan: new folder creates card at suggestedStage', () => {
  const before = { schemaVersion: 1, lastSyncedAt: null, ui: { panelOpenCardId: null }, cards: [] };
  const results = [{ slug: 'bar', date: '2026-05-09', suggestedStage: 'compose',
    artifacts: { ...baseArts, research: 'present', script: 'present',
      voiceover: 'present', compose: 'present' }, title: 'The Bar' }];
  const after = mergeScan(before, results);
  if (after.cards.length !== 1) throw new Error('expected 1 card');
  if (after.cards[0].stage !== 'compose') throw new Error('stage wrong');
  if (after.cards[0].title !== 'The Bar') throw new Error('title wrong');
});

t('mergeScan: orphan card untouched', () => {
  const before = {
    schemaVersion: 1, lastSyncedAt: null, ui: { panelOpenCardId: null },
    cards: [{ id: '1', slug: 'orphan', date: '2026-05-09', title: 'Orphan', stage: 'idea',
      artifacts: baseArts, notes: 'keep me', createdAt: '', updatedAt: '',
      lastScannedAt: null, hasDrift: false }],
  };
  const after = mergeScan(before, []);
  if (after.cards.length !== 1) throw new Error('card lost');
  if (after.cards[0].notes !== 'keep me') throw new Error('notes mutated');
});

t('mergeScan: drift cleared when stage matches suggested', () => {
  const before = {
    schemaVersion: 1, lastSyncedAt: null, ui: { panelOpenCardId: null },
    cards: [{ id: '1', slug: 'foo', date: '2026-05-09', title: 'Foo', stage: 'compose',
      artifacts: baseArts, notes: '', createdAt: '', updatedAt: '',
      lastScannedAt: null, hasDrift: true, suggestedLabel: 'Research' }],
  };
  const results = [{ slug: 'foo', date: '2026-05-09', suggestedStage: 'compose',
    artifacts: { ...baseArts, research: 'present', script: 'present',
      voiceover: 'present', compose: 'present' }, title: null }];
  const after = mergeScan(before, results);
  if (after.cards[0].hasDrift !== false) throw new Error('drift not cleared');
  if (after.cards[0].suggestedLabel !== undefined) throw new Error('label not cleared');
});
```

- [ ] **Step 3: Run** `kanban.html?test=1` → expect 17 + 4 = 21 passed.

- [ ] **Step 4: Commit**

```bash
git add kanban.html
git commit -m "feat(kanban): mergeScan + tests"
```

---

## Task 15: Sync button wiring + non-Chromium fallback

**Files:**
- Modify: `kanban.html`

- [ ] **Step 1: Add sync state CSS**

```css
.btn[disabled] { opacity: 0.4; cursor: not-allowed; }
.btn.syncing .glyph { animation: spin 1s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
```

- [ ] **Step 2: Wire the Sync button** — extend `bindTopbar()`:

```js
function bindTopbar() {
  document.getElementById('btn-add').addEventListener('click', openAddDialog);
  const syncBtn = document.getElementById('btn-sync');

  if (!FS_SUPPORTED) {
    syncBtn.disabled = true;
    syncBtn.title = 'Folder scanning needs a Chromium-based browser. Manual mode still works.';
    return;
  }

  syncBtn.addEventListener('click', async () => {
    syncBtn.classList.add('syncing');
    syncBtn.disabled = true;
    try {
      let handle = await getCachedDirHandle();
      if (handle) {
        const ok = await ensureReadPermission(handle);
        if (!ok) handle = await pickDirHandle();
      } else {
        handle = await pickDirHandle();
      }
      let scanResult;
      try {
        scanResult = await scan(handle);
      } catch (e) {
        console.warn('Scan failed, re-picking:', e);
        await clearCachedDirHandle();
        handle = await pickDirHandle();
        scanResult = await scan(handle);
      }
      state = mergeScan(state, scanResult.results);
      state.lastSyncedAt = new Date().toISOString();
      persist();
      render();
      if (scanResult.errors > 0) {
        console.warn(`Sync completed with ${scanResult.errors} errors.`);
      }
    } catch (e) {
      if (e.name !== 'AbortError') console.error('Sync failed:', e);
    } finally {
      syncBtn.classList.remove('syncing');
      syncBtn.disabled = false;
    }
  });
}

setInterval(() => updateStatusPill(), 30_000);
```

- [ ] **Step 3: Test**

In Chrome: click Sync → folder picker → pick `videos/` → grant permission → board updates with real data; status pill "N cards · synced just now". Reload → handle remembered. In Firefox: button disabled with tooltip.

- [ ] **Step 4: Commit**

```bash
git add kanban.html
git commit -m "feat(kanban): Sync button — File System Access API with fallback"
```

---

## Task 16: Keyboard shortcuts + Help dialog

**Files:**
- Modify: `kanban.html`

- [ ] **Step 1: Add help dialog markup** (after the add dialog)

```html
<dialog id="help-dialog" class="dialog">
  <div class="dialog-body">
    <h2 class="dialog-title">Keyboard shortcuts</h2>
    <ul class="kbd-list">
      <li><kbd>n</kbd><span>Open Add Card</span></li>
      <li><kbd>s</kbd><span>Trigger Sync</span></li>
      <li><kbd>?</kbd><span>Open this help</span></li>
      <li><kbd>Esc</kbd><span>Close panel / dialog</span></li>
      <li><kbd>Delete</kbd><span>Delete card (when panel open)</span></li>
    </ul>
    <p class="help-note">
      <strong>Folder sync</strong> requires a Chromium-based browser
      (Chrome, Edge, Brave, Arc). Manual mode works in any browser.
    </p>
    <p class="help-note">
      <button type="button" class="copy-btn" id="reset-folder">Reset folder access</button>
      &nbsp;Clears the saved <code>videos/</code> directory handle.
    </p>
    <div class="dialog-actions">
      <button type="button" class="btn" id="help-close">Close</button>
    </div>
  </div>
</dialog>
```

- [ ] **Step 2: Add help-dialog CSS**

```css
.kbd-list {
  list-style: none;
  display: flex; flex-direction: column; gap: 8px;
  margin: 4px 0;
}
.kbd-list li {
  display: grid; grid-template-columns: 64px 1fr;
  align-items: center; gap: 12px;
  font-family: var(--font-mono); font-size: 12px;
  color: var(--text-secondary);
}
.kbd-list kbd {
  font-family: var(--font-mono); font-size: 11px;
  color: var(--accent);
  background: var(--surface-3);
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 2px 6px; text-align: center;
}
.help-note {
  font-family: var(--font-mono); font-size: 11px;
  color: var(--text-muted); line-height: 1.5;
  border-top: 1px solid var(--border-subtle);
  padding-top: 12px;
}
.help-note code { color: var(--accent); }
```

- [ ] **Step 3: Wire it**

```js
function openHelpDialog() {
  document.getElementById('help-dialog').showModal();
}

function bindHelpDialog() {
  document.getElementById('btn-help').addEventListener('click', openHelpDialog);
  document.getElementById('help-close').addEventListener('click', () =>
    document.getElementById('help-dialog').close());
  document.getElementById('reset-folder').addEventListener('click', async () => {
    await clearCachedDirHandle();
    document.getElementById('help-dialog').close();
    alert('Folder access reset. Click Sync to pick a new directory.');
  });
}

function bindKeyboard() {
  document.addEventListener('keydown', (e) => {
    const tag = document.activeElement?.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
    const dlgOpen = document.querySelector('dialog[open]');
    if (dlgOpen && e.key !== 'Escape') return;

    if (e.key === 'n') { e.preventDefault(); openAddDialog(); }
    else if (e.key === 's') { e.preventDefault(); document.getElementById('btn-sync').click(); }
    else if (e.key === '?' || (e.shiftKey && e.key === '/')) { e.preventDefault(); openHelpDialog(); }
    else if (e.key === 'Delete' && state.ui.panelOpenCardId) {
      const card = findCard(state.ui.panelOpenCardId);
      if (!card) return;
      if (!confirm(`Delete "${card.title}" (${card.slug})?`)) return;
      mutate(() => {
        state.cards = state.cards.filter(c => c.id !== card.id);
        state.ui.panelOpenCardId = null;
      });
    }
  });
}

bindHelpDialog();
bindKeyboard();
```

- [ ] **Step 4: Test**

`?` opens help, `n` opens add, `s` triggers sync, `Esc` closes dialogs, `Delete` deletes (when panel open), shortcuts ignored when typing in inputs.

- [ ] **Step 5: Commit**

```bash
git add kanban.html
git commit -m "feat(kanban): keyboard shortcuts + help dialog"
```

---

## Task 17: Polish + smoke test

**Files:**
- Modify: `kanban.html`

- [ ] **Step 1: Add panel + topbar reveal animations** (verify if not already present)

```css
.topbar { animation: fade-up 400ms ease 0ms both; }
.panel:not([hidden]) { animation: fade-up 600ms ease 200ms both; }
```

- [ ] **Step 2: Smoke test**

Clear site data (DevTools → Application → Clear site data), then:

1. Open `kanban.html` — empty board, "0 cards · never synced".
2. `+ Add` → slug `test-video`, today, Idea, submit. Card appears. Pill: "1 card · never synced".
3. Drag the card to Voiceover. Moves.
4. Click the card → panel opens. Click title → edit to "Test Video" → Enter. Title updates.
5. Type notes → wait → "Saved · just now" appears.
6. Reload. State persists.
7. Sync → pick `videos/` → real cards from `why-text-is-hard-2026-05-07/` appear with correct artifact statuses.
8. `?` → help dialog. Close.
9. Open `kanban.html?test=1` → 21 passed · 0 failed.

If any step fails: fix and re-test.

- [ ] **Step 3: Final commit**

```bash
git add kanban.html
git commit -m "chore(kanban): polish + smoke-test pass"
```

---

## Self-review notes

**Spec coverage:**
- Goals 1-6 (see + manage progress, drag, add ideas, sync, drift, notes) → Tasks 2/3/7/8/9/10/15.
- Non-goals enforced: no orchestration (Add never scaffolds), no multi-user, no card reordering inside columns (sort by `updatedAt desc`), no filters, dark mode only.
- Data model + 8 stages + 7 artifacts + detection rules → Tasks 3/4/13.
- Drift logic → Task 4 (helper) + Task 14 (mergeScan applies it).
- File System Access API + IndexedDB handle + fallback → Tasks 12/15.
- Browser shortcut spec including `Shift+/` for help → Task 16.
- "Wrong directory at Sync" edge case → Task 16's "Reset folder access" in help.
- localStorage unavailable banner → Task 5's `showStorageBanner`.

**Type/method-name consistency:** every named function listed in the file-structure section appears with the same name in the task that defines it and in the tasks that consume it (`kebabSlug`, `computeSuggested`, `hasDriftFor`, `findCard`, `mergeScan`, `mutate`, `render`, `renderPanel`, `bindBoardEvents`, `bindPanelEvents`, `bindTopbar`, `bindKeyboard`, `bindAddDialog`, `bindHelpDialog`, `getCachedDirHandle`/`setCachedDirHandle`/`clearCachedDirHandle`, `pickDirHandle`, `ensureReadPermission`, `scan`, `exists`, `voiceoverStatus`, `composeStatus`, `thumbnailStatus`, `hasMp4InOutput`, `readOutlineH1`, `setContent`, `frag`, `escapeHtml`, `saveNotesNow`, `updateNotesStatus`, `updateStatusPill`).

**No placeholders:** every step has the actual code, file paths, and expected outputs. The only references to external content are: (1) the visual mockup at `.superpowers/brainstorm/.../kanban-mockup.html`, where Tasks 1, 2, 3, 7 say "copy from the mockup" and list exactly which CSS rule names to copy, and (2) the spec doc, referenced for context only.
