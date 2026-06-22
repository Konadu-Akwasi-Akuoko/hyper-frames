# studio — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build `tools/studio` — a unified, full-stack idea aggregator (The Wire) + 12-stage production board (The Desk), fed by a zero-AI Python discovery CLI and curated by a worth-pursuing skill, with all intelligence in the skill and a server-owned SQLite store that keeps AI token cost flat.

**Architecture:** Bun + Hono server on `:3273` is the only writer of UI-driven tables and the only reader the React client talks to; a Vite + React 19 client on `:5273` renders two views (Ideas/The Wire, Pipeline/The Desk); a Python `studio-discover` CLI writes raw signal rows (yt-dlp channel videos + comments, plus HN/Reddit/Lobsters/daily.dev) into the same local SQLite file; a `studio-ideas` skill reads only the unjudged delta, applies qualitative keep/discard judgment, and inserts curated ideas. See `docs/superpowers/specs/2026-06-22-studio-idea-board-design.md` for the full design and §10.1 for the locked visual language.

**Tech Stack:** Bun 1.3 runtime, `bun:sqlite` (server writer), Hono 4, Vite 8 + React 19 + TypeScript 6, Zod 4, Tailwind v4 (`@theme` tokens), Python 3 + uv (discovery CLI, stdlib `sqlite3` writer, stdlib `urllib` fetchers, `yt-dlp` subprocess), pytest. SQLite is a local file (`studio.db`); **no Docker, no DB server** — both writers open the same file (WAL mode).

## Global Constraints

- **Ports:** server `:3273`, client `:5273` (configurable via `STUDIO_API_PORT` / vite proxy). Never collide with audio-editor's `:3001`/`:5173`.
- **SQLite:** local file `tools/studio/studio.db`, WAL mode, gitignored. Server writes via `bun:sqlite`; discovery CLI writes via Python stdlib `sqlite3`. No Docker.
- **Envelope:** every server response uses `ApiResponse<T>` (`{success:true,data}` | `{success:false,error:{code,message,details?}}`), exactly as `tools/audio-editor/server/lib/response.ts`. Client uses `apiFetch<T>()`.
- **Aggregator, never a judge:** NO numeric score / rank / rubric anywhere — not in DB, server, client, or skill. The `ideas` table has no score column. The human decides make-or-not and long/short/series.
- **Intelligence lives in the skill only.** The server fabricates no curation. The skill applies qualitative keep/discard + a one-line `rationale`.
- **Flat token cost:** the skill reads only `WHERE judged_at IS NULL`; dedup is a targeted `WHERE id = ?`; promote/reject leave the active view (`status IN ('new','keep')`); prune deletes old judged `raw_signal`.
- **Bot-wall discipline (load-bearing):** yt-dlp runs **serial**, bounded (top ~15 videos/channel, ~30 comments/video, tunable), with `--sleep-requests` pacing, optional `--cookies-from-browser`, and graceful metadata-only degradation if comments are walled. Validated on ONE video before any batch path (Task 0).
- **Visual language = §10.1 "The Wire Desk".** Palette: Newsprint `#EDE9E0`, Card Stock `#FBFAF6`, Card Sunk `#E5E0D6`, Press Ink `#1C1A17`, Graphite `#6F6A61`, Signal Teal `#2C6E6A` (meter cold pole only), On-Air Red `#D6402E` (meter peak / ON-AIR / commit only — never a wash). Fonts: Bricolage Grotesque (display), Inter (body), JetBrains Mono (`.num` utility only). One meter law (teal→red) shared across both views. Namespace every component class (`.wire-meter`, `.desk-meter`, `.band-filter`) — never a bare `.hot`/`.cold`/`.x`. `tools/studio/design/mockup.html` is the visual source of truth — port its markup/CSS into React.
- **Stages (12, exact ids/labels from kanban.html):** `idea` (Idea 👨), `research` (Research 👨), `script` (Script 🤖), `voiceover` (Voiceover 🤖), `compose` (Compose 🤖), `review` (Review 👨), `thumbnail` (Thumbnail 🤖), `translate` (Captions 🤖), `render` (Render 🤖), `published` (Published 👨), `publish-qa` (Publish QA 🤖), `shorts` (Shorts 🤖).

---

## File Structure

