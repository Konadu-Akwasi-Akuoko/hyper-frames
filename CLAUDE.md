# hyper-frames — project notes

## Project layout — one repo, many videos

Every video is a self-contained folder under `videos/<slug>-<YYYY-MM-DD>/`, with
its own `index.html`, `design.md`, `hyperframes.json`, `package.json`,
`compositions/`, `assets/`, source audio, transcript, and rendered output.
Never author HyperFrames files at the repo root — the root is reserved for
shared concerns (CLAUDE.md, README, .claude/, docs/, the videos/ index).

When starting a new video:

1. Pick a kebab-case slug from the working title (short and recognizable, not
   the full sentence).
2. Create `videos/<slug>-<YYYY-MM-DD>/` (date = today, when work begins).
3. Run `npx hyperframes init` from inside that folder.
4. Drop the source audio in `audio/` and the user-supplied transcript at the
   folder root as `transcript.json`.
5. All subsequent CLI commands (`lint`, `inspect`, `preview`, `render`) run
   from inside that folder, never from the repo root.

The first video, `videos/why-text-is-hard-2026-05-07/`, is the canonical example
of this layout.

## Authoring workflow

This project is a HyperFrames pipeline: voiceover → transcript → composition → render.
**To author or continue any video, invoke the `video-director` skill.** It directs the
`hyperframes` / `hyperframes-cli` / `hyperframes-registry` plugin skills (sequencing,
state-tracking, and wiring on top of them — not replacing them), works a few sentences
at a time, anchors every animation to `transcript.json`, runs a visual-QA loop on each
scene, and resumes from what's already mounted in `index.html`. It carries the
project's composition-authoring policy — transcript-as-timing-truth, composition
structure (registry-then-local, parametrized blocks), the lint/inspect/snapshot
visual-QA loop, the no-editorial-chrome rule, and the sound-design hand-off — which used
to live in this file and now lives in `.claude/skills/video-director/` (SKILL.md +
`reference/`).

The HyperFrames-origin skills now come from the official **`hyperframes` Claude
Code plugin** (marketplace `heygen-com/hyperframes`), which keeps them current
with upstream — install with `/plugin marketplace add heygen-com/hyperframes`
then `/plugin install hyperframes@hyperframes`. That plugin supplies
`hyperframes`, `hyperframes-cli`, `hyperframes-media`, `hyperframes-registry`,
`website-to-hyperframes`, the animation adapters (`gsap`, `waapi`, `animejs`,
`three`, `lottie`, `css-animations`, `tailwind`), and a few extras
(`contribute-catalog`, `remotion-to-hyperframes`, `typegpu`). Browse them when
picking a tool for a scene; `hyperframes-registry` in particular governs
`hyperframes add` and how blocks/components get wired into the project.

The project's **custom skills stay local under `.claude/skills/`** —
`script-writer`, `voiceover-elevenlabs-v2` / `voiceover-elevenlabs-v3`,
`transcribe-and-plan-cuts`, `thumbnail-creator`, `description-writer`,
`create-srt-and-translate`, `youtube-seo-research`, `youtube-studio`,
`audio-bed-music`, `design-catalog-add`, and `video-director`
(the composition-authoring orchestrator, which now also owns the **SFX pass** —
sound effects are scored inside `video-director` Step H on top of `tools/sfx-plan`
+ `tools/sfx-level`, not in a separate skill). These are not part of the plugin;
do not delete them when refreshing the plugin.

For voiceover in this project, the **default is recording your own voice**: drop
the recording at `audio/raw.mp3`, run the `transcribe-and-plan-cuts` skill (Scribe
v2 transcript + a first-pass cut plan), refine the cuts in `tools/audio-editor`,
and render `audio/voiceover.mp3`. That recorded-voice path is the reason
`tools/audio-editor/` exists. **TTS is the alternative** — reach for
`voiceover-elevenlabs-v2` (ElevenLabs Multilingual v2 + Scribe v2, the long-form
stability champion that matches the plain-prose house style) when you need
mic-free, repeatable, or multi-language narration; use `voiceover-elevenlabs-v3`
only when a video genuinely needs inline audio tags for per-beat emotional shifts.
The `hyperframes-media tts` (Kokoro) path stays parallel for any non-ElevenLabs
use case. Either way, the Scribe v2 `transcript.json` is the timing source of
truth. See `learnings/pipeline.md` Stage 3 for the full recorded-voice vs. TTS split.

Official docs: https://hyperframes.heygen.com/introduction (full text index at
https://hyperframes.mintlify.app/llms.txt). Use these as the upstream source of
truth when the local skills are silent or ambiguous.
