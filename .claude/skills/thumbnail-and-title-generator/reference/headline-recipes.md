# Headline recipes

Patterns for turning a video's working title into a **Specimen** headline. The
headline is **not** the video title — it's a bolder rewrite that wins the click.
The paired YouTube title carries the SEO nouns (see
`reference/title-engine.md`); the headline detonates in the feed.

The Specimen headline has three parts:

1. **White flanking row(s)** — the setup, in white.
2. **ONE accent "punch" row** — the payoff word, bigger (`.punch`) and recolored
   to the per-video `--accent` hue.
3. **A mono `// tell`** — a JetBrains Mono line under the headline that carries a
   concrete stat/number. This is the code-native signal the corpus found
   genuinely unclaimed.

Drawn from `research/thumbnail-title-corpus-2026-06-09/ANALYSIS.md` (the title
engine §3 + the Specimen direction §4-A) and the Bucket-B compositing playbook
in `learnings/bucket-b-thumbnails.md`.

## Hard constraints (every variant must satisfy)

- **ALL CAPS** for the headline. Always.
- **2 to 4 headline rows**: one or more white flanking rows + exactly ONE accent
  punch row. (Vertical Variant B may stack to 4-5 rows; vertical Variant C adds a
  kicker — see `reference/vertical-mode.md`.)
- **One accent punch row, never zero, never two.** The accent is a single ROW
  CLASS (`punch accent`), not an inner span. Localization re-fills the row text,
  so the accent must live on the row.
- **The longest effective row must fit the ~738px left column** with the face
  cleared on the right (the `.thumbnail-text` block runs `left:72px` to
  `right:470px` on the 1280px canvas). The renderer does NOT silently shrink to
  fit. If a row overflows, **reject and rewrite shorter** — never let overflow
  hide. See "Sizing" below.
- **No question marks, ellipses, colons, parentheses.**
- **No adverbs except in upgrade position** ("INSANELY", "BRUTAL",
  "CATASTROPHIC") — never as a hedge ("usually", "sort of").
- **The mono tell carries a concrete number when one exists** — a percentage, a
  count, a year, a dollar figure. The stat is a searchable/authority signal, not
  decoration.

## The direction triad

Each round produces three headlines that differ on **direction**, not just word
choice — otherwise the user can't make a real choice. The triad carries over from
the old text-only signature; the punch row + mono tell are the Specimen layer on
top.

1. **Variant A — direct upgrade.** Keep the working title's topic noun
   front-and-center; harden the framing. Punch row = the topic noun. Lowest-risk
   variant — anchors search intent.
2. **Variant B — sweeping reframe.** Trade the narrow claim for the bigger one
   ("generates secure keys" → "secures the internet"). Punch row = the
   reframed-stakes word. Highest-claim variant.
3. **Variant C — punchy declarative.** Shortest wording; drop the question and
   assert the surprising fact. Punch row = the tension verb or the surprising
   payoff. Highest-contrast, fewest words.

If the user says "all three feel safe", harden the upgrade (escalate the
adjective, sharpen the punch word) across all three. If "all three are too
aggressive", soften — drop the upgrade adverb, return to the topic noun in the
punch row.

## The rephrase moves (feed the triad)

- **Softer → harder.** "is intentionally" → "must"; "can be" → "is"; "how to
  make X" → imperative "make X"; "why X is Y" (question) → "X is Y"
  (declarative).
