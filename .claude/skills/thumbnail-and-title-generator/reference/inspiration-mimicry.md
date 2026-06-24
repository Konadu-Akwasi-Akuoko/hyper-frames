# Inspiration mimicry — pick a proven layout, rebuild it with our content

This is the spine of the generator. We do **not** design a thumbnail from a blank
canvas. For every variant we pick a real, high-performing thumbnail from the
`thumbnailInspo/` library, read its composition off a measuring grid, and rebuild
that *same composition* with OUR content. Same skeleton, our flesh.

## What we copy vs. what we swap (read this twice)

**Copy the COMPOSITION (the skeleton):**
- the archetype (face-reaction / big-text / comparison-vs / iceberg / tier-ranking / …)
- where each element sits — face zone, headline zone + baseline, stat/badge slot,
  device (big number, red circle, arrow, vs-bolt) and its position
- the size hierarchy (what dominates, what's secondary) and the reading path
- the contrast move that stops the scroll (one bright element on dark, a face's
  emotion, a giant numeral, a strike-through)

**Swap ALL the content (the flesh):**
- our headline text and our paired title
- our accent hue from the Specimen palette (never their exact colors verbatim)
- our face still (user-supplied + credited) — never their face or their artwork
- our icons / logos / stat / objects — sourced or drawn by us
- the Specimen type voice (Inter 900 caps + JetBrains Mono tell) and the
  precision annotation kit (never a hand-scribbled arrow)

**Never copy the literal pixels.** We are lifting a *layout pattern* — a public,
uncopyrightable arrangement — not their image. Reproducing their face, their
screenshot, their logo art, or their exact text is off-limits. If a reference's
power is entirely its specific copyrighted still, pick a different reference whose
power is its *composition*.

## Relationship to the Specimen signature

The chosen reference drives the **composition**; the Specimen signature
(`reference/specimen-signature.md` + `templates/styles.css`) supplies the
**style vocabulary** that keeps every thumbnail recognizably ours:

| From the reference (per video) | From the Specimen signature (constant) |
|---|---|
| layout / archetype / element positions | Inter 900 UPPERCASE headline + 2-tone (white + one punch row) |
| which device stops the scroll + where | JetBrains Mono `// tell` with a concrete stat |
| size hierarchy + reading path | accent **palette** (`acc-*`), red reserved |
| whether a face is present + which side | green-tinted near-black base + ambient grid |
| | precision inline-SVG annotation kit (no scribbles) |
| | face compositing: defringe/despill + rim-light + bleed |

So a reference that is `face-left, giant-number, danger-red` becomes: our face
bled on the **left** (overriding the signature's default right), a giant numeral
where theirs sits, our headline in Inter 900 in their headline zone, `acc-red`
because the beat is genuinely red — but rendered in OUR type, OUR palette value,
OUR mono tell. It reads as ours and as a proven layout at once.

## The same principle applies to the title

The reference drives the **title shape** the same way it drives the layout: we copy
the *shape* (the skeleton — `speed-primer`, `comparison-vs`, `assumption-flip`, …)
and swap the *words* (the flesh — our noun, our claim). The reference's real title,
catalogued as `title_shape` + `title_pattern`, is a worked example of the
claim/ground split, not a script to copy. See `title-engine.md` →
"Reference title shape — a prior, not a mandate" for how strongly it binds.

## Step-by-step

### 1. Pick the reference(s)

Open `thumbnailInspo/README.md` and scan the **Quick index** table only. Match
each variant's beat/emotion to a row by `archetype` + `device` + `mimic-for`:

- Default: **three variants → three references**, deliberately different
  archetypes, so the round gives the user genuinely different directions (e.g. a
  face-reaction, a giant-number stat, a comparison-vs). This mirrors the
  three-directions rule.
- If the user asks for variations on one idea, pick **one** reference and vary the
  headline/accent/face across a/b/c instead.
- Vertical (Shorts) mode: prefer references whose `channel` is a shorts source or
  whose layout survives a 9:16 crop (centered-stack, face-bottom, big-text).

Print the picks before building, one line each:
`A ← thumbnailInspo/<channel>/<file> (<slug>): <archetype>/<device> — why it fits.`

### 2. Grid the reference and read the positions

For each picked reference, overlay the measuring grid:

```bash
python3 tools/thumbnail-inspo/grid.py thumbnailInspo/<channel>/<file>.jpg \
  --out thumbnails/round-N/ref/<letter>.grid.png
```

`Read` the gridded PNG. It stamps a numbered 4x4 cell grid (cells 1-4 top row
left→right, 5-8, 9-12, 13-16) plus pixel rulers along the top (x) and left (y).
Read off, in the **same 1280×720 space our templates use**:

- face/object box: which cells, center (x, y), how much of the frame it fills
- headline: which cells, top-left (x, y), baseline y, row count, which word pops
- device/stat/badge: position (x, y) and size
- background treatment and any secondary elements

Cross-check what you read against that entry's `Layout map:` line in the README —
they should agree; trust your eyes on the grid for the exact numbers.

> The reference is most images at 1280×720 (horizontal) — a 1:1 coordinate match.
> If a reference is a different size (a vertical Short), the rulers show its real
> dimensions; scale the fractions to our canvas (multiply by our-width/their-width).

### 3. Rebuild the layout with our content

Author each variant's `.thumbnail` inner HTML to land OUR elements at the
positions you read, using the Specimen classes as building blocks and **inline
`style="left/top/right/…"` overrides** where the reference's layout differs from
the CSS defaults:

- **Headline** — keep `<span class="thumbnail-row">` rows (contract) and the
  `punch accent` row (2-tone). Override `.thumbnail-text` position via inline
  style to match the reference's headline zone (`left`, `top`/`bottom`,
  `right`, `text-align`). Size so the longest row fits its zone — rewrite shorter
  before you overflow.
- **Face** — if the reference has a face, place `.face-wrap` on the reference's
  side via inline style (override the default `right`); add `warm` for
  warm/blonde subjects. If the reference has **no** face (logo-grid, object-hero,
  code-screenshot, diagram), omit the face entirely — do not force one in.
- **Device** — reproduce the scroll-stopper with a signature primitive at the
  reference's coordinates: a giant numeral as a bespoke absolutely-positioned
  `div`; a ring/pointer/bracket from the annotation kit; a `.chip` badge; the
  mono `.stat`. Use `acc-red` only when the device is genuinely a danger/worst beat.
- **Secondary elements** (logo tiles, code window, before/after split) — build
  them as simple absolutely-positioned blocks at their cells; fill with OUR icons
  (Iconify via `tools/thumbnail-render`) or screenshots we own.

Place against OUR `?grid` overlay the same way you read theirs: append `?grid` to
the variant URL, confirm each element's (x, y) matches the reference's, adjust.

### 4. Verify the resemblance

In the Step 8 QA loop, add one check: **put our rendered PNG next to the
reference's grid** and confirm the *composition* matches (positions, hierarchy,
device, reading path) even though every pixel of content is ours. If it doesn't
read as the same layout family, the mimicry failed — re-place, don't ship.

## Anti-patterns

- ❌ Designing a layout from scratch / ignoring the library. Every variant cites a
  reference — this is mandatory, not a quota you can skip.
- ❌ Copying the reference's face, screenshot, logo art, or exact text. We lift the
  arrangement and fill it with our own content.
- ❌ Forcing the Specimen face-right silhouette onto a reference that is face-left,
  centered, or faceless. The reference's composition wins; the signature is the
  type/color/annotation voice, not a fixed silhouette.
- ❌ Eyeballing positions. Grid the reference, read the numbers, place against our
  own grid.
- ❌ Picking three references that are the same archetype. Spread the three across
  different directions so the round is a real choice.
