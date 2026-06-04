# iteration-5 — the folded-in SFX pass (Step H + final reconcile)

New graded **dimension**, not a re-author of the visual loop: this iteration
evaluates the SFX scoring that was folded into `video-director` as **Step H**
(per-scene, right after each scene's visual QA) plus the **final whole-video
reconcile**, replacing the removed standalone `sfx-author` skill.

## What changed in the skill (the thing under test)

- `SKILL.md` — new **Step H. Score the SFX for this pass** between the visual-QA
  loop (G) and loop/stop (renamed I); Done condition now runs the final SFX
  reconcile before handing off to `audio-bed-music`; frontmatter, delegation map,
  Step E, and reference list rewired.
- New reference files: `reference/sfx-cues-and-timing.md`,
  `reference/sfx-arc-and-reconcile.md` (the folded-in sfx-author taste, generalized).
- New tool `tools/sfx-level` (VO-amplitude probe, reuses cut-snap's RMS DSP).
- `tools/sfx-plan` mount-duration fix (`ensure_mount` upserts the full runtime).
- `sound-effects/sfx-catalog.yml` — every cue `default_volume: 0.5` (flat
  project volume + ceiling; duck-below-only via `data-sfx-level`).

## Fixture

`videos/javascript-the-king-programming-languages-2026-05-15/` — the standing
`video-director-eval` fixture (greenfield: `script.md` + `transcript.json` +
`design.md`, **0 scenes authored**). The SFX step needs finished visuals to
score, so this iteration authors the opening batch first, then scores it.

> Live-folder caveat: unlike the visual-only iterations, scoring SFX mutates the
> fixture (writes `data-sfx-*`, `compositions/sfx.html`, mounts the sfx-layer).
> That's accepted — the user opted to use js-king as the fixture and grade the
> result with Opus. The pre-director backup tag still exists for recovery.

## Run plan (live, human + Opus)

1. **Author scenes (visual loop, Steps A–G)** on the opening ~3–5 sentences with
   `video-director`. Stop on a clean boundary once the scenes pass visual QA.
2. **Score SFX (Step H)** on those scenes:
   - punctuation cues from each scene's GSAP beats (`at-scene-ms`, perceptual
     landing), spoken-word cues (`anchor`), heavy cues only if the arc earns one;
   - `tools/sfx-level audio/voiceover.mp3 --at <t>` at each cue → confirm gap vs.
     active + set any duck below 0.5;
   - compact proposal → approve → `tools/sfx-plan --report`.
3. **Grade (human + Opus)** — capture `npx hyperframes snapshot --at <beats>` for
   the visuals and the `sfx-level --batch compositions/sfx.html` report for the
   sound, and judge on taste, not an answer key:
   - did Step H find the earned appears/slide/highlight/snap moments?
   - sane cue characters; heavy cues rationed (no boom on a body beat)?
   - volumes sit right under the VO (0.5 default; ducks only where VO is hot)?
   - **listen** in preview — does each cue land on the beat (not early/late)?
   - record the verdict in `grading.md`.

## Deterministic checks (no answer key needed — run every iteration)

- `tools/sfx-plan --dry-run` on the produced annotations: clean — no
  `DensityViolationError`, no `large lead_ms` warning, no track overlaps.
- Each `at-scene-ms` within ε of its tween's computed perceptual landing.
- The `sfx-layer` mount `data-duration` == full voiceover runtime (530.617).
- Contract audit (run this build via the `sfx-skill-contract-audit` workflow): no
  invented `data-sfx-*` attribute, no wrong cue name. It *did* catch density/cooldown
  inaccuracies inherited from the old sfx-author docs (the tool uses a 6s window —
  warns >0.5/s, raises >1.0/s — and enforces no same-cue cooldown, only per-track
  overlap); the three SFX docs were corrected to state enforced-vs-editorial
  precisely. Re-verify against `tools/sfx-plan/src/sfx_plan/validate.py` if edited.

## Notes

- The skill (`SKILL.md` + `reference/`) is **live-watched** — iterate the prompt
  and re-run on the same scenes without restarting Claude Code.
- SFX correctness is partly **ear-only**; the deterministic tools are the
  backstop, the human listen-in-preview audit stays the gate.
