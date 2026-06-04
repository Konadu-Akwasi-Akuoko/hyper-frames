# Composition structure

Default to multi-block compositions, regardless of runtime. Each chunk you
author is its own block under `compositions/`, mounted from `index.html`. Smaller
blocks are easier to reason about, easier to lint, easier to swap or reorder when
the script changes, and a prerequisite for reuse. (The first project video,
`videos/why-text-is-hard-2026-05-07/`, shipped as a single file because it was
inaugural — that's done, don't retrofit it. Everything since splits from scene
one.)

> **The grading bar is fresh work, not a prior cut.** If this video was authored
> before and backed up (a git tag like `js-king-pre-director`, a `/tmp` copy, an
> archived `compositions/`), that backup is a *recovery backup* — **not** a design
> reference and **not** a target to reproduce. The new compositions you author
> *become* the grading bar (judged by a human + Opus). Treat `design.md` as the
> design source. You may read an old block only for the code **skeleton** below
> (scoped CSS, paused `window.__timelines`, tween-commenting) — never to copy its
> charts, layouts, or motion. Reproducing the backup makes the work circular and
> measures nothing.

This file covers *structure* — where a block comes from, the full-HTML-doc
skeleton, and the `index.html` wiring. Two sibling files cover the *look* and they
are not optional reading: **`visual-language.md`** (the background's subject-tone,
per-scene archetype variety so scenes don't all look alike, and the motion
language — slide-ins, layout reflow, constant subtle motion) and
**`assets-and-media.md`** (placing real images/video via labeled boxes the user
fills). A structurally-correct block that ignores those reads as a flat slideshow.

## Where a block can come from

1. **Official HyperFrames registry** — browse before authoring any primitive:

   ```bash
   npx hyperframes catalog                   # browse everything
   npx hyperframes catalog --type block      # blocks only
   npx hyperframes catalog --tag transition  # filter by tag
   npx hyperframes add <name>                # install + wire
   ```

   The catalog is broad — captions, shader/CSS transitions, VFX (shatter, portal,
   liquid, 3D device showcases), maps, a data chart, effects (grain, vignette,
   shimmer), social overlays, flowchart, logo outro. The **caption components are
   word-timeable** — a direct fit for transcript-as-timing-truth, usually better
   than hand-rolling text emphasis. If a registry item matches, invoke the
   `hyperframes-registry` skill and use `hyperframes add` — don't hand-roll over
   it. And don't default every beat to GSAP: `three`, `lottie`, `css-animations`,
   `waapi`, and `animejs` each own a lane.

