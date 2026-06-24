# SFX per-pass score and the final reconcile

Step H scores the SFX for **only the scene(s) you authored in this pass**, while
the scene's GSAP tween times are still fresh. SFX denote **visual events** — a
motion graphic happening — so every cue is triggered by a visual change. The cue
character + the impact-frame timing math live in `sfx-cues-and-timing.md`; this
file is the per-pass workflow and the whole-video reconcile.

## The governing rule — each cue is independent

A cue is placed because *its own* visual event warrants a sound. The presence,
sameness, recency, proximity, or count of any other SFX is irrelevant. **No cue is
ever suppressed, delayed, dropped, or merged because of a neighbour.** There are
no cross-cue rules — no cooldowns, no dedup, no density caps, no rationing. Reuse a
sound as often as you like, including within one scene; score every visual beat
that's *doing* something, one cue per occurrence.

Read each beat's verb and reach for the cue (full palette in
`sfx-cues-and-timing.md`):

| The beat is doing… | Cue |
| --- | --- |
| appears / pops / fades in | `pop` (or `ui-tick` for a small UI arrival) |
| highlighted / named / flagged | `msg-ding` |
| lands with weight; a major point | `boom` |
| slides / travels / a transition crosses | `whoosh` (peak-aligned, motion only) |
| freeze-frame / highlight one element | `snap` |
| a card / tile taps in | `card-tap` |

Texture is not an event: a continuous drift, an ambient pulse, a per-character
typewriter, a swarm of markers populating — leave them silent.

When a talking-head source is present (`talking-head.md`), a **FACE↔GRAPHICS↔PIP
mode transition is a scorable visual event** — score it off the table like any
reveal (`pop` on a graphics arrival, `whoosh` on a push). But **a held
talking-head shot with no graphic change is texture and stays silent** — a held
talking-head shot is not an event. Guard against double-scoring the seam: the
transition *into* graphics **is** that scene's entrance cue — score **one cue per
reveal**, not two stacked at the seam (a transition cue and a separate entrance
cue for the same arriving graphic).

## The hook tag (one per video, for the music pass)

Mark the single largest beat of the whole video — its one biggest emotional or
informational moment — with `data-sfx-hook="true"` on its element. It is a
breadcrumb the downstream `audio-bed-music` pass reads to carve pre-impact silence
under the bed; **exactly one** exists across all compositions. If this pass has no
clear hook, omit it — a later scene may own it. (This is just a tag on one
element; it is not a cross-cue suppression rule.)

## Timing — the impact frame, aligned by the tool

