# Design — Short 03: WhatsApp's Message Numbers Don't Add Up

**Portrait 1080×1920 Short.** Inherits the parent video's dark system-design
look — every scene reads as a *diagram of a machine*, not a slide. This Short's
single idea: **server-side fan-out** — you send one message into a group and the
*server* multiplies it into one copy per member. That's why 20 billion "sent"
becomes 64 billion in a day. The gap isn't a bug; it's fan-out made visible.

## Format

- **Canvas: 1080×1920 (9:16).** Root host, `html,body`, `.scene`, and the
  viewport meta are all 1080×1920 (scaffolded — confirm before authoring).
- **Vertical safe zones:** keep hero text and the number figures in the middle
  ~60% of the height. Top ~10% and bottom ~12% are phone-UI / caption territory
  — no critical text there. The final "Subscribe" cue lands **upper-middle**,
  never over where the phone's real Subscribe button sits (bottom).
- **Big and few.** One idea per scene, large type, generous negative space.
  Mobile viewers read at arm's length — headlines bigger than the long-form.

## The spine (visual idea, not a storyboard)

The recurring object is a **fan-out tree**: one phone (the sender) → a single
labelled packet rises to a central **server** → the server sprays N copies down
to N member phones. Every beat re-reads that one mechanism:
- **Hook:** two figures that should match but don't — `20,000,000,000 sent`
  vs `64,000,000,000`. The gap is the mystery.
- **Counter-twist:** where do the extra ~40 billion come from? Spotlight the gap.
- **One copy up:** the sender uploads **exactly one** packet, tagged with a
  group ID — your battery/data only ever pay for that one.
- **N copies out:** the server looks up every member and queues a separate copy
  per person. One in, a hundred out — the multiply happens server-side.
- **Name it:** "server-side fan-out", anchored to the real **Apr 2, 2014** day:
  20B sent → 44B delivered → 64B total.
- **The kicker:** cost scales with **group size**, not with who's typing. One
  person triggers thousands of deliveries.
- **CTA:** years later they flipped fan-out inside-out just to put your chats on
  a laptop → subscribe (hands to Short 05 / multi-device).

## Palette (inherited — semantic, not decorative)

| Token | Value | Use |
|-------|-------|-----|
| `bg` | `#0a0f0d` | Background canvas (green-tinted near-black) |
| `panel` | `#101613` | Inset cards, the server box, member cells |
| `border` | `#1e2722` | Hairline rules and panel borders |
| `fg` | `#e9edeb` | Headlines / primary text the viewer reads |
| `soft` | `#c3cbc7` | Secondary / concession lines |
| `muted` | `#79857f` | Labels, captions, metadata |
| `dim` | `#39443f` | De-emphasized strokes, very small text |
| `accent` | `#25d366` | WhatsApp green — rationed; the **one** message sent |
| `accent-2` | `#7dd3fc` | Sky — the machine: the server + the fanned-out copies |
| `cost` | `#f0b429` | Amber — the **gap / the multiplied count** (the surprise) |
| `danger` | `#ff6b5d` | Reserved — the "cost scales with the group" warning beat |

Green = the single message you send. Sky = the machine and the copies it makes.
Amber carries the shock number — the gap, the 64-billion total. Green is
rationed: there is only ever ONE green packet (what you send); everything the
server multiplies is sky. If everything glows green, nothing is the message.

## Typography (inherited, all built-in)

- **Sans — system voice:** `Inter` (300/500/700/900). All structural text:
  headlines, narration, labels. Hierarchy from weight + size + color.
- **Mono — technical:** `JetBrains Mono` (400/500; **avoid 600 — renders italic
  in HyperFrames**). The big figures (`20,000,000,000`, `64B`, `Apr 2 2014`),
  node labels, the group-ID tag. `font-variant-numeric: tabular-nums` on every
  figure so digits don't jitter when they count.
- Portrait headline scale: ~110–180px hero; the big number figures can go larger
  but must stay inside the middle safe band (they're long — watch horizontal fit
  at 1080px, set in mono and shrink rather than overflow).

## Sound (SFX) — per the batch constraint

- **No risers.** Use pops/ticks/wooshes/bass-drops for emphasis; the
  camera-shutter snap and click transients are allowed (user-confirmed
  2026-06-11). The fan-out spray wants a `whoosh` on the packet travelling up
  and soft `card-tap`/`pop` per copy landing; the 64B total lands on a `boom`.

## CTA beat

Final scene adapts a native portrait subscribe block. Land the "Subscribe" cue
upper-middle on the VO's "subscribe" word; never over the phone's real button.
CTA loop (per PLAN.md): "they flipped fan-out inside-out just to let you read
chats on a laptop — why?" → hands to Short 05 (multi-device / can't-read).
