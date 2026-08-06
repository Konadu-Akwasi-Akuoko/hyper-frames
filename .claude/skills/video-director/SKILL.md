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
  How a motion timeline is built depends on the **library you pick for that
  beat** — GSAP for choreography, anime.js for swarms, three for 3D, etc. (Step
  D). Once the lane is chosen, **invoke the matching `hyperframes:<adapter>`
  skill before authoring** so its seek-safe patterns load. The data-attribute
  contract, the transition/entrance/exit rules, the determinism constraints —
  that is the `hyperframes` skill's job. The CLI commands are the
  `hyperframes-cli` skill's job. Installing a registry block is the
  `hyperframes-registry` skill's job. Invoke them; don't reimplement them.

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
2. Read `design.md` (the gate, once per session). You do **not** read the motion
   reference index yourself — the `scene-design-decider` subagent reads the two-tier
   `../../motionGraphicsInspo/README.md` per chunk (Step D) and returns a verdict, so
   the index stays out of your context. Just keep that path on hand to pass into the
   dispatch.
3. Read `index.html` and enumerate the mounted **scene** hosts — the `<div>`s
   with `data-composition-src="compositions/..."` on a scene track. For each,
   note `data-composition-id`, `data-start`, `data-duration`, `data-track-index`.
   Ignore the voiceover `<audio>`, the `substrate-layer`, `sfx-layer`,
   `music-layer`, and the `face-layer` (track-index 8, present only in
   talking-head mode) — those are not scenes (the face layer is full-runtime, so
   it must stay out of the frontier math). Also read the **root `#root` host's
   `data-width`/`data-height`** to fix the **canvas orientation**: default is
   landscape **1920×1080**; a **1080×1920** root means this is a **portrait**
   video (a Short / vertical) — read `reference/portrait-mode.md` once and author
   every block at 1080×1920. You don't choose orientation; you honor whatever the
   root declares (the `shorts-creator` skill scaffolds the portrait root). When
   the root is portrait, **this is a Short owned by `shorts-creator`** — you only
   author its composition. Selection, render, and **all publishing/distribution
   (the multi-platform OpusClip schedule) live in `shorts-creator`'s publish
   step**; never post or schedule from here. Defer to that skill for anything
   beyond the composition. And
   **detect a talking-head source** the same way: if `design.md` declares a
   `talking-head:` field **or** `assets/video/talking-head.mp4` exists, read
   `reference/talking-head.md` once and treat the face video as a **locked
   seek-driven layer beneath every scene** for the whole runtime. You detect it,
   you don't decide it (the human declares it), and it **composes with portrait**
   — a face-led Short is both.
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

**First chunk of a new video only — set the register's hold ceiling.** Before
settling how many sentences your *first* chunk carries, read the repo-root
`../../pacingInspo/README.md` Quick index and open the ONE entry whose register
matches this script: chaptered diagram/system-design explainer (≈1-3 cuts/min,
median scene 9-15s, one canvas held 100s+), brisk sectioned / tier-list
talking-head (≈6-10 cuts/min, ≈4-6s per item), fast video essay / listicle B-roll
churn (≈17-40 cuts/min, ≈1-3s a shot), or vertical Short (≈30+ cuts/min, sub-1.5s,
word-rate). Let that entry's `median scene` and `longest_hold_s` calibrate the
ceiling — a system-design explainer can hold one evolving substrate for many
sentences between resets, a fast essay wants a fresh visual each sentence. Read
the Quick index + that one entry block only; **never load a `<slug>-pace.json`
whole** (its per-scene transcript text floods context). This is evidence
calibrating the *ceiling*, not a target to hit — the transcript's own sentence
boundaries still decide each actual chunk — and you consult it once per video at
first-chunk time, never per chunk (chunk-level design is the
`scene-design-decider`'s job in Step D, and a per-chunk pacing lookup would just
repeat this one).

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
choice in the skill, and you delegate it.** The single biggest failure mode is every
scene looking the same (muted text on a centered card, beat after beat) with the motion
library never opened. The design decision for each chunk — its **archetype**, whether it
earns a **real image** (and which kind), which **motion reference** to adapt cadence from,
and the **font role** for each text piece — is made by the **`scene-design-decider`
subagent**. A dedicated decider, fed the previous scenes as images, picks a *fitted,
distinct* archetype and makes a *recorded* call on the motion library — the consultation
the director, under context pressure, tends to skip. You assemble its inputs, dispatch it,
then author from its verdict.

