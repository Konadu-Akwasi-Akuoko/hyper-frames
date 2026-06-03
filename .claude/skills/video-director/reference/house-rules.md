# House rules

Two project-wide constraints on what a composition contains and when sound gets
added.

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

## Sound design is the last pass — and it isn't yours

Sound follows visuals, never drives them. You (`video-director`) author the
visuals and hand off; you do **not** place SFX or music. Specifically:

- **Do not** add `data-sfx-*` annotations to blocks while authoring. Those are
  written by the `sfx-author` skill, after the composition is visually settled in
  preview. (You'll see `data-sfx-*` on already-finished blocks like the shipped
  js-king scenes — that's fine; it means sound already ran. Don't add your own.)
- The SFX pass runs `sfx-author` → `tools/sfx-plan` → emits
  `compositions/sfx.html` as a native HyperFrames audio sub-composition, and
  mounts it in `index.html`. (Note: the `sfx-layer` host's `data-duration` must
  be the full runtime, or late cues get clipped — but that's `sfx-author`'s
  concern, not yours.)
- After SFX, the music bed runs (`audio-bed-music`) — it sits *beneath* SFX, so
  it's even later.

The pipeline order, for orientation: **voiceover/transcript → (you) visuals →
sfx-author → audio-bed-music → render.** Your Done condition is "visuals
complete and verified"; you then point the user at `sfx-author`.

The shared SFX library lives at the repo-root `sound-effects/` and is referenced
by relative symlinks from each video's `assets/sfx/`. That library must stay at
the repo root — none of which you touch, but know it's there so you don't
duplicate sound assets into a video folder.
