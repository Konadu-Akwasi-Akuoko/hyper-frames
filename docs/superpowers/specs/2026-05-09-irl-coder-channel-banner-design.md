# IRL Coder channel banner — design

**Date:** 2026-05-09
**Status:** spec, ready for implementation plan
**Companion artifact:** the channel logo (`branding/logo/iceberg.svg`), shipped earlier the same day, established the visual signature this banner extends.

## 1. Purpose

A YouTube channel banner that enacts the channel's "iceberg" editorial metaphor at full scale. The type itself acts as the waterline: the manifesto reads `BELOW THE WATERLINE.`, with a single cream-stroke iceberg "tip" above the line and a scatter of amber Lucide topic icons forming the "submerged territory" below it. The banner's words and its picture say the same thing.

The banner pairs with the logo: the avatar carries the symbol; the banner carries the words and a sample of the editorial surface area. A viewer scanning a feed sees the avatar first, then expands to the channel page and reads the banner — the manifesto answers the implicit question "what is this channel about?" before they watch anything.

## 2. Scope

**In scope:**
- A single 2048×1152 banner composition in the channel's locked palette.
- Source SVG, plus a single rasterized 2048×1152 PNG for upload.
- A README documenting the rebuild step and what each file is for.
- A modest extension to `tools/branding-render/` so it can rasterize rectangular sources, not only squares.

**Out of scope:**
- Multiple banner variants for A/B testing. YouTube does not run banner A/B tests; only one banner is live at a time.
- Per-video banner refreshes. The manifesto is the channel's stance, not a per-episode promo.
- Animated / video banners. YouTube does not support motion banners; only static raster.
- Channel watermark, end card, or other brand artifacts. Those are separate, future work.
- Rebranding the visual signature. The four locked constants (espresso, cream, amber, JetBrains Mono ExtraBold) carry over from the logo unchanged.

## 3. Inputs and outputs

### Inputs

- Locked visual signature constants from `.claude/skills/thumbnail-creator/reference/visual-signature.md` (background `#1A1410`, cream `#F5E6D3`, accent amber `#FFB627`, JetBrains Mono ExtraBold).
- The iceberg path used by the logo (`m19 10l-2 9l-4 3l-3-5l-3-1l-2-6l2-5l3-2l3 3l4 1z` from `tabler:iceberg`), reused for the banner's tip icon.
- 16 Lucide line icons, fetched once via `tools/thumbnail-render/bin/icon.mjs`.

### Outputs (committed to the repo)

```
branding/banner/
  banner.svg                   # canonical source, 2048x1152
  banner-2048x1152.png         # the file uploaded to YouTube
  README.md                    # what each file is for, how to rebuild
```

The banner gets a single rasterized PNG. Unlike the logo, YouTube does not consume multiple sizes — the platform downscales the 2048×1152 source for desktop, TV, and phone surfaces automatically.

## 4. Visual specification

### Canvas and palette

