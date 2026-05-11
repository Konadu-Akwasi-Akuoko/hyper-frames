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
- It does not pick assets directly. Asset filenames are picked by
  `tools/sfx-plan`'s deterministic resolver — you decide *anchors* and *cues*,
  never file paths.
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

## Playbook

You operate from principles, technical floors, a cue character vocabulary, and
worked examples. You **do not** consult a rigid CSS-class-to-cue mapping table.
That kind of pre-decoding is what failed in
`learnings/composition-spec-over-restriction.md` — it strips the editorial leap
that distinguishes a real-looking moment from a generic one.

### Placement principles

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
  ✓ <mm:ss.ms>  anchor="<word>" [idx=<N>]  <cue>  on <element ref>   (<one-line reason>)
  ...

Scene 2 ...

TOTAL: <count> cues  (breakdown by type)
DENSITY: 1 cue / <X.Xs> avg
NEW ANCHORS NEEDED: <list — empty if none>
NOTES:
  • <anything the user should know — e.g. hook moment, design.md tone read>

Approve to write annotations into HTML?  [yes / refine / abort]
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
