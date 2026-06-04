# Silence strategy — when the bed should pull back

Continuous underscore fatigues. The strongest momentum-scoring move in film music is
not a crescendo — it is *dropping the bed*. A moment of bed-silence under the voiceover
and SFX gives the viewer a beat to breathe, and the bed's return lands harder than any
swell.

This file is about *when* pulling the bed back tends to land. It is not a fixed list of
silence points — like everything else in this skill, where the bed drops is the human's
call. The file just helps name the candidates.

## Why drop the bed at all

The bed scores the emotional response before the narration is even parsed. But a bed
that never lets up gives the viewer nothing to contrast against — the score flattens
into wallpaper. Silence is a tool here exactly as it is in SFX (`video-director`'s SFX
step — "Silence, the unused cue"): the absence is the effect. A bed that pulls back at the right beat
makes that beat feel weightier, and makes its own return feel earned.

## Where pulling back tends to land

These are the *kinds* of moments where bed-silence tends to work — not a checklist:

- **The payoff line** — the sentence the whole video is about. Let the voiceover carry
  it alone; bring the bed back after.
- **A high-emotional-weight beat** — the moment the script treats as load-bearing, where
  a pad underneath would dilute rather than support.
- **Just before a major reveal** — pre-impact silence. This is the beat the SFX step
  marks with `data-sfx-hook="true"`; the bed thinning or stopping ahead of it is the
  music-side of the same move.
- **The landing** — some videos want the bed to thin or stop under the closing line, so
  the last words land in the room rather than under a pad.

If a `story-spine.md` exists at the video folder root, it names where the script's hook,
climax, and landing landed — useful for spotting which beats are worth pulling back for.
It is optional; absent it, the payoff and load-bearing beats come from `script.md` and
the brainstorm exactly as before.

Most videos pull back once, maybe twice. A bed that drops out every thirty seconds is as
fatiguing as one that never does.

## How it works in this pipeline

A bed pullback is not a new layer — it is a volume move *within* a layer, or a silent
gap *between* layers:

- The simplest form is a gap at a layer boundary: the outgoing layer's tail fades out a
  beat early, the incoming layer fades in a beat late, leaving real silence in between.
- A mid-layer pullback is an `afade` down and back up inside a single layer's segment of
  the `filter_complex` graph — see `reference/ffmpeg-recipe.md` for the filter shape.
- The pullback window is found the same way crossfade boundaries are — the snippets in
  `reference/transcript-pause-finder.md`. A payoff line is usually bracketed by
  sentence-boundary pauses; the bed fades down into the pause before the line and back
  up in the pause after.

Treat a pullback as a Phase 1 brainstorm topic and a Phase 3 plan item — surface it to
the user the way layer boundaries are surfaced, by beat or by quote. The skill does not
decide where the bed drops; the human does.

## What this file is not

- Not a fixed set of silence points. No video gets a prescribed pullback schedule.
- Not a mandate. A bed with no pullbacks is a valid bed — some videos want continuous
  underscore, and the human may choose exactly that.
- Not a license to script the music's emotion. Music is taste — this file describes a
  move the human may reach for; it does not reach for it on their behalf.