The only mode is `data-sfx-at-scene-ms` = the scene-local ms of the element's
**impact frame** (entrance: tween `start + duration`; slide: settle; snap: the
snap frame). `sfx-plan` lands the transient there — onset cues on the frame biased
a hair late (never early), `whoosh` peak-on-arrival with the swell leading in.
(`riser` is retired — this project's videos do not use riser swells.)
You supply only the impact frame; the tool reads the asset's measured
onset/peak and aligns. `data-sfx-lead-ms` is a ±100 ms tuning knob only.

Each cue's signature `default_asset` applies automatically — pin `data-sfx-asset`
only to deliberately diverge for one beat.

For a talking-head mode-transition cue (`talking-head.md`), the **impact frame is
the crossfade midpoint / push settle** — which coincides with the pause boundary
the transition lands on. The scene-local ms math is unchanged: it's still
`data-sfx-at-scene-ms`, just measured at that midpoint/settle frame.

## The compact per-pass proposal + standing approval

The approval gate stays — annotations are written only on `yes` / `approve` /
`go` — but it's a compact, per-pass form so the autonomous loop isn't interrupted.
Print only the cues for **this pass's scene(s)**:

```
SFX — pass scene(s): <NN[-MM]>   hook: <set this pass? / already set / none>
  ✓ cue=<name>  asset=<basename>  at <NNNNms | #id>   (<short reason — the verb>)
  ✓ cue=<name>  asset=<basename>  at <NNNNms | #id>   (<short reason>)
  ✗ skip  <ref>   (<why it's texture, not an event — 6–10 words>)
Approve to write?  [yes / refine / abort]   (or "auto-approve SFX for the rest")
```

- `asset=` shows the basename (usually the cue's signature default; only differs
  when you pin a divergence).
- `at <NNNNms>` is the scene-local impact frame.
- Skips matter as much as writes — they make the editorial reasoning legible.
- In talking-head mode (`talking-head.md`), a transition cue's reason-string reads
  as the transition itself (`graphics crossfades over face`); a held-face beat is a
  logged skip with the texture rationale (`held talking-head shot, no graphic
  change`).
- **Standing approval:** if the user replies *"auto-approve SFX for the rest"*,
  drop the per-pass gate for the remainder of the loop and write directly each
  pass — but still print the proposal block for the record and run the backstops.

On `refine`, treat the instruction as a transformation on the plan and re-print.
On `abort`, write nothing.

## After approval, per pass

1. Add `data-sfx-*` attributes with the `Edit` tool — **one element per call**,
   never reformatting surrounding HTML. The common case is just
   `data-sfx-on-anchor="<cue>"` + `data-sfx-at-scene-ms="<ms>"`.

2. Regenerate the audio sub-composition (idempotent — it rewrites all of
   `compositions/sfx.html` from the placed annotations every run):

   ```bash
   uv run --project ../../tools/sfx-plan sfx-plan --report
   ```

   The run **never fails on cue count or density** (those guards are gone). It
   prints only informational notes:
   - a **`pre-roll`** note → a peak-aligned cue (`whoosh`) is audible
     before its own impact frame. Fine if it's leading a real *motion*; if it's
     punctuating a thing *appearing*, switch it to `pop`/`ding`.
   - an **overlap** note → two cues share a track and overlap. Benign — concurrent
     cues layer; the tool lane-packs them. No action needed.
   - a **clamped** note → a cue's computed start went negative and was pinned to 0.

3. On first run only, the `sfx-layer` host is mounted in `index.html`. Confirm its
   `data-duration` spans the **full runtime** — a short mount clips late cues.

## SFX correctness is partly ear-only

A snapshot can't show sound, so the **human listen-in-preview audit stays the gate
each pass**. After `sfx-plan` regenerates the layer, surface the seek target:

> Scored scene NN. Seek to **{cue_time}s** to hear the cue land.

The user reloads their own `npx hyperframes preview` — **never start, restart, or
kill the preview server.**

## Final whole-video reconcile (runs once, at the Done condition)

When the whole script is covered and every scene has had its per-pass score, run
one reconcile pass before handing off:

1. **Regenerate everything.** `uv run --project ../../tools/sfx-plan sfx-plan
   --report` over the full video (idempotent).
2. **Pre-roll notes are intended.** Every `pre-roll` note should be a `whoosh`/
   leading a real motion — not one punctuating an appearance. Fix the
   strays to `pop`/`ding`.
3. **Exactly one hook.** Confirm precisely one `data-sfx-hook` exists across all
   compositions:
   ```bash
   grep -rn 'data-sfx-hook' compositions/
   ```
   In talking-head mode (`talking-head.md`), the single hook must map to a **real
   motion-graphic beat**, never a **bare face reveal** — a held or revealed face is
   texture, not the video's biggest event; pin the hook to the graphic that carries
   the moment.
4. **sfx-level sweep (advisory).** Run `tools/sfx-level` across every cue's landing
   time (`--batch compositions/sfx.html`) to catch any cue fighting loud VO. Volume
   is a fixed 0.4 peg and not adjustable, so the fix for an offender is to **retime
   or rechoose the cue** (move it to a cleaner nearby pause, or drop it if it's
   texture), then re-run `sfx-plan`. When a talking-head source is present
   (`talking-head.md`) this sweep matters **more**: the on-camera audio is
   near-omnipresent (no graphics-only stretches where VO drops out), so more cues
   land over live voice — sweep every landing.
5. **Full-runtime mount.** Verify the `sfx-layer` host's `data-duration` spans the
   full runtime so no late cue is clipped.

Then **bake** (SKILL.md Done condition) and **hand off to `audio-bed-music`** —
music sits *beneath* SFX. Identify the hook precisely so the music pass can agree
with it; you do not score the music.

## Failure modes you must handle

- **`sfx-catalog.yml` missing** → stop; direct the user to
  `uv run --project tools/sfx-catalog sfx-catalog`. Don't author against an
  imaginary catalog.
- **Composition has placeholder stubs** (`[ TO BE BUILT ]`, `PLACEHOLDER`) → that
  scene's visuals aren't settled; do not score it. SFX follows finished visuals.
- **A requested cue isn't in the catalog** → don't invent it. Name the available
  cues, suggest the closest, and offer a catalog-revision task. Adding cues is
  `tools/sfx-catalog` work, outside this step.
