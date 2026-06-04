# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Releases are cut repo-wide in lockstep: every tool and video manifest carries the
same version.

## [0.7.0] — 2026-06-04

### Added
- **sfx-plan** — opt-in `--bake` finalize: mixes every cue into one
  `audio/sfx-mix.mp3` (ffmpeg; equal-power pan, unity `amix`, limiter, padded to
  the full mount duration) and emits a single `<audio>`, eliminating the per-cue
  `media_preload_none` lint noise and the preview-Play freeze caused by ~160
  force-loaded media elements. Per-cue `preload="none"` stays the fast editing
  default — bake LAST, since a plain run reverts it. Also writes
  `sfx.cues.json` so `sfx-level --batch` still recovers every cue's timing from a
  baked layer.

### Fixed
- **js-king** — preview Play froze while scrubbing still worked: the 162
  force-loaded SFX `<audio>` elements exhausted Chrome's WebMediaPlayer budget
  and evicted the voiceover into `MEDIA_ERR_DECODE`. `preload="none"` on every
  cue restores playback; renders are unaffected (compiler strips `preload`).

### Changed
- **repo** — ignore `renders/` output directories (large MP4 build artifacts;
  render locally, don't commit).

## [0.6.0] — 2026-06-04

### Added
- **sfx-level** — VO-loudness probe tool. Measures the voiceover's RMS loudness
  at a timestamp so the SFX pass places a cue in a real narration gap and ducks
  it correctly relative to speech (reuses cut-snap's RMS DSP).
- **sfx-plan** — `ensure_mount` now upserts the sfx-layer's `data-duration` to
  the full runtime (derived from `transcript.json`), so cues scheduled late are
  no longer silently clipped.
- **image-prep** — onnxruntime dependency for background removal.
- **js-king** — full composition built out: 91 scene sub-compositions plus a
  scored `sfx.html`, wired into `index.html`, with assets and QA snapshots.
- **prompt-evaluation** — video-director SFX-pass eval (iteration-5).

### Changed
- **video-director** — folds the SFX pass in as Step H (per-scene scoring after
  each scene's visual QA) plus a final whole-video reconcile; removes the
  standalone `sfx-author` skill and relocates its taste into
  `reference/sfx-cues-and-timing.md` and `reference/sfx-arc-and-reconcile.md`.
- **sfx-catalog** — flatten every cue role's `default_volume` to 0.5 (uniform
  ceiling; per-cue ducking handled at placement via `data-sfx-level`).
- settings: raise the autocompact threshold and window.
- Refresh narration-map and youtube-studio-mcp lockfiles.

## [0.5.0] — 2026-06-03

### Added
- **video-director** — composition-authoring orchestrator skill. Carries the
  project's authoring policy (transcript-as-timing-truth, registry-then-local
  structure, the lint/inspect/snapshot visual-QA loop, no-editorial-chrome,
  sound-design hand-off), extracted out of CLAUDE.md, and directs the
  hyperframes / hyperframes-cli / hyperframes-registry plugin skills.
- **image-prep** — image preprocessing CLI plus an image-sourcer agent, for the
  image-asset step of the video pipeline.
- **prompt-evaluation** — video-director eval workspace (reference study of an
  external video's motion patterns plus four graded iterations).

### Changed
- js-king: reset the composition to greenfield to re-author from scratch.

## [0.4.0] — 2026-06-02

### Added
- **cut-snap** — deterministic cut-boundary refiner. Snaps audio-cut-decider
  boundaries onto true acoustic silence via RMS-envelope analysis (plateau-edge
  anchor + breath pad + zero-crossing snap), with a transcript-label fallback.
- **dup-detect** — deterministic duplicate-take detector. Recovers identical
  re-takes the agent misses, keeps the tighter-delivered (default later) take,
  and rejects coincidental cross-sentence matches and rhetorical repetition
  (anadiplosis/anaphora) via a truncation / long-match / restart-pause test.
- **transcribe-and-plan-cuts** — deterministic refinement in the cut pipeline
  (agent → dup-detect → cut-snap → editor); the agent now keeps the last
  (completed) take, and the skip-transcribe path runs the full post-agent chain.
- **prompt-evaluation** — human-graded cut-quality eval workspace (the eval that
  produced cut-snap and dup-detect).

### Changed
- youtube-studio-mcp: refresh `uv.lock`.

## [0.3.0] — 2026-06-02

### Added
- js-king: sound design pass across all 12 scenes.

### Changed
- js-king: scaffold the music-bed pipeline; add the sound & music design playbook.
- tools: refresh sfx-plan and youtube-studio-mcp lockfiles.

## [0.1.0] — 2026-05-24

Initial release: the HyperFrames video pipeline, its tooling, and the first
videos.

### Added
- **why-text-is-hard** — the inaugural video and canonical project layout.
- **js-king** (javascript-the-king) — full 12-scene build: per-scene visuals with
  real brand icons and memes, word-level micro-animations, dead-zone fills, and
  scene-01 sound effects.
- **Tooling** — audio-editor, narration-map, sfx-catalog, sfx-plan,
  transcribe-elevenlabs, voiceover (ElevenLabs v2/v3), youtube-seo,
  youtube-studio-mcp, branding-render, thumbnail-render, design-catalog.
- **Pipeline docs** — recorded-voice voiceover default, post-render
  re-transcribe flow, design spec with the Excalifont typeface.

### Fixed
- analytics: fan `traffic_sources` detail mode out per source type.
- audio-editor: render region chrome inside the wavesurfer shadow root.

### Changed
- Migrate the HyperFrames skills to the official plugin.
- Drop the storyboard stage from the pipeline.
- audio-editor: prefer raw-timeline artifacts when present.
- mcp: apply the `http_safe` decorator to every tool registration.

[0.7.0]: https://github.com/Konadu-Akwasi-Akuoko/hyper-frames/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/Konadu-Akwasi-Akuoko/hyper-frames/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/Konadu-Akwasi-Akuoko/hyper-frames/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/Konadu-Akwasi-Akuoko/hyper-frames/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/Konadu-Akwasi-Akuoko/hyper-frames/compare/v0.1.0...v0.3.0
[0.1.0]: https://github.com/Konadu-Akwasi-Akuoko/hyper-frames/releases/tag/v0.1.0
