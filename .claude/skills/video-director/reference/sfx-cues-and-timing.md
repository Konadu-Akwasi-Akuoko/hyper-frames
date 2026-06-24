# SFX cues and timing — which cue a visual beat earns, and how to land it

This is the look-up layer for **Step H**. SFX in this project exist to denote
**visual events** — a motion graphic happening on screen — never to enhance the
audio. So every cue is triggered by a visual change, scored while the scene's GSAP
tween times are still fresh in context. The mechanical contract is
`tools/sfx-plan`'s `data-sfx-*` attributes (`tools/sfx-plan/README.md`); this file
is the editorial reading on top of it.

## Governing principle — each cue is independent

A cue is placed for exactly one reason: **its own visual element/event warrants a
sound.** The presence, sameness, recency, proximity, or count of any *other* SFX
is irrelevant and never enters the decision. No cue is ever suppressed, delayed,
dropped, or merged because of a neighbouring cue.

Consequences, all deliberate:

- **No cross-cue rules.** No same-cue cooldowns, no dedup, no "double-hit"
  avoidance, no density caps, no rationing. The tool enforces none of these and
  neither do you.
- **Reuse freely.** The same sound may fire as often as you like — including
  repeatedly within one scene. Reusing one ding all video is *sonic branding*, not
  laziness; it makes the score read as one piece.
- **One cue per visual beat, every instance.** Three cards appearing in sequence =
  three pops, one per card (each at its own impact frame). Never score only the
  first and let the rest ride silently — every visual event earns its sound.

If a beat genuinely *isn't doing anything* (a continuous drift, an ambient pulse,
a per-character typewriter), it's texture, not an event — leave it silent. Silence
is a choice about *that element*, not about its neighbours.

## Cue selection — decide by the on-screen verb

Pick the cue by **what the beat is doing**, never by the element's CSS class. Each
cue is a *signature*: it pins one handpicked `default_asset` in
`sound-effects/sfx-catalog.yml` and reuses it across the whole video, so you
normally write just `data-sfx-on-anchor="<cue>"` and get the right sound.

| The motion is doing… | Cue | align | signature (default) |
| --- | --- | --- | --- |
| a thing **appears / pops / fades in** | `pop` | onset | Hollow Pop |
| a small **UI arrival** (tighter, sharper) | `ui-tick` | onset | Mouse Click |
| a thing is **highlighted / named / flagged** | `msg-ding` | onset | upward bell |
| a thing **lands with weight; a major point** | `boom` | onset | clean bass drop |
| a thing **slides / travels / a transition crosses** | `whoosh` | peak | fast woosh |
| a **freeze-frame / highlight one element** | `snap` | onset | camera shutter |
| a **card / tile taps in** | `card-tap` | onset | soft tap |
| a light **chip / blip arrives** | `card-blip` | onset | synthetic blip |

**`riser` is retired — do not use it.** This project's videos do not use riser
swells; for a building reveal, score the payoff frame itself (`boom`/`pop`/
`msg-ding`) rather than a pre-rolled build. `whoosh` is the only peak-aligned cue.

The cue's `align` mode is a property of the cue, not a choice you make:
**punctuation cues are onset-aligned** (the audible transient lands on the impact
frame) and **`whoosh` is peak-aligned** (the swell leads in, the peak lands
on arrival — correct only for *motion*, never for a static element appearing). If
you're tempted to put a `whoosh` on a thing that simply *appears in place*, that's
the wrong cue — use `pop`. (A whoosh's swell would read as sound-before-visual;
`sfx-plan` prints a `pre-roll` note when a peak cue precedes its own impact frame.)

If you need a cue the palette doesn't have, stop and surface the gap — adding a cue
is catalog work (`tools/sfx-catalog`), not a per-pass decision.

**When a talking-head source is present** (see `talking-head.md`), a **mode
transition** scores onto the **existing** cues by its on-screen verb — there is **no
new "mode-switch" cue**. A **FACE reveal or a PIP inset appearing in place** is a
thing that *appears* → **`pop`** (onset). A **push / slide / crossfade-with-travel
between modes** is a transition that *travels* → **`whoosh`** (peak). A **gentle
dissolve with no travel** is texture — leave it **silent**, exactly like a held face
or a continuous drift.

## Timing — `data-sfx-at-scene-ms` is the impact frame

Every cue carries exactly one timing reference: **`data-sfx-at-scene-ms`** — the
scene-local milliseconds, relative to the host composition's own `data-start`, of
the **impact frame**: the moment the element is *fully present*.

Read it straight off the GSAP tween you just keyed. The scene's timeline is the
paused IIFE at the bottom of the file:

```js
const tl = gsap.timeline({ paused: true });
tl.fromTo("#card",
  { opacity: 0, y: 30 },
  { opacity: 1, y: 0, duration: 0.55, ease: "power3.out" },
  4.9,  // ← position parameter: scene-local start, in seconds
);
```

The impact frame by motion type:

| Motion type | Impact frame (scene-local) |
| --- | --- |
| **entrance** (fade / pop / scale-in) | `start + duration` — when it's fully there |
| **slide / translate** | `start + duration` — where it settles |
| **opacity snap** (`duration ≤ 0.1s`) | `start` |
| **stagger** (`stagger: { each: N }`) | each target's `start` shifts by N; compute each independently |

