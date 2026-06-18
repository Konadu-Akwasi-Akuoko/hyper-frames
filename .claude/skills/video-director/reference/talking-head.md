# Talking-head mode — a continuous on-camera take as a seek-driven layer

The trigger is a **continuous talking-head recording** the creator shot of
themselves narrating — one take, on camera, that supplies **both** the
voiceover (its audio) **and** a picture layer (its video). This file is the
delta for that case. Everything in `SKILL.md` and the other references still
applies; this file states only what *changes* when a talking-head source is
present. Like `portrait-mode.md`, it is a condition-triggered delta that layers
**on top of** the A–I loop — not a different pipeline. The two deltas compose: a
face-led Short is both portrait and talking-head at once.

The director does **not** decide whether a video is talking-head. It detects the
source in Step A and honors it, exactly as it detects orientation.

## The trigger — detected in Step A

A project declares a talking-head source two coordinated ways, both checked in
Step A:

1. **`design.md` carries a `talking-head:` field** pointing at the take — the
   human's written intent (e.g. `talking-head: assets/video/talking-head.mp4`).
2. **The transcoded, seek-ready file exists at `assets/video/talking-head.mp4`**
   — the on-disk artifact the composition mounts.

When either is present, read this file once and treat the face video as a
**locked seek-driven layer running beneath every scene** for the whole runtime.
Once authoring has begun, the mounted `#face-layer` host in `index.html` is the
durable signal (matching `state-and-resume.md` — the hosts ARE the state); the
`design.md` field is the first-pass intent before anything is mounted.

## The prep — cut the VIDEO first, then derive both streams

The phone shoots **4K HEVC (H.265)** to save card space, and the raw take has
mistakes, restarts, and dead air to cut. The order is load-bearing: **cuts apply
to the video, not to a standalone audio file.** Cut the audio while the picture
stays full-length and the mouth desyncs from the voice on the very first cut.
So the cut master is the single source both the picture layer and the voiceover
derive from. The director runs this as a one-time Step-A prep when it finds an
un-transcoded source; it does not own it as composition mechanics.

1. **Plan the cuts on the raw take.** Extract a scratch audio track, transcribe
   it, and plan cuts exactly as the recorded-voice path already does — the
   `transcribe-and-plan-cuts` skill + `tools/audio-editor` produce `cuts.json`.
   (This is the *only* step that touches the standalone audio, and only to decide
   cut points.)

2. **Apply `cuts.json` to the *video*.** The audio-editor renders audio cuts;
   the picture needs the **same** keep-windows applied with one more ffmpeg pass —
   select the kept segments from `cuts.json` and concat them into a cut master.
   Same timestamps, applied to the video stream, so picture and embedded audio
   are cut together and stay locked.

3. **Derive both streams from the cut master** — guaranteed frame-identical
   because they share one source and one set of cuts:

   ```bash
   # Picture layer: cut master -> H.264, keep native resolution (visually
   # lossless), DROP audio (the <video> is muted picture-only), fast-start seek.
   ffmpeg -i cut-master.mov -an -c:v libx264 -crf 18 -preset slow \
     -pix_fmt yuv420p -movflags +faststart assets/video/talking-head.mp4

   # Voiceover: the cut master's audio — HyperFrames' timing + render audio
   # comes from THIS <audio> element, never the muted seek-driven <video>.
   ffmpeg -i cut-master.mov -vn -c:a libmp3lame -q:a 2 audio/voiceover.mp3
   ```

4. **Re-transcribe the cut `voiceover.mp3`** → the final `transcript.json`. After
   cuts every timestamp has shifted, so timing truth must reflect the **cut**
   timeline, not the raw take (the "after the cuts are applied" re-transcribe).

