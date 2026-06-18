# derive-streams

Takes the talking-head **cut master** and emits BOTH delivered streams in one
deterministic run: a **muted picture** and the **voiceover audio**.

**Guarantee: one master → two frame-identical streams.** Both outputs are
derived from the SAME source with pinned encoder flags, so the picture and the
voiceover line up frame-for-frame by construction — there is no re-timing,
re-sync, or resample step that could let them drift. The argv math lives in a
zero-I/O module (no RNG, no clocks) and floats round to 6 decimals before they
are baked into the args, so identical inputs always produce byte-identical
commands.

## How it works

Two pinned ffmpeg invocations from the same master:

- **Video (muted picture):** `-an -c:v libx264 -crf 18 -preset slow
  -pix_fmt yuv420p -movflags +faststart`. NO scale filter — the picture is
  delivered at its native resolution; `-an` mute is mandatory.
- **Audio (voiceover):** `-vn -c:a libmp3lame -q:a 2`.

These flags are fixed by `talking-head.md` and honored verbatim.

Before running, `ffprobe` asserts the master has **exactly 1 video + 1 audio**
stream and fails loud otherwise. On a normal run the tool prints a
`[derive-streams]` summary confirming the two output durations match.

## Usage

```bash
uv run --project tools/derive-streams derive-streams \
  <cut-master.mov> \
  --video-out <assets/video/talking-head.mp4> \
  --audio-out <audio/voiceover.mp3> \
  [--crf 18] [--preset slow] [--audio-quality 2] [--dry-run]
```

`--dry-run` prints both ffmpeg argv lists and exits without running anything.

Requires `ffmpeg` (and `ffprobe`) on PATH.

## Tests

Run the suite scoped to this tool (collect from the project, not the repo root):

```bash
uv run --directory tools/derive-streams pytest -q
# or, from inside the tool: cd tools/derive-streams && uv run pytest -q
```

The argv-contract tests run anywhere; the integration tests (real two-stream
derive, byte-identical re-run, stream-count assertions) self-skip when
`ffmpeg`/`ffprobe` are not on PATH.
