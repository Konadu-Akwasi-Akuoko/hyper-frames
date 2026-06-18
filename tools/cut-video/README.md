# cut-video

Applies a `cuts.json` (a list of **removed** `[start, end]` spans in seconds) to
a video **or** audio source, emitting one frame-accurate cut master. The keep
math complements the removed spans, and cut-video cuts the VIDEO so picture and
audio stay **frame-locked** — both streams are trimmed on the *same* absolute
source-time keep-windows, then concatenated and re-encoded.

It **re-encodes** rather than stream-copying: `-c copy` is keyframe-bound and
drifts on sub-frame cut boundaries, so cut-video always re-encodes at native
resolution (no scale filter). It is deterministic — identical input yields a
byte-identical filtergraph and, under pinned encoder flags, a reproducible
encode, as required by the render-safe pipeline.

## How it works

1. Probe the source (ffprobe): stream set, duration, and frame rate. The mode is
   inferred from the streams — video present -> `video`, audio-only -> `audio` —
   and validated (video mode needs exactly 1 video + 1 audio; audio mode needs
   exactly 1 audio).
2. Sort + coalesce the removed spans (merge touching/overlapping, no zero-length
   keeps), then walk a cursor from 0 to EOF emitting the kept windows. Keeps at
   or below the epsilon (default 1 frame) are dropped; whole-duration-removed
   raises a loud error.
3. Build a deterministic `filter_complex_script`: per keep `i`,
   `[0:v]trim=…,setpts[vi]` + `[0:a]atrim=…,asetpts[ai]`, then a single
   `concat`. Boundary floats are rounded to 6 decimals so the graph text is
   byte-identical across runs.
4. Re-encode once via ffmpeg with pinned flags (`libx264 -crf 12 -preset medium
   -pix_fmt yuv420p`, audio `pcm_s16le`, `+faststart`). Audio mode uses the
   `atrim`/`aconcat` half only with `libmp3lame -q:a 2`.

## Usage

```bash
# Cut a video master (mode inferred: video present -> video)
uv run --project tools/cut-video cut-video \
  <video-dir>/cuts.json \
  <video-dir>/source.mp4 \
  -o <video-dir>/cut-master.mp4

# Cut an audio-only source (e.g. render the voiceover from raw.mp3 + cuts.json)
uv run --project tools/cut-video cut-video \
  <video-dir>/cuts.json \
  <video-dir>/audio/raw.mp3 \
  -o <video-dir>/audio/voiceover.mp3 --mode audio

# Preview the keep-windows + filtergraph without invoking ffmpeg
uv run --project tools/cut-video cut-video cuts.json source.mp4 -o out.mp4 --dry-run

# Extract the audio track to an mp3 (e.g. for transcription)
uv run --project tools/cut-video cut-video extract-audio source.mp4 \
  -o audio/raw.mp3 --mono --ar 16000 --bitrate 64k
```

## Tunables

- `--mode video|audio` — override the inferred mode.
- `--crf` (default 12), `--preset` (default `medium`) — libx264 quality/speed.
- `--epsilon-frames` (default 1) — drop keeps shorter than this many frames.
- `--snap` — snap keep boundaries to the nearest integer frame time.
- `--dry-run` — print the before/after summary + the generated filtergraph and
  exit without invoking ffmpeg.
- `extract-audio`: `--bitrate` (default `64k`), `--mono`, `--ar`.

Requires `ffmpeg` (and `ffprobe`) on PATH.

## Tests

Run the suite scoped to this tool (the repo is a flat collection of `uv`
projects with no root config, so collect from the project, not the repo root):

```bash
uv run --directory tools/cut-video pytest -q
# or, equivalently, from inside the tool: cd tools/cut-video && uv run pytest -q
```

The pure keep-math + filtergraph tests run anywhere; the CLI integration tests
(real ffmpeg cut, byte-identical re-run, A/V-sync, extract-audio) self-skip when
`ffmpeg`/`ffprobe` are not on PATH.
