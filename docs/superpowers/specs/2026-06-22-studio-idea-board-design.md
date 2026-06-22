# Design — `tools/studio`: unified idea aggregator + production board

- **Date:** 2026-06-22
- **Status:** Approved (functional + architecture). Visual design pending a dedicated `frontend-design` pass (see §10).
- **Author:** Akwasi Konadu Akuoko (with Claude Code)
- **Supersedes:** `kanban.html` (root) and `tools/topic-pipeline/` — both retired into this tool (see §11).

---

## 1. Summary

A single full-stack web app, `tools/studio`, that unifies the two halves of the
channel's content workflow:

1. **Ideas** — an *aggregator* backlog. It collects raw signal from a fixed set
   of YouTube channels (their recent videos + top comments) and the text
   aggregators (Hacker News, Reddit, Lobsters, daily.dev). A skill applies
   qualitative *worth-pursuing* judgment — keep or discard, never a grade — and
   the curated ideas land in a backlog the human triages.
2. **Pipeline** — the 12-stage production board (ported from `kanban.html`) that
   tracks each committed video from Idea → Published → Shorts, deriving real
   progress by scanning the `videos/` folder.

Ideas flow into Pipeline: promoting an idea creates a board card and removes the
idea from the backlog, so the backlog stays small.

The app is the human surface (browse, triage, drag). The *intelligence* lives in
a skill, not in the server. The store is server-owned SQLite so the AI never
loads the whole dataset — the explicit defense against context-token bloat.

---

## 2. Context & motivation

The channel already had two partial, disconnected systems:

- **`kanban.html`** (repo root, 3,176 lines, vanilla single-file HTML/JS) — a
  live, polished Kanban board tracking videos through 12 production stages with
  drag-and-drop, localStorage, and a File System Access API scan of `videos/`.
  Its first column is "Idea", but it tracks *committed* video projects, not a
  loose brainstorm backlog, and nothing feeds it automatically.
- **`tools/topic-pipeline/`** (Python, last run 2026-05-21, ~1 month dormant) —
  a heavy daily pipeline that mined 18 reference channels via yt-dlp (metadata
  only, **no comments**), scored candidates on a 6-axis LLM rubric, and kept a
  61-item `inbox.json` with a `null → go/pass/later/shipped` lifecycle, a review
  dashboard, and prune-to-graveyard.

The gap: nothing was a *small, comment-aware idea backlog that feeds the
production board*. The decision (see §3) is to build one app that absorbs the
useful bones of both and drops the parts that made `topic-pipeline` heavy
(scoring rubric, LLM judgment phase, daily cron).

---

## 3. Decisions (the brainstorm outcomes)

| # | Decision | Rationale |
|---|---|---|
| D1 | **Combine** ideas + production into one web app | The two halves are one flow: mined idea → drag into production → track to publish. |
| D2 | **Full client+server stack** — Bun + Vite + React + Hono, matching `tools/audio-editor` | User chose "powerful"; reuse the house full-stack pattern. |
| D3 | **SQLite, server-owned** store | Kills the token-bloat fear: the AI queries bounded rows, never loads the whole store. |
| D4 | **Aggregator, not judge — no scoring** | No numeric grade, no rank, no 6-axis rubric. The human decides make-or-not. The AI **suggests** a format (long / short / series) with a one-line reason; the human confirms or overrides (amended 2026-06-22, see `2026-06-22-studio-kind-suggestion-design.md`). |
| D5 | **Intelligence lives in the skill** | The skill decides *worth pursuing or not* (qualitative keep/discard with a one-line rationale) and *suggests a format* (qualitative, with a one-line reason) — not the server, never a number. |
| D6 | **Absorb the text aggregators too** | HN / Reddit / Lobsters / daily.dev folded into discovery as raw `trend` ideas (no scoring). |
| D7 | **Retire both** `kanban.html` and `topic-pipeline` | Harvest channel list + free-API fetchers + prune idea; drop the rubric/judgment/cron. Old files stay in git history. |
| D8 | **Distinct ports** — server `:3273`, client `:5273` | Avoid collision with `audio-editor` (`:3001` / `:5173`). Configurable via env. |
| D9 | **Visual design rethought from scratch** via the `frontend-design` skill, referencing real apps | Deferred to a dedicated pass (§10) after this doc is approved, before implementation. |

