---
name: audio-bed-music
description: Add a music bed underneath the voiceover, animation, and SFX of a HyperFrames video. Runs a short brainstorm (via the superpowers:brainstorming skill) to settle vibe and layer count, asks the human to curate the actual tracks (the skill does NOT recommend music — taste is human), then bakes a single deterministic music-bed.wav with ffmpeg, snaps the layer boundaries to natural narration pauses, and wires the bed into the composition as compositions/music.html. Use when the user asks to "add a music bed", "score this video with music", "underscore the video", "lay music under the narration", "add background music", or anything similar on a HyperFrames video that already has VO + SFX. Runs after video-director's SFX pass (Step H + the final reconcile), not before — music sits beneath SFX.
---

# audio-bed-music

You are adding a music bed to a HyperFrames video whose voiceover, animation,
and SFX are already approved in `npx hyperframes preview`. The bed sits
*underneath* everything else — it must never compete with VO consonants or
draw attention away from a SFX hit.

Music is taste, not engineering. **This skill does not recommend tracks,
genres, composers, or Envato search strings.** It runs a short brainstorm
with the human to surface emotional register and layer structure, then once
the human has dropped audio files into the folders this skill specifies, it
takes over: probe durations, find narration pauses, fit layers to source
lengths, bake the bed with ffmpeg, wire it in, and verify.

## When this skill should NOT run

- VO and SFX are not done yet. Music is the last audio pass.
- The composition still has unresolved visual changes — boundary timing
  depends on the locked narration timestamps.
- No `transcript.json` at the video folder root. Without it, you can't snap
  crossfade boundaries to silence, and the bed will fight the VO.

If any of these is true, stop and tell the user what's missing.

## Inputs the skill reads

From the video folder (`videos/<slug>-<YYYY-MM-DD>/`):

- `audio/voiceover.mp3` — the spoken track. Its duration is the target
  duration of the music bed.
- `transcript.json` — Scribe v2 word-level timing. The source of truth for
  pause windows where layer crossfades hide.
- `index.html` — to find the existing `compositions/sfx.html` mount and
  mirror its pattern when adding the music layer.
- `compositions/sfx.html` — the structural reference for the new
  `compositions/music.html`.
- `design.md`, `script.md` — taste context for the brainstorm (tone,
  intended audience). Read for context, not as a mechanical filter.
- `story-spine.md` at the video folder root — optional, if present. A 3–4
  line note of where the script's hook, climax, and landing landed. Use it
  as *orientation* for where a layer crossfade or a bed-pullback might
  coincide with a narrative turn — the Phase 1 brainstorm and the human
  still decide layer count, register, and intensity. It prescribes nothing.
  Most videos will not have one; that changes nothing about Phase 1.

## Phases

### Phase 1 — Brainstorm vibe and structure

Hand off to the `superpowers:brainstorming` skill. The user has opinions; your
job here is to surface them, not to recommend them.

Two questions need answers before track curation can begin, plus one optional question worth surfacing:

1. **Emotional register.** What does the bed feel like under the narration?
   The brainstorming flow will explore this in the user's own language —
   never paste in a pre-baked list of options from this skill. Do not
   suggest specific genres, artists, scores, or composer names. If the user
   asks you to name examples, ask what *they* are reaching for first.

2. **Layer structure.** How many distinct musical sections does the video
   want? Common answers:
   - **1 layer** — one bed top-to-tail. Simplest. Right when the video has
     a flat tonal arc (calm explainer, single-mood vlog).
   - **2 layers** — one crossfade. Right when the script has one
     reversal/turning point.
   - **3 layers** — two crossfades (intro/build/resolve). Right for
     three-act or rise-then-fall narratives.
   - **N>3 layers** — supported, but rare. Each extra layer is another
     boundary to snap and another track to curate.

   The brainstorm should also surface *where* in the narration each
   boundary lives — by beat or by quote, not by timestamp. The skill snaps
   to real pauses later; the human just describes intent.

