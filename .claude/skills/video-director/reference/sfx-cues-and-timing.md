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
| tension **builds into a reveal** | `riser` | peak | Riser Stop (peak@82%) |
| a **freeze-frame / highlight one element** | `snap` | onset | camera shutter |
| a **card / tile taps in** | `card-tap` | onset | soft tap |
| a light **chip / blip arrives** | `card-blip` | onset | synthetic blip |

`riser`'s climax sits near the end of its file, so peak-align lands the climax on
the reveal with the full build leading in. (`sfx-plan` prints a `pre-roll` note for
it — that long pre-roll *is* the build, so it's expected for a riser.)

The cue's `align` mode is a property of the cue, not a choice you make:
**punctuation cues are onset-aligned** (the audible transient lands on the impact
frame) and **whoosh/riser are peak-aligned** (the swell leads in, the peak lands
on arrival — correct only for *motion*, never for a static element appearing). If
you're tempted to put a `whoosh` on a thing that simply *appears in place*, that's
the wrong cue — use `pop`. (A whoosh's swell would read as sound-before-visual;
`sfx-plan` prints a `pre-roll` note when a peak cue precedes its own impact frame.)

If you need a cue the palette doesn't have, stop and surface the gap — adding a cue
is catalog work (`tools/sfx-catalog`), not a per-pass decision.

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

That's all you supply. **`sfx-plan` does the rest** — it lands the cue's transient
on that frame, biased a hair late so it is **never early** (onset cues), or lands
the peak there with the swell leading in (whoosh/riser). You never compute peak
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

## Volume — 0.5 is the default and the ceiling

Every cue's volume is a flat **0.5**, set once as `default_volume: 0.5` in the
catalog. **Do not write `data-sfx-volume="0.5"`.** A cue never goes above 0.5;
write `data-sfx-volume` **only to duck below 0.5** when the cue is fighting hot VO.
Probe the narration under a cue with `tools/sfx-level` (next).

## Reading `tools/sfx-level` — the VO-amplitude probe

SFX correctness is partly **ear-only** — a snapshot can't show sound, so the human
listen-in-preview audit stays the gate each pass. `tools/sfx-level` is the
deterministic backstop: given the voiceover and a timestamp it reports the
narration's RMS/peak dBFS in a window and classifies it **gap** vs.
**active-speech**:

```bash
uv run --project ../../tools/sfx-level sfx-level audio/voiceover.mp3 --at <t>
```

`<t>` is the **global** time the cue lands at (host `data-start` + `at-scene-ms`
÷ 1000). Use it to confirm a cue lands where you expect and to decide a duck:
`gap` → leave 0.5; `active-speech` with a hot window → set `data-sfx-volume` to the
recommended ducked value (never above 0.5). At the final reconcile, sweep all cues
(`--batch compositions/sfx.html`).

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
(independence); `sfx-plan` lands each pop's transient on its card's frame, never
early. If the narration is hot under them, `sfx-level` may suggest a duck — set
`data-sfx-volume` below 0.5 on each. Done.
