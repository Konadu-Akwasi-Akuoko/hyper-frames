# hyper-frames — project notes

## Project layout — one repo, many videos

Every video is a self-contained folder under `videos/<slug>-<YYYY-MM-DD>/`, with
its own `index.html`, `design.md`, `hyperframes.json`, `package.json`,
`compositions/`, `assets/`, source audio, transcript, and rendered output.
Never author HyperFrames files at the repo root — the root is reserved for
shared concerns (CLAUDE.md, README, .claude/, docs/, the videos/ index).

When starting a new video:

1. Pick a kebab-case slug from the working title (short and recognizable, not
   the full sentence). **Exception — a video promoted from a `tools/studio` idea
   already owns its slug; match it exactly (see "From a promoted idea" below),
   don't invent a shorter one.**
2. Create `videos/<slug>-<YYYY-MM-DD>/` (date = today, when work begins).
3. Run `npx hyperframes init` from inside that folder. It scaffolds into a nested
   `my-video/` subdir — move its contents up into the folder root and remove it.
4. Drop the source audio in `audio/` and the user-supplied transcript at the
   folder root as `transcript.json`.
5. All subsequent CLI commands (`lint`, `inspect`, `preview`, `render`) run
   from inside that folder, never from the repo root.

The first video, `videos/why-text-is-hard-2026-05-07/`, is the canonical example
of this layout.

## Idea tracking & production board — `tools/studio`

`tools/studio` is the channel's single surface for **what to make** and **where
each video is**: a full-stack app (Hono `:3273` + Vite/React `:5273`, local
SQLite, no Docker) with two views — **The Wire** (an idea aggregator backlog) and
**The Desk** (the 12-stage production board whose progress is derived by scanning
`videos/`). It **supersedes** the old root `kanban.html` and
`tools/topic-pipeline/` — both retired (left in git history; do not maintain
them).

The flow: `studio-discover` (Python CLI) fetches raw signal from the seed YouTube
channels (videos + top comments) and the text aggregators (HN/Reddit/Lobsters/
daily.dev) into `raw_signal`; the **`studio-ideas` skill** curates that delta into
the idea backlog (qualitative keep/discard + a one-line rationale, **never a
grade** — and a suggested format, long/short/series, the human confirms);
promoting an idea on The Wire pops it out of the backlog and lands a
card on The Desk. All intelligence lives in the skill, never the server. Run it:

```bash
cd tools/studio && bun dev                       # Wire :5273, Desk + API :3273
cd tools/studio/discovery && uv run studio-discover --db ../studio.db   # then invoke studio-ideas to curate
```

Design + plan: `docs/superpowers/specs/2026-06-22-studio-idea-board-design.md`
(§10.1 = the "The Wire Desk" visual language) and
`docs/superpowers/plans/2026-06-22-studio-implementation.md`. Tool-local rules:
`tools/studio/CLAUDE.md`.

**From a promoted idea → video folder.** A promoted idea already has a Desk card
and a fixed slug — find it, don't re-derive it:

```bash
sqlite3 -json tools/studio/studio.db \
  "SELECT id,kind,status,title,rationale,source_url,promoted_slug \
   FROM ideas WHERE title LIKE '%<term>%';"
```

The video folder **must be named exactly `promoted_slug`** (it already ends in
`-<date>`). The Desk joins on-disk progress to the card **by exact folder name**
(`server/routes/board.ts` matches `board_overlay.slug` ↔ `videos/<name>`); any
other slug splits it into two cards. The slug is title-derived and long — keep it,
a shorter folder name loses board tracking. The card's `kind` (long/short/series)
and `source_url` (the seed video) are the brief.

## Authoring workflow

This project is a HyperFrames pipeline: voiceover → transcript → composition → render. The full stage-by-stage map — topic → publish, plus the
Shorts spur — lives in `learnings/pipeline.html`.
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

**After any compaction, re-invoke `video-director` before continuing composition
work.** Compaction summarizes the skill's SKILL.md + reference guides out of context
while this CLAUDE.md survives — so the mandate persists but the guidance does not.
Skills are live-watched, so re-invoking reloads the full guidance cheaply. Do this
before acting on the post-compaction summary, even for a narrow follow-up edit: treat
the mounted hosts in `index.html` as the source of truth for what is already built and
re-detect state per the skill's Step A rather than trusting the summary. (A
`SessionStart(compact)` hook also nudges this, but it can only inject a pointer, not
force the call — this line is the binding instruction.)

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

The project's **custom skills stay local under `.claude/skills/`** (not part of
the plugin — do not delete them when refreshing it):

- **Authoring:** `video-director` — the composition orchestrator; also owns the
  **SFX pass** as Step H, on `tools/sfx-plan` + `tools/sfx-level` (not a separate
  skill).
