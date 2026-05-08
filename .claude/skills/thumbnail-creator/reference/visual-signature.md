# Visual signature — locked

The channel's thumbnail brand. These constants do not change per video.
Changing them is a rebrand exercise, not a per-video parameter.

If you ever rebrand: re-run the visual-signature design exercise (propose
3 candidate signatures, pick one, update both this file and
`templates/styles.css`). Do not change one constant in isolation — the four
together are what gives the channel a recognizable silhouette in the feed.

## The constants

| Constant | Value |
|---|---|
| Font | `JetBrains Mono`, weight 800 (ExtraBold) |
| Background | `#1A1410` (espresso brown) |
| Text color | `#F5E6D3` (warm off-white) |
| Accent color | `#FFB627` (amber) |
| Icon style | Lucide line icons (or Iconify line set), 320×320 px display, parent-SVG default stroke-width 2 in 24×24 viewBox; accent on exactly one detail |

## Why each constant

**Font — JetBrains Mono ExtraBold.** Monospace evokes terminals and code
without copying Pawel's bitmap font (Press Start 2P-style). ExtraBold
survives at thumbnail grid size (~210 px wide on the YouTube feed) where
thinner weights smudge. JetBrains Mono is widely-loaded enough to be a
recognizable choice without being precious.

**Background — #1A1410 espresso brown.** Differentiates from Pawel's pure
black AND from the cool-blue dark background most tech channels default to.
Warm dark reads as "scholarly" or "lab notebook" rather than "techbro" or
"cyberpunk." A viewer scanning a feed of dark-blue and pure-black thumbnails
notices warm dark immediately.

**Text — #F5E6D3 warm off-white.** Off-white instead of pure white
reinforces the paper/print register and prevents the high-contrast vibration
that pure-white-on-pure-black produces. Subtle, but adds up.

**Accent — #FFB627 amber.** High contrast against espresso. Warm complement
(both colors are in the same temperature family), so they don't fight each
other. Critically: not red. Pawel uses coral red. We use amber so a
side-by-side feed comparison is unambiguous.

**Icons — Lucide line (Iconify fallback), accent on one detail.** Real
SVG icons from a curated set — Lucide first, then any of the matching
Iconify line sets (Phosphor, Tabler, MynaUI, Heroicons-outline,
Lineicons). Hand-coded SVGs are not allowed; they break visual
consistency. The "one detail" rule is what gives the icon its accent
without overwhelming it: the lock body in amber, but the shackle in
off-white; the disk's lid in amber, but the body in off-white; the
key bow in amber, the shaft in off-white.

## What we explicitly chose NOT to do

- Pawel's bitmap pixel font. Copying it would put our thumbnails next to
  his in any feed and lose every time on direct comparison.
- Pure black background. Saturated and indistinguishable from every other
  dark-mode tech channel.
- Coral red accent. That's now Pawel's signature; we'd be the imitator.
- White line icons with a red dot. Same reason — that's now him.
- "Explained in N Minutes" formula text. Strongly associated with him.

## Rebrand process (if ever needed)

1. Re-run the candidate-signatures design exercise (see brainstorming
   conversation 2026-05-08 for the format — three candidates, sample
   contact sheets, pick one).
2. Update this file with the new constants and the new "why."
3. Update `templates/styles.css` with the new CSS variable values.
4. Re-render the most recent video's thumbnails to verify the new brand
   reads as intended.
5. Do not retroactively re-render old videos' thumbnails — the brand
   evolution is part of the channel history.
