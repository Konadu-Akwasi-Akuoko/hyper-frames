# inspo-ingest

A mechanical CLI that turns a bounded YouTube clip into a motion-inspo capture:
a horizontal film-strip PNG of the most significant cut frames, a fuller-res
hero frame, and a markdown index-entry **stub** printed to stdout. It never
authors prose — the `Tags:`, `Use when:`, and `Motion:` lines come out empty for
a human to fill in.

Everything is deterministic: no randomness anywhere. Given the same URL, window,
and flags, it picks the same frames every run.

## Requirements

These binaries must be on `PATH` (the tool preflights and exits non-zero with a
`brew install` hint if any are missing):

- `yt-dlp` — `brew install yt-dlp`
- `ffmpeg` and `ffprobe` — `brew install ffmpeg`
- `magick` (ImageMagick v7) — `brew install imagemagick`

## Usage

```
inspo-ingest <youtube-url> --slug <kebab-name> --section MM:SS-MM:SS
  [--scene-threshold 0.4] [--max-frames 6] [--min-frames 3] [--frame-width 480]
  [--out <dir>] [--keep-clip]
```

Run it via uv from the repo root:

```bash
uv run --project tools/inspo-ingest inspo-ingest \
  "https://www.youtube.com/watch?v=VIDEO_ID" \
  --slug liquid-text-morph \
  --section 1:12-1:18
```

### Options

| Flag | Default | Meaning |
|---|---|---|
| `--slug` | (required) | Kebab name for outputs: `<slug>-strip.png`, `<slug>.png` |
| `--section` | (required) | Window `MM:SS-MM:SS` or `HH:MM:SS-HH:MM:SS` |
| `--scene-threshold` | `0.4` | Scene score (0–1) recorded in the stub |
| `--max-frames` | `6` | Top-N frames in the strip (ranked by scene score) |
| `--min-frames` | `3` | Floor; if fewer candidates, fall back to even spacing |
| `--frame-width` | `480` | Per-tile width in px (height auto, 16:9) |
| `--out` | `motionGraphicsInspo/` at repo root | Output directory |
| `--keep-clip` | off | Keep the downloaded clip + intermediate frames |

## Pipeline

1. **Preflight** — confirm `yt-dlp`, `ffmpeg`, `ffprobe`, and `magick` are on
   `PATH`; exit non-zero naming the missing binary otherwise.
2. **Download** the bounded section with yt-dlp's verified
   `--download-sections "*START-END"` syntax into a temp dir as one muxed mp4
   (`-f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]" --merge-output-format mp4`).
3. **Scene-detect** with ffmpeg's `select=gte(scene,0),metadata=print` so every
   frame's `lavfi.scene_score` is captured; parse `(pts_time, score)` pairs.
4. **Rank** by score descending, take the top `--max-frames`, then re-sort by
   time. If fewer than `--min-frames` candidates exist, fall back to evenly
   spaced timestamps across the clip.
5. **Extract** the chosen frames with output-side `-ss` (frame-accurate) and
   `scale=W:-1`.
6. **Tile** them horizontally into `<out>/<slug>-strip.png` via `magick +append`
   (`-resize Wx -bordercolor #1a1a1a -border 3 -background none`; never
   `montage`, which needs a configured font Homebrew builds can lack).
7. **Hero frame** — extract the highest-score frame at fuller res to
   `<out>/<slug>.png`.
8. **Cleanup** — delete the temp clip and intermediate frames unless
   `--keep-clip`.
9. **Stub** — print a markdown index entry with the real Source URL, window,
   chosen absolute frame timestamps, and threshold, plus empty `Tags:`,
   `Use when:`, and `Motion:` lines.

## `scan` vs `clip` — whole-video auto-detection

The tool has three subcommands (`clip`, `scan`, and `pace` — the latter is
documented in its own section below):

- **`clip`** (the original behavior, documented above) — you hand it *one
  bounded window* via `--section MM:SS-MM:SS` and it captures whatever has the
  biggest pixel-change in that window. It is mechanically faithful but
  **content-blind**: point it at a window where a talking head cuts to a static
  render and it will dutifully capture the cut, motion graphics or not.
