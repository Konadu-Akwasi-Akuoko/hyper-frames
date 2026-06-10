# Annotation kit — the precision grammar

The Specimen signature carries ONE annotation device family: a unified
**inline-SVG kit** that draws clean, engineered marks in the accent hue. This
is the corpus's deliberate zag. The dev/coding lane's single most-overused
accent is the **hand-drawn scribble marker arrow** (awesome-coding, Cleo,
codehead, devforge, fireship all lean on it). A *precision* mark reads as the
opposite — measured, authoritative, code-native — and is open white space.

Two hard prohibitions, no exceptions:

- **NO hand-drawn scribble arrows.** No wobbly marker strokes, no Excalifont
  doodles, no sketchy arrowheads. Every line in this kit is geometrically
  clean.
- **NO leader-line library.** The old `leader-line` JS dependency is dropped.
  Annotations are static inline SVG authored by hand against the coord grid.
  Nothing computes endpoints at runtime.

An annotation is **optional**. Most variants ship with none — the headline +
mono-tell + face carry the thumbnail. Add a mark only when it does real work:
pointing the eye at the face's emotion, bracketing a stat, ringing one element.
A redundant flourish is worth less than the clean negative field it occupies.
When in doubt, omit it.

## The container contract (locked)

Every annotation is one absolutely-positioned `<div class="anno">` holding one
inline `<svg>`. The CSS (`templates/styles.css`) locks the behavior — do not
restate it inline:

```css
.anno { position: absolute; z-index: 4; pointer-events: none; }
.anno svg { overflow: visible; stroke: var(--accent); fill: none;
            stroke-linecap: round; stroke-linejoin: round; }
.anno svg .filled { fill: var(--accent); stroke: none; }
.anno .anno-label { font-family: 'JetBrains Mono', monospace; font-weight: 700;
                    color: var(--accent); font-size: 26px; ... }
```

What this means for your markup:

- **Stroke inherits `var(--accent)`.** NEVER hardcode a hex (`stroke="#19E3C2"`).
  The accent hue is the one per-video brand variable, set by the `acc-*` class
  on `.thumbnail`. Hardcoding breaks the palette swap and a localization
  re-render. Leave `stroke`/`fill` off the SVG elements entirely and let the
  cascade supply them.
- **Solid bits use `class="filled"`** — a node dot, an arrowhead, a filled
  caret. `.filled` overrides to `fill: var(--accent); stroke: none`. Open bits
  (lines, rings, brackets) stay stroke-only; do not add `fill`.
- **`overflow: visible` is set on the SVG**, so stroke can extend past the
  `width`/`height` box. Keep a small SVG and let geometry spill, or size the
  SVG to the mark — either works.
- **`z-index: 4`** sits the anno above the face (`z-index: 2`) and chip
  (`z-index: 3`), below the vignette and grid overlay. Don't override it.
- **`pointer-events: none`** — annotations never intercept anything; harmless,
  leave it.
- Position the whole mark with `style="left:..;top:..;"` on the `.anno` div, in
  **canvas pixels** (1280×720 horizontal, 1080×1920 vertical). All internal
  SVG coordinates are then relative to that origin.

Everything lives **inside `.thumbnail`** (the `ANNOTATION_SVG` token in
`variant.html` mounts there), so the mark scales with the thumbnail at every
preview size and renders deterministically.

## Workflow — place endpoints off the coord grid

Never eyeball coordinates. Read them.

1. **Turn on the grid.** Open the variant with `?grid` (e.g.
   `a.html?grid`). The `.with-grid` overlay draws a 20px-minor / 100px-major
   graph with **numbered x/y axis labels** and a red dashed title-safe border
   (60px inset). The renderer strips query params, so the grid is NEVER in the
   final PNG.
2. **Read the target (x, y).** Find the pixel you want the mark to touch — the
   corner of the face's eye, the edge of a stat, the top of the headline.
   Read its coordinates straight off the numbered axes.
3. **Read the anchor (x, y).** Where the mark *originates* — usually open
   negative field near the headline.
4. **Set the `.anno` origin** to the anchor: `style="left:<x>px;top:<y>px;"`.
5. **Set the internal SVG coordinates** so the mark's far endpoint lands on the
   target, computed relative to the anchor origin (target − anchor).
6. **Re-open with `?grid`** to verify the endpoint sits exactly on the target,
   then without `?grid` to confirm the mark reads on its own.

Keep marks inside the **title-safe border** unless they intentionally touch the
bled face. Endpoints that land on empty background read as broken — the bucket-B
QA fails an arrow that stops in dead space, and so should you.

### The `data-anchor` auto-draw helper (concept)

For repeatable targeting you may place an **invisible anchor** at the target
and let a small init helper wire the pointer to it, instead of hand-computing
the delta:

- Drop a zero-size marker at the target read off the grid, e.g.
  `<div class="anno-anchor" data-anchor="eye" style="left:980px;top:300px;"></div>`.
- Give the pointer's `.anno` a `data-anchor="eye"` reference. A tiny inline
  script (mirrors the `cg-init` axis-label snippet in `variant.html`) reads the
  two element positions and sets the SVG line's far endpoint to the anchor's
  coordinates at load.
- This is a **convenience for the authoring/preview pass only** — it computes
  static endpoints once, NOT a runtime leader-line. The marker has zero size
  and no paint, so it never appears in the PNG. If you don't wire the helper,
  hand-set the endpoint per step 5 above; both produce the same static SVG.

