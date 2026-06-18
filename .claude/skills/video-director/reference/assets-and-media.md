# Assets & media — real images and video via labeled boxes

Code-and-text scenes can only go so far. The beats that land hardest use **real
imagery** — an emotion-matched reaction shot, a product logo, a photo of the thing
being described, a short clip — placed as a full-height side cutout against the substrate.
You can't generate those photos. The user can: *"put in the box what you want and I'll
make it happen."* This file is the contract for that handoff.

The principle: **you author a labeled placeholder ("box"); the user fills it.** The box
reserves the exact space and records exactly what's wanted, so layout and motion are
verifiable *before* the real asset exists — and the user gets one clean list of what to
supply.

## Declaring an asset box

Where a scene wants an image or video, place a styled placeholder `<div>` instead of an
`<img>`, carrying the request as data-attributes:

```html
<div class="asset-box"
     data-asset="surprised-celebrity"          <!-- stable id; becomes the filename stem -->
     data-asset-class="reaction"                <!-- reaction | logo | glyph | photo (routes sourcing) -->
     data-asset-kind="image"                    <!-- image | video | svg -->
     data-asset-desc="Surprised celebrity reaction face, looking left toward the text"
     data-asset-emotion="surprised"             <!-- reaction boxes: the beat's emotion (drives picture choice) -->
     data-asset-treatment="cutout,grain,duotone" <!-- bg-removed + image-prep presets -->
     data-asset-placement="right-full-height"   <!-- where it sits -->
     style="/* the real footprint: position + size it exactly where the asset goes */">
</div>
```

A **referent** box (showing a named thing, not a reaction) carries `data-asset-class` of `logo` /
`glyph` / `photo` and a `data-asset-referent` naming the exact thing, and usually drops
`data-asset-emotion`:

```html
<div class="asset-box"
     data-asset="javascript-logo"
     data-asset-class="logo"                    <!-- → Iconify logos: / local assets/icons/ -->
     data-asset-kind="svg"
     data-asset-referent="javascript"           <!-- the exact named thing; drives the icon slug / search -->
     data-asset-desc="The JavaScript brand logo, igniting beside the word"
     data-asset-placement="inline-mark"
     style="/* footprint where the mark sits */">
</div>
```

A `photo`-class referent (e.g. `data-asset-referent="data center"`) also gets a
`data-asset-credit` slot once sourced, since Wikimedia photos carry an attribution obligation (see
the routing section).

A **`background`** box is the full-frame backdrop case — a real scene you can't draw (a wooden
desk, a blueprint render, a skyscraper sky), usually one you drew from a `../../motionGraphicsInspo/`
reference. It is **always human-supply** (never `image-sourcer` — see the carve-out below):

```html
<div class="asset-box"
     data-asset="wooden-desk-backdrop"
     data-asset-class="background"              <!-- full-frame backdrop; human-supply only -->
     data-asset-kind="image"
     data-asset-desc="Warm wooden desk seen at a perspective tilt, soft vignette — riffs on
                      the motionGraphicsInspo wooden-desk reference, but no article on it
                      (our article is a separate foreground element)"
     data-asset-scope="scene"                   <!-- scene | substrate (does it persist?) -->
     data-asset-placement="background"
     style="position:absolute; inset:0; z-index:0; /* sits behind the scene's foreground */">
</div>
```

- **`data-asset-desc`** on a background box must name the **motionGraphicsInspo reference it
  riffs on and how it diverges** — that is the "put in the box what you like and I'll get it"
  handoff. Same family, not the same shot.
- **`data-asset-scope`** — `scene` (this beat only → a scene-local full-frame box) or `substrate`
  (persists across scenes / sets the video's mood → promote it to the substrate layer, one request,
  see `composition-structure.md`). Decide by whether the backdrop should outlive this scene.
- Animate the box as the backdrop will move (a slow drift/parallax), exactly like any other box.

- **`data-asset`** — a stable kebab id, unique within the video. It is the filename
  stem the user fills (`assets/images/surprised-celebrity.png`) and how you find the box
  again to swap it.
