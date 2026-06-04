# House rules

Two project-wide constraints: what a composition contains, and where the sound
layers split between you and the downstream music pass.

## No editorial chrome

When authoring compositions for this project, do **not** add:

- corner metadata strips ("PROJECT-NAME · 01 / 09", "PART 01 · TITLE")
- bottom scene labels ("SCENE 01 · HOOK")
- running timecodes ("00:00 / 02:00")
- hairline footer rules

The viewer never reads them — they steal screen real estate from the actual
content. Per-video `design.md` files reinforce this (often phrased as "no
eyebrows").

Ambient decoratives are still fine — radial glows, grid backgrounds, ghost type
drifting in the background. Those add atmosphere, not labels. Only add chrome if
the user explicitly asks for it.

The visual-QA reviewer (`reference/verify-and-preview.md`) flags chrome as a
defect, so a stray label triggers a regenerate.

## Sound follows visuals — SFX is yours, music is not

Sound follows visuals, never drives them. But the SFX layer is **yours now** —
scored per scene in **Step H**, right after that scene's visual QA, and
reconciled across the whole video at the Done condition (see
`reference/sfx-cues-and-timing.md` and `reference/sfx-arc-and-reconcile.md`).
Only the **music bed** is downstream and someone else's pass. Specifically:

- **Do not** add `data-sfx-*` annotations *while authoring visuals* (Steps D–F).
  SFX is a deliberate, separate step (H) once the scene's visuals pass QA — never
  smeared into the authoring. (You'll see `data-sfx-*` on already-finished blocks;
  that's a scene whose Step H already ran. Re-running `tools/sfx-plan` is
  idempotent.)
- Step H runs `tools/sfx-plan` → emits `compositions/sfx.html` as a native
  HyperFrames audio sub-composition and mounts it in `index.html`. The `sfx-layer`
  host's `data-duration` must be the full runtime or late cues get clipped —
  `tools/sfx-plan` sets this for you; the final reconcile verifies it.
- After your SFX reconcile, the music bed runs (`audio-bed-music`) — it sits
  *beneath* SFX, so it's even later, and it is the one sound layer you never author.

The pipeline order, for orientation: **voiceover/transcript → (you) visuals + SFX
(Step H + final reconcile) → audio-bed-music → render.** Your Done condition is
"visuals complete and verified **and** the whole-video SFX reconcile passed"; you
then point the user at `audio-bed-music`.

The shared SFX library lives at the repo-root `sound-effects/` and is referenced
by relative symlinks from each video's `assets/sfx/`. Cue assets are pinned with
`data-sfx-asset` (paths under `sound-effects/`); that library must stay at the
repo root, so never duplicate sound assets into a video folder.