```
tools/studio/
├── package.json, bun.lock, vite.config.ts, eslint.config.js, index.html
├── tsconfig.json, tsconfig.app.json, tsconfig.node.json, tsconfig.server.json
├── .gitignore, CLAUDE.md, README.md
├── studio.db                      (gitignored)
├── design/mockup.html             (already exists — visual source of truth)
├── server/
│   ├── index.ts                   bootstrap, port 3273, error envelope
│   ├── lib/{response,schemas,db,ids,scan,stages}.ts
│   └── routes/{ideas,board,channels,discovery}.ts
├── src/
│   ├── main.tsx, App.tsx, api.ts, types.ts
│   ├── styles/globals.css         (@theme tokens from §10.1)
│   ├── views/{Wire,Desk}.tsx
│   └── components/{WireMeter,DeskMeter,BandFilter,Dispatch,LaneCard,DetailPanel,ViewToggle}.tsx
└── discovery/
    ├── pyproject.toml             (uv; [project.scripts] studio-discover; [tool.pyright])
    ├── src/studio_discovery/{__init__,cli,youtube,aggregators,store,ids}.py
    └── tests/{test_youtube_argv,test_aggregators,test_ids,test_store}.py
```

---

### Task 0: Feasibility spike — yt-dlp comment fetch (the #1 risk; gates discovery)

**Files:** none committed (scratch validation). Records findings in the discovery CLI defaults.

**Interfaces:** Produces the validated yt-dlp comment argv used by `youtube.py` in Task 9.

- [ ] **Step 1:** Pick one known video from a seed channel (e.g. a recent Fireship short). Run, timing it:
  `yt-dlp --skip-download --no-warnings --write-comments --extractor-args "youtube:comment_sort=top;max_comments=30,all,30" --dump-single-json "<url>" > /tmp/studio-spike.json`
- [ ] **Step 2:** Inspect: `python3 -c "import json;d=json.load(open('/tmp/studio-spike.json'));print(d.get('comment_count'), len(d.get('comments') or []));[print(c.get('text','')[:80]) for c in (d.get('comments') or [])[:5]]"`
- [ ] **Step 3:** If comments return: lock the argv. If walled/empty: retry with `--cookies-from-browser chrome`; if still walled, record that comment fetch degrades to metadata-only and the skill works comment-free for that source. **Either way the spike resolves the design — never leaves it open.**
- [ ] **Step 4:** Note pacing that didn't trip the wall (`--sleep-requests`, serial). No commit (scratch), but write the resolved argv + max_comments default into Task 9's `youtube.py`.

---

### Task 1: Scaffold `tools/studio`

**Files:** Create `tools/studio/{package.json,vite.config.ts,eslint.config.js,index.html,tsconfig*.json,.gitignore,CLAUDE.md,README.md}`.

**Interfaces:** Produces the buildable shell. `package.json` scripts: `dev` (concurrently vite+api), `dev:vite`, `dev:api` (`bun --hot server/index.ts`), `build` (`tsc -b && vite build`), `lint`. Deps mirror audio-editor (hono ^4, react ^19, react-dom ^19, zod ^4; dev: vite ^8, @vitejs/plugin-react, tailwindcss ^4 + @tailwindcss/vite, typescript ~6, @types/bun, @types/node, @types/react*, eslint stack, concurrently).

- [ ] **Step 1:** Write `package.json` (name `studio`, type module) copying audio-editor's scripts/deps; `dev:api` → `bun --hot server/index.ts`.
- [ ] **Step 2:** Write `vite.config.ts` — `server.port = 5273`, proxy `/api` → `http://localhost:3273`. Plugins: react(), tailwindcss().
- [ ] **Step 3:** Write `tsconfig.*` (4 files) mirroring audio-editor's project-references layout (app = `src`, node = vite config, server = `server`). Write `eslint.config.js`, `index.html` (root div + `/src/main.tsx`, Google Fonts links for Bricolage Grotesque + Inter + JetBrains Mono), `.gitignore` (`node_modules`, `dist`, `studio.db`, `studio.db-*`).
- [ ] **Step 4:** Write `CLAUDE.md` ("do not start the dev server — user keeps `bun dev` running on :5273/:3273; tell the user to reload the tab"; ports; sqlite local-file note; tailwind v4 `@theme` note) and `README.md`.
- [ ] **Step 5:** `cd tools/studio && bun install`. Verify `bunx tsc -b` runs (no source yet → trivially passes once stubs exist) and commit.

---

### Task 2: SQLite layer — `db.ts`, `ids.ts`, `stages.ts`

