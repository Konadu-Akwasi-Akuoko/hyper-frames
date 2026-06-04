---
name: video-director
description: Author a HyperFrames video incrementally from an approved `script.md` + Scribe v2 `transcript.json`, a few sentences at a time, anchoring every animation to real transcript word timings and wiring each block into `index.html`. Use this whenever the user wants to turn a script into a composition — "build the video", "author the composition", "animate this script", "direct this video", "keep going on the video", "continue the composition", "do the next scene" — or names a `videos/<slug>-<date>/` folder that has `script.md` + `transcript.json` + `design.md` and asks to make it move. Use it even when the user doesn't say "video-director" by name; if the task is turning narrated script text into HyperFrames scenes, this is the skill. It DIRECTS the `hyperframes` / `hyperframes-cli` / `hyperframes-registry` plugin skills (it sequences, tracks state, and wires — it does not replace them), resumes cleanly across sessions by reading what's already mounted, and runs a visual-QA loop on every scene. It also owns the **SFX pass** — sound effects are scored per scene as Step H (right after each scene's visual QA) and reconciled across the whole video at the end, on top of `tools/sfx-plan` + `tools/sfx-level`. Runs after voiceover + transcript exist and before `audio-bed-music`. Not for the music bed, not for generating the voiceover/transcript — those are upstream/downstream skills.
---

# video-director

You are the director sitting on top of the `hyperframes` plugin skills. The
script is written, the voice is recorded, the transcript is timed — your job is
to turn that narration into a moving composition, **a few sentences at a time**,
without trying to build the whole video in one context-blowing session.

Why incremental: a finished explainer is dozens of scene blocks. Authoring them
all at once buries the timing detail that makes a video feel alive and makes the
session impossible to reason about. Instead you author the next 1-2 sentences as
one composition block, wire it in, verify it actually looks good, and stop on a
clean boundary. The next session — yours or a fresh one — reads `index.html` to
see how far you got and picks up the next uncovered sentence. The mounted blocks
ARE the durable state; there is no sidecar progress file to keep in sync.

What you own vs. what you delegate is the whole point of this skill, so be clear
about it:

- **You own** sequencing (which chunk next), state detection + resume,
  mapping transcript words to script sentences, choosing the timing anchor for
  each animation beat, the `index.html` wiring math, and the per-pass quality
  gate.
- **You delegate** every piece of composition mechanics to the plugin skills.
  How a GSAP timeline is built, the data-attribute contract, the
  transition/entrance/exit rules, the determinism constraints — that is the
  `hyperframes` skill's job. The CLI commands are the `hyperframes-cli` skill's
  job. Installing a registry block is the `hyperframes-registry` skill's job.
  Invoke them; don't reimplement them.

## Preconditions

Before authoring anything, confirm the video folder is ready:

- `script.md`, `transcript.json` (Scribe v2, word-level), and `design.md` exist.
- `index.html` + `hyperframes.json` exist (i.e. `npx hyperframes init` has run).
- The voiceover audio is in place (`audio/voiceover.mp3`), mounted as the
  `<audio>` track in `index.html`.

If the transcript or design is missing, stop and point at the upstream skill
(`transcribe-and-plan-cuts` / voiceover-* for timing; `script-writer` /
`design-catalog-add` for the design). Don't author against round-number timing
or an undefined palette.

**Visual Identity Gate (defer to the `hyperframes` skill):** read `design.md`
once at the start of a session before you author. Every color, font, and motion
choice traces back to it. The `hyperframes` skill enforces this gate — honor it.

## The incremental loop

One pass = the next **1-2 sentences** (or one small coherent micro-beat — a
single sentence that carries a distinct visual idea, like "Ten days." standing
alone). Repeat until the whole script is covered. Each pass is self-contained so
the loop survives a fresh session.

### A. Detect current state

1. Resolve the video folder: an explicit path the user gave → the current
   working directory if it's a video folder → otherwise ask.
2. Read `design.md` (the gate, once per session).
3. Read `index.html` and enumerate the mounted **scene** hosts — the `<div>`s
   with `data-composition-src="compositions/..."` on a scene track. For each,
   note `data-composition-id`, `data-start`, `data-duration`, `data-track-index`.
   Ignore the voiceover `<audio>`, the `substrate-layer`, `sfx-layer`,
   `music-layer` — those are not scenes.
4. Compute the **frontier** = the max of (`data-start` + `data-duration`) across
   scene hosts. That's how far into the audio the video is already authored. An
   index with only the scaffold (root + voiceover + maybe substrate, zero scene
   hosts) has frontier = 0.
5. Read `script.md` (cheap — always fine to read in full).
6. **Never `Read` `transcript.json` directly** — it's ~1500+ entries and floods
   context. Run a filtered `python3 -c` to find the transcript word at ≈the
   frontier time, then locate that word in `script.md`. Everything after it is
   uncovered; the next sentence is your resume point. The filter patterns are in
   `reference/transcript-timing.md`.

Full state-detection and resume logic, including edge cases (mid-video gaps, a
block whose duration doesn't reach the next sentence, a script edited after
blocks were authored): `reference/state-and-resume.md`.

### B. Select the next chunk

Take the next 1-2 sentences after the frontier, or a shorter beat if one
sentence is its own visual idea. **Quote the chunk text back to the user in one
line** so the pass is auditable — they should be able to see exactly what you're
about to animate. Identify the chunk's first content word and the last word
before the next chunk starts.

### C. Pull exact transcript word timings

Run the `python3 -c` filter (see `reference/transcript-timing.md`) to get:

- `chunk_start` — the `start` of the chunk's first word.
- `chunk_end` — the `end` of the chunk's last word.
- the specific word timestamps for each beat you'll animate (the entrance, each
  highlight, the payoff word).

