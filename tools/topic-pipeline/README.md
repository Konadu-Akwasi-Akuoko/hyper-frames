# tools/topic-pipeline

> **RETIRED 2026-06-22** — superseded by `tools/studio` (idea aggregator + board).
> Its free-API fetchers and channel yt-dlp approach were harvested into
> `tools/studio/discovery/`; the scoring rubric / LLM judgment / daily cron were
> dropped by design. Kept for reference only; no longer maintained.

Daily topic-discovery + popularity-scoring system for the hyper-frames
YouTube channel.

Surfaces fresh tech content from four text aggregators, probes YouTube
demand and Tier B/C reference-channel coverage, generates 1–5 video
angle proposals per candidate via an LLM judgment phase, and produces
an interactive dashboard for review.

The scoring rubric is the v2 6-axis system documented in `RUBRIC.md`;
the daily operational runbook is `SCHEDULED_TASK_PROMPT.md`. This README
is the orientation doc — read those two for the authoritative spec.

## What it does

```
Daily scheduled run
  ↓
  fetch.py             → data/archive/YYYY-MM-DD/{shortlist,raw,run_meta}.json
  competitors.py       → data/competitors/feed.json + .../competitors.json
  cold_search.py       → data/archive/YYYY-MM-DD/ytsearch.json
  autocomplete.py      → data/archive/YYYY-MM-DD/autocomplete.json
  inspiration.py       → data/archive/YYYY-MM-DD/inspiration.json
  needs_judgment.py    → data/archive/YYYY-MM-DD/pending.json
                          ↓
  Claude reads each pending article, applies the v2 LLM rubric
  (yt_competition + per-angle audience_reach / curiosity_hook /
   computing_depth), generates 1–5 angles per candidate
                          ↓
                         data/archive/YYYY-MM-DD/judgment.json
                          ↓
  angle_demand.py      → data/archive/YYYY-MM-DD/angle_demand.json
  merge.py             → data/inbox.json (persistent, preserves user_status)
  render.py            → data/dashboard.html + data/inbox.md
                          ↓
  apply_decisions.py   → folds in any exported dashboard decisions
                          ↓
  Summary posted in chat
```

Weekly (manual): `clusters.py`, `prune.py`, `discover_channels.py`.

## Sources (all free, unauthenticated)

| Source | Mechanism |
|---|---|
| Hacker News | HN Algolia API — `/api/v1/search_by_date` |
| Reddit | JSON API — `r/{programming,compsci,webdev,databases,cpp,rust,golang}/top.json` |
| Lobste.rs | Public RSS — `https://lobste.rs/rss` |
| daily.dev | GraphQL — `anonymousFeed(ranking: POPULARITY)` |
| YouTube | yt-dlp against Tier B/C channel feeds + per-candidate `ytsearch10:` |

Tier A (the four text aggregators) is configured in `config.json:sources`.
Tier B (style-reference) and Tier C (watchlist) channels live in
`config.json:reference_channels`. See `RUBRIC.md` for the tiering rules.

## Scoring rubric (6 axes, 0–20 each → composite /120, displayed /100)

Three axes are properties of the **source/topic**, three are properties
of the **angle**. Each candidate carries 1–5 angles; angle composite uses
the candidate-level axes plus the angle-level axes.

| Axis | Stage | What it measures |
|---|---|---|
| 1. Demand | mechanical (composed in merge.py) | Sum of four sub-caps: aggregator_breadth (0-4) + cold_search (0-5) + autocomplete (0-3) + tier_b_hit (0-8) |
| 2. Evergreen | mechanical (fetch.py) | Title/URL regex: ephemeral keywords penalize, evergreen keywords reward |
| 3. YT competition | LLM, with cooldown overlay | 0 = saturated by Tier B/C; 20 = no high-quality video exists. 30-day cooldown forces ≤4 if Tier B covered the topic recently |
| 4. Audience reach | LLM, per angle | Who has experienced the thing? 20 = every internet user; 0 = sub-niche |
| 5. Curiosity hook | LLM, per angle | Does the angle shape into a Tier B-style title? Test against 5 hook patterns |
| 6. Computing depth | LLM, per angle | Does the honest answer involve computing? Keeps the channel on-brand |

