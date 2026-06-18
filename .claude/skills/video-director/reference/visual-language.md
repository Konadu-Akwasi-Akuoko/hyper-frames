# Visual language — background, per-scene variety, motion

This file is the answer to the most common failure of an auto-authored explainer:
**every scene looks the same** — muted text on a centred card, beat after beat, on a
flat background that says nothing about the subject. A video that does that reads as a
slideshow. The fix isn't one trick; it's three habits — give the background a *tone*,
give each scene its own *shape*, and keep everything *alive*. Compositions mechanics
(GSAP, data-attrs, determinism) still come from the `hyperframes` skill; this file is
the taste layer on top.

## 1. The background carries the subject's tone — not a logo

The substrate (the persistent layer behind every scene, see
`composition-structure.md`) is mood and depth, never structure and never branding. Two
rules:

- **Tint it to the subject, rationed.** The video is *about* something — let the
  backdrop whisper it. For JavaScript that's a faint warm **JS-yellow** presence: a
  low-opacity accent **WASH** (accent token at low alpha over the light field), a
  tint on the drift, a desaturated accent-tinted texture. Enough that a viewer feels
  "this is a JS video" without being able to point at why. Pull the hue from the
  `accent` token in `design.md` so the next video tints to *its* subject automatically
  (a Python video leans on its accent, etc.). On white, an accent used as **TEXT/thin
  emphasis** needs a darker **accent-ink** variant (a pale accent like JS-yellow is too
  low-contrast as ink on white) — reserve the pale accent for fills/washes.
- **No vignette.** Never darken (or lighten) the substrate edges with a radial/elliptical
  vignette (`radial-gradient(... , transparent, #000)`, an inset `box-shadow` darkening, a
  corner overlay, etc.). An edge-to-center tonal ramp is a worst case for YouTube's codec
  on **ANY** canvas: a ramp toward `#fff` **bands** as a ramp toward `#000` does — at low
  bitrate it quantizes into chunky concentric **banding** rings and its feathered edge
  **smears into any motion graphics** drifting over it, exactly the choppy, bleeding look
  this whole file exists to kill. If you want depth, reach for a small, *contained* accent
  **WASH** (kept well inside the frame, not an edge-to-center ramp) or a textured drift —
  and if any soft radial ramp is unavoidable, dither it with low-opacity grain/noise so it
  can't band. This is a hard rule: the visual-QA reviewer treats an edge vignette as a defect.
- **No literal logo or brand mark in the background.** A JS logo (or any product mark)
  sitting in the substrate is too loud and dates instantly. Tone, texture, a low-alpha
  wash — yes (on the light default this is a SUBTLE DARK-ON-LIGHT gesture, never an
  additive glow, which is invisible on white). Iconography — no. (Logos belong *in a
  scene*, as a deliberate foreground asset, not baked into the floor.)
- **It moves and it yields.** The substrate breathes/drifts/fades slowly
  (deterministic, long yoyo loops) and **YIELDS contrast to the foreground** behind a busy
  scene so foreground content always wins. The invariant is direction-neutral; only the
  mechanic flips with the canvas: on the light canvas it **RECEDES** toward base white and
  its decoratives/tint drop in opacity (the dark equivalent dimmed toward black) — either
  way the substrate gives up contrast so foreground wins. Static backgrounds read as dead.

  On the **light default**, the grid / ghost-type / drift are subtle **DARK-on-light** —
  faint low-alpha dark-gray hairlines, low-alpha dark ghost type; light-on-dark decoratives
  vanish on white. (The grid-alone = flat-slideshow caution below still binds either way.)

  With a talking-head source present, the **face-layer's PIP separation on white** comes
  from a **NON-white border** (accent or dark-gray) + drop shadow, never a light border or
  a glow (a glow is invisible on white) — colors deferred to `reference/talking-head.md`.

**When a talking-head source is present**, the persistent **face-layer host
(track-index 8)** sits in the same z-stack — hidden in GRAPHICS mode, full-frame in
FACE, inset in PIP. It is a continuous take, not a substrate gesture; the full layer
order lives in `composition-structure.md` and the mode policy in
`reference/talking-head.md`.

Avoid the generic technical grid as the *primary* background gesture — a faint grid can
be one ingredient, but a grid alone is the "flat slideshow" smell this whole file
exists to kill.

