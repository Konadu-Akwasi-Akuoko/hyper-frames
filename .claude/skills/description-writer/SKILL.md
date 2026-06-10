---
name: description-writer
description: Guided generator that turns an approved script + transcript into a production-ready YouTube description for a hyper-frames video. Reads outline.md, script.md, voiceover.txt, transcript.json, narration-map.json (optional), and seo/research.json (optional) from a `videos/<slug>-<date>/` folder; researches citations for concrete claims via WebSearch in parallel; composes hook, explainer, chapters with real timestamps, sources, and hashtags; writes `<video-dir>/description.md` and copies it to the clipboard via pbcopy. Use when the user says "write the description", "draft the YouTube description", "generate the video description", "fill in the description", "make the description for this video", or names a `videos/<slug>-<date>/` folder and asks for a description.
---

# description-writer

You are guiding the user through writing the YouTube description for a
single hyper-frames video. Output: a single `<video-dir>/description.md`
file copied to the clipboard, ready to paste into YouTube Studio.

The description has 5 fixed sections in fixed order — hook, explainer,
chapters, sources, hashtags. You do not redesign the shape per video.
You only choose: hook wording, explainer phrasing, chapter labels, which
claims earn citations, and which 3 nouns become hashtags.

## Workflow

### Step 1 — Resolve the target video folder

Resolve the target folder in this order:

1. If the user's message contains a path like `videos/<slug>-<date>/`
   (relative or absolute), use that.
2. If the current working directory matches `**/videos/<slug>-<date>/`,
   use that.
3. Otherwise, ask: "Which video folder should I work in?" — list
   existing `videos/*` directories.

Convert the result to an absolute path. Use that absolute path for
every subsequent file read and write — do not depend on CWD after this
step.

Halt with an actionable message if any of these are missing in the
resolved folder:

- `outline.md` — "Run `script-writer` first; the description needs the
  beat structure."
- `script.md` — "Run `script-writer` first; the description needs the
  narration body. Don't fabricate from `outline.md` alone."
- `voiceover.txt` — "Run `voiceover-elevenlabs-v2` first; the
  description hook lifts from the canonical narration."
- `transcript.json` — "Run `voiceover-elevenlabs-v2` first; chapter
  timestamps require word-level timing."

Never proceed without all four. The description is downstream of the
voiceover pipeline by design.

### Step 2 — Read the context files

Read these in parallel (small, bounded files):

- `<video-dir>/outline.md` — H1 is the working title (format:
  `# <topic> — 9-beat outline`). H2 headers are beat labels; the
  cycles list inside Beat 6 expands into multiple chapters.
- `<video-dir>/voiceover.txt` — canonical narration. The hook is
  lifted from here; this is the strongest curiosity-gap source.
- `<video-dir>/script.md` — narration body with `<!-- BEAT N: ... -->`
  comments marking beat boundaries. Use this to scan for citation
  candidates (specific years, named people, named institutions, named
  papers, specific statistics).

**Never `Read` `transcript.json` directly** — it's ~1500+ word entries
and floods context. Always load slices via the Python filter recipe
(see Step 4 and `reference/chapter-stamping.md`, also project
`CLAUDE.md` lines 67–96).

Optional: if `<video-dir>/narration-map.json` exists, you can read it
for the precomputed pause-window list (gaps > 400ms) — handy for
sanity-checking chapter boundaries. Not required.

### Step 3 — Probe `seo/research.json`

Same hook contract as `thumbnail-and-title-generator` and `script-writer` (see
`.claude/skills/youtube-seo-research/reference/consumer-integration.md`):

- **Present** → load it. Print: `Using SEO research from <date>.`
  Capture `signals.top_nouns[:3]` and `signals.demand_phrases[:2]` for
  use at Step 6.
- **Missing** → ask once per session:
  `"No SEO research found. Run it now via the youtube-seo-research skill (~25s)? [Y/n/skip]"`.
  On Y, invoke `youtube-seo-research` via the `Skill` tool and load
  the result. On n/skip, proceed without it; ask the user for 3 topic
  nouns at Step 6 (hashtags) and write the explainer without verbatim
  noun-rotation.

**Never block on missing data.** The description can ship without SEO
research — only the explainer's noun-rotation discipline and the
hashtag picks are affected.

### Step 4 — Derive chapter timestamps from the transcript

Build the chapter list from `outline.md`'s structural beats, in
narration order. The default mapping is one chapter per beat that
appears in the voiceover, with Beat 6's escalation cycles expanded
into one chapter per cycle.