- **`scan`** — you hand it a **whole-video URL** and it finds the genuine
  motion-graphics beats for you. It streams the video through **DIS dense
  optical flow**, auto-segments each real animation beat, and emits a hero
  still + keyframe strip (+ an optional flow heatmap) and **objective motion
  descriptors** per beat. Flow does the detection and the objective tagging;
  the *semantic* choice of "which animation fits which scene" stays human.

The back-compat shim means the original positional-URL-first form still works:
if the first argument isn't a known subcommand, `clip` is injected, so every
existing `motion-inspo-add` call keeps running unchanged.

### Whole-video workflow

```
inspo-ingest scan <youtube-url> --slug <prefix>
  [--max-height 1080] [--max-beats 12] [--min-beat 1.2] [--merge-gap 0.6]
  [--pad 0.4] [--flow-fps 10] [--heatmap]
```

```bash
uv run --project tools/inspo-ingest inspo-ingest scan \
  "https://www.youtube.com/watch?v=VIDEO_ID" \
  --slug data-viz-reel
```

With `scan`, `--slug` becomes a **filename prefix / namespace** for the N
emitted beats rather than a single output name.

How it works:

1. **Proxy download** — one file, capped at `--max-height` (default 1080p; a
   1600px hero downsamples cleanly from 1920px-wide, and 4K of a full video is
   many GB for nothing the model sees). Scan **prefers the H.264/AVC rendition**
   over an equal-resolution AV1/VP9 one, because it software-decodes the entire
   proxy and AV1 has no hardware decode path on most machines (≈5-10× slower).
