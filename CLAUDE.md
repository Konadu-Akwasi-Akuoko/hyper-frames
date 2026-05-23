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
`sfx-author`, `audio-bed-music`, and `design-catalog-add`. These are not part of
the plugin; do not delete them when refreshing the plugin.

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

### 1. Transcript-as-timing-truth

Animations must land on the spoken word, not on round numbers. A word-level
transcript (ElevenLabs Scribe v2-shaped) is the authoritative timing source.
Pull `start`/`end` for the exact word an animation punctuates and key
entrances/highlights/cuts to those timestamps. Round numbers ("at 4.0s, fade
in") are a code smell — find the word and use its timestamp.

The transcript is supplied by the user's own pipeline, not generated here. Don't
run `hyperframes-media transcribe` or assume Whisper output — work from the
`transcript.json` at the video folder root.

This is the single biggest lever for the video feeling alive vs. merely synced.
It matters more, not less, as runtime grows.

**`transcript.json` schema (Scribe v2):**

```ts
{
  audio_duration_secs?: number,          // present on most Scribe v2 outputs
  language_code: string,
  language_probability: number,
  text: string,                          // full concatenated text
  words: Array<                          // discriminated on `type`
    | {
        text: string,
        type: "word",
        start: number,                   // seconds, global to the audio
        end: number,                     // seconds, global to the audio
        speaker_id: string,
        logprob?: number,
      }
    | {
        text: string,
        type: "spacing",
        start: number,                   // seconds, global to the audio
        end: number,                     // seconds, global to the audio
      }
  >
}
```

`speaker_id` and `logprob` only appear on `"word"` rows; `"spacing"` rows are
bare timing markers between words. Discriminate on `type` when reading.

`start`/`end` are global audio timestamps. If you need scene-local time,
subtract the scene's start offset (the offset is the global timestamp of the
scene's first word).

**Do not `Read` `transcript.json` directly.** It's ~1500+ word entries per
video — reading it floods context with data you'll mostly discard. Run a
filtered `python3 -c` against it instead and only the matching slice lands in
context:

```bash
# Find every word in a time window (seconds, global). Adjust START/END/SCENE_START.
python3 -c "
import json
t = json.load(open('transcript.json'))
START, END, SCENE_START = 289.0, 305.0, 274.12
for w in t['words']:
    if w['type'] == 'word' and START <= w['start'] <= END:
        print(f\"{w['start']:.2f}  (local {w['start']-SCENE_START:.2f})  {w['text']}\")
"
```

Variations: filter by `w['text']` substring to locate a phrase, or print just
`start` for the first match if you only need one timestamp. If the schema ever
looks off, sanity-check with `head -c 500 transcript.json` (cheap — no full
read).

**`tools/narration-map/` is an optional planning aid, not the source of timing
truth.** Run it once per video when you want a one-shot overview — pause
windows (gaps > 400ms), scene-boundary candidates (pauses after `.!?`), and
top-N longest-duration words (often the emphatic moments). For per-tween
anchoring, the python filter above is more direct.

```bash
# From inside the video folder, when you want the planning overview:
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

### Sound design — the last authoring pass

Sound design follows visuals, never drives them. Run it only after the
composition is settled in `npx hyperframes preview`.

The pipeline ships with:

- A shared SFX library at `sound-effects/` (~1416 assets across 4 sub-libraries).
- A repo-level metadata catalog at `sound-effects/sfx-catalog.yml` (committed;
  rebuild only when the library changes via `uv run --project tools/sfx-catalog sfx-catalog`).
- A Claude skill at `.claude/skills/sfx-author/` that proposes a cue plan,
  awaits human approval, and writes `data-sfx-*` annotations into the HTML.
- A deterministic placement tool at `tools/sfx-plan/` that resolves
  annotations into a native HyperFrames audio sub-composition at
  `compositions/sfx.html`.

Assets staged into `videos/<slug>/assets/sfx/` are **relative symlinks** into
`sound-effects/`, not copies. `sound-effects/` must stay at the repo root —
moving it, or shipping a video folder to a machine without the library,
breaks playback in both preview and render.

Invoke the skill when visuals are done and you want SFX:

> "add sound design to this video" / "score this composition" / "do the sfx pass"

The skill always proposes its full plan before writing anything. Treat the
proposal as the contract — refine before approval, not after the fact.

**Phase A scope, by design.** This pipeline handles SFX placement only. Music
beds, ambient drone, sidechain ducking, and master loudness normalization to
−14 LUFS / −1 dBTP are Phase B/C — explicit non-goals for now.

### 2. Lint / inspect / preview before declaring done

The HyperFrames CLI loop catches real bugs (overlapping tweens, contrast failures,
layout overflow, missing assets). Run it — don't skip to render:

- `npx hyperframes lint` — schema + static checks
- `npx hyperframes inspect` — composition tree, timing, asset resolution
- `npx hyperframes preview` — visual check before committing render time

**The user always has `npx hyperframes preview` running in another window.** Do
not start, restart, or kill the preview server — they reload the open studio tab
themselves after edits. After any composition change, tell the user the timestamp
or scene to seek to so they can verify in the already-open preview. The
`hyperframes` skill barely mentions preview — it lives in the `hyperframes-cli`
skill, and Claude tends to skip the seek-to-verify step unless told. Treat
"surface a seek target" as a hard step on every authoring/edit task. Skip it only
for non-composition edits (CLAUDE.md tweaks, asset renames that don't touch HTML).

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

The catalog is broad — captions, shader and CSS transitions, VFX (shatter, portal,
liquid, 3D device showcases), maps, a data chart, effects (grain, vignette,
shimmer), social overlays, flowchart, logo outro. Browse it visually at
https://hyperframes.heygen.com/catalog/. The **caption components are
word-timeable** — a direct fit for transcript-as-timing-truth, usually better than
hand-rolling text emphasis. And don't default every beat to GSAP: `three`,
`lottie`, `css-animations`, `waapi`, and `animejs` each own a lane.

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
