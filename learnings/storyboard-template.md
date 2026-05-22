# Storyboard template

Copy this file to `videos/<slug>-<date>/storyboard.md` and fill it in. Delete this
top block once you start.

**How to use**
- Draft the beats in **script order** first (you can do this from `script.md` alone).
- Once the voiceover is recorded and `transcript.json` exists, do a second
  **timing-enrichment pass**: replace every placeholder timestamp with the real
  word `start`/`end` from `transcript.json` (filter it, don't read it whole — see
  the project `CLAUDE.md`). Round numbers are a code smell; anchor on the spoken word.
- At build, snap block boundaries to the nearest `spacing` row in the transcript.
- A storyboard beat ≈ a `compositions/*.html` block. Plan the block split here.
- This is a plan of **intent and candidate tools, not a locked recipe**. Name
  candidates, leave room to invent during authoring. (See the spec-over-restriction
  learnings before you over-specify.)

---

## Global direction

- **Format:** 1920×1080 · ~<runtime> · single audio track `audio/voiceover.mp3`.
- **Voiceover:** recorded own voice (default) — cut in `tools/audio-editor`; the
  Scribe v2 `transcript.json` is timing truth. (TTS via `voiceover-elevenlabs-v2`
  only if this video took the TTS path.)
- **Style basis:** <the arc / motif in one or two lines — e.g. iceberg subversion,
  the recurring visual spine, the through-line>.
- **Design tokens:** *see `design.md`* (palette, type, motion). Reference it here;
  don't restate it. <If no `design.md` yet, jot the proto-palette and promote it later.>
- **Project constraints:** no editorial chrome (no scene labels / part numbers /
  running timecodes). Ambient decoratives (glows, grid, ghost type) are fine.
  Multi-block from scene one. Check the catalog before hand-rolling.

---

## Tooling menu — pick per beat, don't default to GSAP

Each beat below names an **Adapter** and optional **Catalog candidates**. Choose
from these; reach past GSAP whenever another tool owns the lane.

### Animation adapters (`.claude/skills/<name>/`)
| Adapter | Best for | Determinism hook |
|---------|----------|------------------|
| `gsap` | primary scene choreography, multi-element timelines, staggers | paused timeline on `window.__timelines[id]` |
| `three` | 3D objects, device showcases, depth/camera moves, shader plates | render from HF time on `hf-seek` event |
| `lottie` | After Effects exports, logo/icon reveals, decorative accents | `autoplay:false`, register on `window.__hfLottie` |
| `css-animations` | ambient loops, grain/shimmer/glow, simple one-element entrances | finite iterations, `animation-fill-mode: both` |
| `waapi` | lightweight data-driven DOM motion, generated keyframes | `fill:"both"`, paused; adapter seeks `currentTime` |
| `animejs` | compact SVG/DOM micro-flourishes | `autoplay:false`, register on `window.__hfAnime` |

GSAP stays the primary path; the others are deliberate choices for a specific beat.

### Catalog (browse: https://hyperframes.heygen.com/catalog/)
Install + wire: `npx hyperframes add <slug>` (slug = the name in the catalog URL),
and **invoke the `hyperframes-registry` skill before wiring**.

| Group | What's in it | Reach for it when |
|-------|--------------|-------------------|
| Captions (15) | clip-wipe, editorial-emphasis, highlight, kinetic-slam, pill-karaoke, weight-shift… | **word-timed text treatment** — direct fit for transcript-as-timing-truth |
| Shader Transitions (14) | whip-pan, cross-warp-morph, flash-through-white, sdf-iris, cinematic-zoom… | a beat-to-beat transition with punch |
| CSS Transitions (13) | dissolve, push, grid, blur, scale, 3d… | a lighter scene transition |
| HTML-in-Canvas / VFX (7) | shatter, portal, liquid-glass, magnetic, vfx-iphone-device | break/reveal effects, 3D device frames |
| Showcases (7) | app-showcase, 3d-ui-reveal, money-count… | a pre-built set piece |
| Maps (6) | world-map, us-map (+ bubble/hex/flow) | geography |
| Data (1) | data-chart | bars / lines / a stat reveal |
| Effects (6) | grain-overlay, vignette, shimmer-sweep, texture-mask-text… | atmosphere / accents |
| Social Overlays (7) | x-post, reddit-post, macos-notification, yt-lower-third… | a quoted post / notification |
| Blocks | flowchart, logo-outro | a diagram / an outro |

**Decision rule:** check the catalog first. If nothing matches and it's a
didactic-explainer primitive (pixel grid, code reveal, custom diagram), author it as
a parametrized local block (see `CLAUDE.md` "Author missing primitives as
parametrized local blocks"). Don't inline it in `index.html`.

---

## Block plan

| # | block file | window (s) | dur | beat |
|---|------------|-----------|-----|------|
| 00 | `compositions/00-<name>.html` | 0.0 – <t> | <d> | <beat> |
| 01 | `compositions/01-<name>.html` | <t> – <t> | <d> | <beat> |
| … | | | | |

---

## Beat sheet

> Repeat this block per beat. Keep each field to a line or two.

### 00 · <BEAT NAME>
- **Window:** <start> – <end> · `compositions/00-<name>.html`
- **Anchors:** "<spoken phrase>" @ **<t>** · "<phrase>" @ **<t>**
- **On screen:** <what the viewer sees>
- **Camera / mood:** <static / push-in / travel; the feeling>
- **Adapter:** <gsap | three | lottie | css-animations | waapi | animejs>
- **Catalog candidates:** <slug, slug — or "none; hand-rolled block">
- **Motion:** <the key tweens, each keyed to an anchor timestamp>
- **Depth:** <far → near layers>
- **Transition in / out:** <how it enters / leaves; catalog transition candidate>
- **SFX intent:** <pre-note for the later sfx-author pass>
- **Blocks used:** <local block names>

---

## Reusable blocks to author

| Block | Params | Used by beats |
|-------|--------|---------------|
| `<name>` | <inputs> | <beats> |

## Open questions for the human (before build)
- <asset sourcing / licensing>
- <faithful vs. stylized mocks>
- <claims to keep hedged per fact-check.md>
- <missing design.md?>