---

## 4. Goals & non-goals

**Goals**
- One UI for both the idea backlog and the production pipeline.
- Channel mining that includes **video comments** (net-new; nothing in the repo
  does this today).
- Skill-driven, qualitative idea curation (keep/discard + why).
- Flat AI token cost regardless of backlog size.
- The human keeps full control: make-or-not, the final long/short/series format
  (the AI only *suggests* it), stage.

**Non-goals**
- No numeric scoring, ranking, or rubric of any kind.
- No automatic decision to make a video. (The format is AI-*suggested* but the
  human confirms or overrides it — still no numeric grade.)
- No editorial chrome beyond what the board needs (consistent with project
  house rules for compositions; not applicable to this internal tool, but the
  aesthetic restraint carries over).
- No rebuild of `topic-pipeline`'s LLM judgment phase or daily scheduled cron in
  this phase (a manual/optional scheduled discovery run is future work, §14).
- No cross-device sync / hosted backend — this is a local dev tool.

---

## 5. Architecture

### 5.1 Directory layout

```
tools/studio/
├── server/                 # Hono on :3273 — the only writer of studio.db
│   ├── index.ts            # app bootstrap, port, error envelope
│   ├── routes/
│   │   ├── ideas.ts        # list/triage/promote/prune ideas
│   │   ├── board.ts        # list cards (derived scan + overlay), set stage/notes
│   │   ├── channels.ts     # CRUD the mining channel list
│   │   └── discovery.ts    # trigger a raw discovery fetch (shells out to discovery CLI)
│   └── lib/
│       ├── db.ts           # SQLite open + migrations
│       ├── scan.ts         # videos/ artifact scanner (ported from kanban.html)
│       ├── response.ts     # ApiResponse<T> envelope (ok/fail), matches audio-editor
│       └── schemas.ts      # Zod request/response validation
├── src/                    # Vite + React on :5273 — human surface
│   ├── main.tsx, App.tsx
│   ├── api.ts              # apiFetch<T>() wrapper (matches audio-editor)
│   ├── views/
│   │   ├── Ideas.tsx       # backlog triage
│   │   └── Pipeline.tsx    # 12-stage board
│   └── styles/             # design tokens — defined by the frontend-design pass (§10)
├── discovery/              # Python, zero-AI plumbing
│   ├── pyproject.toml      # uv project, [project.scripts], [tool.pyright]
│   └── src/studio_discovery/
│       ├── cli.py          # argparse entry; `studio-discover`
│       ├── youtube.py      # yt-dlp argv builders (pure) + runner: channel videos + top comments
│       ├── aggregators.py  # HN / Reddit / Lobsters / daily.dev free-API fetchers (ported)
│       └── store.py        # writes raw_signal rows into studio.db
├── studio.db               # SQLite (gitignored; rebuildable). Schema in §6.
├── package.json            # bun; scripts: dev, dev:api, dev:vite
├── vite.config.ts          # client :5273, proxy /api → :3273
├── CLAUDE.md               # "do not start the dev server" + invocation notes
└── README.md
```

### 5.2 Components & responsibilities

- **Hono server (`:3273`)** — the *only* process that writes `studio.db`. Serves
  the React app's data via `/api/*` using the `ApiResponse<T>` envelope. Derives
  board state by scanning `videos/` and overlaying manual fields. Triggers raw
  discovery by shelling out to the discovery CLI. Contains **no idea-judgment
  intelligence**.
- **React client (`:5273`)** — the human surface. Two views (Ideas, Pipeline).
  Talks only to `/api/*`. Holds no business logic beyond presentation + optimistic
  UI. Vite proxies `/api` to the server.
