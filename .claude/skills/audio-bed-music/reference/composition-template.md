# Composition template

The music bed mounts as a HyperFrames audio sub-composition at
`compositions/music.html`, mirroring the shape of `compositions/sfx.html`.
Single `<audio>` element, paused GSAP timeline, mounted from `index.html`
at a low track-index so it sits beneath SFX in the studio.

## `compositions/music.html`

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  </head>
  <body>
    <template id="music-layer-template">
      <div
        data-composition-id="music-layer"
        data-width="1920"
        data-height="1080"
      >
        <audio
          id="music-bed"
          class="clip"
          data-start="0"
          data-duration="387.61"
          data-volume="0.18"
          data-track-index="10"
          src="../audio/music-bed.wav"
        ></audio>
        <script>
          (() => {
            window.__timelines = window.__timelines || {};
            window.__timelines["music-layer"] = gsap.timeline({ paused: true });
          })();
        </script>
      </div>
    </template>
  </body>
</html>
```

Adjust `data-duration` to the actual baked length from `ffprobe`. Keep
`data-track-index="10"`; SFX typically uses 19–29 and you want music
visually below.

## `index.html` mount

Add the sub-comp mount block alongside the existing sfx-layer mount
(usually near the end of `<body>`, after the `main` timeline registration
and before `</body>`). Order matters for visual stacking in the studio
timeline, not for audio mixing — but listing music *above* sfx in the
file makes the layering intent obvious to a future reader.

```html
<!-- music-layer: baked bed (audio/music-bed.wav) -->
<div
  id="music-layer"
  data-composition-id="music-layer"
  data-composition-src="compositions/music.html"
  data-start="0"
  data-duration="387.61"
  data-track-index="10"
></div>
```

## Volume tuning

`data-volume="0.18"` is a sensible starting point for a bed mastered to
−28 LUFS sitting under a VO mastered to ~−14 to −18 LUFS. After the user
scrubs the preview, they'll want to nudge:

- **VO consonants feel buried** → drop in 0.02 steps until the bed is
  audibly present but the VO sibilance comes through cleanly.
- **Bed is inaudible / pointless** → raise in 0.02 steps until the bed has
  emotional presence without competing for attention.
- **Typical landing range:** 0.12 → 0.22. Outside that range, the bed
  itself is probably the problem (too hot, too dynamic, wrong mix) and
  re-baking with a different `loudnorm I` target is more reliable than
  pushing `data-volume` further.

Edit `compositions/music.html` and reload the preview tab. No re-bake
needed unless re-baking is what fixes it.

## SFX coexistence

The music bed lives at track-index 10. SFX cues sit at 19–29 by the
project convention (see `tools/sfx-plan`). They mix independently — the
HyperFrames runtime sums the audio outputs, so a SFX cue at `data-volume=
0.35` plus a music bed at `data-volume=0.18` plays both at their authored
levels.

If SFX hits feel masked by the bed, that's a SFX volume problem (raise
SFX cue `default_volume` in `sfx-overrides.yml`), not a music problem.
Don't add per-SFX-cue ducking to the music — keep the bed flat and tune
the SFX layer to sit on top.