**Assemble the payload** (all cheap, mostly already in hand):

- the **chunk text** (Step B) and **±3 sentences** of surrounding `script.md` context;
- the **prior 1-2 scenes** — their `compositions/<NN>-*.html` source path(s) (from the
  Step A.3 host enumeration) **and** rendered snapshot PNG path(s): reuse the most recent
  Step G QA snapshot of those scenes if present, else take one quick headless
  `npx hyperframes snapshot` at each prior scene's midpoint (it doesn't touch the preview);
- the **last 2-3 archetypes** used (for the anti-repeat rule);
- the **`design.md` path** (palette/accent/font roles) and the repo-root
  **`../../motionGraphicsInspo/README.md` path**.

**Dispatch** the `scene-design-decider` subagent (the Agent tool,
`subagent_type: scene-design-decider`, `model: sonnet`) with that payload. It reads the
two-tier motion index itself, weighs the prior scenes' images, and returns a **structured
verdict** — the per-chunk record that Step G checks:

  CHUNK: "<first words…>"
  ARCHETYPE: <archetype> — <why it fits> | anti-repeat: <how it differs from the prior scene>
  IMAGERY: box: class=<logo|glyph|photo|reaction|background> referent="<thing>" [emotion=…]
           — OR —  text-only — <named candidate> rejected because <reason>
  MOTION-REF: <slug> — adapting <cadence>   — OR —   none — <nearest considered / "no fit" / "index empty">
  MOTION-LANE: <gsap|animejs|three|typegpu|lottie|waapi|css-animations> — <why this motion shape fits>
  TYPE-ROLE: <role→font; verbatim quote → human-voice font, never system font>
  NOTES: <optional authoring guidance>

**Match the motion library to the SHAPE of the motion**, per the verdict's
`MOTION-LANE` — never auto-default to GSAP:
- **`hyperframes:gsap`** — CHOREOGRAPHY: a few named elements in a precise
  multi-step sequence (enter → grow → count → settle); timelines, labels,
  position parameter, nesting. The pre-wired default; most text/graphic tweens.
- **`hyperframes:animejs`** — SWARM: many small elements moving as one
  coordinated field via `stagger()` (2D grid ripple, radial dial, particle/dot
  field, traveling wave). Tell: if you're writing a GSAP stagger over a grid and
  fighting it, switch.
- **`hyperframes:three`** — 3D/depth, camera moves, shader/displacement, WebGL.
- **`hyperframes:typegpu`** — GPU/WGSL shaders, compute, liquid-glass, thousands
  of particles.
- **`hyperframes:lottie`** — hand-illustrated / After-Effects-export loops.
- **`hyperframes:waapi`** / **`hyperframes:css-animations`** — ONE simple native
  enter/exit, cheap.
- **`hyperframes:tailwind`** — utility styling; pair it with a motion lane, it's
  not a lane itself.

**Once you pick the lane, invoke its `hyperframes:<lane>` skill BEFORE authoring
this beat's motion** — its `window.__hf*` registration + determinism patterns are
not in video-director, and default GSAP still means invoking `hyperframes:gsap`.
The lane governs **motion only**; it does nothing for **composition correctness**
(layout collisions, leaders crossing text) — that stays the inspect/snapshot
visual-QA loop's job (Step G).

**Author from the verdict.** It is the design spec for this block: build the named
**archetype**; declare the **asset box** with the verdict's `data-asset-class` (`reaction`
→ Pinterest, `logo`/`glyph` → Iconify SVG, `photo` → Wikimedia; `background` → human-supply
shopping list) and `referent`, or commit to **text-only**; **adapt the cited motion-ref's
cadence** (open its `<slug>-strip.png` yourself if you need the staging — the verdict names
the slug), reading it as the same *family*, never reproducing it; and route each text role
to the verdict's **font** (a verbatim quote → the human-voice font, never system
narration). If the verdict is genuinely wrong for the beat, you may **overrule it — but say
so explicitly in your authoring note**, so the override is on the record too; never
silently diverge.

