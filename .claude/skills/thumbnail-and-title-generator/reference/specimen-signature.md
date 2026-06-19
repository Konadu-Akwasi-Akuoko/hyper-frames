# Specimen signature — locked

The channel's thumbnail brand: the **Specimen** face-forward signature. These
constants do not change per video. Changing them is a rebrand exercise, not a
per-video parameter.

The brand identity lives in **base + mono tell + type voice + pointer grammar**.
Exactly one variable is tunable per video: the **accent hue** (a palette, not a
single locked color). These style constants hold.

> **Layout is no longer a fixed constant.** The generator now *replicates the
> composition of a proven thumbnail* picked from `thumbnailInspo/` per variant
> (see `reference/inspiration-mimicry.md`), so the **layout / silhouette is
> reference-driven**, not the single face-right shape this doc originally locked.
> What stays locked is the **style vocabulary** below — the type voice (Inter 900
> 2-tone + JetBrains Mono tell), the accent palette, the green-tinted near-black
> base, the precision annotation kit, and the face compositing recipe. Read the
> "Face — bled to the right" / "face-right layout" notes as the *default* slot the
> token scaffold fills, overridden per variant to match the chosen reference.

If you ever rebrand, re-run the visual-signature design exercise (propose 3
candidate signatures from a fresh corpus read, pick one, update both this file
and `templates/styles.css`). Do not change one constant in isolation — the set
together is what gives the channel its silhouette. See the rebrand process at the
bottom.

## The constants

| Constant | Value |
|---|---|
| Base color | Green-tinted near-black `#0B0E14`; radial top-left `#16201f` → `#0B0E14` → `#05070b`, plus a faint ambient teal grid (`.bg-grid`) and a corner vignette. NOT navy, NOT pure black. |
| Headline font | `Inter`, weight 900 (Black), UPPERCASE |
| Headline treatment | 2-tone: white flanking rows + ONE accent-hued "punch" row, larger. Rows are `<span class="thumbnail-row">`; the punch row adds `punch accent`; the vertical Variant C kicker adds `kicker`. Base size on `.thumbnail-text` is the flanking size; `.punch` is `1.7em`. |
| Mono tell | A JetBrains Mono line under the headline — `// <span class="stat">98.8%</span> of all websites`. Class `.mono-tell`, font-size `0.42em`. The stat is a concrete searchable/authority number. |
| Accent | A PALETTE — the only per-video brand variable. Set via a class on `.thumbnail`. Default `acc-teal`. (Full palette below.) |
| Annotation | A unified inline-SVG kit. `<div class="anno" style="left/top"><svg>…</svg></div>`; SVG stroke inherits `var(--accent)`, solid bits use `class="filled"`. Primitives: precision pointer, bracket, ring, underline, callout. NO scribble arrows, NO leader-line library. |
| Face | A pop-culture/reaction STILL bled to the right: `.face-wrap > .face-glow + img.face`, height `760`, `object-position: bottom right`. The USER supplies + credits the image; WE composite. `.thumbnail.warm` kills the glow disc for warm/blonde subjects. |
| Brand chip | Optional small per-topic badge: `.chip`; override `--chip-bg` / `--chip-ink`. |
| Design aid | Numbered coordinate-grid overlay (`.grid-overlay` shown under `.with-grid` via `?grid`): 20px minor / 100px major + numbered x/y axis labels + a `.grid-safe-area` title-safe border. NEVER in the final PNG. |

### The accent palette

One class on `.thumbnail` selects the hue; it drives `var(--accent)` for the
punch row, the mono `.stat`, and every annotation stroke. Brand identity does
not live in the hue — it lives in base + mono + layout + pointer — so the hue
may vary per video.

| Class | Hue | Hex |
|---|---|---|
| `acc-teal` (default) | electric teal | `#19E3C2` |
| `acc-cyan` | electric cyan | `#34C3FF` |
| `acc-violet` | violet | `#8A7BFF` |
| `acc-amber` | amber | `#F5A524` |
| `acc-slate` | slate-blue | `#5B8DEF` |
| `acc-lime` | lime | `#B6F23A` |
| `acc-red` | red | `#FF4D4D` |

**The red caveat.** Red is fully available, but it is the niche's
most-saturated accent — 7 of 11 corpus channels recolor a word red/orange, and
it is also the rejected Pawel/coral signature. Reserve `acc-red` for
emotionally-red beats (worst / danger / anger). Default to cooler, unclaimed
hues (teal, cyan, violet, slate) for maximum contrast against competitors.

## Why each constant

