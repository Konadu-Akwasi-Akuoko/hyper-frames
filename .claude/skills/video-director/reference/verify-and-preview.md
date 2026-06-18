# Verify and preview — the visual-QA loop

The HyperFrames CLI loop catches real bugs (overlapping tweens, contrast
failures, layout overflow, missing assets). Run it — don't skip to render. But
lint alone is not enough: a scene that passes lint can still have unreadable
text, an emphasis firing on the wrong word, or a panel that escaped its frame.
The visual-QA loop catches that before the user ever sees it.

Defer the command mechanics to the `hyperframes-cli` skill; this file enforces
*when* you run them, *that* you look at the frames, and *that* you regenerate
when they're not good.

## The per-pass gate

1. **`npx hyperframes lint`** — schema + static checks (overlapping tweens,
   missing assets, the data-attribute contract). **Blocking.** If something looks
   fine in preview but lint flags it, fix the lint finding — those warnings have
   caught shippable-looking bugs.

2. **`npx hyperframes inspect --at <beat timestamps> --json`** — rendered layout
   audit (text and container overflow) at the *actual* animation beats, not just
   evenly-spaced midpoint samples. Pass the timestamps of the moments you
   animated. Parse the JSON. **Blocking** — overflow is a real bug, and small
   text / clipping shows up here mechanically.

3. **`npx hyperframes snapshot --at <chunk_start>,<key beats>,<chunk_end>,<seam>`** —
   capture PNG frames of this scene at the moments that matter. **Always include the
   seam** with the previous scene (`prev_scene_end − 0.25`, i.e. mid-overlap) — that
   is where two scenes co-render and bleed: text-on-text collision *or* a static
   incoming graphic with no entrance rendering solid over the previous scene. Grade
   the seam frame on **every** pass, including graphic-only scenes with no text — a
   scene that looks clean in isolation can still bleed at the seam. Then **dispatch a
   Sonnet subagent** (the
   Agent tool with `model: sonnet`) to `Read` the batch of PNGs and grade them
   against the rubric below. Offloading the image read to Sonnet keeps the loop
   cheap — the director (often on Opus) doesn't burn its own context staring at
   pixels. **Claude does the looking — do not use `--describe` / Gemini.** When a
   talking-head source is present (`reference/talking-head.md`), add each **mode
   transition's** global timestamp to the beat list so the reviewer sees the
   reveal/hide frame — the frame where the face appears, disappears, or flips to
   PIP is exactly where a mid-clause cut or an occluding inset shows up. For a flip
   to PIP, also add a **held-graphics** timestamp (a beat where the PIP is settled
   on-screen, not mid-flip) — the inset border/shadow and the cover's opacity only
   read clearly once the PIP has landed.

4. **If the reviewer flags anything → fix the block and re-run 1-3 on this scene
   only.** Loop until the frames look right. This is the self-correcting heart of
   the gate: small text, weak contrast, off-anchor emphasis, overflow, chrome —
   each is a regenerate, not a shrug.

5. **Surface the seek target.** Only once the scene passes, tell the user where
   to look: "Seek to **{chunk_start}s** to verify scene NN in your open preview."
   Treat this as a hard step on every authoring pass — Claude tends to skip it.

## The visual-QA rubric (pass to the Sonnet reviewer)

Give the reviewer the snapshot PNG paths, the scene's `design.md` palette/type,
and the chunk's intended emphasis word(s). Ask it to return, per frame,
`{frame, verdict: "pass" | "flag", flags: []}` where each flag names the problem.
What to check:

- **Legibility.** Is every piece of text comfortably readable at 1080p? Flag
  anything that reads as too small, too thin, or too low-contrast against its
  background. (Body text below ~24px or thin weights on busy backgrounds are
  usual offenders.) On the **white** substrate default the offenders invert: flag
  **dark text that's too thin/small to hold on white** (a hairline near-black weight
  disappears into a light field the way a light/thin one did on dark), and flag
  **very-light or pale text washing out** against the near-white base.
- **Contrast / accessibility.** Text-to-background contrast should be clearly
  sufficient. Flag muted-on-muted, accent-on-accent, or anything that strains. On
  the **white** default add the inverse offenders: flag **pale-accent-on-white** (a
  JS-yellow / pale-cyan accent that reads fine as ink on dark but vanishes on white —
  it needs the darker/saturated accent-**ink** variant, see `visual-language.md`),
  **muted-gray-on-white strain** (`--muted` mid-gray text fighting the near-white
  base), and any **light-on-light** pairing.