- **Discovery CLI (`discovery/`, Python)** — pure plumbing. Fetches raw signal
  (yt-dlp for channels' videos + top comments; HTTP for the text aggregators)
  and writes `raw_signal` rows with `judged_at = NULL`. Bounded + serial
  (§7.4). Decides nothing.
- **The skill (`.claude/skills/studio-ideas/`)** — the intelligence. Orchestrates
  a discovery run, reads only *new* `raw_signal` rows, applies qualitative
  worth-pursuing judgment, inserts keepers into `ideas` with a `rationale`, marks
  raw rows judged. Built with `/skill-creator`. See §7.

### 5.3 Stack & conventions

Matches `tools/audio-editor` exactly so there's one house pattern to maintain:
Bun runtime, Hono 4 backend, Vite + React 19 + TypeScript frontend, Zod
validation, the strict `ApiResponse<T>` success/error envelope, `apiFetch<T>()`
on the client. Python tools follow the repo's `uv` convention (`pyproject.toml`
with `[project.scripts]` + `[tool.pyright]`, pure argv builders kept separate
from subprocess runners, as in `tools/inspo-ingest`).

---

## 6. Data model — `studio.db` (SQLite, server-owned)

Four small tables. The server owns all writes; the discovery CLI writes only
`raw_signal`; the skill writes `ideas` (and marks `raw_signal.judged_at`).

```sql
-- Channels to mine. Seeded from the user's list (§7.1); editable in the UI.
CREATE TABLE channels (
  handle      TEXT PRIMARY KEY,      -- e.g. '@Fireship'
  url         TEXT NOT NULL,         -- canonical /videos or /shorts URL
  note        TEXT,                  -- freeform ("house-style match", "shorts only")
  active      INTEGER NOT NULL DEFAULT 1
);

-- Raw, unjudged signal. The seen-ledger: a row is fetched once, judged once.
CREATE TABLE raw_signal (
  id          TEXT PRIMARY KEY,      -- stable hash of (source, external_id)
  source      TEXT NOT NULL,         -- 'youtube:@Fireship' | 'youtube-comments:@Fireship'
                                     -- | 'hn' | 'reddit:r/programming' | 'lobsters' | 'dailydev'
  external_id TEXT NOT NULL,         -- video id / article id / comment thread id
  title       TEXT,
  url         TEXT,
  payload_json TEXT NOT NULL,        -- source-specific: views, duration, points,
                                     -- comment_count, comment quotes, published_at, etc.
  fetched_at  TEXT NOT NULL,         -- ISO8601
  judged_at   TEXT,                  -- NULL = not yet judged by the skill
  judged_verdict TEXT                -- NULL | 'kept' | 'discarded' (audit trail)
);
CREATE INDEX idx_raw_unjudged ON raw_signal(judged_at) WHERE judged_at IS NULL;

-- Curated ideas (skill output + manual adds). NO score column, by design.
CREATE TABLE ideas (
  id            TEXT PRIMARY KEY,
  type          TEXT NOT NULL,       -- 'mirror' | 'comment_demand' | 'trend' | 'manual'
  kind          TEXT NOT NULL DEFAULT 'unset',  -- 'unset' | 'long' | 'short' | 'series'  (AI suggests, human confirms)
  kind_source   TEXT,                -- 'ai' | 'human' | NULL  (provenance of current kind; NULL = none / 'unset')
  kind_why      TEXT,                -- one-line reason for an AI format pick (only meaningful when kind_source='ai')
  status        TEXT NOT NULL DEFAULT 'new',    -- 'new' | 'keep' | 'rejected' | 'promoted'
  title         TEXT NOT NULL,
  rationale     TEXT,                -- the skill's one-line "why pursue"
  source        TEXT,                -- where it came from (mirrors raw_signal.source)
  source_url    TEXT,
  source_title  TEXT,
  evidence_json TEXT,                -- views/points/comment quotes/counts for the card
  raw_signal_id TEXT,                -- provenance link (nullable for manual)
  first_seen    TEXT NOT NULL,
  notes         TEXT,
  promoted_slug TEXT                 -- set when promoted → links to a board card
);
CREATE INDEX idx_ideas_status ON ideas(status);

-- Manual overlay on the production board. Progress itself is DERIVED from the
-- videos/ scan; this table only holds human overrides + cards with no folder yet.
CREATE TABLE board_overlay (
  slug        TEXT PRIMARY KEY,      -- '<slug>-<YYYY-MM-DD>'
  title       TEXT,
  stage       TEXT,                  -- manual stage when it differs from detected
  notes       TEXT,
  kind        TEXT,                  -- 'unset' | 'long' | 'short' | 'series' | NULL  (promote-time snapshot; display-only on the Desk in v1)
  kind_source TEXT,                  -- 'ai' | 'human' | NULL  (promote-time snapshot)
  created_from_idea TEXT,            -- ideas.id provenance (nullable)
  updated_at  TEXT NOT NULL
);
```

