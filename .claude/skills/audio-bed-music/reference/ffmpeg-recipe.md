# FFmpeg bake recipe

One `ffmpeg` invocation with a `filter_complex` graph produces the bed
deterministically. Re-running with the same inputs produces an identical
output, which matters when iterating on volume or boundary placement.

The full path to ffmpeg on macOS Homebrew is `/opt/homebrew/bin/ffmpeg`.
Use it explicitly if your shell alias doesn't resolve in non-interactive
bash.

## Per-layer filter chain

Each layer goes through this pipeline before the outer crossfades:

```
atrim → asetpts=PTS-STARTPTS → [optional inner acrossfade for bridges]
       → afade (head/tail only) → loudnorm
```

- **`atrim=0:LENGTH`** — clip to the planned input span. `LENGTH` is the
  per-layer source duration computed in [transcript-pause-finder.md](transcript-pause-finder.md)
  step 3, plus 1s of head/tail headroom on the outer-crossfade ends.
- **`asetpts=PTS-STARTPTS`** — reset timestamps to zero after `atrim`. Skip
  this and `acrossfade` misalignments will silently shift the output.
- **Inner `acrossfade=d=2:c1=qsin:c2=qsin`** — only on bridged layers
  (two sources stitched). Place between the two source streams of that
  layer, before `loudnorm`.
- **`afade=t=in:st=0:d=1.5`** — fade-in only on the first layer (head of
  the bed). Without it the bed slams in at full level.
- **`afade=t=out:st=START:d=DUR`** — fade-out only on the last layer (tail
  of the bed). `START` is `LENGTH - DUR`. Typically `DUR=3` to `DUR=4`.
- **`loudnorm=I=-28:LRA=11:TP=-2`** — one-pass loudness normalization to
  −28 LUFS integrated, max true peak −2 dBTP. Per-layer (not on the
  final output) so layers reach equal perceived loudness regardless of
  source mastering. One-pass is approximate (expect the final bake to
  land in the −24 to −28 LUFS range); two-pass is more accurate but
  rarely worth the extra complexity for an ambient bed.

## Outer crossfades and final limiter

Between adjacent layers:

```
acrossfade=d=2:c1=qsin:c2=qsin
```

`qsin` (quarter-sine fade-out paired with quarter-cosine fade-in) gives
**equal-power** crossfades. The default `tri` (linear) produces a −6 dB
dip at the midpoint and reads as a brief level drop, which is the opposite
of what you want at a boundary that's supposed to disappear.

After the last outer crossfade, finish with:

```
alimiter=limit=0.85
```

The limiter is insurance against post-loudnorm peaks bumping into 0 dBFS.
0.85 ≈ −1.4 dBFS, leaving comfortable headroom.

## Three-layer template

This is the recipe from the captcha-video session. Three layers, with the
middle layer (`B`) bridged from two source files. Adapt the layer count
and bridge by adding/removing chains and outer `acrossfade` steps.

```bash
/opt/homebrew/bin/ffmpeg -y \
  -i "audio/layer_a/<file>.wav" \
  -i "audio/layer_b/<main>.wav" \
  -i "audio/layer_b/<bridge>.wav" \
  -i "audio/layer_c/<file>.wav" \
  -filter_complex "
    [0:a]atrim=0:100.6,asetpts=PTS-STARTPTS,
         afade=t=in:st=0:d=1.5,
         loudnorm=I=-28:LRA=11:TP=-2[a];

    [1:a]atrim=0:155.3,asetpts=PTS-STARTPTS[b1];
    [2:a]atrim=0:33.1,asetpts=PTS-STARTPTS[b2];
    [b1][b2]acrossfade=d=2:c1=qsin:c2=qsin,
            atrim=0:176.16,asetpts=PTS-STARTPTS,
            loudnorm=I=-28:LRA=11:TP=-2[b];

    [3:a]atrim=0:114.85,asetpts=PTS-STARTPTS,
         afade=t=out:st=110.85:d=4,
         loudnorm=I=-28:LRA=11:TP=-2[c];

    [a][b]acrossfade=d=2:c1=qsin:c2=qsin[ab];
    [ab][c]acrossfade=d=2:c1=qsin:c2=qsin[bed];
    [bed]alimiter=limit=0.85[out]
  " \
  -map "[out]" -ac 2 -ar 48000 -c:a pcm_s16le \
  audio/music-bed.wav
```

