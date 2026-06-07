# motionGraphicsInspo — the motion reference index

The canonical motion-graphics reference for this project's videos. Unlike a folder
of look stills, every entry here teaches **motion** — the cadence that separates a
scene that's merely synced from one that's *alive*: what enters, in what order, the
easing and overshoot, where it settles, the camera move.

Each reference is derived from a real YouTube clip (a beat someone got right) into
two artifacts plus a written note:

- a **hero still** (`<slug>.png`) — the at-a-glance look,
- a **keyframe strip** (`<slug>-strip.png`) — several frames of the beat tiled
  left-to-right, so the *staging* (what appears when) is legible in one image,
- a **`Motion:` note** in this index — the *cadence* a still sequence can't encode
  (timing, ease, overshoot, drift).

> Why a strip and not a GIF: an animated GIF read by an agent collapses to its
> first frame — motion is invisible. A tiled strip reads in full. So motion reaches
> the reader as **strip + note**, never as animation.

## How this index is read (progressive disclosure, two tiers)

The reader is the **`scene-design-decider`** subagent (dispatched per chunk by
`video-director`), which does its own retrieval. The index is built in two tiers so
that retrieval stays cheap as the library grows:

1. **Scan the `## Quick index` table first.** One compact row per entry — `slug`,
   `archetype`, `motion` verbs, `energy`, `mood`, and a one-line `use-when`. This is
   the search surface: match a beat's *meaning* to a row from text alone. The table
   stays scannable even at a hundred entries; reading it is a few hundred tokens, not
   the whole library.
2. **Drill into the matching `## Entries` block, and open *only* that entry's strip.**
   When a row fits the beat in hand, jump to its full entry (the `Motion:` note carries
   the cadence the row can't) and `Read` its `<slug>-strip.png` for the staging. Don't
   vision-parse the whole folder — the two tiers exist so you open at most a couple of
   strips per decision.
3. **Adapt the cadence — never reproduce the scene.** A reference may land in the same
   *family* as your block; it must not be the same thing. Copy the reasoning (the
   stagger, the settle, the push), invent the scene. Lifting a reference's literal
   layout makes the work derivative and homogenises the channel. Citing nothing is a
   first-class outcome — most beats fit no entry; this is **not a quota**.

## Entry schema — two parts per reference

Every reference contributes **both** a Quick-index row **and** a full Entries block,
kept in sync (same slug, same PNG pair).

**Quick-index row** (one line in the `## Quick index` table):

```
| [<slug>](#<slug>) | <archetype> | <verb>, <verb> | <energy> | <mood> | <one-line use-when> |
```

**Entries block** (the full detail under `## Entries`):

```
### <kebab-slug>
- Hero: `<slug>.png` · Strip: `<slug>-strip.png`
- Tags: motion=[<verb>, <verb>] · archetype=<archetype> · energy=<energy> · mood=<mood>
- Use when: <one line — the beat meaning this fits>
- Motion: <2-4 sentences — what enters, in what order, easing/overshoot, where it settles, camera move>
- Motion-metrics: energy=<calm|measured|punchy|frenetic> · cadence=<punctuated|continuous> · spatial=<localized|full-frame> · gate=<eased|continuous> · src=scan
  (flow: motion_energy=<m> · eased_energy_share=<s> · sparsity=<p> · spatial_concentration=<c> · mov_texture=<t>)
- Source: <youtube-url> @ <MM:SS-MM:SS>
```

The `### <kebab-slug>` heading is what the Quick-index row's `[<slug>](#<slug>)` link
anchors to, so the reader jumps straight from row to detail.

The `Motion-metrics:` line carries **objective measured values** computed by a `scan`
pass over the source — distinct from the human-judged `energy`/`mood` in the `Tags:`
line, which are curatorial reads of mood, not measurements. It is present **only for
scan-sourced entries** and is omitted entirely for clip-mode hand-captured ones (which
have no manifest to copy from). The four categorical tokens (`energy`, `cadence`,
`spatial`, `gate`) are what `scene-design-decider` ranks on as a **secondary signal**
beneath the prose `Tags:`/`Motion:`; the parenthetical raw floats are provenance, not
something the reader matches on.

### Tag vocabulary

A controlled core so the index stays scannable — extend a dimension when a beat
genuinely needs a word that isn't here, but prefer an existing one.

- **motion** (multi-value, the cadence verbs): `stagger`, `overshoot`, `settle`,
  `slide-in`, `wipe`, `mask-reveal`, `marker-sweep`, `typewriter`, `count-up`,
  `morph`, `snap`, `pop`, `scale-bloom`, `kinetic-type`, `parallax-push`,
  `parallax-drift`, `camera-orbit`, `draw-on`, `card-flip`, `accordion-reflow`,
  `blur-rack`, `glitch`, `particle`.
- **archetype** (the layout family): `stat-hero`, `kinetic-type`, `diagram-build`,
  `side-cutout`, `split-contrast`, `quote-card`, `checklist`, `code-reveal`,
  `timeline`, `map`, `device-mockup`, `collage`, `title-card`, `lower-third`.
- **energy**: `calm` · `measured` · `punchy` · `frenetic`.
- **mood**: `neutral` · `serious` · `playful` · `triumphant` · `tense` · `ominous`
  · `warm` · `clinical`.

## Adding a reference

Use the **`motion-inspo-add`** skill — it runs the backing tool
(`tools/inspo-ingest`, which downloads the bounded clip, scene-detects the
keyframes, and tiles the strip), then reads the strip and authors the `Tags:` /
`Use when:` / `Motion:` lines (the judgment the tool can't make) and appends **both**
the Quick-index row and the Entries block below. Keep every `<slug>.png` /
`<slug>-strip.png` pair in sync with exactly one row and one entry.

---

## Quick index

_Empty — references are seeded from source channels via `motion-inspo-add`._

| Slug | Archetype | Motion | Energy | Mood | Use when |
|---|---|---|---|---|---|

## Entries

_Empty — references are seeded from source channels via `motion-inspo-add`._