2. **Flow decode** — an **ffmpeg pipe** does the decode + fps-decimation to
   `--flow-fps` + downscale to 256px all in C (on libdav1d's fast path for AV1),
   streaming raw BGR frames that the scan reads one fixed-size frame at a time —
   so Python never touches a full-resolution decode, only tiny 256px frames at
   the flow rate. DIS optical flow runs **single-threaded** (no faster
   multi-threaded on frames this small, holds the work to one core, and is
   bit-deterministic). Each sampled pair becomes one `FlowFingerprint` row keyed
   by **absolute proxy seconds**.
3. **Segment** — group contiguous active runs, split on hard cuts, gate each
   candidate with the validated two-axis motion-graphics gate, merge sub-gap
   neighbors, drop sub-`--min-beat` blips, pad boundaries, score, and cap at the
   top `--max-beats`, re-sorted by time.
4. **Per-beat capture** — run the existing scene-detect / rank / extract / tile
   pipeline against the one proxy, once per beat window. Frame extraction uses a
   **fast input-side seek** (jump near the keyframe, then decode the last second
   for exact-frame accuracy) so pulling stills at late absolute timestamps stays
   near-instant instead of re-decoding the whole proxy from zero each time.

### `scan` options

| Flag | Default | Meaning |
|---|---|---|
| `--max-height` | `1080` | Cap (px) on the downloaded proxy's height |
| `--max-beats` | `12` | Cap on emitted beats (top-scoring, re-sorted by time) |
| `--min-beat` | `1.2` | Minimum beat duration (s); shorter blips are dropped |
| `--merge-gap` | `0.6` | Merge neighboring beats separated by less than this (s) |
| `--pad` | `0.4` | Padding (s) added to each beat's boundaries (clamped) |
| `--flow-fps` | `10` | Optical-flow sampling rate (frames/s) |
| `--heatmap` | off | Also emit a per-beat flow heatmap PNG |
| `--from-proxy` | none | Analyze this existing proxy file instead of downloading (skips yt-dlp; `--max-height` ignored; the URL is still recorded as `source_url`) |

`--from-proxy` exists for the **combined ingest** flow: `pace` and `scan` use
identical proxy parameters (≤1080p, AVC-preferred), so after a `pace` run you
can point `scan` at its cached file and analyze the same video for motion beats
with zero additional network traffic:

```bash
uv run --project tools/inspo-ingest inspo-ingest pace "<url>" --slug my-video
uv run --project tools/inspo-ingest inspo-ingest scan "<url>" --slug my-video \
  --from-proxy scratch/pacing/my-video/proxy.mp4 --out scratch/inspo-scans/my-video
```

One yt-dlp invocation total for both analyses (bot-wall discipline). The
external proxy is never deleted by scan's cleanup.

### JSON manifest output

`scan` writes per-beat files plus a single JSON manifest:

```
<slug>-beat-001-0m12s.png        # hero still
<slug>-beat-001-0m12s-strip.png  # keyframe strip
<slug>-beat-001-0m12s-flow.png   # flow heatmap (only with --heatmap)
<slug>-scan.json                 # the manifest
```

The manifest records `source_url`, the proxy/flow parameters, `opencv_version`,
the gate thresholds, and a time-ordered `beats[]` array. Each beat entry carries
its `window` (`start_s`/`end_s`), the `files` paths (`hero`, `strip`, and
`flow` when `--heatmap`), the objective `metrics`, the `descriptor`
(`energy`, `cadence`, `spatial`), `gate_kind`, `score`, and `frame_times_abs_s`.
There is **no** pre-baked markdown `stub` string in the scan manifest —
`motion-inspo-add` (Mode B) turns these structured fields into the README entry
itself. It is deterministic: time-ordered, fixed float formatting, sorted keys,
so a re-run is byte-identical (modulo `opencv_version`).

**`scan` emits CANDIDATES only — it never writes the library.** It does not
append to `motionGraphicsInspo/README.md`. The human (via `motion-inspo-add`)
reviews the manifest, keeps or drops beats, and authors the prose `Tags:`,
`Use when:`, and `Motion:` lines.

### Expected runtime

The ffmpeg-pipe decode keeps `scan` well under realtime: the flow pass over a
10-minute proxy at the default `--flow-fps 10` runs in roughly 20-30s on one CPU
core (≈250 frame-pairs/s), so a typical `scan` is dominated by the proxy
**download**, not the flow. It still costs more than a single-window `clip` —
budget a minute or two end-to-end for a ~10-minute video. `--flow-fps` (fewer
pairs) and `--max-height` (smaller download/decode) are the main runtime knobs;
the work is single-core by design, so it won't peg the whole machine.

## pace — scene-change + narration pacing

`pace` takes a **whole-video URL** and measures how the video is *edited*: it
detects EVERY scene change (hard cuts AND soft transitions like crossfades or
wipes), fetches the video's word-level auto captions, aligns narration to the
resulting scenes (words-per-second, silences, whether cuts land in speech
pauses or on sentence boundaries), and emits deterministic **candidate**
artifacts — a JSON manifest, a mechanical markdown pacing report, and per-scene
thumbnails tiled into contact sheets.

**`pace` emits CANDIDATES only — it never writes any library or prose.** Every
number it produces is mechanical; the judgment (`Pacing:` notes, curation into
a library) happens afterward, outside the tool.

```
inspo-ingest pace <youtube-url> --slug <prefix>
  [--out <dir>] [--max-height 1080] [--sample-fps 10]
  [--hard-floor 0.05] [--hard-ratio 6.0] [--hard-window 3.0] [--min-gap 0.3]
  [--soft-wide-min 0.12] [--soft-adj-max 0.10] [--soft-plateau 0.5]
  [--dedupe 0.2] [--langs en-orig,en] [--no-frames] [--thumb-width 160]
```

```bash
uv run --project tools/inspo-ingest inspo-ingest pace \
  "https://www.youtube.com/watch?v=VIDEO_ID" \
  --slug fast-explainer
```

### `pace` options

| Flag | Default | Meaning |
|---|---|---|
| `--slug` | (required) | Filename prefix for the emitted artifacts |
| `--out` | `scratch/pacing/<slug>/` at repo root | Output dir; doubles as the download cache |
| `--max-height` | `1080` | Cap (px) on the downloaded proxy's height |
| `--sample-fps` | `10` | Sampling rate for the soft-transition feature pass |
| `--hard-floor` | `0.05` | Absolute scene-score floor a hard cut must clear |
| `--hard-ratio` | `6.0` | Adaptive multiplier on the rolling-median scene score |
| `--hard-window` | `3.0` | Full width (s) of the centered rolling-median window |
| `--min-gap` | `0.3` | Debounce (s); qualifying cut frames closer than this cluster |
| `--soft-wide-min` | `0.12` | Min wide-baseline HSV delta for a soft-transition plateau |
| `--soft-adj-max` | `0.10` | Max adjacent HSV delta for a soft-transition plateau |
| `--soft-plateau` | `0.5` | Minimum plateau span (s) for a soft transition |
| `--dedupe` | `0.2` | Boundaries within this (s) collapse to one (hard wins) |
| `--langs` | `en-orig,en` | Subtitle language preference order (comma-separated) |
| `--no-frames` | off | Skip per-scene thumbnails and contact sheets |
| `--thumb-width` | `160` | Per-scene thumbnail width (px) |

### How it works

1. **ONE yt-dlp call total** — the proxy download also fetches subtitles
   (`--write-auto-subs --write-subs --sub-langs ... --sub-format
   json3/srv3/vtt --sleep-subtitles 2`) and `--write-info-json` in the same
   invocation. No separate subtitle fetch, ever (bot-wall discipline). The
   proxy, subtitle files, and info JSON live in the out dir as a **cache**: on
   re-run, when the proxy + a json3 track + the info JSON already exist, the
   network fetch is skipped entirely and logged. Determinism is scoped to
   "same cached inputs → byte-identical manifest".
2. **Hard cuts** — the full-fps ffmpeg scene-score pass (thresholdless, scores
   every frame) is run over the whole proxy, then an **adaptive threshold**
   picks the cuts: a frame qualifies iff its score is at least
   `max(--hard-floor, --hard-ratio × rolling-median)` of its ±`--hard-window`/2
   neighborhood (self excluded), debounced to the cluster max within
   `--min-gap`. A fixed threshold cannot serve motion-graphics content — it
   false-positives during animation at low T and misses subtle talking-head
   cuts at high T; the rolling ratio adapts to the local baseline.
3. **Soft transitions** — crossfades/wipes are structurally invisible to
   adjacent-frame metrics, so a low-fps 256px HSV pipe pass (same ffmpeg-pipe
   pattern as `scan`, no optical flow) computes per-sample deltas vs the
   previous sample and vs the sample ~1s earlier. A sustained plateau of high
   wide-baseline delta with moderate adjacent delta (≥ `--soft-plateau` s)
   marks a soft boundary at its wide-delta peak; candidates within 1s of a
   hard cut are suppressed. These defaults are first-guess heuristics —
   calibrate on live runs.
4. **Scenes** — boundaries are merged (within `--dedupe` s they collapse, hard
   beats soft, then higher score, then earlier) and the proxy is tiled into
   1-based scene windows spanning `[0, duration]` exactly.
5. **Transcript alignment** — the preferred json3 track (`--langs` order,
   `en-orig` first because it carries word-level `tOffsetMs` timing) is parsed
   into word onsets, bracketed non-speech tokens (`[Music]`…) are dropped, and
   each scene gets word count, words/s, coverage, leading/trailing silence,
   whether its opening cut sits inside a speech pause, and whether it follows a
   sentence end. Missing or cue-level-only subtitles degrade gracefully
   (`"subtitles": null` / `"word_level": false`); they never fail the run.
6. **Thumbs + contact sheets** (default on; `--no-frames` to skip) — one thumb
   per scene sampled *inside* the scene at `start + min(0.3, duration/2)`
   (never AT the boundary, where a fast-seek grab can land on the wrong side
   of the cut) into `<slug>-thumbs/scene-NNN.png`, then tiled row-major, 10
   per row, max 10 rows per sheet, into `<slug>-scenes-sheet-NNN.png`. Sheets
   are built with `magick +append`/`-append` (never `montage`, never
   `-annotate` — both need a configured font that Homebrew builds can lack),
   so there are no on-image labels; tile order matches the report's table.

### `pace` outputs

```
proxy.<ext>                    # cached download (plus proxy.<lang>.json3, proxy.info.json)
<slug>-pace.json               # the inspo-pace/1 manifest
<slug>-pacing.md               # mechanical report: aggregates + per-scene table
<slug>-thumbs/scene-NNN.png    # one per scene (unless --no-frames)
<slug>-scenes-sheet-NNN.png    # contact sheets, 10x10 tiles, row-major
```

The `inspo-pace/1` manifest is a **frozen field-name contract** (downstream
copies fields mechanically by exact name). Sketch:

```jsonc
{
  "schema": "inspo-pace/1",
  "source_url": "...", "slug": "...",
  "video": {"title": "...", "channel": "...", "upload_date": "...", "duration_s": 612.0},
  "proxy": {"max_height": 1080, "duration_s": 611.96},
  "scene_detect": {"hard": {...}, "soft": {...}, "dedupe_s": 0.2},
  "subtitles": {"lang": "en-orig", "track_kind": "auto", "source_format": "json3",
                "word_level": true, "punctuated": true, "word_count": 1742},  // or null
  "scenes": [{
    "index": 1, "window": {"start_s": 0.0, "end_s": 4.2}, "duration_s": 4.2,
    "boundary": {"kind": "start", "score": null},   // then "cut" | "soft"
    "narration": {"word_count": 12, "words_per_s": 2.86, "coverage": 0.95,
                  "first_word_offset_s": 0.21, "leading_silence_s": 0.21,
                  "trailing_silence_s": 0.4, "cut_in_pause": true,
                  "pause_before_cut_s": 0.7, "sentence_aligned": true,
                  "text": "..."},                   // or null without subtitles
    "files": {"thumb": "fast-explainer-thumbs/scene-001.png"}  // or null
  }],
  "aggregates": {"scene_count": 87, "cuts_per_minute": 8.3, "soft_transition_count": 4,
                 "scene_duration_s": {"median": 5.1, "p25": 2.9, "p75": 9.4,
                                      "min": 0.8, "max": 31.2},
                 "longest_hold_s": 31.2, "words_per_s_mean": 2.7,
                 "pct_cuts_in_pause": 0.62, "pct_sentence_aligned": 0.55}
}
```

It is deterministic: every float quantized to 4 decimals, sorted keys, trailing
newline — a re-run over the same cached inputs is byte-identical. The markdown
report carries the same numbers (header facts, aggregates block, per-scene
table with a 12-word text excerpt) and **no judgment prose**.

### Known limitations

- **No diarization** — per-scene words/s conflates the narrator with speech in
  embedded clips.
- **ASR timing** — auto-caption word onsets are ±0.1–0.2s on clean speech and
  unreliable over music; treat `cut_in_pause` / `sentence_aligned` as
  approximate. Manual (cue-level) tracks have no word timing at all
  (`word_level: false`), which degrades the narration stats further.
- **Detection defaults are calibrated, not universal** — `--hard-floor 0.05`
  and `--soft-wide-min 0.12` were originally tuned on two videos (2026-06-09:
  a quiet diagram-explainer and a fast-cut essay) and **formally re-validated
  on 17 videos across 4 registers (2026-06-10)** — chaptered explainer, brisk
  sectioned talking-head, fast essay/listicle churn, and vertical Short. The
  per-frame score distributions confirm both floors generalize: `--hard-floor
  0.05` sits 5–10× above the per-frame noise floor in every register (median
  nonzero scene score 0.002–0.009), and `--soft-wide-min 0.12` sits 10–40×
  above the static-canvas baseline in the slow-explainer register where soft
  transitions actually matter (median wide-delta 0.003–0.012). No register
  needed a different floor; the adaptive ratio + `--min-gap` debounce + dedupe
  do the real cut selection, so the floors are robust noise gates rather than
  the binding selector. Tuning knobs still apply per video: lower
  `--soft-wide-min` catches more eased transitions but starts firing on
  in-scene text build-ons; raise `--hard-floor` toward 0.12 on noisy
  hard-cut-heavy footage if precision suffers. Slow pans or very long
  dissolves can still fool the soft detector in either direction — QA the
  contact sheet (adjacent near-identical tiles = over-detection; a
  suspiciously long scene = under-detection).

## Design

All subprocess calls (and all `cv2` work) live in `cli.py`. The parsing,
ranking, even-spacing fallback, scene-boundary math, transcript alignment, and
every argv list (yt-dlp / ffmpeg / ffprobe / magick) are **pure functions** in
`frames.py`, `strip.py`, `motion.py`, `scenes.py`, and `transcript.py`, so the
test suite asserts the exact verified flag shape and the decision logic without
a network connection or any binary installed.

## Tests

```bash
uv run --project tools/inspo-ingest pytest tools/inspo-ingest/tests -q
```
