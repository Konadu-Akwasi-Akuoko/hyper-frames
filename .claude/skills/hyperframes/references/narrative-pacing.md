# Narrative Pacing

`beat-direction.md` plans one scene. `transitions.md` plans one boundary.
`motion-principles.md`'s build / breathe / resolve plans the inside of one scene. This
file is the level above all of them: the **tension arc across the whole runtime** —
where energy peaks, where it breathes, and how those choices line up with what the
script is doing emotionally.

This is a set of lenses, not a recipe. There is no prescribed arc for any video. The
Rhythm Planning step in `beat-direction.md` already asks you to name a pattern
(`fast-fast-SLOW-fast-SHADER-hold`); this file is about choosing that pattern to
**reinforce the script's emotional beats**, not to manufacture visual variety.

## The rhythm pattern is a choice, not a default

`beat-direction.md` gives rhythm templates by video *type* (social ad, product demo,
brand reel). Those are starting points. For a multi-minute explainer the pattern should
be chosen against the *script*, not the format:

- Find the script's strongest beat — the payoff the hook was carved to set up. Visual
  energy should peak there, not at a round-numbered scene.
- Find where the script slows down to explain something dense. That is a *hold*,
  wherever it falls in the runtime.
- Find where the script lands. Energy resolves there — it does not keep escalating into
  the outro.

A rhythm pattern picked for variety alone ("three slow scenes, time for a fast one")
drifts away from the narration. A pattern picked against the script's arc stays locked
to it.

## Pacing follows the emotional arc

Cut speed *is* an emotional signal. Fast cuts read as urgency and climax; slow pacing
reads as reflection and weight. Match the cut rhythm to what the script is feeling:

- **Climactic / high-stakes narration** → faster cuts, shorter scenes, the boldest
  transition (`transitions.md` "Climax / hero reveal" row).
- **Dense / explanatory narration** → slower pacing, longer holds. Let one idea land
  before the next. Pacing adapts to complexity — slow for the hard part, fast for
  emphasis.
- **Reflective / landing narration** → wind-down. `transitions.md`'s "Wind-down" and
  "Outro" rows already describe this; the point here is that the wind-down is keyed to
  the *script's* landing, not to a scene count.

Motion supports the story; it never leads it. A simple animated callout that clarifies
the narrated idea beats a spectacular transition that doesn't.

## Re-hooking at the sag

Viewer attention dips at predictable points across a long runtime — roughly every couple
of minutes, and around the midpoint. The fix is not louder motion everywhere; it is a
deliberate **fresh visual moment before the dip** — a register shift, a new visual world
(`beat-direction.md`: "each beat is a WORLD"), a hero reveal — placed where the script
itself introduces a turn or a new stake.

This is a lens, not a slot. Do not place a re-hook "at 50%". Place it where the script
gives you a turn to land it on. If the script has no mid-video turn, do not manufacture
one with motion.

## The transcript is the arc's timing source

The script's emotional arc is *already in the transcript*. The pacing arc is keyed to it
the same way every other animation is (CLAUDE.md: transcript-as-timing-truth):

- A long silence in the transcript (>600ms) is the script breathing. It is a *breathe*
  phase — see `motion-principles.md`'s build / breathe / resolve. Do not fill it with
  new motion.
- The emphatic words — the longest-duration words, the ones `narration-map.json`
  surfaces — are where energy concentrates.
- If a `story-spine.md` exists at the video folder root, it names where the script's
  hook, climax, and landing landed — useful orientation for where the tension arc should
  peak and resolve. It is optional; a video without one is paced from the transcript and
  script exactly as before.

## The hard-cut question

The storytelling research flags a hard cut as a deliberate **pattern-interrupt** — a way
to jolt the viewer awake at a register shift. This skill already agrees more than it
might first appear:

- `beat-direction.md`'s transition picker has a dedicated "Choose hard cut for" column
  (rapid-fire lists, percussive edits, comedic timing, "anytime a 0.3–0.8s transition
  would feel too slow").
- `motion-principles.md` explicitly says "Use hard cuts for disruption and register
  shifts" — and scolds you for crossfading everything.
- The catalog lists hard cut / smash cut as a transition type.

So a deliberate hard cut **is** a sanctioned transition choice. The one thing to be
careful about: `transitions.md`'s hard rule "Every composition uses transitions. No
exceptions." forbids *unhandled* scene boundaries — a boundary you forgot to transition.
A hard cut is a *handled* boundary; choosing it is using a transition, not skipping one.
Do not read the hard rule as "every boundary must be a soft transition."

Where genuine judgment remains — whether a particular tension moment wants a hard cut
versus a fast shader transition — that is the user's call, made against their own rules.
This file surfaces the option; it does not override `transitions.md`.

## What this file is not

- Not an arc template. No video gets a prescribed tension curve from this file.
- Not a slot system. "Re-hook at 50%", "peak at scene 5" — if you find yourself placing
  beats by percentage, stop. The script's arc decides; this file only helps you read it.
- Not a license to break `transitions.md`. The hard rules there stand.
