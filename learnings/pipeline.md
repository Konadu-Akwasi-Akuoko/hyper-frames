# HyperFrames video pipeline — moved

The pipeline reference now lives in **[pipeline.html](./pipeline.html)** — the
single canonical, browsable doc (stage cards, the sound-design lifecycle, the
captions/publishing flow, the Shorts engine, and the failure smells). Open it in
a browser; it is kept current with the skill set.

This file is now just a pointer so existing links keep resolving. The inbound
reference in `CLAUDE.md` (the Stage 3 recorded-voice vs. TTS split) points at
`pipeline.html`.

## What's in pipeline.html

- **Main pipeline** — topic → publish, stages 0–13. Authoring is `/video-director`
  (the orchestrator over the `hyperframes` plugin skills), which owns the SFX
  pass as **Step H**. `/hyperframes` is no longer the authoring entry point.
- **Sound & music** — the SFX three-subsystem split (`tools/sfx-catalog` →
  video-director Step H → `tools/sfx-plan`, with `tools/sfx-level`) plus the
  human-curated music bed (`/audio-bed-music`), which sits beneath SFX.
- **Captions & publishing** — `/create-srt-and-translate` (English `captions.srt`
  by default, the 13 translations only on an explicit request), `/description-writer`,
  the manual YouTube upload, and `/video-publish-qa` (the post-upload metadata gate).
- **Shorts engine** — `/shorts-creator` (two-phase long-form → ~5 vertical 9:16
  Shorts; portrait is a layout delta on video-director).
- **Smell tests** — the spec-over-restriction failure smells + the rules.

> **Companion read:** [composition-spec-over-restriction.md](./composition-spec-over-restriction.md)
> — why the design/compose stages stay deliberately lightweight.
