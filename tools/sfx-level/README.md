# sfx-level

A deterministic **voiceover-loudness probe** for SFX cue placement. Given a
voiceover track and a moment, it tells you how loud the narration is right there
— so you can see whether a cue lands in a real gap or on top of a spoken
syllable. It reuses `tools/cut-snap`'s numpy short-time RMS so the two tools
measure loudness identically (no librosa / pyloudnorm stack).

It is the audio-level half of the video-director SFX step (Step H): `tools/sfx-plan`
aligns each cue's own `peak_time_s` onto the moment; `sfx-level` reads the
voiceover *at* that moment so you can confirm the placement. SFX volume itself is
a fixed **0.4** hard peg in `tools/sfx-plan` — this probe is advisory and never
sets a level.

## Usage

Run from a video folder.

```bash
# Single moment
uv run --project ../../tools/sfx-level sfx-level audio/voiceover.mp3 --at 12.84

# Every placed cue in a generated sfx.html
uv run --project ../../tools/sfx-level sfx-level audio/voiceover.mp3 \
    --batch compositions/sfx.html
```

Flags:

- `--at <seconds>` — probe one timestamp.
- `--batch <sfx.html>` — report the VO level at every `<audio>` cue's `data-start`.
- `--window-ms <ms>` — half-window radius around the moment (default `120`).
- `--json` — machine-readable output.

## What it reports

- `rms_dbfs` / `peak_dbfs` — the voiceover's loudness in the window.
- `classification` — `gap` (room-tone quiet, the cue sits in the clear) vs
  `active-speech` (a word is being spoken here). Calibrated per file: a window
  within `+8 dB` of the track's room-tone floor reads as a gap.
**Advisory only — no volume recommendation.** SFX volume is a fixed **0.4** hard
peg, applied uniformly in `tools/sfx-plan` (`PEG_VOLUME`): every cue plays at 0.4
"no matter the sfx", and a `data-sfx-volume` override is ignored. This tool does
not recommend a level — it tells you whether a cue lands in a clean gap or on top
of a word so you can judge its *placement*. A cue fighting hot VO is fixed by
retiming or rechoosing the cue, never by changing its volume.

## Notes

- Deterministic: identical input → identical output.
- Requires `ffmpeg` on `PATH` (used to decode the audio to PCM, same as cut-snap).
