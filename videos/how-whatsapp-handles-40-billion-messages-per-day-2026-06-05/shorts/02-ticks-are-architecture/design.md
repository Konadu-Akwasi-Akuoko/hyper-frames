# Design — Short 02: What WhatsApp's Ticks Are Actually Telling You

**Portrait 1080×1920 Short.** Inherits the parent video's dark system-design
look — every scene reads as a *diagram of a machine*, not a slide. This Short's
single idea: **the ticks are the architecture leaking through** — the grey/blue
ticks you watch every day are store-and-forward reporting its own state. The
relay (server in the middle) is the hero object; the ticks are its read-out.

## Format

- **Canvas: 1080×1920 (9:16).** Root host, `html,body`, `.scene`, and the
  viewport meta are all 1080×1920 (already scaffolded — confirm before authoring).
- **Vertical safe zones:** keep hero text and the tick glyphs in the middle ~60%
  of the height. Top ~10% and bottom ~12% are phone-UI / caption territory — no
  critical text there. The final "Subscribe" cue lands **upper-middle**, never
  over where the phone's real Subscribe button sits (bottom).
- **Big and few.** One idea per scene, large type, generous negative space.
  Mobile viewers read at arm's length — headlines bigger than the long-form.

## The spine (visual idea, not a storyboard)

The recurring object is a **three-node relay**: `phone → [server] → phone`, with
the server in the middle doing the holding. Every beat re-reads the same relay:
- **Hook/twist:** the ticks float up as the "secret" the relay is leaking.
- **Store-and-forward:** the message hops phone → server (held) → phone, never
  phone↔phone directly. The direct path is shown crossed out.
- **The tick ladder:** one grey ✓ = server has it; two grey ✓✓ = device has it;
  two blue ✓✓ = read. Build them as a state ladder, each rung lighting in turn.
- **Offline queue:** the message drops into an encrypted queue with a **30-day**
  countdown — drains instantly inside the window, gone forever after.
- **CTA:** the relay carries every message but can't read one → subscribe.

## Palette (inherited — semantic, not decorative)

| Token | Value | Use |
|-------|-------|-----|
| `bg` | `#0a0f0d` | Background canvas (green-tinted near-black) |
| `panel` | `#101613` | Inset cards, the server box, queue cells |
| `border` | `#1e2722` | Hairline rules and panel borders |
| `fg` | `#e9edeb` | Headlines / primary text the viewer reads |
| `soft` | `#c3cbc7` | Secondary / concession lines |
| `muted` | `#79857f` | Labels, captions, metadata, **grey ticks** |
| `dim` | `#39443f` | De-emphasized strokes, very small text |
| `accent` | `#25d366` | WhatsApp green — rationed; the message itself |
| `accent-2` | `#7dd3fc` | Sky — the machine: the relay/server, **blue read-ticks** |
| `cost` | `#f0b429` | Amber — the 30-day queue countdown / the "waiting" state |
| `danger` | `#ff6b5d` | "Gone forever" — the message expiring past the window |

Green = the message. Sky = the machine that carries it (and the blue read-tick is
the machine confirming a human action). Grey ticks are `muted` — deliberately
quiet until they go blue. Amber appears **only** on the 30-day queue. Green is
rationed — if everything glows green, nothing is the message.

## Typography (inherited, all built-in except Excalifont)

- **Sans — system voice:** `Inter` (300/500/700/900). All structural text:
  headlines, narration, labels. Hierarchy from weight + size + color.
- **Mono — technical:** `JetBrains Mono` (400/500; **avoid 600 — renders italic
  in HyperFrames**). The countdown figure (`30 DAYS`), node labels, the tick
  state read-out. `font-variant-numeric: tabular-nums` on figures.
- **Hand — human voice:** `Excalifont` (local `fonts/`). Reserved for hand
  annotations only (e.g. a circled tick, a scribbled "read!"). Never structural
  headlines.
- Portrait headline scale: ~110–180px hero; the tick glyphs can go larger.

## Sound (SFX) — per the batch constraint

- **No risers.** Use pops/ticks/wooshes/bass-drops for emphasis; the camera-shutter
  snap and click transients are allowed (user-confirmed 2026-06-11). A soft tick
  on each ✓ rung lighting is on-theme.

## CTA beat

Final scene adapts a native portrait subscribe block. Land the "Subscribe" cue
upper-middle on the VO's "subscribe" word; never over the phone's real button.
CTA loop (per PLAN.md): "the server carries every message but can't read one" →
hands to Short 05 (encryption).
