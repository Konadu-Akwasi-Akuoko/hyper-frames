# Design — How Does a CAPTCHA Actually Work?

Technical / editorial dark mode. Feels like a Computerphile / Fireship explainer with
a touch of editorial restraint. Every scene reads as a diagram, not a slide.

## Palette

| Token       | Value     | Use                                                  |
| ----------- | --------- | ---------------------------------------------------- |
| `bg`        | `#0b0d12` | Background canvas (warm-tinted near-black)           |
| `panel`     | `#11141b` | Inset cards, code blocks                             |
| `border`    | `#1f242c` | Hairline rules and panel borders                     |
| `fg`        | `#e8eaed` | Headlines, primary text                              |
| `muted`     | `#7a8493` | Captions, labels, metadata                           |
| `dim`       | `#3a4150` | De-emphasized strokes, very small text               |
| `accent`    | `#ffb547` | Amber phosphor — focal callouts, math glyphs, cursor |
| `accent-2`  | `#67e8f9` | Cyan — secondary callouts, vector points             |
| `danger`    | `#ff6b5d` | "Hard" / problem state                               |
| `ok`        | `#7dd87d` | "Easy" / resolved state                              |

## Typography

- **Sans (display / body):** `Inter`. Weights 300, 500, 700, 900.
- **Mono (technical):** `JetBrains Mono`. Weights 400, 600.
- Headlines: 96–140px / 800.
- Section eyebrows: 22px / 500 mono, uppercase, `letter-spacing: 0.18em`, `muted` color.
- Body labels: 28–36px / 400.
- Tabular numerics on coordinates (`font-variant-numeric: tabular-nums`).

## Motion

- Crossfade transitions between scenes (0.5s, `power2.inOut`).
- Entrance staggers ≤ 500ms across a scene.
- Vary eases: at least 3 different across a scene.
- Ambient motion on every decorative layer (slow drift, breathe, pulse).

## Don'ts

- No gradient text.
- No purple-to-blue or neon gradients.
- No cyan-on-dark cliché — accent is amber, not cyan-first.
- No left-edge accent stripes on cards.
- No identical card grids.