- **`data-asset-class`** — the lane: `reaction` (emotion/meme/face), one of the three
  **referent** kinds `logo` / `glyph` / `photo`, or **`background`** (a full-frame backdrop).
  This routes sourcing — see "Two kinds of image" below. A `logo`/`glyph` saves an SVG to
  `assets/icons/`; `photo`/`reaction`/`background` save a PNG (to `assets/images/` and
  `assets/backgrounds/` respectively). `background` is the one class **never auto-sourced** —
  it's always human-supply via the shopping list.
- **`data-asset-referent`** — *(referent boxes)* the exact named thing to show (`javascript`,
  `data center`, `Brendan Eich`); drives the icon slug or photo search. Referent boxes usually
  omit `data-asset-emotion`.
- **`data-asset-desc`** — a precise sentence: subject, framing, direction it faces.
  "Emotion-matched" means the *right* picture for the beat (surprised/crying/smug/angry),
  not generic stock. Name the emotion in `data-asset-emotion`.
- **`data-asset-treatment`** — `cutout` (background removed) plus any `image-prep`
  presets (`grain`, `duotone`, `halftone`, `vintage`) so every supplied photo lands on
  one consistent look. See the tool section below.
- **`data-asset-placement`** — usually a **full-height side cutout** (`left-full-height`
  / `right-full-height`), the signature move; also `bottom`, `inset`, `card-inline`
  (e.g. a reaction tucked into a quote card).
- **`style`** — give the box the asset's *real* footprint and position. It must occupy
  the space the final image will, so `inspect`/`snapshot` measure the true layout.

