# Design — Javascript The King of Programming Languages

Technical / editorial dark mode. Feels like a Computerphile / Fireship explainer with
a touch of editorial restraint. Every scene reads as a diagram, not a slide.

## Palette

| Token       | Value     | Use                                                  |
| ----------- | --------- | ---------------------------------------------------- |
| `bg`        | `#0b0d12` | Background canvas (warm-tinted near-black)           |
| `panel`     | `#11141b` | Inset cards, code blocks                             |
| `border`    | `#1f242c` | Hairline rules and panel borders                     |
| `fg`        | `#e8eaed` | Headlines, primary / hero text the viewer reads      |
| `soft`      | `#c2c9d4` | Secondary / concession narration — still readable    |
| `muted`     | `#7a8493` | Labels, captions, metadata **only**                  |
| `dim`       | `#3a4150` | De-emphasized strokes, very small text               |
| `accent`    | `#f7df1e` | JS-yellow — rationed; marks JavaScript itself only   |
| `accent-2`  | `#67e8f9` | Cyan — secondary callouts, vector points             |
| `danger`    | `#ff6b5d` | "Hard" / problem state                               |
| `ok`        | `#7dd87d` | "Easy" / resolved state                              |

## Text hierarchy & emphasis

A clear brightness ramp, not one flat gray, is what keeps text from reading bland:

- **`fg` `#e8eaed`** — default for narration and headlines the viewer reads.
- **`soft` `#c2c9d4`** — secondary / concession lines (a deliberate step down from
  fg, still readable). Use when a line is setup for a brighter payoff line.
- **`muted` `#7a8493`** — labels, captions, metadata **only**. Never a hero
  narration line.
- **`dim` `#3a4150`** — strokes and very small de-emphasized text.

Rule: **narration the viewer reads is `fg` or `soft`, never `muted`.** Hero and
accent words may carry a subtle `text-shadow` glow (bloom) for depth — **never a
gradient fill**.

*Exception:* "unlit" UI text that a highlight ignites *from* (e.g. the Hacker News
comment body whose damning fragments brighten `muted` → `fg` on the beat) may sit
at `muted` as its dim base — that's a lighting mechanic, not a label.

## Typography

Three faces, each with one job. The split is semantic, not decorative: clean Inter
is the system/authority voice; hand-drawn Excalifont is the human scribbling on top
of it — which mirrors the video's thesis (a messy human language running clean
infrastructure).

- **Sans (display / body) — the system voice:** `Inter`. Built-in (reference by
  family name only — no `@font-face`, no Google Fonts link). Weights 300 / 500 /
  700 / 900. Carries **all** structural text: headlines, narration/reframe lines,
  body, labels, UI chrome (wordmarks, button-like affordances), data. Hierarchy
  comes from **weight + size + color**.
- **Mono (technical):** `JetBrains Mono`. Built-in. Weights 400, 600. Code,
  metadata lines, timestamps, coordinates, tabular data. Never prose or headlines.
- **Hand-annotation — the human voice:** `Excalifont` (single weight, loaded
  locally from `fonts/Excalifont-Regular.woff2`). **Reserved.** Use ONLY for:
  (1) verbatim human quotes — a real person's words; (2) hand-drawn annotations
  layered *on* clean content (circled emphasis, scribbled underlines/arrows,
  margin notes pointing at Inter text). **Never** for structural headlines, body,
  or UI — if it's the narrator/system talking, it's Inter. Appearances should be
  deliberate and sparse: when Excalifont shows up, a human is speaking or annotating.
- Headlines: 96–140px / weight 700–900. Body labels: 28–36px / 400–500.
- No eyebrows (no small uppercase mono kickers above headlines).
- Tabular numerics on coordinates (`font-variant-numeric: tabular-nums`).

## Motion

- Crossfade transitions between scenes (0.5s, `power2.inOut`).
- Entrance staggers ≤ 500ms across a scene.
- Vary eases: at least 3 different across a scene.
- Ambient motion on every decorative layer (slow drift, breathe, pulse).

## Don'ts

- No gradient text.
- No purple-to-blue or neon gradients.
- No cyan-on-dark cliché — accent is JS-yellow, not cyan-first.
- No left-edge accent stripes on cards.
- No identical card grids.
