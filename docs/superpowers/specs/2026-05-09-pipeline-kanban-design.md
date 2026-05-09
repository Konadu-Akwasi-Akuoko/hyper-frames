# Pipeline Kanban — Design Spec

**Date:** 2026-05-09
**Status:** Draft (pending user review)
**Owner:** akwasikonaduakuoko

## Purpose

A single-file HTML Kanban board, served from `kanban.html` at the repo root, that tracks every video in `videos/` through the production pipeline. The Kanban is **observability, not orchestration** — it tracks state, it does not run skills. Skills (`youtube-seo-research`, `script-writer`, `voiceover-elevenlabs`, `thumbnail-creator`, etc.) are invoked from the terminal as usual; the Kanban watches the resulting artifacts.

State persists in `localStorage`, scoped under a versioned namespace. An optional file-system scan (Chromium-only) reads `videos/` to auto-suggest stages and surface drift, but the user's manual placement always wins.

## Goals

1. See every video at a glance, partitioned by pipeline stage.
2. See artifact-level sub-progress on every card without opening it (the 7 progress dots).
3. Move cards manually (drag/drop or stage selector in the panel).
4. Add new ideas before the folder exists; let them sit in `Idea` until research begins.
5. Sync with disk on demand: detect new folders, refresh artifact status, surface drift between manual placement and what the filesystem suggests.
6. Make written notes per video (e.g. "Scene 4 voiceover needs redo before render").

## Non-goals

- No orchestration. Adding a card does **not** scaffold the folder, run a skill, or trigger anything beyond updating localStorage. (The pipeline-entry skills already self-bootstrap their folders idempotently — see `youtube-seo-research`, `script-writer`, `thumbnail-creator`.)
- No multi-user, no cloud sync, no shared backend. localStorage only.
- No card reordering inside a column. Cards within a column sort by `updatedAt desc` automatically.
- No filters, search, or settings page in v1.
- No editing of stage definitions or artifact rules in the UI. Those are constants in the source.

## Architecture

### File layout

One file at the repo root: `kanban.html`. No build step, no `node_modules`, no CDN dependencies for JS (Google Fonts CDN is acceptable for `Fraunces` + `JetBrains Mono`; if offline-first becomes a concern, the fonts can be vendored).

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

### Code organization (inside the IIFE)

1. `STAGES` — the 8-stage enum, in pipeline order.
2. `ARTIFACTS` — the 7 detectable artifacts (one per stage except `idea`), with detection rules.
3. `state` — the in-memory model, hydrated from localStorage on boot.
4. `persist()` — serialize `state` to localStorage on every mutation.
5. `render()` — re-render `<main>` and `<aside>` from state. Cheap at this scale (≤ ~100 cards expected).
6. `bindEvents()` — drag/drop, click, "+" submit, "Sync" click, delete, save-notes, keyboard shortcuts.
7. `scan()` — File System Access API directory walk; returns scan results.
8. `mergeScan(results)` — apply scan results without overriding manual placements.
9. `dirHandleStore` — IndexedDB wrapper for the `FileSystemDirectoryHandle` (localStorage cannot hold it).

### Data model

**localStorage key:** `hyper-frames:kanban:v1`

```ts
{
  schemaVersion: 1,
  cards: [
    {
      id: "uuid-v4",                  // crypto.randomUUID()
      slug: "why-text-is-hard",       // matches videos/<slug>-<date>/ folder
      date: "2026-05-07",             // YYYY-MM-DD
      title: "Why Text Is Hard",      // working title (editable)
      stage: "compose",               // one of the 8 STAGES
      notes: "Scene 4 voiceover needs redo…",
      artifacts: {
        research:  "present" | "missing" | "partial" | "unknown",
        script:    "...",
        voiceover: "...",   // rolls in narration: partial = mp3+transcript only; present = +narration-map
        compose:   "...",
        thumbnail: "...",
        render:    "...",
        published: "...",   // manual flag; never auto-detected
      },
      lastScannedAt: "2026-05-09T14:22:18Z" | null,
      createdAt:     "2026-05-07T09:01:02Z",
      updatedAt:     "2026-05-09T14:22:18Z"
    }
  ],
  ui: {
    panelOpenCardId: null
  }
}
```