Default chapter slots (skip any beat the script omits):

1. `0:00` — Intro / hook (Beat 1; YouTube requires this slot)
2. Beat 2 — Subversion
3. Beat 3 — Stakes
4. Beat 4 — Thesis
5. Beat 5 — Foundation
6. Beat 6, Cycle 1
7. Beat 6, Cycle 2
8. Beat 6, Cycle 3 (and 4, 5… if the cycles list is longer)
9. Beat 7 — Synthesis
10. Beat 8 — Reframe
11. Beat 9 — Closer

For each chapter after `0:00`, derive the start timestamp from
`transcript.json` by:

1. Reading the first ~3–6 words of that beat from `script.md` (skip
   `<!--` comments and strip markdown). For Beat 6 cycles, the
   opener is the first words of each cycle's prose block.
2. Running the Python filter from `reference/chapter-stamping.md`
   against `transcript.json` to find the global `start` time of the
   first matching word sequence.
3. Converting global seconds to `M:SS` (or `MM:SS` past 9:59) — never
   round to 30s buckets; use the real word's start time.

If a beat-opener phrase does not match any contiguous run in the
transcript, **stop and ask the user**: "Couldn't find anchor for
Beat N in the transcript. Did the voiceover diverge from `script.md`?"
Do not invent a timestamp. Do not guess.

Spelled-out year handling: voiceover scripts speak years like "nineteen
ninety-seven" or "two thousand and three", not "1997" or "2003". When
the beat opener contains a digit-year, normalize against the words
transcript by spelling it out before matching. See
`reference/chapter-stamping.md` for the full normalization table.

YouTube requires the first chapter to be at `0:00`. If Beat 1's first
spoken word starts at, say, 0.4s, still write the first chapter line as
`0:00`. Do not round up.

### Step 5 — Identify citation candidates and research them

Scan `script.md` for **claim signals** that earn external citations:

- Specific years tied to specific events ("In 1950, Alan Turing
  proposed…", "In 2024, researchers at ETH Zurich…").
- Named people tied to specific work ("Luis von Ahn coined CAPTCHA in
  2003", "Chad Houck at DEF CON").
- Named institutions tied to specific results ("ETH Zurich",
  "Microsoft", "Google").
- Named papers, models, or tools ("YOLO", "reCAPTCHA v3",
  "Cloudflare Turnstile").
- Specific statistics with magnitudes ("819 million hours", "31.8%",
  "six billion dollars").

Build a parallel `WebSearch` batch — one query per distinct claim —
and fire all of them in a **single message** with multiple tool calls.
See `reference/citation-recipes.md` for query phrasing patterns
(prefer "<author> <year> <topic> paper" over generic noun queries).

Prefer `WebSearch` for everything; only use `WebFetch` if a search
result page itself is the source you want to cite (rare) or you need a
specific paragraph from a known URL.

Soft cap: 6 sources. If the script has more than 6 citable claims,
pick the 6 strongest (specific year + named entity > generic claim).
The full list expands in iteration if the user asks for more.

### Step 6 — Compose the description

Write the 5 sections in order. Total target 1500–3500 chars; hard
cap 5000.

**1. Hook (~145 chars, single paragraph, no bullets).**
The first ~145 characters are what YouTube shows in the feed-card
expand. Lift the strongest curiosity-gap line from `voiceover.txt`'s
Beat 1 or Beat 2 — usually the subversion sentence. Rewrite for
written prose (drop spoken hedges, sharpen the verb). Must read as a
hook, not as a teaser ("In this video we explore…" is banned).

**2. Explainer (1–2 short paragraphs).**
Tell the viewer what they're about to watch, why it matters, and what
the video's specific angle is. If `seo/research.json` was loaded:

- Must contain `signals.top_nouns[:3]` verbatim, naturally placed —
  these are the searchable nouns that earn the YouTube search match.
- The top `signals.demand_phrases` entry, if it fits without
  contortion. Drop it if forcing the phrase reads awkwardly.

See `reference/seo-integration.md` for the noun-rotation discipline.

**3. Chapters.**
From Step 4. Format: `M:SS  Label` — two spaces between timestamp and
label. Labels are imperative-ish reworkings of the beat headings
("Intro" not "Familiar-action open", "How the Turing test flips"
not "Foundation"). Keep labels under ~50 chars each.

The chapter section is preceded by a single line "Chapters" header (no
markdown `#` — YouTube renders descriptions as plain text).

**4. Sources & further reading.**
From Step 5. Bulleted list, one source per line. Format:
`• <Title or paper name> — <attribution>: <URL>`. Use bullet
characters (`•` or `-`), not markdown asterisks. URLs go on the same
line as the title — YouTube auto-links them.

**5. Hashtags.**
Exactly 3, on a single line at the very end, space-separated:
`#tag1 #tag2 #tag3`. Derive from `signals.top_nouns[:3]` if SEO data
present; otherwise ask the user for 3 topic nouns. CamelCase
multi-word tags (`#ImageRecognition`, not `#image-recognition` or
`#image_recognition`).

See `reference/description-anatomy.md` for the full per-section
template with the captchas video as the worked example.

### Step 7 — Length check and write

Count the total character length of the composed description. Print:

```
Description ready — <N> chars, <M> chapters, <K> sources.
```

Trim strategy if over 3500 chars:

1. Shorten the explainer to a single paragraph (drop the second).
2. Trim sources to top 5, then top 4.
3. Tighten chapter labels (drop articles, use sentence fragments).

Never trim chapters below the beat list — every Beat 1–9 (with cycles
expanded) that appears in narration deserves a chapter. Never trim
the hook.

If still over 5000 chars after all trim passes, **stop and ask**: "Too
long even after trim. Which section do you want to cut harder —
explainer, sources, or chapter labels?"

Write to `<video-dir>/description.md`. If the file exists, ask once:
"description.md already exists. Overwrite? [Y/n]". Default Y if no
response.

Copy to clipboard with the project's clipboard recipe (per project
CLAUDE.md lines 155–162):

```bash
printf '%s' "$(cat <video-dir>/description.md)" | pbcopy
```

`pbcopy` is darwin-only; the project is darwin-pinned (per
`CLAUDE.md`), so no cross-platform shim is needed.

### Step 8 — Iterate

Print the confirmation line (chars, chapter count, source count) and
ask:

> "Anything to tweak — tone, chapter labels, source set, or hashtags?"

Interpret feedback per `reference/iteration-recipes.md`. Default:
**edit-in-place** on this run (the description is a single file, not a
folder of variants). Start a new run only when the user moves to a
different video folder.

The loop ends when the user says "ship it", "done", "looks good",
"that works", or equivalent. Never declare done on your own.

## Hard rules (always in effect)

- First ~145 chars must be hook-shaped — what shows in the YouTube
  feed-card expand. Bans on "In this video we explore", "Today we'll
  talk about", and any other narrator-from-stage opener.
- Chapters derived from `transcript.json` only — never invented, never
  rounded to nearest 30s.
- A chapter at `0:00` is mandatory — YouTube requires it for the
  chapter UI to render at all.
- Every concrete claim with a name/year/statistic needs a real URL —
  `WebSearch` first, `WebFetch` only when a specific page is the
  citation.
- Exactly 3 hashtags. From `signals.top_nouns[:3]` if SEO data present;
  otherwise ask the user.
- Never `Read` `transcript.json` directly — always filter via
  `python3 -c` (per project CLAUDE.md lines 67–96).
- Length: 1500–3500 chars target. 5000 hard cap.
- `pbcopy` is the clipboard mechanism. Use `printf '%s'` (not `echo`)
  to avoid trailing newlines.
- Never declare done on your own; the loop ends when the user says
  "ship it" or equivalent.
- Never fabricate from `outline.md` alone if `script.md` is missing —
  halt and tell the user to run `script-writer` first.

## Reference files (load on demand)

- `reference/description-anatomy.md` — the 5-section structure with
  the captchas video as the worked example. Load at Step 6.
- `reference/chapter-stamping.md` — the Python transcript-filter
  recipe and the spelled-out-year normalization table. Load at Step 4.
- `reference/citation-recipes.md` — what claims earn URLs, query
  phrasing patterns, and the parallel-WebSearch dispatch shape. Load
  at Step 5.
- `reference/seo-integration.md` — which `seo/research.json` fields
  drive which section. Load at Steps 3, 6, and 7.
- `reference/iteration-recipes.md` — feedback-to-action mapping. Load
  at Step 8 (every iteration).

## Things this skill does NOT do

- Write the script. That's `script-writer` (this runs after).
- Generate the voiceover. That's `voiceover-elevenlabs-v2` /
  `voiceover-elevenlabs-v3`.
- Pick a thumbnail title. That's `thumbnail-and-title-generator`.
- Upload to YouTube. The user pastes manually after `pbcopy`.
- A/B test the description. YouTube's native A/B is for titles +
  thumbnails only; descriptions are not A/B-testable.
- Internationalize. Single locale (en) by design.