**When a talking-head source is present** (Step A), the decider also returns the
chunk's **presentation mode** — FACE / GRAPHICS / PIP — as the verbatim `MODE:`
verdict line; content decides it per chunk, never a fixed slot
(`reference/talking-head.md`). The chosen mode **constrains the archetype pick**:
GRAPHICS runs the face hidden underneath (the archetype is unconstrained), PIP
requires the archetype to **reserve a safe zone** for the inset, and FACE leaves
the graphics scene empty/transparent (archetype + imagery moot). The full policy the decider applies (the §2 imagery gate, the archetype
menu, the motion-adapt rule, the type roles) lives in `reference/visual-language.md` and
`reference/decision-examples.md` — read them when you need to sanity-check a verdict.

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
  `<template>` wrapper**. The canonical skeleton (head + motion-library setup +
  scoped style + `<div data-composition-id>` root + paused timeline registered on
  `window.__timelines["<id>"]`) is in `reference/composition-structure.md`; it
  shows the GSAP default — invoke the verdict's `hyperframes:<lane>` skill first
  for the adapter's registration + seek-drive patterns.
- Layout before animation: build the static hero frame first, then add the GSAP
  keyed to the Step-C word timestamps.
- **Real imagery → labeled asset box.** Where the beat wants a photo/clip you
  can't generate, drop a styled placeholder `<div data-asset … data-asset-desc>`
  sized to the asset's real footprint (usually a full-height side cutout), and
  animate the *box* as the asset will move. The user fills it later; the full
  contract (attributes, the shopping list, swapping in the file, `image-prep`
  treatment) is in `reference/assets-and-media.md`.
- **Real background → labeled `background` box (human-supply).** When a beat's look —
  often one you drew from a motionGraphicsInspo reference — wants a real backdrop you
  can't draw (a wooden desk, a blueprint render, a skyscraper sky), drop a **full-frame
  `background` box** (`data-asset-class="background"`, `data-asset-placement="background"`)
  whose `data-asset-desc` says exactly what you want *and names the motionGraphicsInspo
  reference it riffs on plus how it diverges* — that's "put in the box what you like and
  I'll get it." Animate
  the box as the bg will move (slow drift/parallax). **Decide its scope:** a backdrop that
  should persist across scenes / set the whole video's mood is requested **as / into the
  substrate** (one request, not per-scene — `reference/composition-structure.md`); one
  specific to a single beat is a **scene-local** full-frame box in this block. A
  `background` box is **always human-supply** — it goes to the shopping list, never to
  `image-sourcer`. Request one only when it actually helps; ration it like any imagery
  (Step D / `reference/visual-language.md`). Contract: `reference/assets-and-media.md`.
- Time inside the block is **scene-local**: subtract `chunk_start` from each
  global word timestamp. **Exception — the face layer seeks with GLOBAL
  timestamps, zero offset** (it spans the whole runtime); never apply the
  scene-local subtraction to its seek (`reference/talking-head.md`).
- **Talking-head mode (when present) — author the chunk to its `MODE:` verdict.**
  A **FACE** reveal = show the `face-layer` host (track-index 8) at the exact
  global word timestamp; **GRAPHICS** = the same footage runs **hidden
  underneath** while the archetype covers the frame (nothing about the take
  moves); **PIP** = a **bordered, drop-shadowed inset** in the archetype's
  reserved safe zone, **never occluding** the live graphic. Policy +
  border/shadow + safe-zone geometry: `reference/talking-head.md`.
- Entrance animation + a transition into the scene. **No exit animation** unless
  this is the final chunk of the whole script (the transition is the exit) — but
  if this scene's foreground text must clear before the *next* scene's text comes
  up at the seam, fading that foreground out across the trailing overlap is part of
  the transition, not a forbidden exit (see Step F).
