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

Lucide is the primary source. Cached SVG bodies are at
`tools/thumbnail-render/icons/lucide.json` (committed, version-pinned).

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

Never pick from filled, multi-color, or pictographic sets
(`fluent-color`, `noto`, `twemoji`, `flat-color-icons`, etc.). Those
have different visual weight and break the signature.

### Resolving an Iconify body

```bash
node <repo-root>/tools/thumbnail-render/bin/icon.mjs <set>:<icon>
```

The CLI prints the SVG body to stdout. First use fetches from
`api.iconify.design` and writes the body to
`tools/thumbnail-render/icons/iconify-cache.json` (committed —
every Iconify icon ever used is reviewable in git). Subsequent
uses are offline.

Example:

```bash
node tools/thumbnail-render/bin/icon.mjs ph:cursor-click
```

Returns the Phosphor cursor-click body, ready to substitute into
`{{ICON_SVG_BODY}}` in `templates/variant.html`.

### When to ask the user vs. pick yourself

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

### Accent placement on cached bodies

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

## Reuse is encouraged

If two videos share a topic family, share the icon. The icon is a
category marker, not a unique identifier. Reusing icons across videos
strengthens the channel's visual identity.

## When in doubt

Pick the most literal topic noun. "Database indexes" → Lucide
`Database`. "Cursor click" → `ph:cursor-click`. Don't overthink. The
icon's job is to confirm what the text already said, not to be clever.