2. **The user's personal `design-catalog/`** — an optional glance, separate from
   the official registry. It's the user's own library of reusable motion
   graphics, viewable at `design-catalog/index.html`, built by
   `tools/design-catalog`, and grown via the `design-catalog-add` skill. It's
   currently sparse (don't expect a hit), but it's where standout effects get
   parked for reuse, so check it as it fills up.

3. **Author it locally** — the default for this project. The registry skews
   toward branding, social overlays, shader transitions, and VFX. The
   **didactic-explainer primitives** that recur here — pixel grids, Bézier
   canvases, high-resolution rasters, side-by-side comparisons, live code
   reveals, algorithm visualizers — won't be in either catalog. Author them
   locally (next section).

## Author missing primitives as parametrized local blocks

When you author a didactic primitive, **don't inline it in `index.html`** and
don't bury a one-glyph-specific version in a single scene. Author it as a
**parametrized block**: declare its inputs with `data-composition-variables` on
the `<html>` root (or the composition root), and mount it with
`data-variable-values`.

The difference is "I built a bitmap grid for the letter A in this one video"
versus "I have a `bitmap-grid` block that takes any glyph at any resolution." The
first is a one-off; the second compounds across videos. Bias toward the second
from scene one — the third time the same primitive shows up, it should already be
a block, not another hand-coded copy.

A genuine one-off (a layout that will never recur) can be a plain local block
without variables. Use judgment: if you can imagine wanting it again, parametrize
it. If a local block proves useful across 2+ videos, consider promoting it to the
shared `design-catalog/` (via `design-catalog-add`) — but prove the abstraction
with the second video first; don't optimize for reuse prematurely.

## The block template — a full HTML document

A composition block is a **full HTML document**, not a `<template>` wrapper. The
canonical skeleton (matching the project's shipped blocks):

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1920, height=1080">
  <title>Scene NN — <name></title>
  <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
  <style>
    :root {
      /* design.md tokens — copy the palette so the block is self-contained */
      --bg: #0b0d12; --panel: #11141b; --border: #1f242c;
      --fg: #e8eaed; --soft: #c2c9d4; --muted: #7a8493;
      --accent: #f7df1e; --accent-2: #67e8f9; /* ... */
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body {
      width: 1920px; height: 1080px; overflow: hidden;
      background: transparent;          /* lets the substrate show through */
      font-family: "Inter", system-ui, sans-serif;
    }
    /* Scope every selector under the composition root id to avoid collisions */
    #scene-NN-slug { position: absolute; inset: 0; width: 1920px; height: 1080px; overflow: hidden; }
    /* ... block-specific layout ... */
  </style>
</head>
<body>
  <div id="scene-NN-slug" data-composition-id="scene-NN-slug" data-width="1920" data-height="1080">
    <!-- static hero-frame layout first -->
  </div>

  <script>
    window.__timelines = window.__timelines || {};
    const tl = gsap.timeline({ paused: true });

    // Entrance crossfade — the transition INTO this scene, at scene-local 0
    tl.fromTo("#scene-NN-slug", { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "power2.inOut" }, 0);

    // Every tween comments the word it lands on + the LOCAL timestamp.
    // global word start was e.g. 7.67; scene started at chunk_start, so local = 7.67 - chunk_start.
    // tl.fromTo("#thing", { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.45, ease: "power3.out" }, <local>);

    window.__timelines["scene-NN-slug"] = tl;
  </script>
</body>
</html>
```

Notes that matter:

- `background: transparent` on `html, body` — the persistent substrate layer
  sits behind every scene; an opaque block would hide it. That substrate is not a
  generic dark grid: it carries a **rationed subject tone** (a faint accent glow,
  no logo) and drifts slowly. See `visual-language.md` §1.
- **Scope CSS** under the composition root id (`#scene-NN-slug .thing`), because
  all blocks render into the same document tree at runtime.
- The timeline is **paused** and registered as
  `window.__timelines["<data-composition-id>"]`. The player owns playback;
  duration comes from the host's `data-duration`, not the GSAP timeline length.
  Never create empty tweens to pad duration.
- **Comment every tween with the word it punctuates and the local timestamp** —
  this is how transcript-as-timing-truth stays auditable. If you open an existing
  block (a shipped scene, or a `/tmp` backup of an earlier cut) it is **only** to
  copy this skeletal convention — the scoped CSS, the paused `window.__timelines`
  registration, the tween-commenting. **Do not lift its visual design — its
  charts, layouts, emphasis treatments, or motion. A prior/backup version is a
  backup, not a design reference or a grading bar; design every block fresh from
  `design.md`** (see the callout at the top of this file).
- Keep motion alive in dead zones (gaps between beats) with small settle pulses
  on already-visible elements rather than leaving the frame static. This is the
  floor, not the ceiling — `visual-language.md` §3 adds the rest of the motion
  language (edge slide-ins, layout reflow so new elements push rather than stack,
  and a constant low-amplitude tilt/drift so nothing sits perfectly still).
- **No exit animations** except on the final scene of the whole video — the
  transition into the next scene IS the exit. The final block is the one place a
  fade-to-black is allowed.

For the GSAP specifics (easing, stagger, position parameter, timeline nesting),
invoke the `hyperframes` skill and its `gsap` adapter — this file only covers
what's project-specific.

## The host-wiring template — index.html

Mount each block from `index.html` as an absolutely-positioned host `<div>`
inside `#root`. The shape (from the shipped js-king `index.html`):

```html
<div id="root" data-composition-id="main" data-start="0" data-duration="<full audio length>"
     data-width="1920" data-height="1080">

  <!-- Persistent background behind every scene (high track-index, full length).
       Subject-toned + drifting, never a logo — see visual-language.md §1. -->
  <div id="substrate-layer" data-composition-id="substrate"
       data-composition-src="compositions/substrate.html"
       data-start="0" data-duration="<full>" data-track-index="7"
       data-width="1920" data-height="1080"
       style="position: absolute; inset: 0; z-index: 0"></div>

  <!-- Voiceover — the timing source of truth. -->
  <audio id="voiceover" src="audio/voiceover.mp3"
         data-start="0" data-duration="<full>" data-track-index="9" data-volume="1"></audio>

  <!-- One host per scene block. Append these as you author each chunk. -->
  <div id="scene-NN" data-composition-id="scene-NN-slug"
       data-composition-src="compositions/NN-slug.html"
       data-start="<chunk_start − 0.5>" data-duration="<spans to next chunk's first word>"
       data-track-index="1"            <!-- alternate 1 / 2 vs the previous scene -->
       data-width="1920" data-height="1080"
       style="position: absolute; inset: 0; z-index: N"></div>
</div>

<script>
  window.__timelines = window.__timelines || {};
  window.__timelines["main"] = gsap.timeline({ paused: true });
</script>

<!-- sfx-layer is appended by tools/sfx-plan during Step H; music-layer later by audio-bed-music. -->
```

Wiring rules:

- `data-start = chunk_start − 0.5` and **alternate `data-track-index` 1/2**
  versus the previous scene, so both scenes are mounted during the 0.5s overlap
  and the incoming transition can render over the outgoing scene. (Abutting
  blocks with no overlap, all on track-index 1, is the older js-king pattern —
  standardize on the overlap so transitions always have something to cross over.)
- **The seam must not show two legible text layers at once.** Both scenes *are*
  mounted during the 0.5s overlap — if each just opacity-crossfades its full
  layout, the outgoing scene's text and the incoming scene's text render on top of
  each other and collide (the scene-2→3 "how / infrastructure" mush). Avoid this:
  the transition is a **cover/occlude**, not a dual text dissolve. Either (a) the
  outgoing scene fades/clears its *foreground text* out across the overlap before
  the incoming text becomes legible, or (b) the incoming scene enters with an
  opaque-enough wipe/slide/panel that occludes the outgoing one. Two readable text
  blocks may never share the frame at a seam. Verify by snapshotting *at the seam*
  (`prev_end − 0.25`) in the visual-QA loop. Mechanics: `visual-language.md` §3
  (reflow + slide), `verify-and-preview.md` (the seam-collision check).
- `data-duration` runs to the next chunk's first word, so there's never a visual
  gap where no scene is mounted.
- Keep `#root` `data-duration` at the full voiceover length from the start, so
  the timeline length is stable as you add scenes.
- Never start/restart the preview to check wiring — see
  `reference/verify-and-preview.md`.
