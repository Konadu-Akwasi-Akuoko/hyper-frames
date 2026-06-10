---
name: youtube-seo-research
description: Mine YouTube autocomplete + top-N video metadata for a topic into <video-dir>/seo/research.json, then surface a 5-line digest of searchable nouns, demand phrases, saturation warnings, and hook-shape data. Use when the user wants to research a topic before titling or scripting — phrases like "research SEO for this video", "what are competitors using", "what should I title this", "do keyword research", "research the topic before I write". Also invoked programmatically by other skills (script-writer, thumbnail-and-title-generator) when their consumer hooks detect a missing seo/research.json. Backed by the tools/youtube-seo/ Python CLI; this skill handles natural-language invocation, topic resolution, the digest, and follow-ups.
---

# youtube-seo-research

You are the LLM-driven wrapper around `tools/youtube-seo/`. Your job: resolve which video and topic the research is for, run (or re-use) the research artifact at `<video-dir>/seo/research.json`, and surface a single 5-line digest the user (or invoking skill) can act on.

The tool does the data fetching. You do the workflow, the natural-language interpretation, and the digest. Don't reimplement the tool's logic in shell — always shell out.

## Reference files (load on demand)

- `reference/signal-interpretation.md` — how to read each section of the digest, when to ignore signals, the saturated-keyword trap. Load before printing the digest.
- `reference/consumer-integration.md` — the consumer hook pattern + field map per consumer skill. Load when explaining how consumer skills use the JSON, or when a consumer skill is invoking you.

## Workflow

### Step 1 — Resolve the video folder

Resolve in this order:

1. If the user's message contains a path like `videos/<slug>-<date>/` (relative or absolute), use that.
2. If the current working directory matches `**/videos/<slug>-<date>/`, use that.
3. Otherwise, ask: "Which video folder should I research?" — list existing `videos/*` directories, **plus an option to create a new folder** (the user supplies a slug; date is today).

Convert the result to an absolute path and use it for every subsequent file read/write.

### Step 1.5 — Bootstrap the folder if it doesn't exist

This skill is often the **first** stage of a new video. If the resolved folder doesn't exist on disk, scaffold it now using the project's canonical bootstrap from `CLAUDE.md`. The block is **idempotent** — when invoked later in the pipeline against an existing folder, it skips `mkdir` and `npx hyperframes init` entirely:

```bash
# from the repo root — skip if folder already exists
if [ -d "videos/<slug>-<YYYY-MM-DD>" ]; then
  cd videos/<slug>-<YYYY-MM-DD>
  echo "Folder already exists. Skipping mkdir + hyperframes init."
else
  mkdir -p videos/<slug>-<YYYY-MM-DD>
  cd videos/<slug>-<YYYY-MM-DD>
  npx hyperframes init
fi
```

Use today's date when constructing a new folder name. Never author SEO artifacts (`seo/research.json`) at the repo root — they always live inside the resolved video folder.

### Step 2 — Resolve the topic

In this order:

1. If the user's message contains an explicit `topic:` or `--topic` phrase, use that verbatim.
2. If `<video-dir>/outline.md` exists and its H1 matches `# <topic> — 9-beat outline`, extract the topic.
3. Otherwise ask: "What topic phrase should I research? (e.g. 'text rendering', 'database B-tree', 'password hashing slow')". Keep it 2–5 words; YouTube autocomplete works best on short phrases.

Print: `Topic: <topic>` so the user can interrupt if it's wrong.

### Step 3 — Probe `<video-dir>/seo/research.json`

- **Missing** → proceed to Step 4 (run the tool).
- **Present** → read the file's `generated_at` field. Tell the user:
  > "Existing research found (generated <date>, topic: '<topic>'). Use it, or regenerate (~25s)?"
  - "use" / no answer → skip to Step 5 (load + digest).
  - "regenerate" / "force" / "refresh" → continue to Step 4 with `--force`.

### Step 4 — Run the tool

Shell out:

```bash
uv run --project <repo-root>/tools/youtube-seo seo-research \
  --topic "<topic>" \
  [--force]
```

Run from inside the video folder so the default output (`<cwd>/seo/research.json`) lands in the right place. Show the command's stdout/stderr to the user as it runs.

If the tool exits non-zero:
- **Soft-block (`yt-dlp soft-blocked`)** → tell the user, suggest waiting 30–60 minutes or running `yt-dlp --cookies-from-browser firefox` manually. Stop. Do not retry automatically.
- **Other errors** → surface the error, stop.

### Step 5 — Load and print the canonical 5-line digest

Read `<video-dir>/seo/research.json`. Load `reference/signal-interpretation.md` to inform what to highlight.

Print this exact format (substitute real values; omit the hook-shape line when `signals.hook_patterns` is null):

```
SEO context — <topic> (n=<N> videos, <L> autocomplete probes)
  Top searchable nouns: <noun1> (<count>), <noun2> (<count>), <noun3> (<count>)
  Demand phrases:       "<phrase1>", "<phrase2>"
  Saturation warning:   <N> videos >100K views use "<pattern>" — differentiate
  Top-performer ages:   median <X> months, freshest <Y> weeks
  Hook shape:           peak at ~<S>s; top performers hold <P5>%/<P15>%/<P30>% at 5/15/30s
```

When a signal is empty (no demand phrases surfaced, no saturation warnings, etc.), substitute `(none surfaced)` instead of dropping the line — empty signals are themselves informative.

For ages: derive from `top_videos[].upload_date` (yt-dlp format `YYYYMMDD`). Compute median and freshest at print time.

### Step 6 — Offer follow-ups

After the digest, ask:

> "Want me to: (a) expand to a related topic and re-research, (b) hand off to script-writer or thumbnail-and-title-generator, or (c) explain any signal in detail?"

Handle each:
- **(a) expand** → take the new topic, restart from Step 3 (probe → fetch → digest).
- **(b) handoff** → invoke the named skill via the `Skill` tool. The consumer skill's hook will detect the now-present `seo/research.json` and use it.
- **(c) explain** → load `reference/signal-interpretation.md`, walk through whichever signal the user asked about, with the actual numbers from this run.

If the user is silent or says "thanks / done", stop here.

## Hard rules

- Never block on missing data. If autocomplete failed (`autocomplete: null` in the JSON), the demand-phrases line says `(none surfaced — autocomplete failed)`. Continue.
- Never edit `seo/research.json` by hand. Re-run with `--force` instead.
- Never invent signals not in the JSON. If `top_nouns` is empty, say so — don't fabricate.
- The digest's job is to inform the user/consumer skill, not to make decisions for them. Don't recommend a specific title; surface what the data shows.

## Things this skill does NOT do

- Generate descriptions, tags, or chapters.
- A/B test titles (YouTube native does that).
- Pull related videos (out of scope; would need Invidious).
- Update consumer skills' decision logic — those skills own their own consumption.