### Stages (fixed enum, in order)

```
idea → research → script → voiceover → compose → thumbnail → render → published
```

### Artifact detection rules (used by scan + dot rendering)

| Stage      | Detection rule                                                                                          | Status mapping                                  |
|------------|---------------------------------------------------------------------------------------------------------|-------------------------------------------------|
| research   | `seo/research.json` exists                                                                              | present / missing                               |
| script     | `script.md` exists                                                                                      | present / missing                               |
| voiceover  | `audio/voiceover.mp3` AND `transcript.json` exist; `narration-map.json` may also exist                  | missing if neither core file; partial if mp3+transcript but no narration-map; present if all three |
| compose    | `index.html` exists AND `index.html` size > 8 KB                                                        | partial if exists but ≤ 8 KB (init scaffold only); present if > 8 KB |
| thumbnail  | `thumbnail-a.png`, `thumbnail-b.png`, `thumbnail-c.png` presence count                                  | missing if 0; partial if 1-2; present if 3      |
| render     | any `*.mp4` inside `output/`                                                                            | present / missing                               |
| published  | manual flag (no on-disk artifact)                                                                       | always `unknown` from scan; user toggles via stage selector / drag |

The 8-KB threshold for `compose` distinguishes a freshly-`init`'d scaffold (~5 KB) from a real composition. A future enhancement could swap in a more semantic check (e.g. presence of a non-default block in `compositions/`).

### Suggested-stage logic

The scan computes a `suggestedStage` per folder:

> The rightmost stage in `STAGES` whose artifact is `present`. If none are `present`, fall back to `idea`. The `published` stage is never auto-suggested — it requires manual placement.

### Drift detection

```
hasDrift =
  suggestedStage !== card.stage
  AND card.stage !== 'published'
  AND suggestedStage !== 'idea'  // don't flag "scan suggests no progress yet" as drift
```

When `hasDrift` is true, the card renders the amber drift glyph (top-right) with a tooltip:
`"Scan suggests: <suggestedStage>"`.

## UI

### Layout

```
┌──────────────────────────────────────────────────────────┐
│  TOPBAR — 52px tall, sticky                              │
│  brand · Pipeline           status-pill   + Add  ↻ Sync ?│
├────────────────────────────────────┬─────────────────────┤
│  BOARD (8 columns, horizontal)     │  PANEL (400px)      │
│  ┌──┬──┬──┬──┬──┬──┬──┬──┐         │  (hidden when no    │
│  │c │c │  │c │c │c │c │c │         │   card open)        │
│  │c │  │  │c │c │  │c │  │         │                     │
│  │  │  │  │c │  │  │  │  │         │                     │
│  └──┴──┴──┴──┴──┴──┴──┴──┘         │                     │
│  Idea Res Scr Voi Com Thu Ren Pub  │                     │
└────────────────────────────────────┴─────────────────────┘
```

When the panel is closed, it collapses to 0 width and the board takes the full viewport. When open it's pinned at 400px on the right.

### Topbar (52px)

- Brand mark (3 stacked SVG bars, copper, fading downward)
- `hyper-frames` (Fraunces italic) + `Pipeline` (mono, uppercase, tracked)
- Right side: status pill (`12 cards · synced 4m ago` with leading green dot), `+ Add`, `↻ Sync`, `?` icon button
- Hairline copper gradient scan line on the top edge

### Columns (each 210px wide, 6px gap)

- Sticky column header: stage name (mono, uppercase, tracked, muted) + count badge (mono pill)
- Column header has a `linear-gradient` background fading from `--bg` to transparent + `backdrop-filter: blur(6px)` so cards scroll cleanly under it
- Body scrolls vertically when overflowing
- Subtle vertical "ghost rule" between columns (single-pixel gradient, fades at top/bottom) instead of hard borders
- Empty columns render an italic Fraunces caption inside a dashed-border placeholder ("No drafts in flight.")

### Card