```
composite = demand + evergreen + yt_competition
          + audience_reach + curiosity_hook + computing_depth
display   = round(composite / 1.2)        # 0-100 for the dashboard
best      = angle with max composite for the candidate
```

Full rubric, hook-pattern definitions, and worked examples: `RUBRIC.md`.
v1→v2 calibration evidence: `CALIBRATION-2026-05-08.md`.

## Files

```
tools/topic-pipeline/
├── README.md                       this file
├── RUBRIC.md                       v2 scoring rubric (authoritative)
├── CALIBRATION-2026-05-08.md       v1→v2 hand-rescore validation
├── SCHEDULED_TASK_PROMPT.md        the prompt the scheduled Claude task runs daily
├── config.json                     sources, channels, filters, paths
├── fetch.py                        Tier A fetch + dedup + mechanical pre-rank
├── competitors.py                  Tier B/C channel feed via yt-dlp
├── cold_search.py                  per-candidate YouTube demand + cooldown probes
├── autocomplete.py                 YouTube autocomplete demand sub-cap
├── inspiration.py                  Tier B mood board + starter angles
├── needs_judgment.py               filters shortlist to candidates lacking angles
├── angle_demand.py                 re-probes demand on LLM-proposed angle titles
├── merge.py                        composes the v2 6-axis composite into inbox.json
├── render.py                       dashboard.html + inbox.md generator
├── apply_decisions.py              applies exported dashboard decisions
├── clusters.py                     groups near-duplicate inbox candidates
├── prune.py                        ages stale candidates to graveyard.json
├── discover_channels.py            promotes recurring untracked channels
└── data/
    ├── inbox.json                  persistent state, source of truth (committed)
    ├── inbox.md                    flat scannable digest of inbox (committed)
    ├── dashboard.html              interactive review surface (committed)
    ├── graveyard.json              aged-out candidates (committed; never deleted)
    ├── clusters.json               output of clusters.py
    ├── discovered_channels.json    output of discover_channels.py
    ├── decisions.json              user's exported go/pass/later decisions (gitignored)
    ├── decisions-applied-*.json    archived after apply_decisions.py runs (gitignored)
    ├── competitors/feed.json       latest Tier B/C channel snapshot
    ├── cold-search/                frozen calibration probes (see its README)
    └── archive/
        └── YYYY-MM-DD/             one folder per daily run (gitignored)
            ├── shortlist.json      mechanical shortlist for that day
            ├── raw.json            full fetch for that day
            ├── run_meta.json       per-source counts + errors
            ├── competitors.json    dated copy of the day's competitor feed
            ├── ytsearch.json       cold-search results
            ├── autocomplete.json   autocomplete probe results
            ├── inspiration.json    mood board + starter angles
            ├── pending.json        ids needing LLM judgment
            ├── judgment.json       LLM judgment output for that day
            └── angle_demand.json   angle-aware demand re-probes
```

## Running manually

All commands run from `tools/topic-pipeline/`. Substitute the day under
`data/archive/` for `YYYY-MM-DD`.

```bash
cd tools/topic-pipeline

# 1. Tier A fetch
python3 fetch.py
python3 fetch.py --dry-run            # see what would come back

# 2. Refresh Tier B/C channel feed (~5 min)
python3 competitors.py

# 3. Cold-search demand probes (~3-5 min)
python3 cold_search.py --candidates data/archive/YYYY-MM-DD/shortlist.json

# 4. Autocomplete probes (~10 s)
python3 autocomplete.py --candidates data/archive/YYYY-MM-DD/shortlist.json

# 4b. Mood board + starter angles
python3 inspiration.py --candidates data/archive/YYYY-MM-DD/shortlist.json

# 5. Materialize the not-yet-judged subset for the LLM phase
python3 needs_judgment.py \
  --shortlist data/archive/YYYY-MM-DD/shortlist.json \
  --format json > data/archive/YYYY-MM-DD/pending.json

# 5. (manual / Claude) — apply the v2 LLM rubric to each pending candidate
#    and write data/archive/YYYY-MM-DD/judgment.json. See SCHEDULED_TASK_PROMPT.md.

# 5b. Re-probe demand on the LLM-proposed angle titles
python3 angle_demand.py --top-n 20

# 6. Compose the v2 6-axis composite into inbox.json
python3 merge.py \
  --shortlist     data/archive/YYYY-MM-DD/shortlist.json \
  --judgment      data/archive/YYYY-MM-DD/judgment.json \
  --ytsearch      data/archive/YYYY-MM-DD/ytsearch.json \
  --autocomplete  data/archive/YYYY-MM-DD/autocomplete.json \
  --angle-demand  data/archive/YYYY-MM-DD/angle_demand.json

# 7. Regenerate the dashboard + inbox.md
python3 render.py

# 8. Fold in any exported dashboard decisions
python3 apply_decisions.py            # auto-archives decisions.json
python3 apply_decisions.py --dry-run  # preview
python3 apply_decisions.py --keep     # don't rename decisions.json after applying

# 8a. (optional) cluster duplicates
python3 clusters.py

# 8b. (weekly) prune stale candidates
python3 prune.py --dry-run            # always preview first
python3 prune.py

# 8c. (weekly) auto-discover niche channels
python3 discover_channels.py

# Open the dashboard
open data/dashboard.html
```