`studio.db` is **gitignored and rebuildable** — `raw_signal` and `ideas` are
regenerable from discovery; `board_overlay` is small and could optionally be
mirrored to a committed JSON snapshot if durability across machines is wanted
(future, §14). This avoids committing an opaque binary and avoids the
token-bloat of a committed growing JSON.

---

## 7. Discovery & the skill

### 7.1 Channel seed list (D6/D7)

Seeded into `channels` (14 unique; `@awesome-coding` was listed twice by the
user):

```
@Shadeofcode   @devforgehq      @Fireship          @thecodingkoalaa
@technetiumm   @TheCodingSloth  @awesome-coding     @codehead01
@SwagProfessorExplain  @Latticx  @CleoAbram (shorts)  @ByteByteGo
@pawel_code_stuff  @CodeSource
```

Text aggregators (no config needed; ported from `topic-pipeline`): Hacker News
(Algolia `search_by_date`), Reddit (`r/programming,compsci,webdev,databases,
cpp,rust,golang` top.json), Lobsters (RSS), daily.dev (GraphQL anonymous feed).

### 7.2 Two layers, cleanly split

**Layer 1 — Discovery CLI (zero AI).** `studio-discover` fetches raw signal and
writes `raw_signal` rows (`judged_at = NULL`). Per active channel: recent videos
(title, views, date, duration → duration is a *displayed hint* for short vs
long, not a decision) and the top N comments of recent videos. Per text
aggregator: trending items with their native signal (points, comment counts).
Dedup is by `raw_signal.id = hash(source, external_id)` — a row is never
fetched or surfaced twice.

**Layer 2 — The skill (the intelligence).** `.claude/skills/studio-ideas/`,
built via `/skill-creator`. Flow:

1. Trigger a discovery run (invoke the CLI) — or operate on already-fetched raw.
2. Read **only new** rows: `SELECT … FROM raw_signal WHERE judged_at IS NULL`.
   (This is the flat-token-cost guarantee — the skill never reads the whole
   store, only the new delta.)
