# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
Releases are cut repo-wide in lockstep: every tool and video manifest carries the
same version.

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