## Trim math

The output length of an `acrossfade=d=D` over inputs of length `Lₐ` and `Lᵦ`
is `Lₐ + Lᵦ − D`. For N layers with `d=2` outer crossfades:

```
output_length = sum(per_layer_lengths) − 2 * (N − 1)
```

Pick per-layer trim lengths so the sum equals `VO_duration + 2 * (N − 1)`.
For the captcha bake: 100.6 + 176.16 + 114.85 − 2 − 2 = 387.61s. The VO
was 387.63s; a 0.02s mismatch is inaudible.

For a bridged layer, the bridged stream's effective length before its
outer crossfade is `L_main + L_bridge − D_inner − trim_excess`. Use a final
`atrim` after the inner crossfade to hit exactly the layer length you
need (see `[b]` in the template — the inner crossfade produces 186.4s,
trimmed to 176.16s).

## N-layer generalization

For N layers `[0, 1, …, N−1]`:

1. One input chain per source file, named `[L0_a]`, `[L1_a]`, `[L1_b]`
   (if layer 1 is bridged), `[L2_a]`, etc.
2. Inner `acrossfade` for any bridged layer.
3. `loudnorm` on each layer's pre-crossfade stream → `[layer_0]`,
   `[layer_1]`, …, `[layer_N-1]`.
4. Chain outer `acrossfade`s:
   `[layer_0][layer_1]acrossfade=d=2:c1=qsin:c2=qsin[l01];`
   `[l01][layer_2]acrossfade=d=2:c1=qsin:c2=qsin[l02];`
   …
5. Final `alimiter` on `[l0…N-1]`.

For 2 layers, drop everything but `[layer_0][layer_1]…[bed]`. For 1 layer
(no crossfades), the recipe collapses to `atrim → afade in → afade out →
loudnorm → alimiter`.

## Verify

After the bake:

```bash
# Duration check — should match VO duration within ±1s
/opt/homebrew/bin/ffprobe -v error \
  -show_entries format=duration -of default=nw=1:nk=1 \
  audio/music-bed.wav

# Loudness check — should report I near -28 LUFS, TP <= -2 dBTP
/opt/homebrew/bin/ffmpeg -hide_banner -nostats \
  -i audio/music-bed.wav -af ebur128=peak=true -f null - 2>&1 | tail -15
```

If integrated loudness comes back hotter than −22 LUFS, re-bake with a
lower `loudnorm I` target (e.g. `I=-32`) or check that you didn't
accidentally drop the per-layer `loudnorm` filters.

## Waveform sanity (optional but cheap)

Render PNG waveforms before baking to visually align cut points against
amplitude envelopes:

```bash
mkdir -p audio/.waveforms
for f in audio/voiceover.mp3 audio/layer_*/...wav; do
  /opt/homebrew/bin/ffmpeg -y -loglevel error -i "$f" \
    -filter_complex "showwavespic=s=2400x320:colors=#67e8f9:split_channels=0" \
    -frames:v 1 "audio/.waveforms/$(basename ${f%.*}).png"
done
```

After the bake, render the bed itself with a different colour so it's
visually distinct from the source layers:

```bash
/opt/homebrew/bin/ffmpeg -y -loglevel error -i audio/music-bed.wav \
  -filter_complex "showwavespic=s=2400x320:colors=#ffb547|#67e8f9:split_channels=0" \
  -frames:v 1 audio/.waveforms/music-bed.png
```

These PNGs are disposable. Add `audio/.waveforms/` to `.gitignore` or treat
it as cache.
