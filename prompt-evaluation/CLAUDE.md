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

## Disposable editor fixture

`videos/tapc-eval/` is a throwaway video folder that exists only so the
`tools/audio-editor` web app (which resolves slugs under `videos/`) can load
the 90s eval clip + fixture transcript + the current iteration's `cuts.json`
for grading by ear. It is not a real video. Safe to delete when the eval is
done. Open it at `http://localhost:5173/#/edit/tapc-eval`.
