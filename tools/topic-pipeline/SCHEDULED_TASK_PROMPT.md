# Daily topic-pipeline run — scheduled task prompt

Run this prompt once per day. It refreshes the topic-discovery inbox and
dashboard at `/Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/topic-pipeline/data/`.

The pipeline scores topics for a YouTube channel publishing **curiosity-driven
videos about computing, software engineering, and technology**, in the
direction of Pawel / Veritasium / Cleo Abram / Computerphile / Kurzgesagt.
The full design lives in `RUBRIC.md` (v2 6-axis rubric); this prompt is the
operational runbook that produces it.

---

## Task

Execute this procedure exactly. Do not improvise the order of operations.

### 0. Prerequisites

Working directory: `/Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/topic-pipeline/`

Use `Bash` for shell commands and `WebFetch` for reading articles. The Python
scripts use only the standard library plus `yt-dlp` (already on PATH).

### 1. Fetch — pull the day's candidates from text aggregators

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/topic-pipeline
python3 fetch.py
```

Produces under `data/archive/YYYY-MM-DD/`:
- `shortlist.json` — top 60 candidates by mechanical pre-rank (aggregator breadth + evergreen)
- `raw.json` — full pre-filter set
- `run_meta.json` — per-source counts + error strings (read this in step 9
  for the chat summary so silent degradations like Reddit 429-throttling
  surface explicitly instead of looking like a quiet day)

Single-source failures (HN / Reddit / Lobste.rs / daily.dev) are logged and
non-fatal. Note today's date — you'll reuse it.

`fetch.py` also folds in any `pending_judgment=true` YouTube candidates from
`inbox.json` (created via the dashboard's "Inspire from this" flow + applied
by `apply_decisions.py`). They ride along in the shortlist with their
mechanical subtotal so cold-search, autocomplete, inspiration, and judgment
all process them on the next run — the loop closes itself. Look for
`[inbox]    + N pending YouTube candidates` in the fetch.py log.

### 2. Refresh the competitor channel feed (Tier B + Tier C)

```bash
python3 competitors.py
```

Pulls the latest 25 videos from each style-reference (Tier B, 13 channels)
and watchlist (Tier C, 5 channels) channel via yt-dlp. Writes
`data/competitors/feed.json` and `data/archive/YYYY-MM-DD/competitors.json`.
~3-5 minutes wall-clock.

This data feeds (a) the 30-day cooldown overlay applied in `merge.py` and
(b) the inspiration-mode mood board for angle generation.

### 3. Cold-search demand probes

```bash
python3 cold_search.py --candidates data/archive/YYYY-MM-DD/shortlist.json
```

Per candidate, runs `ytsearch10:` on the title-derived query. Records:
- `demand_score` (0–5) — median view count of top-5 results
- `tier_b_hits` / `tier_c_hits` — tracked channels in the results, with
  `days_ago` for cooldown logic
- `untracked_channels` — surfacing data for `#112` auto-discovery

Output: `data/archive/YYYY-MM-DD/ytsearch.json`. ~3-5 minutes.

### 4. Autocomplete probes

```bash
python3 autocomplete.py --candidates data/archive/YYYY-MM-DD/shortlist.json
```

Per candidate, hits the public Google suggest endpoint (full title + 4-word
prefix stem) and scores 0/1/3 by Jaccard overlap. Output:
`data/archive/YYYY-MM-DD/autocomplete.json`. ~10 seconds.

### 4b. Inspiration — Tier B mood board + starter angles

```bash
python3 inspiration.py --candidates data/archive/YYYY-MM-DD/shortlist.json
```

Per candidate, scores Jaccard similarity against every Tier B video title in
`data/competitors/feed.json`, keeps the top 5 (the **mood board**), classifies
the candidate's shape (project / exploit / primer / tool / opinion / news),
and emits 0–3 **starter angles** by instantiating the curiosity-hook patterns
from RUBRIC.md against a topic seed extracted from the title. News and most
opinion candidates skip starter generation. Output:
`data/archive/YYYY-MM-DD/inspiration.json`. ~1 second.

Starter angles are deliberately rough: each is prefixed with `[<pattern>]`
(e.g. `[hidden-mechanism] Why <topic> actually works the way it does`) so the
judgment phase treats them as drafts, not finished titles.

### 5. Judge — apply the v2 LLM rubric to each shortlist candidate

First, materialize the not-yet-judged subset so judgment never re-runs on
candidates that already have angles in inbox.json:

```bash
python3 needs_judgment.py \
  --shortlist data/archive/YYYY-MM-DD/shortlist.json \
  --format json > data/archive/YYYY-MM-DD/pending.json
```

