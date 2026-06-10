# Accent recipes

The accent does two jobs in the **Specimen** signature, and this file governs
both:

1. **Placement** — which word in the headline gets the accent hue and the
   `.punch` enlargement (and, optionally, one inner accent).
2. **Hue** — which color from the locked palette the whole thumbnail uses,
   set as a class on `.thumbnail`.

The accent is the **only per-video brand variable**. The Specimen identity
itself lives in the base (#0B0E14 + grid + vignette), the mono-tell, the
layout, and the precision pointer — none of which change per video. So the
hue is free to move with the topic; the placement rules are not.

---

## Part 1 — Placement: which word gets the accent

The headline is white flanking rows plus **one** accent-hued `.punch` row
(bigger). Markup contract: rows are `<span class="thumbnail-row">`; the punch
row adds `punch accent`. The accent is a **row class, never an inner span** —
other skills parse it that way. (Vertical Variant C's kicker row adds
`kicker` on top.)

### The cap

**Maximum 2 accent regions per thumbnail.** That is: one `.punch accent` row
(required) plus **at most one** inner accent on a single word elsewhere.
Three regions dilute the signal and the eye no longer knows where to land.
Default to one region; reach for the second only when a genuine tension word
earns it.

### The tier system

#### Tier 1 — always the punch

The **topic noun** the viewer doesn't know yet but wants to. This is the word
the viewer is choosing the video for, and it is searchable. It goes on the
`.punch accent` row.

Examples: `INDEXES`, `COMPRESSION`, `HASHING`, `JAVASCRIPT`, `RENDERING`.

If you mark only one accent region per thumbnail, this is it.

#### Tier 2 — the optional second region

The **verb or adjective creating tension** with the topic noun. The pair is
what makes the eye land on two accent words that don't normally go together —
that mismatch is the curiosity gap. When you take the second region, apply it
as an **inner accent** (not a second punch row — there is only one punch row).

Examples:
- `MOUSE` (punch noun) + `SECURES` (tension verb, inner accent)
- `RENDERING` (punch noun) + `INSANELY DIFFICULT` (tension adjective, inner)
- `HASHING` (punch noun) + `MUST BE SLOW` (counterintuitive verb, inner)

#### Tier 3 — never accent

Connectors carry no curiosity weight; accenting them wastes the cap and the
contrast.

`IS`, `VS`, `IN`, `BE`, `THE`, `A`, `AN`, `EXPLAINED`, `MUST`, `WHY`, `HOW`,
`WHAT`, `YOUR`, `YOU`.

### The three placement patterns

Pick the one that fits the wording. The three variants in a round may use
different patterns — that is part of the variation.

#### Pattern A — Topic-only (the safe default)

One region: the topic noun on the punch row, everything else white. Use when
the wording has no clear tension verb/adjective.

`DATABASE / INDEXES / EXPLAINED` → punch: `INDEXES`.

#### Pattern B — Contrast-pair

Two regions across an X-VS-Y comparison: the punch row carries one side, an
inner accent marks the other. The connector `VS` stays white. Implicit fight.

`AUTO-INCREMENT / VS UUID / EXPLAINED` → punch: `AUTO-INCREMENT`, inner: `UUID`.

#### Pattern C — Tension-pair (strongest)

Two regions: the topic noun on the punch row + the surprising verb/adjective
as an inner accent. The eye lands on two accent words that don't belong
together.

`WHY YOUR MOUSE / SECURES THE / INTERNET` → punch: `MOUSE`, inner: `SECURES`.

### Per-variant defaults

- **Variant A** (direct upgrade text): Pattern A or C, whichever fits.
- **Variant B** (sweeping reframe text): Pattern C — the sweeping verb is
  exactly the tension word that earns the second region.
- **Variant C** (punchy declarative text): Pattern A or C.

If a variant has no obvious tension word, fall back to Pattern A. Never force
Tier 2 onto a connector.

### When in doubt

Mark only the topic noun (Tier 1, Pattern A). Under-using the accent is
recoverable next round; over-using it dilutes the brand.

---

## Part 2 — Hue: which palette color the thumbnail uses

The hue is set with **one class on `.thumbnail`**. The accent color, the
mono-tell `.stat`, the `.punch accent` row, and every inline-SVG annotation
(stroke inherits `var(--accent)`) all pick it up. One class, whole-thumbnail.

### The palette

| Class | Hue | Hex | Reach for it when |
|---|---|---|---|
| `acc-teal` | electric teal | `#19E3C2` | **DEFAULT.** Engineered/precise neutral; unclaimed in the doom lane. |
| `acc-cyan` | cyan | `#34C3FF` | Cool, clean, "signal/data" topics; networking, protocols, the web. |
| `acc-violet` | violet | `#8A7BFF` | Premium/abstract/theory; AI, compilers, type systems, "deep" topics. |
| `acc-amber` | amber | `#F5A524` | Warm reveal/wonder; "finally understand," money/payoff, optimism. |
| `acc-slate` | slate-blue | `#5B8DEF` | Calm authority; infra, databases, systems design, sober explainers. |
| `acc-lime` | lime | `#B6F23A` | Energetic/growth/go; speed, performance wins, "it just works." |
| `acc-red` | red | `#FF4D4D` | **Sparingly** — emotionally-red beats only (see below). |

### Default to teal

When the topic gives no strong emotional signal, use `acc-teal`. It is the
locked default, it reads as "engineered/precise" rather than "alarm," and it
is the hue the corpus found genuinely unclaimed in the dark-base lane.

### Pick by topic and emotion

Match the hue to the beat the title is selling, using the table above. The
choice is about register, not literal subject color:

- A calm systems-design explainer → `acc-slate` (authority), not lime.
- "Why is X suddenly everywhere" wonder/reveal → `acc-amber`.
- A protocol/networking deep-dive → `acc-cyan`.
- AI / compiler / type-theory abstraction → `acc-violet`.
- A raw performance-win or speed topic → `acc-lime`.
- Anything ambiguous → `acc-teal`.

One hue per thumbnail. Do not mix palette classes within a round unless the
three variants are deliberately testing different emotional framings — and
even then, hold the hue constant per variant.

### The red-sparingly rule

Red is **fully available** in the palette but is the niche's **most-saturated
accent**. The corpus read (`research/.../ANALYSIS.md` §2 *Color* and §5) is
unambiguous: a hot coral/red recolored word appears on **7 of 11 channels**
(awesome-coding, fireship, shadeofcode, codehead, technetiumm, koala,
devforge) and is the exact palette of Pawel's rejected reference signature.
A red accent on dark therefore **collides with the densest part of the field**
and reads as generic doom-lane "alarm."

So:

- **Reserve `acc-red` for emotionally-red beats** — *worst*, *danger*,
  *broken*, *anger*, *the thing that kills X*. When the title genuinely sells
  a red emotion, red is the honest choice and it earns its saturation.
- **For everything else, default to the cooler/unclaimed hues** (teal, cyan,
  violet, slate) for maximum contrast against competitors. Cool-on-near-black
  is where the white space is.

Because the brand identity lives in base + mono-tell + layout + pointer — not
in the hue — varying the color costs nothing and buys differentiation. Spend
that freedom on contrast, not on joining the red cluster.

### Warm-subject note (face composites)

When the thumbnail has a warm/blonde subject and uses `.thumbnail.warm`
(which kills the glow disc), the chosen accent still drives the type and
annotations normally — `.warm` only affects the face glow, never the hue
class. Pick the hue by topic/emotion as above; a cool accent (teal/cyan)
reads cleanly against a warm face and reinforces the cool-vs-warm contrast.

### When in doubt

`acc-teal`. It is the default for a reason: unclaimed, precise, and the safest
high-contrast read against the saturated red field.
