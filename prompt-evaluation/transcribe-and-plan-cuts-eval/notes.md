# transcribe-and-plan-cuts — eval notes

## What's being tuned

The promptable unit is the **`audio-cut-decider` sub-agent**
(`.claude/agents/audio-cut-decider.md`) — specifically its cut policy and the
boundary/precision rules. The skill's transcription step is a deterministic
ElevenLabs call and is not in scope.

## Fixture

- **Source recording:** `videos/javascript-the-king-programming-languages-2026-05-15`
- **Window:** 2:30–4:00 of `raw.mp3` (global 150s–240s), chosen as the most
  mistake-dense stretch: 2 false starts, 2 duplicate takes, 1 stutter, plus two
  anaphora "traps" that must be KEPT.
- **Rebased to local [0, 90].** Built by `build_fixture.py` (re-runnable).
  - `videos/tapc-eval/transcript.raw.json` — frozen fixture (agent input + editor).
  - `videos/tapc-eval/audio/raw.mp3` — 90s clip, re-encoded, exact 1:1 with the fixture clock.
  - `transcript.clip.json` — snapshot of the fixture (eval record).
- **Answer key:** `reference-cuts.json` — the human's real cuts inside the
  window (from the finalized `cuts.json`), rebased. 5 cuts.

## Iterations

### iteration-1 — baseline (current agent, unedited)

