# Accent-word recipes

Rules for picking which words get the accent color (`#FFB627` amber).
Drawn from `research/pawel-code-stuff/analysis/thumbnail-patterns.md` §5.

(The research file calls these "red words" because Pawel uses red. Our
accent is amber. Same rules apply — same tier system, same cap.)

## The cap

**Maximum 2 accent regions per thumbnail.** Three would dilute the signal
and make the eye not know where to land.

## The tier system

### Tier 1 — always accent

The **topic noun** the viewer doesn't know yet but wants to. This is the
word the viewer is choosing the video for.

Examples: `INDEXES`, `COMPRESSION`, `HASHING`, `MOUSE`, `RENDERING`.

If you only mark one accent region per thumbnail, mark this one.

### Tier 2 — often accent (the second region)

The **verb or adjective creating tension** with the topic noun. This pair
is what makes the viewer's eye land on TWO accent words that don't
normally go together — and that mismatch is the curiosity gap.

Examples:
- `MOUSE` (noun) + `SECURES` (surprising verb)
- `RENDERING` (noun) + `INSANELY DIFFICULT` (surprising adjective)
- `PASSWORD HASHING` (noun) + `MUST BE SLOW` (counterintuitive verb)

### Tier 3 — never accent

Connectors. They carry no curiosity weight; accenting them wastes the cap.

`IS`, `VS`, `IN`, `BE`, `THE`, `A`, `AN`, `EXPLAINED`, `MUST`, `WHY`,
`HOW`, `WHAT`, `YOUR`, `YOU`.

## The three sub-patterns

Pick the pattern that fits the thumbnail's wording:

### Sub-pattern A — Topic-only

One accent region: just the topic noun. The safe default. Use when the
title doesn't have a clear tension verb/adjective.

**Example:** `DATABASE / INDEXES / EXPLAINED`
- accent: `INDEXES`

### Sub-pattern B — Contrast-pair

Two accent regions: both sides of an X-VS-Y comparison. The connector
"VS" stays in the text color. Implicit fight.

**Example:** `AUTO-INCREMENT / VS UUID / EXPLAINED`
- accent: `AUTO-INCREMENT`, `UUID`

### Sub-pattern C — Tension-pair (strongest)

Two accent regions: the topic noun + the surprising verb/adjective. The
viewer's eye lands on two accent words that don't normally go together.

**Example:** `WHY YOUR MOUSE / SECURES THE / INTERNET`
- accent: `MOUSE`, `SECURES`

## How to pick the pattern per variant

The 3 variants in a round can use different sub-patterns — that's part of
the variation. Suggested defaults:

- **Variant A** (direct upgrade text): sub-pattern A or C, whichever fits.
- **Variant B** (sweeping reframe text): sub-pattern C — the sweeping
  verb is exactly the tension word that earns accent.
- **Variant C** (punchy declarative text): sub-pattern A or C.

If a variant has no obvious tension verb/adjective, fall back to
sub-pattern A. Don't force tier 2 onto a connector word.

## When in doubt

Mark only the topic noun (tier 1, sub-pattern A). Under-using accent is
recoverable in the next round; over-using it dilutes the brand.