Read `data/archive/YYYY-MM-DD/pending.json` (an array of
`{id, title, url, sources, mechanical_subtotal}`) — this is the working set
for the LLM judgment phase. The helper enforces the "skip already-judged"
rule in code, not in prompt text. (merge.py also warns if judgment.json ever
contains ids that already had angles, as a belt-and-suspenders check.)

For each candidate in `pending.json`:

1. Fetch the article body via `WebFetch` on its `url`. If paywalled, judge
   from title + metadata only and mark `notes` accordingly.
2. Apply the v2 rubric below and produce a structured record.

Write the accumulated results to `data/archive/YYYY-MM-DD/judgment.json`.

#### v2 judgment rubric (3 LLM-scored axes)

The mechanical pipeline already produced demand (sub-caps from cold-search +
autocomplete + Tier B hits + aggregator breadth) and evergreen, and merge.py
applies the cooldown overlay automatically. **Your job in the judgment phase
is to score the 3 LLM axes** below: one candidate-level (yt_competition),
two angle-level (audience_reach, curiosity_hook, computing_depth — three but
all tied to angles).

**Axis 3 — yt_competition (0-20, candidate-level, applied to all angles)**
Search YouTube via `WebFetch` on
`https://www.youtube.com/results?search_query=<query>` and read the top 5
results. (Cross-reference `data/archive/YYYY-MM-DD/ytsearch.json` for the
yt-dlp-fetched view counts and dates — that data is already there.)

- 20 = no high-quality video on this topic exists
- 14 = one or two videos exist but old, low-engagement, or beginner-only
- 8 = multiple recent videos but none at high production quality
- 0 = saturated; a Tier B / Tier C channel covered it well at scale

(merge.py applies the 30-day cooldown overlay automatically — it sees the
ytsearch.json `tier_b_hits` / `tier_c_hits` and forces the score down where
appropriate. You score the *open-lane question* honestly; the overlay is
mechanical.)

**Axis 4 — audience_reach (0-20, per-angle)** *Who has experienced the thing?*

- 20 = every internet user (CAPTCHAs, password rules, autocorrect, Wi-Fi)
- 14 = every computer user (file dialogs, fonts, lossy JPEGs)
- 8 = every working developer (git, regex, JSON)
- 4 = every backend engineer (consensus, MVCC, CAP)
- 0 = a sub-niche (specific ISA dialects, kernel fastpath internals)

**Axis 5 — curiosity_hook (0-20, per-angle)** *Does the angle shape into a
Tier B-style title?*

Try to phrase the angle's title in 3 of these 5 patterns and judge how
natural the fit is:
- Hidden-mechanism reveal — *"The X inside every Y"*, *"Why Y actually does X"*
- Counterintuitive twist — *"Why X is harder/slower/weirder than you think"*
- Personal-stake question — *"How easy is it to X?"*, *"Why can't I X?"*
- Hyper-claim with story — *"The most X Y ever made"*
- Mystery / unsolved — *"The X nobody can explain"*

If the topic resists 4+ patterns, it's a build-log topic, not a curiosity
topic — score low. Score reflects how naturally a curious non-expert would
form the question on their own.

**Axis 6 — computing_depth (0-20, per-angle)** *Does the honest answer
involve computing?* Independent of curiosity; this keeps the channel on-brand.

- 20 = central computing topic (algorithms, OS internals, networking
  protocols, cryptography, compilers, distributed systems primitives,
  rendering pipelines, computer vision, ML internals)
- 14 = adjacent — answer touches computing meaningfully but isn't the core
- 8 = answer mostly non-computing but has a computing angle if pulled
- 0 = answer doesn't involve computing at all

#### Angle generation rules

For each candidate, generate **between 1 and 5 angles**:

1. **Angle 1 is always the article's own framing.** Score it on its own
   merits — sometimes the article framing is the right video.
2. **Angles 2-5 are reframes.** Each must be:
   - Meaningfully distinct from each other and from Angle 1 (not rephrasings)
   - A viable curiosity-driven 5-10 min video on its own
   - Phrased as a Tier B-style title (use the curiosity-hook patterns above)
