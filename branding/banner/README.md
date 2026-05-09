# IRL Coder channel banner

Channel-level banner asset. Pairs with the avatar in `branding/logo/`. Per-video assets live under `videos/<slug>-<date>/`; this directory is for the YouTube channel itself.

## Files

| File                       | Use                                              |
|----------------------------|--------------------------------------------------|
| `banner.svg`               | Canonical source. Edit this; the PNG regenerates. |
| `banner-2048x1152.png`     | Upload this to YouTube as the channel banner.     |

YouTube downscales the 2048×1152 source for desktop, TV, and phone surfaces automatically — only one PNG size is needed for upload.

## Design

Manifesto-style banner that enacts the channel's iceberg metaphor: the type **is** the waterline. `BELOW THE WATERLINE.` runs across the horizontal centerline of the banner in JetBrains Mono ExtraBold (100 px, cream `#F5E6D3`), with a thin cream waterline extending edge-to-edge on either side of the text. A cream-stroke iceberg silhouette sits above the waterline as the visible "tip"; below it, 16 amber `#FFB627` Lucide line icons are scattered in three loose bands — compact icons inside the 1235×338 phone-safe area (visible on phones), larger icons across the lower half of the canvas (visible only on desktop and TV). The full icon scatter forms the "submerged territory" the manifesto names.

Full design rationale: `docs/superpowers/specs/2026-05-09-irl-coder-channel-banner-design.md`.

## Rebuild

If `banner.svg` changes, regenerate the PNG with:

```bash
cd tools/branding-render && npm run build:banner
```

This rasterizes `branding/banner/banner.svg` to `banner-2048x1152.png` next to it. Then commit the SVG and the regenerated PNG together.

## Don't

- Don't edit the PNG directly. It regenerates from the SVG.
- Don't make the banner promote a specific video. The manifesto is the channel's permanent stance; per-video promo would force a redesign on every upload.
- Don't put critical content outside the 1235×338 centered safe area. Phones crop to the safe area; anything outside it only shows on desktop and TV.
- Don't change one color or the manifesto in isolation. The visual signature is shared with the avatar (`branding/logo/`); rebranding is a separate exercise.