- 5 cuts, 15.95s removable. Invariants pass.
- **Found all 5 real mistakes; zero false positives on the anaphora traps.**
- **Boundary precision** runs slightly late vs. the answer key (dup-take "And he
  chose JS" starts +1.9s late).
- **Token alignment:** 3 of 5 `end` boundaries (cut_0001/0002/0005) land on a
  word *start* / inside a pre-restart silence, not on a token *end* — violates
  the literal invariant #5, though splice-safe in practice (cut ends at the
  next word's onset, so nothing is chopped).
- Awaiting human grading in `iteration-1/grading.md`.

#### Root-cause finding (cut_0001, human-graded)

The human's ideal boundaries land **inside silence valleys** (14.743 / 18.854),
which are **sub-token** — no transcript token starts/ends there. Invariant #5
("every boundary must equal a token start/end") structurally forbids the agent
from placing them, and it self-contradicts the padding rule (`:138-141`): in a
gap with no interior tokens, "round to the nearest token boundary" discards the
~0.3s breath the same rule asks for.

The true safety requirement is **"don't land inside a `word` token"** — inside
silence, any timestamp is splice-safe. Why valleys matter: a word's energy ramps
up *before* its labeled `start` and decays *after* its `end`, so cutting on a
labeled edge either clips a kept word's onset (end side) or leaves a mistake's
rising onset in the kept audio (start side).

**iteration-2 hypotheses:**
- **A (cheap, transcript-only):** relax invariant #5 to "not inside a `word`
  token"; place `cut.start = prev_word.end + ~0.3s`, `cut.end = next_word.start
  − ~0.3s` inside the silence. Predicts ~14.68 / ~18.92 (≈60ms off the human).
- **B (heavier):** add an RMS/silence probe of `raw.mp3` so boundaries snap to
  the true amplitude minimum instead of guessing the pad region is silent.

### iteration-2 — prompt edit (capped-pad rule + relaxed invariant #5)

Edited `audio-cut-decider.md`: rewrote the boundary section to the silence-valley
capped-pad rule with worked examples, relaxed invariant #5 to "not inside a word
token." Re-ran the agent (hypothesis A).

**Result: the prompt edit did not work.**
- **8/8 boundaries still on word edges** — placement byte-identical to baseline
  on 3 of 4 cuts. The agent ignored the capped-pad rule even though a worked
  example handed it the exact answer (`14.68`) for this fixture's cut_0001.
- **Recall regressed:** dropped the "And he chose JavaScript" duplicate
  (39.68–42.62). Policy for duplicates was untouched → looks like run variance,
  but shows recall isn't stable across runs.

**Conclusion:** an LLM won't reliably do per-boundary timestamp arithmetic from a
prompt instruction. Boundary placement is deterministic math on the transcript
and belongs in code, not the agent's head.

### iteration-2b — deterministic snapper (works)

`snap_boundaries.py` applies the capped-pad rule to the agent's spans.
Run on iteration-2's cuts → `iteration-2/cuts.snapped.json`:

| cut | agent | snapped | human |
|-----|-------|---------|-------|
| cut_0001 | 15.000–19.220 | 14.680–18.920 | 14.743–18.854 (±66ms) |
| cut_0002 | 27.049–29.720 | 26.794–29.420 | — |
| cut_0003 | 65.320–67.080 | 65.250–67.075 | — (0.01s gap, barely moves) |
| cut_0004 | 69.580–73.800 | 68.950–73.500 | — |

Deterministic, instant, matches the human ear. Snapped cuts loaded into the
editor (`videos/tapc-eval/cuts.json`) for ear-confirmation.

**Open design decisions for the pipeline:**
1. Wire the snapper in as a post-agent step in the skill (agent → snap → write
   cuts.json), and **revert the failed prompt edit** to `audio-cut-decider.md`
   (it had no effect and embeds this fixture's numbers — train/test leakage).
2. Recall variance (dropped duplicate) is a separate, unaddressed axis.
3. cut_0003's 0.01s gap can't be solved transcript-only → option B (waveform).

### iteration-2c — option B: tools/cut-snap (RMS plateau edge + breath pad)

Built `tools/cut-snap` (uv tool, numpy + ffmpeg, deterministic). Per boundary:
decode raw.mp3 → RMS envelope across the inter-word gap → adaptive threshold
(`floor + 8dB`) → find the plateau edge (true acoustic word edge) → apply the
capped-pad breath offset FROM that edge → zero-crossing snap. Falls back to the
transcript-label capped-pad when no silence floor exists.

**Design correction during build:** first version placed the boundary AT the
plateau edge → removed the entire pause (zero lead-in). Fixed: the plateau edge
is the *anchor*, capped-pad then leaves the ~0.3s breath. The acoustic edge is
more accurate than the transcript label, so cut-snap beats transcript-only
capped-pad.

Run on iteration-2's cuts → `iteration-2/cuts.cutsnap.json`:

| cut | agent | capped-pad | cut-snap | human |
|-----|-------|-----------|----------|-------|
| cut_0001 | 15.000–19.220 | 14.680–18.920 | 14.725–18.895 | 14.743–18.854 |
| cut_0002 | 27.049–29.720 | 26.794–29.420 | 26.834–29.355 | — |
| cut_0003 | 65.320–67.080 | 65.250–67.075 | 65.253–67.074 | — (0.01s gap, no-op) |
| cut_0004 | 69.580–73.800 | 68.950–73.500 | 69.035–73.435 | — |

cut_0001 within 18ms/41ms of the human ear. Loaded into the editor for
ear-confirmation. **Not yet wired into the skill** (per scope decision —
awaiting ear verdict). [Later wired into the skill as Step 5.]

## iteration-3 — recall-variance diagnosis via a decision log

**New eval instrument:** dispatched the agent with an extra (eval-only)
instruction to write `decisions.json` — every candidate it identified, KEEP and
CUT, with a one-line rationale. The point: `cuts.json` only shows survivors, so
it can't tell "never noticed" from "noticed and rejected." The decision log can.

**3 parallel runs** (`iteration-3/run-1..3`) to surface the variance:

| run | cuts | caught the "And he chose JavaScript" duplicate? |
|-----|------|--------------------------------------------------|
| run-1 | 8 | NO — decision log: `keep`, "rhetorical doubling, the punchline reveal" |
| run-2 | 4 | NO — decision log: `keep`, "sentence-spanning rhetorical repetition" |
| run-3 | 8 | YES — `cut`, but cut the **second** take (kept first) |

**Diagnosis (the decision log earned its keep):**
1. **Detection is 100% reliable.** All 3 runs *noticed* the repeat. The
   "forgetting" was an illusion — not a scan failure.
2. **The variance is category classification** — "rhetorical doubling" vs
   "re-take." That's the false-negative driver.
3. **Even the catch cut the wrong take.** Policy default "cut the second, keep
   the cleanest first" is backwards here: take 1 has a 0.40s mid-phrase
   hesitation (`chose`→`JavaScript`), take 2 is tight (0.10s). Human kept take 2
   (`ref_0003` = cut 37.755–41.108 = remove take 1 + pause). Text-only the agent
   can't tell which take is cleaner — but the **intra-phrase timing gap** can.

## iteration-4 — prompt fix for the duplicate policy (FAILED, same as iter-2)

Edited `audio-cut-decider.md`: (a) textually-identical close repeats are ALWAYS
proposed + flagged `duplicate_or_rhetorical`, never silently kept; (b) flip the
default to cut the **earlier** take, keep the **last**. Re-ran 3x.

| run | cuts | duplicate handling |
|-----|------|--------------------|
| run-1 | 5 | `cut` — but kept take 1, citing "policy says keep the first" (OLD policy) |
| run-2 | 4 | `keep` both — "rhetorical repetition" |
| run-3 | 4 | `keep` both — "rhetorical repetition" |

**Recall on the duplicate: 1/3.** 2/3 kept both; the one cut kept take 1 (citing
the OLD "keep the first" policy).

**!! CONFOUND — iteration-4 did NOT test the fix. !!** Subagent definitions
(`.claude/agents/*.md`) are loaded **once at session start and are NOT
live-watched** — mid-session edits do not apply until a restart (or editing via
the `/agents` UI). Confirmed against the official docs
(code.claude.com/docs/en/sub-agents.md). So all 3 iteration-4 agents ran the
**session-start (baseline) policy**, not the edited one. run-1 cutting take 1
"citing the old policy" is exactly that — it *was* the old policy. The earlier
"prompt edits can't fix judgment" conclusion is therefore **unproven**: the edit
never loaded. (The decision-log instruction worked only because it rode in the
dispatch *prompt*, which is always fresh.)

Reload behaviour (docs):

| file | live-reloaded mid-session? | apply an edit by |
|------|----------------------------|------------------|
| `.claude/agents/*.md` (subagents) | **No** | restart (or `/agents` UI) |
| `.claude/skills/SKILL.md` (skills) | **Yes** (watched) | automatic |
| `CLAUDE.md` (all scopes) | No | `/compact` or restart |

**Eval-methodology rule going forward:** to iterate on a subagent `.md`, you must
restart Claude Code (or use `/agents`) between edit and re-dispatch — otherwise
you re-test the session-start version. Skills can be iterated live.

The iteration-4 `.md` edits were reverted (dead this session; fixture-leakage
example removed). The baseline duplicate policy ("cut the second, keep the
first") is itself wrong per the answer key (human kept the *last* take 5/5) — a
real fix worth testing properly after a restart, separate from dup-detect.

### iteration-4b — tools/dup-detect (deterministic, works 5/5)

Built `tools/dup-detect` (uv tool, pure stdlib — no numpy, no ffmpeg). Per the
transcript: normalize words → find non-overlapping identical word-runs
(>= `--min-words`, default 3) whose two takes start within `--window`s
(default 30) → keep the take with less internal timing **slack** (sum of
inter-word gaps), defaulting to the **later** take unless the earlier is tighter
by > `--slack-margin` (default 0.15s) → bracket the cut to absorb the inter-take
pause → flag `duplicate_or_rhetorical`. cut-snap refines the edges afterwards.

Run on the fixture: **all 5 duplicates detected, all 5 keep-last — matches the
human answer key 5/5 on both detection and direction**, deterministically.

| ref | human cut | dup-detect (pre cut-snap) | keep | match |
|-----|-----------|---------------------------|------|-------|
| ref_0001 | 14.849–19.007 | 15.000–19.220 | last | ✓ |
| ref_0002 | 26.951–29.476 | 27.049–29.720 | last | ✓ (margin fixed a 20ms near-tie) |
| ref_0003 | 37.755–41.108 | 38.100–41.140 | last | ✓ (the JS dup the agent drops) |
| ref_0004 | 64.408–66.309 | 64.740–66.520 | last | ✓ (margin fixed a 10ms near-tie) |
| ref_0005 | 69.010–73.557 | 69.580–73.800 | last | ✓ |

**Design note — the slack margin.** First pass (keep the strictly-tighter take)
got direction right 3/5; ref_0002 and ref_0004 flipped to keep-first on a
10–20ms slack difference. The human kept the *later* take all 5 times — the
structural reason being that take B is the *completed* sentence and take A the
abandoned fragment. Added a margin so a near-tie can't flip the default. Now 5/5.

**End-to-end demo** (`iteration-4/dup-merge-demo*.json`): merged dup-detect into
iteration-3 run-2 (the run that dropped the JS dup). It skipped the 4 cuts the
agent already had and **added exactly the 1 it missed** → 5 cuts; cut-snap then
refined cut_0003 to 37.862–40.835 (vs human 37.755–41.108). The recall fix is
now independent of agent run variance.

**Open:**
1. Wire dup-detect into the skill, between the agent and cut-snap
   (agent → dup-detect merge → cut-snap → editor).
2. Optionally, after a restart, *properly* test fixing the agent's own duplicate
   policy ("keep the last take") — iteration-4 never did. Lower priority since
   dup-detect now owns identical-repeat recall regardless.
3. dup-detect only catches *textually-identical* repeats. Non-verbatim re-takes
   (different words, e.g. the stutter take "had to b-bolt it on" vs "had to bolt
   it on") still rely on the agent. Division of labour is intentional.

## iteration-5 — full-scale test (real 601s recording) + the re-take filter

Built `videos/tapc-fulltest-2026-06-02/` (full raw.mp3 601s + raw-timeline
transcript 1268 words + the human's 19-cut `reference-cuts.json` as answer key).
The user ran the wired pipeline in a fresh session (so the restart loaded the
"keep last" agent policy) and ear-graded in the editor.

**Headline: on the full run the agent's recall was perfect** — it caught all 13
real identical-repeat duplicates itself. So every cut dup-detect *added* was a
false positive. Two failure modes surfaced:

**(a) Coincidental cross-sentence match (the reported bug).** dup-detect matched
the 3-word run "the browser. And" across two unrelated sentences **21 words / 9s
apart** ("JavaScript had escaped *the browser. And* there's the line..." vs "to
escape *the browser and* infiltrate"), and the keep-last span `[A.start, B.start]`
deleted the whole Hacker News quote between them. A 3-word function-word run is
never a re-take when the occurrences are paragraphs apart.

**(b) Anadiplosis / anaphora.** "...becomes *the most generated. The most
generated* becomes the most shipped..." and "*X is a browser. Y is a browser.*"
— deliberate rhetorical repetition, structurally identical to a re-take at the
timing level (gap≈0, a ~0.5s cadence pause).

**Research (labelled all 16 candidate repeats vs the answer key).** Found a
clean, principled separator:
- **Truncation in take A** is the decisive signal. In speech-repair theory a redo
  leaves a *word fragment* at the interruption point — Scribe marks these with a
  trailing `-`/`--`/`...` ("con...", "sourced--", "re-"). **9/13 real re-takes are
  truncated; 0/3 rhetorical repeats are.**
- **Long verbatim match** (≥5 words) — coincidence/rhetoric rarely spans that many.
- **Restart pause** ≥0.7s — real redos restart after a beat; rhetorical cadence
  pauses are shorter (the anadiplosis pause was 0.52s).

**Fix (replaced the old `pause≥0.4 OR len≥5 OR adjacent≤1` test):**

> re-take ⟺ `truncated(take A)` OR `len ≥ 5` OR `pause_before_B ≥ 0.7s`

Dropped the adjacency signal (it was what admitted the anadiplosis at gap=0).
Verified: **13/13 real kept, 3/3 rhetorical/coincidental rejected** on the full
transcript; small fixture unchanged (5/5). Regenerated `tapc-fulltest/cuts.json`:
15 cuts, quote preserved, anadiplosis preserved, dup-detect added 0 (correct —
the agent already had full recall this run).

**Standing lesson:** dup-detect is *recall insurance* for the runs where the
agent's duplicate recall fails (≈2/3 on the hard fixture). On an easy run it
should — and now does — add nothing rather than noise. Its precision ceiling is
verbatim rhetorical repetition, now handled by the truncation/long/pause test;
the residual risk is a transcript whose fragments aren't marked.