**Sometimes a beat (or the whole video) wants a real background image** the tinted
substrate can't be — a wooden desk under an article, a blueprint grid behind a connector
diagram, a deep-blue cloudy sky behind a hero shot (the kind of backdrop the
`../../motionGraphicsInspo/` references show). You can't draw those; leave a **`background` placeholder
box** describing exactly what you want and let the user supply it
(`assets-and-media.md`). Decide its scope by whether it *persists*: a backdrop that sets
the mood across many scenes belongs **in the substrate** (one request, promoted to the
substrate layer — `composition-structure.md`); one tied to a single beat is a
**scene-local** full-frame box. Request a background only when it genuinely helps — most
beats are better served by the rationed subject tone above than by a literal photo floor.

### Default light-canvas token recipe

The in-video substrate is **light by default** — copy these into the substrate's `:root`,
keeping the token *names* and flipping only the values. **GOING-FORWARD default only**:
existing videos under `videos/` keep their committed dark tokens, do not retro-flip them.
The **in-video substrate is light by default**, but the **YouTube thumbnail / Short cover
stays on its locked dark Specimen base** — that cover/substrate mismatch is deliberate, do
not "fix" it.

| Token | Value | Note |
|---|---|---|
| `--bg` | `#f7f8fa` | warm near-white, **not** pure `#fff` (pure white clips/blooms at codec edges) |
| `--panel` | `#ffffff` | cards **LIGHTER** than bg — the inverse relationship |
| `--border` | `#d8dbe0` | visible light-gray hairline — but the **PIP frame NEVER uses `--border`** |
| `--fg` | `#14171c` | near-black ink |
| `--soft` | `#3a4150` | dark mid-gray secondary text |
| `--muted` | `#6b7280` | mid-gray that reads on white |
| `--accent` / `--accent-2` | subject-tinted (e.g. `#f7df1e` / `#67e8f9`) | keep the subject hue; for accent-colored **TEXT/thin emphasis** on white derive a darker/saturated **accent-ink** variant (a pale accent is too low-contrast as ink) |
| `danger` / `ok` | dark/saturated values that read on white | a pale pastel fails on white |

## 2. Every scene gets its own shape — driven by the sentence

