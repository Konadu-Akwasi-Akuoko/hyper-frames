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
Always invoke the `hyperframes` skill (and `hyperframes-cli`) before authoring or editing
compositions. The patterns below are project-specific overlays on top of those skills,
not replacements.

The full skill set lives under `.claude/skills/` — `hyperframes`, `hyperframes-cli`,
`hyperframes-media`, `hyperframes-registry`, `website-to-hyperframes`,
`script-writer`, `voiceover-elevenlabs-v2` / `voiceover-elevenlabs-v3`, plus animation adapters (`gsap`, `waapi`,
`animejs`, `three`, `lottie`, `css-animations`, `tailwind`). Browse them when
picking a tool for a scene; `hyperframes-registry` in particular governs
`hyperframes add` and how blocks/components get wired into the project.

For voiceover generation in this project, default to `voiceover-elevenlabs-v2`
(ElevenLabs Multilingual v2 + Scribe v2). It's the long-form stability champion
(per the official models page) and matches the project's plain-prose house
style. Use `voiceover-elevenlabs-v3` only when a video genuinely needs inline
audio tags for per-beat emotional shifts. The `hyperframes-media tts` (Kokoro)
path stays parallel and untouched for any non-ElevenLabs use case.

Official docs: https://hyperframes.heygen.com/introduction (full text index at
https://hyperframes.mintlify.app/llms.txt). Use these as the upstream source of
truth when the local skills are silent or ambiguous.

### 1. Transcript-as-timing-truth

Animations must land on the spoken word, not on round numbers. A word-level transcript
(ElevenLabs-shaped — see any per-video `transcript.json` at the video folder root for the
canonical shape) is the authoritative timing source. Each entry in `words[]` carries
`text`, `type` ("word" or "spacing"), `start`, `end`, and `speaker_id`; pull `start`/`end`
for the exact word an animation punctuates and key entrances/highlights/cuts to those
timestamps. Round numbers ("at 4.0s, fade in") are a code smell — find the word and use
its timestamp.

The transcript is supplied by the user's own pipeline, not generated here. Don't run
`hyperframes-media transcribe` or assume Whisper output — work from the
`transcript.json` at the video folder root (e.g.
`videos/why-text-is-hard-2026-05-07/transcript.json`) that the user has provided.

This is the single biggest lever for the video feeling alive vs. merely synced. It
matters more, not less, as runtime grows.

**Don't hand-roll `python3 -c` to find word timestamps.** The repo ships a
reusable narration-map tool at `tools/narration-map/`. Run it once per video,
right after the transcript lands, and key animations off the resulting
`narration-map.json` instead of grepping the raw transcript. The tool emits
anchor-word starts (for any phrases you list in `anchors.txt`), pause windows
(gaps > 400ms by default), scene-boundary candidates (pauses after `.!?`), and
the top-N longest-duration words (often the emphatic moments).

```bash
# From inside the video folder, once transcript.json is in place:
uv run --project ../../tools/narration-map narration-map \
  transcript.json --anchors anchors.txt
```

Writes `narration-map.json` next to the transcript. See
`tools/narration-map/README.md` for the full output shape and tunables.

**YouTube SEO research is a shared per-video artifact.** The
`youtube-seo-research` skill (backed by `tools/youtube-seo/`) generates
`<video-dir>/seo/research.json` from one topic phrase using yt-dlp +
YouTube autocomplete (free, no API key, ~25s). Multiple skills consume
it: `script-writer` reads it at the outline step (Step 2.5),
`thumbnail-creator` reads it at the paired-title step (Step 4). Run it
once per video — both skills will probe for it and offer to invoke the
`youtube-seo-research` skill if it's missing.

```bash
# From inside the video folder, after outline.md exists:
uv run --project ../../tools/youtube-seo seo-research
```

Writes `<video-dir>/seo/research.json`. See the skill's
`reference/signal-interpretation.md` for how to read the digest, and
`reference/consumer-integration.md` for which fields each consumer skill
uses.