3. Apply qualitative **worth-pursuing judgment** for *this* channel:
   - **Fit** — is there a real computing / system-design angle (on-brand)?
   - **Novelty** — dedup against existing `ideas` (DB query) **and videos already
     made** (scan `videos/` slugs). Don't resurface what's covered.
   - **Demand shape** — cluster raw comments into themes ("viewers keep asking
     about ‹X›") with representative quotes + a count.
   - **Format fit** — suggest a `kind` (long / short / series) from the topic's
     shape (short = single tight mechanism / Cleo-style quick hit; long = full
     system-design / deep explainer needing build-up; series = too big for one
     video / multi-part; when ambiguous, the safer single-video format). A
     suggestion, qualitative — no number, no rank.
   - **Verdict: keep or discard.** No number, no rank.
4. Insert **only keepers** into `ideas` with `type`, `evidence_json`, a one-line
   `rationale`, and a suggested `kind` + `kind_source='ai'` + a one-line
   `kind_why` (the human confirms or overrides the format on The Wire).
5. Mark every judged raw row: `judged_at = now`, `judged_verdict = 'kept'|'discarded'`.
   Discarded rows stay in `raw_signal` (audit trail; never resurfaced, never nag).

### 7.3 The app's role in discovery

The server can **trigger a raw fetch** (`POST /api/discovery/run` → shells out to
the CLI) and the UI can show incoming raw counts. But the curated **Ideas
backlog is skill-produced** — the server never fabricates intelligence with a
mechanical dump. After a run, the human asks the skill to curate (or reviews raw
directly). Final triage (keep/reject, confirm or override the AI-suggested
`kind`, promote) is always the human's.

### 7.4 Bot-wall guardrail (load-bearing, #1 feasibility risk)

Project memory records that batch yt-dlp scans get IP-flagged
(`motion-inspo-batch-youtube-botwall`), and comment extraction is heavier than
metadata. Therefore discovery is:

- **Serial**, not parallel, across channels (no burst). One yt-dlp invocation at
  a time, with `--sleep-requests` and `--sleep-subtitles`-style pacing.
- **Bounded**: top ~15 videos/channel, top ~30 comments/video (tunable via CLI
  flags; conservative defaults).
- **Cookie-aware**: optional `--cookies-from-browser` when soft-blocked (the
  interactive Keychain/FDA path noted in memory; not required for metadata).
- **Gracefully degrading**: if comments get walled, fall back to metadata-only
  for that pass and log it — never crash the run.
- Comment fetching feasibility (exact yt-dlp flags: `--write-comments` +
  `--extractor-args "youtube:comment_sort=top;max_comments=…"`, or
  `getcomments`) is the **first thing validated in the implementation plan** on a
  single video before any batch path is built.

---

## 8. The production board (ported from `kanban.html`)

### 8.1 Stages (12, unchanged from `kanban.html`)

`Idea → Research → Script → Voiceover → Compose → Review → Thumbnail →
Captions → Render → Published → Publish QA → Shorts` (each tagged human vs AI
decision point, as in the original).

### 8.2 Progress is derived, not stored

The server's `scan.ts` (ported from `kanban.html`'s File System Access scan)
walks `videos/<slug>-<YYYY-MM-DD>/` and infers artifact completion from real
files: `seo/research.json`, `script.md`, `audio/voiceover.mp3` + `transcript.json`
(+ `narration-map.json`), `index.html`, `compositions/sfx.html|music.html`,
`thumbnail-{a,b,c}.png`, `captions.srt` / `multi-lingual/srt/`, `renders/*.mp4`.
`board_overlay` holds only manual overrides (a stage set by hand, notes, title)
and cards that have no folder yet (e.g., a just-promoted idea). Where the scan
and the overlay disagree, the UI flags "drift" (also ported behavior).

### 8.3 Promote flow (Ideas → Pipeline)

Promoting an idea:
1. Inserts a `board_overlay` row in stage `Idea` (slug derived from the title,
   kebab-cased; date = today), `created_from_idea = ideas.id`.
2. Sets the idea's `status = 'promoted'`, `promoted_slug = <slug>` → it leaves
   the active backlog (keeps it small — the user's "pop it out" requirement,
   automatic).
3. The `videos/<slug>-<date>/` folder is created **later** by the normal
   authoring flow (e.g., `script-writer` scaffolding). The scan links card ↔
   folder by slug once it exists.

### 8.4 Lifecycle / prune (the topic-pipeline trick, kept)

- Ideas: `new → keep | rejected → promoted`.
- **The active backlog view = `status IN ('new','keep')`.** `rejected` and
  `promoted` ideas are excluded from default reads, so they never bloat the
  working set — no separate ideas graveyard table is needed.
- **`raw_signal` is the table that actually grows.** A prune action (manual /
  on-demand) deletes judged rows (`judged_at IS NOT NULL`) older than N days
  (default 90). They've served their dedup + audit purpose; old aggregator/video
  items effectively never re-surface, and on the rare re-fetch they simply get
  re-judged. This keeps the only unbounded table bounded.

---

## 9. Token-bloat guardrails (the core user concern, enumerated)

1. **Server-owned SQLite** — the AI never opens `studio.db` directly; it acts
   through bounded API/CLI queries.
2. **Skill reads only the delta** — `WHERE judged_at IS NULL` — never the whole
   `raw_signal` or `ideas` table.
