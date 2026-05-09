# YouTube SEO research — design

**Date:** 2026-05-09
**Status:** Approved for planning
**Owner:** akwasikonaduakuoko

## 1. Motivation

The thumbnail-creator skill's Step 4 (paired YouTube title) and the script-writer skill's Step 3 (working-title H1 + outline framing) currently rely entirely on the LLM's instinct from the seed topic. That's fine for taste and blind to demand: the LLM doesn't know which searchable nouns viewers actually type, doesn't see what phrasings already saturate the niche, and can't tell when it's about to ship a title that competes head-on with a 2M-view incumbent.

This design adds a free, anonymous, CLI-only research pass that mines yt-dlp + YouTube autocomplete for one topic, writes a structured JSON file at `<video-dir>/seo/research.json`, and feeds the data into multiple consumer skills via a shared, documented hook pattern.

The work has two layers:

1. **`tools/youtube-seo/`** — a deterministic Python CLI that fetches data, computes a small signals block, and writes the JSON. Mirrors the `tools/narration-map/` pattern.
2. **`youtube-seo-research`** — an LLM-driven skill that wraps the tool: triggers on natural-language requests, resolves the topic, shells out to the tool, prints a digest, and answers follow-ups. Other skills (`script-writer`, `thumbnail-creator`) invoke it via the `Skill` tool when they detect missing research.

## 2. Architecture

### 2.1 Tool — `tools/youtube-seo/`

A `uv` Python project, mirroring the layout of `tools/narration-map/`.

```
tools/youtube-seo/
├── pyproject.toml          # uv project; [tool.pyright] section; deps: requests, click
├── README.md               # usage, output schema, examples
└── src/youtube_seo/
    ├── __init__.py
    ├── cli.py              # click entrypoint: `seo-research` command
    ├── autocomplete.py     # suggestqueries fetcher + a-z expansion
    ├── search.py           # yt-dlp subprocess wrapper for ytsearchN
    ├── signals.py          # noun-frequency, saturation, demand, hook-patterns
    └── output.py           # JSON schema assembly + atomic write
```

**Dependencies:** `requests` (autocomplete HTTP), `click` (CLI). `yt-dlp` is shelled out via `subprocess` — already a homebrew binary on the user's machine, so no Python dependency. Tokenization for noun frequency uses a hand-rolled stopword list + regex split (no `nltk`).

### 2.2 Skill — `.claude/skills/youtube-seo-research/`

```
.claude/skills/youtube-seo-research/
├── SKILL.md                       # entry point, workflow, triggers
└── reference/
    ├── signal-interpretation.md   # how to read the digest, when to ignore it
    └── consumer-integration.md    # field map per consumer + hook pattern
```

The skill is the user-facing surface. It triggers on natural-language phrases ("research SEO for this video", "what are competitors using", "what should I title this", "do keyword research") and on programmatic invocation by other skills.

### 2.3 Consumer hook (the shared pattern)

Any skill that benefits from SEO context follows this hook at its decision point:

1. **Probe** for `<video-dir>/seo/research.json`.
2. **Missing** → invoke the `youtube-seo-research` skill via the `Skill` tool, with one-line user confirmation. If the user declines, proceed without it. **Never block on missing data.**
3. **Present** → load it and read the fields the consumer skill cares about. Optionally surface a consumer-specific compressed digest at the consumer's decision point.