### 2. Lint / inspect / preview before declaring done

The HyperFrames CLI loop catches real bugs (overlapping tweens, contrast failures,
layout overflow, missing assets). Run it — don't skip to render:

- `npx hyperframes lint` — schema + static checks
- `npx hyperframes inspect` — composition tree, timing, asset resolution
- `npx hyperframes preview` — visual check before committing render time

**After any composition edit, run `npx hyperframes preview` and surface the studio
URL (`http://localhost:<port>/#project/<project-name>`) to the user before declaring
the task done.** The `hyperframes` skill barely mentions preview — it lives in the
`hyperframes-cli` skill, and Claude tends to skip it unless told. Treat preview as a
hard step on every authoring/edit task, not an optional one. Skip it only for
non-composition edits (CLAUDE.md tweaks, asset renames that don't touch HTML).

Treat lint/inspect output as blocking. If something looks fine in preview but lint
flags it, fix the lint finding — those warnings have caught shippable-looking bugs.

## Composition structure

Default to multi-block compositions, regardless of runtime. Break scenes into
composition blocks under `compositions/` (per `hyperframes.json`) and wire them from
`index.html`. The first video
(`videos/why-text-is-hard-2026-05-07/index.html`, 1249 lines) shipped as a single
file because it was inaugural — that work is done, don't retrofit it. Going forward,
split scenes into blocks from scene one. Easier to reason about, easier to lint,
easier to swap or reorder when the script changes, and a prerequisite for reuse.

### Check the registry before hand-rolling

Before authoring any primitive — a chart, a card, a transition, a social overlay,
a logo outro, a grain texture, a shimmer sweep — browse the registry first:

```bash
npx hyperframes catalog                   # browse everything
npx hyperframes catalog --type block      # blocks only
npx hyperframes catalog --tag transition  # filter by tag
npx hyperframes add <name>                # install + wire
```

If a registry item matches the need, use `hyperframes add` — don't hand-roll over
it. **Always invoke the `hyperframes-registry` skill
(`.claude/skills/hyperframes-registry/`) before installing or wiring** — it governs
the snippet-merge, sub-composition mounting, and `hyperframes.json` registration
patterns. The skill exists; use it.

### Author missing primitives as parametrized local blocks

The registry skews toward branding, social overlays, shader transitions, and VFX.
The **didactic-explainer primitives** that recur in this project's videos — pixel
grids, Bézier canvases, high-resolution rasters, side-by-side comparisons, live
code reveals, algorithm visualizers — won't be there. When you need one, **don't
inline it in `index.html`.** Author it as a parametrized block under
`compositions/<name>.html`, declare its inputs with `data-composition-variables`
on the `<html>` root, and mount it from `index.html` via `data-composition-src`
+ `data-variable-values`.

The difference is "I built a bitmap grid for the letter A in this one video"
versus "I have a `bitmap-grid` block that takes any glyph at any resolution."
The first is a one-off; the second compounds across videos. Bias toward the
second from scene one — the third time the same primitive shows up, it should
already be a block, not another hand-coded copy.

If a local block proves useful across 2+ videos, consider promoting it to a
shared registry (custom/self-hosted via `hyperframes publish` or similar). Don't
optimize for that prematurely — prove the abstraction with the second video
first.

## Video generation

- **No editorial chrome.** When authoring HyperFrames compositions for this project,
  do not add corner metadata strips ("PROJECT-NAME · 01 / 09", "PART 01 · TITLE"),
  bottom scene labels ("SCENE 01 · HOOK"), or running timecodes ("00:00 / 02:00").
  The viewer never reads them — they steal screen real estate from the actual content.
  Hairline footer rules are also out by default.

  Ambient decoratives (radial glows, grid backgrounds, ghost type drifting in the
  background) are still fine — those add atmosphere, not labels. Only add chrome
  if the user explicitly asks for it.
