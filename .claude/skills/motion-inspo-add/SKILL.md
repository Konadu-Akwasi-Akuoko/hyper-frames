---
name: motion-inspo-add
description: Ingest a YouTube video into the repo-root inspiration libraries. DEFAULT for a whole-video URL is COMBINED ingest — motion-beat references into motionGraphicsInspo/ AND a pacing study into pacingInspo/, sharing one download. Narrower asks route to one mode - a clip window ("the beat at 1:12") captures a single motion beat; "motion only"/"scan for motion refs" does just the motion library; "ingest the pacing"/"study the cut cadence" does just the pacing library. Use whenever the user says "add a motion reference", "ingest this video", "add this to the library", "ingest this VFX clip", "build the motion library", "grab the motion from this video", "ingest this video's pacing", or hands over a YouTube URL for the inspiration libraries. Trigger even if the user doesn't name the skill — if the task is turning a YouTube video or beat into a reference our authoring skills can draw from, this is the skill. NOT for consuming references while authoring a video (that's video-director) and NOT for the ffmpeg mechanics (that's the tools/inspo-ingest CLI this skill drives).
allowed-tools: Read, Edit, Glob, Grep, Bash(uv run --project tools/inspo-ingest:*), Bash(git diff:*), Bash(git status:*), Bash(ls:*), Bash(mv:*)
---

# motion-inspo-add

Curation workflow for the project's motion reference library at
`motionGraphicsInspo/` (repo root). It mirrors `design-catalog-add`: a backing
tool does the mechanical work, and **you (Claude) do the judgment the tool can't** —
reading the captured motion and writing it down so the `video-director` can later
lift the *cadence* of a real, well-made beat.

The split is the whole point:

- **`tools/inspo-ingest`** (mechanical, deterministic): downloads the bounded clip,
  scene-detects the keyframes, tiles the **strip** PNG, extracts the **hero** PNG,
  prints an index-entry **stub**. It never writes prose.
- **You** (judgment): read the strip, author the `Tags:` / `Use when:` / `Motion:`
  lines, and append the finished entry to `motionGraphicsInspo/README.md`.

Why the strip and not a GIF: a GIF read by an agent collapses to its first frame —
motion is invisible. A tiled strip reads in full, so the staging is legible; the
`Motion:` note you write carries the timing a still can't.

## Hard rules

- **Author the `Motion:` and `Tags:` from the actual strip — never from imagination.**
  `Read` `motionGraphicsInspo/<slug>-strip.png` first. The note describes what the
  *source* does (its real cadence), faithfully; adapting-not-reproducing is the
  director's job downstream, not a reason to be vague here.
- **Drive the tool; don't reimplement it.** The ffmpeg/yt-dlp/montage mechanics live
  in `tools/inspo-ingest`. If something's wrong with the capture, re-run it with
  different flags — don't hand-build frames.
- **One row ↔ one entry ↔ one PNG pair.** The README is a two-tier index: every
  reference is a `## Quick index` table row **and** a `## Entries` detail block, sharing
  one slug. Each `<slug>.png` / `<slug>-strip.png` pair has exactly one row and one entry,
  and vice versa — never a row without its entry, never an entry without its PNGs.
- **Only the target library changes.** `motionGraphicsInspo/` for Modes A/B,
  `pacingInspo/` for Mode C, both for the default combined ingest — and nothing
  else either way. Confirm with `git diff --stat` before declaring done.

## Mode routing — combined ingest is the DEFAULT

When the user hands over a **whole-video YouTube URL with no narrower framing**,
ingest it into BOTH libraries. Route to a single mode only when the ask names one:

| Ask | Route |
|---|---|
| Bare URL / "ingest this video" / "add this video to the library" | **Combined ingest (below)** |
| URL + a timestamp or clip window ("the beat at 1:12") | Mode A only |
| "scan for motion refs", "motion only" | Mode B only |
| "ingest the pacing", "pacing only", "study the cut cadence" | Mode C only |

Combined ingest — one network call total, `pace` first because its single
yt-dlp invocation fetches the proxy, subtitles, and metadata that both
analyses need:

```bash
uv run --project tools/inspo-ingest inspo-ingest pace "<url>" --slug <slug>
uv run --project tools/inspo-ingest inspo-ingest scan "<url>" --slug <slug> \
  --from-proxy scratch/pacing/<slug>/proxy.mp4 --out scratch/inspo-scans/<slug>
```

Then curate both outputs: the scan manifest per **Mode B** (keep/drop beats →
`motionGraphicsInspo/`) and the pace artifacts per **Mode C** /
`pacingInspo/CLAUDE.md` (promote + author the `Pacing:` note → `pacingInspo/`).
The two curations are independent — a talking-head video may yield zero kept
motion beats and still be a worthwhile pacing entry, and vice versa. Never
re-download for the second analysis; `--from-proxy` exists precisely because
this IP has tripped YouTube's bot-wall before.

## Mode A — single beat (clip)

You already know the one window worth keeping; capture it directly into the library.

### Step 1 — Get the source beat

You need three things; read them from context or ask:

- The **YouTube URL**.
- The **time window** of the beat, `MM:SS-MM:SS` — the specific few seconds whose
  motion is worth keeping. A URL alone isn't enough; the tool downloads only this
  bounded section. If the user gives a URL with a `t=`/timestamp but no end, propose a
  tight window (a few seconds) around it and confirm.
- A **slug** — kebab-case, technique-first, so the library is findable by name alone
  (e.g. `staggered-stat-cards-overshoot`, `kinetic-headline-on-sky`). Draft one from
  the beat and confirm it.

Quote the three back in one line so the capture is auditable.

### Step 2 — Run the ingest tool

From the repo root:

```bash
uv run --project tools/inspo-ingest inspo-ingest "<youtube-url>" --slug <slug> --section MM:SS-MM:SS
```

Useful flags (defaults are usually right): `--scene-threshold` (lower catches softer
cuts/transitions, higher only hard cuts), `--max-frames` / `--min-frames` (strip width),
`--frame-width`, `--keep-clip` (debug). It writes `motionGraphicsInspo/<slug>.png` and
`motionGraphicsInspo/<slug>-strip.png` and prints a stub with the real `Source:`, the
chosen frame timestamps, and empty `Tags:` / `Use when:` / `Motion:` lines.

If preflight fails (missing `yt-dlp`/`ffmpeg`/`ffprobe`/`magick`), report exactly which
binary and stop — the user installs it (`brew install <formula>`) before retrying.

If the strip looks wrong (too few distinct frames, the cut you wanted got missed,
frames landed on a dead hold), re-run with a tuned `--scene-threshold` or a tighter
`--section`. Capture quality is worth a second pass.

### Step 3 — Read the strip and author the entry

`Read` `motionGraphicsInspo/<slug>-strip.png` (and the hero if helpful). The strip's
left-to-right progression *is* the motion; read it as frames of one beat. Then write:

- **Tags** — pick from the controlled vocabulary in `motionGraphicsInspo/README.md`
  (`motion=[…]` verbs, `archetype`, `energy`, `mood`). Prefer an existing tag; extend a
  dimension only when nothing fits. Tags are the index's search surface — they're how
  the director finds this entry from text alone, so make them honest and specific.
- **Use when** — one line naming the *beat meaning* this fits ("a stat lands as the
  payoff", "a name/title arrives over a hero shot"), not the literal subject of the
  source video.
- **Motion** — 2-4 sentences of **cadence**: what enters, in what order, the easing and
  overshoot, where it settles, any camera move. This is the part a still sequence can't
  encode and the reason the entry exists. Describe *how much*, not just "it animates" —
  the stagger step, the overshoot strength, the settle — because the director needs the
  numbers-feel to adapt it, not a label.

### Step 4 — Append to the index (both tiers)

The tool prints a **two-part stub**: a Quick-index row and a full Entries block (it
already has the correct `Source:`, slug, and filenames). Fill the blank judgment fields
you authored in Step 3 into **both** parts, then append each to its section in
`motionGraphicsInspo/README.md`:

- the filled **row** under `## Quick index` (into the markdown table — `slug` ·
  `archetype` · `motion` · `energy` · `mood` · `use-when`), and
- the filled **entry block** under `## Entries` (`### <slug>` with Hero/Strip, Tags,
  Use when, Motion, Source).

On the first add, replace the `_Empty …_` placeholder under *each* section. Keep the
row's cells consistent with the entry's `Tags:` line (same archetype, same motion verbs)
so the scan surface doesn't lie about the detail. Match the schema in that README exactly.

### Step 5 — Verify and hand off

- `git diff --stat` — confirm only `motionGraphicsInspo/<slug>.png`,
  `motionGraphicsInspo/<slug>-strip.png`, and `README.md` changed. Restore any stray.
- Show the user the finished entry and point them at the hero + strip to eyeball:
  *"Added `<slug>` — open `motionGraphicsInspo/<slug>-strip.png` to confirm the capture
  matches the motion you meant."*

### Batch mode ("build the motion library")

When the user hands over several URLs or a channel's worth of beats, loop Steps 1-5 per
clip. Keep slugs distinct and the library *diverse* — the director's failure mode is
sameness, so favor references that span different archetypes, energies, and moods rather
than five variants of one look. After a batch, one final `git diff --stat` to confirm
the file count matches the entries added (no strays — parallel work can drop files).

## Mode B — whole-video manifest review (scan)

When you don't know the windows — a whole video, a channel reel, "grab the good beats
from this" — let `scan` find the candidate beats, then curate them down with the user.
`scan` emits CANDIDATES ONLY; it never writes the library. The judgment (keep/drop, then
the prose lines) is still yours; the `Motion-metrics:` line is a mechanical copy.

### Step B1 — Get the whole-video URL

Just the URL — **no time window**. Scan segments the whole video and finds the
motion-graphics beats itself. Draft a kebab `--slug` *prefix* (it namespaces every
emitted beat, e.g. `data-viz-reel` → `data-viz-reel-beat-001-…`) and confirm it.

### Step B2 — Scan into a throwaway staging dir

Run scan into a **staging dir OUTSIDE the committed tree** (a temp dir, or repo
`scratch/`), **never** directly into `motionGraphicsInspo/` — scan dumps a PNG pair for
**every** candidate beat (the ones you'll keep *and* the ones you'll drop), and you do
not want the rejects in the library:

```bash
uv run --project tools/inspo-ingest inspo-ingest scan "<youtube-url>" --slug <prefix> --out <staging-dir>
```

Useful knobs: `--max-beats` (cap the candidate count), `--flow-fps` (detection
sampling rate / runtime), `--max-height` (proxy size — download/decode cost),
`--heatmap` (also emit a per-beat flow heatmap to eyeball the detection).

### Step B3 — Review the manifest, curate keep/drop with the user

`Read` `<staging-dir>/<prefix>-scan.json`. For **each** candidate beat: `Read` its
`-strip.png` (and the hero if useful), then decide **keep or drop *with the user***.
Present each candidate with its objective `descriptor` (energy / cadence / spatial) and
its `window` so the human curates from real evidence. **Dropping is first-class** — most
scans yield only a few keepers, and a lean library beats a padded one.

### Step B4 — Promote each KEPT beat into the library

For each beat the user keeps:

- author a **technique-first kebab slug** (same naming rule as Mode A Step 1 — findable
  by name alone), then
- `mv` **both** the beat's hero PNG and its `-strip.png` from the staging dir into
  `motionGraphicsInspo/` under the new slug name (so the library holds `<slug>.png` /
  `<slug>-strip.png`, not the scan's `-beat-NNN-…` names).

Leave the rejected beats' PNGs in staging (they get thrown away with it) — never `mv`
them into the library.

### Step B5 — Author prose, copy metrics mechanically

From each kept beat's `-strip.png`, author the `Tags:` / `Use when:` / `Motion:` lines
with the **identical judgment as Mode A Step 3** (read the strip; cadence from the frame
progression). Then fill the `Motion-metrics:` line **mechanically** by copying the kept
beat's manifest fields per the frozen contract — this is a copy, not judgment:

- `energy` ← `descriptor.energy`
- `cadence` ← `descriptor.cadence`
- `spatial` ← `descriptor.spatial`
- `gate` ← `gate_kind`
- `src=scan` (literal — marks the entry as scan-sourced)

…and the five parenthetical raw floats, each copied from the manifest's `metrics` object
under its **exact** field name (the `Motion-metrics:` display label on the left, the real
`metrics.<field>` key on the right — they differ for three of the five, so copy by key):

- `motion_energy` ← `metrics.motion_energy`
- `eased_energy_share` ← `metrics.eased_energy_share`
- `sparsity` ← `metrics.sparsity`
- `spatial_concentration` ← `metrics.spatial_concentration`
- `mov_texture` ← `metrics.mov_texture`

### Step B6 — Append both tiers

Append **both** tiers for each kept beat — the `## Quick index` row **and** the
`## Entries` block (the entry block now carrying the `Motion-metrics:` line) — to
`motionGraphicsInspo/README.md`, same two-tier sync rule as Mode A Step 4 (one row ↔ one
entry ↔ one PNG pair, cells consistent with the `Tags:` line). The Quick-index table
stays lean — there is **no** Motion-metrics column; the metrics live in the detail tier
only.

### Step B7 — Verify

`git diff --stat` — confirm **only** `motionGraphicsInspo/` changed: the kept PNG pairs
plus `README.md`. The staging dir and its manifest are throwaway and are **never
committed**; no `-beat-NNN-…` names, no dropped-beat PNGs, no `-scan.json` should appear.
Restore any stray.

## Mode C — whole-video pacing study (pace)

When the ask is about a video's *temporal* craft — "how does this creator pace
scene changes against narration", "ingest this video's pacing", "study the cut
cadence" — the target library is **`pacingInspo/`** (repo root), not
`motionGraphicsInspo/`, and the tool subcommand is `pace`:

```bash
uv run --project tools/inspo-ingest inspo-ingest pace "<youtube-url>" --slug <slug>
```

It detects every scene change (hard cuts + eased transitions), fetches the
yt-dlp word-level transcript in the same single network call, aligns narration
to scenes (wps, pauses, sentence alignment), and emits candidates into
`scratch/pacing/<slug>/`. The full curation procedure — contact-sheet QA,
threshold tuning, which three artifact kinds get promoted, the two-tier index
contract, and the authored `Pacing:` note — lives in **`pacingInspo/CLAUDE.md`**;
follow it rather than the Mode A/B steps. Do not mix the libraries: one beat ↔
one PNG pair belongs in motionGraphicsInspo; one whole-video timeline belongs
in pacingInspo.

## Anti-patterns

- ❌ Writing the `Motion:` note from the hero still or the video's title instead of
  reading the strip. The cadence is in the frame progression.
- ❌ Inventing tags when the README vocabulary already has the word. The index stays
  scannable only if the vocabulary stays small.
- ❌ Describing the source's *subject* in `Use when:` ("a JavaScript video") instead of
  its *beat meaning* ("a power claim lands"). The director matches on meaning.
- ❌ Hand-editing frames or `sfx.html`-style mechanics. Re-run the tool instead.
- ❌ Adding the Entries block but forgetting the Quick-index row (or vice versa), or
  leaving a `<slug>.png` with no entry, or an entry with no PNGs. Row, entry, and PNG
  pair travel together — a row with no entry makes the scan surface point at nothing.
- ❌ (Mode B) Committing the scan staging dir / `-scan.json`, or leaving dropped-beat
  PNGs in `motionGraphicsInspo/`. Scan into throwaway staging; only the kept, renamed
  PNG pairs land in the library.