**Files:** Create `server/lib/db.ts`, `server/lib/ids.ts`, `server/lib/stages.ts`. Test `server/lib/db.test.ts`.

**Interfaces:**
- Produces `getDb(): Database` (singleton, opens `studio.db` relative to `import.meta.dir`, `PRAGMA journal_mode=WAL`, runs `migrate()` idempotently creating the 4 tables + indexes from spec §6).
- Produces `rawSignalId(source: string, externalId: string): string` (stable hash) and `urlHash(url)` in `ids.ts`, matching the Python `ids.py` so cross-writer dedup agrees.
- Produces `STAGES: {id,label,who:'human'|'ai'}[]` (12, from Global Constraints), `stageIndex(id)`, `MILESTONE_STAGES = ['published','publish-qa','shorts']` in `stages.ts`.

- [ ] **Step 1:** Write failing `db.test.ts` (`bun:test`): open an in-memory/temp db, assert `migrate()` creates tables `channels,raw_signal,ideas,board_overlay` and that inserting/reading an idea round-trips; assert no `score` column exists on `ideas`.
- [ ] **Step 2:** Run `bun test server/lib/db.test.ts` → FAIL.
- [ ] **Step 3:** Implement `db.ts` with the exact DDL from spec §6 (4 tables, `idx_raw_unjudged` partial index, `idx_ideas_status`). Implement `ids.ts` (`createHash('sha1')` of `source+'\x1f'+externalId`, hex 16). Implement `stages.ts`.
- [ ] **Step 4:** Run `bun test server/lib/db.test.ts` → PASS.
- [ ] **Step 5:** Commit.

---

### Task 3: Response envelope + Zod schemas

**Files:** Create `server/lib/response.ts` (copy audio-editor verbatim: `ApiResponse<T>`, `ApiError`, `ok`, `fail`), `server/lib/schemas.ts` (Zod request/response shapes), `src/types.ts` (shared client types: `Idea`, `BoardCard`, `Channel`, `ArtifactStatus`, `Stage`).

**Interfaces:** Produces `ok(c,data,status?)`, `fail(c,code,msg,status,details?)`, `ApiError`. Zod: `IdeaTriageBody` (`status: 'keep'|'rejected'`, optional `kind`, `notes`), `IdeaPromoteBody`, `SetStageBody`, `ChannelBody`. Client `Idea` mirrors `ideas` columns; `BoardCard = {slug,title,date,stage,artifacts:Record<string,ArtifactStatus>,suggestedStage?,hasDrift,notes,fromIdea?}`.

- [ ] **Step 1:** Copy `response.ts` from audio-editor (unchanged).
- [ ] **Step 2:** Write `schemas.ts` Zod objects for each mutating route body.
- [ ] **Step 3:** Write `src/types.ts` mirrors. `bunx tsc -b` clean.
- [ ] **Step 4:** Commit.

---

### Task 4: `scan.ts` — port the kanban artifact scanner to server fs

**Files:** Create `server/lib/scan.ts`. Test `server/lib/scan.test.ts` (temp `videos/` fixture tree).

**Interfaces:** Produces `scanVideos(root: string): Promise<ScannedVideo[]>` where `ScannedVideo = {slug,date,artifacts:Record<ArtifactId,ArtifactStatus>,suggestedStage,title?}`. `ArtifactStatus = 'present'|'partial'|'missing'|'unknown'`. Reuses the exact probe logic from kanban.html (use `node:fs/promises`):
- `research`: `seo/research.json` exists.
- `script`: `script.md`.
- `voiceover`: present iff `audio/voiceover.mp3` + `transcript.json` + `narration-map.json`; partial if mp3+transcript only; missing if both absent.
- `compose`: `index.html`.
- `review`: present if `compositions/sfx.html` OR `compositions/music.html`.
- `thumbnail`: count of `thumbnail-{a,b,c}.png` → 3 present / 1-2 partial / 0 missing.
- `render`: any `.mp4` under `renders/` or `output/`.
- `suggestedStage`: last of `[research,script,voiceover,compose,review,thumbnail,translate,render]` whose status is `present` (translate/published/publish-qa/shorts are stage-derived, not scanned).
- Folder name parse: `^(?<slug>.+)-(?<date>\d{4}-\d{2}-\d{2})$`. Optional `outline.md` H1 → `title`.