3. **Dedup is a targeted query**, not a full-table load
   (`WHERE id = hash(source, external_id)`).
4. **Promote/reject leave the active view** (`status IN ('new','keep')` only) →
   the working backlog shrinks as you triage.
5. **Prune deletes old judged `raw_signal`** (the one growing table) past a
   retention window → the only unbounded store stays bounded.
6. **The board UI reads via paginated API**, not via the AI.

Net: AI context cost is **constant** regardless of how long the tool runs or how
many ideas accumulate.

---

## 10. Frontend & UX

**This section specifies the information architecture and interactions the UI
must realize. The visual language — typography, color, spacing, motion, exact
layout — is produced by a dedicated `frontend-design` pass (the next step after
this doc is approved, before any implementation), surveying real reference apps
(Linear, Notion, Trello-style boards, content-calendar tools) per the user's
request. That pass appends its output to this doc as §10.1.**

**Information architecture (decided):**

- **Two top-level views**, switchable: **Ideas** and **Pipeline**.
- **Ideas view** — the triage surface. Cards grouped or filterable by `type`
  (mirror / comment_demand / trend) and `status` (new / keep). Each card shows:
  title, the skill's `rationale`, source + evidence (views / points / comment
  quotes + count / date), and a duration hint for YouTube sources. Per-card
  actions: **keep**, **reject**, **confirm or override the suggested kind**
  (long / short / series; the AI suggestion shows a `·ai` marker until the human
  confirms), add **notes**, **promote**. A "run discovery" affordance surfaces
  incoming raw counts.
- **Pipeline view** — the 12-stage board, ported behavior: draggable cards
  across stages, click-to-open detail panel (title/slug/folder, stage selector,
  artifact checklist, notes, delete), Sync to rescan `videos/`, drift flag,
  add-card, keyboard shortcuts.
- **Cross-view link** — promoting in Ideas lands a card in Pipeline's `Idea`
  stage; the two views share the running app, not separate tools.

**Constraints for the visual pass:** single coherent design system across both
views (the board and the backlog must feel like one app, not two bolted
together); restraint over decoration; the existing `kanban.html` warm-dark /
copper palette is a *reference point to evaluate*, not a mandate — the pass
rethinks from scratch.

### 10.1 Visual language — **The Wire Desk** (decided)

The frontend-design pass ran three independent directions through an adversarial
judge panel. The winner (26/30) is **The Wire Desk**. It was the only direction
to break the dark-mode monoculture entirely — a *daylight assignment desk, ink
on newsprint* — which is the cleanest single move away from both the old
copper-on-charcoal identity and the near-black-plus-one-accent AI default. A
working mockup of both views with sample data lives at
**`tools/studio/design/mockup.html`** — it is the visual source of truth for the
build.

**Thesis.** The whole app is a *meter*. Raw dispatches arrive on **The Wire**
(Ideas) cold and unleveled; as a story commits and moves down **The Desk**
(Pipeline) its meter fills and warms toward a single saturated broadcast-red
**ON-AIR** at Published. Editorial confidence (a characterful display voice, real
measure, generous radius) gives it assignment-desk gravity with zero broadsheet
hairlines.

