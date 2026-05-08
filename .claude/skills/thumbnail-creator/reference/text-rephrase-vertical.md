# Text rephrase recipes — vertical (Shorts / TikTok)

Loaded by the thumbnail-creator skill at Step 3 when in vertical mode.
The horizontal recipes in `text-rephrase-recipes.md` are NOT applied;
this file replaces them. The general direction triad (direct upgrade,
sweeping reframe, punchy declarative) and all hard rules from
`SKILL.md` still apply — only the row count, character budget, and
font-sizing cap differ.

In vertical mode, each variant slot is locked to a fixed rhythm:
A is the wide-recap, B is the stacked-staccato, C is the headline+kicker.
This is on top of the direction differentiation — A still skews "direct
upgrade", B "punchy declarative", C "sweeping reframe".

---

## Shared constraints (apply across A, B, C)

- ALL CAPS only.
- No question marks, ellipses, colons, parentheses, emoji, arrows.
- Max 2 accent regions per variant.
- Same icon across all 3 variants in a round.
- The text column is 920 px wide. The font formula is:
  `floor(920 / (longest_row_chars * 0.6))`, capped at 220, floor at 90.
- A computed font size below 90 px is a hard reject — rephrase shorter.

## Variant A — wide recap

- Rows: exactly 3.
- Words per row: 3-6.
- Chars per row (incl. spaces): 9-14.
- Direction: direct upgrade of the working title.
- Tone: complete phrase; reads top-to-bottom as one sentence with
  comma rhythm.
- Expected dominant font size: 110-135 px.

Worked example — working title "Why text is hard":

```
STOP GUESSING
AT HOW TEXT
GETS RENDERED
```

Accent: `TEXT` (Tier-1 topic noun) on row 2.

## Variant B — stacked staccato

- Rows: 4-5.
- Words per row: 1-2.
- Chars per row: 4-9.
- Direction: punchy declarative reframe; the most tabloid-feeling.
- Tone: poster / sticker. One beat per row. Each row stands alone.
- Expected dominant font size: 150-180 px.

Worked example — working title "Why text is hard":

```
TEXT
IS
HARDER
THAN
YOU THINK
```

Accent: `TEXT` (row 1) and `HARDER` (row 3). Two accent regions cap.

## Variant C — headline + kicker

- Rows: exactly 3.
- Rows 1-2: 1-3 words each, 4-9 chars each. Dominant font 170-220 px.
  (4 chars hits the 220 px cap; 9 chars lands at 170 px. Anything
  shorter still works visually but caps at 220 px so the variant
  doesn't grow unbounded. Anything longer drops into Variant A
  territory.)
- Row 3 (kicker): 3-6 words, 14-18 chars. Rendered at 0.6em of the
  dominant size via the `.kicker` CSS class — the rephrase produces the
  text; the template applies the class.
- Direction: sweeping reframe; the headline carries the emotional claim
  and the kicker grounds it.
- Computed kicker pixel size (0.6 × dominant) must clear the 90 px
  floor; if not, shorten the kicker or drop the row.

Worked example — working title "Why text is hard":

```
TEXT
RENDERING
THE LAYER NOBODY SEES
```

Accent: `RENDERING` (row 2) — the kicker stays unaccented in this case
because its job is to ground, not to emphasize.

Alternative accent: `TEXT` (row 1) + a single word in the kicker
(e.g. `NOBODY`) when the kicker carries the surprise rather than
serving as a quiet anchor. Pick one accent strategy per variant; do
not mix.

## How the three rhythms relate

The user judges the round on which rhythm pulls them in, not just
which words. Don't make the three texts paraphrase the same beat with
different line breaks — that defeats the rhythm differentiation. Each
variant should feel like a different cover for a different audience:

- A reads like an article headline.
- B reads like a TikTok meme cover.
- C reads like a magazine front.
