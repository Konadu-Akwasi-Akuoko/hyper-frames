# prompt-evaluation — notes

Workspace for evaluating and improving this project's local skills through
human-graded output-quality evals. One subfolder per skill under evaluation.

## How we run these (project-specific overlay on skill-creator)

We borrow skill-creator's *structure* — a frozen fixture, a per-iteration
output snapshot, and human grading — but skip its baseline-subagent benchmark
machinery (built for with-skill-vs-without comparison, overkill for a single
skill graded by a human).

- **Grader:** human (the repo owner). These are taste/judgment skills; an
  assertion can't tell you a cut sounds clean or a script is in voice.
- **Dimension:** output quality (given the skill fires, is the result good) —
  not triggering accuracy.
- **Inner loop:** freeze a fixture once, then re-run only the promptable unit
  (e.g. the `audio-cut-decider` agent) each iteration so the prompt is the
  single variable. Never re-run paid API steps (ElevenLabs Scribe) per
  iteration.
- **Reload trap (learned the hard way):** subagent definitions
  (`.claude/agents/*.md`) load **once at session start and are NOT
  live-watched**. Editing one mid-session and re-dispatching in the *same*
  session silently re-tests the session-start version — your edit is ignored
  until you **restart Claude Code** (or edit via the `/agents` UI). Skills
  (`SKILL.md`) ARE live-watched and can be iterated without restart; `CLAUDE.md`
  needs `/compact` or a restart. So: to iterate on an *agent* prompt you must
  restart between edit and re-run; instructions passed through the *dispatch
  prompt* (the Agent tool's `prompt` arg) are always fresh and need no restart.
  Source: code.claude.com/docs/en/sub-agents.md.
- **Never touch a live `videos/<slug>-<date>/` folder.** Real recordings have
  hand-edited `cuts.json` the skills warn against clobbering. Eval fixtures get
  their own disposable folders.

## Techniques that worked (reuse these)

From the transcribe-and-plan-cuts eval — the playbook for an output-quality eval:

1. **Freeze a fixture + a human answer key.** A mistake-dense slice, rebased to a
   local clock, with the human's real cuts as ground truth. Grade by ear in
   `tools/audio-editor`.
2. **Decision-log probe** to diagnose *why* an agent varies: have it write every
   candidate (kept + acted-on) with a rationale, via the **dispatch prompt**, and
   run **3–5 copies in parallel** (one run hides the variance). Separates
   detection failure from judgment failure. They have different fixes.
3. **Restart before re-running an edited agent `.md`** — or you re-test the
   session-start version (the reload trap above). Skills can be iterated live.
4. **When a prompt can't fix a fine-grained judgment, move it to deterministic
   code** (cut-snap, dup-detect). Find the rule by **labeling all candidates
   against the answer key** and picking a *principled* separating feature, not a
   hand-tuned threshold. Frame the tool as recall insurance: it should add
   nothing on an easy run.

## Skills under evaluation

- [transcribe-and-plan-cuts](transcribe-and-plan-cuts-eval/) — improving cut
  quality. Status: **shipped — two deterministic tools wired into the skill.**
  Two findings, same shape: judgment the agent can't do reliably from text was
  moved into code. (1) **Boundary precision** → `tools/cut-snap` (waveform DSP),
  skill Step 6. (2) **Duplicate-take recall** → `tools/dup-detect`, skill Step 5:
  a decision-log probe showed the agent *detects* repeats 100% reliably but its
  *classification* (rhetorical vs re-take) and *which-take* call vary run to run;
  dup-detect replaces both with a hard rule (identical text = re-take) + a
  measurable signal (delivery slack → keep the tighter, default later take).
  Matches the human 5/5 on the fixture, deterministically. The agent's own
  duplicate policy was also flipped to "keep the last take" as a backstop (takes
  effect next restart — reload trap). Pipeline: agent → dup-detect → cut-snap →
  editor. Largely done; remaining is optional (a graded post-restart test of the
  agent's keep-last policy, low value since dup-detect owns recall).

- [video-director](video-director-eval/) — improving the incremental
  composition-authoring loop. Status: **iteration 2 graded (Opus done, human
  pending) — the overhaul worked: 5 of 6 findings landed.** Re-authored greenfield
  in a clean, bias-controlled session against the overhauled skill (see
  `video-director-eval/iteration-2/grading.md`). The iteration-1 "flat slideshow" is
  gone: subject-toned background (no logo), three distinct archetypes (card /
  split-contrast / kinetic type), real motion + scene-02 reflow, and the 2→3 seam
  collision fixed via a scrim cover (verified at the exact 21.4s frame that collided
  before). **Holdout = imagery (#3 + scene-01 reaction #6b):** the director
  *considered and declined* asset boxes, judging all three opening beats text-driven.
  **Iteration-3 tuning done (skill only, not yet re-authored):** a `/workflows` design
  panel (run `wf_79999e15-891`, 9 agents, anti-overfit-weighted judges) produced five
  generalizing edits, applied by hand — Step D flipped from a neutral "want imagery?"
  question to a **signal-list default** (named emotion / irony-comedy-punchline / human
  reaction / named who / concrete recognisable thing → reach for an asset box); a
  "let the image carry — no dim, no divider" craft rule in `visual-language.md` §2; a
  two-sided "when imagery earns its place" section + video-agnostic ironic-payoff→laughing-
  cutout worked case in `assets-and-media.md`; and a run-level "consecutive bare-text beats"
  flag in `verify-and-preview.md`. Guards: triggers are sentence-content not scene-number,
  text-only stays legitimate, no quota. See `video-director-eval/iteration-3/tuning.md`.
  **Sourcing loop closed (post-tuning):** the box mechanism wasn't the bottleneck — the human
  round-trip to *find* the file was. New **`image-sourcer` agent** (`.claude/agents/`,
  `model: sonnet`, medium-effort) sources the image itself: Chrome-driven, **Pinterest-first**
  (user logged in, no wall) → web-image-search fallback → picks the best emotion-matched shot →
  `curl`s the full-res original → `image-prep` cutout → returns confidence + runner-ups; the
  director swaps on high confidence, shopping-list is now the *fallback*. Mechanism was proven
  live on the real Steve-Harvey-laughing search before the agent was written (verify-then-
  crystallize): logged-in grid extract → `/236x/`→`/originals/` rewrite resolves at full res
  (1080–1484px). Wired into `assets-and-media.md` + the SKILL delegation map. Agent loads at
  session start (reload trap) → live next session = iteration-3 authoring. See
  `video-director-eval/iteration-3/tuning.md` "Closing the sourcing loop".
  **Referent imagery added (second category, multi-source):** reaction shots are only one kind —
  when the script *names a recognisable thing* (JavaScript, infrastructure, a company), show the
  thing. Routed by a new `data-asset-class`: `logo`/`glyph` → **Iconify** (static SVG, local
  `assets/icons/` checked first), `photo` → **Wikimedia Commons** (licensed, attribution captured),
  `reaction` → Pinterest, web catch-all. Gated by a 3-part AND threshold (is-the-subject +
  recognisable-on-sight + adds-meaning-words-can't) so it's not logo-on-every-noun. Hard rules:
  determinism (author-time static fetch, never a runtime `<iconify-icon>`/CDN), license capture,
  **box-on-failure — director never deletes a box on a failed source**. Mechanisms proven live
  (Iconify `logos/javascript.svg`; Wikimedia data-center search → CC BY-SA) before designing.
  Produced via a `/workflows` design panel (`wf_90c299e8-1d1`) whose *return* failed twice (network,
  then a too-heavy synth schema) — recovered the 8 successful design+judge `StructuredOutput`
  payloads from the agent transcripts and **synthesized by hand** (all candidates anti-overfit 5 /
  technical 5, convergent). Edits across `image-sourcer.md` (route-by-class + referent lane),
  `visual-language.md` §2, `assets-and-media.md` (routing table), `SKILL.md`, `verify-and-preview.md`
  (overfit-inverse + determinism checks). See `iteration-3/tuning.md` "Referent imagery".
  **Iteration 3 RE-AUTHORED + GRADED (Opus pass via `/workflows` grader `wf_7a11fd45-ff4`;
  human pending).** Sentences 1-5, greenfield, against the imagery-pushed skill (session
  `faf29741`). Result: **the imagery push FAILED — zero images rendered.** Grades: mechanics
  **A** (lint/inspect clean, both seams resolved, Sonnet 13/14), visual-design **B** (three
  distinct archetypes + real reflow/kinetic motion held all of iteration 2's wins; docked for
  the Excalifont type-role miss), imagery **D** (2 of 5 gate-passing referents declined; HN
  logo hand-built in CSS not sourced; "infrastructure" rendered as a bare yellow word; the
  textbook data-center→Wikimedia case missed; `image-sourcer` **never dispatched**). **Failure
  class = JUDGMENT, not detection or mechanism:** the author *saw* the signals (named the irony
  + the HN source in its own thinking) and consciously routed them to typographic lighting —
  "the quote itself is the design, no side imagery needed." Root cause: **Step D has two halves
  (archetype-variety + imagery-as-default) and the variety half can fully satisfy it, so the
  imagery check is silently skippable.** The human's "frame is off" = type-role miss (verbatim
  HN quote set in Inter, not the reserved Excalifont) + the fake CSS YC logo — NOT composition.
  **Iteration-4 hardening VALIDATED (the lever).** Don't shout signals — raise the cost of
  *declining*. Step D now requires an **auditable per-chunk verdict block** (imagery + type-role,
  quoted back like the Step B chunk quote); declining must **name the candidate it rejected**, so a
  silent "just typographic" is no longer reachable; text-only stays first-class as a *named*
  rejection, never a quota. Bundled the verbatim-quote→human-voice-font (Excalifont) check into the
  same verdict + a NEW **Type-role fidelity** bullet in the verify rubric (the gap that let the
  Excalifont miss through) + a Step G verdict-emitted checkpoint. Taught by **multi-shot worked
  examples** — NEW `reference/decision-examples.md`, two sets ×6, all **video-agnostic** (zero
  js-king), each a reasoning-trace→verdict; built via dynamic `/workflows` run `wf_1c5cd93f-f1f`
  (25 agents: 12 slots drafted + adversarially vetted for correctness/anti-overfit/decline-names-a-
  candidate/format, then synthesized; plain-text return, edits applied by hand). Working halves
  untouched (signal list, 3-part gate, archetype variety, `image-sourcer.md`). **Iteration-4 result
  (session `cf5af7a3`, human-passed on sight, no Opus grade run):** the lever bit — all 3 verdicts
  emitted before authoring; Scene 01 HN logo **sourced** via `image-sourcer` → static SVG, verbatim
  quote in **Excalifont** (both iter-3 D-grade defects reversed); Scenes 02/03 stayed `text-only`
  as *named* rejections (no silent skip, no face-on-every-noun overfit). Caveat: only the **logo**
  referent + type-role fix were exercised on real output — sentences 1–5 had no concrete-subject
  beat, so `class=photo` (Wikimedia) and `class=reaction` (Pinterest) routing stay **bank-only,
  unproven in practice**. Full write-up: `iteration-4/learnings.md`. See also
  `iteration-3/grading.md` + `iteration-3/tuning.md` "iteration-4 hardening".
  (Prior: iteration 1 graded human+Opus, six findings → skill overhauled +
  `tools/image-prep`; see `iteration-1/grading.md`.) Methodology variant: no frozen
  slice and no disposable fixture — the eval **dogfoods on a reset
  `javascript-the-king`** (backed up as `js-king-pre-director`, stripped to
  voiceover-only; author the opening sentences with the skill, tune the
  *live-watched skill prompt* until human+Opus judge the batch good, then scale).
  Promptable unit = the skill itself. Three grade layers: planning decisions
  (decision-probe + eyeball), structural correctness (deterministic → the
  `comp-check` tool to be crystallized, à la cut-snap/dup-detect), and rendered
  visual quality (human + Opus on `snapshot` PNGs — the skill's runtime loop uses
  a cheaper Sonnet reviewer, the eval uses the stronger judges).
  **Iteration-1 outcome:** mechanics were strong but the visual design was a flat
  slideshow — six findings (generic background, every-scene-the-same, no real
  imagery, flat motion, a broken scene-seam transition, concrete scene fixes). All
  six were moved into the skill as *generalizing* changes plus a new tool, not
  patched per-scene: NEW `reference/visual-language.md` (subject-tone background,
  per-scene archetype variety, motion language) + `reference/assets-and-media.md`
  (real images/video via labeled boxes the user fills) + `tools/image-prep`
  (rembg BG-removal + grain/duotone/halftone/vintage presets), and edits to
  `composition-structure.md` / `verify-and-preview.md` / `SKILL.md` (seam-collision
  transition fix + extended visual-QA rubric). Reference study of the cited creator
  lives in `video-director-eval/reference-study/`. Scope this iteration was
  skill+tooling only; iteration 2 re-authors the scenes against the updated skill
  and re-grades.

## Disposable editor fixture

`videos/tapc-eval/` is a throwaway video folder that exists only so the
`tools/audio-editor` web app (which resolves slugs under `videos/`) can load
the 90s eval clip + fixture transcript + the current iteration's `cuts.json`
for grading by ear. It is not a real video. Safe to delete when the eval is
done. Open it at `http://localhost:5173/#/edit/tapc-eval`.