Prefer the hand-set path for one-off marks; reach for `data-anchor` when a
target (e.g. the face's eye-line) recurs across all three variants in a round.

## The primitives

All snippets below assume `stroke`/`fill` come from the cascade. Coordinates
are illustrative — recompute every one against the grid. Each goes in the
`ANNOTATION_SVG` token slot.

### 1. Precision pointer (line + right-angle elbow + node)

The workhorse. A straight run, a clean right-angle elbow, and a terminal
**node** that lands on the target. Replaces the scribble arrow entirely. The
elbow is what reads as "engineered" — no diagonal-only freehand strokes.

Node as an **open ring** (points without obscuring):

```html
<div class="anno" style="left:760px;top:300px;">
  <svg width="220" height="120" viewBox="0 0 220 120">
    <path d="M0 0 H140 V96" fill="none" stroke-width="4"/>
    <circle class="filled" cx="140" cy="108" r="7"/>
  </svg>
</div>
```

Node as a **filled dot** (use when you want a harder landing):

```html
<div class="anno" style="left:760px;top:300px;">
  <svg width="220" height="120" viewBox="0 0 220 120">
    <path d="M0 0 H140 V96" fill="none" stroke-width="4"/>
    <circle class="filled" cx="140" cy="100" r="9"/>
  </svg>
</div>
```

The elbow direction is yours: `H…V…` (across then down) or `V…H…` (down then
across). Aim the run from negative field toward the target; let the final
segment meet the node at a right angle. The node is the only `.filled` element.

### 2. Bracket

A measured square bracket spanning a region — wraps a stat, a row of the
headline, or one edge of the face. Cleo's "12.2 KM" callout energy, as a
repeatable mark. Stroke-only, no fill.

```html
<div class="anno" style="left:120px;top:430px;">
  <svg width="60" height="180" viewBox="0 0 60 180">
    <path d="M44 0 H8 V180 H44" fill="none" stroke-width="4"/>
  </svg>
</div>
```

Rotate the path (`H`/`V` swapped) for a horizontal bracket over/under a row.
Keep the return tics short and equal so it reads as a bracket, not a frame.

### 3. Ring / circle

Encircles one element — a number, a logo, a single word — to single it out.
Always stroke-only and **open**; a filled ring obscures what it marks. Pair
sparingly with a pointer; usually the ring alone is enough.

```html
<div class="anno" style="left:540px;top:250px;">
  <svg width="160" height="160" viewBox="0 0 160 160">
    <circle cx="80" cy="80" r="74" fill="none" stroke-width="4"/>
  </svg>
</div>
```

Use an `<ellipse>` instead of `<circle>` when the target is wider than tall (a
multi-character stat). Keep one full clean revolution — no double-loop scribble
(that is the banned hand-drawn device).

### 4. Underline / caret

Sits under one word or stat to assert it — the precision substitute for a
recolor. Two forms: a flat underline rule, or a small filled caret (the
code-native cursor tell) tucked beneath.

Underline rule:

```html
<div class="anno" style="left:300px;top:392px;">
  <svg width="280" height="24" viewBox="0 0 280 24">
    <path d="M0 8 H280" fill="none" stroke-width="5"/>
  </svg>
</div>
```

Caret (filled — the one `.filled` element):

```html
<div class="anno" style="left:300px;top:392px;">
  <svg width="40" height="28" viewBox="0 0 40 28">
    <path class="filled" d="M20 4 L36 26 H4 Z"/>
  </svg>
</div>
```

Reserve underline/caret for a single word; underlining a whole row competes
with the headline weight.

### 5. Callout (pointer + a mono `.anno-label`)

A pointer that terminates in a short **JetBrains Mono** label — a measured
tag, a count, a one-word verdict. The label is a sibling `<div class="anno-label">`
inside the same `.anno`; it inherits the accent color and 26px mono styling
from the locked CSS. Keep the label terse (1–3 words or one number); it is a
tag, not a sentence.

```html
<div class="anno" style="left:700px;top:260px;">
  <svg width="170" height="90" viewBox="0 0 170 90" style="display:block;">
    <path d="M0 84 V20 H150" fill="none" stroke-width="4"/>
    <circle class="filled" cx="156" cy="20" r="6"/>
  </svg>
  <div class="anno-label" style="position:absolute;left:0;top:96px;">100% CPU</div>
</div>
```

Position the `.anno-label` relative to the `.anno` origin (absolute `left`/`top`
in px). The mono label is what makes a callout read as instrument readout
rather than decoration — it rhymes with the headline's `.mono-tell` line.

## Composition rules

- **At most ONE annotation per thumbnail.** Two marks fight for the eye and
  re-introduce the clutter the floor channels lose to. One precise mark beats
  three.
- **Point at meaning, not decoration.** The pointer lands on the face's
  emotion or the headline's claim; the bracket/ring isolates the stat. Marks
  that touch empty field read as broken.
- **Never recolor — annotate.** The 2-tone is the punch row's job. Use a ring
  or underline to single out a word, not a second accent hue. The accent is a
  palette of exactly one per video.
- **Keep stroke-width consistent** (4–5px at 1280×720; scale up proportionally
  for the 1080×1920 canvas) so the kit reads as one grammar across the channel.
- **The mark inherits the hue.** Because everything is `var(--accent)`, a single
  annotation works for every accent in the palette — author once, swap the
  `acc-*` class freely.

## Vertical mode

The kit is canvas-agnostic — same container, same primitives, same inheritance.
Only the numbers change: place against the 1080×1920 grid, mind the TikTok
bottom-UI band and the profile-grid 1:1 crop markers the `?grid` overlay draws,
and scale stroke-width up. See `reference/vertical-mode.md` for the safe-zone
geometry.
