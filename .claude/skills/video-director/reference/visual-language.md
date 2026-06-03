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
  low-opacity glow, a hair of warmth in the vignette, a tint on the drift. Enough that
  a viewer feels "this is a JS video" without being able to point at why. Pull the hue
  from the `accent` token in `design.md` so the next video tints to *its* subject
  automatically (a Python video leans on its accent, etc.).
- **No literal logo or brand mark in the background.** A JS logo (or any product mark)
  sitting in the substrate is too loud and dates instantly. Tone, glow, texture — yes.
  Iconography — no. (Logos belong *in a scene*, as a deliberate foreground asset, not
  baked into the floor.)
- **It moves and it yields.** The substrate breathes/drifts/fades slowly
  (deterministic, long yoyo loops) and is allowed to dim further behind a busy scene so
  foreground content always wins contrast. Static backgrounds read as dead.

Avoid the generic technical grid as the *primary* background gesture — a faint grid can
be one ingredient, but a grid alone is the "flat slideshow" smell this whole file
exists to kill.

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

Emphasis primitives to vary across scenes (don't reuse the same one every beat):
**highlighter marker chips** (solid rounded rect behind a keyword, dark text on top),
**hand-drawn scribble underline** (Excalifont/SVG, for human/quote moments),
**colour ignition** (a fragment shifting `muted → fg`/`accent`/`danger` on its word),
**scale-pulse bloom** on a payoff word, **green-check badges** for list rows.

## 3. Keep it alive — the motion language

Beyond entrance + the existing "settle pulse in dead zones" rule, three additions make
the difference between *synced* and *alive*:

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

## Don't overdo it

These are tools for *fit*, not a checklist to max out. A quiet beat (a single word
landing in silence) may want stillness and one archetype done cleanly — that restraint
is itself variety against a busy neighbour. The goal is that a viewer scrubbing the
timeline sees a *different idea* in every scene, all clearly the same video. Judge it on
the `snapshot` frames in the visual-QA loop (`verify-and-preview.md`).
