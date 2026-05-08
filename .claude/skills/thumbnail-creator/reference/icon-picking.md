# Icon picking

Rules for choosing the single icon that appears on every variant in a
round.

## The constraints

- **One icon per video.** Same icon across all 3 variants in every round.
  Variation lives in text and accent placement, not the icon.
- **Names the topic statically.** No diagrams, no before/after, no arrows,
  no comparisons. The icon is the period at the end of the headline, not
  the headline itself.
- **One accent detail.** Apply the accent color to exactly one geometric
  region of the icon. Never tint the whole icon. The lock body but not
  the shackle. The key bow but not the shaft. The second "A" but not the
  first.

## Source of icons — Lucide first

Lucide is the primary source. Cached icons are at
`tools/thumbnail-render/icons/lucide.json` (committed, version-pinned).
Each entry is `{body, viewBox}`; Lucide is canonically 24×24, so
`viewBox` is always `"0 0 24 24"`.

To find the right icon: think of the **topic noun**, not the insight.
Then look it up in the cache.

### Lookup table

| Topic noun | Lucide name | Suggested accent region |
|---|---|---|
| Database, table, index | `Database` | top ellipse (the disk's "lid") |
| Password, auth, encryption | `Lock` | the body rectangle |
| Key, secret | `Key` or `KeyRound` | the bow (round end) |
| Code, function, method | `Code` | the angle brackets |
| File, document, format | `FileText` | the corner fold |
| Terminal, shell, CLI | `Terminal` | the prompt `>` |
| CPU, processor | `Cpu` | the central square |
| Network, request | `Network` | one node circle |
| Server, backend | `Server` | the indicator dot |
| Disk, storage | `HardDrive` | the indicator dot |
| Cloud, hosted | `Cloud` | one bump of the cloud |
| URL, web, internet | `Globe` | one meridian line |
| Security, protection | `Shield` | the inner mark |
| Layers, stack | `Layers` | the top layer |
| Branching, git | `GitBranch` | the merge node |
| Hash, identifier | `Hash` | one of the bars |
| Bits, binary | `Binary` | one of the digits |
| Performance, signal | `Activity` | a peak |
| Lightning, speed, power | `Zap` | the bolt body |
| Random, dice | `Dice5` | the center pip |
| Fingerprint, identity | `Fingerprint` | a ridge |
| Eye, observability | `Eye` | the pupil |
| Mouse, input | `Mouse` | the scroll wheel |
| Keyboard, input | `Keyboard` | one key |
| Image, raster | `Image` | the sun (corner circle) |
| Type, text | `Type` | the crossbar of the T |
| Brackets, syntax | `Brackets` | one bracket |
| Function, math | `FunctionSquare` | the f symbol |
| Workflow, pipeline | `Workflow` | one connector |

If a topic isn't in this table, search Lucide's icon set
(https://lucide.dev/icons) for the matching topic noun. If you find a
new one, add it to the `TOPICS` array in
`tools/thumbnail-render/scripts/sync-icons.mjs` and run
`npm run sync-icons` to refresh the cache.

## Fallback — Iconify

If no Lucide icon in the lookup table fits the topic, fall back to
Iconify. Iconify aggregates ~200 icon sets and ~200,000 icons; we use
only the line-icon sets that match the locked aesthetic.

### Iconify icon-set search order

Try sets in this order. Pick the first one whose conventional naming
matches the topic noun:

1. `lucide` (Iconify-mirrored — only useful when our local cache is
   missing an icon for some reason)
2. `ph` (Phosphor Regular)
3. `tabler`
4. `mynaui`
5. `heroicons` (outline variant)
6. `lineicons`

For generic topic nouns, never pick from filled, multi-color, or
pictographic sets (`fluent-color`, `noto`, `twemoji`,
`flat-color-icons`, etc.). Those have different visual weight and
break the signature.

Exception: when the topic noun *is* a specific brand, brand-logo sets
become eligible. See "Brand exception — when the topic IS the brand"
below.

### Resolving an Iconify icon

```bash
node <repo-root>/tools/thumbnail-render/bin/icon.mjs <set>:<icon>
```

The CLI prints JSON `{"body": "...", "viewBox": "..."}` to stdout.
First use fetches from `api.iconify.design` and writes the entry to
`tools/thumbnail-render/icons/iconify-cache.json` (committed — every
Iconify icon ever used is reviewable in git). Subsequent uses are
offline.

Example:

```bash
node tools/thumbnail-render/bin/icon.mjs ph:cursor-click
# {"body":"<path .../>","viewBox":"0 0 256 256"}
```

Substitute `body` into `{{ICON_SVG_BODY}}` and `viewBox` into
`{{ICON_VIEWBOX}}` in `templates/variant.html`. Most line-icon sets
are 24×24 native; brand sets like `logos` use larger viewBoxes — the
CLI captures whichever the source uses, so you don't need to inspect
the SVG by hand.

## Brand exception — when the topic IS the brand

The default rules above (line icons, one accent region) optimize for
visual-signature consistency across the channel. They break down for
a narrow case: videos where the topic noun *is* a specific brand
(Jenkins, Docker, React, Postgres, Kubernetes), where the brand mark
itself is the most click-recognizable thing the thumbnail can show.

For those, brand-icon sets become eligible.

### Eligibility

Use the brand exception only when the brand appears in the working
title or is the explicit subject of the video. "Building CI
pipelines" is a generic topic — use `Workflow` per the line-icon
path. "Why Jenkins still wins in 2026" is a brand topic — Jenkins
logo is fair game.

If you're unsure whether a topic qualifies, default to the line-icon
path. The exception is for unambiguous brand-as-subject videos, not
for "this video happens to mention Postgres".

### Set preference order

Try in this order:

1. `simple-icons` — monochrome silhouettes. Single fill, fits the
   minimal aesthetic better than multi-color marks. First choice.
2. `logos` — multi-color brand marks. Use only when the brand's
   identity collapses without its colors (Google's wordmark, Slack's
   hash, Firefox's gradient).
3. `devicon` — also multi-color, dev-tool focused. Final fallback
   when neither `simple-icons` nor `logos` carries the brand.

Resolve via the same CLI:

```bash
node tools/thumbnail-render/bin/icon.mjs simple-icons:jenkins
node tools/thumbnail-render/bin/icon.mjs logos:jenkins
```

### Color handling — class-driven, not body-mutating

Brand bodies stay verbatim from the cache. Color decisions live in
CSS, applied via the `ICON_CLASS` token on the `<svg>` element.

Three classes for brand icons:

1. **`brand-silhouette`** — for monochrome silhouettes (`simple-icons`).
   Renders the logo in the locked text color (`#F5E6D3`). Cleanest,
   most professional. Lets the thumbnail's accent live on the text
   instead. Recommended default for brand-silhouette icons.

   The CSS sets both `color` (so `fill="currentColor"` paths resolve
   correctly) and `fill` (for paths without their own fill attribute),
   plus `stroke: none` to override the locked line-icon defaults.

2. **`brand-silhouette accent`** — same family, but tints the whole
   logo amber (`#FFB627`). Use only when the brand reads even when
   fully recolored (Jenkins butler, Docker whale silhouette) AND the
   thumbnail text is short enough that the icon needs to carry more
   visual weight.

3. **`brand-color`** — for multi-color marks (`logos`, `devicon`).
   Each path's own fill attribute wins; the locked line-icon `fill:
   none` and `stroke` defaults are cleared. Result: the logo renders
   in its native brand colors.

Brand silhouettes are single-region — the "accent one geometric
region, leave the rest default" rule doesn't apply, since there's no
"rest" to leave. Don't try to inline `fill="#FFB627"` on a single
path inside a `simple-icons` body; use the `accent` class instead.

For multi-color marks, never tint at all — the point of using a
multi-color set is the recognition, and tinting destroys that.
Multi-color thumbnails should compensate by keeping accent regions on
the text, not the icon.

### Trade-off you're making

Brand logos shift the visual rhythm of the channel: thumbnails with
brand logos look slightly different from thumbnails with line icons.
That's the cost. The benefit is click-recognition on brand-specific
videos.

Use the exception sparingly. Once the channel has a few brand-logo
thumbnails mixed with line-icon thumbnails, the variance itself
becomes part of the signature — but only if the line-icon style
remains the clear majority.

## When to ask the user vs. pick yourself

Pick yourself when:
- The topic noun has an obvious Iconify name in one of the listed sets.
- A quick preview via `bin/icon.mjs` shows it reads as the topic at a
  glance.

Ask the user when:
- The topic is abstract enough that multiple plausible icons exist
  ("compression" — Archive? FileMinus? Layers? Box?). List 2–3
  candidates and let them pick.
- The first-pick fetch returns an icon that looks wrong at thumbnail
  size (too busy, too symbolic, multi-element).

## Accent placement on cached bodies

Lucide and Iconify bodies arrive without `class` attributes. To accent
one detail, inline `stroke="#FFB627"` (for stroked elements) or
`fill="#FFB627"` (for filled elements) on exactly one child of the
body. The "Suggested accent region" column in the Lucide lookup table
above tells you which element to accent for common icons. For Iconify
icons, pick the most distinctive geometric region — usually the part
that visually carries the icon's identity (lock body, key bow, the
crossbar of a "T", the disk's lid, etc.).

The locked CSS classes `.stroke`, `.accent-stroke`, `.accent-fill`
remain in `templates/styles.css` for any case where they're useful,
but the default path for cached bodies is inline `stroke="#FFB627"`.

For brand-logo silhouettes (`simple-icons`, `logos`, `devicon`),
**don't** mutate the body. Use the `ICON_CLASS` token instead — set
it to `brand-silhouette`, `brand-silhouette accent`, or `brand-color`
as appropriate. See "Brand exception — when the topic IS the brand"
above for the full class table.

## Reuse is encouraged

If two videos share a topic family, share the icon. The icon is a
category marker, not a unique identifier. Reusing icons across videos
strengthens the channel's visual identity.

## When in doubt

Pick the most literal topic noun. "Database indexes" → Lucide
`Database`. "Cursor click" → `ph:cursor-click`. Don't overthink. The
icon's job is to confirm what the text already said, not to be clever.
