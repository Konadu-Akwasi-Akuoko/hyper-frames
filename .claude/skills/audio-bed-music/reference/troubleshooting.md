# Troubleshooting

Common failure modes from real bake sessions and the targeted fix for
each. Diagnose by listening *and* by reading the waveform PNG; both
signals together narrow the cause faster than either alone.

## "VO consonants are masked"

**Symptom:** Sibilants and plosives in the voiceover lose definition.
Words like "checkbox", "passed", "fourteen" lose their crispness.

**Fix order:**
1. Drop `data-volume` in `compositions/music.html` by 0.02 and reload.
2. If 0.10 isn't quiet enough, the bed itself is probably top-heavy. Open
   the bed waveform — if the upper half of the amplitude envelope
   dominates, re-bake with `loudnorm I=-32` to bring it down. Don't push
   `data-volume` below 0.10; below that the bed has no emotional
   presence and you may as well not have it.
3. If specific moments mask while the bulk of the bed is fine, the source
   for that layer has a high-frequency element (a melody line, a vocal
   sample) that fights the VO. Re-curate that layer's source.

## "Layer boundary is audible as a level dip"

**Symptom:** At a crossfade, the mix briefly drops in level before
recovering. Reads as a stutter.

**Cause:** Linear crossfade (the `acrossfade` default) produces a −6 dB
dip at the midpoint because the two halves don't sum to constant power.

**Fix:** Confirm `c1=qsin:c2=qsin` is present on every outer `acrossfade`
in the bake invocation. If it's already there, the issue is loudness
mismatch between the layers — re-bake with per-layer `loudnorm` (one of
the layers may have lost its `loudnorm` filter in editing). The `ebur128`
verification step catches this: if integrated loudness is fine but a
specific layer measured in isolation is much hotter, that layer's
per-layer normalization wasn't applied.

## "Crossfade is audible as a hard cut"

**Symptom:** Boundary sounds like a splice, not a blend. Often
accompanied by a transient (click, breath, kick) right at the midpoint.

**Cause:** The boundary midpoint landed on top of a SFX hit or a VO
emphatic word rather than inside a pause.

**Fix:** Re-snap the midpoint to a larger pause in the same window (see
`transcript-pause-finder.md` snippet 1). If no large-enough pause exists
near the intended narrative beat, widen the search window — the human's
intent doesn't change much over ±5 seconds, and a 0.6s gap two seconds
away is better than a 0.2s gap right on the beat.

## "Internal bridge splice sounds glued"

**Symptom:** Inside a bridged layer, the join between two source files
(main + short, or stem + stem) reads as two different tracks butted
together rather than continuous music.

**Cause:** The two sources aren't musically continuous — they're from
different sections of the same composition with incompatible energy or
key.

**Fix:** Swap the bridge source. Layer folders typically contain several
candidates (full version, shorts, loops, stems) — pick a different one.
Loops are usually the most splice-friendly because they're designed to
repeat. If no candidate works, raise the inner crossfade duration to 4s
(`acrossfade=d=4:...`) to soften the transition; this works best when
the bridge moment falls under busy VO that masks the crossfade itself.

## "Bed clips / peaks visible in waveform"

**Symptom:** The bed's waveform PNG shows the envelope hitting the top
and bottom of the canvas. Audible distortion in dense passages.

**Cause:** A layer wasn't loudnormed, or the `alimiter` step is missing
from the filter chain.

**Fix:**
1. Confirm every layer has `loudnorm=I=-28:LRA=11:TP=-2` in its chain.
2. Confirm `alimiter=limit=0.85` is the last filter before `-map "[out]"`.
3. Re-verify with `ffmpeg -af ebur128=peak=true`. True peak should be
   ≤ −2 dBTP. If it's higher, the limiter isn't doing its job — drop
   `limit` to `0.8`.

## "Bed duration doesn't match VO"

**Symptom:** `ffprobe` reports the bed is shorter or longer than the
voiceover. Either silence at the end or the closer line plays over a
cut-off bed.

**Cause:** Trim math is off. Each outer `acrossfade=d=D` subtracts `D`
from the sum of input lengths.

**Fix:** Recompute with the formula in `ffmpeg-recipe.md` ("Trim math"
section):

```
output_length = sum(per_layer_lengths) − 2 * (N − 1)
```

For N layers and 2s crossfades, the target sum-of-trims is
`VO_duration + 2 * (N − 1)`. Adjust the final layer's `atrim` length to
absorb the difference — its tail is faded out anyway, so a small change
there is inaudible.

## "No `transcript.json` at the video folder"

**Symptom:** The pause-finder snippets fail with `FileNotFoundError`.

**Cause:** Voiceover pipeline hasn't been run, or the transcript landed
under a different name.

**Fix:** Stop. Tell the user the music bed needs `transcript.json` at
the video folder root before boundaries can be snapped to silence.
Refer them to the `voiceover-elevenlabs-v2` (default) or
`voiceover-elevenlabs-v3` skill to generate it. Resume once the file
exists.

## "Source folder has zip artifacts (`__MACOSX/`, `.DS_Store`)"

**Symptom:** `ls` on `audio/layer_*/` includes hidden macOS / archive
metadata files. Probing them with `ffprobe` fails.

**Fix:** Skip files starting with `.` or `_` when enumerating sources.
Don't delete them — they're harmless, and the user may have downloaded
the layer folder as a `.zip` they want intact.

## "User wants different vibe per layer after the bake"

**Symptom:** After the bake, the user listens and says "actually layer
B should be tenser." This is taste drift, not an engineering failure.

**Fix:** Hand back to `superpowers:brainstorming` for the affected
layer only. Once the user re-curates that layer's folder, re-run Phase 4
(bake) and Phase 5 (wire) — Phase 3's boundary plan typically stays
valid since the boundary timing is independent of the source identity.