So for the tween above: `start 4.9s + duration 0.55s = 5.45s → data-sfx-at-scene-ms="5450"`.

**Mode-transition impact frame (talking-head only, `talking-head.md`):** a mode
cue's impact frame is the **settle point** — the frame the reveal/push finishes
landing. Because mode transitions land on a **natural pause / sentence boundary**,
the `at-scene-ms` aligns to that pause, not a round number. The cue lives on the
**graphics host** that owns the seam (never the persistent `#face-layer`, which has
no per-scene tween), so the usual **scene-local = global − host `data-start`** still
governs: read the boundary as global ms from the transcript, subtract the graphics
host's `data-start`, write that as `data-sfx-at-scene-ms`.

That's all you supply. **`sfx-plan` does the rest** — it lands the cue's transient
on that frame, biased a hair late so it is **never early** (onset cues), or lands
the peak there with the swell leading in (whoosh). You never compute peak
offsets, leads, or "perceptual landing" multipliers; the tool reads the asset's
measured `onset_time_s` / `peak_time_s` and aligns from there.

> Very slow fades are the one nuance: if an element fades over ~1s, `start +
> duration` can feel a touch late because the eye registered it earlier. You may
> set the impact frame a little before full opacity — but **never before the
> element is clearly visible.** Late is free; early is the bug we removed.

`data-sfx-at-scene-ms` is **scene-local** — `sfx-plan` adds the host mount's
`data-start` to get global time. An annotation living directly in `index.html`
resolves at offset 0.

`data-sfx-lead-ms` is a ±100 ms peak-tuning knob only (compensating an asset whose
perceived attack differs from its measured peak). You rarely need it; never use it
to *reach* a different moment — move `at-scene-ms` instead.

## Assets — the signature is automatic

Each cue's `default_asset` is its signature sound; just writing the cue gives you
the right file, reused consistently everywhere. Pin `data-sfx-asset="<path under
sound-effects/>"` on an element **only** to deliberately diverge from the
signature for that one beat. For a per-video pool change across many cues, use
`sfx-overrides.yml` at the video root, not a `data-sfx-asset` on every element.

## Volume — a fixed 0.4 hard peg

Every cue plays at a flat **0.4**, hard-pegged in `tools/sfx-plan` (`PEG_VOLUME`).
The level is uniform by design — *no matter the sfx*. **Do not write
`data-sfx-volume`**: it is ignored, as is the catalog's `default_volume`. There is
no per-cue volume control and no ducking. When the layer is baked it mounts at
unity (`data-volume="1"`), so 0.4 is the net level of every cue. If a cue clashes
with hot VO, fix it by retiming or rechoosing the cue — not by changing volume.
Probe placement with `tools/sfx-level` (next).

## Reading `tools/sfx-level` — the VO-amplitude probe (advisory)

SFX correctness is partly **ear-only** — a snapshot can't show sound, so the human
listen-in-preview audit stays the gate each pass. `tools/sfx-level` is the
deterministic backstop: given the voiceover and a timestamp it reports the
narration's RMS/peak dBFS in a window and classifies it **gap** vs.
**active-speech**:

```bash
uv run --project ../../tools/sfx-level sfx-level audio/voiceover.mp3 --at <t>
```

`<t>` is the **global** time the cue lands at (host `data-start` + `at-scene-ms`
÷ 1000). The probe is **advisory** — volume is pegged at 0.4 and it recommends no
level. Use it to confirm a cue lands where you expect and whether it sits over a
word: `gap` → clean; `active-speech` → the cue plays at 0.4 over live narration,
usually fine, but if it muddies the word, **retime or rechoose the cue** (there is
no volume override to reach for). At the final reconcile, sweep all cues
(`--batch compositions/sfx.html`).

**Talking-head caution (`talking-head.md`):** the take's audio **is** the continuous
voiceover, so a mode-transition cue fires **over live narration** far more often than
in a faceless explainer — there are no silent graphics-only stretches to land in.
Always `sfx-level`-probe the boundary and **expect `active-speech`**; if a cue
genuinely fights the word, move it to the cleanest nearby pause rather than
quieting it.

## Worked example — a three-card stagger *(illustrative)*

> Copy the logic, not the numbers. Three cards reveal one after another:

```js
tl.fromTo("#cards .card",
  { opacity: 0, x: -40 },
  { opacity: 1, x: 0, duration: 0.55, ease: "expo.out",
    stagger: { each: 1.05, from: 0 } },
  7.3,
);
```

Each card *appears* → the verb is "appears" → **`pop`** on **each** card (three
cards, three pops — independence in action). The impact frame for each is its own
`start + duration`:

| Card | start (s) | `data-sfx-at-scene-ms` |
| --- | --- | --- |
| 1 | 7.30 | `7850` |
| 2 | 8.35 | `8900` |
| 3 | 9.40 | `9950` |

You write three `pop` annotations, one per card, each with its own `at-scene-ms`.
No pinned asset needed (the `pop` signature applies); no spacing to worry about
(independence); no volume to set (every cue is the fixed 0.4 peg); `sfx-plan`
lands each pop's transient on its card's frame, never early. If the narration is
hot under them, `sfx-level` flags it — retime or rechoose if a pop muddies a word,
but the level stays 0.4. Done.