The single most important instruction in this skill: **let the sentence decide how the
scene looks.** A concession ("never the most loved") wants a different composition than
a power claim ("runs the world's infrastructure") or a pivot question ("so how did that
happen?"). If you find yourself reaching for a centred text card again, stop — that's
the default that makes everything blur together.

Two hard habits:

- **Pick an archetype from the menu below, fitted to the beat's meaning.**
- **Never repeat the previous scene's archetype back-to-back.** Adjacent scenes must
  *look* different at a glance. Variety is the style, not a garnish.

**When a talking-head source is present**, the per-chunk choice also picks one of three
**presentation modes** (FACE / GRAPHICS / PIP — `reference/talking-head.md`). Mode sits
*orthogonally on top* of this menu: the archetype is what fills the frame in GRAPHICS and
the live graphic in PIP, while FACE shows the take instead. **GRAPHICS is the default and
the majority** for an explainer, so most beats still pick an archetype here exactly as
below — and the back-to-back rule still binds: the underlying archetype must vary even
across a run of GRAPHICS beats. The mode itself is decided per the verdict in
`reference/talking-head.md`, never by a fixed slot.

### Archetype menu (not exhaustive — invent when the sentence calls for it)

| Archetype | When the sentence wants it | Shape |
|---|---|---|
| **Side-cutout + text** | a human reaction, an emotion, a "who" | full-height image one side, text the other (see `assets-and-media.md`) |
| **Referent mark / inset** | the beat *names a recognisable thing that is its subject* — a tech/brand logo, a real place/person/object | the named thing shown for real — a logo igniting beside the word, a real-photo cutout, a concept glyph as a diagram node (see `assets-and-media.md`) |
| **Full-bleed kinetic type** | a punchy claim, a quote, a single word | large words owning the frame, word-by-word reveal, marker-chip emphasis |
| **Split / contrast** | "X vs Y", before/after, two camps | screen halved, each side its own state (`ok` vs `danger` tokens) |
| **Diagram / build** | a mechanism, a flow, "how it works" | nodes/arrows/steps assembling in time — a thing being *explained* |
| **Number / stat hero** | a figure, a date, a ranking | the number huge and central, context small around it, tabular-nums |
| **Quote / source card** | a verbatim citation, a comment | a framed card with attribution chrome (the one place a card is right) |
| **Checklist / attributes** | a list of properties, "it's used by…" | icon + check-badge + word rows that arrive and reflow (ref pattern) |
| **Code reveal** | a code point, a syntax contrast | real syntax-highlighted snippet, lines/tokens lighting on the beat |

**The motion reference library lives in `../../motionGraphicsInspo/`.** Its `README.md`
is a two-tier, progressively-disclosed index (a Quick-index scan table over full
`Motion:`-note entries + strips). You don't read it directly — the
**`scene-design-decider` subagent** scans it per chunk, drills into a fitting entry, opens
its **keyframe strip** (`<slug>-strip.png`), and names the slug + cadence in its verdict.
Each entry pairs a hero still + a strip with a written **`Motion:` note** — the strip shows
the *staging* (what enters, in what order), the note carries the *cadence* (timing, ease,
overshoot, drift) a still can't. When the decider cites one, you open that strip to author
and **adapt the cadence — never reproduce the scene.** It should read as the same family,
not the same shot (the "design original; copy the reasoning, not the scene" rule). It's a
source of taste, not a quota: most beats won't draw on one. Where a reference's look needs
a real backdrop you can't draw, that's a `background` box (§1 + `assets-and-media.md`).

**Split / contrast — what "lit vs muted" means on white.** The lit-vs-muted contrast in a
text-only split inverts its direction on the light canvas: **LIT** gains **WEIGHT /
SATURATION / DARKNESS** (it ignites toward `fg`/`accent-ink`), while **MUTED** recedes
*toward the light field* (a lighter gray). `ok`/`danger` must be dark/saturated enough to
read on white. The principle below survives unchanged — "dim is a crutch" still holds; only
the *direction* of the dim inverts.

**When an image carries a contrast beat, let it carry — don't double up.** If a
reaction/emotion cutout is doing the editorial work of an "X vs Y", the *image* is the
contrast: do **not** also dim the opposing text, and do **not** draw a divider line
down the middle. The muted-vs-lit dim and the centre rule are crutches for a *text-only*
split-contrast; with a face present they become competing over-decoration that fights
the cutout for the eye — two devices straining to make one point. Pick one: either the
cutout reacts against evenly-lit, undivided type, or there's no image and the split/dim
does the contrasting. A side-cutout + reaction reads cleaner than a split here precisely
because the picture already tells you which side is which.

**Show the thing you name — referent imagery, and the gate that keeps it honest.** There are two
reasons to put a real picture on screen, and they're different. One is to **react for the viewer**
(the laughing cutout on an ironic beat — covered above). The other is to **show the named thing
itself**: the sentence says "JavaScript" and the JS logo ignites beside the word; it says "a
humming data center" and a real server-hall photo fills one side; it says "infrastructure" and a
clean server glyph anchors the beat. This is illustration, not emotion — and it's powerful exactly
because it's literal, which is also why it's the easiest thing to overdo. So gate it. A named thing
earns a picture only when **all three** hold: it **is the subject of the beat** (the line turns on
it, not a noun mentioned in passing or buried in a list); it is **recognisable on sight** (a logo
you'd know, a real face/place/object, a near-universal glyph — if you'd have to label it for the
viewer, it fails); and **showing it adds meaning the words can't** (identity, scale, texture,
instant recognition that bare type would have to spell out). Fail any one and the better call is
**kinetic type** (the name is the hero as words), a **diagram node** (when it's mechanism, not
identity), a **stat hero** (when it's really a number), or **nothing**. Two hard exclusions:
abstract ideas with no settled mark ("the economy", "trust", "performance") stay type or diagram,
never a stock photo; and a glyph that merely restates the word it sits beside (a "users" icon next
to the word *users*) is noise — cut it. And ration across the batch: if two adjacent beats would
both sprite a logo, at most one is the real subject — demote the other to type. A run of
logo-stamped nouns is the same inertia smell as a run of bare-text cards. The trigger is always a
property of the *sentence*, never a scene index and never a quota. Where each kind of referent
image actually comes from — local icons, Iconify, Wikimedia — is in `assets-and-media.md`.

**The talking-head layer is not a side-cutout image asset.** When a talking-head source is
present, the live **face-layer host (track-index 8)** is a continuous seek-driven take
(`reference/talking-head.md`) — it is **not** a sourced side-cutout/referent image and is **not**
subject to the three-part referent gate above. So a real human reaction can now come from
*revealing the take* (FACE or PIP) rather than sourcing a reaction cutout — the take is the
creator's own face, already on the beat's audio. The gate above still governs every *other*
picture you place (logos, photos, glyphs); it just doesn't touch the face layer.

**PIP mode constrains the archetype: reserve a face-box safe zone, never occlude the graphic.**
When the verdict picks PIP (`reference/talking-head.md`), the chosen archetype must lay the live
graphic out to leave a bordered, drop-shadowed inset in genuine dead space — the graphic stays
fully visible, the face sits beside it, never on top of it. A full-bleed archetype (full-frame
kinetic type, edge-to-edge diagram) cannot host a PIP unless it is **reflowed** to leave that dead
space (the same make-room-don't-stack reflow as §3). The reservation is a structural input the
archetype declares (`composition-structure.md`); the per-region safe-zone geometry — and, in
portrait, how it dodges the phone-UI danger zones — is the layout call here in §2 and
`portrait-mode.md` §safe-areas.

Emphasis primitives to vary across scenes (don't reuse the same one every beat):
**highlighter marker chips** (solid rounded rect behind a keyword, dark text on top —
works on white), **hand-drawn scribble underline** (Excalifont/SVG, for human/quote
moments — works on white), **colour ignition** (a fragment that **DARKENS + saturates**
on its word, `muted → fg`/`accent-ink`/`danger`, never *brightens*), **a WEIGHT bump or
a soft DARK text-shadow** on a payoff word (a drop shadow, **NOT** a luminous bloom),
**green-check badges** for list rows (work on white). The luminous text-shadow **bloom is
invisible on white** — do not reach for it as the inline default; and do **NOT** fall back
to **scale-pulse on inline words** (it eats the word's whitespace mid-pulse). Reserve scale
for **block-level** elements only.

## 3. Keep it alive — the motion language

Beyond entrance + the existing "settle pulse in dead zones" rule, three additions make
the difference between *synced* and *alive*. (Entrance is non-negotiable: **every**
appearing element enters — nothing sits solid at scene-local t=0, or it bleeds across
the seam onto the previous scene. The element either rides the scene-root crossfade or
carries its own `opacity:0` + fade-in. See the **Entrance invariant** in
`composition-structure.md`. **When a talking-head source is present**, a mode change
(FACE↔GRAPHICS↔PIP) is a **seam-class event** — it lands on a natural pause / sentence
boundary via crossfade or clean push, never mid-clause, and the locked face layer is
exempt from the invariant while the graphics/PIP revealed on top still obey it; the full
policy is in `reference/talking-head.md`, not restated here.)

- **Slide-in from the edge an element belongs to.** A right-side cutout enters from the
  right; a bottom logo rises from the bottom; a list row slides from where the list
  grows. Eased (`power3.out` / a gentle `back.out`), short, with a small settle. Things
  arrive *from somewhere*, they don't just fade in place.
- **Layout reflow — make room, don't stack.** When a new element joins an occupied
  frame, the elements already there **animate aside to accommodate it** rather than the
  newcomer landing on top of them. Author the scene as a flow/grid layout whose children
  reflow (animate their positions with GSAP) instead of absolutely-positioned pieces
  that overlap. This reads as a designed, physical space — and it's the structural cure
  for text-on-text collisions (the same discipline applies at scene seams, see
  `composition-structure.md`).
- **Constant subtle motion.** Nothing sits perfectly still. Give cards, headline text,
  chips, and images a low-amplitude idle — a gentle 3-D tilt (`rotateX/Y` a degree or
  two on a `yoyo` loop) or a slow 2-D drift/camera-shake. Keep it *subtle*: it should be
  felt, not noticed, and never fight legibility. Deterministic only — no `Math.random`,
  no `repeat: -1` with random; use fixed values and long `yoyo` cycles.

**Where the concrete cadence comes from.** These three habits are the *what*; the
specific timing that makes a beat feel expensive — how many ms a stagger steps, how hard
the overshoot, how long the settle, where a camera push lands — is lifted from a fitting
`../../motionGraphicsInspo/` entry that the **`scene-design-decider`** cited for this chunk
(its `MOTION-REF:` line names the slug + which cadence to adapt). Open that **strip** for
the staging and its **`Motion:` note** for the easing/overshoot, then **adapt that cadence
to this beat — never reproduce the source scene** (same family, not the same shot). A prose
bullet can say "ease it"; a real reference tells you *how much*. When the decider returned
`MOTION-REF: none`, these habits carry the scene — non-quota, most beats just use them.

## Don't overdo it

These are tools for *fit*, not a checklist to max out. A quiet beat (a single word
landing in silence) may want stillness and one archetype done cleanly — that restraint
is itself variety against a busy neighbour. The goal is that a viewer scrubbing the
timeline sees a *different idea* in every scene, all clearly the same video. Judge it on
the `snapshot` frames in the visual-QA loop (`verify-and-preview.md`).