**Base — green-tinted near-black `#0B0E14`, not navy, not pure black.** The
corpus read found the dark-base lane wall-to-wall: 8 of 11 channels sit on cold
navy or neutral charcoal, and pure black is indistinguishable from every
dark-mode tech channel. A faintly *green* near-black reads as "engineered /
precise / lab" rather than "techbro cyberpunk" or "alarm," and a viewer scanning
a feed of navy and pure-black thumbnails registers the warm-green dark
immediately. The teal grid and vignette add a structured spatial texture (the
corpus's "owned layout grammar" gap) without copying awesome-coding's
literal graph paper.

**Headline — Inter 900, UPPERCASE, 2-tone.** Heavy weight survives at thumbnail
grid size (~210 px wide on the feed), where thinner weights smudge. The 2-tone
(white flanking + one accent punch row) keeps the proven white-plus-one-recolored
device the whole lane uses — but the punch is bigger, not just recolored, so the
emphasis reads even before color does, and the accent hue is the unclaimed one,
not red.

**Mono tell — JetBrains Mono, with a concrete stat.** This is the genuinely
unclaimed type gap the corpus identified: every competitor uses a generic
display face (Impact / Anton / Inter / Fredoka) as free-floating text, and no
one owns a **monospace/terminal voice as a system signal**. Used here as a small,
consistent code-native line — not the hero voice — it is the recurring brand tell
that fireship's spark and awesome-coding's MONDAY stamp prove works, but
code-native. The embedded stat (`98.8%`, etc.) doubles as an authority number
and a searchable concrete noun, satisfying the title engine's search-noun rule on
the image itself.

**Accent — a palette, default teal, red reserved.** The dark lane's accent is
almost always hot coral-red/orange (awesome-coding `#FF4D5E`, fireship, shadeofcode,
codehead, technetiumm, koala `#ff4d4d`, devforge orange) — and that is exactly
Pawel's rejected signature. A *non-red cool accent* (electric teal/cyan) on
near-black is almost entirely unclaimed in the doom lane and reads as
"engineered/precise" rather than alarm. We ship it as a palette rather than a
single locked color because the brand silhouette is carried by base + mono +
layout + pointer; varying the hue per video lets each topic pick a contrast
against whatever else is in its feed, while red stays in reserve for the beats
that genuinely earn it.

**Annotation — precision, not scribble.** The hand-drawn marker arrow is the
single most-overused accent device in the corpus (awesome-coding, cleo, codehead,
devforge, fireship). A clean *engineered* pointer reads as the deliberate
opposite — Cleo's measured "12.2 KM" callout energy, but as a repeatable system.
The kit is one inline-SVG vocabulary (pointer, bracket, ring, underline, callout)
whose stroke inherits the accent so a hue swap recolors every mark automatically;
solid fills use `class="filled"`. Endpoints are placed by reading the numbered
coordinate grid, never eyeballed.

**Face — a bled reaction still, user-supplied.** Keeps Bucket-B's proven
emotional-face engine: one high-recognition face with a single readable emotion
bled off the right edge beats an anonymous everyman or a clutter pile every time.
The user supplies and credits the source image (we do not source third-party
copyrighted imagery); we composite — cut out, defringe/despill, rim-light, bleed.
`.thumbnail.warm` drops the `.face-glow` disc because a cool glow behind a warm or
blonde subject rings as a fake keyline. The full compositing recipe lives in
`learnings/bucket-b-thumbnails.md`.

**Brand chip — optional per-topic badge.** A small consistent badge (`.chip`,
with `--chip-bg` / `--chip-ink` overrides) for a topic logo or stamp. Optional,
not always present; it is the only place native-color brand identity enters and
must not fight the accent (the navy/coral study scored an amber-accent-on-yellow-chip
collision 3/10 — keep chip and accent visually distinct).

**Design aid — numbered coordinate grid.** A `.grid-overlay` shown under
`.with-grid` via `?grid`: 20px minor / 100px major lines, numbered x/y axis
labels, and a `.grid-safe-area` title-safe border. It exists so annotation
endpoints and the headline can be placed against real coordinates instead of
guessed. The renderer strips query params, so it is **never** in the final PNG.

## What we explicitly chose NOT to do

- **Coral / red as the default accent.** That is the saturated dark-lane device
  (7 of 11 channels) and Pawel's rejected signature; defaulting to it makes us the
  imitator. Red is in the palette but reserved for emotionally-red beats.
- **Navy or pure-black base.** Navy is the lane's wall; pure black is
  indistinguishable from every dark-mode tech channel. Green-tinted near-black is
  the contrast.
- **A generic display face as the type voice.** Impact / Anton / Fredoka are
  what everyone uses. The monospace tell is the unclaimed code-native signal —
  we keep it, not them.
- **Hand-drawn scribble arrows.** The single most-overused accent in the corpus.
  Replaced with the precision-SVG kit.
- **A leader-line library.** Dropped — the inline-SVG annotation kit covers the
  same job with placed coordinates and inherited stroke, with no dependency.
- **Borrowed-meme face as a free-floating sticker.** The face is composited
  (defringe/despill + rim-light + bleed), not pasted; a raw cutout with a matte
  fringe reads as amateur.
- **Editorial chrome.** No corner metadata strips, scene labels, or timecodes on
  the thumbnail (the project's standing no-chrome rule). The grid overlay is a
  design aid only and never ships.

## Rebrand process (if ever needed)

1. Re-run the candidate-signatures design exercise from a fresh corpus read (see
   `research/thumbnail-title-corpus-2026-06-09/ANALYSIS.md` for the format —
   per-channel one-liners, saturated-vs-white-space axis map, three candidate
   directions, pick one).
2. Update this file with the new constants and the new "why."
3. Update `templates/styles.css` with the new CSS variable values, the new
   `acc-*` palette classes, and the annotation kit.
4. Verify the HARD COMPATIBILITY CONTRACT still holds (downstream skills depend
   on it): round-N/ and round-N-vertical/ folders; `a.html` / `b.html` /
   `c.html` / `contact-sheet.html`; outputs `thumbnail-{a,b,c}.png` and
   `thumbnail-vertical-{a,b,c}.png`; `contact-sheet.html` keeps the `variant-letter`
   / `variant-text` / `variant-yt-text` spans (create-srt `extract_titles.py`);
   headline rows stay `<span class="thumbnail-row">` with the accent as a ROW
   class (never an inner span) and each variant carries a `<title>` (create-srt
   `localize_thumbnails.py`); vertical-mode keywords and output naming unchanged
   (shorts-creator).
5. Re-render the most recent video's thumbnails to confirm the new brand reads
   as intended.
6. Do not retroactively re-render old videos' thumbnails — the brand evolution is
   part of the channel history.