- **Script & research:** `script-writer`, `youtube-seo-research`.
- **Voiceover:** `transcribe-and-plan-cuts` (recorded voice, the default),
  `voiceover-elevenlabs-v2` / `voiceover-elevenlabs-v3` (TTS).
- **Packaging:** `thumbnail-and-title-generator` (now **reference-driven** — every
  variant replicates the layout of a proven thumbnail picked from the
  `thumbnailInspo/` library rather than designing from scratch; composition from
  the reference, the locked "Specimen" style vocabulary for the voice),
  `description-writer`, `create-srt-and-translate`.
- **Publishing:** `youtube-studio`, `video-publish-qa`, `shorts-creator`.
- **Music & catalog growth:** `audio-bed-music`, `design-catalog-add`, and
  `motion-inspo-add` — which grows TWO repo-root inspiration libraries on
  `tools/inspo-ingest`: `motionGraphicsInspo/` (single-beat motion references —
  hero + keyframe strip + tagged `Motion:` note; `video-director` consults it
  while picking each scene's archetype + motion) and `pacingInspo/`
  (whole-video scene-change × narration pacing studies; `script-writer` cites
  its measured numbers when calibrating reset cadence). A bare whole-video URL
  defaults to combined ingest into both from one download; see each library's
  CLAUDE.md for the curation contract. A **third** repo-root inspiration library,
  `thumbnailInspo/` (top YouTube thumbnails harvested from proven creators —
  one tagged entry per thumbnail with a replication-grade `Layout map`), is grown
  by `tools/thumbnail-inspo/` (`fetch.py` harvests from the CDN bot-wall-free;
  `grid.py` overlays a measuring grid; `build_readme.py` renders the index from
  the cataloging pass) and consumed by `thumbnail-and-title-generator`, which
  picks + grids + replicates a reference for every variant. See
  `thumbnailInspo/CLAUDE.md` for the pick-and-mimic contract.

The **publishing + retention skills** are grounded in `docs/creator-patterns.md`
— a synthesized reference distilled from 237 transcripts across 12 channels
(hook taxonomy, the first-10-seconds rule, the ~45–60s reset cadence, the Cleo
Shorts CTA, title formulas, and per-workstream wiring in §6). `script-writer`
front-loads a cold-open hook and resets every subtopic from §6 WS1.
`video-publish-qa` runs post-upload packaging QA (title / tags / description /
captions) via the `youtube-studio` MCP under a preview-then-confirm gate, fixing
what the v1 MCP allows and handing off captions (it can't write them). And
`shorts-creator` turns a finished long-form video into ~5 vertical 1080×1920
Shorts that funnel back to it — Phase 1 selects beats + drafts each clip's
Cleo-CTA script, Phase 2 builds one Short at a time by orchestrating `voiceover-*`
→ `video-director` (dimension-aware: a 1080×1920 root triggers
`reference/portrait-mode.md`) → `thumbnail-and-title-generator` (vertical) → render, with a
manual Studio upload/stagger hand-off (the v1 MCP can't upload or schedule).

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
truth. See `learnings/pipeline.html` (Stage 3) for the full recorded-voice vs. TTS split.

Two **render-safe deterministic CLIs own the talking-head prep's video-cutting +
stream-derivation** (pure segment/argv math, pinned encoder flags, no RNG/clock —
like `tools/cut-snap`): `tools/cut-video` applies a `cuts.json` to a take —
`--mode audio` renders the cut `voiceover.mp3` from `raw.mp3` (the rendering step
`transcribe-and-plan-cuts` hands off), and the default video mode concats the kept
segments into a frame-locked cut master; `tools/derive-streams` then splits that
cut master into the muted seek-driven picture layer (`assets/video/talking-head.mp4`)
and the `audio/voiceover.mp3` in one pass. `video-director`'s
`reference/talking-head.md` drives both as the one-time Step-A video prep.

## Hard rules (composition authoring)

These always apply when authoring a composition; `video-director` carries the
full versions.

- **No editorial chrome.** No corner metadata strips, scene labels, or running
  timecodes. Ambient decoratives (glows, grids, ghost type) are fine. Add chrome
  only if the user asks.
- **The user keeps `npx hyperframes preview` running.** Don't start, restart, or
  kill it — after any edit, tell the user the timestamp or scene to seek to.
- **Don't `Read transcript.json` directly** (~1500+ word entries flood context).
  Filter it with a `python3 -c` slice, and anchor animations to real word
  timings, never round numbers.

Official docs: https://hyperframes.heygen.com/introduction (full text index at
https://hyperframes.mintlify.app/llms.txt). Use these as the upstream source of
truth when the local skills are silent or ambiguous.