3. **Inspiration mode (now automated by `inspiration.py`):** read
   `data/archive/YYYY-MM-DD/inspiration.json[<cid>]` before writing angles.
   - `mood_board` — 3-5 Tier B titles closest by Jaccard. Use them as a
     reference for **title shape, not content**. If a Tier B channel has a
     near-duplicate title (similarity ≥ 0.30), prefer reframes that move
     to a *different* angle on the same topic. Also check
     `upload_date`: a high-similarity Tier B hit at scale (≥ 100K views)
     within the last ~12 months is a saturation signal — drop
     `yt_competition` toward 0-4 even when no cold-search cooldown fires.
   - `starter_angles` — 0-3 templated drafts. Treat them as inspiration:
     keep the *pattern* (hidden-mechanism / counterintuitive-twist /
     personal-stake / hyper-claim / mystery), rewrite the title in
     production-quality wording, refine the lens, then score on the v2
     rubric. Discard a starter if the pattern doesn't fit the candidate.
   - `candidate_shape` — `news` / `opinion` candidates emit no starters.
     Score article framing only; do not invent reframes for non-technical
     content (consistent with rule 5 below).
4. **Cooldown-adjacent generation:** if `data/archive/YYYY-MM-DD/ytsearch.json`
   shows a `tier_b_hits` or `tier_c_hits` entry within 30 days for this
   candidate, the generator must produce angles *meaningfully adjacent* to
   that existing video's angle. Direct duplicates are forbidden.
5. **Junk filter:** if the candidate is news, opinion, business, or
   lifestyle with no computing handle, still produce Angle 1 but score it
   honestly low (audience_reach 0-4 OR computing_depth 0-4 → composite
   buries it). Do not invent reframes for non-technical content.
6. Cap at 5 angles total. Strong candidates have 2-3; weak candidates have 1.

Each angle's record:
- `title`: punchy one-sentence video title
- `lens`: 3-8 word description of the angle's framing
- `is_original_article_framing`: true only for Angle 1
- `scores.audience_reach`: 0-20
- `scores.curiosity_hook`: 0-20
- `scores.computing_depth`: 0-20
- `notes` (optional): 1-2 sentences

#### Output schema

Write to `data/archive/YYYY-MM-DD/judgment.json`:

```json
{
  "generated_at": "ISO-8601",
  "candidates": {
    "<candidate_id>": {
      "yt_competition": 14,
      "angles": [
        {
          "is_original_article_framing": true,
          "title": "Why dark mode wasn't a toggle — it was a system refactor",
          "lens": "frontend system architecture",
          "scores": {
            "audience_reach": 14,
            "curiosity_hook": 12,
            "computing_depth": 12
          },
          "notes": "Article framing. Mid-tier candidate."
        },
        {
          "is_original_article_framing": false,
          "title": "Why your eye sees the same gray differently at 8am and 8pm",
          "lens": "human visual system + display internals",
          "scores": {
            "audience_reach": 18,
            "curiosity_hook": 18,
            "computing_depth": 16
          },
          "notes": "Deeper perceptual angle; ties to text-rendering video."
        }
      ]
    }
  }
}
```

### 5b. Angle-aware demand probing

```bash
python3 angle_demand.py --top-n 20
```

Re-probes cold-search + autocomplete on each LLM-proposed angle (not just the
candidate title). Closes the calibration gap where jargon-heavy titles
(e.g. "WEI repackaged") understated demand because nobody types that into
YouTube — viewers search "captcha." Per candidate, takes the **max** demand
sub-cap across angles and writes `angle_demand.json`.

Defaults to top-20 by mechanical rank to bound API calls
(60 × 3 angles = 180 ytsearch probes ≈ 6 minutes; top-20 keeps it under 2).
The merge step lifts a candidate's `cold_search` / `autocomplete` /
`tier_b_hit` sub-caps when the angle out-probes the title — the lift never
decreases a title-probe value.

### 6. Merge — compose the v2 6-axis composite

```bash
python3 merge.py \
  --shortlist data/archive/YYYY-MM-DD/shortlist.json \
  --judgment data/archive/YYYY-MM-DD/judgment.json \
  --ytsearch data/archive/YYYY-MM-DD/ytsearch.json \
  --autocomplete data/archive/YYYY-MM-DD/autocomplete.json \
  --angle-demand data/archive/YYYY-MM-DD/angle_demand.json
```

merge.py composes the demand axis from the four sub-caps (taking the per-
sub-cap max of title-probe vs. angle-probe), applies the 30-day cooldown
overlay to yt_competition, computes per-angle composites (sum of 6 axes /
1.2 → 0-100), updates `data/inbox.json` in place, and preserves any
`user_status` / `user_notes` set previously. Watch for `angle_lifts=N` in
the merge log — that's the count of candidates whose demand was lifted by
an angle reframe.

### 7. Render

```bash
python3 render.py
```

Regenerates `data/dashboard.html` from `data/inbox.json`.

### 8. Apply user decisions (if any)

If `data/decisions.json` exists, the user has exported decisions from the
dashboard since the last run. Apply them with:

```bash
python3 apply_decisions.py
python3 render.py
```