**Palette (final — after cutting teal's accent-creep so it does ONE job).**

| Token | Hex | Role |
|---|---|---|
| Newsprint | `#EDE9E0` | App background — cool rag paper (NOT cream `#F4F1EA`) |
| Card Stock | `#FBFAF6` | Raised surfaces: cards, lanes, panels (lifted by soft shadow, never a border) |
| Card Sunk | `#E5E0D6` | Inset troughs on the desk; empty meter segments |
| Press Ink | `#1C1A17` | Primary text + display (warm near-black, never `#000`) |
| Graphite | `#6F6A61` | Secondary text, metadata, all mono readouts |
| **Signal Teal** | `#2C6E6A` | **Meter ramp COLD pole only** (raw / low level) |
| **On-Air Red** | `#D6402E` | **The one saved color** — meter peak, ON-AIR, the commit/promote moment. Strictly rationed; never a wash, header, or background |

Interaction neutrals (the Chanel cut): focus rings and the keep affordance are
**ink/graphite**, never teal. The only two *data* colors in the whole app are the
meter ramp `Signal Teal → On-Air Red`.

**Type (three tiers, hard boundaries).**
- **Display — Bricolage Grotesque** (700/800): wordmark, idea titles, stage names. The deliberate anti-Fraunces, characterful-but-mechanical voice.
- **Body — Inter**: UI chrome, rationale lines, notes, panel copy.
- **Utility — JetBrains Mono**: scoped to a `.num` / `[data-mono]` class for *measured/coded* values ONLY (timecodes, view/point/comment counts, durations, slugs, paths, dates). Never body — that was the old tool's mistake.

**Signature — THE LEVEL METER (one law across both views).** A tiny VU/signal
meter is the single shared gene. On **The Wire** it stands *vertical* as a
5-segment notch on each dispatch's left edge: **fill height = the AI's rationale
lean** (raw → pursue), segments colored along the shared ramp (cold teal at the
base, warming to red at the top) — a lean, never a number, never a grade. On
**The Desk** it lies *horizontal* as a continuous level-bar under each card title:
**fill width = artifact progress derived from the `videos/` scan** (real files on
disk, not a hand-set value). Both run the identical `teal → red` ramp, so the
whole cockpit reads at a glance as a wall of meters at different levels, and
"committing" a story is literally a meter peaking into the red. The **commit
animation** — a dispatch's strip flashing On-Air Red as it leaves the wire ==
a card peaking red as it lands in Published — is the seam that makes the two
views one app.

**Grafted from the runner-up directions (judge's synthesis):**
- **Left-rail band filter** (Mirror / Comment-demand / Trend, each with a live count + a subject glyph) — the best triage affordance for a single power user scanning mixed signal.
- **Subject type-glyphs**, inline before each idea title: a vectorscope target = *mirror*, a waveform tick = *comment-demand*, a rising-trace = *trend*. These carry source type so the meter stays pure-lean.
- **A meter legend/key** in both views that teaches the `raw → pursue` / `idea → on-air` ramp on sight.
- **Squelch reject**: a rejected dispatch desaturates and drops out of the wire — a crisp "cut from feed" gesture.

**Build watchouts (carried into the plan):**
1. **Don't drift into the cream default** — `#EDE9E0` is only ~7–10/channel off the forbidden cream; lock body to Inter, Bricolage at display sizes only, and never let On-Air Red become a decorative wash (it appears solely on the meter peak, the commit flash, and the ON-AIR dot).
2. **Two data-color tokens** (`--meter-cold`, `--meter-hot`) used ONLY by meter/commit; a separate neutral `--focus`. If teal appears outside a meter/progress fill, it's a regression.
3. **Mono is a scoped utility**, document default Inter — never `font-family:mono` on `body` (the old kanban's exact sin).
4. **Namespace every component class** (`.wire-meter`, `.desk-meter`, `.band-filter`); never a bare generic class (`.hot`, `.cold`, `.x`) that could match a nested container — per project memory on scene-class collisions.
5. **Light-mode shadow discipline** — soft Card-Stock shadows + inset troughs with enough spread to register on `#EDE9E0`; zero hairlines (the anti-default-#3 promise).
6. **The meter must encode real data, not a fake score** — wire = a 2–3 state lean notch; desk = artifact-completion from the actual `videos/` scan.
7. **One shared token layer** (one radius `6px`, one shadow scale, one type scale) across both views from the start, so they never read as two bolted-together apps.
8. **Keyboard-first** — wire the core triage keys (navigate, keep, reject, promote, set-kind) + a `⌘K` palette; an unwired hint strip is editorial chrome.
9. **The AI-suggested-format marker is muted, never the saved color** — an AI `kind` suggestion shows a small mono `·ai` marker on the format chip (graphite / `--press-ink` on `--card-sunk`), with `kind_why` as the hover tooltip; confirming clears the marker. On-Air Red stays rationed to the meter peak / ON-AIR / commit — the format chip and its `·ai` marker are never red. (Full interface contract: `2026-06-22-studio-kind-suggestion-design.md`.)

---

## 11. Migration & retirement

- **`kanban.html`** → retired. Port into `tools/studio`: the 12 stages, the
  `videos/` scan logic, drag-drop, detail panel, drift detection, keyboard
  shortcuts. The file remains in git history; remove or leave dormant at the root
  (decided in the plan — default: leave the file, stop maintaining it, note in
  the root `CLAUDE.md`/README that `tools/studio` supersedes it).
- **`tools/topic-pipeline/`** → retired. Harvest into `discovery/`: the free-API
  fetchers (HN/Reddit/Lobsters/daily.dev), the channel-feed yt-dlp approach
  (extended with comments), the discovered-channels and prune/graveyard ideas.
  Drop: the 6-axis rubric, `needs_judgment`/`angle_demand`/LLM judgment phase,
  the daily `SCHEDULED_TASK_PROMPT` cron. The folder remains in git history; its
  `data/inbox.json` (61 items with `user_status`) is a **one-time import
  candidate** — a migration step can seed `ideas` from any `go`/`later`/`shipped`
  entries so existing decisions aren't lost (decided in the plan).
- Update root `CLAUDE.md` to point authoring/idea workflows at `tools/studio` and
  note the two retirements.

---

## 12. Testing strategy

- **Discovery CLI (Python)** — unit-test the pure argv builders (yt-dlp command
  construction, like `tools/inspo-ingest`) and the aggregator response parsers
  with fixture JSON. No network in tests.
- **Server (TS)** — test `scan.ts` against a temp `videos/` fixture tree; test
  the `ApiResponse` envelope, dedup hashing, and promote/prune transitions
  against a temp SQLite file.
- **Skill** — exercise the worth-pursuing flow on a small fixture `raw_signal`
  set; assert it reads only unjudged rows, writes `rationale`, suggests a `kind`
  with `kind_source='ai'` + `kind_why`, and marks rows judged.
- **Feasibility spike (before build)** — the single-video comment fetch (§7.4) is
  validated first; the whole discovery feature depends on it.

---

## 13. Risks & open items

1. **Bot-wall on comments (highest).** Mitigations in §7.4; validated first.
2. **yt-dlp comment volume/shape varies** by video; the parser must tolerate
   missing/limited comments and degrade.
3. **daily.dev GraphQL / Lobsters RSS drift** — ported fetchers may need
   refreshing; covered by fixture-based parser tests + graceful per-source
   failure (one dead source never fails the run).
4. **Slug collision on promote** — reuse `kanban.html`'s uniqueness rule
   (slug + date unique).
5. **`studio.db` durability** — gitignored/rebuildable by design; if the human
   wants `board_overlay` to survive a machine move, add the optional JSON
   snapshot (§14).

---

## 14. Out of scope / future

- Optional scheduled discovery run (cron) — explicitly *not* in this phase.
- Committed JSON snapshot mirror of `board_overlay` for cross-machine durability.
- Any scoring/ranking — permanently out of scope by D4.
- In-app AI curation button (would require the server to invoke an AI; the skill
  path stays the intelligence home).

---

## 15. Build phases (high-level; detailed plan via `writing-plans`)

0. **Feasibility spike** — validate single-video comment fetch (§7.4).
1. **Frontend-design pass** — visual language (§10), appended as §10.1.
2. **Scaffold** `tools/studio` (bun + Hono + Vite + React), ports `:3273`/`:5273`,
   SQLite + migrations.
3. **Pipeline view** — port `kanban.html` (scan, board, promote target).
4. **Discovery CLI** — yt-dlp channels+comments + aggregator fetchers → `raw_signal`.
5. **Ideas view** — triage UI over `ideas`.
6. **The skill** (`/skill-creator`) — worth-pursuing curation over `raw_signal`.
7. **Migration** — seed channels, optional `inbox.json` import, retire notes.
8. **Tests + docs** — per §12; `CLAUDE.md`/README.
```
