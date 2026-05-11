# Composition: spec-over-restriction kills creativity

**Date learned:** 2026-05-10
**Videos involved:**
- `videos/why-text-is-hard-2026-05-07/` — maiden video, came out rich and "alive"
- `videos/how-does-captchas-work-2026-05-10/` — second video, first attempt produced a generic CSS checkbox; second attempt (after resetting to maiden conditions) produced a real-looking reCAPTCHA widget

## The failure mode

The captchas video was first built with a pipeline that *looked* more rigorous than the maiden video's:

- A 141-line `design.md` that pre-specified atmosphere layers, transition formulas, and component recipes
- A `.hyperframes/expanded-prompt.md` that pre-decoded the script into 11 per-beat scene specs (depth layers, animation verbs, transitions per scene)
- 11 pre-scaffolded `compositions/*.html` files, one per beat

The output was demonstrably worse than the maiden video:

- Beat 1 rendered a generic CSS checkbox floating in space, not a real-looking reCAPTCHA widget
- 10 of 11 compositions were left as `[ TO BE BUILT ]` stubs because the session ran out of runway after thinly scaffolding everything
- The expanded-prompt also smuggled in chrome elements (top/bottom hairlines + `VERIFICATION · 1 / 1` corner label) that **directly violated the project CLAUDE.md "No editorial chrome" rule** — even though the expanded-prompt's own negative-prompt section cited that rule

After deleting the expanded-prompt, deleting all 11 stub compositions, and replacing the 141-line `design.md` with the maiden video's 43-line `design.md`, re-running `/hyperframes` produced **miles better** results in a single session.

## Why heavier specs make worse scenes

Every meaningful design decision gets pre-made in the spec layer, before the implementer sees the script. By the time the scene-builder agent reads "you click I'm not a robot," the spec has already decoded that into "BG: vignette + grain + ghost type 'VERDICT'; MG: checkbox container ~360px square; FG: hairlines + `VERIFICATION · 1 / 1` label." The implementer's job is to render the spec faithfully. It has nowhere to invent a real-looking reCAPTCHA widget — because nobody told it to, and the spec told it something else.

In the maiden video, the model saw the script line "you start typing" and *invented* an editor window with a titlebar, three dots, and a glowing amber cursor. That leap is what makes scenes feel alive. The leap can only happen when the model is reading the script directly, not a pre-digested spec of the script.

## Rules going forward

### 1. Keep `design.md` ≤ ~50 lines

What belongs:
- Palette (10-ish tokens)
- Typography (sans / mono, sizes, eyebrow rules)
- Motion (eases, stagger, ambient-loop rule, ≥3 eases per scene)
- 5–6 Don'ts

What does **not** belong (yet):
- Atmosphere-layer recipes ("2–5 of: vignette / grain / hairlines / ghost type / scan strip")
- Transition tables with role / when / duration / easing
- Component formulas ("Stat callout: Oswald 800, 140–180px, tabular-nums…")

These are tempting because they look thorough. They close the lexicon. Add them only after the **third** video proves you keep reaching for the same primitive — premature abstraction otherwise.

### 2. Skip `expanded-prompt.md` by default

The prompt-expansion step is heavy scaffolding that pre-decides every scene's depth layers, verbs, and transitions. Most videos do not need it. The maiden video shipped without it.

Use it only when:
- Runtime is 6+ minutes AND
- The script has dense beats that genuinely need explicit per-scene timing locks AND
- You're willing to treat the expansion as a **constraint envelope** (palette + anchor timings + transition out), not as a scene script

Even then: the expansion must self-check against project CLAUDE.md before emitting. The captchas expansion cited the no-chrome rule then violated it — that's a bug class worth treating as a hard gate.

### 3. Multi-composition split is fine, but commit to building all scenes

Pre-scaffolding `compositions/scene-01.html` ... `scene-11.html` is neutral on creativity, but it creates a coordination tax. Either:
- Build all scenes in a single session, OR
- Use single-file composition for short videos (≤2–3 min)

Don't end a session with placeholder stubs and consider the work "done."

### 4. The first scene sets the quality bar

If Scene 1 is a generic CSS checkbox, every later scene will be a generic CSS something-else. If Scene 1 is a real-looking reCAPTCHA widget, the model carries that level of worldbuilding forward.

Practical lever: when invoking `/hyperframes`, **point at a known-good reference video** as the explicit quality bar. The captchas rebuild used: *"Treat `videos/why-text-is-hard-2026-05-07/index.html` as the quality bar — invent worldbuilding (real-looking reCAPTCHA on a real-looking webpage, etc.), not generic CSS primitives."* That sentence is doing most of the work.

### 5. First-message specificity matters

The captchas first session was kicked off with: *"Ok, I'm done with this voiceover, what is the next step?"* That open-endedness lets the skill machinery default to its heaviest path (expanded-prompt + per-beat split + subagent dispatch).

The maiden session was kicked off with: *"Use /clean-audio to transcribe… cut 2 minutes via ffmpeg… put everything in `output`."* That specificity anchored a small, concrete first step and let the build grow iteratively.

Rule of thumb: the first message should name **one concrete artifact** to produce, not ask "what's next."

### 6. Pipeline-emitted artifacts must respect project CLAUDE.md

When a skill or scaffold step produces an intermediate artifact (`design.md`, `expanded-prompt.md`, per-scene spec, etc.), that artifact has to pass the same project rules the final composition does. The captchas `expanded-prompt.md` is the cautionary tale: it cited the no-chrome rule in its negative-prompt section, then prescribed `VERIFICATION · 1 / 1` in Beat 1's depth layers. A meta-check at the end of any spec-generating step ("re-read project CLAUDE.md; does this artifact comply?") catches this.

## Quick failure smell-tests

If any of these are true mid-pipeline, you are heading toward the captchas-failure mode:

- `design.md` is over 60 lines
- `.hyperframes/expanded-prompt.md` exists and is over 100 lines
- `compositions/` contains files marked `PLACEHOLDER` or `[ TO BE BUILT ]`
- The Scene 1 thumbnail is a CSS primitive, not a real-looking artifact
- The session is on turn 7+ and Scene 1 isn't built yet

Reset to maiden-video conditions and re-invoke `/hyperframes` with an explicit quality-bar reference.
