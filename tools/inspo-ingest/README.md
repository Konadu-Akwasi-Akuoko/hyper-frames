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
6. **Tile** them horizontally into `<out>/<slug>-strip.png` via `magick montage`
   (`-tile x1 -geometry WxH>+4+4 -background none`).
7. **Hero frame** — extract the highest-score frame at fuller res to
   `<out>/<slug>.png`.
8. **Cleanup** — delete the temp clip and intermediate frames unless
   `--keep-clip`.
9. **Stub** — print a markdown index entry with the real Source URL, window,
   chosen absolute frame timestamps, and threshold, plus empty `Tags:`,
   `Use when:`, and `Motion:` lines.

## `scan` vs `clip` — whole-video auto-detection

The tool has two subcommands:

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

## Design

All subprocess calls live in `cli.py`. The parsing, ranking, even-spacing
fallback, and every argv list (yt-dlp / ffmpeg / ffprobe / montage) are **pure
functions** in `frames.py` and `strip.py`, so the test suite asserts the exact
verified flag shape and the ranking logic without a network connection or any
binary installed.

## Tests

```bash
uv run --project tools/inspo-ingest pytest tools/inspo-ingest/tests -q
```
