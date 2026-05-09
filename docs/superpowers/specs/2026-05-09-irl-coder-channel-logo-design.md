# IRL Coder channel logo — design

**Date:** 2026-05-09
**Status:** spec, ready for implementation plan
**Replaces:** the current pixel-art "IRL CODER" PNG logo (Press Start 2P-style with a pixel crown)

## 1. Purpose

Replace the current pixel-art channel logo with an icon-only mark that aligns
with the channel's locked thumbnail brand. The viewer should read the YouTube
avatar circle and a thumbnail next to it as one coherent visual identity.

The current logo and the thumbnail brand currently speak different visual
languages: the logo is bitmap pixel-art (Press Start 2P-style); the thumbnail
visual signature explicitly chose AGAINST that aesthetic to differentiate from
Pawel's coral-red bitmap-pixel signature. This spec resolves that mismatch in
favor of the thumbnail brand.

The logo carries one idea: **the iceberg**. It's a literal nod to the channel's
9-beat "iceberg" narrative arc encoded in `script-writer` — mundane action
revealed as unsuspected depth. Surface above water, larger mass below. No other
tech channel uses this metaphor as its avatar.

## 2. Scope

**In scope:**
- A single icon-only logo composed from a curated Iconify line icon
  (`tabler:iceberg`), styled to the channel's locked palette.
- Source SVG with a transparent background and embedded fill/stroke colors.
- Rendered PNG variants at the sizes YouTube actually uses
  (800, 176, 96, 48, 24 px), each on the espresso-brown circle backdrop.
- A documented, repeatable build step so the assets can be regenerated if the
  brand evolves.

**Out of scope:**
- Wordmark or text-paired lockup. The logo is icon-only; "IRL CODER" appears in
  the YouTube channel name field, not in the avatar.
- Channel banner, end-card, or watermark — separate brand artifacts, future
  work.
- Rebranding the thumbnail visual signature. That is locked and unchanged.
- Updating per-video assets retroactively.

## 3. Inputs and outputs

### Inputs

- The locked visual signature constants from
  `.claude/skills/thumbnail-creator/reference/visual-signature.md`:
  background `#1A1410`, text/cream `#F5E6D3`, accent amber `#FFB627`, Lucide
  line-icon family.
- The Iconify icon body for `tabler:iceberg`, fetched once via
  `tools/thumbnail-render/bin/icon.mjs` and cached in
  `tools/thumbnail-render/icons/iconify-cache.json`.

### Outputs (committed to the repo)

A new top-level `branding/` directory:

```
branding/
  logo/
    iceberg.svg              # canonical source, 800×800 viewBox, transparent background
    iceberg-800.png          # YouTube source upload (transparent PNG, espresso circle baked in)
    iceberg-176.png          # channel page header
    iceberg-96.png           # feed avatar
    iceberg-48.png           # comment thread
    iceberg-24.png           # notification badge
    README.md                # how to regenerate, when to use which file
```

The 800 px PNG is what gets uploaded to YouTube. The smaller sizes are kept
committed so they can be referenced wherever a non-YouTube surface needs the
avatar at a known size (README badges, social profile pictures, etc.) without
re-rastering on every consumer.

## 4. Visual specification

### Composition

- Canvas: 800×800 transparent PNG, with the espresso circle (`#1A1410`) drawn
  as a filled disk inside that canvas. Inside the disk: the iceberg icon
  centered.
- Icon: `tabler:iceberg` (Iconify), rendered from its native 24×24 viewBox.
- ViewBox crop: `2 2 20 20` — tightens framing so the iceberg fills more of
  the circle without overflowing.
- Icon display size: 70% of the circle's diameter (560 px inside the 800 px
  disk).

### Color and stroke

- Iceberg outline (full path, including the submerged portion): stroke
  `#FFB627` (amber), `stroke-width: 1.5`, `stroke-linecap: round`,
  `stroke-linejoin: round`. The stroke-width is in the icon's native 24-unit
  space, so the visual stroke scales with the canvas.
