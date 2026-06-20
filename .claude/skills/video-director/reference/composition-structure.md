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
   shimmer), social overlays, flowchart, logo outro. **Do not use the `vignette`
   effect on the substrate / full-frame background** — edge vignettes band and smear
   at YouTube bitrates (`visual-language.md` §1, hard rule). The **caption components are
   word-timeable** — a direct fit for transcript-as-timing-truth, usually better
   than hand-rolling text emphasis. If a registry item matches, invoke the
   `hyperframes-registry` skill and use `hyperframes add` — don't hand-roll over
   it. And don't default every beat to GSAP — choose the library by the **shape**
   of the motion: `gsap` (choreography / multi-step sequence), `animejs` (swarms /
   coordinated grids via stagger), `three` (3D / depth / camera), `typegpu`
   (GPU/WGSL shaders), `lottie` (hand-illustrated loops), `waapi` /
   `css-animations` (one simple native enter/exit). The verdict's `MOTION-LANE`
   carries the call; once chosen, invoke the matching `hyperframes:<adapter>`
   skill before authoring that beat's motion.

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

When a talking-head source is present (`reference/talking-head.md`), a **PIP-capable
archetype must accept a "face safe-zone" region input** — a declared variable
reserving the dead space the bordered face inset sits in, so the live graphic is
never occluded. That reservation is a *structural input* the block declares here; the
safe-zone **geometry** (where the band sits, portrait danger-zone dodging) defers to
`visual-language.md`. A full-bleed archetype that leaves no such region cannot host PIP.

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
      /* design.md tokens — copy the palette so the block is self-contained.
         Light-canvas default; on white --fg is dark ink, --panel is lighter-than-bg,
         --border is a light hairline. See visual-language.md §1. */
      --bg: #f7f8fa; --panel: #ffffff; --border: #d8dbe0;
      --fg: #14171c; --soft: #3a4150; --muted: #6b7280;
      --accent: #f7df1e; --accent-2: #67e8f9; /* subject-tinted — but for accent-colored TEXT/thin emphasis on white, derive a darker/saturated accent-INK variant; a pale accent is too low-contrast as ink on white */
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body {
      width: 1920px; height: 1080px; overflow: hidden;
      background: transparent;          /* lets the (now light) substrate show through */
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
  generic grid: on the **light-canvas default** it carries a **rationed subject
  tone** as a SUBTLE DARK-ON-LIGHT gesture — a low-opacity accent-tinted wash or a
  faint dark hairline grid, never an additive glow (invisible on white) — and drifts
  slowly. See `visual-language.md` §1. The substrate may also host a
  **human-supplied background image** — a `background` box with
  `data-asset-scope="substrate"` (a backdrop that should persist across scenes, e.g.
  a blueprint grid or sky), promoted here instead of into a single block. It still
  **RECEDES** (lightens toward base, decorative alpha drops) behind busy scenes so
  dark foreground always wins contrast. Contract: `assets-and-media.md`. **QA hazard:
  on the white default a MISSING/unmounted substrate renders as a correct-looking
  white frame — the old dark tell is gone — so verify `#substrate-layer` is actually
  mounted by inspecting `index.html`, not by glancing at a frame.** **When a
  talking-head source is present
  (`reference/talking-head.md`), this transparent background is load-bearing for the
  GRAPHICS→FACE hand-off** — the running `#face-layer` is revealed by clearing the
  scene above it, so an opaque scene background would wall the face off permanently and
  break the mode transition. Keep it transparent; tint via scene-local fills, never an
  opaque `html, body`.
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
- **Entrance invariant — nothing may render at full opacity at scene-local t=0.**
  Because `data-start = chunk_start − 0.5`, t=0 sits 0.5s *inside* the overlap with
  the previous scene; any element opaque at t=0 is drawn solid on top of the
  *outgoing* scene and bleeds across the seam (this is the scene-21 memory-gauge
  bug: a `.mem`/`.ml` gauge column with no fade rendered over the previous Apache
  scene). Every element that appears must satisfy **one** of: **(a)** it is covered
  by the scene-root entrance crossfade at the top of the timeline
  (`tl.fromTo("#scene-NN-slug", { opacity: 0 }, { opacity: 1, … }, 0)`), which fades
  the *whole* scene — every child — in together; or **(b)** it carries its own
  `opacity: 0` baseline + a `fromTo` fade-in. Static stage scaffolding (an empty
  gauge frame the fill later climbs into, a baseline axis) is allowed **only** when
  the root crossfade covers it. The mental check at t=0: the scene is either fully
  transparent (root fade still at 0) **or** has no solid children yet. A per-element
  motion tween that animates `height`/`x`/`color` but never touches `opacity` does
  **not** count as an entrance — that was exactly the gauge's failure mode.
- **No exit animations** except on the final scene of the whole video — the
  transition into the next scene IS the exit. The final block is the one place a
  fade-to-black is allowed.

For the chosen library's specifics, invoke the matching `hyperframes:<adapter>`
skill **before authoring that beat's motion** — `hyperframes:gsap` (easing,
stagger, position parameter, timeline nesting), `hyperframes:animejs`,
`hyperframes:three`, `hyperframes:typegpu`, `hyperframes:lottie`,
`hyperframes:waapi`, `hyperframes:css-animations`. Each carries the adapter's
`window.__hf*` registration + seek-safe determinism patterns; this file only
covers what's project-specific.

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

  <!-- Face layer — ONLY when a talking-head source is present (`reference/talking-head.md`).
       One persistent host spanning the whole runtime, sized to the ROOT dims (not the
       source's), seek-driven, never autoplay/loop. The inner <video> is MUTED — this is
       the one case where the source audio IS the voiceover, so the muted picture rides
       above while the <audio id="voiceover"> still drives all timing. Omit this host
       entirely on the default graphics-only pipeline. -->
  <div id="face-layer" data-composition-id="face"
       data-start="0" data-duration="<full>" data-track-index="8"
       data-width="1920" data-height="1080"
       style="position: absolute; inset: 0; z-index: 1">
    <video src="assets/video/talking-head.mp4" muted preload="auto"
           style="width: 100%; height: 100%; object-fit: cover"></video>
    <!-- currentTime tracks GLOBAL composition time on every hf-seek (zero offset —
         see talking-head.md §seek); never autoplay/loop. z-index + geometry animate
         per mode (below). -->
  </div>

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
- **The seam must not show any element from one scene rendered solid over the
  other.** Both scenes *are* mounted during the 0.5s overlap, so the failure has
  two shapes. **(1) Text-on-text:** if each scene just opacity-crossfades its full
  layout, the outgoing scene's text and the incoming scene's text render on top of
  each other and collide (the scene-2→3 "how / infrastructure" mush). **(2) Static
  graphic bleed:** an incoming element with *no entrance* (no `opacity:0`+fade, not
  covered by the root crossfade) is drawn at full opacity from scene-local t=0,
  which is 0.5s *inside* the overlap — so it sits solid on top of the still-present
  previous scene (the scene-20→21 memory-gauge bleed). This is the **Entrance
  invariant** above; a graphic, label, panel, or shape bleeds the same way text
  does. Avoid both: the transition is a **cover/occlude**, not a dual dissolve, and
  every element obeys the entrance invariant. Either (a) the outgoing scene
  fades/clears its *foreground* out across the overlap before the incoming content
  becomes legible, or (b) the incoming scene enters with an opaque-enough
  wipe/slide/panel that occludes the outgoing one. No element from either scene may
  share the seam frame at full strength with the other. Verify by snapshotting *at
  the seam* (`prev_end − 0.25`) in the visual-QA loop. Mechanics:
  `visual-language.md` §3 (reflow + slide), `verify-and-preview.md` (the seam-bleed
  check).
- `data-duration` runs to the next chunk's first word, so there's never a visual
  gap where no scene is mounted.
- Keep `#root` `data-duration` at the full voiceover length from the start, so
  the timeline length is stable as you add scenes.
- **Face-layer mode + z behavior — only when a talking-head source is present**
  (`reference/talking-head.md` owns the full policy). The `#face-layer` host (track-index
  8) is one element whose **geometry animates and whose z-index flips per mode**: in
  GRAPHICS mode it sits **below** the scene graphics (the opaque-enough scene covers it,
  face running hidden underneath); in PIP it **lifts above** to a bordered, drop-shadowed
  corner inset — the **PIP inset border traces `--fg` or `--accent`, NEVER `--border`
  (now a light hairline that disappears against the frame) and NEVER `--bg`/white
  (vanishes on white → reads as a glitch); the drop shadow is the primary depth cue
  on white** (see `reference/talking-head.md`). In FACE it fills the frame with the
  scene transparent over it. The
  GRAPHICS↔PIP z-flip is a **discrete jump fired only while the face is covered** (never
  tweened, never on screen); while the face is visible only opacity + geometry move. The FACE/GRAPHICS/PIP
  mode is *realized here* by revealing / hiding / insetting that one host at the exact
  transcript word-boundary timestamps from the `MODE:` verdict line — transitions
  **crossfade or clean-push on natural pauses, never mid-clause** (same seam discipline
  as scene entrances above). The locked face layer is **exempt from the Entrance
  invariant** — it is supposed to persist across every seam; the invariant governs the
  graphics/PIP revealed *on top*. See `talking-head.md` for the verdict grammar, the
  seek-with-global-timestamps rule, and the PIP hard rules.
- Never start/restart the preview to check wiring — see
  `reference/verify-and-preview.md`.
