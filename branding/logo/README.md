# IRL Coder channel logo

Channel-level identity assets. Per-video assets live under `videos/<slug>-<date>/`; this directory is for the YouTube channel itself.

## Files

| File              | Use                                              |
|-------------------|--------------------------------------------------|
| `iceberg.svg`     | Canonical source. Edit this; everything else regenerates. |
| `iceberg-800.png` | Upload this to YouTube as the channel avatar.     |
| `iceberg-176.png` | Channel page header avatar size.                  |
| `iceberg-96.png`  | Feed avatar size.                                 |
| `iceberg-48.png`  | Comment thread avatar size.                       |
| `iceberg-24.png`  | Notification badge avatar size.                   |

The PNGs are committed so README badges, social profiles, and external surfaces can reference them at known sizes without re-rastering.

## Design

Espresso disk (`#1A1410`) with an amber-stroke iceberg (`#FFB627`, stroke-width 1.5 in 24-unit space, rounded joins) and a cream waterline (`#F5E6D3`). The portion of the iceberg below the waterline is filled with translucent amber (`fill-opacity: 0.35`) — the visible submerged mass encodes the channel's "iceberg" narrative metaphor (mundane action revealed as unsuspected depth).

Full design rationale: `docs/superpowers/specs/2026-05-09-irl-coder-channel-logo-design.md`.

## Rebuild

If `iceberg.svg` changes, regenerate all five PNGs with:

```bash
cd tools/branding-render && npm run build:logo
```

This rasterizes `branding/logo/iceberg.svg` to PNGs at 800, 176, 96, 48, and 24 px and writes them next to the SVG. Then commit the SVG and all five regenerated PNGs together.

## Don't

- Don't edit the PNGs directly. They regenerate from the SVG.
- Don't add a wordmark inside the avatar circle. The channel name appears next to the avatar in every YouTube surface that matters; reusing 96 px of brand real estate for redundant text is a waste.
- Don't change one color in isolation. The four constants (espresso, cream, amber, transparent corners) are the visual signature; rebranding is a separate exercise.