## Running as a scheduled task

The full daily flow is `SCHEDULED_TASK_PROMPT.md`. Register that prompt
as a daily Claude scheduled task. It executes the steps above end-to-end,
posts a chat summary, and surfaces silent degradations (e.g. Reddit
429-throttling) via `run_meta.json` instead of hiding them behind a low
candidate count.

## Reviewing candidates

Open `data/dashboard.html` in a browser. The left sidebar splits views by
**Inspiration** source (All / HN / Reddit / Lobste.rs / daily.dev /
YouTube) and **Status** (Unreviewed / Pending / All / Go / Later / Pass /
Shipped).

Each candidate card shows:

- The 3 source-level axes (demand / evergreen / yt-competition) as bar
  charts, with the demand sub-cap breakdown (`breadth · cold · auto ·
  TierB`) inline.
- All angles ranked by composite, the best one starred. Each angle
  carries audience / hook / depth scores and any LLM judgment notes.
- **Go on this angle** per angle; **Pass** / **Later** / **Mark shipped**
  per candidate. Shipped candidates record the video folder slug and
  link directly to `videos/<slug>-<date>/`.
- **Export decisions** — downloads a JSON of localStorage state. Save to
  `data/decisions.json` and the next pipeline run merges those statuses
  back via `apply_decisions.py`.

The YouTube tab shows the latest Tier B/C feed. The **Inspire from this**
button queues a Tier B/C video as a new pending-judgment candidate; on
export it lands in `decisions.json:create_candidates[]`, and the next
fetch run pulls it through cold-search → autocomplete → judgment.

Both status decisions and the YouTube inspiration queue persist in
browser localStorage between sessions.

## Adding a Tier A source

1. Write a `fetch_<source>(...)` function in `fetch.py` that returns a
   list of dicts with the canonical fields:
   `source, title, url, external_id, points, comments, created_at, comments_url, tags`.
   Note: in v2 only the source *name* feeds the composite (via
   aggregator_breadth, capped at 4). `points`/`comments` are kept for
   per-source records but no longer affect scoring.
2. Add a section under `config.json:sources` with that source's settings.
3. Add a `run_source(...)` call in `fetch.py:main()`.
4. (Optional) Add a colored source-tag style in `render.py`'s dashboard CSS.

## Adding a Tier B or Tier C channel

Edit `config.json:reference_channels.style_reference` (Tier B) or
`.watchlist` (Tier C). The next `competitors.py` run picks it up, and
both `cold_search.py` (cooldown overlay) and `inspiration.py` (mood
board) start using it automatically.

`discover_channels.py` surfaces untracked channels that recur across
cold-search results — a good source of Tier B/C promotion candidates.

## Tuning

Most levers are in `config.json`:

- **Per-source minimums** (`min_points`, `min_score`, `min_upvotes`) —
  how aggressive each source's pre-filter is.
- **Evergreen keyword sets** — what counts as ephemeral vs. evergreen.
- **Drop patterns** — minimal platform-admin filters (Ask HN, hiring
  threads, etc.).
- **Shortlist size + min mechanical score** — how many candidates the
  LLM judges per run.
- **`reference_channels.videos_per_channel` / `fetch_concurrency`** —
  competitor-feed depth and parallelism.

Topic relevance filtering (is this a video-worthy technical topic?)
lives entirely in the LLM judgment stage — see `SCHEDULED_TASK_PROMPT.md`.