3. **Intensity direction (optional).** Should the bed's intensity rise,
   fall, or stay flat across the layers? A taste question with no right
   answer — a rising bed suits a video building to a climax, a falling one
   a video that opens loud and resolves quiet, a flat one an even-toned
   explainer. Surface it in the user's own language; don't answer it for
   them. If they have no strong feeling, that is itself an answer — not
   every bed wants an intensity arc.

Whether the bed should ever *pull back to silence* — under a payoff line,
before a reveal, on the landing — is another taste dimension worth
surfacing here. See `reference/silence-strategy.md` for where pullbacks
tend to land; the human still decides whether the bed has any.

Record the answers in your working memory before moving on. Do not write
them to disk — they're inputs to the planning phase, not artifacts.

### Phase 2 — Folder scaffolding and curation hand-off

Tell the user to create `audio/layer_a/`, `audio/layer_b/`, ... `audio/layer_N/`
inside the video folder (one folder per layer chosen in Phase 1). The user
drops their chosen tracks into the matching folder — typically as WAV or MP3.
Multiple variants per layer are welcome (full version, shorts, loops, stems);
the skill will pick the best fit later.

If the user has an Envato Elements / Artlist / similar subscription, they
already know how to browse. If they ask for search terms, **stay neutral**:
phrasings like "documentary underscore", "ambient pad", "cinematic tension"
are descriptions of what they decided on in Phase 1, not new suggestions.
Reflect their own words back; do not introduce new vocabulary.

Wait for the user to confirm the folders are populated before proceeding.
Don't probe an empty folder.

### Phase 3 — Probe sources and propose layer windows

Once the layer folders are populated:

1. **List every audio file in each `audio/layer_*/`** including any
   subfolders the user (or Envato's zip) created (e.g. `Loops/`, `Shorts/`,
   `Stems/`). Capture each file's duration via `ffprobe`.
2. **Get the VO's duration** — this is the target total of the bed.
3. **Find narration-pause candidates** for each layer boundary using
   `transcript.json`. See `reference/transcript-pause-finder.md` for the
   exact Python snippets. For each boundary, the human's Phase-1 intent
   ("after the Turing setup", "right before the closer") narrows the search
   window; within that window, pick the largest gap as the crossfade
   midpoint candidate. A boundary lands hardest when it coincides with a
   *narrative turn*, not just a convenient pause — prefer a slightly
   shorter gap on a real turn over a longer gap mid-thought. If a
   `story-spine.md` exists at the video folder root, it names those turns;
   it is optional, and absent it the Phase-1 intent is the guide as before.
4. **Check source-length constraints.** Each layer must be long enough to
   cover (boundary_out − boundary_in + 2s) when using a 2s crossfade on
   each side. If the longest single file in a layer is shorter than the
   span needed, you have options:
   - **Shift the boundary** to a different pause that fits the source.
   - **Bridge the layer** by concatenating two files from the *same*
     layer folder with an inner 2s crossfade (musically natural when
     sources are from the same composition — e.g. main + a "short" or
     loop variant of the same track).
   - **Ask the user to curate a longer source** for that layer.
5. **Render waveform PNGs** for the chosen sources and the VO into
   `audio/.waveforms/` using `ffmpeg showwavespic` (see recipe). The
   PNGs are sanity-check artifacts, not deliverables.
6. **Propose the boundary plan** to the user in a short table:

   ```
   | Layer | Source(s)               | Boundary midpoint (global s) | Pause at boundary    |
   | ----- | ----------------------- | ---------------------------- | -------------------- |
   | A     | layer_a/<file>.wav      | start of bed                 | (fade-in)            |
   | A→B   | acrossfade 2s           | 99.59s                       | 0.70s "in. \| The"   |
   | B     | layer_b/main.wav + ...  |                              |                      |
   | ...   |                         |                              |                      |
   ```

   Surface every internal-bridge splice in the same table so the user can
   see what's stitched. Wait for explicit approval before baking. This is
   a hard gate.

### Phase 4 — Bake the bed

Run a single `ffmpeg` invocation with a `filter_complex` graph that:

1. Trims each source to the planned input length.
2. Applies `afade` at the head of layer A (1.5s fade-in) and the tail of
   the last layer (3–4s fade-out).
3. Concatenates bridged sources within a single layer using
   `acrossfade=d=2:c1=qsin:c2=qsin` (equal-power).
4. Runs `loudnorm=I=-28:LRA=11:TP=-2` on each layer independently so
   layers reach roughly equal perceived loudness regardless of source
   mastering.
5. Crossfades adjacent layers with `acrossfade=d=2:c1=qsin:c2=qsin`.
6. Finishes with `alimiter=limit=0.85` to catch any post-loudnorm peaks.
7. Outputs stereo 48 kHz `pcm_s16le` to `audio/music-bed.wav`.

The full template is in `reference/ffmpeg-recipe.md`. Adapt it to the
layer count — N layers means N − 1 outer crossfades.

Verify:

- `ffprobe -show_entries format=duration` — within ±1s of the VO.
- `ffmpeg -af ebur128=peak=true` — integrated `I` near −28 LUFS (one-pass
  loudnorm typically lands in the −24 to −28 LUFS range; anything that
  ends up hotter than −22 should be re-baked with a lower target).

### Phase 5 — Wire into the composition

Create `compositions/music.html` mirroring the shape of `compositions/sfx.html`:
a single `<audio class="clip">` pointing at `../audio/music-bed.wav`, paused
GSAP timeline registered on `window.__timelines["music-layer"]`. See the
template in `reference/composition-template.md`.

Mount it from `index.html` next to the existing sfx-layer mount, using a
**low track-index** (typically `10`) so the music sits visually below SFX
(usually `19–29`) in the studio timeline.

Initial `data-volume="0.18"`. This is a starting point — the user always
tunes it during preview. Document the dial-up/dial-down range in your
hand-off message.

### Phase 6 — Verify and hand off

1. `npx hyperframes lint` — confirm no new errors. Pre-existing warnings
   are fine; new warnings against `compositions/music.html` are not.
2. Surface **seek targets** for the user to scrub in their open preview
   tab. At minimum: 0:00 (fade-in), each layer boundary (±2s window), one
   moment deep inside each layer, and the closing seconds (fade-out).
   Each seek target is a one-line annotation telling the user what to
   listen for — "boundary should hide in the pause; you should hear a
   colour shift, not a level dip."
3. Tell the user how to tune volume: edit `data-volume` in
   `compositions/music.html` and reload the preview tab. Sensible range
   is roughly 0.10 → 0.25. Step in 0.02 increments.
4. If they want to swap a bridge source (e.g. the splice inside a layer
   sounds glued), re-run Phase 4 with a different file from the same
   layer folder. The boundary plan in Phase 3 stays valid.

## What this skill does NOT do

- Recommend specific tracks, artists, scores, or Envato search strings.
- Generate music. The user curates; the skill orchestrates.
- Run sidechain ducking under VO. Not needed at a properly set
  `data-volume` (~0.15–0.20) on a bed normalized to ~−28 LUFS. If the
  user wants ducking later, that's a separate, larger task.
- Master loudness for the final mixed video (the −14 LUFS / −1 dBTP
  YouTube target). That's a render-time concern.
- Re-render `compositions/sfx.html`. SFX is upstream of music and stays
  untouched.

## Reference files

- `reference/transcript-pause-finder.md` — Python snippets for locating
  pauses and validating source-length constraints.
- `reference/silence-strategy.md` — when the bed should pull back to
  silence (payoff lines, high-weight beats, pre-reveal, the landing) so VO
  and SFX carry. Describes when pulling back tends to land; prescribes no
  fixed silence points. Read it during the Phase 1 brainstorm and Phase 3
  planning.
- `reference/ffmpeg-recipe.md` — the bake invocation, with annotations
  for what each filter does and how to extend it to N layers.
- `reference/composition-template.md` — the `compositions/music.html`
  template and the `index.html` mount snippet.
- `reference/troubleshooting.md` — common failure modes (VO masked,
  splice audible, bed clipping, duration mismatch) and the targeted
  fixes.