**Render the box visibly** so the preview is honest: a dashed accent border, a faint
fill, and the `data-asset-desc` text centered inside (plus a small "📷 image" / "🎬
video" tag). Scope this `.asset-box` style in the block like everything else. Animate
the *box* now (slide-in, tilt) exactly as the real asset will move — when the file
arrives you swap the element and the motion already works.

Once a reaction box is in play on a contrast beat, see `visual-language.md` §2: let
the image carry the contrast — don't *also* dim the opposing text or divide the frame.

## Filling a box yourself — the `image-sourcer` agent

The box stays the spec; what changes is **who fills it**. Rather than handing the user a
find-the-file errand for every beat, dispatch the **`image-sourcer`** subagent (the Agent
tool, `model: sonnet`) to source the asset *for* the box — **except `background` boxes,
which are excluded from auto-sourcing.** A full-frame backdrop (a bespoke desk, a blueprint
render, a skyscraper sky) is not findable stock and isn't worth a poor Pinterest/Wikimedia
pick; it always goes to the shopping list for the user's manual review pass. So the
`image-sourcer` lane below covers `reaction` / `logo` / `glyph` / `photo` only. It **routes
on `data-asset-class`**:
a `reaction` box drives Chrome — Pinterest first (the user is logged in there), open-web as
fallback — and treats the cutout through `image-prep`; a `logo`/`glyph` box is a plain Iconify
fetch (local `assets/icons/` checked first) saved as a static SVG; a `photo` box pulls a
licensed Wikimedia Commons image and treats it. Every path lands a static file at the box's
target so the composition renders deterministically (see "Two kinds of image" below).

Dispatch it once the box is authored (its footprint and `data-asset-*` spec are the brief),
passing the agent the box's fields verbatim plus the absolute `video_dir`:

> `video_dir`, `asset_id` (= `data-asset`), `class` (= `data-asset-class`), `referent`
> (= `data-asset-referent`, for referent boxes), `description` (= `data-asset-desc`),
> `emotion` (= `data-asset-emotion`, reaction boxes), `treatment` (= `data-asset-treatment`),
> the placement + box pixel height, and any specific search phrases you have in mind.

It returns a structured report: source used, chosen URL, dimensions, the treated path, a
**confidence** + why, runner-up URLs, and any flags (watermark, busy background, low res).
Treat it as **advisory** — *you* decide whether to swap its pick in. On `high` confidence,
swap the box for the `<img>` (see below) and re-run the visual-QA loop against the real
pixels. On `low` confidence or `status: no-suitable-asset`, fall back to the shopping list
below — let the human supply that one. So the human round-trip becomes the **exception for
the hard cases**, not the default for every box.

**On a failed source, leave the box standing — never delete it.** If nothing suitable turns up
(agent or you), the placeholder `<div>` stays exactly where it is so the layout still reserves
the space and the human knows precisely what to source. A failure removes *nothing*; the box is
the durable contract, and an empty frame where a box used to be is worse than a labeled box still
waiting.

(The agent loads at session start — a freshly added or edited `image-sourcer.md` is only
dispatchable in the *next* session, not the one that wrote it. See
`prompt-evaluation/CLAUDE.md`'s reload-trap note.)

## Two kinds of image, and where each comes from

There are two reasons to put a real picture on screen, and they route to different sources.
**Reaction** imagery reacts *for* the viewer (a laughing cutout on an ironic beat). **Referent**
imagery shows *the named thing itself* — split into a brand/tech **logo**, a concept **glyph**, or
a **photo** of a real place/person/object. The decision of *whether* a beat earns referent imagery
is the three-part gate in `visual-language.md` §2 (named + recognisable-on-sight + adds-meaning-
words-can't, else stay type/diagram); this section is *where the asset comes from* once you've
decided it's earned.

**The on-camera take is neither kind** — when a talking-head source is present, its
footage is a **non-asset-box media source** outside this `reaction`/`logo`/`glyph`/`photo`/
`background` routing entirely: creator-supplied, transcoded once, **never image-sourced and
never on the shopping list**. It mounts as the seek-driven `#face-layer` host, not a box you
fill; see `reference/talking-head.md`.

| `class` | the beat | primary source | fallback | saved as |
|---|---|---|---|---|
| `logo` | names a product/language/company with a known mark ("JavaScript", "React", "Netflix") | **local `assets/icons/`** (the project ships many tech logos — check first) → Iconify `logos:` set (true coloured mark) | open-web (`<name> logo png transparent`) | static **SVG** → `assets/icons/<id>.svg` |
| `glyph` | an abstract-but-iconic concept with a settled shorthand ("infrastructure"→server, "security"→lock, "database"→cylinder) | Iconify mono sets (`mdi`/`lucide`/`solar`/`tabler`), `currentColor`-tintable to the accent | a different set / synonym → open-web; or **draw a diagram** instead | static **SVG** → `assets/icons/<id>.svg` |
| `photo` | a specific notable real thing where realness/scale/identity is the payoff ("a humming data center", "Brendan Eich") | **Wikimedia Commons** (freely-licensed, capture artist + license + source URL) | open-web image search | treated **PNG** → `assets/images/<id>.png` |
| `reaction` | an ironic/comedic/emotional turn — react for the viewer | **Pinterest** (logged-in) | open-web image search | treated **PNG** → `assets/images/<id>.png` |
| `background` | a full-frame backdrop the scene can't draw (wooden desk, blueprint render, sky) | **human-supply** — the shopping list, sourced in the user's manual review pass (**never `image-sourcer`** — bespoke/AI-rendered backdrops aren't findable stock) | the user | treated **PNG** → `assets/backgrounds/<id>.png` |

Three rules cut across all of them:

- **Determinism — fetch at author time, save a static file.** Every asset becomes a file on disk
  under `assets/` *before* render. Never wire a runtime `<iconify-icon>` web component or a CDN
  `src` into a composition — it would hit the network mid-render and break the offline `snapshot`/
  `render`. The saved SVG/PNG is the deliverable.
- **Icons aren't photos.** A `logo`/`glyph` SVG is *not* run through `image-prep` — it's already
  clean vector. A coloured `logos:` brand mark is used verbatim (don't recolour it); a monochrome
  glyph stays `currentColor` and the block tints it to `accent`/`fg` in CSS.
- **Wikimedia photos carry an attribution obligation.** CC BY / CC BY-SA require credit. The agent
  captures `artist` + `license` + `sourceUrl`; record it on the box (`data-asset-credit`) so the
  user can decide how to credit. NC/ND-licensed images are flagged, not auto-used.

## The shopping list (the fallback)

For any box the agent couldn't fill (or you chose not to auto-source), at the end of an
authoring pass (Step F/G) scan the batch's blocks for every still-unfilled `data-asset`
box and emit **one table** to the user — their single to-do:

| id | kind | scene | description | emotion | treatment | placement | target path |
|---|---|---|---|---|---|---|---|
| surprised-celebrity | image | 01 | Surprised celeb facing left | surprised | cutout,grain,duotone | right-full | `assets/images/surprised-celebrity.png` |
| wooden-desk-backdrop | image · **bg (scene)** | 03 | Wooden desk, perspective tilt — riffs on motionGraphicsInspo desk reference, no article on it | — | grain | background | `assets/backgrounds/wooden-desk-backdrop.png` |
| blueprint-grid | image · **bg (substrate)** | — | Blueprint grid w/ ruler border — riffs on motionGraphicsInspo blueprint reference; persists, promote to substrate | — | — | background | `assets/backgrounds/blueprint-grid.png` |

Surface it alongside the seek target ("Seek to 0.0s… and drop these N assets"). The user
replies by placing files at the listed paths (project convention:
`assets/images/`, `assets/memes/`, `assets/video/`, `assets/backgrounds/`; `assets/icons/`
already holds many tech logos you can use directly — check there before requesting a logo box).
**Flag every `background` row as a background** and tag its scope — `bg (scene)` vs
`bg (substrate)` — since the user sources these in the manual review pass and a `substrate`
one is wired once behind the whole video rather than into a single block (see
`composition-structure.md`).

## Swapping a box for the real asset

Once the file exists, replace the placeholder `<div>` with the media, keeping the same
id/class/box geometry and the same timeline target so motion is untouched:

```html
<img class="asset" data-asset="surprised-celebrity"
     src="assets/images/surprised-celebrity.png" alt=""
     style="/* same footprint the box had */">
```

Video: `<video class="asset" src="assets/video/<id>.mp4" autoplay muted loop
playsinline>` — but the player owns timing, so prefer short loops and keep determinism;
a still cutout is usually enough and cheaper than a clip. **One video is NOT an
asset-box clip: the continuous talking-head take.** When a talking-head source is
present it is the single seek-driven `#face-layer` host — `currentTime` bound to
hf-seek, never `autoplay`/`loop` — not this decorative-clip model; see
`reference/talking-head.md`.

A **referent SVG** (`logo`/`glyph`) swaps to an `<img>` pointing at the static file — or, for a
monochrome glyph you want tinted to the palette, **inline the SVG** so CSS `currentColor` reaches
it:

```html
<!-- coloured brand mark: reference the static file -->
<img class="asset asset-mark" data-asset="javascript-logo"
     src="assets/icons/javascript-logo.svg" alt="" style="/* same footprint */">

<!-- monochrome concept glyph: inline so color:var(--accent) tints it -->
<span class="asset asset-glyph" data-asset="infra-glyph"
      style="color:var(--accent); /* same footprint */"><!-- paste the saved SVG markup --></span>
```

A **`background` box** swaps the same way — to a full-frame `<img>` behind the scene's
foreground (`z-index:0`), keeping the box geometry and timeline target. But if its
`data-asset-scope` is `substrate`, the supplied image doesn't swap into *this* block at all:
it's wired into `compositions/substrate.html` (the persistent layer) so it sits behind every
scene — see `composition-structure.md`. Either way, keep foreground contrast winning by making
the backdrop **recede behind busy text** — direction-neutrally: on a white canvas it lightens
toward the base tone and its decorative alpha drops; on a dark canvas it dims toward black. Same
yield, opposite mechanic (`visual-language.md` §1).

Re-run the visual-QA loop after swapping — a real image changes contrast and edges; the
emphasis and legibility checks must pass against the actual pixels, not the placeholder.

## Treatment — one consistent look via `tools/image-prep`

Raw photos and screenshots clash. Run every supplied raster through
**`tools/image-prep`** (a uv project) to background-remove and apply the house VFX so
disparate sources share one feel:

```bash
uv run --project tools/image-prep image-prep \
  assets/images/_raw/surprised-celebrity.jpg \
  assets/images/surprised-celebrity.png \
  --remove-bg --preset duotone --height 1080
```

Presets (`grain`, `duotone`, `halftone`, `vintage`) read the `bg`/`accent` tokens so
the cutout sits in the palette. See `tools/image-prep/README.md`. Background removal
(`--remove-bg`) is what makes a photo read as a cutout on the substrate rather than a pasted
rectangle. The user supplies raw files; you (or they) run image-prep to produce the
treated asset the box swaps to.

**White-canvas note.** Cutout and duotone presets tuned against a dark substrate read as a
halo'd **sticker** on white — the matte-edge fringe and the dark-toward-`bg` duotone target
that vanished on black now ring the subject. On a white canvas, re-tune the **duotone target
lighter** (toward the light `bg`/`panel` tones) so the wash darkens-and-saturates into the
palette rather than glowing, and run an **edge despill/defringe pass** after `--remove-bg` to
erode the cool matte halo (consistent with the cutout despill memory — kill the cool ring,
darken the warm-hair edge). A subject tint on white is a low-opacity **dark-on-light wash /
desaturated texture, never an additive glow** (a glow is invisible on white).

**A `background` image is the exception to `--remove-bg`** — it *is* the backdrop, so
never cut it out. Treat it only for palette/feel (a light `grain`, or `duotone` toward
the `bg`/`accent` tokens) and, if needed, scale to the 1920×1080 frame.

**The talking-head take is a second exception — it bypasses `image-prep` entirely.** When
a talking-head source is present, the take is **transcoded 4K H.264**, not a raster run
through this tool; its PIP border + drop shadow are **live CSS on the `#face-layer` host**,
not baked-in treatment. See `reference/talking-head.md`.

## When imagery earns its place — and when it doesn't

**A worked case — reaction (the *yes* side).** An ironic payoff — a line whose humour is the
twist, e.g. a language nobody wanted now running the world's infrastructure — is a prime imagery
beat. The move is a web-searched laughing-reaction cutout (a celebrity mid-laugh,
background-removed, dropped on the substrate beside the line) reacting *for* the viewer, which
makes the irony land funnier and keeps watch-time up. Note what you do **not** add there:
with the laughing face carrying the contrast, leave the opposing line at full strength and
don't divide the frame (see `visual-language.md` §2). Phrase the trigger to yourself as a
beat *category* — "an ironic payoff", "a line whose humour is the twist", "a named who" —
not "scene 2", so the instinct generalises to any video's punchline.

**A worked case — referent (the other *yes* side).** When the line *names a recognisable thing
that is its subject* — "…and it all compiles to **WebAssembly**", "…racks humming in a **data
center**" — show that thing for real: the Wasm `logos:` mark igniting beside the word
(`class: logo`, a static SVG from Iconify or local `assets/icons/`), or a licensed Wikimedia
server-hall photo as a full-height cutout (`class: photo`). The picture *is* the identity or the
scale, which bare type would have to spell out. But hold the three-part gate from
`visual-language.md` §2: the thing must be the **subject** of the beat (not a noun in passing),
**recognisable on sight**, and **add meaning the words can't**. "JavaScript" igniting on the line
about JavaScript passes; a generic "users" glyph next to the word *users* is noise.

**The counterweight (the *no* side).** Boxes are for beats where a real picture does work
text can't — an emotion, a face, a concrete object, a named logo, a real place. A quiet
typographic beat (a single word landing in silence, a pure claim, a definition), an abstract idea
with no settled mark ("the economy", "trust", "performance"), or a mechanism/stat you can draw in
code needs no box. Don't request an asset just to fill space: forcing a face onto a typographic
beat — or stamping a logo on every noun — is as wrong as never reaching for imagery at all. A run
of consecutive logo-drops is the same inertia smell as a run of bare-text cards; if two adjacent
beats would both sprite a logo, at most one is the real subject. The archetype menu in
`visual-language.md` is half code-native (kinetic type, diagram, code reveal, stat) and half
imagery (side-cutout, referent mark) — pick by what the sentence needs.
