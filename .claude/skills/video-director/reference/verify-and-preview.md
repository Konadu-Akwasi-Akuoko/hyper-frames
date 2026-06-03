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
   is where two scenes co-render and text can collide; a scene that looks clean in
   isolation can still mush at the seam. Then **dispatch a Sonnet subagent** (the
   Agent tool with `model: sonnet`) to `Read` the batch of PNGs and grade them
   against the rubric below. Offloading the image read to Sonnet keeps the loop
   cheap — the director (often on Opus) doesn't burn its own context staring at
   pixels. **Claude does the looking — do not use `--describe` / Gemini.**

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
  usual offenders.)
- **Contrast / accessibility.** Text-to-background contrast should be clearly
  sufficient. Flag muted-on-muted, accent-on-accent, or anything that strains.
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
  (glows, grids, drifting ghost type) are fine.
- **Layout integrity.** Flag clipping, overlap, or content escaping the
  1920x1080 frame that `inspect` didn't already catch.
- **Seam collision (the seam frame).** On the mid-overlap frame, flag **two
  legible text layers sharing the screen** — the outgoing scene's text still up
  while the incoming scene's text is already on. The transition must cover/occlude,
  not dissolve text through text (see `composition-structure.md` wiring rules).
- **Per-scene distinctness.** Compare this scene's archetype to its neighbour's.
  Flag a scene that repeats the previous one's shape (e.g. a second centered text
  card in a row) — adjacent scenes should look different at a glance
  (`visual-language.md` §2).
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

## Never touch the preview server

The user **always** has `npx hyperframes preview` running in another window and
reloads the open studio tab themselves after edits. Do **not** start, restart, or
kill the preview server. After any composition change, just tell them the
timestamp or scene to seek to.

`snapshot` and `inspect` spin up their own headless Chrome to capture/measure —
they do **not** touch the running preview, so they're safe to run every pass.

Skip the seek-target step only for non-composition edits (CLAUDE.md tweaks, asset
renames that don't touch HTML).