- **Entrance invariant — every appearing element must enter; nothing renders solid
  at scene-local t=0.** Scene-local t=0 is 0.5s *inside* the overlap with the
  previous scene, so any element opaque at t=0 bleeds onto it (the scene-21
  memory-gauge bug). Satisfy it either with the scene-root crossfade (fades the
  whole scene in) **or** a per-element `opacity:0` + `fromTo`. A tween that animates
  only `height`/`x`/`color` is not an entrance. Details + the seam consequence:
  `reference/composition-structure.md` ("Notes that matter" + wiring rules).
  **Carve-out (talking-head):** the locked `face-layer` is **exempt** — it is
  *supposed* to persist across every seam, so the invariant governs only the
  graphics/PIP revealed *on top* of it, not the continuous take
  (`reference/talking-head.md`).
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
  the host's **`data-width`/`data-height` matching the root** — landscape
  `1920`/`1080`, or **portrait `1080`/`1920`** when the root is vertical (Step A;
  `reference/portrait-mode.md`) — and `style="position:absolute;inset:0;z-index:N"`.
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
- **Talking-head mode transitions (when present) are seam-class events** — a mode
  change (FACE↔GRAPHICS↔PIP) lands on a **natural pause / sentence boundary**
  (after `.!?` primary, `>400ms` gaps secondary) via **crossfade or clean push**,
  never mid-clause (`reference/talking-head.md`).

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
   **seam bleed (text or graphic)**, **per-scene distinctness**,
   **archetype-family rotation (windowed, across a long subtopic)**, **imagery fit**,
   **type-role fidelity**, **liveliness**).
   It returns `{frame, verdict, flags[]}` per image. **Claude does the looking — no
   Gemini, no `--describe`.**
4. **If anything is flagged → fix the block (back to Step E) and re-run 1-3 on
   this scene only. Loop until the frames look right.** Small text, weak contrast,
   off-anchor emphasis, overflow, a scene that looks like its neighbour, a seam
   where one scene's text or a static no-entrance graphic bleeds over the other —
   each one is a regenerate, not a shrug.
5. Only once the scene passes: surface the seek target so the user can confirm
   in their own preview — "Seek to **{chunk_start}s** to verify scene NN." If the
   pass left any **asset boxes** — including any **`background` boxes** — surface the
   **shopping list** here too (the table from `reference/assets-and-media.md`) so the
   user knows exactly which images/video/backgrounds to drop in. Backgrounds are
   flagged as such in the list (with the substrate-vs-scene-local hint) because the
   user sources them during their manual review pass.

