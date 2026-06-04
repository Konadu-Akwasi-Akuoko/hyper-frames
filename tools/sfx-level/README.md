# sfx-level

A deterministic **voiceover-loudness probe** for SFX cue placement. Given a
voiceover track and a moment, it tells you how loud the narration is right there
— so a cue lands in a real gap (or ducks correctly) instead of fighting a spoken
syllable. It reuses `tools/cut-snap`'s numpy short-time RMS so the two tools
measure loudness identically (no librosa / pyloudnorm stack).

It is the audio-level half of the video-director SFX step (Step H): `tools/sfx-plan`
aligns each cue's own `peak_time_s` onto the moment; `sfx-level` reads the
voiceover *at* that moment to set the duck.

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
- `recommended_volume` — advisory, **capped at the project's `0.5` ceiling**.
  `0.5` is the flat default for every cue (set as each cue's `default_volume` in
  `sound-effects/sfx-catalog.yml`); this tool only ever recommends `≤ 0.5`. `0.5`
  is the rule: a cue keeps `0.5` in a gap *and* under ordinary speech. Ducking is
  a genuine exception — it drops below `0.5` only when the window approaches the
  track's loudest-speech level, where `0.5` would fight the word. When the tool
  recommends a duck, write that value as an explicit `data-sfx-volume` on the cued
  element; otherwise leave it off and the cue stays `0.5`.

## Notes

- Deterministic: identical input → identical output.
- Requires `ffmpeg` on `PATH` (used to decode the audio to PCM, same as cut-snap).