Keep **native resolution** through the transcode: the face host is sized to
whatever the root declares (Step A's host-matching rule), and a 4K root wants a
4K source full-frame. If the root is smaller, the browser downscales at seek —
fine. The cost of staying 4K is render-seek time, not quality; that tradeoff is
the creator's, already taken.

Because both streams come from the one cut master, `transcript.json` is timing
truth for **both** the audio and the face-video seek (see the seek rule below) —
the muted `<audio id="voiceover">` drives the timeline while the muted picture
rides above it, frame-locked.

## The face layer — one persistent host, z-order flips per mode

The face video mounts as a **single persistent host** spanning the full runtime,
alongside the substrate and voiceover — not a per-chunk scene. Its full markup
and exact track-index/z-index live in `composition-structure.md` (one source of
truth); the canonical band is **`id="face-layer"`, `data-start="0"`,
`data-duration="<full runtime>"`, `data-track-index="8"`**, sized to the root
dims. The `<video>` inside is **muted** (audio comes from `<audio
id="voiceover">`), `preload="auto"`, and **seek-driven**: its `currentTime`
tracks the global composition time on every hf-seek — the same seek-binding the
canvas adapters use, never `autoplay`/`loop` (that is the decorative-clip model
in `assets-and-media.md`, the wrong model here — it would break determinism and
the audio lock).

The one place a single static z-index can't serve: the face must sit **below**
the graphics in GRAPHICS mode and **above** them in PIP. Resolve it on the one
host — **its z-index and geometry animate per mode**: full-frame at low z
(covered when a graphics scene is opaque over it), lifting to a bordered corner
inset above the active graphic in PIP. One element, one decode.

**The z-flip fires only while the face is covered.** A `z-index` change is a
discrete jump, never a tween — so it must never be on screen. The only flip is
GRAPHICS↔PIP (face below ↔ above); sequence it under cover: GRAPHICS→PIP lifts
the z **while the face is still hidden**, *then* the inset enters the safe zone;
PIP→GRAPHICS drops the z only **after** the inset has fully exited. FACE↔PIP
needs no flip (the face is already on top). The standing rule: while the face is
**visible**, only its **opacity and geometry** animate — never its `z-index`.

## The three presentation modes

Per chunk, the take is presented one of three ways:

- **FACE full-frame** — the on-camera take fills the frame. The graphics scene
  is empty/transparent so the layer shows through. Archetype and imagery are
  moot here (the take IS the picture).
- **GRAPHICS full-frame** — a motion-graphics scene (the normal archetype menu,
  `visual-language.md` §2) covers the frame; the face footage keeps running
  **hidden underneath**, audio unbroken. **This is the default and the majority**
  for an explainer — the graphics carry the information, the face is texture.
- **PIP** — the face in a **bordered, drop-shadowed inset** beside or around the
  live motion graphic, in a reserved safe zone.

"Show face" = reveal the layer at that exact global word timestamp. "Go to
graphics" = the same footage runs hidden underneath; nothing about the take
moves. Face and audio are one continuous take, so the face you reveal is
whatever the creator was doing at that real second — you cannot float an
arbitrary face moment over arbitrary audio, and you never need to: they are the
same recording.

## Content decides the mode — never a fixed slot

Pick the mode that best **delivers the beat to the viewer**, read from the
sentence in front of you — exactly the "let the sentence decide how the scene
looks" discipline of `visual-language.md`, applied to mode. There is no slot:
**even the hook may be graphics or PIP** if that lands it harder than a face,
and a mid-body aside may cut to FACE if the words are *to* the viewer rather than
*about* a thing. A run of all-one-mode is a smell the same way an all-imagery run
is — content, not a quota, decides each beat. GRAPHICS being the majority is an
*outcome* of explainer content, not a target to hit.

This is **fully automatic**: the per-chunk mode is decided by the
`scene-design-decider` (Step D) and authored without a per-beat human
checkpoint — it rides the existing decider verdict and the standing-approval
rhythm, not a new gate.

## PIP — must stand out, must never occlude

Two hard rules, both reviewer-enforced defects (`verify-and-preview.md`):

- **Stand out.** The inset carries a **border color + drop shadow** so it reads
  as a deliberate framing of the face, not a glitch. This is content-bearing
  framing, **not** editorial chrome — it is exempt from the no-chrome house rule
  the way a labeled diagram is, because the face *is* the subject.
- **Never occlude the live graphic.** The chosen archetype must **reserve a safe
  zone** for the inset, or the face sits in genuine dead space — the graphic
  stays fully visible. The reservation is a structural input the archetype
  declares (`composition-structure.md`); the safe-zone geometry — where the band
  sits, and in portrait how it dodges the phone-UI danger zones — lives in
  `visual-language.md` (and `portrait-mode.md` §safe-areas when both deltas are
  active). A full-bleed archetype (kinetic type, full-frame diagram) cannot host
  a PIP unless it is reflowed to leave that dead space.

## Transitions land on pauses — never mid-clause

A mode change (FACE↔GRAPHICS↔PIP) is a **seam-class event**. It lands on a
**natural pause / sentence boundary** pulled from the transcript — sentence
boundaries (after `.!?`) are the strong signal, `>400ms` pause gaps the
secondary one (`transcript-timing.md` narration-map). It **crossfades or
clean-pushes**, never a mid-clause whip-cut. The reveal/hide is itself an
entrance and obeys the seam discipline (cover, don't cross-dissolve;
`composition-structure.md`).

**The locked face layer is the one exception to the Entrance invariant.** The
invariant ("nothing renders solid at scene-local t=0", to stop seam bleed)
governs the graphics revealed *on top* and the PIP inset's entrance — **not** the
continuous take, which is *supposed* to persist across every seam. The Step G
seam-bleed check scopes to the graphics overlay, not the underlying take.

## The MODE verdict line — the parsed contract

When a talking-head source is active, the `scene-design-decider` adds one
labeled line to its verdict, parsed verbatim by the director. Emitted only in
talking-head mode; omitted otherwise. Exact grammar:

```
MODE: <face|graphics|pip> — transition at "<word>" (<global ms>) via <crossfade|push>; [pip-safe-zone: <region>]
```

The `pip-safe-zone` clause is present only for `pip`. The mode is named with its
rejected alternative and the principled reason, the same way imagery names the
candidate it declined (`decision-examples.md` Set C).

## Seek with GLOBAL timestamps — the offset trap

The face layer is one continuous element spanning the whole runtime, so it is
**seeked with global transcript timestamps, with zero offset** — a word's global
`start` is the exact frame to show. Do **not** apply the scene-local subtraction
(`global − data-start`) to the face seek: that math is for per-scene tweens
inside a chunk host, and using it on the take lands every face reveal at the
wrong frame. Per-scene tweens stay local; the face seek stays global.

## What does NOT change

The incremental A–I loop, transcript-as-timing-truth, the `scene-design-decider`
dispatch (it just gains the conditional MODE call), the 0.5s seam overlap, the
visual-QA loop, the SFX pass (Step H — a mode transition is a visual event
scored like any reveal; a held face is texture and stays silent), the final
reconcile + bake. Talking-head is a **layer-and-mode delta, not a different
pipeline.**
