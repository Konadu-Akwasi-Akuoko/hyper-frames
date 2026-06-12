# Design — Short 01: How 32 People Ran 40 Billion Messages a Day

**Portrait 1080×1920 Short.** Inherits the parent video's dark system-design
look — every scene reads as a *diagram of a machine*, not a slide. This Short's
single idea: **extreme leverage** — a tiny team, tiny hardware, impossible scale.
The trade-off motif still applies (the bus-factor bill at the end speaks in amber).

## Format

- **Canvas: 1080×1920 (9:16).** Root host, `html,body`, `.scene`, and the
  viewport meta are all 1080×1920 (already scaffolded — confirm before authoring).
- **Vertical safe zones:** keep hero text and the shock numbers in the middle
  ~60% of the height. Top ~10% and bottom ~12% are phone-UI / caption territory —
  no critical text there. The final "Subscribe" cue lands **upper-middle**, never
  over where the phone's real Subscribe button sits (bottom).
- **Big and few.** One idea per scene, large type, generous negative space.
  Mobile viewers read at arm's length — headlines bigger than the long-form.

## Palette (inherited — semantic, not decorative)

| Token | Value | Use |
|-------|-------|-----|
| `bg` | `#0a0f0d` | Background canvas (green-tinted near-black) |
| `panel` | `#101613` | Inset cards, server boxes, code blocks |
| `border` | `#1e2722` | Hairline rules and panel borders |
| `fg` | `#e9edeb` | Headlines / primary text the viewer reads |
| `soft` | `#c3cbc7` | Secondary / concession lines |
| `muted` | `#79857f` | Labels, captions, metadata only |
| `dim` | `#39443f` | De-emphasized strokes, very small text |
| `accent` | `#25d366` | WhatsApp green — rationed; the message / WhatsApp itself |
| `accent-2` | `#7dd3fc` | Sky — infrastructure (sockets, processes, servers) |
| `cost` | `#f0b429` | Amber — the bill: the bus-factor risk at the close |
| `danger` | `#ff6b5d` | Failure state (a crashing process flickering out) |

Green = the message / WhatsApp. Sky = the machine that carries it. Amber appears
**only** on the closing trade-off. Green is rationed — if everything glows green,
nothing is the message.

## Typography (inherited, all built-in except Excalifont)

- **Sans — system voice:** `Inter` (300/500/700/900). All structural text:
  headlines, narration, labels. Hierarchy from weight + size + color.
- **Mono — technical:** `JetBrains Mono` (400/500; **avoid 600 — renders italic
  in HyperFrames**). The big counting figures — `32`, `40,000,000,000`,
  `2,000,000`, `14M`. `font-variant-numeric: tabular-nums` on all stat figures.
- **Hand — human voice:** `Excalifont` (local `fonts/`). Reserved for hand
  annotations only (e.g. a circled "32" or a scribbled "per engineer?!"). Never
  structural headlines.
- Portrait headline scale: ~110–180px hero; stat figures can go larger.

## Scene beats (anchor to transcript word timings)

1. **Hook** — "Thirty-two engineers / forty billion messages a day." The `32`
   and `40B` are the heroes — mono, huge, stacked vertically. Green on the 40B
   (the messages), sky/fg on the 32 (the team).
2. **Counter-twist** — two million live phones on one server. A single server
   box (sky), a swarm of tiny process-dots inside it.
3. **The socket** — one persistent pipe per phone, held open. Vertical pipe
   metaphor reads well in portrait.
4. **The actor + let-it-crash** — process-dots; one flickers `danger` and a
   clean one respawns; the others keep glowing.
5. **Meta-reward line** — "Subscribe if that already sounds insane" — a light,
   quick on-screen beat (not the full CTA card yet).
6. **The leverage math** — `~14,000,000 users / engineer`. The payoff stat.
7. **CTA (final scene)** — the bus-factor bill in `cost` amber, then the
   subscribe block. "Subscribe" cue upper-middle, landing on the VO's
   "subscribe" word. Adapt a native portrait follow block.

## Motion (inherited)

- Crossfade between scenes (0.5s, `power2.inOut`); no text-on-text at seams.
- Entrance staggers ≤500ms; elements slide from the edge they belong to.
- Vary eases (≥3 across the Short). Message-dots ease like packet traffic
  (fast launch → gentle arrive).
- Low-amplitude idle on everything; faint contained green glow on the substrate
  (no edge vignette, no grid-as-hero, no logo).

## Don'ts (inherited)

- No gradient text, no neon gradients, no edge vignettes, no left-edge accent
  stripes, no WhatsApp logo in the substrate.
- No editorial chrome (no scene labels, timecodes, corner metadata).
- Green rationed; green + amber never decoratively in the same breath.
