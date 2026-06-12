# Design — How WhatsApp Handles 40 Billion Messages Per Day

Dark technical system-design mode. Every scene reads as a *diagram of a machine*,
not a slide: sockets, processes, queues, and envelopes assembling in time. The
recurring editorial motif is the **trade-off** — every architecture choice has a
bill — so the palette carries a dedicated `cost` token alongside the subject green.

## Palette

| Token      | Value     | Use                                                              |
| ---------- | --------- | ---------------------------------------------------------------- |
| `bg`       | `#0a0f0d` | Background canvas (green-tinted near-black)                       |
| `panel`    | `#101613` | Inset cards, server boxes, code blocks                            |
| `border`   | `#1e2722` | Hairline rules and panel borders                                  |
| `fg`       | `#e9edeb` | Headlines, primary / hero text the viewer reads                   |
| `soft`     | `#c3cbc7` | Secondary / concession narration — still readable                 |
| `muted`    | `#79857f` | Labels, captions, metadata **only**                               |
| `dim`      | `#39443f` | De-emphasized strokes, very small text                            |
| `accent`   | `#25d366` | WhatsApp green — rationed; marks the message / WhatsApp itself    |
| `accent-2` | `#7dd3fc` | Sky — infrastructure callouts (sockets, processes, servers, keys) |
| `cost`     | `#f0b429` | Amber — the *bill*: trade-offs, prices paid, "none of it is free" |
| `danger`   | `#ff6b5d` | Failure state: crashes, the outage, dropped messages              |

`accent` green belongs to the message in flight and to WhatsApp-the-subject.
`accent-2` sky belongs to the machine that carries it. When a scene states a
trade-off, the cost side speaks in `cost` amber — that color appearing should
itself signal "here's what it cost them." Never use green and amber decoratively
in the same breath; they are semantic.

## Text hierarchy & emphasis

A clear brightness ramp, not one flat gray:

- **`fg` `#e9edeb`** — default for narration and headlines the viewer reads.
- **`soft` `#c3cbc7`** — secondary / concession lines (setup for a brighter payoff).
- **`muted` `#79857f`** — labels, captions, metadata **only**. Never a hero
  narration line.
- **`dim` `#39443f`** — strokes and very small de-emphasized text.

Rule: **narration the viewer reads is `fg` or `soft`, never `muted`.** Hero and
accent words may carry a subtle `text-shadow` glow (bloom) for depth — **never a
gradient fill**. Inline emphasis is a text-shadow bloom or color ignition, never
a scale pulse on an inline word (it eats the whitespace).

## Typography

Three faces, each with one job:

- **Sans (display / body) — the system voice:** `Inter`. Built-in (reference by
  family name only — no `@font-face`, no Google Fonts link). Weights 300 / 500 /
  700 / 900. Carries **all** structural text: headlines, narration lines, body,
  labels, diagram chrome. Hierarchy from **weight + size + color**.
- **Mono (technical):** `JetBrains Mono`. Built-in. Weights 400, 600. Code,
  protocol tokens (FunXMPP bytes, key material), counters, timestamps, server
  metadata, tabular data. Never prose or headlines. Tabular numerics on all
  counting/stat figures (`font-variant-numeric: tabular-nums`).
- **Hand-annotation — the human voice:** `Excalifont` (single weight, loaded
  locally from `fonts/Excalifont-Regular.woff2`). **Reserved.** Use ONLY for:
  (1) verbatim human words — "let it crash", the "No Ads! No Games! No Gimmicks!"
  desk note; (2) hand-drawn annotations layered *on* clean content (circled
  emphasis, scribbled arrows, margin notes). **Never** structural headlines or UI.
- Headlines: 96–140px / weight 700–900. Body labels: 28–36px / 400–500.
- No eyebrows (no small uppercase mono kickers above headlines).

## Recurring diagram vocabulary

The video follows one message through a machine, so a small consistent visual
vocabulary recurs (drawn fresh per scene, parametrized when reused):

- **The message** — a small rounded green chat-bubble chip (or green dot in
  transit). The one element that's always `accent` green.
- **Phones** — slim rounded-rect outlines, `border` stroke, `accent-2` when live.
- **Servers / boxes** — `panel` rectangles with hairline `border`, mono labels.
- **Sockets / pipes** — long horizontal strokes; warm/lit = `accent-2`, idle = `dim`.
- **Processes (actors)** — small glowing dots/cells inside a server box.
- **The bill** — when a trade-off lands, an amber `cost` line item or counterweight.

## Motion

- Crossfade transitions between scenes (0.5s, `power2.inOut`); incoming foreground
  occludes or outgoing foreground clears — never text-on-text at a seam.
- Entrance staggers ≤ 500ms across a scene; elements slide in from the edge they
  belong to, with a small settle.
- Vary eases: at least 3 different across a scene.
- Ambient motion on every decorative layer and a low-amplitude idle on content
  (slow drift, breathe, 1–2° tilt yoyo). Nothing sits perfectly still.
- Message-in-flight motion (dots traveling pipes) eases like packet traffic:
  fast launch, gentle arrive (`power2.in` → `power3.out`).

## Substrate

Green-tinted near-black depth with a faint, slow-drifting contained glow
(`accent` at very low opacity, well inside the frame — no edge vignette, no
grid-as-hero, no logo). It may dim further behind busy diagram scenes.

## Don'ts

- No gradient text.
- No purple-to-blue or neon gradients.
- No edge vignettes on the substrate (YouTube banding).
- No left-edge accent stripes on cards.
- No identical card grids; no two adjacent scenes with the same archetype.
- No WhatsApp logo in the substrate; the brand lives in scenes, deliberately.
- Green is rationed: if everything glows green, nothing is the message.
