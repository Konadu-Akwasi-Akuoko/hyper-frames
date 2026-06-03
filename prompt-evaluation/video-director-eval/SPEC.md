# video-director eval — SPEC

Status: **spec only — not yet run.** Build/run this once the `video-director`
skill is stable. This documents the methodology so a later session can execute it
end-to-end.

## Why this eval differs from transcribe-and-plan-cuts

TAPC graded a near-deterministic output (cut timestamps vs. an answer key) by
freezing a 90s slice. Video "quality" is visual and subjective, and the skill's
whole value is the *incremental authoring loop*, not a single output. So instead
of a frozen slice with a pre-authored "good bar", this eval **dogfoods on the
real `javascript-the-king` video**: reset it to blank, author the opening batch
with the skill, tune the skill prompt until the batch is genuinely good, then run
the dialed-in skill across the whole video (which also produces the finished
video).

What carries over from the TAPC playbook: the **promptable unit is live-watched**
(here it's the skill itself), the **decision-log probe** for diagnosing variance,
and **moving un-promptable judgment into deterministic code** (here, `comp-check`).

## The loop

### 1. Back up, then reset js-king to blank

The current `javascript-the-king-programming-languages-2026-05-15/` has 12
authored scene blocks. This eval overwrites them, so preserve first:

```bash
# named backup (git history also has it, but a branch/tag is safer)
git branch js-king-pre-director            # or: git tag js-king-pre-director
# optional belt-and-suspenders copy of the compositions
cp -r videos/javascript-the-king-programming-languages-2026-05-15/compositions \
      /tmp/js-king-compositions-backup
```

Then strip the video to **voiceover only**:

- `index.html` → reset to the scaffold: `#root` + the `<audio>` voiceover (+
  optional `substrate-layer`), **zero scene hosts**, the `window.__timelines["main"]`
  stub, and the `sfx-layer`/`music-layer` mounts removed (sound reruns later).
- `compositions/` → archive the old `scene-*.html` blocks out (move to the /tmp
  backup); keep `substrate.html` if you keep the substrate layer.
- **Keep** `script.md`, `transcript.json`, `design.md`, `audio/voiceover.mp3`.

This cleared folder is the fixture. It's "frozen" by *not editing*
script/transcript/voiceover between iterations — only the skill changes.

### 2. Run the skill on the first 3–5 sentences only

Invoke `video-director` on the folder. It authors that opening batch (a few
sentence-level blocks) end-to-end, including its Step-G visual-QA loop. Stop it
after the batch (a small explicit cap for the eval, e.g. "author through the
first ~5 sentences then stop").

### 3. Grade the batch — human + Opus

This is the ground-truth bar (layer c below). Capture frames with
`npx hyperframes snapshot --at <beats>` and judge the PNGs with a **human plus
Opus** against `design.md` and the human's taste. Be honest: is this genuinely
good — legible, on-design, emphasis anchored to the right word, motion varied,
reads as a diagram not a slide? Record verdicts in `iteration-N/grading.md`.

**The `js-king-pre-director` backup is NOT the bar.** It is a recovery backup of
the prior cut, not a design reference and not a target to reproduce — the fresh
compositions authored here *are* the new grading bar. Reproducing the backup
makes the eval circular (it would measure transcription, not generation), so the
skill must design original work; the verify loop reads old blocks only for the
code skeleton, never their visual design.

> Note: the skill's *runtime* Step-G loop uses a **Sonnet** reviewer to stay
> cheap. The eval deliberately uses the stronger **human + Opus** judges — so it
> also measures whether the cheaper Sonnet loop's output holds up to the higher
> bar. If Opus/human routinely catch things Sonnet passed, that's a signal to
> strengthen the rubric in `reference/verify-and-preview.md`.

### 4. Iterate the skill prompt

`SKILL.md` + `reference/` are live-watched — edit, no restart. Reset just the
batch's blocks, re-run step 2 on the **same** 3–5 sentences, re-grade. Repeat
until the batch is reliably good across a couple of runs. Generalize from the
failures (don't overfit to these five sentences) — the prompt has to work on the
whole video and the next video.

### 5. Scale

Once the opening batch is dialed in, let the skill run across the **whole**
js-king video, batch by batch — which produces the finished video. Spot-grade
later batches; fold any new failure mode back into the prompt (or into
`comp-check` / the block templates).

## What "good" is graded on

No formal answer key — judgment plus deterministic checks.

- **(a) Planning decisions** — eyeballed against `script.md` during grading: did
  it chunk sensibly (3–5-sentence cohesion), pick a fitting primitive, anchor to
  real transcript words (no round numbers)? Make these auditable with the
  **decision-log probe** when a batch varies run-to-run: dispatch a *separate*
  subagent (via the dispatch prompt, no reload trap) to emit every
  chunk-boundary / primitive / anchor choice + rationale, run 3–5 in parallel,
  and separate segmentation failure from design-choice failure.
- **(b) Structural correctness** — deterministic, via `comp-check` (below):
  `lint` pass; `inspect --at <beats> --json` pass (no overflow/clipping/small-text
  at the beats); timing continuity (scene hosts tile the transcript span, overlaps
  only at the 0.5s seams); reusability (recurring didactic primitives are
  parametrized blocks, not inline copies); every animated beat within ε of a real
  transcript word; no editorial chrome; no exit anim except the final scene +
  entrance/transition present on each.
- **(c) Rendered visual quality** — human + Opus on the `snapshot --at` PNGs
  (rubric reused from `reference/verify-and-preview.md`), judged against
  `design.md`. The gate. The fresh compositions are themselves the new grading
  bar — do **not** grade by similarity to the `js-king-pre-director` backup, and
  do not let the skill reproduce it.

## comp-check — the deterministic tool to crystallize

When a structural failure recurs and can't be fixed by prompt wording, move it
into code — exactly how TAPC produced `cut-snap` / `dup-detect`. Build
`tools/comp-check/` (a uv project, mirroring `tools/cut-snap`) or a workspace
`check_structure.py`, in priority order:

1. **anchor-check** (highest value — enforces transcript-as-timing-truth): parse
   each block's GSAP timeline positions, assert each animated beat lands within ε
   of a real transcript word `start`/`end`, not a round number.
2. **coverage/gap-check**: sort scene hosts by `data-start`, assert they tile the
   transcript span with overlaps only at the ≤0.5s seams and no hole > threshold.
3. **chrome-lint**: pattern-scan blocks for corner strips / scene labels /
   timecodes / footer rules. Zero variance.
4. **reusability-check**: flag an inline didactic primitive that should be a
   parametrized local block.

comp-check wraps `npx hyperframes lint`/`inspect --json` (which already catch
overlap/contrast/overflow/missing-assets) and adds the project-specific
invariants the CLI doesn't know about. Frame each check as recall insurance — it
adds nothing on a clean pass.

## Directory layout (when built)

```
prompt-evaluation/video-director-eval/
  SPEC.md                 # this file
  iteration-1/            # snapshot frames + grading.md (human+Opus)
  iteration-2/
  ...
  decision-probe/         # optional: the dispatch-prompt the probe subagent uses
  check_structure.py      # → promote to tools/comp-check/ when it stabilizes
```

No `build_fixture.py` and no `videos/vd-eval/` — the fixture is the reset
js-king folder itself, not a disposable slice.