- `cursor: grab` (`grabbing` while dragging)
- Top row: slug (mono, dim, ellipsizes) + drift glyph (right-aligned, only when `hasDrift`)
- Title: Fraunces 500, opsz 14, SOFT 50, ~15px
- Date: mono, 10px, faded
- 7 dots: 7px diameter, 5px gap, three states:
  - `missing`: hollow ring (1px stroke, faded)
  - `partial`: filled amber, 2-pixel amber-soft halo, 2.4s breath animation
  - `present`: filled sage
- Hover: border lifts, background lightens to surface-2, dots scale 1.08x
- The card matching `state.ui.panelOpenCardId` gets a copper-rail accent (`is-open` class)

### Side panel (400px)

- Header: panel title (Fraunces 22, opsz 36, SOFT 30) + slug · date meta + close button
- Body sections, gap 24px:
  1. **Folder** — mono path with copy button
  2. **Stage** — `<select>` dropdown (Fraunces option text, custom chevron)
  3. **Artifacts** — 7-row list, each row: status dot · label (Fraunces) + path (mono) · `Open` link (right-aligned, copper). Missing rows render in italic dim text with no link.
  4. **Notes** — Fraunces textarea, auto-saves on blur (500ms debounce on input). Status row below: green dot + `Saved · Ns ago`.
- Footer: `Open in Finder` (primary, copper) + `Delete card` (danger, muted brick).

### Add Card dialog

- Native `<dialog>` element
- Slug input (live kebab-case as user types)
- Working title input (optional; defaults to title-cased slug on submit)
- Date picker (default = today)
- Stage dropdown (default = `idea`)
- Submit creates card, closes dialog, panel does not auto-open
- Esc / backdrop click cancels

### Help dialog

- Native `<dialog>`
- Lists keyboard shortcuts (see Interactions §)
- One-paragraph note on browser support (File System Access API → Chromium only)
- Reachable via `?` button in topbar OR `Shift+/` keybind

### Visual style

**Palette:**
- `--bg: #0F0E0C` (warm charcoal, never pure black)
- Surfaces ladder: `#131210` → `#1A1815` → `#221F1B` → `#2B2723`
- Border ladder: `#2A2723` → `#3A3631` → `#4D4842`
- Text ladder: `#EDE7DC` → `#B5AC9D` → `#8A8278` → `#5C544A` → `#3F3934`
- Accent (copper): `#D4A574` (one strategic accent — used sparingly: brand mark, scan line, primary button, links, currently-open card edge)
- Amber: `#E0A050` (partial dot, drift glyph)
- Sage: `#8FAF7E` (present dot, status indicator)
- Brick: `#C4615A` (delete; never alarming red)

**Type:**
- **Fraunces** (variable, opsz 9-144, weight 300-700, SOFT 30-100): titles, panel header, notes, empty placeholders, artifact labels, brand-name (italic). The "content" voice.
- **JetBrains Mono** (400-600): all chrome — buttons, slugs, dates, paths, labels, status pill, stage names, counts. The "tool" voice.
- The serif/mono split is semantic: serif for content the user wrote, mono for the system speaking.

**Atmospheric details:**
- Background SVG turbulence at 2.5% opacity, overlay blend mode — adds tooth to the dark surface
- 1px copper gradient scan line at the top of the page; fainter echo at the top of the panel
- Page-load reveal: columns fade-up in sequence with 60ms stagger; panel fades in last
- All transitions 120-180ms, ease curves only — never bouncy

The visual mockup at `.superpowers/brainstorm/27329-1778293267/content/kanban-mockup.html` is the canonical reference. Implementation should match it pixel-for-pixel except for legitimate refinements caught during build.

## Interactions

### Add card

1. `+` button or `n` key opens the add-dialog.
2. Slug field live-kebabs on input (lowercase, hyphenate spaces, strip non-`[a-z0-9-]`).
3. Submit validates: slug non-empty, slug unique within `state.cards`. On failure, inline error.
4. Create card with the chosen stage (default `idea`), `artifacts` all `unknown`, `id = crypto.randomUUID()`.
5. `persist()` → `render()` → close dialog. Panel does not auto-open.
6. Esc / backdrop / cancel button cancels.

### Drag and drop (HTML5 DnD)