`apply_decisions.py` handles two flows:

- **Status updates** (`go` / `pass` / `later` / `shipped` + selected angle
  index) — merged into `user_status` / `user_selected_angle_index` on the
  matching inbox entry. `shipped` also writes `video_folder` (e.g.
  `videos/<slug>-<YYYY-MM-DD>`) so the inbox remembers which video the
  candidate became. `shipped` is immune to `prune.py` and is hidden from the
  default "All (active)" status view; use the "Shipped" sidebar entry to
  revisit them.
- **YouTube-derived candidates** (the dashboard's "Inspire from this" button on
  the YouTube tab) — creates a new pending-judgment candidate with
  `sources=["youtube"]`, hashing the YouTube URL with the same scheme as
  aggregator candidates. The next pipeline run picks them up for
  cold-search / autocomplete / judgment alongside the day's HN/Reddit batch.

By default the script renames `decisions.json` to
`decisions-applied-<UTC-timestamp>.json` after a successful apply so it isn't
double-processed. Pass `--keep` to disable the rename, `--dry-run` to preview.

### 8a. (Optional) Cluster duplicates

```bash
python3 clusters.py
```

Reads `data/inbox.json` and groups candidates whose title + tags + angle
lenses pairwise-Jaccard ≥ 0.25. When the same article gets posted from
multiple sources or different framings of the same news beat surface
together, this lets you pick one and `pass` the rest instead of judging
each separately. Output: `data/clusters.json` plus a stderr summary of
the top clusters. Run it after merge.py if the inbox feels noisy.

### 8b. (Weekly) Prune stale candidates to graveyard

```bash
python3 prune.py --dry-run    # always preview first
python3 prune.py              # apply
```

Moves candidates from `inbox.json` to `graveyard.json`:
- unreviewed for ≥ 30 days
- `later` for ≥ 60 days
- `pass` for ≥ 90 days

`go` and `shipped` are never pruned. Each moved record gets
`graveyarded_at` + `graveyard_reason` so nothing is lost. Idempotent.

### 8c. (Weekly) Auto-discover niche channels

Not part of the daily flow — run on a slow cadence (weekly or when the
discovered list feels stale):

```bash
python3 discover_channels.py
```

Aggregates `untracked_channels[]` across every `data/archive/*/ytsearch.json`
and surfaces handles that surface across multiple candidate searches. Strong
signals (high overlap, high view counts, multi-day persistence) are Tier B/C
candidates — review the printed table and promote useful ones into
`config.json`'s `reference_channels.style_reference` or `.watchlist`.

Output: `data/discovered_channels.json` plus a ranked stderr table.

### 9. Summary — surface to the user

Read `data/archive/YYYY-MM-DD/run_meta.json` to get per-source counts and
errors. For any source whose `error` is non-null, render the source as
`{name}: 0 ({error})` so silent failures (rate-limits, network blips) are
visible instead of buried.

Report in chat using this exact structure:

```
Topic pipeline — daily run YYYY-MM-DD

Pulled: {N} new candidates (HN: {a}, Reddit: {b}, Lobste.rs: {c}, daily.dev: {d})
  (substitute "{name}: 0 (rate-limited)" or similar for any source with a non-null error)
Competitors: {ok}/{total} channels updated
Cold-search: {ok}/{total} candidates probed (cooldowns triggered: {k})
Judged: {M} (skipped {S} already-judged)

Top 3 unreviewed by composite score:
  1. {composite} — {title}  [{best_lens}]
  2. {composite} — {title}  [{best_lens}]
  3. {composite} — {title}  [{best_lens}]

Cooldown notices (Tier B/C coverage in last 30 days):
  • {title} — {reason}
  • ...

Dashboard: open file:///Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/topic-pipeline/data/dashboard.html
```

Keep the summary under 250 words. Three top candidates is the limit.

## Failure modes

- **fetch.py errors on all sources**: log the error, abort with a clear message. Do not produce a stale dashboard.
- **A single source fails**: that's expected. fetch.py handles it; just note in the summary which sources returned data.
- **competitors.py / cold_search.py fail on a subset of channels/candidates**: per-channel/per-candidate failures are logged and non-fatal. The merge step will still run; affected candidates will have `demand_sub_caps.cold_search = 0` etc.
- **WebFetch fails on an article URL**: skip that candidate, judge the next one. Note skipped count in summary.
- **Article paywalled / behind login**: judge from title + metadata; mark `notes` as "judged from title only".

## Operating envelope

Total wall-clock budget: under 25 minutes including all article fetches and
LLM judgments. If approaching 35 minutes, abort the judgment loop early —
write what you have and let the next day catch up.