- [ ] **Step 1:** Write failing `scan.test.ts`: build a temp dir with two fake video folders (one with `script.md` only → suggested `script`; one with full voiceover trio → suggested `voiceover`), assert `scanVideos` output.
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement `scan.ts` per the probes above.
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit.

---

### Task 5: Server routes + bootstrap

**Files:** Create `server/index.ts`, `server/routes/{board,ideas,channels,discovery}.ts`.

**Interfaces (endpoints):**
- `GET /api/board` → cards = merge(`scanVideos(VIDEOS_ROOT)` ⨝ `board_overlay`), computing `hasDrift` (suggested≠overlay stage, exempting milestone stages and `idea`). `POST /api/board` (add card), `PATCH /api/board/:slug` (stage/notes/title), `DELETE /api/board/:slug`, `POST /api/board/sync` (rescan).
- `GET /api/ideas?status=new,keep&type=` (default active view `status IN ('new','keep')`), `PATCH /api/ideas/:id` (triage: status/kind/notes), `POST /api/ideas/:id/promote` (insert `board_overlay` stage `idea`, set idea `status='promoted'`, `promoted_slug`), `POST /api/ideas` (manual add), `POST /api/ideas/prune` (delete judged `raw_signal` older than N days).
- `GET /api/channels`, `POST /api/channels`, `PATCH /api/channels/:handle`, `DELETE /api/channels/:handle`.
- `POST /api/discovery/run` → spawn `studio-discover` (Bun.spawn), stream/return summary counts; `GET /api/discovery/raw-counts` → unjudged counts by source.
- `server/index.ts`: `export default { port: 3273, fetch: app.fetch }`, mounts routes, `onError` envelope (ApiError/ZodError/INTERNAL), `notFound`.

- [ ] **Step 1:** Write `paths.ts` (`VIDEOS_ROOT = resolve(import.meta.dir,'../../../videos')`, `SLUG_RE`, slug guard) reused from audio-editor.
- [ ] **Step 2:** Implement `board.ts` against `getDb()` + `scanVideos`. Test promote/drift transitions on a temp db.
- [ ] **Step 3:** Implement `ideas.ts` (active-view filter, triage, promote, prune).
- [ ] **Step 4:** Implement `channels.ts`, `discovery.ts`.
- [ ] **Step 5:** Wire `index.ts`. `bunx tsc -b` clean. Smoke: `bun server/index.ts &` then `curl :3273/api/board` returns the envelope. Commit.

---

### Task 6: Client foundation + design tokens (§10.1)

**Files:** Create `src/main.tsx`, `src/App.tsx`, `src/api.ts` (copy audio-editor `apiFetch`), `src/styles/globals.css`.

**Interfaces:** `globals.css` `@theme` block defines every §10.1 token as a CSS var (`--news`, `--card-stock`, `--card-sunk`, `--ink`, `--graphite`, `--meter-cold`, `--meter-hot`, `--radius:6px`, font families). `App.tsx` holds the view toggle state (`'wire'|'desk'`), masthead, and renders `<Wire/>` / `<Desk/>`. Lift the mockup's CSS into `globals.css` (namespaced classes).

- [ ] **Step 1:** Copy `api.ts`. Write `main.tsx` (React 19 root).
- [ ] **Step 2:** Port `tools/studio/design/mockup.html`'s `<style>` into `globals.css` as `@theme` tokens + component classes, verbatim palette/fonts.
- [ ] **Step 3:** Write `App.tsx` masthead + `ViewToggle` + view switch. `bunx tsc -b` clean. Commit.

---

### Task 7: The Wire view (Ideas) — port mockup markup into React

**Files:** Create `src/views/Wire.tsx`, `src/components/{WireMeter,BandFilter,Dispatch}.tsx`.

**Interfaces:** Consumes `GET /api/ideas`, `PATCH /api/ideas/:id`, `POST /api/ideas/:id/promote`. Renders the mockup's left rail (band filter by `type` with counts + glyphs; the meter legend "Meter = rationale lean. Never a score."; keyboard hints) and the dispatch list. `WireMeter` = vertical 5-segment, `data-lean` fill on the shared teal→red ramp (lean derived from the idea, NOT a score — map `type`/evidence to a 2-3 state lean). Inline type glyphs (target/waveform/rising-trace). Per-dispatch actions: keep, reject (squelch desaturate), set kind (long·short·series), promote. Keyboard: j/k nav, k keep, x reject, p promote, 1/2/3 kind.