- Waterline (the horizontal line `M3 10h18`): stroke `#F5E6D3` (cream), same
  width and joins as the iceberg outline.
- Submerged mass (everything below y=10 in the icon's viewBox): fill `#FFB627`
  (amber), `fill-opacity: 0.35`, no stroke. Implemented as a duplicate of the
  iceberg path clipped to the rectangle `(0, 10, 24, 14)`. This gives the
  underwater portion visible volume rather than a hollow outline, encoding
  the "hidden depth" half of the iceberg metaphor.

### Why this composition

- The cream waterline is the only cream element in the mark. It's the
  literal surface/depth divide — visually it IS the channel metaphor, so
  it gets the highest-contrast color in the palette.
- Amber on amber (stroke + translucent fill) keeps the iceberg as one visual
  body. Using cream for the stroke and amber for the fill would split the
  iceberg in two; using the same hue at different opacities reads as one
  object viewed across an interface (the waterline).
- 35% fill-opacity was selected from a comparison against 20% (too quiet at
  small sizes — submerged mass disappears in the 24 px notification badge)
  and 50% (too dense — competes with the stroke detail at 800 px).
- 70% icon-to-circle ratio, plus the `2 2 20 20` viewBox crop, is what gives
  the silhouette enough presence at 24 px without crowding the circle at
  800 px. A naive 60% with the full 0 0 24 24 viewBox left too much padding
  and visibly clipped under CSS scaling — the v1 brainstorm screen made
  that mistake; this spec doesn't repeat it.

### Sizes

| Size  | Use case                | Source       |
|-------|-------------------------|--------------|
| 800px | YouTube source upload   | rasterized   |
| 176px | Channel page header     | rasterized   |
| 96px  | Feed avatar             | rasterized   |
| 48px  | Comment thread          | rasterized   |
| 24px  | Notification badge      | rasterized   |

All five sizes render from the same canonical SVG. The renderer does not
re-author the SVG per size; it only sets the PNG output dimensions.

## 5. Build / render approach

The repo already has a Puppeteer-based renderer at
`tools/thumbnail-render/bin/render.mjs` that converts HTML pages to PNGs at a
fixed pixel size, used by the `thumbnail-creator` skill. The same machinery
can render this logo — no new tool needed, just a new entry point.

Approach:

1. Author `branding/logo/iceberg.svg` directly. The SVG is small (~25 lines)
   and self-contained — the espresso disk, the translucent submerged fill
   (with its clipPath defs), the iceberg stroke, the cream waterline.
2. Add a small build script `tools/branding-render/bin/render.mjs` (or extend
   the existing thumbnail-render tool with a `--logo` mode) that takes the
   SVG and rasterizes it via Puppeteer at each target size.
3. Run the build once and commit the resulting PNGs. Document the rebuild
   command in `branding/logo/README.md`.

Implementation-plan-level decisions (which renderer to extend vs. fork, exact
script invocation, README contents) are deferred to the writing-plans step.

## 6. What this design rejects

- **Keeping the pixel-art logo.** Mixed signals between the avatar and the
  thumbnail strip in the YouTube feed. Coherence compounds; mismatch erodes
  it.
- **Wordmark or text in the logo.** YouTube already shows the channel name
  next to the avatar in every surface that matters. Adding "IRL CODER" inside
  the avatar circle wastes the most precious 96 px of brand real estate.
- **Hand-coded SVG icons.** The thumbnail visual signature explicitly bans
  these for per-video work. The logo follows the same rule for the same
  reason — using a curated Iconify line set guarantees stylistic consistency
  with future thumbnail icons.
- **Cream stroke with amber fill (or other accent inversions).** Tested in
  the brainstorm round-1 contact sheet (variants A/B/C). The amber-stroke
  + translucent-amber-fill + cream-waterline composition was the user's
  pick after seeing all four side-by-side at 96 px feed size.

## 7. Open questions

None at spec time. The visual is locked; remaining decisions (build script
location, README phrasing) are implementation details for the plan.
