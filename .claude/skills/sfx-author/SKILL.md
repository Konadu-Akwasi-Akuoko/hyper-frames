---
name: sfx-author
description: Editorial sound-design pass for a finished HyperFrames video. Reads index.html + compositions/*.html + transcript.json + narration-map.json + design.md + sound-effects/sfx-catalog.yml. Proposes a SFX cue plan, awaits human approval, then writes data-sfx-* annotations and runs tools/sfx-plan to emit compositions/sfx.html as a native HyperFrames audio sub-composition. Use when the user says "add sound design", "score this video", "add sfx", "do the sound pass", or asks for cues/whooshes/ticks on a finished composition. Only runs after the composition is visually approved in preview.
---

# sfx-author

You are running the sound-design pass on a HyperFrames video whose visuals are
already finished. Your job is to decide *which moments earn a hit*, propose a
cue plan, get explicit human approval, then write `data-sfx-*` attributes into
the composition HTML and run `tools/sfx-plan` to materialize a native audio
sub-composition at `compositions/sfx.html`.

This is the **last** authoring pass before render. If the composition is not
visually settled in `npx hyperframes preview`, stop and ask the user to confirm
visuals are locked before continuing.

## Inputs you always read

From the video folder (`videos/<slug>-<YYYY-MM-DD>/`):

- `index.html` and every file under `compositions/*.html` — the visuals you are
  scoring. Skip `compositions/sfx.html` (that's your own output).
- `transcript.json` — word-level timing, the source of all spoken text.
- `narration-map.json` — pre-computed anchors, pause windows, scene-boundary
  candidates, emphatic words. This is your fastest path to timing.
- `anchors.txt` — the human-curated anchor list that produced `narration-map.json`.
  You may need to extend it (see `reference/anchor-discipline.md`).
- `design.md` — tone signals. Read it; do not pattern-match keywords. Use it as
  context for cue character choice, never as a mechanical filter.

From the repo:

- `sound-effects/sfx-catalog.yml` — available cues + per-asset metadata. The cue
  recipes (`ui-tick`, `whoosh`, `boom`, `riser`, `pop`) define what's pickable.

Optional, per-video:

- `sfx-overrides.yml` at the video folder root — override cue recipes for this
  video specifically (e.g. swap `ui-tick`'s candidate pool to sharper variants).
  Absence means "use repo defaults."

## What this skill does

- Reads all inputs above.
- Walks the visuals and the narration *together*. Identifies moments that earn
  a sound. Decides cue character per moment based on what the moment is *doing*.
- Produces a cue plan in the exact format shown in
  `reference/proposal-template.md`.
- **Hard-gates** on user approval before writing anything.
- On approval, makes surgical Edit calls to add `data-sfx-*` attributes to the
  named elements. Does not rewrite or reformat surrounding HTML.
- Registers any new anchor words in `anchors.txt` and re-runs `tools/narration-map`
  so the new anchors are resolvable (see `reference/anchor-discipline.md`).
- Runs `tools/sfx-plan` from the video folder. Reports the cue count, warning
  count, and the path written.
- Idempotently mounts the sfx-layer in `index.html` (only on first run).
- Launches `npx hyperframes preview` and surfaces the studio URL.

## What this skill does NOT do

- It does not author or modify animations. SFX follows visuals; visuals are not
  retimed for SFX.
- It does not delegate asset choice. Every cue must declare its asset via
  `data-sfx-asset` — picking the file is an editorial decision on par with
  picking the cue and the timing. `tools/sfx-plan`'s deterministic resolver
  still runs as a safety net for any cue that slipped through review without
  a pinned asset, but the skill should never *rely* on it: falling through to
  the resolver produces timbrally inconsistent scores across scenes (the same
  cue family ends up sounding different in scene 1 vs. scene 4). See Hard
  Rule 8 and the "Asset selection" subsection in the Playbook. For per-video
  pool tweaks that should apply across many cues, the right surface is still
  `sfx-overrides.yml`, not a one-off `data-sfx-asset` on every element.
- It does not edit `compositions/sfx.html`. That file is generated. If the user
  has hand-edited it, mention that next run will overwrite their changes.
- It does not run if visuals are unfinished. If `compositions/` contains stubs
  with `[ TO BE BUILT ]` or `PLACEHOLDER`, stop and surface the gap.
- It does not bypass the proposal-then-confirm gate. Auto-apply is forbidden.

## Hard rules (non-negotiable)

1. Propose the full plan before any HTML edit. The user must approve with the
   literal word `yes`, `approve`, or `go`. Any other response is a refine or an
   abort, not implicit approval.
2. Anchors in `data-sfx-anchor` must already exist in `narration-map.json` at
   write time. If you need a new one, add it to `anchors.txt` and re-run
   `tools/narration-map` *before* writing the attributes.
3. Respect the technical floors in the Playbook section. They are mix-craft
   physics, not aesthetics; violating them produces an actually worse mix.
4. Never edit `compositions/sfx.html` by hand. Always run `tools/sfx-plan`.
5. If `sfx-catalog.yml` is missing, stop and direct the user to run
   `uv run --project tools/sfx-catalog sfx-catalog`. Do not proceed without it.
6. **Visual-entry cues use `data-sfx-at-scene-ms`, never `data-sfx-anchor` +
   negative lead.** If the moment being scored is a visual element entering,
   exiting, or snapping into place (any tween on the cued element), the cue
   MUST use `data-sfx-at-scene-ms` set to the perceptual landing time computed
   from the element's GSAP tween: `start + fade_duration × 0.5–0.7` for fades;
   `start + duration` for travel-and-settle slides/snaps. Using
   `data-sfx-anchor` + negative `data-sfx-lead-ms` to *reach* a visual moment
   from a spoken word is forbidden — it's the bug pattern that produces
   SFX-before-visual desync. Anchors are for spoken-word cues only (label
   spoken aloud, name said, payoff line landing). See
   `reference/timing-modes.md` for the perceptual-landing formulas and a
   worked before/after example.
7. **`data-sfx-lead-ms` is a peak-tuning knob, not a timing-source knob.** Use
   it for ±100 ms nudges to compensate for an asset's perceived attack vs. its
   measured peak. Do not use it for ≥200 ms shifts to reach a different
   moment — if you're using a large negative lead to land on a visual, you're
   using the wrong reference; switch to `data-sfx-at-scene-ms`. `sfx-plan`
   emits a `large lead_ms` warning at ≥200 ms on anchor cues; treat it as
   blocking.
8. **Every cue must pin its asset via `data-sfx-asset`.** Picking the asset is
   an editorial decision, not a resolver job. Browse `sfx-catalog.yml`'s
   `assets:` section (filtered by the cue's pool) and pick the one whose
   character matches the moment. Prefer assets already used elsewhere in the
   same video for cross-scene timbral consistency — e.g. if `Hollow Pop 06.wav`
   carries the scene-01 pops, the scene-04 card pops should use it too unless
   you have a specific reason to diverge. The proposal must show
   `asset=<basename>` on every `✓` line. Cues without `data-sfx-asset` are a
   skill bug — `tools/sfx-plan`'s resolver still runs as a safety net, but
   relying on it produces timbrally inconsistent scores.

## Playbook

You operate from principles, technical floors, a cue character vocabulary, and
worked examples. You **do not** consult a rigid CSS-class-to-cue mapping table.
That kind of pre-decoding is what failed in
`learnings/composition-spec-over-restriction.md` — it strips the editorial leap
that distinguishes a real-looking moment from a generic one.

### Placement principles

**Mode decision — pick the timing mode *before* picking the cue.** For each
candidate moment, ask: *is the trigger a spoken word, or a visual change?*

- **Spoken word** (label spoken aloud, name said, line landing on a payoff
  word) → `data-sfx-anchor` + index. The "lead sound ahead of picture"
  principle below still applies via cue defaults.
- **Visual change** (card entering, slide-in, glyph snapping, label
  appearing) → `data-sfx-at-scene-ms`. Read the GSAP timeline at the bottom
  of the scene file; find the tween whose target is the cued element;
  compute scene-local ms = `tween_start_ms + (fade/slide_duration_ms ×
  0.5–0.7)` for fades, or `tween_start_ms + duration_ms` for slides/snaps
  that travel before settling. Drop `data-sfx-anchor`,
  `data-sfx-anchor-index`, and `data-sfx-lead-ms` on these — they're for the
  spoken-word path. See `reference/timing-modes.md` for full per-ease
  formulas and the scene-01-open worked example.

"Lead sound ahead of picture" (next principle) is about the asset's
`peak_time_s` math inside whichever mode you've picked. It is *not* a license
to use anchor + negative lead to reach a visual moment.

- Score moments that *earn* a hit — the spoken payoff, the visual punchline,
  the threshold cross between scenes, the reveal of the line that the line is
  about.
- Skip texture (typewriter chatter, decorative drift, ambient pulses) — they
  belong to atmosphere, not punctuation.
- Lead sound ahead of picture. The ear is faster than the eye; a cue that lands
  exactly on the frame feels late.
- Match cue character to what the moment is *doing*, not to what CSS class the
  element wears.
- When in doubt, score less. Silence is a tool, and an unused cue is cheaper
  than a wrong one.
- Read the script (`transcript.json`) first; only then look at the HTML.

### Technical floors (mix-craft physics, not aesthetic preferences)

These are not negotiable. Violating them produces an actually worse mix.

- **Peak alignment.** A cue's *peak* (catalog `peak_time_s`) lands on the
  anchor's `start`, not the cue's start. `tools/sfx-plan` does this math for
  you — your job is to pick the anchor correctly.
- **Default leads.** `-50ms` for `ui-tick`, `-150ms` for `whoosh`, `0ms` for
  `boom`, `-(duration)` for `riser`. Override via `data-sfx-lead-ms` only when
  you have a specific reason — keep a note in the proposal saying why.
- **Same-cue cooldowns.** `ui-tick` ≥ 2s apart; `whoosh` ≥ 4s apart;
  `boom` ≥ 30s apart. Two ticks 1.2s apart smear; the ear hears one event
  smeared over both, not two.
- **Density ceiling.** ≤ 1 cue per 3s rolling average across the whole video.
  Above ~1 per 1.5s, the tool will hard-fail — and rightly so, because the
  ducking math thrashes and VO intelligibility collapses.

### Cue character library

Pick by **intent**, not by element type. Five cues plus the option of silence.

| Cue       | Character           | Best when the moment is…                                              |
|-----------|---------------------|------------------------------------------------------------------------|
| `whoosh`  | spatial motion      | crossing a threshold, entering/exiting a frame, scene transitions      |
| `ui-tick` | discrete arrival    | a thing snapping into place, a label landing, a small reveal           |
| `pop`     | playful arrival     | softer than tick — lighter or rhythmic reveals                         |
| `boom`    | weight / finality   | scale, gravitas, the line that lands                                   |
| `riser`   | build-to-payoff     | tension into a reveal, the climb before the hit                        |
| *(none)*  | negative space      | the punchline is *the silence*; or the texture is texture              |

Available cues are defined in `sfx-catalog.yml`'s `cues:` section. If you need
a cue that isn't there, *stop and surface the gap* — don't author against an
imaginary cue. Adding new cues is catalog work, outside this skill's scope.

### Asset selection

Picking the cue is half the decision; picking the *asset within the cue's
pool* is the other half. The pool is defined in `sfx-catalog.yml` (or
overridden per-video in `sfx-overrides.yml`). Browse it before proposing.

Order of preference when picking:

1. **Cross-scene consistency.** If the same cue is already scored elsewhere
   in this video with a specific asset, reuse it unless the moment's
   character explicitly diverges. The score reads as one piece when the
   same cue family always sounds the same.
2. **Character match.** Among assets in the pool, pick the one whose
   timbre matches what the moment is doing — sharper for snaps, hollower
   for soft arrivals, brighter for lifts.
3. **Duration fit.** Avoid assets longer than the visual moment they
   punctuate — a 600ms tail on a 200ms card landing smears.

When the same cue is used three times in a row (the "rack" effect, as
with the scene-04 thesis cards), use the *same* asset for all three —
that's the point of the rack.

### Hook moment

Each video has at most **one** "hook moment" — the largest emotional or
informational beat. Mark it on its element with `data-sfx-hook="true"`. In
Phase A this is a breadcrumb only (no audio change). Phase C will use it to
mute music/ambience for ~500ms before the moment (pre-impact silence). Choose
the hook carefully; if you can't identify a single clear hook, omit the tag.

## The proposal you produce before any edit

Before touching HTML, print a plan in the exact format below. The full template
with annotations lives at `reference/proposal-template.md`; this is the
inline version.

```
SFX CUE PLAN — <slug>
Runtime <mm:ss> · <N> scenes detected
Read design.md as: <one-line characterization>
(informs cue character choice; no mechanical keyword-to-caps mapping)

Scene 1 (00:00–<scene end>) "<scene title or first-line gist>"
  ✗ skip   <element ref>                            (<reason in 6–10 words>)
  ✓ <mm:ss.ms>  mode=<anchor("word"#N) | at-scene-ms(N)>  cue=<name>  asset=<basename>  on <element ref>   (<one-line reason>)
  ...

Scene 2 ...

TOTAL: <count> cues  (breakdown by type)
DENSITY: 1 cue / <X.Xs> avg
NEW ANCHORS NEEDED: <list — empty if none>
NOTES:
  • <anything the user should know — e.g. hook moment, design.md tone read>

Approve to write annotations into HTML?  [yes / refine / abort]
```

The `mode=` column is mandatory and surfaces the editorial intent at review
time — picking the wrong mode is the SFX-before-visual bug Rule 6 forbids,
so the proposal makes it inspectable. Example lines:

```
✓ 00:07.42  mode=at-scene-ms(7420)  cue=pop  asset=Hollow Pop 06.wav  on .target #1   (signup-forms card landing — perceptual midpoint of 400ms fade-in)
✓ 00:02.79  mode=anchor("and"#1)    cue=card-tap  asset=Mouse Click 04.wav  on #s1-cb   (checkbox click follows the spoken "and")
```

Rules for the proposal:

- Every line shows either `✓` (will write) or `✗ skip` (considered, deliberately
  not scoring). Skips are as important as wrote-ins — they make your editorial
  reasoning legible.
- Reason fields stay short. The full thinking belongs in your own head; the
  proposal is a contract surface.
- `NEW ANCHORS NEEDED` lists any `data-sfx-anchor` values you intend to use that
  don't yet appear in `narration-map.json`. If the list is non-empty, your first
  write action is to extend `anchors.txt` and re-run `tools/narration-map` —
  before any HTML edit.

## Refine loop

The user can respond with `refine` plus natural-language instructions. Treat
each refine as a transformation on the current plan:

- "drop the boom in scene 3" → remove that line, re-print plan.
- "the hook is 02:48 not 03:41" → move the `data-sfx-hook` tag to the element
  spoken at 02:48, re-print plan.
- "score the Bézier markers after all — make them quieter" → add `ui-tick` cues
  with `data-sfx-volume="0.5"` on those elements, re-print plan.
- "the whoosh into scene 3 lands late" → after the plan is written, this is a
  post-preview refine: add `data-sfx-lead-ms="-200"` to that element and re-run
  `tools/sfx-plan`.

Loop until the user types `yes`/`approve`/`go`. Then write.

## After approval

1. If `NEW ANCHORS NEEDED` is non-empty: append each anchor on its own line to
   `anchors.txt` (preserve existing entries; add a `# sfx` comment block if
   useful for legibility). Then run:

   ```bash
   uv run --project ../../tools/narration-map narration-map \
       transcript.json --anchors anchors.txt
   ```

   from the video folder. Verify the new anchors appear in the regenerated
   `narration-map.json` before continuing.

2. Use the `Edit` tool to add `data-sfx-*` attributes to each scored element.
   One element per Edit call. Never reformat surrounding HTML.

3. From the video folder, run:

   ```bash
   uv run --project ../../tools/sfx-plan sfx-plan --report
   ```

   Report the cue count, warning count, and the studio URL.

4. Run `npx hyperframes preview`. Surface the URL the user should open. Stop
   and wait for their audit feedback.

5. On feedback, loop back into the refine flow.

## Failure modes you must handle gracefully

- **`sfx-catalog.yml` missing** → instruct the user to build it
  (`uv run --project tools/sfx-catalog sfx-catalog`) and stop.
- **Anchor not resolvable after extending `anchors.txt`** → the anchor text
  isn't a literal substring of the transcript. Surface the candidate words from
  `transcript.json` that are nearby in time and ask the user to choose a real
  anchor word.
- **`tools/sfx-plan` raises `DensityViolationError`** → the plan was too dense
  even though you tried to honor the ceiling. Drop the lowest-priority cues in
  the densest window and re-run.
- **Composition has placeholder stubs** (`[ TO BE BUILT ]` etc.) → stop. SFX is
  the last pass; visuals must be done first.
- **User asks for a cue not in `sfx-catalog.yml`'s `cues:` section** → don't
  invent. Tell the user the available cues; suggest a similar one; offer to
  open a catalog-revision task.
- **User asks for a specific named SFX file** → use `data-sfx-asset` on the
  element to pin it. Do NOT add a new cue to the global catalog.
- **User asks for a per-video tweak to a cue's pool or defaults** → use
  `sfx-overrides.yml` at the video folder root (see `tools/sfx-plan/README.md`).

## Skill's checklist when invoked

When this skill is invoked, use `TaskCreate` to add these items and execute
them in order:

1. Verify visuals are settled (no placeholders; preview is clean).
2. Load all inputs; verify `sfx-catalog.yml` version matches.
3. Walk HTML + transcript + narration-map. Identify candidate moments.
4. Apply placement principles. Pick cue character from the library.
5. Apply technical floors (cooldowns, density ceiling).
6. Produce the proposal in the exact format above.
7. **WAIT for user approval. Hard gate.**
8. If new anchors needed: extend `anchors.txt`, re-run `tools/narration-map`.
9. Write `data-sfx-*` attributes via `Edit` (one element at a time).
10. Run `tools/sfx-plan --report`.
11. Run `npx hyperframes preview` and surface the URL.
12. Wait for audit feedback; loop step 9 onward on refines.

## Reference documents

Read these before producing your first proposal in a fresh session — they
encode the taste this skill is built on:

- `reference/cue-vocabulary.md` — per-cue: when it earns a hit, when it doesn't.
- `reference/worked-examples.md` — concrete annotated walkthroughs from
  `videos/why-text-is-hard-2026-05-07/`. The "this is what good looks like"
  reference.
- `reference/anchor-discipline.md` — how to pick an anchor word, when to extend
  `anchors.txt`, edge cases (homonyms, repeated words, anchors that don't appear
  in the transcript).
- `reference/proposal-template.md` — the exact proposal output format with
  annotations.
- `reference/timing-modes.md` — when each timing mode is correct, how to read
  a GSAP timeline to extract a tween's start/duration for a given target,
  perceptual-landing math by motion type, and the scene-01-open
  before/after worked example for anchor + negative lead → at-scene-ms.

## When to invoke this skill

Trigger on any of:

- "add sound design", "score the video", "add SFX", "do the sound pass"
- "add whooshes / ticks / cues to this composition"
- The user signals visuals are done and asks "what's next?" right after a
  `hyperframes preview` cycle. Confirm visuals are locked before starting.

**Do not invoke** if:

- Composition is unfinished (placeholder stubs, only Scene 1 built, etc.).
- The user is asking about music or mastering — those are Phase B/C, out of
  scope for this skill. Surface that politely.
- `sound-effects/sfx-catalog.yml` is missing — point at the catalog tool first.
