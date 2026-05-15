# Density as narrative — spending the cue budget

The technical floors govern cue density as a **ceiling**: ≤ 1 cue per 3s rolling
average, plus the same-cue cooldowns. That ceiling is mix-craft physics — it does not
change, and nothing here relaxes it.

This file is about density as a **shape**. Staying under the ceiling everywhere, evenly,
produces a flat score — cues sprinkled at a constant rate, tracking nothing. Cue
frequency is itself an editorial signal: where hits cluster, the moment reads as busy
and high-stakes; where they thin, the moment reads as calm or weighty. Spend the budget
the ceiling allows so its shape matches the story's energy.

## The ceiling is not the plan

The `≤ 1 cue / 3s` ceiling and the cooldowns (`ui-tick` ≥ 2s, `whoosh` ≥ 4s, `boom` ≥
30s) are the floor of correctness. The plan is what you do *inside* them. Two videos can
both honor the ceiling and feel completely different — one with cues spread evenly, one
with cues that breathe with the narration.

## Density shapes — consider, don't prescribe

Three shapes worth considering. None is required; most videos blend them.

- **Rising toward a climax.** Sparse open, density builds as stakes rise, peaks at the
  payoff beat, then a deliberate near-silent beat just after. The cue frequency curve
  mirrors the script's tension curve.
- **Sparse throughout.** A contemplative or essay-toned video. Few cues, each one
  unmistakably earning its place. The restraint *is* the texture — see "Silence — the
  unused cue" in `cue-vocabulary.md`.
- **Front-loaded.** A high-energy open that sets the video's pace in the first scenes,
  then settles into a calmer body. Right when the hook is doing heavy lifting.

Choose the shape against the script's arc — the same way `hyperframes`'
`narrative-pacing.md` chooses the rhythm pattern against the script. Density picked for
its own sake drifts from the narration; density picked against the arc stays locked to
it.

## Reading the shape from the script

You do not compute a density curve. You read it off the material you already load:

- Where the script **escalates** — stakes naming, a chain of consequences — cues can
  cluster (still under the ceiling).
- Where the script **breathes** — the >600ms pauses `narration-map.json` surfaces — cues
  thin or stop. A breathe phase is not a slot to fill.
- The **payoff beat** — the line the whole video is about — is the natural density peak,
  and the natural home for the once-per-video `boom`.

## Spending versus saving

A cue spent in a low-stakes moment is a cue the cooldown makes unavailable near the
climax. This matters most for `boom` (≥ 30s apart, "more than once per 30s wears out
instantly"). Spend the boom on the line the video is about — not the first big number
that happens to scroll past. Saving density for the moment that earns it is as
deliberate an act as spending it.

## What this file is not

- Not a required density curve. The ceiling is the only hard number; the shape is yours
  to choose against the script.
- Not a per-window quota. Nothing here says "N cues in scene 3."
- Not a license to approach the ceiling. "When in doubt, score less" still holds — the
  shape is about *where* the budget goes, not about spending all of it.

## Cross-layer coordination

The video has more layers than SFX. The `hyperframes` hero / SHADER transition, this
skill's climax `boom` (and the `data-sfx-hook="true"` beat), and — on a later pass — the
`audio-bed-music` bed's swell should all point at the **same beat**. The failure mode is
three layers each independently picking a different "most important moment," so the
video has no single climax.

If a `story-spine.md` exists at the video folder root, it names where the script's hook,
climax, and landing landed — use it to confirm your `data-sfx-hook` beat and any climax
`boom` agree with the other layers. It is optional; absent it, identify the climax from
the transcript and visuals exactly as usual.

Music is a separate, later skill (`audio-bed-music`) — not this pass's job. But the two
layers trade foreground: where the bed runs dense, SFX can afford to thin; where the bed
pulls back, an SFX hit carries further. You are not scoring the music here — you are
just identifying the climax beat precisely enough that the music pass can agree with it.