- Canvas: 2048×1152 (YouTube's recommended TV-safe size).
- Background: solid espresso `#1A1410`, edge-to-edge.
- Phone-safe area: 1235×338, centered. Type, tip icon, waterline, and most of the submerged icons must fit inside this region; only outer-region icons may sit outside it.

### Waterline

- Color: cream `#F5E6D3`.
- Stroke width: 4 px (in 2048-source space).
- Geometry: horizontal line at y=576 (vertical center of the canvas).
- Run: edge-to-edge except for an interruption around the type, where the line breaks 32 px before the left edge of `BELOW` and resumes 32 px after the right edge of `WATERLINE.`. The text sits in this gap as if the channel name itself is the horizon.

### Type — `BELOW THE WATERLINE.`

- Font: JetBrains Mono, weight 800 (ExtraBold).
- Size: 100 px.
- Color: cream `#F5E6D3` (same as the waterline).
- Case: ALL CAPS.
- Alignment: centered horizontally on the canvas (x=1024). Vertical center on y=576 (sits exactly on the waterline; the line interruption around the text is what makes the type visually IS the waterline).
- Letter-spacing: −0.02 em (slight tightening for the monospace at this size).
- Width budget: 20 chars × ~60 px/char ≈ 1200 px, fits inside the 1235 px phone-safe area with ~17 px margin per side. Going larger than 100 px overflows the safe area on phones; going smaller wastes the canvas. 100 px is the locked size.

### Tip icon (above waterline)

- Source: the iceberg path from the logo (`m19 10l-2 9l-4 3l-3-5l-3-1l-2-6l2-5l3-2l3 3l4 1z`), drawn in its native 24-unit space.
- Size: 160×160 px display at the source canvas.
- Position: centered horizontally at x=1024; vertical center at y=416 (so the bottom of the icon sits 80 px above the waterline at y=576).
- Style: cream `#F5E6D3` stroke, stroke-width `1.5` in 24-unit space (so effective ~10 px at 160 display), no fill. No translucent submerged-mass treatment — that's the logo's job; the banner's tip is a pure silhouette of "what's visible above water."
- The waterline path (the `M3 10h18` line that runs through the icon's middle) is omitted from the tip icon. The banner's own cream waterline IS that horizontal stroke; redrawing it inside the tip icon would create a visible double-line.

### Submerged territory (below waterline)

- 16 distinct Lucide line icons, all from the same family (consistent stroke style with the logo's tabler:iceberg).
- Locked icon set (representing the channel's editorial surface area):
  `Type, Globe, KeyRound, Database, Cpu, Image, Code, Cookie, Terminal, Wifi, Hash, Layers, GitBranch, Lock, Cog, Server`.
- Color: amber `#FFB627`.
- Size range: 60 – 130 px (varied per icon to suggest depth without literal perspective).
- Opacity range: 0.18 – 0.50 (varied to suggest depth-fade).
- Stroke width: each icon's native Lucide stroke (typically `2` in 24-unit space) — left untouched per the logo's "use real icons from the curated set" rule.
- Layout: hand-placed scatter, non-gridded. Constraints:
  - The scatter must read as a complete composition when cropped to the 1235×338 phone-safe area. ~12 of the 16 icons sit inside the safe area; the remaining ~4 sit outside it (left/right edges of the canvas) and only show on desktop/TV.
  - No icon overlaps the 100 px clear zone immediately below the waterline (y=576 to y=676). The space immediately under the type stays clean so the manifesto reads sharply.
  - No two icons overlap.
  - Icon centers spread across the lower half (y=676 to y=1100); none touches the bottom edge.

The exact `(x, y, size, opacity)` per icon is locked at SVG-author time (not at spec time) because hand-tuning a scatter against a live preview is faster than encoding the positions in prose. The constraints above are the contract the scatter must satisfy.

## 5. Build / render approach

The repo has `tools/branding-render/`, which currently exposes `renderSvgToPng(svgPath, outPng, size)` — square-only. The banner is rectangular (2048×1152), so the renderer needs to accept rectangular dimensions.

Approach:

1. Author `branding/banner/banner.svg` directly. The SVG is self-contained: espresso rectangle backdrop, two cream waterline segments (left of text and right of text), the type, the tip icon, and the 16 submerged icons inlined with `<use>` references to a shared `<defs>` block.
2. Generalize `renderSvgToPng` to accept rectangular dimensions. Specific API shape (overloaded `size` param vs. new function vs. options object) is a plan-level decision; backwards-compatibility for the existing logo callers is required.
3. Add a build script `tools/branding-render/scripts/build-banner-png.mjs` that renders `branding/banner/banner.svg` to `branding/banner/banner-2048x1152.png` and exposes it as `npm run build:banner`.
4. Document the rebuild command in `branding/banner/README.md`.

## 6. What this design rejects

- **Promotional banner with the latest video's thumbnail.** Highest impact per visit, but requires a redesign after every upload — high maintenance for a small-channel pipeline. The manifesto pays back permanently.
- **Topic showcase strip of past videos.** Needs ≥4 finished videos to read as full; the channel currently has one. Premature.
- **Single accent iceberg next to the type.** Quietest, most logo-coherent, but adds nothing the logo doesn't already say. The banner is the place to expand the metaphor, not echo it.
- **Centered text with a separate horizontal line above or below.** Two competing horizontals. The locked design uses one horizontal — the type sits on the line and breaks it.
- **Gridded icon arrangement.** Reads as "navigation" or "feature list," not "underwater territory." Hand-placed scatter is the locked approach.
- **The full logo (espresso disk + amber iceberg + waterline + submerged fill) used as the tip.** Creates a waterline-within-a-waterline. The banner's waterline is its own; the tip is a stroke-only silhouette.

## 7. Open questions

None at spec time. The composition is locked; the build-script API shape is the only deferred detail and that's an implementation concern for the plan.