Round numbers ("fade in at 4.0s") are a code smell — find the word and use its
timestamp. This is the single biggest lever for the video feeling alive instead
of merely synced, and it matters more as runtime grows.

### D. Decide the block's design

**Let the sentence decide how the scene looks — this is the highest-leverage
choice you make.** The single biggest failure mode is every scene looking the same:
muted text on a centered card, beat after beat. A concession, a power claim, a
pivot question, a statistic, a quote each want a *different* composition. Before
you author, pick a layout **archetype that fits this beat's meaning** (side-cutout
+ image, full-bleed kinetic type, split/contrast, diagram/build, stat hero, quote
card, checklist, code reveal — the menu lives in `reference/visual-language.md`),
and **never reuse the previous scene's archetype back-to-back**. Then ask the imagery question as a **default, not a coin-flip**. Text can almost
always carry a beat — so don't ask whether it *can*; read what the sentence is
*doing*. These signals are the tell: a **named emotion** (surprise, grief, smugness,
panic); **irony, comedy, or a punchline** (the payoff turns on a twist — "the
language nobody wanted now runs the world"); a **human reaction**; a **named "who"**
(a specific person, creator, company, character); or a **concrete thing you'd
recognise on sight** (a real object, place, person, product, or logo — not a concept
you'd draw). On any of these the default is to **declare an asset box**
(`reference/assets-and-media.md`) and reach for it — don't wait to be talked into it.
Set the box's `data-asset-class` so `image-sourcer` routes to the right source: `reaction`
(emotion/punchline → Pinterest), or for a named recognisable thing `logo`/`glyph` (→ Iconify,
saved as a static SVG) or `photo` (→ Wikimedia, licensed). A named thing earns the box only
when it *is* the beat's subject and is recognisable on sight — not every noun (`visual-language.md` §2).
The explainers people actually binge lean on exactly this (a laughing cutout landing
an ironic payoff, a real face on the "who"), and that small reach is what keeps a
viewer from clicking away. Pure text on a signal beat is the **exception you
justify** — the line is genuinely abstract, or a code/diagram/stat says it better —
not just "text can carry it." Text-only stays right for genuinely typographic beats
(a quiet word landing in silence, a pure claim, a definition), where forcing a face
would only cheapen it. The test is the signal in the sentence, **not the scene
number, and never a quota**. The background is not a neutral grid — it carries a rationed
subject tone (`visual-language.md` §1).

Before you author, **emit a per-chunk verdict block** — one per chunk in this pass, the same auditable discipline as Step B, where you quote the chunk text back so the pass can be checked. Quoting the text proves *which* line you're animating; the verdict proves *how you read it*, so the imagery decision is on the record instead of happening silently inside the authoring. The block is exactly:

  Chunk: "<first few words…>"
  Imagery: box: class=<logo|glyph|photo|reaction> referent="<thing>" [emotion="<e>"] [treatment="<…>"]
           — OR —  text-only — <named candidate> weighed, rejected because <principled reason>
  Type-role: <role→font assignments for this chunk; verbatim human quote → human-voice font, never system font>

The iron rule: a `text-only` verdict must **name the candidate it weighed and why it loses** — literal/cheesy, not the beat's subject, an abstract with no settled mark, or already carried by a neighbour. A bare "just typographic" with no named, rejected candidate is no longer a reachable outcome; declining is a *named* rejection, not a shrug. This keeps `text-only` first-class — it stays the right call for genuinely typographic beats — but only as an auditable decision, never a quota and never a default you fall into by inertia. Fold the type-role line in while the chunk is in front of you: route a verbatim human quote (or a hand-drawn annotation) to the design's reserved human-voice font, and never let that font carry system narration. Worked examples for both sets — the §2 imagery gate and the font roles — are in `reference/decision-examples.md`; copy the reasoning, not the scenes.

Then check these sources for the pieces, in order, and author:

1. **Official HyperFrames registry** — `npx hyperframes catalog`
   (`--type block`, `--tag transition`), and the caption components for
   word-timed text (often a better fit than hand-rolling text emphasis). If a
   real match exists, invoke the `hyperframes-registry` skill and
   `npx hyperframes add <name>`.
2. **The user's personal `design-catalog/`** — an optional glance (viewer at
   `design-catalog/index.html`, built by `tools/design-catalog`, grown via the
   `design-catalog-add` skill). It's currently sparse, so don't expect hits —
   but check it as it grows; it's where the user parks motion graphics worth
   reusing.
3. **Author it locally** (the default for this project's didactic primitives —
   pixel grids, Bézier canvases, code reveals, comparisons — which won't be in
   either catalog). A recurring primitive → a **parametrized local block** with
   `data-composition-variables`, so the next video can reuse it. A genuine
   one-off → a plain local block. Either way it lives under `compositions/`.

Obey `design.md` tokens and the no-editorial-chrome rule throughout. Details and
the parametrized-block pattern: `reference/composition-structure.md`.

**`design.md` is the design source — never a prior cut of this same video.** If
the video was authored before and backed up (a git tag like `js-king-pre-director`,
a `/tmp` copy, an archived `compositions/`), that backup is **not** a design
reference and **not** a quality bar to reproduce. Its charts, layouts, and motion
are off-limits — lifting them makes the work circular and (in an eval) measures
nothing. You may read an old block *only* for the code **skeleton** — scoped CSS,
the paused `window.__timelines` registration, the tween-commenting convention —
never to copy its visual design. The grading bar is the **fresh** composition you
produce here, judged by a human + Opus against `design.md`. Design every block
original; mechanics that `design.md` itself prescribes are fair game, a prior
block's inventions are not.

### E. Author the composition block

Defer the mechanics to the `hyperframes` skill; this is what's specific here:

- One **full HTML document** at `compositions/<NN>-<slug>.html` — **not a
  `<template>` wrapper**. The canonical skeleton (head + GSAP + scoped style +
  `<div data-composition-id>` root + paused timeline registered on
  `window.__timelines["<id>"]`) is in `reference/composition-structure.md`.
- Layout before animation: build the static hero frame first, then add the GSAP
  keyed to the Step-C word timestamps.
- **Real imagery → labeled asset box.** Where the beat wants a photo/clip you
  can't generate, drop a styled placeholder `<div data-asset … data-asset-desc>`
  sized to the asset's real footprint (usually a full-height side cutout), and
  animate the *box* as the asset will move. The user fills it later; the full
  contract (attributes, the shopping list, swapping in the file, `image-prep`
  treatment) is in `reference/assets-and-media.md`.
- Time inside the block is **scene-local**: subtract `chunk_start` from each
  global word timestamp.
- Entrance animation + a transition into the scene. **No exit animation** unless
  this is the final chunk of the whole script (the transition is the exit) — but
  if this scene's foreground text must clear before the *next* scene's text comes
  up at the seam, fading that foreground out across the trailing overlap is part of
  the transition, not a forbidden exit (see Step F).
- **Motion language** beyond entrance: edge slide-ins, layout reflow (new elements
  push existing ones aside rather than stacking on them), and a constant
  low-amplitude idle (tilt/drift) so nothing sits perfectly still.
  `reference/visual-language.md` §3.
- Deterministic only — no `Math.random`, `Date.now`, or `repeat: -1`.
- Do **not** add `data-sfx-*` annotations while authoring visuals — SFX is scored
  in the dedicated Step H of *this* skill, once the scene's visuals pass QA.

### F. Wire the host into index.html

Append a host `<div>` after the previous scene host, using the attribute set
from `reference/composition-structure.md`:

- `data-composition-id`, `data-composition-src="compositions/<NN>-<slug>.html"`,
  `data-width="1920"`, `data-height="1080"`, and
  `style="position:absolute;inset:0;z-index:N"`.
- `data-start = chunk_start − 0.5` — a 0.5s overlap so the incoming scene can
  transition over the outgoing one.
- `data-duration` spans to the next chunk's first word so there's no visual gap.
- **Alternate `data-track-index` 1/2** versus the previous scene, so both scenes
  are mounted during the 0.5s overlap and the transition can actually render.
  (Transitions between scenes are mandatory — the `hyperframes` skill requires
  them — which is why the overlap exists.)
- **The seam must cover, not cross-dissolve text.** Both scenes are live during
  the overlap; if each just fades its whole layout, the two scenes' text collide
  into mush. The outgoing scene clears its foreground text before the incoming
  text is legible, or the incoming scene occludes with a wipe/slide/panel. Two
  readable text blocks never share the frame at a seam — verify by snapshotting at
  `prev_end − 0.25`. Detail: `reference/composition-structure.md` wiring rules.

Leave `#root` `data-duration` at the full voiceover length from the start.

### G. Verify — the visual-QA loop (regenerate until it looks good)

This is a hard gate, not a formality, and it is more than lint. A scene that
passes lint can still have unreadable 14px text, an emphasis that fires on the
wrong word, or a panel that escaped its frame. Catch that here, before the user
ever sees it. Per pass:

1. `npx hyperframes lint` — schema and timing. **Blocking.**
2. `npx hyperframes inspect --at <beat timestamps> --json` — text and container
   overflow at the *actual* animation beats (not just midpoint samples). Parse
   the JSON. **Blocking** — overflow is a real bug.
3. `npx hyperframes snapshot --at <chunk_start>,<key beats>,<chunk_end>,<seam>` —
   capture PNG frames of this scene, **including the seam with the previous scene**
   (`prev_end − 0.25`, mid-overlap) where text can collide. Then **dispatch a
   Sonnet subagent** (the Agent tool with `model: sonnet`) to `Read` the batch of
   PNGs and return a structured pass/flag report. Offloading the image read keeps
   this loop cheap. Pass the subagent the detailed rubric from
   `reference/verify-and-preview.md` (legibility, palette/type per `design.md`,
   anchored emphasis landing on the word, contrast, reads-as-a-diagram, no chrome,
   **seam collision**, **per-scene distinctness**, **imagery fit**, **type-role
   fidelity**, **liveliness**).
   It returns `{frame, verdict, flags[]}` per image. **Claude does the looking — no
   Gemini, no `--describe`.**
4. **If anything is flagged → fix the block (back to Step E) and re-run 1-3 on
   this scene only. Loop until the frames look right.** Small text, weak contrast,
   off-anchor emphasis, overflow, a scene that looks like its neighbour, a seam
   that mushes two text layers — each one is a regenerate, not a shrug.
5. Only once the scene passes: surface the seek target so the user can confirm
   in their own preview — "Seek to **{chunk_start}s** to verify scene NN." If the
   pass left any **asset boxes**, surface the **shopping list** here too (the table
   from `reference/assets-and-media.md`) so the user knows exactly which images/
   video to drop in.

**Verdict check.** Confirm every signal beat in this pass resolved to either a
declared asset box or a written, candidate-named `text-only` justification — i.e. the
per-chunk verdict (Step D) was actually emitted, not skipped — which is the auditable
checkpoint that the imagery decision was made on the record rather than silently
defaulting to bare text.

**Never start, restart, or kill the preview server.** The user always has
`npx hyperframes preview` running in another window and reloads it themselves.
`snapshot` and `inspect` run headless in their own Chrome — they don't touch the
running preview. Full command detail and the rubric: `reference/verify-and-preview.md`.

### H. Score the SFX for this pass

Sound is scored **per pass, on the scene(s) you just authored** — while this
scene's GSAP tween times and the Step-C word timings are still in context. That
freshness is the whole point: it is how a cue lands neither early nor late. You
score **only this pass's scene(s)** here; the whole-video reconcile runs once at
the Done condition (below). SFX is **not just booms and risers** — the common
case is small punctuation driven by *this scene's own beats*. Dense policy lives
in `reference/sfx-cues-and-timing.md` (mode/cue/asset mechanics, the `data-sfx-*`
contract, peak math) and `reference/sfx-arc-and-reconcile.md` (the arc ledger,
density shape, final reconcile); this is the per-pass sub-flow.

1. **Punctuation cues from this scene's GSAP beats — the common case.** Walk the
   timeline you just wrote and score what each beat is *doing*, never by CSS
   class: a thing **appears** → `ui-tick`/`pop`; something **slides in** →
   `whoosh`; something is **highlighted** → `ui-tick`/`msg-ding`; something
   **snaps into place** → `ui-tick`; a card **taps in** → `card-tap`. These are
   visual changes, so the timing mode is **`data-sfx-at-scene-ms`** (scene-local
   ms, relative to the host's own `data-start`). Compute the **perceptual
   landing** from the tween you just keyed — a **fade** lands at `start +
   dur×0.5–0.7`, a **slide/snap** at `start + dur`. **Pin every cue's asset** with
   `data-sfx-asset`, reusing the file a same-family cue already uses in this video.
   Lead with these — most passes are nothing but punctuation.

2. **Spoken-word cues — anchor mode.** When the trigger is a *word landing* (a
   label said aloud, a name read, a payoff line), use **`data-sfx-anchor` +
   `data-sfx-anchor-index`** (1-indexed), never `data-sfx-at-scene-ms`. The two
   modes are **mutually exclusive** — using anchor + a large negative lead to
   *reach* a visual moment is the forbidden SFX-before-visual bug. The anchor must
   resolve in `narration-map.json` at write time — if the word isn't there, append
   it to `anchors.txt`, re-run `tools/narration-map`, and verify it resolves
   **before** writing the attribute. `data-sfx-lead-ms` is ±100 ms peak-tuning
   only (≥200 ms warns; treat as blocking).

3. **Heavy/global cues — against the derived arc ledger.** `boom`, `riser`, and
   the single `data-sfx-hook` are rationed across the *whole* video, not this
   pass. There is no sidecar — **derive** the budget: read `story-spine.md` (if
   present) / `script.md` for where hook/climax/landing fall, then **scan the
   already-placed `data-sfx-*` across all compositions** for what's already spent
   (mounted state is the source of truth). Spend a heavy cue only on a genuine
   peak the ledger hasn't claimed; score the hook with **restraint** (one decisive
   cue, or silence into the hit — never a stack). Most passes spend none.

4. **VO check + the 0.5 rule.** Before committing each cue, probe the narration
   under it — `uv run --project ../../tools/sfx-level sfx-level audio/voiceover.mp3
   --at <t>` returns VO RMS/peak dBFS and classifies gap vs. active speech — to
   confirm the cue lands where you think and catch one fighting hot VO. Volume is a
   flat **0.5 default *and* ceiling**, set once as `default_volume: 0.5` in
   `sound-effects/sfx-catalog.yml` — do **not** write `data-sfx-volume="0.5"` on
   elements. Write `data-sfx-volume` **only to duck below 0.5** when sfx-level
   reports the VO is hot under the cue; never above.

5. **Compact proposal + approval gate.** Print one terse line per cue — `mode= /
   cue= / asset= / on <element> / <short reason>` — plus a `ledger:` line and any
   `NEW ANCHORS NEEDED`. **Write `data-sfx-*` annotations only on
   `yes`/`approve`/`go`** (one `Edit` per element; never reformat surrounding
   HTML). Honor a **standing approval** ("auto-approve SFX for the rest") so the
   autonomous loop runs uninterrupted on later passes; absent that, the gate holds
   each pass — but keep printing the compact proposal for the record. Full format:
   `reference/sfx-arc-and-reconcile.md`.

6. **Plan, then ear-audit.** Run `uv run --project ../../tools/sfx-plan sfx-plan
   --report` from the video folder — it idempotently regenerates the whole
   `compositions/sfx.html` and reports cue count plus warnings. A
   `DensityViolationError` fails the run (>1 cue/s in a 6s window — real, fix it);
   a `large lead_ms`, density (>0.5/s), or `overlap on track` warning still exits
   0 but *you* treat it as blocking. SFX correctness is **partly
   ear-only** — a snapshot can't show sound — so surface the seek target for the
   cued beat ("Seek to **{t}s** to hear scene NN") and let the **human
   listen-in-preview audit stay the gate** for this pass; the deterministic tools
   (`sfx-plan` warnings + `sfx-level`) are the automated backstop, not a
   substitute. **Never start, restart, or kill the preview server.**

### I. Loop or stop

If more script remains and the session still has headroom, go back to Step A
(state is re-detected, so the loop is idempotent and self-correcting). To stop
for the session, stop on a **block boundary** — never mid-block — and report:
the chunks authored this pass, the new frontier timestamp, and the next
uncovered sentence. Optionally drop a frontier hint in `index.html`:
`<!-- director: covered through {t}s / "…last sentence" -->`. The next session
resumes purely by re-running Step A; treat the mounted hosts as the source of
truth and the comment as a convenience.

## Done condition

The whole script is covered (every sentence maps to a mounted block whose
window spans its transcript words), lint and inspect are clean, the final block
holds the only exit animation, every scene has had its per-pass SFX score (Step
H), and you've surfaced the last seek target. Then run the **final SFX
reconcile** — one whole-video pass that re-runs `tools/sfx-plan` over everything
and verifies the density curve/shape (no `DensityViolationError`; trim any
6s-window warning), per-track overlap, your own same-cue spacing (the tool does
not check cooldowns — you do), that `boom`/`riser` were spent only on genuine
peaks, that **exactly one** `data-sfx-hook` exists and
was scored with restraint, that the `tools/sfx-level` sweep finds no cue fighting
loud VO, and that the `sfx-layer` mount spans the full runtime (checklist:
`reference/sfx-arc-and-reconcile.md`). Only then hand off to the music bed
(`audio-bed-music`) — music sits *beneath* SFX and is the one sound layer you
never author yourself.

## Delegation map

| Concern | Owner | Your role |
|---|---|---|
| Composition mechanics: data-attrs, `class="clip"`, `window.__timelines`, layout-before-animation, transition/entrance/exit rules, determinism | `hyperframes` | Tell it *which chunk*, *what design*, *which word timestamps* to key to |
| CLI loop: `init` / `lint` / `inspect` / `snapshot` / `preview` / `render` | `hyperframes-cli` | Decide *when* (lint+inspect+snapshot every pass, blocking); run the snapshot→Sonnet-review→regenerate loop; never touch preview; surface a seek target |
| Registry: `catalog`, `add`, snippet-merge, `hyperframes.json` | `hyperframes-registry` | Check it before authoring; hand off the install/wire |
| Animation adapters (gsap / three / lottie / css / waapi / animejs) | those skills | Pick the lane per beat; don't re-document them |
| Image sourcing: find + fetch a real asset for a box, routed by `data-asset-class` — `reaction`→Pinterest, `logo`/`glyph`→Iconify (static SVG), `photo`→Wikimedia (licensed), web as catch-all — then treat it | `image-sourcer` agent | Declare the box with its `class`/`referent`, then dispatch `image-sourcer` (`model: sonnet`) with the `data-asset-*` spec + `video_dir`; weigh its confidence, swap the pick in (or leave the box standing + shopping-list on failure), surface any required attribution (`reference/assets-and-media.md`) |
| Image treatment: background removal + VFX presets (grain/duotone/halftone/vintage) | `tools/image-prep` | Declare asset boxes + the shopping list; the `image-sourcer` agent runs image-prep for you, or run it directly on a human-supplied raster for a consistent cutout look (`reference/assets-and-media.md`) |
| Voiceover / transcript | voiceover-* / `transcribe-and-plan-cuts` | Precondition; refuse to run if missing |
| SFX scoring: cue choice, timing mode, the arc ledger, the per-pass + final-reconcile passes | **you** (Step H, this skill) | Own it — score each scene's sound after its visual QA; ration the heavy cues across the video |
| SFX mechanics: `data-sfx-*` resolution → `compositions/sfx.html`; VO loudness at a cue | `tools/sfx-plan` / `tools/sfx-level` / `sfx-catalog.yml` | Annotate + run them; never hand-edit `sfx.html` |
| Music bed | `audio-bed-music` | Hand off only after the final SFX reconcile; never author the music yourself |

## Reference files

Load these as needed — they hold the dense, project-specific authoring policy
that used to live in the root `CLAUDE.md`:

- `reference/transcript-timing.md` — the Scribe v2 schema, the `python3 -c`
  filter patterns (so you never `Read` the transcript), the narration-map
  planning aid, and the seo/research.json note.
- `reference/composition-structure.md` — multi-block default, the
  catalog-then-local decision, the **full-HTML-doc block template** and the
  **index.html host-wiring template** (incl. the seam-collision transition rule),
  and the parametrized-local-block pattern.
- `reference/visual-language.md` — the look layer: the background's rationed
  **subject tone** (no logo), **per-scene archetype variety** (so scenes don't all
  look alike) with the archetype menu, and the **motion language** (slide-ins,
  layout reflow, constant subtle tilt/drift). Read before designing any block.
- `reference/assets-and-media.md` — using **real images/video via labeled boxes**
  the user fills: the `data-asset` placeholder contract, the collected shopping
  list, swapping in the file, and the `tools/image-prep` treatment (BG-removal +
  VFX presets).
- `reference/decision-examples.md` — the worked-example bank for Step D's
  **per-chunk verdict**: Set A (does this beat earn an image — logo/glyph/photo/
  reaction YES vs. a candidate-named `text-only`) and Set B (which font carries
  each role — verbatim quote → human-voice font, etc.). Copy the reasoning.
- `reference/verify-and-preview.md` — the lint → inspect → snapshot → Sonnet
  PNG review → regenerate loop, the visual-QA rubric (incl. seam-collision,
  distinctness, imagery, liveliness; snapshot the seam), and the
  never-touch-preview + surface-a-seek-target rules.
- `reference/sfx-cues-and-timing.md` — the SFX reading layer for **Step H**: the
  full cue vocabulary (appears/slide/highlight/snap → tick/pop/whoosh/ding, not
  just booms), the anchor-vs-`at-scene-ms` timing-mode decision + perceptual-
  landing math, peak alignment / leads / cooldowns / density ceiling, asset
  pinning, and reading `tools/sfx-level` for the 0.5-default-and-ceiling volume.
- `reference/sfx-arc-and-reconcile.md` — the SFX budget layer for **Step H**:
  density-as-narrative, the single hook moment, the per-pass **arc ledger by
  derivation**, the compact proposal + standing approval, and the **final
  whole-video reconcile checklist** before the `audio-bed-music` hand-off.
- `reference/house-rules.md` — no editorial chrome; the music bed is the last
  pass (and is someone else's pass).
- `reference/state-and-resume.md` — reading `index.html` into a frontier,
  mapping it back to the next uncovered sentence, batching across sessions, and
  the resume edge cases.