- [ ] **Step 1:** Build `Dispatch.tsx` + `WireMeter.tsx` from the mockup's `.dispatch`/`.wire-meter` markup, typed against `Idea`.
- [ ] **Step 2:** Build `BandFilter.tsx` + `Wire.tsx` list, wire data via `apiFetch`, optimistic triage.
- [ ] **Step 3:** Wire keyboard handlers (ignore when typing in inputs). `bunx tsc -b` clean.
- [ ] **Step 4:** Verify in Chrome MCP (screenshot, exercise keep/reject/promote). Commit.

---

### Task 8: The Desk view (Pipeline) — board

**Files:** Create `src/views/Desk.tsx`, `src/components/{DeskMeter,LaneCard,DetailPanel}.tsx`.

**Interfaces:** Consumes `GET /api/board`, `PATCH/POST/DELETE /api/board*`, `POST /api/board/sync`. 12 horizontal lanes, cards with `DeskMeter` (horizontal continuous teal→red, width = artifact-progress fraction from scan). Drag-to-stage (HTML5 DnD), click → `DetailPanel` (slug/folder, stage selector, artifact checklist, notes, delete), drift flag, add-card dialog, Sync button. Published lane goes On-Air Red + ON-AIR dot. Keyboard: n add, s sync, ? help, Esc close, Delete card.

- [ ] **Step 1:** Build `LaneCard` + `DeskMeter` from the mockup's `.lane`/`.card`/`.desk-meter` markup, typed against `BoardCard`.
- [ ] **Step 2:** Build `Desk.tsx` (lanes, DnD, sync) + `DetailPanel`.
- [ ] **Step 3:** Wire keyboard + add-card. `bunx tsc -b` clean.
- [ ] **Step 4:** Verify in Chrome MCP (screenshot both views, drag a card, promote-from-Wire lands in Desk Idea lane). Commit.

---

### Task 9: Discovery CLI (Python) + tests

**Files:** Create `discovery/pyproject.toml`, `discovery/src/studio_discovery/{__init__,cli,youtube,aggregators,store,ids}.py`, `discovery/tests/{test_youtube_argv,test_aggregators,test_ids}.py`.

**Interfaces:** `studio-discover` entry (argparse). Pure argv builders kept separate from runners (inspo-ingest convention):
- `youtube.py`: `channel_videos_argv(handle, n)` → `['yt-dlp','--skip-download','--dump-json','--playlist-end',str(n),'--ignore-errors','--no-warnings', f'https://www.youtube.com/@{handle}/videos']` (ported from competitors.py). `comments_argv(video_url, max_comments)` → the Task-0-validated comment argv. Runners parse one JSON/line (videos) and `comments[]` (single-json). Serial across channels with `--sleep-requests`.
- `aggregators.py`: `fetch_hn/fetch_reddit/fetch_lobsters/fetch_dailydev` ported verbatim from `topic-pipeline/fetch.py` (HN Algolia `search_by_date`; Reddit per-sub `top.json` w/ 2.5s sleeps + UA; Lobsters RSS regex; daily.dev GraphQL `anonymousFeed`). Each returns normalized dicts `{source,external_id,title,url,payload}`.
- `ids.py`: `raw_signal_id(source,external_id)` = sha1(`source\x1fexternal_id`)[:16] — must match `server/lib/ids.ts`.
- `store.py`: `open_db(path)` (stdlib sqlite3, WAL), `upsert_raw(rows)` (INSERT OR IGNORE into `raw_signal`, `judged_at=NULL`), idempotent.
- `cli.py`: flags `--db`, `--channels` (or read from db `channels`), `--videos-per-channel 15`, `--comments-per-video 30`, `--sleep 2`, `--no-comments`, `--sources hn,reddit,lobsters,dailydev,youtube`. Serial, bounded, degrades gracefully (one dead source/channel never fails the run); prints a per-source summary.

- [ ] **Step 1:** `uv init` the project; `pyproject.toml` with `[project.scripts] studio-discover` + `[tool.pyright] venvPath="." venv=".venv"`.
- [ ] **Step 2:** TDD `test_youtube_argv` (assert exact channel + comment argv lists), `test_ids` (assert hash equals a known value also asserted in `db.test.ts`), `test_aggregators` (feed fixture JSON to each parser, assert normalized rows). Implement modules to pass.
- [ ] **Step 3:** `uv run pytest` green.
- [ ] **Step 4:** Live bounded run: `uv run studio-discover --db ../studio.db --sources hn,lobsters --videos-per-channel 3 --comments-per-video 10` against 1-2 channels; confirm `raw_signal` rows land (`sqlite3 studio.db 'select source,count(*) from raw_signal group by 1'`). Commit.

