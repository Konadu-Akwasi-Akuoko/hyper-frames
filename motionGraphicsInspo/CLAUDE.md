# motionGraphicsInspo — instructions

The canonical motion-graphics reference library. `README.md` is the source of
truth: a **two-tier** tagged index — a compact `## Quick index` scan table over full
`## Entries` blocks — where each entry pairs a hero still + a keyframe strip with a
written `Motion:` note. It teaches **motion** (cadence), not just look.

## Reading it (consumption — the `scene-design-decider` subagent's job)

The reader is the `scene-design-decider` subagent that `video-director` dispatches per
chunk; it does its own retrieval:

1. **Scan the `## Quick index` table** — one row per entry (`slug` · `archetype` ·
   `motion` · `energy` · `mood` · `use-when`). Match a beat's meaning to a row from the
   text alone. This is the cheap surface; reading it doesn't load the whole library.
2. **Drill into the matching `## Entries` block and open *only* that entry's strip**
   (`<slug>-strip.png`) — the strip shows the staging, the `Motion:` note carries the
   timing/ease the strip can't. Don't vision-parse the whole folder; open at most a
   couple of strips per decision.
3. **Adapt the cadence — never reproduce the scene.** Same family, never the same
   thing. Copy the reasoning, invent the block. Reaching for a reference is
   signal-driven and **non-quota** — most chunks cite nothing.

## Adding a reference (curation — the `motion-inspo-add` skill's job)

Do **not** hand-build entries. Invoke the **`motion-inspo-add`** skill, which:

1. runs `tools/inspo-ingest` (download bounded clip → scene-detect keyframes → tile
   the strip + extract the hero), then
2. reads the produced strip and authors the `Tags:` (from the README vocabulary),
   `Use when:`, and `Motion:` lines — the judgment the tool can't make — and appends
   the entry to `README.md`.

Keep filenames ↔ index entries in sync: every `<slug>.png` / `<slug>-strip.png` pair
has exactly one `README.md` entry, and vice versa.
