# Timing modes — when to use `data-sfx-anchor` vs. `data-sfx-at-scene-ms`

Every cue needs exactly one timing reference. Picking the right mode is the
single most common bug surface in this pipeline — get it wrong and the SFX
lands before the visual, hard to diagnose after the fact.

## The rule, restated

| Trigger of the cue                               | Mode                                      |
| ------------------------------------------------ | ----------------------------------------- |
| A spoken word (label said, name read, line lands)| `data-sfx-anchor` + `data-sfx-anchor-index` |
| A visual change (entry, slide, snap, scale)      | `data-sfx-at-scene-ms`                    |

These are mutually exclusive. The scanner raises if both are set or neither.

A negative `data-sfx-lead-ms` ≥ 200ms on an anchor cue is the bug pattern this
file exists to prevent. If you're using anchor + large negative lead to "back
up" to a visual moment, you're using the wrong mode — switch to
`data-sfx-at-scene-ms`. `sfx-plan` will warn (via the `large lead_ms` check),
but the warning shouldn't be load-bearing — make the right choice the first
time.

## Reading a GSAP timeline to get a tween's start + duration

Scene compositions register their timelines on `window.__timelines` from an
IIFE at the bottom of the file. The pattern looks like:

```js
const tl = gsap.timeline({ paused: true });

tl.fromTo("#some-element",
  { opacity: 0, y: 30 },
  { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" },
  4.9,  // ← position parameter: when this tween starts, in scene-local seconds
);
```

To compute the perceptual landing for `#some-element`:

1. Find the tween whose target selector matches the element you're scoring.
2. Read its **position parameter** (the trailing number) — that's
   `tween_start_seconds`. Convert to ms.
3. Read its `duration` — that's `fade_or_slide_duration_seconds`.
4. Apply the perceptual-landing formula for the motion type (below).

### Staggers

`stagger: { each: N }` means each subsequent target starts N seconds after the
previous one. For a 3-target stagger with `each: 1.05` starting at `7.3`:

| Target index | `tween_start_ms` |
| ------------ | ---------------- |
| 1            | 7300             |
| 2            | 8350             |
| 3            | 9400             |

Each target keeps the same `duration` — only the start moves.

## Perceptual landing by motion type

> "Perceptual landing" = the moment the viewer's eye registers the element as
> present. SFX peak should land *there*, not on the tween's mathematical
> `data-start`.

| Motion type                                  | Landing formula                                       |
| -------------------------------------------- | ----------------------------------------------------- |
| **Fade-in (ease-in-out)**                    | `start + duration × 0.5–0.7`                          |
| **Fade-in (ease-out / expo.out / power3.out)** | `start + duration × 0.30–0.50` (opacity arrives fast) |
| **Fade-in (ease-in / power2.in)**            | `start + duration × 0.65–0.85` (opacity arrives late) |
| **Slide / translate (any ease)**             | `start + duration` (the element settles at the end)   |
| **Scale + fade combo**                       | Use the *slower* of the two — usually the fade        |
| **Opacity snap (duration ≤ 0.1s)**           | `start` exactly — no perceptual delay                 |

The 0.5–0.7 range in `SKILL.md` Rule 6 is the safe middle. Pick the lower end
for snappier eases, the upper end for slower ones.

## Worked example — scene-01-open's three target reveals

This is the broken-before / corrected-after example that motivated this whole
mechanism.

### Before — anchor + negative lead (broken)

```html
<div class="target"
     data-sfx-anchor="every" data-sfx-anchor-index="1"
     data-sfx-on-anchor="hollow-pop" data-sfx-lead-ms="-220">…</div>
<div class="target"
     data-sfx-anchor="every" data-sfx-anchor-index="2"
     data-sfx-on-anchor="hollow-pop" data-sfx-lead-ms="-550">…</div>
<div class="target"
     data-sfx-anchor="every" data-sfx-anchor-index="3"
     data-sfx-on-anchor="hollow-pop" data-sfx-lead-ms="-640">…</div>
```

Problems:
- "every" is said at multiple unrelated points; the anchor drifts if narration
  is recut.
- The negative leads (220/550/640 ms) are back-computing to *animation start*,
  not perceptual landing — so the pop lands before the card is visible.
- A per-video cue (`hollow-pop`) was added to the global catalog just to pin
  one file. Catalog pollution.

### After — at-scene-ms + pinned asset (correct)

```html
<div class="target"
     data-sfx-on-anchor="pop"
     data-sfx-asset="Mister Horse Free SFX/Pop/Hollow Pop 06.wav"
     data-sfx-at-scene-ms="7575">…</div>
<div class="target"
     data-sfx-on-anchor="pop"
     data-sfx-asset="Mister Horse Free SFX/Pop/Hollow Pop 06.wav"
     data-sfx-at-scene-ms="8625">…</div>
<div class="target"
     data-sfx-on-anchor="pop"
     data-sfx-asset="Mister Horse Free SFX/Pop/Hollow Pop 06.wav"
     data-sfx-at-scene-ms="9675">…</div>
```

The math (from the GSAP timeline at `compositions/scene-01-open.html:430-441`):

```js
tl.fromTo("#s1-targets .target",
  { opacity: 0, x: -40 },
  { opacity: 1, x: 0, duration: 0.55, ease: "expo.out",
    stagger: { each: 1.05, from: 0 } },
  7.3,
);
```

- start = 7300 / 8350 / 9400 ms
- duration = 550 ms, ease = `expo.out` (opacity arrives fast)
- landing = start + 275 ms (50% of duration — middle of the expo.out range)
- result: 7575 / 8625 / 9675 ms

Wins:
- Stable if narration is recut (timing is bound to the visual, not a word).
- Lands on perceptual midpoint of the fade — no SFX-before-visual feel.
- Uses the shared `pop` cue; the brand-specific file is pinned per-element via
  `data-sfx-asset`. No catalog change required.

## When `data-sfx-lead-ms` is still useful

Even on `at-scene-ms` cues, you may want a small lead to compensate for an
asset whose peak doesn't land at `peak_time_s`. ±100ms is normal. ≥200ms is a
smell — either pick a different asset or re-check your landing math. The
`large lead_ms` warning fires on anchor cues only (at-scene-ms cues are
exempt), but the spirit applies to both.