---

### Task 10: The `studio-ideas` skill (via /skill-creator)

**Files:** Create `.claude/skills/studio-ideas/SKILL.md` (+ any reference files skill-creator produces).

**Interfaces:** The skill flow (spec §7.2 Layer 2): (1) optionally trigger a discovery run; (2) read ONLY `SELECT ... FROM raw_signal WHERE judged_at IS NULL` (the flat-cost guarantee) via `sqlite3` CLI or the server; (3) apply worth-pursuing judgment — Fit (computing/system-design angle), Novelty (dedup vs existing `ideas` + `videos/` slugs), Demand shape (cluster comment themes w/ quotes+counts); verdict keep|discard, NO number; (4) insert keepers into `ideas` with `type`, `evidence_json`, one-line `rationale`, `kind='unset'`; (5) mark every judged row `judged_at=now`, `judged_verdict`. Discarded rows stay (audit, never resurfaced).

- [ ] **Step 1:** Invoke `/skill-creator` with the §7 contract; generate `SKILL.md` encoding the 5-step flow, the delta-only read, the no-grade rule, and the exact SQL.
- [ ] **Step 2:** Dry-run the skill against the Task-9 raw rows on a copy db; assert it reads only unjudged, writes `rationale`, leaves `kind` unset, marks rows judged. Commit.

---

### Task 11: Migration + retirement

**Files:** Modify root `CLAUDE.md`; create `tools/studio/discovery/seed_channels.py` (one-off) or seed via SQL; optional `inbox.json` import.

**Interfaces:** Seed `channels` from spec §7.1 (14 handles, CleoAbram = shorts URL). Optional: import `topic-pipeline/data/inbox.json` items with `user_status in (go,later,shipped)` into `ideas` (type `trend`/`manual`, `status` mapped, rationale from notes) — one-time, idempotent by id. Update root `CLAUDE.md`: point idea/board workflows at `tools/studio`, note `kanban.html` + `topic-pipeline` retired (left in git history).

- [ ] **Step 1:** Seed channels (idempotent INSERT OR IGNORE). Verify `GET /api/channels`.
- [ ] **Step 2:** Import inbox.json keepers into `ideas`. Verify they appear in The Wire.
- [ ] **Step 3:** Edit root `CLAUDE.md` retirement notes. Commit.

---

### Task 12: End-to-end verification + docs

**Files:** Modify `tools/studio/README.md`, `CLAUDE.md` as needed.

- [ ] **Step 1:** `bunx tsc -b` (all projects) + `bun run lint` clean; `uv run pytest` green; `bun test` (server) green.
- [ ] **Step 2:** Boot server (`bun --hot server/index.ts &`) + vite (`vite &`); curl every endpoint, assert envelopes.
- [ ] **Step 3:** Chrome MCP: load `:5273`, screenshot The Wire + The Desk, run discovery via the UI button, curate via the skill, triage + promote an idea, confirm it lands on The Desk, drag it across a stage, Sync. Capture screenshots.
- [ ] **Step 4:** Final README (how to run, ports, discovery + skill workflow). Commit.

---

## Self-Review

- **Spec coverage:** §5 layout → Tasks 1-9; §6 DDL → Task 2; §7 discovery+skill → Tasks 9-10; §8 board → Tasks 4,5,8; §9 token guardrails → Tasks 2,5,10 (delta read, active view, prune); §10/§10.1 frontend → Tasks 6-8; §11 migration → Task 11; §12 testing → Tasks 2,4,9,10,12. All covered.
- **No-grade invariant** enforced in Task 2 (no score column, asserted in test), Task 5 (no scoring endpoints), Task 7/8 (meter encodes lean/progress, not a score), Task 10 (skill verdict keep|discard).
- **Cross-writer hash agreement:** `ids.ts` (Task 2) and `ids.py` (Task 9) tested against the same known value.
- **Type consistency:** `ArtifactStatus`, `Stage`, `BoardCard`, `Idea` defined in Task 3, consumed unchanged in Tasks 4,5,7,8.
- **Risk-first:** Task 0 validates comments before any batch path (spec §7.4/§13).