The full canonical digest is printed once by `youtube-seo-research` when it runs. Consumer-specific digests are compressed reminders printed at consumer decision moments (e.g., thumbnail-creator's title-pairing step) that may happen hours or days after the original research.

## 3. CLI surface

```bash
uv run --project ../../tools/youtube-seo seo-research \
  [--topic "explicit phrase"] \
  [--n 30] \
  [--force] \
  [--region us] \
  [--hl en] \
  [--output <path>]
```

**Defaults:**

- **`--topic`** — when omitted, the tool reads `outline.md` from CWD and extracts the H1 topic (the `# <topic> — 9-beat outline` pattern script-writer produces). If `outline.md` is missing or unparseable, the tool exits with a clear message asking for `--topic`.
- **`--n`** — `30` videos via `ytsearchN:`.
- **`--force`** — when omitted, the tool exits if `seo/research.json` already exists at the output path. Output includes the existing file's `generated_at` timestamp so the user knows what they'd be regenerating.
- **`--region`** / **`--hl`** — `us` / `en`. Passed to autocomplete as `gl=us&hl=en`. yt-dlp respects the user's IP-derived region; documented in README.
- **`--output`** — defaults to `<cwd>/seo/research.json`. Tool creates the `seo/` directory if missing.

## 4. Data collection pipeline

Three passes, ~25s total wall time, fully anonymous (no cookies, no API key).

### 4.1 Autocomplete seed

One GET to:

```
https://suggestqueries.google.com/complete/search?client=firefox&ds=yt&hl=en&gl=us&q=<topic>
```

`client=firefox` returns clean JSON: `["query", ["suggestion1", ...], [], {...}]`. Returns up to ~10 suggestions.

### 4.2 Autocomplete a-z expansion

26 GETs, one per appended letter (`<topic> a`, `<topic> b`, …, `<topic> z`). Hard-coded 0.3s sleep between calls. Empty result arrays are kept in the output (negative signal — that prefix has no demand).

### 4.3 Top-N video pull

One subprocess call:

```bash
yt-dlp --dump-json "ytsearch30:<topic>"
```

Captures full per-video JSON for the top N. Each video's `description` is truncated to the first 500 chars (preserves SEO-relevant intro, saves space). All other fields kept verbatim, including `heatmap`.

### 4.4 Throttling and failure modes

- **Autocomplete:** hard-coded 0.3s between calls. On HTTP 429 from suggestqueries, abort the autocomplete pass, log a warning, write `autocomplete: null` in the output JSON. Top-videos pass continues.
- **yt-dlp soft-block** ("Sign in to confirm you're not a bot"): tool prints the failure and exits non-zero. v1 does not auto-retry with cookies. README documents `--cookies-from-browser firefox` as a manual recovery path; surfaced as a future enhancement, not v1.
- **Network failure mid-run:** no partial JSON written (atomic write — write to temp file, rename on success). User re-runs.
- **Empty autocomplete on a niche topic:** JSON written with empty arrays per letter. Downstream digests handle gracefully.

## 5. Computed signals

A `signals` block in the output JSON, computed from the raw data:

### 5.1 `top_nouns`

Top 10 nouns by frequency across all top-N video titles. Pipeline: lowercase tokenize → strip punctuation → drop stopwords (`how`, `why`, `the`, `is`, `vs`, `a`, `an`, `to`, `of`, `in`, `on`, `for`, `with`, `you`, `your`, `i`, `we`, `it`, `that`, `this`, `and`, `or`, `but`, `not`, `do`, `does`, `did`, `be`, `been`, `was`, `were`, `are`) → count → sort. Skip TF-IDF (overkill for a 30-doc corpus).

### 5.2 `saturation_warnings`

N-grams of length 3 to 6 words (sliding window over title tokens, after stopword-aware normalization) that appear in 3 or more videos with `view_count > 100_000` AND `upload_date` within the last 18 months. Each warning carries: the n-gram, match count, and one sample title. Capped at the 5 highest-match-count warnings (avoid drowning the digest). Tells the consumer: "this lane is saturated by recent successful videos — differentiate or commit deliberately."

### 5.3 `demand_phrases`

Autocomplete suggestions that surface in 3+ adjacent letter expansions (i.e., `<topic> a` AND `<topic> b` AND `<topic> c` all return a suggestion containing the phrase). Distinguishes real recurring search demand from one-off completions. Each entry: the phrase + `letter_hits` count.

### 5.4 `hook_patterns`

Computed from the per-video `heatmap` arrays (yt-dlp returns these for most videos). For videos that have heatmap data:

- `median_peak_position_seconds` — median time of the global heatmap peak across the corpus.
- `median_intensity_at_5s`, `median_intensity_at_15s`, `median_intensity_at_30s` — median heatmap value at those timestamps. Tells you how fast top performers lose viewers.
- `videos_with_heatmap` — denominator (some videos have no heatmap).
- `note` — one-line human-readable summary, e.g., `"Top performers tend to lose ~30% of viewers between 5s and 30s — peak hook lives in the first 12s."`

If fewer than 5 videos in the corpus return heatmap data, `hook_patterns` is written as `null` and the `note` field is `"Insufficient heatmap coverage (<5 videos) — skipped."`. Consumers handle the null case gracefully (omit the hook-shape line from any digest).

Not surfaced in the title-pairing digest — it's hook-shape data, not title-shape. Lives in the JSON for current and future consumers.

## 6. Output schema — `<video-dir>/seo/research.json`

```json
{
  "topic": "text rendering",
  "generated_at": "2026-05-09T14:32:00Z",
  "params": {"n": 30, "region": "us", "hl": "en"},
  "autocomplete": {
    "seed": ["text rendering explained", "text rendering pipeline", "..."],
    "expanded": {
      "a": ["text rendering algorithm", "..."],
      "b": [],
      "c": ["..."]
    }
  },
  "top_videos": [
    {
      "title": "...",
      "channel": "...",
      "channel_id": "...",
      "view_count": 1234567,
      "like_count": 45000,
      "comment_count": 2100,
      "upload_date": "20240312",
      "duration_seconds": 847,
      "tags": ["typography", "fonts"],
      "categories": ["Education"],
      "chapters": [{"start": 0, "end": 45, "title": "Intro"}],
      "description_excerpt": "first 500 chars",
      "heatmap": [{"start_time": 0, "end_time": 8.5, "value": 0.92}]
    }
  ],
  "signals": {
    "top_nouns": [
      {"noun": "rendering", "count": 18},
      {"noun": "font", "count": 12}
    ],
    "saturation_warnings": [
      {
        "pattern": "how text rendering works",
        "match_count": 5,
        "sample_title": "How text rendering actually works"
      }
    ],
    "demand_phrases": [
      {"phrase": "text rendering explained", "letter_hits": 4}
    ],
    "hook_patterns": {
      "median_peak_position_seconds": 12.4,
      "median_intensity_at_5s": 0.84,
      "median_intensity_at_15s": 0.67,
      "median_intensity_at_30s": 0.52,
      "videos_with_heatmap": 22,
      "note": "Top performers tend to lose ~30% of viewers between 5s and 30s — peak hook lives in the first 12s."
    }
  }
}
```

`autocomplete: null` when the autocomplete pass failed; consumers handle the null case. `heatmap` may be `null` per-video when yt-dlp didn't return one for that video.

## 7. Caching policy

- The tool checks for `seo/research.json` at the output path before doing any fetch. If present and `--force` is not set, it exits immediately:
  ```
  seo/research.json already exists (generated 2026-05-09T14:32:00Z).
  Use --force to regenerate.
  ```
- No TTL. Topic relevance doesn't drift fast enough to justify automatic staleness, and silent re-fetches would waste the user's network and time.
- `--force` overwrites in place via atomic rename.

## 8. The `youtube-seo-research` skill

### 8.1 Triggers

Listed in the skill's frontmatter `description`:

- "research SEO for this video"
- "what are competitors using"
- "what should I title this"
- "do keyword research"
- "research the topic before I write"
- Programmatic invocation from other skills via the `Skill` tool when their hook detects missing research.

### 8.2 Workflow

1. **Resolve video folder.** Same logic as thumbnail-creator: explicit path in message → CWD match `**/videos/<slug>-<date>/` → ask user with a list. Convert to absolute path.
2. **Resolve topic.** If `<video-dir>/outline.md` exists, parse the H1 (`# <topic> — 9-beat outline`) and use the topic. Otherwise ask the user.
3. **Probe `<video-dir>/seo/research.json`.** If present and not stale (i.e., user didn't pass `force`), summarize the existing file and offer to regenerate. If missing, proceed.
4. **Shell out:** `uv run --project <repo>/tools/youtube-seo seo-research` (append `--force` if step 3 determined a regeneration is wanted). Capture stdout/stderr; report any failures plainly.
5. **Print the canonical 5-line digest:**
   ```
   SEO context — text rendering (n=30 videos, 27 autocomplete probes)
     Top searchable nouns: rendering (18), font (12), unicode (9)
     Demand phrases:       "text rendering explained", "text rendering pipeline"
     Saturation warning:   5 videos >100K views use "how X works" — differentiate
     Top-performer ages:   median 14 months, freshest 3 weeks
     Hook shape:           peak at ~12s; top performers hold 84%/67%/52% at 5/15/30s
   ```
6. **Offer follow-ups:** expand search to a neighboring topic, re-run with `--force`, or hand off to a downstream skill (`script-writer`, `thumbnail-creator`) if the user is on that path.

### 8.3 Reference files

- **`reference/signal-interpretation.md`** — how to read each section of the digest. When to ignore signals (sparse niche, autocomplete returned little). The saturated-keyword trap. Why `top_nouns` is more reliable than `tags`.
- **`reference/consumer-integration.md`** — the consumer hook pattern + field map (see §9.3 below).

## 9. Consumer integration

### 9.1 `script-writer` (Step 2.5 — new step)

Insertion point: between Step 2 (folder creation + `hyperframes init`) and Step 3 (9-beat outline). After Step 2 the video folder exists, so `<video-dir>/seo/` has a place to land.

**Step 2.5 — SEO research checkpoint:**

```
Probe <video-dir>/seo/research.json.
Missing → "Want to run SEO research on '<topic>' before drafting the outline?
          Will surface searchable nouns, demand phrases, and what incumbents
          already cover, so the working title and framing can differentiate.
          [Y/n/skip]"
          Y → invoke youtube-seo-research skill via Skill tool; it prints the digest.
          n / skip → proceed without it (current behavior).
Present → load it; brief one-line "Using existing seo/research.json (generated <date>)" note.
```

**Step 3 changes** — when SEO data is loaded:

- **Working title H1.** Bias the topic phrasing toward a top searchable noun from `signals.top_nouns`. The H1 becomes the file's identity and what thumbnail-creator later reads, so the searchable anchor pays off twice.
- **Outline beat framing.** If `signals.saturation_warnings` flags a `"how X works"` pattern that matches the natural framing, lean on the iceberg arc's reframing strength to differentiate (e.g., open with the mundane action rather than the explainer setup).
- **Beat 1 hook budget.** If `signals.hook_patterns.median_peak_position_seconds` is, say, ~12s, that's the budget for open + subversion combined before viewers drop off. Tightens the discipline already in `nine-beat-arc.md`.
- **Coverage check.** Read `top_videos[].chapters` titles for the top 5–10 videos. If the script is about to retread a beat that incumbents already over-cover, flag it during outline review.

No script-writer-specific digest needed — `youtube-seo-research` already printed the canonical digest at Step 2.5. Step 3 reads the JSON silently and references it during outline review when the user asks "why this framing?".

### 9.2 `thumbnail-creator`

**Step 2 changes** — after reading `outline.md` and `script.md`, probe `<video-dir>/seo/research.json`:

- Present → load it. Continue.
- Missing → ask once per session: `"No SEO research found. Run it now via the youtube-seo-research skill (~25s)? [Y/n/skip]"`. On Y, invoke `youtube-seo-research` via the `Skill` tool and load the result. On n/skip, proceed without it (current behavior) and don't re-prompt during subsequent thumbnail iterations in the same session.

**Step 4 changes** — when SEO data is loaded, before producing the 3 paired titles, print a compressed 5-line digest:

```
SEO context — text rendering (n=30 videos, 27 autocomplete probes)
  Top searchable nouns: rendering (18), font (12), unicode (9)
  Demand phrases:       "text rendering explained", "text rendering pipeline"
  Saturation warning:   5 videos >100K views use "how X works" — differentiate
  Top-performer ages:   median 14 months, freshest 3 weeks
```

(Hook-patterns line omitted — title pairing is not where hook-shape applies.)

Then produce 3 paired titles, informed by — but not slavishly conforming to — the digest. Update `reference/youtube-title-pairing.md` with a new section "Using SEO research" that codifies:

- **Always** include at least one of the top 3 searchable nouns in the title (carry the search anchor).
- **Avoid** verbatim copying of any saturation-warned pattern; either differentiate the wording or commit to the lane only if the thumbnail claim is genuinely sharper.
- **Prefer** demand phrases when they fit naturally — they're the actual queries getting typed.
- **Ignore** when the digest is empty or noisy. The skill must never block on missing signal.

### 9.3 Field map (in `consumer-integration.md`)

| Consumer | Decision point | Fields used |
|---|---|---|
| `script-writer` | Step 2.5 (research) + Step 3 (outline) | `top_nouns` (working title), `saturation_warnings` (framing), `hook_patterns` (beat 1 budget), `top_videos[].chapters` (coverage check) |
| `thumbnail-creator` | Step 2 (probe) + Step 4 (paired title) | `top_nouns`, `demand_phrases`, `saturation_warnings`, `top_videos[].upload_date` (recency context) |

### 9.4 Adding a new consumer (process documented in `consumer-integration.md`)

1. Identify the decision point in the consumer skill's flow.
2. Add the probe + invoke-or-fall-back at that point.
3. Document which fields you read in this table.
4. Decide whether to print a consumer-specific digest or rely on the canonical one.

## 10. Updates to `CLAUDE.md`

Add a new subsection under "Authoring workflow", parallel to the existing narration-map block:

> **YouTube SEO research is a shared per-video artifact.** The `youtube-seo-research` skill (backed by `tools/youtube-seo/`) generates `<video-dir>/seo/research.json` from one topic phrase using yt-dlp + YouTube autocomplete (free, no API key, ~25s). Multiple skills consume it: `script-writer` reads it at the outline step, `thumbnail-creator` reads it at the paired-title step. Run it once per video — both skills will probe for it and offer to invoke the `youtube-seo-research` skill if it's missing.
>
> ```bash
> # From inside the video folder, after outline.md exists:
> uv run --project ../../tools/youtube-seo seo-research
> ```
>
> Writes `<video-dir>/seo/research.json`. See the skill's `reference/signal-interpretation.md` for how to read the digest, and `reference/consumer-integration.md` for which fields each consumer skill uses.

## 11. Out of scope (v1)

- Description-text generation
- Tag-list generation for upload
- Related-videos pull (would require Invidious — fragile, defer)
- Channel deep-dives ("show me what this competitor publishes over time")
- Deeper hook-shape analysis (correlating heatmap peaks with transcript content)
- A/B testing the titles (YouTube native does that)
- Updating the topic-pipeline tool to consume SEO research (could come later)
- Updating any voiceover or animation skills to consume SEO research (no current decision benefits from it)
- Cookie-based recovery from yt-dlp soft-blocks — documented as a manual `--cookies-from-browser firefox` recovery path in the README, not built into the tool

## 12. Implementation order (for the plan)

This section is a hint for `writing-plans`, not a binding sequence.

1. Build `tools/youtube-seo/` — autocomplete fetcher, search wrapper, signals module, CLI, output schema, atomic write, README.
2. Test the tool end-to-end on the existing `videos/why-text-is-hard-2026-05-07/` folder (its `outline.md` H1 is a real topic).
3. Create the `youtube-seo-research` skill via `/skill-creator:skill-creator` — `SKILL.md` + the two reference files. Wire it to invoke the tool.
4. Update `script-writer` SKILL.md to add Step 2.5.
5. Update `thumbnail-creator` SKILL.md to add the Step 2 probe and Step 4 digest, plus update `reference/youtube-title-pairing.md`.
6. Update root `CLAUDE.md` with the new subsection.
7. Smoke test: run `script-writer` on a fresh fake topic, confirm Step 2.5 fires; run `thumbnail-creator` on the same folder, confirm the digest renders.
