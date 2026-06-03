# Reference-study: the "awesome" visual language

Source: `youtube.com/watch?v=SoQ19gHEM2A` ("Why Python is overtaking JavaScript",
~5 min, a Python/types explainer). Pulled with `yt-dlp` (video + `en` auto-subs,
both gitignored under this folder); 25 frames sampled every 12s into `frames/`,
`contact-sheet.jpg` for the montage. This is **evidence for the skill edits, not a
design to copy** — we extract the *mechanics* (placement, motion, emotion-mapping),
not its specific memes or its Python content.

The user's brief named this creator as the bar. Below, each pattern is what the
frames + the user's written notes jointly establish, phrased so the skill can
generalize it to any video.

## The canvas

- **Pure black** (`#000`) with a faint **starfield / dust** drift — *not* a visible
  technical grid. The background is mood and depth, never structure. Our project's
  substrate is dark-but-tinted (`--bg #0b0d12`); the takeaway is "atmosphere that
  drifts," plus the user's ask to lend it a **rationed subject tone** (a faint
  JS-yellow presence here) — no logo.
- Everything else sits on that void in high contrast. Negative space is used
  generously; sparse frames (one logo centered) alternate with dense ones (text +
  cutout + chips).

## Side cutouts — the signature move

- A **person/reaction image fills one entire side, top to bottom** (left or right),
  background removed, with a subtle light edge/separation so it reads as a cut-out
  pasted on the void. The opposite side carries the text. (John Cena right; vintage
  ad-women left/right; Steve Carell, Mark Wahlberg, the pipe-man.)
- The image is **emotion-matched to the beat** — "the correct picture for the correct
  thing": a *screaming* comic panel on the risky/scary point, a *smug* vintage woman
  on the confident point, a *crying* woman on the sad point, a *surprised* face on the
  reveal. Generic stock is the exception (a spaghetti-on-fork shot stands in for
  "flexibility"; an AI dev-at-night scene for "production").
- **Treatment is consistent**: vintage/halftone/grain/duotone so disparate photos
  share one look and feel intentional, not pasted screenshots. Logos (JS, Python,
  PHP, TS) are flat brand art, BG-removed, sometimes with confetti.

## Typography & emphasis

- **Big bold sans** for structure (TEAMS, MASSIVE CODEBASES, DYNAMICALLY TYPED).
- **Highlighter-marker chips** behind the key word — a solid mint/yellow/cyan rounded
  rect with dark text on top (TYPED, STRING, INTEGER, TYPES, BAD, POOR). This is the
  emphasis primitive, the analogue of our scribble-underline.
- **Hand-drawn script** for asides/labels ("Types" in pink marker, the handwritten
  "we need TYPES"). Maps to our Excalifont hand-annotation token.
- **Checklist rows**: an icon/emoji + a green check badge + a word, stacked
  (ANNOTATED / UNTYPED; TYPE INFERENCE / SMART CASTING / TOOLING). A clean "list of
  attributes" archetype.
- **Code** is shown as real syntax-highlighted snippets (`def get_user_name(id: int)
  -> str | None:`), not screenshots — directly authorable in our stack.

## Motion (from watching, not the stills)

- **Cutouts slide in from the edge they live on** (right image enters from the right,
  bottom logo rises from the bottom), eased, settling with a small overshoot.
- **Reflow, not stacking**: when a new element joins, the existing ones shift to make
  room (text reflows left as an image claims the right; list rows push down as a new
  row arrives) — elements share a layout, they don't overlap-and-fight. This is the
  structural antidote to our scene-2→3 text-on-text collision.
- **Constant subtle motion**: nothing is perfectly still. Cutouts and chips carry a
  gentle float / 3D-tilt / low-amplitude shake; the starfield drifts. Keeps the frame
  alive in dead air between beats.
- **Scene changes** are quick cuts or short covering wipes — the incoming frame
  *occludes* the outgoing one. You never see two legible text layers cross-dissolving
  through each other.

## Cadence

- One visual idea per beat; the look **changes every sentence**. Adjacent scenes never
  reuse the same archetype back-to-back — logo-hero, then side-cutout+text, then a
  code snippet, then a checklist, then a marked-up headline. Variety *is* the style.

## What we take into the skill (→ `reference/visual-language.md`, `assets-and-media.md`)

1. Background = drifting atmosphere + rationed **subject tone**, no logo.
2. **Archetype variety** per scene, driven by the sentence; never default to a
   centered text card; no two neighbors share an archetype.
3. **Real imagery via boxes**: full-height side cutouts, emotion-matched, BG-removed,
   VFX'd to one consistent look (→ `tools/image-prep`).
4. **Motion language**: edge slide-ins, layout reflow, constant low-amplitude
   tilt/shake.
5. **Transitions** cover/occlude — never cross-dissolve two text layers.
6. Emphasis primitives beyond the underline: **marker chips**, **green-check list
   rows**, **hand-script asides**, **inline code**.