- **Anchor landing.** The emphasized element (highlight, scale pulse, reveal)
  should be visibly active on the frame captured at the word it punctuates. Flag
  emphasis that lands a beat early/late or on the wrong element.
- **Palette / type fidelity.** Colors and fonts trace to `design.md`. Flag
  off-palette colors or stray font families.
- **Type-role fidelity.** Confirm each text role landed in the font `design.md`
  assigns it — this is visible in the rendered frame, so the reviewer can catch it.
  Flag a **verbatim human quote rendered in the system font** instead of the design's
  reserved human-voice font (a real person's quoted words flattened into narration),
  and flag the **inverse — the human-voice font on plain system narration** (the
  script's own paraphrase dressed up as a quote, implying a speaker who doesn't exist).
  The hinge is provenance, not cadence: only a real person's actual words or hand-drawn
  marks earn the human-voice font.
- **Reads as a diagram, not a slide.** The frame should carry visual structure
  (the thing being explained), not just centered text. Flag bullet-list-on-a-card
  filler where a visual was warranted.
- **No editorial chrome.** Flag any corner metadata strip, scene label, running
  timecode, or footer rule (see `reference/house-rules.md`). Ambient decoratives
  (grids, drifting ghost type, contained shapes) are fine — but on the **white**
  default a **glow has no equivalent** (an additive bloom is invisible on white), so
  author **contained dark/accent shapes** instead, and keep grids / ghost type as
  **subtle dark-on-light**.
- **Substrate present (white-default tell).** On the white default a **missing
  substrate renders as a plausible white frame** — the dark-substrate tell (scenes
  popping on a black field) is gone, so a clean white frame is **not** proof the
  substrate exists. Confirm `#substrate-layer` is actually mounted in `index.html`;
  don't read an empty white capture as a passing background.
- **No edge vignette / gradient banding.** Flag any **edge-to-center tonal ramp** on
  the substrate — into **white OR black** (both band at YouTube bitrates), and flag a
  **gray corner vignette** — and flag visible **banding** (concentric/stair-stepped
  rings in a soft gradient). All compress badly and smear into motion graphics
  (see `visual-language.md` §1). A small **contained accent wash** is fine; a full-frame
  ramp into either tonal extreme is a defect.
- **Layout integrity.** Flag clipping, overlap, or content escaping the
  1920x1080 frame that `inspect` didn't already catch.
- **Seam bleed (the seam frame).** On the mid-overlap frame, flag **any element
  from one scene rendered solid over the other** — not just text. Two shapes:
  **(1)** two legible text layers sharing the screen (the outgoing scene's text
  still up while the incoming scene's text is already on); **(2)** any foreign
  graphic, label, panel, or shape from the incoming scene drawn at full opacity over
  the outgoing scene because it has no entrance (no `opacity:0`+fade, not covered by
  the scene-root crossfade) — the scene-21 memory-gauge column bleeding onto the
  Apache scene is the canonical case. The hinge: anything appearing where it doesn't
  belong during the overlap. The transition must cover/occlude, and every element
  must obey the entrance invariant (see `composition-structure.md` wiring rules +
  "Notes that matter").
- **Talking-head mode (only when a talking-head source is present).** When the
  project mounts the `#face-layer` host (track-index 8), also check the mode
  call per `reference/talking-head.md`. When the scene flips to PIP, **capture a
  HELD-GRAPHICS frame, not only the transition frames** — a defect in the inset
  border, shadow, or graphic opacity only shows clearly while the PIP is settled and
  on-screen, not mid-flip. Flag as **blocking defects**: **(a)** a PIP inset missing
  its **border + drop shadow**, OR whose border is **white / near-white / invisible on
  white** (a frameless inset reads as a glitch — the border must bind to `--fg` or
  `--accent`, never `--border` or `--bg`/white; the drop shadow is the primary depth
  cue and reads fine on white); **(b)** a PIP face box **occluding or overlapping
  the live graphic** instead of sitting in its reserved safe zone; **(c)** a covering
  **GRAPHICS scene that isn't genuinely opaque** — dark face footage **ghosting
  through** a low-opacity white cover during the hand-off. Flag as a
  **regenerate/revisit** judgment: **(d)** a mode that doesn't best deliver the
  beat (a face talking *about* a thing where a graphic lands harder, or a graphic
  burying words spoken *to* the viewer); **(e)** a **face reveal landing
  mid-clause** instead of on a word/sentence boundary. **FACE full-frame is a
  valid, deliberate mode** — do not penalize it under the "reads as a diagram"
  or imagery-fit bullets; a bare on-camera take *is* the picture there, not a
  missed asset box.
- **Per-scene distinctness.** Compare this scene's archetype to its neighbour's.
  Flag a scene that repeats the previous one's shape (e.g. a second centered text
  card in a row) — adjacent scenes should look different at a glance
  (`visual-language.md` §2).
- **Archetype-family rotation (windowed).** Beyond the adjacent-pair check above:
  across a *run* of scenes covering one long subtopic, flag the same archetype
  **family** repeating for ~3+ consecutive scenes — even when each adjacent pair
  technically differs. Families (from `visual-language.md` §2): *typographic*
  (kinetic type, quote/source card, checklist), *structural* (split/contrast,
  diagram/build, code reveal), *figural* (side-cutout, referent mark), *numeric*
  (stat hero). A 2.5-minute subtopic rendered as three typographic cards in a row
  reads as one long static block — the visual analogue of the script's
  dragging-subtopic failure. Rotate the family every ~3 scenes.
- **Imagery fit.** If the beat carries an imagery signal — a named emotion,
  irony/comedy/a punchline, a human reaction, a named "who", or a concrete recognisable
  thing (a logo, a real place/person/object) — but renders as bare text, flag it as a
  missed asset box. (Pure text is fine for genuinely typographic beats; flag only when a
  signal is present and went untreated.) If an `asset-box` placeholder is present, flag it
  only if mis-sized, clipped, or mis-placed — a labeled box is expected pre-supply, not a
  defect. Across the batch under review, a run of several consecutive bare-text beats is
  itself worth surfacing — not a per-scene defect, but a "revisit whether one of these
  wanted a face, an object, or a clip" note, since a string of locally-defensible text-only
  calls is usually inertia, not fit.
- **Imagery overfit (the inverse).** Flag the *opposite* failure too: a logo, glyph, or
  photo stamped on a noun that **isn't the beat's subject** — decoration, not meaning (a
  generic "users" glyph beside the word *users*, a logo on a thing only mentioned in
  passing). And if two adjacent scenes both sprite a referent mark, flag it — at most one is
  the real subject; a run of logo-drops is as much a smell as a run of bare-text cards. A
  referent earns its place only when it *is* the subject, is recognisable on sight, and adds
  meaning text can't (`visual-language.md` §2).
- **Asset determinism.** Flag any composition that pulls an image from the network at render
  time instead of a static file — a runtime `<iconify-icon>` web component, an
  `api.iconify.design` / CDN `src`, or a remote `https://` image URL. Every asset must be a
  saved file under `assets/` (SVG in `assets/icons/`, PNG in `assets/images/`); a network
  reference breaks the offline `snapshot`/`render`.
- **Liveliness.** Flag a frame that reads as dead-static where motion was due — no
  idle tilt/drift, nothing mid-transition in a stretch that should breathe
  (`visual-language.md` §3). (Judge gently; a deliberately still quiet beat is fine.)
  If this scene cited a `../../motionGraphicsInspo/` reference, also sanity-check its
  motion against that entry's `Motion:` note — the cadence should read as the same
  *family* (a comparable stagger/overshoot/settle), **adapted, not reproduced**; flag a
  scene that names a reference but moves nothing like it, or one that copies it outright.

## Never touch the preview server

The user **always** has `npx hyperframes preview` running in another window and
reloads the open studio tab themselves after edits. Do **not** start, restart, or
kill the preview server. After any composition change, just tell them the
timestamp or scene to seek to.

`snapshot` and `inspect` spin up their own headless Chrome to capture/measure —
they do **not** touch the running preview, so they're safe to run every pass.

Skip the seek-target step only for non-composition edits (CLAUDE.md tweaks, asset
renames that don't touch HTML).