- **Question → declarative.** Drop the question mark; assert the answer.
- **Narrow → sweeping** (Variant B's engine). "generates secure keys" → "secures
  the internet"; "fixes a bug" → "saves your database".
- **Adjective upgrade.** "complicated" → "insanely difficult"; "fast" → "brutal";
  "important" → "catastrophic". One upgrade per headline — never stack them.

## Pick the punch word

The punch row is the single biggest element on the thumbnail. It is exactly ONE
row (`<span class="thumbnail-row punch accent">`), bigger than the white rows and
in the accent hue. Choose what goes in it:

- **The topic noun** — when the noun *is* the hook and you want maximum search
  legibility (Variant A's default). `JAVASCRIPT`, `POSTGRES`, `RENDERING`.
- **The tension verb** — when a verb creates the surprise against the setup
  (Variant C's default). `WON`, `LYING`, `SECURES`, `FAILS`.

Pick the one word a viewer would remember after a half-second glance. The flanking
white rows are the setup; the punch row is the thing they screenshot. One punch
word, never a phrase — if the payoff needs two words, the headline is too long.

**Reserve the accent hue for the punch row only.** The accent is the per-video
brand variable (default `acc-teal`; the full palette lives in
`reference/specimen-signature.md`). If a beat is genuinely emotionally-red
(worst/danger/anger), `acc-red` is available — but it is the niche's most
saturated accent, so default to a cooler unclaimed hue for contrast against
competitors. The hue does not change the punch-word logic.

## Searchable-noun discipline

The corpus title engine is blunt: **winners name one concrete, searchable noun;
floors trade the noun for a vague mood.** The headline must keep the topic noun
present — usually in the punch row (Variant A) or a flanking row (Variants B/C
when the punch is a verb). Test: *if a viewer searched the one noun in this
headline, would the video be a satisfying result?* If no, the noun is too vague
("coding", "tech", "stuff") — replace it with the specific one ("JavaScript",
"Postgres", "$10M").

The sweeping reframe (Variant B) is allowed to *generalize the stakes*
("internet", "your database") but must still carry the searchable noun somewhere
in the rows — never drop it for pure vibe.

## The mono tell

Under the headline sits a JetBrains Mono line (`.mono-tell`, `font-size: 0.42em`
relative to the headline base):

```html
<div class="mono-tell">// <span class="stat">98.8%</span> of all websites</div>
```

- **Lead with `//`** — the comment marker is the code-native tell.
- **Carry a concrete number** in `<span class="stat">` (recolored to the accent)
  whenever the topic has one — a percentage, count, year, dollar figure, or
  benchmark. The number is the authority signal; it is what makes the tell more
  than flavor.
- **Keep it one short clause.** It reads as a footnote, not a second headline.
  `.mono-tell` is `white-space: nowrap`, so a long tell will overrun the column —
  keep it well inside the ~738px width.
- **Omit it** (set `MONO_TELL` to `""`) only when the topic has no honest
  number and no crisp factual clause. A weak tell is worse than none.

Mine the stat from `script.md` or `seo/research.json` — never invent one. If the
number is approximate or disputed (e.g. a "40B/day" style claim), verify it
before it ships as authority.

## Sizing

`ROW_FONT_SIZE_PX` sets the **flanking** white-row size on `.thumbnail-text`. The
two derived sizes follow from it:

- `.punch` row = **1.7em** (≈ 1.7 × the flanking size) — the dominant element.
- `.mono-tell` = **0.42em** — the footnote.

Because the punch row is the largest, it is almost always the row that decides
whether the headline fits. Procedure:

1. Draft the rows. Identify the longest **effective** row at its rendered size —
   usually the punch row at 1.7em, but check a long flanking row too.
2. Size so that longest row fits inside ~738px with margin. Inter 900 is
   proportional (not monospace), so confirm fit by rendering with `?grid` and
   reading the coordinate overlay — do not trust a character count alone.
3. If the punch row won't fit at a legible flanking size, **rewrite the punch
   word shorter** (or move the long word to a flanking row and punch a shorter
   one). Shortening beats shrinking — small text loses at ~210px feed size, which
   is the size that matters.

Never let the renderer hide overflow. Preview-vs-output drift is the worst
failure mode: what overflows in the round HTML overflows in the PNG.

## Worked examples

### Example 1 — text rendering

Working title: *Why is rendering text so complicated?*

- **A (direct):** white `WHY TEXT` / punch+accent `RENDERING` / white `IS A FIGHT`
  · tell `// 1,114 scripts in Unicode`
- **B (sweeping):** white `A LETTER ON` / white `YOUR SCREEN IS` / punch+accent
  `A BATTLE` · tell `// 100,000+ glyphs to place`
- **C (punchy):** white `YOUR FONT IS` / punch+accent `LYING` / white `TO YOUR EYES`
  · tell `// 0 pixels are where you think`

### Example 2 — JavaScript dominance

Working title: *Why you can't escape JavaScript anymore*

- **A (direct):** white `YOU CAN'T ESCAPE` / punch+accent `JAVASCRIPT` ·
  tell `// <span class="stat">98.8%</span> of all websites`
- **B (sweeping):** white `ONE LANGUAGE` / white `QUIETLY RUNS` / punch+accent
  `THE WEB` · tell `// built in 10 days, 1995`
- **C (punchy):** white `THE WORST LANGUAGE` / punch+accent `WON` ·
  tell `// <span class="stat">98.8%</span> of all websites`

  Here `acc-red` is defensible — "worst" is an emotionally-red beat. Default the
  other two variants to a cooler hue for contrast.

### Example 3 — mouse entropy

Working title: *Why moving your mouse generates secure keys*

- **A (direct):** white `YOUR MOUSE` / punch+accent `GENERATES` / white `SECURE KEYS`
  · tell `// 256 bits from your jitter`
- **B (sweeping):** white `WHY YOUR MOUSE` / punch+accent `SECURES` / white `THE INTERNET`
  · tell `// every TLS handshake needs it`
- **C (punchy):** white `MOVE YOUR MOUSE` / white `OR THE INTERNET` / punch+accent
  `FAILS` · tell `// 0 entropy = 0 security`

## Anti-patterns

- **No accent punch row, or two of them.** Exactly one. The white rows set up;
  the single accent row pays off.
- **Accent on an inner `<span>` instead of the row.** Breaks localization
  (`create-srt localize_thumbnails.py` re-fills row text). Accent is a ROW CLASS.
- **A punch *phrase* instead of a punch word.** If the payoff needs two words,
  the headline is too long — shorten it.
- **A mono tell with no number and no crisp fact.** Omit it rather than ship
  filler. Inventing a stat is worse than omitting the tell.
- **"TOPIC EXPLAINED IN N MINUTES."** The formula pattern — wins on SEO-heavy
  broad nouns but loses engagement. Reserve as the fallback when the user asks
  for "something safer."
- **Stacked adjectives** ("INSANELY DIFFICULT IMPOSSIBLE") — pick one.
- **Filler** ("ACTUALLY", "REALLY", "BASICALLY") and **hedges** ("MAYBE",
  "MIGHT", "PROBABLY") — cut them all.
- **Dropping the searchable noun for a vague mood** — the corpus floor. Keep one
  concrete noun a viewer could search.
