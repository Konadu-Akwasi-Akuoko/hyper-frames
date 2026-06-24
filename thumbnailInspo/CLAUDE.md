# thumbnailInspo — instructions

The canonical **thumbnail reference library**. It is the analogue of
`motionGraphicsInspo/` (single-beat motion) and `pacingInspo/` (whole-video
cadence), but for **YouTube thumbnail composition**: a tagged index of real,
high-performing thumbnails harvested from proven creators, each described
precisely enough that a new thumbnail can be built by *replicating its layout*
rather than inventing one from scratch.

`README.md` is the source of truth: a **two-tier** index — a compact
`## Quick index` scan table over full `## Entries` blocks. Each entry pairs a
harvested thumbnail bitmap (`<channel>/<file>.jpg`) with a written **Layout map**
(where every element sits, in the 1280x720 / 1080x1920 pixel space the templates
place elements in) and a **Why it works** note.

## The core idea — pick-and-mimic, never from scratch

The `thumbnail-and-title-generator` skill does **not** design a composition from
a blank canvas. For every thumbnail it builds it:

1. **Picks a reference** from this library's `## Quick index` whose archetype +
   device match the video's beat (a shocked-face reaction, a giant-number stat, a
   vs/comparison, an iceberg, a tier-list, a code screenshot, …).
2. **Grids the reference** with `tools/thumbnail-inspo/grid.py` to read exactly
   where each element lands (cell numbers + pixel rulers in the same coordinate
   space the templates use).
3. **Rebuilds that same layout** with OUR content — our headline, our accent hue,
   our face still, our icons/stat — in the locked Specimen signature. Same
   skeleton, our flesh: the icons/images/text change, the *composition* is lifted.

This is deliberate: the channel's thumbnails should sit visually next to the
creators who already win the niche's click, not reinvent layout each time.

## Reading it (consumption — the thumbnail skill's job)

1. **Scan the `## Quick index` table** — one row per entry (`slug` · `channel` ·
   `archetype` · `layout` · `device` · `face` · `accent` · `use-when`). Match the
   video's beat/emotion to a row from the text alone. Cheap surface; reading it
   doesn't load the library.
2. **Drill into the matching `## Entries` block and open *only* that entry's
   image** (and its `.grid.png` if already generated, else grid it on demand).
   The `Layout map` carries the element positions the row can't.
3. **Replicate the layout, swap the content.** Same archetype + element positions;
   our headline, accent, face, stat. Adapt sizing to our text length — never
   overflow — but keep the skeleton. Picking a reference is **mandatory** for
   every thumbnail (unlike the motion library, where citing nothing is fine).

## Adding references (curation — `tools/thumbnail-inspo/`)

Do **not** hand-place files. The tooling under `tools/thumbnail-inspo/` does the
mechanical work; **you (Claude) author the judgment** the tool can't:

- **`fetch.py`** (mechanical, deterministic): resolves each channel's *Popular*
  playlist (view-sorted) — or the `/shorts` tab for shorts channels — and pulls
  the top-N thumbnails straight from the `i.ytimg.com` CDN into
  `thumbnailInspo/<slug>/`, with a per-channel `_manifest.json` (id, title, rank,
  watch URL). The CDN GET is **not** bot-walled; only one serialized metadata
  call per channel touches YouTube's tab extractor. Channels live in
  `channels.txt` — edit it and re-run to refresh/extend.
- **`grid.py`** (mechanical): stamps a labeled measuring grid (numbered cells +
  pixel rulers) on any reference so its element positions read off directly.
- **You** (judgment): open each harvested thumbnail and author its `## Entries`
  block — the `Tags:`, `Reads as:`, `Layout map:`, `Why it works:`, and
  `Mimic for:` lines — then add the matching `## Quick index` row. The tool never
  writes prose.
- **Titles + title shape** (mechanical + judgment): `fetch.py` already records each
  thumbnail's real YouTube `title` in the manifest. After cataloging, run
  `python3 tools/thumbnail-inspo/backfill_titles.py` to inject `title` into every
  catalog entry, then classify each into `title_shape` (surface formula) +
  `title_pattern` (the title-engine pattern it rides). These let the skill pair a
  proven title shape with the layout — the shape is a prior, not a script to copy.

Keep filenames ↔ index entries in sync: every harvested `<channel>/<file>.jpg`
that earns a place has exactly one `README.md` entry (Quick-index row + Entries
block), and every entry points at a real file. Not every harvested file must be
indexed — drop weak/duplicate ones; a lean, diverse index beats a padded one.

## Tagging vocabulary (keep it small and honest)

- **archetype** (the thumbnail's core idea): `face-reaction`, `big-text`,
  `object-hero`, `comparison-vs`, `before-after`, `tier-ranking`,
  `diagram-arch`, `code-screenshot`, `number-stat`, `meme`, `logo-grid`,
  `iceberg`, `roadmap`.
- **layout** (composition skeleton): `face-left`, `face-right`, `text-left-face-right`,
  `text-center`, `full-bleed-object`, `split-vertical`, `centered-stack`,
  `grid-tiles`, `corner-badge`.
- **device** (the scroll-stopper, ≤2): `giant-number`, `red-circle`, `red-arrow`,
  `shocked-face`, `glow-accent`, `strike-through`, `x-mark`, `checkmark`,
  `vs-bolt`, `danger-red`, `neon-on-dark`, `hand-point`, `progress-bar`.
- **face**: `yes` / `no`. **accent**: dominant accent color word.
- **text**: headline text density `low` / `med` / `high`.
- **title_shape** (the title's surface formula, exactly one of 14):
  `speed-primer`, `x-explained`, `every-x-explained`, `comparison-vs`,
  `what-is-x`, `open-why-how`, `listicle-n`, `assumption-flip`, `panic-threat`,
  `curiosity-reversal`, `scale-story`, `first-person-feat`, `identity-advice`,
  `meme-skit`. Two carry corpus caveats: `every-x-explained` wins only on
  maximally-searched nouns; `meme-skit` is a documented floor.
- **title_pattern** (which of `title-engine.md`'s 5 patterns it rides):
  `concrete-noun-verb`, `curiosity-gap-reversal`, `open-what-why-how`,
  `assumption-flip`, `identity-status`.

Prefer an existing tag; extend a dimension only when nothing fits.