- `dragstart`: stash card.id in `dataTransfer`, add `.dragging` class. If the panel is showing this card, close the panel.
- `dragover` on column body: `preventDefault()` + add `.drop-target` highlight.
- `dragleave`: remove highlight.
- `drop`: read card.id, set `card.stage = column.stage`, update `updatedAt`, `persist()`, `render()`.
- `dragend`: remove `.dragging` regardless of drop outcome.
- No reordering within a column. Cards in a column sort `updatedAt desc`.

### Click card → side panel

- Click on card body opens the panel: set `state.ui.panelOpenCardId`, `persist()`, `render()`.
- Click on a different card swaps panel content (same render cycle).
- Click panel `×`, click outside the panel, or press `Esc` closes the panel (`panelOpenCardId = null`).
- The panel does not block the board — clicks on cards/columns still work.

### Stage dropdown in panel

- Same effect as drag: updates `card.stage`, `updatedAt`, `persist()`, `render()`.

### Edit working title

- Click the title in the panel → swaps to `<input>`. `Enter` or blur saves; `Esc` reverts.

### Notes textarea

- Auto-save on blur. On input: debounce 500ms then persist (so rapid typing doesn't thrash localStorage).
- Status row shows `Saved · Ns ago` with a green dot. The `N seconds ago` ticker updates every 30 seconds.

### Delete card

- Red footer button → native `confirm()` → on yes: splice from `state.cards`, set `panelOpenCardId = null`, `persist()`, `render()`. No undo in v1.

### Sync (header button)

1. **First click ever:** call `showDirectoryPicker({ mode: 'read', startIn: 'documents' })`. User picks `videos/`. Browser may prompt for permission. On grant: write the `FileSystemDirectoryHandle` to IndexedDB under key `videosDirHandle`. Run scan.
2. **Subsequent clicks:** read cached handle from IndexedDB. Call `await handle.queryPermission({ mode: 'read' })`. If `'granted'`, scan. If `'prompt'`, call `requestPermission()`. If denied or the handle is stale (`NotFoundError` on first read), fall back to first-click flow.
3. During scan: button shows a spinner; disable Sync; columns remain interactive.
4. After scan: status pill updates to `<count> cards · synced just now`. The "N min ago" ticker updates every 30 seconds.

### Scan algorithm

```
videosDirHandle = (cached or freshly picked)
results = []
errors = 0

for await (entry of videosDirHandle.values()):
  if entry.kind != 'directory': continue
  match = entry.name.match(/^(.+)-(\d{4}-\d{2}-\d{2})$/)
  if !match: continue                     // skip non-conforming folders
  slug, date = match[1], match[2]
  try:
    artifacts = {
      research:  await exists(entry, 'seo/research.json'),
      script:    await exists(entry, 'script.md'),
      voiceover: voiceoverStatus(entry),  // see helper
      compose:   await composeStatus(entry),
      thumbnail: await thumbnailStatus(entry),
      render:    await hasMp4InOutput(entry),
      published: 'unknown',
    }
    suggestedStage = computeSuggested(artifacts)
    title = await readOutlineH1(entry)    // best effort, may be null
    results.push({ slug, date, suggestedStage, artifacts, title })
  catch error:
    errors += 1
    console.warn(`scan failed for ${entry.name}:`, error)

return { results, errors }
```

**Helpers:**
- `exists(dir, path)` — splits on `/`, walks `getDirectoryHandle` then `getFileHandle`. Returns `'present'` on hit, `'missing'` on `NotFoundError`. Other errors → `'unknown'`.
- `voiceoverStatus(dir)`:
  - `audio/voiceover.mp3` AND `transcript.json` both missing → `'missing'`
  - both present, `narration-map.json` missing → `'partial'`
  - all three present → `'present'`
  - any other state → `'partial'`
- `composeStatus(dir)` — `index.html` missing → `'missing'`; exists with size ≤ 8 KB → `'partial'`; exists with size > 8 KB → `'present'`.
- `thumbnailStatus(dir)` — count of `thumbnail-{a,b,c}.png` present: 0 → `'missing'`, 1-2 → `'partial'`, 3 → `'present'`.
- `hasMp4InOutput(dir)` — list `output/` directory; any `*.mp4` → `'present'`; else `'missing'`. `output/` missing → `'missing'`.
- `readOutlineH1(dir)` — read `outline.md` (best effort), match `/^# (.+?)(?: — 9-beat outline)?$/m`, return the captured title or null.

**Errors are non-fatal.** Per-folder errors increment a counter; the scan continues with the rest. The status pill says `12 of 13 folders synced (1 error)` when errors > 0.

### Merge scan into state

For each `result`:
- Find `card` with matching `slug` AND `date`:
  - **If found:** update `card.artifacts = result.artifacts`, `card.lastScannedAt = now`. Do **not** change `card.stage`. Recompute `hasDrift` for rendering.
  - **If not found:** create a new card with `stage = result.suggestedStage`, `title = result.title || titleCase(slug)`, `artifacts = result.artifacts`, `notes = ""`, fresh timestamps.

For each existing `card` with no matching `result`:
- Leave it alone. The user may be tracking an idea before its folder exists.

### Browser support

- **Chromium-based browsers** (Chrome, Edge, Brave, Arc, Opera): full support.
- **Firefox / Safari**: File System Access API unavailable. Sync button is rendered disabled with a tooltip: `"Folder scanning needs a Chromium-based browser. Manual mode still works."` Everything else (add, drag, panel, notes, delete) works identically.

Detect via `'showDirectoryPicker' in window`.

### Keyboard shortcuts

| Key            | Action                                  |
|----------------|-----------------------------------------|
| `n`            | Open Add Card dialog                    |
| `s`            | Trigger Sync                            |
| `?` (Shift+/)  | Open Help dialog                        |
| `Esc`          | Close panel / close any open dialog     |
| `Delete`       | Delete card (when panel open; confirms) |

Shortcuts are disabled while focus is inside `<input>`, `<textarea>`, or `<select>`.

## Edge cases

- **Two cards with the same slug+date.** Disallowed by Add validation. Scan never creates duplicates because `mergeScan` matches on `slug+date`.
- **User renames a folder on disk.** Next scan creates a new card from the new folder name; the old card stays orphaned. v1 accepts this — user can manually delete the orphan. (Future: detect renames via stable id stored in folder metadata; out of scope.)
- **User picks the wrong directory at Sync time.** The scan finds zero matching folders (none match the `<slug>-<date>` regex). Status pill shows `0 of 0 folders synced`. User can re-trigger Sync; the folder picker reopens because the cached handle is the wrong one. Provide a "Reset folder access" link in the Help dialog to clear `videosDirHandle` from IndexedDB.
- **localStorage quota.** Negligible — ~100 cards × ~500 bytes = ~50 KB. Default quota is 5-10 MB. Not a concern in v1.
- **localStorage unavailable** (private browsing in some browsers). Render an in-page banner: `"localStorage is unavailable. Changes will not persist."` All features work in-memory.
- **Network offline.** Doesn't matter. The whole app is local. Google Fonts may FOUT — accept it (system serif fallback is fine).
- **Schema migration.** `schemaVersion` is the migration anchor. v1 reads only `:v1` keys; future v2 reads `:v2`, falling back to upgrading from `:v1` if absent. Out of scope for this spec.

## Out of scope (explicitly)

- Multi-user / cloud sync.
- Filters, search, tags, custom stages.
- Editing artifact-detection rules in the UI.
- Bulk operations (multi-select, mass move).
- Card reordering inside a column.
- Mobile / touch-optimized layout. Desktop-only in v1.
- Undo/redo. v1 uses native `confirm()` for destructive actions.
- Per-user theme switching. Dark mode only.
- Renaming a folder via the UI.
- Scaffolding a new video folder via the UI. (Skills do that; the Kanban observes.)

## Open questions

None at spec time. All design decisions are locked.

## Reference

- Visual mockup: `.superpowers/brainstorm/27329-1778293267/content/kanban-mockup.html`
- Project conventions: `CLAUDE.md` at repo root
- Pipeline-entry skills (now self-bootstrapping):
  - `.claude/skills/youtube-seo-research/SKILL.md`
  - `.claude/skills/script-writer/SKILL.md`
  - `.claude/skills/thumbnail-creator/SKILL.md`
