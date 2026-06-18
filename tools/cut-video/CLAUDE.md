# cut-video — notes

## Mode inference rule

The cut mode is **inferred from the source's stream set**, not guessed from the
file extension:

- If the source has a **video stream**, mode is `video`: both the video and the
  audio are trimmed on the same absolute keep-windows and concatenated
  (`-map [v] -map [a]`, re-encoded `libx264` + `pcm_s16le`).
- If the source is **audio-only**, mode is `audio`: only the `atrim`/`aconcat`
  half runs (`-map [a]`, `libmp3lame -q:a 2`).

Pass `--mode video|audio` to override. The chosen mode is then validated against
the stream set (video mode asserts exactly 1 video + 1 audio; audio mode asserts
exactly 1 audio) and fails loud otherwise.

## Determinism

All keep-window math and the `filter_complex_script` synthesis live in the
zero-I/O `segments` module — no RNG, no wall-clock, all boundary floats rounded
to 6 decimals before they hit the graph text. `ffmpeg.py` + `cli.py` own the
single `subprocess.run`. Always re-encode (never `-c copy`): stream-copy is
keyframe-bound and drifts on sub-frame cut boundaries.