**Verdict check.** Confirm each chunk in this pass has a `scene-design-decider` verdict
(Step D) on the record, and that the verdict carries its **`MOTION-REF:` line** — a cited
slug-with-cadence or a named `none` (nearest-considered / no-fit / index-empty) — alongside
a resolved **`IMAGERY:` line** (a declared asset box or a candidate-named `text-only`) and a
named **`MOTION-LANE:` line** (the library the director then invoked before authoring this
beat's motion). The `MOTION-REF:` line *existing* (not its content) is the checkpoint that
converts a silently skipped motion-reference consultation into a logged decision; the
`IMAGERY:` line is the same checkpoint for the image-vs-text call; the `MOTION-LANE:` line is
the checkpoint that the library was a deliberate motion-shape choice, not a reflexive GSAP
default. If you overruled the verdict while authoring, that note is part of the record too.

**Never start, restart, or kill the preview server.** The user always has
`npx hyperframes preview` running in another window and reloads it themselves.
`snapshot` and `inspect` run headless in their own Chrome — they don't touch the
running preview. Full command detail and the rubric: `reference/verify-and-preview.md`.

### H. Score the SFX for this pass

Sound is scored **per pass, on the scene(s) you just authored** — while this
scene's GSAP tween times are still in context. That freshness is how each cue
lands on its visual. SFX in this project denote **visual events** (motion
graphics), never the audio. Mechanics live in `reference/sfx-cues-and-timing.md`
(the verb→cue palette, the impact-frame timing math, the `data-sfx-*` contract)
and `reference/sfx-arc-and-reconcile.md` (the per-pass proposal + final
reconcile); this is the sub-flow.

The governing rule: **each cue is independent and element-bound.** A cue is
placed because *its* visual event warrants a sound — never suppressed, delayed,
or skipped because of any other cue nearby. There are **no cross-cue rules** — no
cooldowns, no dedup, no density caps. Reuse a sound as often as you like,
including repeatedly within one scene.

1. **One cue per visual beat, chosen by the verb.** Walk the timeline you just
   wrote; score every beat that's *doing* something by what it does, never by CSS
   class: **appears/pops in** → `pop` (or `ui-tick`); **highlighted/named** →
   `msg-ding`; **lands with weight / a major point** → `boom`;
   **slides/travels / a transition crosses** → `whoosh`;
   **freeze-frame / highlight one element** → `snap`; a **card taps
   in** → `card-tap`. Every occurrence gets its cue — three cards appearing =
   three pops, one per card. (`riser` is retired — do not use it; score a
   building reveal on its payoff frame with `boom`/`pop`/`msg-ding`.)

2. **Timing = the impact frame.** The only mode is **`data-sfx-at-scene-ms`** —
   the scene-local ms (relative to the host's own `data-start`) when the element
   is *fully present*: for an entrance, the tween's `start + duration`; for a
   slide, where it settles; for a snap, the snap frame. Read it off the tween you
   just keyed. `sfx-plan` lands the cue's transient there (onset for punctuation,
   peak for whoosh) — **never early** — so you only supply the impact frame.
   `data-sfx-lead-ms` is a ±100 ms tuning knob only; you rarely need it.

3. **The signature sound is automatic.** Each cue pins one handpicked
   `default_asset` in `sound-effects/sfx-catalog.yml` and reuses it everywhere, so
   you usually write just `data-sfx-on-anchor="pop"` and get the right sound. Pin
   `data-sfx-asset` on an element **only** to deliberately diverge.

4. **The hook tag (for the music pass).** Mark the single biggest beat of the
   whole video — its one largest emotional/informational moment — with
   `data-sfx-hook="true"` on its element. It is a breadcrumb the downstream
   `audio-bed-music` pass reads to carve pre-impact silence; **exactly one** exists
   across the video. If this pass has no clear hook, omit it — a later scene may
   own it.

5. **VO check (advisory) + the 0.4 peg.** SFX volume is a fixed **0.4 hard peg**
   — every cue plays at 0.4 "no matter the sfx", set in `tools/sfx-plan`
   (`PEG_VOLUME`). **Do not write `data-sfx-volume`** — it is ignored (so is the
   catalog's `default_volume`). `tools/sfx-level` is now **advisory only**: probe
   the narration under a cue — `uv run --project ../../tools/sfx-level sfx-level
   audio/voiceover.mp3 --at <t>` (VO RMS/peak dBFS, gap vs. active speech) — to
   see whether a cue's *placement* lands in the clear or on top of a word. A cue
   fighting hot VO is fixed by **retiming or rechoosing the cue**, never by
   changing volume.

6. **Compact proposal + approval gate.** Print one terse line per cue — `cue= /
   asset= / at-scene-ms= / on <element> / <short reason>`. **Write `data-sfx-*`
   only on `yes`/`approve`/`go`** (one `Edit` per element; never reformat
   surrounding HTML). Honor a **standing approval** ("auto-approve SFX for the
   rest") so the autonomous loop runs uninterrupted; absent that the gate holds
   each pass — but keep printing the proposal. Full format:
   `reference/sfx-arc-and-reconcile.md`.

7. **Plan, then ear-audit.** Run `uv run --project ../../tools/sfx-plan sfx-plan
   --report` from the video folder — it idempotently regenerates the whole
   `compositions/sfx.html`. It **never fails on cue count or density** (those
   guards are gone); it only prints informational notes — a `pre-roll` note flags
   a whoosh used where an appearance belongs (switch it to `pop`/`ding`); an
   overlap note is benign (cues layer). SFX correctness is **partly ear-only** — a
   snapshot can't show sound — so surface the seek target ("Seek to **{t}s** to
   hear scene NN") and let the **human listen-in-preview audit stay the gate**.
   **Never start, restart, or kill the preview server.**

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
and verifies: every `pre-roll` note is intended (a whoosh leading a real
motion, not punctuating an appearance — fix those to `pop`/`ding`), that
**exactly one** `data-sfx-hook` exists, that the `tools/sfx-level` sweep (advisory)
finds no cue fighting loud VO — retime or rechoose any offender, since volume is
pegged at 0.4 and not adjustable — and that the `sfx-layer` mount spans the full
runtime (checklist: `reference/sfx-arc-and-reconcile.md`).

Once the SFX is locked and the final reconcile passes, **bake it** as the last
SFX action: `uv run --project ../../tools/sfx-plan sfx-plan . --bake`. This mixes
all cues into one `audio/sfx-mix.mp3` and emits a single `<audio>` (no
per-element `media_preload_none` lint noise, one media player instead of ~160 —
the per-cue layer otherwise freezes preview Play). **Bake LAST and don't re-run
plain `sfx-plan` afterward** — a plain run regenerates the per-cue editing layer
and reverts the bake. Track `sfx-mix.mp3` in git alongside `voiceover.mp3`. The
per-cue `preload="none"` form stays the default precisely because re-baking on
every edit would wreck the fast scoring loop. Only then hand off to the music bed
(`audio-bed-music`) — music sits *beneath* SFX and is the one sound layer you
never author yourself.

## Delegation map

| Concern | Owner | Your role |
|---|---|---|
| Composition mechanics: data-attrs, `class="clip"`, `window.__timelines`, layout-before-animation, transition/entrance/exit rules, determinism | `hyperframes` | Tell it *which chunk*, *what design*, *which word timestamps* to key to |
| CLI loop: `init` / `lint` / `inspect` / `snapshot` / `preview` / `render` | `hyperframes-cli` | Decide *when* (lint+inspect+snapshot every pass, blocking); run the snapshot→Sonnet-review→regenerate loop; never touch preview; surface a seek target |
| Registry: `catalog`, `add`, snippet-merge, `hyperframes.json` | `hyperframes-registry` | Check it before authoring; hand off the install/wire |
| **Scene design decision**: per-chunk archetype + imagery + motion-ref + motion-lane + type-role | **`scene-design-decider` subagent** | Assemble the payload (chunk + ±3 sentences, prior 1-2 scenes as source **+ images**, last archetypes, `design.md` + motion-index paths); dispatch per chunk (Step D, `model: sonnet`); author from the returned structured verdict; overrule it only with an on-record note. Its verdict is the audit log Step G checks |
| Motion inspiration: the repo-root `motionGraphicsInspo/` **two-tier index** — a Quick-index scan table over `Motion:`-note entries + strips (a *motion-technique* source, distinct from the registry/design-catalog *code-reuse* sources) | `scene-design-decider` (reads it) over `motionGraphicsInspo/README.md` | You **never read the index yourself** — the decider scans the Quick index, drills into a fitting entry, and opens its strip per chunk; **adapt the cadence, never reproduce the scene**; non-quota. Add references via the `motion-inspo-add` skill |
| Animation adapters (gsap / animejs / three / typegpu / lottie / waapi / css-animations / tailwind) | those skills | Decide the library per beat per the verdict's `MOTION-LANE` (match motion shape, not auto-GSAP); **invoke the matching `hyperframes:<lane>` skill to load its seek-safe patterns before authoring that beat's motion**; don't re-document them |
| Image sourcing: find + fetch a real asset for a box, routed by `data-asset-class` — `reaction`→Pinterest, `logo`/`glyph`→Iconify (static SVG), `photo`→Wikimedia (licensed), web as catch-all — then treat it | `image-sourcer` agent | Declare the box with its `class`/`referent`, then dispatch `image-sourcer` (`model: sonnet`) with the `data-asset-*` spec + `video_dir`; weigh its confidence, swap the pick in (or leave the box standing + shopping-list on failure), surface any required attribution (`reference/assets-and-media.md`). **`background`-class boxes are excluded — they're human-supply via the shopping list, never sent to `image-sourcer`.** |
| Image treatment: background removal + VFX presets (grain/duotone/halftone/vintage) | `tools/image-prep` | Declare asset boxes + the shopping list; the `image-sourcer` agent runs image-prep for you, or run it directly on a human-supplied raster for a consistent cutout look (`reference/assets-and-media.md`) |
| Voiceover / transcript | voiceover-* / `transcribe-and-plan-cuts` | Precondition; refuse to run if missing |
| SFX scoring: cue choice, the impact-frame timing, the per-pass + final-reconcile passes | **you** (Step H, this skill) | Own it — score each scene's sound after its visual QA; each cue is independent and element-bound (no cross-cue rules) |
| SFX mechanics: `data-sfx-*` resolution → `compositions/sfx.html`; VO loudness at a cue | `tools/sfx-plan` / `tools/sfx-level` / `sfx-catalog.yml` | Annotate + run them; never hand-edit `sfx.html` |
| Music bed | `audio-bed-music` | Hand off only after the final SFX reconcile; never author the music yourself |
| **Talking-head (when present)**: per-chunk presentation mode (FACE/GRAPHICS/PIP) + face-reveal timing; the one-time cut-and-derive prep | **you** (mode choice + reveal) / **ffmpeg** (delegated Step-A prep) | Detect the source in Step A (`design.md` `talking-head:` / `assets/video/talking-head.mp4`); as Step-A prep, plan cuts (`transcribe-and-plan-cuts`), apply them to the **video**, derive the muted picture + voiceover from the one cut master, then re-transcribe the cut audio (full order in `reference/talking-head.md`); own the per-chunk mode (rides the `scene-design-decider` `MODE:` verdict) and seek-driven face reveal on global timestamps (`reference/talking-head.md`) |

## Reference files

Load these as needed — they hold the dense, project-specific authoring policy
that used to live in the root `CLAUDE.md`:

- `reference/transcript-timing.md` — the Scribe v2 schema, the `python3 -c`
  filter patterns (so you never `Read` the transcript), the narration-map
  planning aid, and the seo/research.json note.
- `reference/composition-structure.md` — multi-block default, the
  catalog-then-local decision, the **full-HTML-doc block template** and the
  **index.html host-wiring template** (incl. the seam-bleed transition rule and the
  entrance invariant), and the parametrized-local-block pattern.
- `reference/visual-language.md` — the look layer: the background's rationed
  **subject tone** (no logo) and when a beat earns a **real background image**
  beyond the tinted substrate, **per-scene archetype variety** (so scenes don't all
  look alike) with the archetype menu (and the `../../motionGraphicsInspo/` references
  that illustrate them), and the **motion language** (slide-ins, layout reflow,
  constant subtle tilt/drift, and lifting concrete cadence from a reference's `Motion:`
  note). Read before designing any block.
- `reference/assets-and-media.md` — using **real images/video/backgrounds via
  labeled boxes** the user fills: the `data-asset` placeholder contract (incl. the
  full-frame **`background`** class — human-supply, never auto-sourced), the
  collected shopping list, swapping in the file, and the `tools/image-prep`
  treatment (BG-removal + VFX presets).
- `reference/decision-examples.md` — the worked-example bank for Step D's
  **per-chunk verdict**: Set A (does this beat earn an image — logo/glyph/photo/
  reaction YES vs. a candidate-named `text-only`) and Set B (which font carries
  each role — verbatim quote → human-voice font, etc.). Copy the reasoning.
- `reference/verify-and-preview.md` — the lint → inspect → snapshot → Sonnet
  PNG review → regenerate loop, the visual-QA rubric (incl. seam-bleed (text or
  graphic), distinctness, imagery, liveliness; snapshot the seam), and the
  never-touch-preview + surface-a-seek-target rules.
- `reference/sfx-cues-and-timing.md` — the SFX reading layer for **Step H**: the
  independence principle (each cue element-bound, no cross-cue rules), the
  verb→cue palette with each cue's signature `default_asset` + `align` mode, the
  **impact-frame** `data-sfx-at-scene-ms` timing (the tool lands the transient
  there, never early), and the fixed **0.4 volume peg** (with `tools/sfx-level` as
  an advisory placement probe).
- `reference/sfx-arc-and-reconcile.md` — the SFX workflow layer for **Step H**:
  the single hook tag (for the music pass), the compact proposal + standing
  approval, the per-pass write/regenerate steps (and the informational notes
  `sfx-plan` prints — pre-roll / overlap / clamped), and the **final whole-video
  reconcile checklist** before the `audio-bed-music` hand-off.
- `reference/portrait-mode.md` — the **vertical 1080×1920 delta** for Shorts:
  the dimension flip (root + CSS + viewport + every host), phone-UI **safe
  areas**, how each archetype family reflows landscape→vertical, the faster cut
  cadence, and the subscribe-CTA beat (the native portrait registry blocks +
  where the "Subscribe" cue sits). Read once when Step A finds a portrait root.
- `reference/talking-head.md` — the **talking-head delta** for a continuous
  on-camera take: the one-time prep (cut the video first, then derive the muted
  picture layer + the voiceover from one cut master, re-transcribe), the
  **seek-driven face layer** (`#face-layer`, track-index 8, full runtime), the
  three modes **FACE / GRAPHICS / PIP**, the content-decides-mode policy, the PIP
  safe-zone + border/shadow rules, and the boundary-snapped mode transitions.
  Read once when Step A detects a talking-head source (composable with
  portrait-mode).
- `reference/house-rules.md` — no editorial chrome; the music bed is the last
  pass (and is someone else's pass).
- `reference/state-and-resume.md` — reading `index.html` into a frontier,
  mapping it back to the next uncovered sentence, batching across sessions, and
  the resume edge cases.
