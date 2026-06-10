# TODO — deferred work with activation conditions

Each item below was deliberately deferred, not forgotten. Each has a concrete
trigger; when the trigger fires, the instructions are written to be executable
without re-deriving the context. Origin: the 2026-06-09/10 sessions that built
`tools/inspo-ingest pace`, the `pacingInspo/` library, and the combined-ingest
default in `motion-inspo-add`.

---

## 1. Wire `pacingInspo/` into video-director's scene chunking

**Trigger:** `pacingInspo/README.md` has **~10+ entries** spanning at least 3
registers (e.g. diagram explainer, fast video essay, talking-head tutorial,
narrative doc). Count the Quick-index rows.

**Why deferred:** with 2 entries (one slow diagram explainer at 1.94 cuts/min,
one fast essay at 10.5 cuts/min) the library offers only extremes; a consumer
hook would overfit every video toward one of two channels. Chunk pacing is also
mostly decided upstream at script time — `script-writer` already cites the
library (its Step 4 reset-cadence bullet + external-references note) — so the
director hook is a refinement, not a missing limb.

**What to do when it fires:**

1. Edit `.claude/skills/video-director/SKILL.md` **Step B ("Select the next
   chunk")** — this is where chunk boundaries (one to a few sentences, each
   sentence its own visual idea) are chosen. Add a short paragraph: before
   settling chunk size for a *new* video (first chunk only, not per chunk),
   read `pacingInspo/README.md`'s Quick index and the ONE entry whose register
   matches this video's script; let its `median scene` and `longest_hold_s`
   calibrate how many sentences a chunk can carry in this register before it
   drags. Evidence, never a target — the transcript's own sentence boundaries
   still win.
2. Mirror the reading discipline already written in `script-writer/SKILL.md`
   (search for `pacingInspo` there): Quick index + one entry block only; never
   load `<slug>-pace.json` whole (per-scene transcript text floods context).
3. Decide whether the lookup belongs in the director itself or in the
   `scene-design-decider` dispatch (`.claude/agents/scene-design-decider.md`).
   Default answer: the director, once per video, at first-chunk time — the
   decider is per-chunk and per-chunk pacing lookups would be wasteful and
   repetitive. Remember agents' .md files load at session start (project
   memory: subagent-md-loads-at-session-start); skills are live-watched.
4. Update `pacingInspo/CLAUDE.md` "Consumers" section (it currently names this
   wiring as unwired) and the project memory file
   `pacing-inspo-library-and-pace-subcommand.md`.

## 2. Distill `pacingInspo/` aggregates into `docs/creator-patterns.md` §3

**Trigger:** same threshold as item 1 (~10+ entries, ≥3 registers). Do item 1
and this together.

**Why deferred:** §3 carries the ~45–60s reset-cadence band synthesized from
237 transcripts; adding "measured" numbers from 2 videos would dress noise as
evidence next to a much larger corpus.

**What to do when it fires:**

1. Compute cross-video stats from the manifests (filter, don't load whole):
   `python3 -c` over `pacingInspo/*-pace.json` pulling each `aggregates` block
   — cuts/min, scene_duration_s median/p75, longest_hold_s, pct_cuts_in_pause,
   pct_sentence_aligned — grouped by register (assign registers by hand from
   the Quick-index pacing one-liners).
2. Add a short measured-bands subsection to `docs/creator-patterns.md` §3:
   per-register hold-length bands and cut-on-sentence behavior, each citing
   the contributing slugs as evidence. Keep §3's existing prose intact —
   this is an evidence appendix, not a rewrite.
3. Then simplify `script-writer/SKILL.md`'s pacingInspo references to point at
   the distilled §3 bands first, raw library second (the skill currently
   reads the library directly because no distillation exists).
4. Re-check the claim in `pacingInspo/CLAUDE.md` "Consumers" and update.

## 3. Re-validate `pace` detection defaults as the library grows

**Trigger:** rolling — every new ingest's contact-sheet QA is the cheap check;
do a formal pass after **~5 more ingests**, or immediately if any QA shows
systematic over/under-detection that flag-tuning per video keeps fighting.

**Why flagged:** `--hard-floor 0.05` and `--soft-wide-min 0.12` were calibrated
on exactly two videos (2026-06-09). They generalized across those two opposite
registers, but n=2.

**What to do when it fires:**

1. Per-video QA (already documented in `tools/inspo-ingest/README.md` known
   limitations): adjacent near-identical contact-sheet tiles = over-detection;
   an implausibly long scene = under-detection. Re-runs reuse the cached proxy
   (`scratch/pacing/<slug>/proxy.mp4`), so threshold sweeps are fast and
   network-free.
2. For the formal pass, reuse the distribution-dump method: a `python3 -c`
   script importing `inspo_ingest.strip.scene_detect_argv`,
   `inspo_ingest.frames.parse_scene_scores`, and
   `inspo_ingest.cli._compute_scene_features` against each cached proxy;
   print score/wide_delta histograms (counts ≥0.03/0.05/0.08/0.12/0.22 and
   medians) and compare where each video's true cuts sit vs the floors.
3. If defaults change, update all three in lockstep or tests fail:
   `cli.py` `_build_pace_parser` defaults, `tests/test_cli.py`
   `test_pace_parser_defaults_match_plan`, and the `tools/inspo-ingest/README.md`
   options table + calibration note. Then re-run
   `uv run --project tools/inspo-ingest pytest tools/inspo-ingest/tests -q`.
4. Consider per-register flag presets in `motion-inspo-add` Mode C guidance
   only if the same manual overrides keep recurring; do not add presets to the
   tool itself (it stays mechanical).
