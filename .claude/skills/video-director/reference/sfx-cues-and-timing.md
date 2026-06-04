# SFX cues and timing — what each cue is for, and how to land it

This is the look-up layer for **Step H** (score the SFX for this pass). Step H tells you *when* to score and *how the pass is gated*; this file tells you *which cue a moment earns* and *how to time it so it lands neither early nor late*. Read it the way you read `visual-language.md` before designing a block — to pick the right tool for what the beat is doing, not to scan for elements that "should" have a sound.

The governing fact: **you are scoring one pass — the scene(s) you just authored — while that scene's GSAP tween times and the transcript word times are still in context.** That freshness is the whole point. The cue *character* comes from what the beat is *doing*; the cue *timing* comes from the tween you just wrote or the word that was just spoken. Both are in front of you right now. They won't be next session.

The mechanical contract is `tools/sfx-plan`'s `data-sfx-*` attributes, used **verbatim** (`tools/sfx-plan/README.md`). This file is the editorial reading on top of that contract — it never invents an attribute the contract doesn't define.

---

## The everyday cue is punctuation, not artillery

**Most cues you write are small.** A scene authored in a pass is a handful of GSAP beats — a thing fades in, a panel slides from an edge, a label highlights, a card taps into place. Each beat is a candidate for a *light* cue that simply punctuates the motion you already animated. That is the common case, and it is where most of your cue budget goes:

| The beat is doing…                              | Everyday cue            |
| ----------------------------------------------- | ----------------------- |
| **A thing appears** (fades/pops in)             | `ui-tick` or `pop`      |
| **A thing slides in** from an edge / traverses  | `whoosh`                |
| **A thing is highlighted / named / resolves**   | `ui-tick` or `msg-ding` |
| **A thing snaps into final position**           | `ui-tick`               |
| **A card / tile taps in**                       | `card-tap`              |

Lead with these. They are driven by *this scene's own beats*, so they're the cues the per-pass freshness exists to serve. You score them off the tween times you already have in front of you.

**`boom`, `riser`, and the single hook-silence are the heavy artillery — rationed across the whole video, not the per-pass default.** A pass usually scores zero of them. Reach for one only at a genuine peak, and only after checking the arc ledger (Step H): scan the already-placed `data-sfx-*` across all compositions, read `story-spine.md` / `script.md` for where hook/climax/landing fall, and confirm whether the boom, the riser, and the one hook are already spent. If you're about to write a `boom` in a routine pass, that is almost always the wrong cue — ask whether the moment is really *the* line the video is about, or just a thing arriving (which wants a `ui-tick`).

> **When in doubt, score less.** Silence is a tool, and an unused cue is cheaper than a wrong one. A pass that adds one well-placed `ui-tick` and skips three tempting ones is a good pass.

---

## Cue character library — pick by intent

Pick the cue by **what the moment is doing**, never by what CSS class the element wears. A `data-sfx-on-anchor` value names the cue recipe (its filter pool, default lead, default track) from `sfx-catalog.yml`'s `cues:` section. If you need a cue that isn't there, stop and surface the gap — authoring a new cue is catalog work, not a per-pass decision.

### `ui-tick` — discrete arrival *(everyday)*

Sharp, bright, ≤ 0.5s, fast attack. The sound of *a thing landing*.

- **Earns it:** a label/headline that fades in on its word; a diagram element that snaps into final position; a list item revealed in step with the line that names it; a highlight resolving on the term it marks.
- **Doesn't:** a per-character typewriter (the line is the moment, not each glyph); an element that drifts in continuously (drift is texture); an entrance masked by a louder cue.
- **Failure mode:** ticks stacked too close smear into one event. In a dense reveal, put **one** tick on the heading/first reveal and let the rest ride the visual rhythm.

### `pop` — playful arrival *(everyday)*

≤ 0.3s, warm-to-bright, soft attack. Lighter than tick, less authoritative.

- **Earns it:** rhythmic reveals where a tick would feel too sharp (icons landing on a beat); lighter-toned moments; a reveal inside an already-scored scene where another tick would crowd.
- **Doesn't:** serious/technical moments (use tick); anything that needs presence (a pop won't carry weight — use tick or boom).

### `whoosh` — spatial motion / threshold cross *(everyday)*

0.4–1.5s, swelling attack, peaks toward the middle. The sound of *something passing through*.

- **Earns it:** a panel or large element sliding in from an edge or traversing the frame; a scene-boundary cross at a real visual cut.
- **Doesn't:** small element entrances (use tick/pop); the opening beat out of cold silence (a whoosh into nothing feels jarring); a boundary that lands on a deliberate silence (the whoosh would steal the beat).
- **Failure mode:** a whoosh on *every* boundary wears thin. Reserve it for boundaries with a real visual cross; let some fall silent.

### `card-tap` — a tile lands *(everyday)*

A short, dry tap. The sound of a *card/tile placed onto a surface*.

- **Earns it:** a card, tile, or chip tapping into place — especially a small grid or rack of them. When a rack of cards taps in one after another, use the **same asset** for all of them; sameness is the point of a rack.
- **Doesn't:** a soft fade-in (that's a pop) or a slide (that's a whoosh).

### `msg-ding` — a notification / a thing flagged *(everyday)*

A bright, bell-like single hit. The sound of *attention called to a thing*.

- **Earns it:** a callout, badge, notification, or highlight that *flags* an element as noteworthy — a softer-affordance cousin of `ui-tick` when the beat is "look here," not "this snapped into place."
- **Doesn't:** a routine arrival (tick/pop); use sparingly so it stays meaningful.

### `boom` — weight / finality *(rationed)*

Sub-bass-dominated, peak near the start, 0.3–2s tail. The sound of *something landing with weight*.

- **Earns it:** the line the whole video is about, when it lands; a reveal of a huge scale paired with a major visual; the final word of a key sentence on a major reveal.
- **Doesn't:** more than once per ~30s — booms wear out instantly. Not on a function word ("is", "a") — comedic. Not every number is a boom moment.
- **Arc-ledger rule:** before writing one, scan the placed `data-sfx-*` — if a boom is already spent on a genuine peak, this beat almost certainly isn't one too. A `boom` spent early is a `boom` your 30s spacing rule keeps you from placing at the climax (the tool won't stop you — *you* hold the budget).

### `riser` — build-to-payoff *(rationed)*

≥ 1.5s, slow attack, ends on the payoff. The sound of *tension climbing toward release*.

- **Earns it:** a 1.5–3s build into a major reveal; a scene's final tension-into-revelation movement.
- **Doesn't:** more than once per scene; adjacent scenes both ending on risers (reads as filler); a riser ending in silence with no payoff cue (feels unfinished — pair it with the reveal's own cue).

### Silence — the unused cue *(rationed: the one hook-silence)*

Absence of sound is a tool:

- The line is so emphatic any sound would dilute it.
- The moment immediately precedes a big payoff — deliberate negative space.
- The texture is the texture (typewriter, ambient drift, background motion, a swarm of markers populating a diagram).

If you're tempted to add a cue but can't say *what the moment is doing*, leave it silent.

**The hook.** A video has at most **one** hook moment — its largest emotional or informational beat — marked with `data-sfx-hook="true"` on its element. The tag is a breadcrumb; the *scoring* of that beat earns **restraint, not a stack**. Two readings only: **one decisive cue** (a single `boom` on the payoff word, or a single `riser` resolving into the reveal), or **silence into the hit** (the beat before runs silent so the one hook cue lands out of negative space — the strongest version when the visuals already carry the weight). A tick + whoosh + boom on the same moment is mud, not impact. The hook is part of the whole-video ration — scan the placed annotations to confirm **exactly one** `data-sfx-hook` exists before adding one in a pass. The final reconcile (`sfx-arc-and-reconcile.md`, Done condition) verifies that count and that the hook was scored with restraint.

---

## Timing mode — the load-bearing choice

Every cue needs **exactly one** timing reference. `data-sfx-anchor` and `data-sfx-at-scene-ms` are **mutually exclusive** — `tools/sfx-plan` raises at scan time if both are set or neither. Picking the wrong mode is the single most common bug in this pipeline: the cue lands before the visual, and it's hard to diagnose after the fact. Decide the mode *before* you pick the cue.

| The trigger is…                                       | Mode                                          |
| ----------------------------------------------------- | --------------------------------------------- |
| **A visual change** (entry, slide, snap, highlight)   | `data-sfx-at-scene-ms`                        |
| **A spoken word** (label said, name read, line lands) | `data-sfx-anchor` + `data-sfx-anchor-index`   |

Ask one question: **is the thing I'm punctuating a visual change, or a spoken word?** Because the everyday cues are driven by the scene's own GSAP beats, **`at-scene-ms` is the common mode** — read straight off the tween you just wrote. Reach for `anchor` only when the trigger genuinely *is* a spoken word: a label spoken aloud, a name said, a payoff line landing on its word.

> **The forbidden bug:** using `data-sfx-anchor` + a large negative `data-sfx-lead-ms` to "back up" from a spoken word onto a *visual* moment. That is SFX-before-visual desync. If you're reaching a visual with a negative lead, you've picked the wrong mode — switch to `data-sfx-at-scene-ms`, which binds the cue to the visual directly. `sfx-plan` *prints* a `large lead_ms` warning at ≥ 200ms on anchor cues (it does **not** fail the run — the CLI still exits 0); **you treat it as blocking** and fix it before proceeding. Make the right call the first time — the warning is the backstop, not the plan.

### Reading the GSAP tween for `at-scene-ms`

`data-sfx-at-scene-ms` is **scene-local milliseconds**, relative to the host composition's own `data-start`. The scene's timeline is registered on `window.__timelines["<id>"]` from a paused IIFE at the bottom of the file you just authored. A tween looks like:

```js
const tl = gsap.timeline({ paused: true });

tl.fromTo("#some-element",
  { opacity: 0, y: 30 },
  { opacity: 1, y: 0, duration: 0.6, ease: "power3.out" },
  4.9,  // ← position parameter: scene-local start, in seconds
);
```

To get the cue's `data-sfx-at-scene-ms`:

1. Find the tween whose target selector matches the element you're scoring.
2. Read the **position parameter** (the trailing number) → `start`. Convert to ms.
3. Read `duration`.
4. Apply the **perceptual-landing** formula for the motion type.

**Perceptual landing** = the moment the viewer's eye registers the element as *present*. The SFX peak lands *there*, not on the tween's mathematical start.

| Motion type                                       | Landing time                                  |
| ------------------------------------------------- | --------------------------------------------- |
| **Fade-in, ease-in-out**                          | `start + duration × 0.5–0.7`                  |
| **Fade-in, ease-out / expo.out / power3.out**     | `start + duration × 0.30–0.50` (arrives fast) |
| **Fade-in, ease-in / power2.in**                  | `start + duration × 0.65–0.85` (arrives late) |
| **Slide / translate (any ease)**                  | `start + duration` (settles at the end)       |
| **Scale + fade combo**                            | use the *slower* of the two (usually the fade)|
| **Opacity snap (duration ≤ 0.1s)**                | `start` exactly — no perceptual delay         |

The `0.5–0.7` band is the safe middle for an unspecified ease: lower end for snappier eases, upper end for slower ones. **Fades** take the midpoint band; **slides and snaps** take `start + duration` because the element is still travelling until the end.

For a **stagger** (`stagger: { each: N }`), each subsequent target starts N seconds after the previous one; every target keeps the same `duration`. Compute each landing independently. A 3-target stagger with `each: 1.05` from `7.3`, `duration: 0.55`, `ease: expo.out` (→ 50% of duration):

| Target | start (ms) | landing (ms) |
| ------ | ---------- | ------------ |
| 1      | 7300       | 7575         |
| 2      | 8350       | 8625         |
| 3      | 9400       | 9675         |

### Picking an anchor for the speech path

When the trigger genuinely is a spoken word, the anchor must already resolve via `narration-map.json` **at write time**. The chain is `anchors.txt → tools/narration-map → narration-map.json → tools/sfx-plan`. If the word you want isn't in the map, append it to `anchors.txt` (grouped under a `# sfx anchors` comment) and re-run `tools/narration-map` *before* writing the attribute:

```bash
uv run --project ../../tools/narration-map narration-map \
    transcript.json --anchors anchors.txt
```

Choosing the word:

- **Prefer the conceptually-loaded word**, not a function word — anchor the noun the beat is *about*, never "the"/"is"/"a". A boom on "is" is comedic; a boom on the noun lands.
- **Prefer emphatic words.** `narration-map.json`'s `emphatic_words` ranks words by spoken duration — where the voice lingers is often the key term.
- **Prefer a single word** over a phrase, unless the phrase *is* the moment.
- **Match the visual peak, not the visual start.** A label that fades over 200ms is resolved at the *end* of the fade; the anchor word should fall in or just after that window.

**`data-sfx-anchor-index`** disambiguates a word said more than once — 1-indexed, in spoken order (`narration-map.json`'s `matches` array). Never share one anchor + index + cue across two elements — they'd resolve to the same file and overlap; use different indices, cues, or anchors. Don't hand-edit the generated `narration-map.json` (edit `anchors.txt` and re-run), and don't bloat `anchors.txt` with a word when an existing anchor a few words earlier would land just as tight.

If the moment is in **pure silence** (a pre-VO opener, a logo before narration), no spoken word exists to anchor on — surface the gap rather than faking a word.

---

## Peak alignment, leads, and the ±100ms rule

- **Peak alignment is `sfx-plan`'s job, not yours.** A cue's *peak* (the catalog's `peak_time_s`) is what lands on the resolved reference — the anchor word's `start`, or the `at-scene-ms` you computed — **not** the cue file's own start. `tools/sfx-plan` does that subtraction for you. Your job is to pick the reference correctly; the tool aligns the peak from there.
- **Default leads** come from the cue recipe and ride automatically: `-50ms` for `ui-tick`, `-150ms` for `whoosh`, `0ms` for `boom`, `-(duration)` for `riser` (so it *ends* on the payoff). You don't write these; leave them alone unless you have a specific reason, and note the reason in the proposal if you override.
- **`data-sfx-lead-ms` is a ±100ms peak-tuning knob, never a timing-source knob.** Use it only to compensate for an asset whose perceived attack differs from its measured `peak_time_s`. A ≥ 200ms shift is a smell: you're either using the wrong mode (switch to `at-scene-ms`) or the wrong asset (pick one with a tighter attack). Never use lead to *reach* a different moment — that's the forbidden anchor-to-visual pattern, and the fix is `data-sfx-at-scene-ms`, not a bigger lead.

---

## Spacing and density — what the tool enforces vs. what you enforce

Be precise about which constraints `tools/sfx-plan` actually checks and which are
your own craft discipline. Conflating them leads to either trusting a guard that
isn't there or treating an advisory note as a hard stop.

**What `sfx-plan` actually enforces** (`validate.py`):

- **Per-track overlap (warning).** Two cues on the *same* `data-track-index`
  can't overlap — a cue must not start before the previous cue on its track ends.
  `sfx-plan` emits an `overlap on track N` warning; treat it as blocking.
- **Density hard cap (raises, fails the run).** Density is a rolling **6-second**
  window. Above **1.0 cues/s** (≈ 1 per 1s) `sfx-plan` raises
  `DensityViolationError` and exits non-zero — the ducking math thrashes and VO
  intelligibility collapses. Drop the lowest-priority cues in the densest window
  and re-run.
- **Density warning (advisory).** Above **0.5 cues/s** (≈ 1 per 2s) over that 6s
  window it prints a `density …/s` warning to stderr — not a failure, a nudge to
  trim.
- **Large-lead warning (advisory, anchor cues only).** `|data-sfx-lead-ms| ≥ 200`
  on an anchor cue prints a warning (the SFX-before-visual smell); `at-scene-ms`
  cues are exempt. It does **not** fail the run — *you* treat it as blocking.

**What the tool does NOT enforce — your editorial spacing heuristic:**

- **Same-cue cooldowns are not a tool check.** There is no minimum-gap logic and
  no `cooldown` field in the catalog. Keep your own spacing anyway, because two
  hits of the same cue too close together smear: aim for `ui-tick` ≥ 2s apart,
  `whoosh` ≥ 4s apart, `boom` ≥ 30s apart. When the same everyday cue would fire
  three times in quick succession (a list of items appearing), score **one** cue
  on the heading/first reveal and let the rest ride the visual rhythm. The tool
  won't flag a 1.2s tick pair — *you* prevent it.

As an **editorial target**, keep the whole-video average comfortably under the
tool's warn line — roughly **≤ 1 cue per 3s** is a safe aim that leaves headroom
below the 1-per-2s warning. Within that, cue frequency is itself a signal: where
hits cluster, the moment reads busy and high-stakes; where they thin, it reads
calm or weighty. Spend the budget so its shape tracks the story's energy — dense
where the script escalates, silent where it breathes (the > 600ms pauses
`narration-map.json` surfaces are *not* slots to fill). Because your boom spacing
is a budget, a `boom` spent in a low-stakes moment is one you can't place near the
climax — saving it is as deliberate as spending it.

Because Step H scores one pass at a time, your spacing also reaches *backwards*:
check the `data-sfx-*` already placed in the **previous** scene's tail before
scoring this scene's opening cue, so a seam doesn't double-hit. The whole-video
density curve is re-checked at the final reconcile.

---

## Asset pinning — `data-sfx-asset` on every cue

Picking the *file within the cue's pool* is the other half of the decision, and it's editorial — not a resolver job. **Every cue pins its asset via `data-sfx-asset`** (a path under `sound-effects/`). Browse `sfx-catalog.yml`'s `assets:` section (filtered by the cue's pool) and pick by, in order:

1. **Cross-scene consistency.** If the same cue is already scored elsewhere in the video with a specific asset, **reuse that asset** unless this moment's character explicitly diverges. The score reads as one piece when a cue family always sounds the same. (Scan the placed `data-sfx-asset` values as part of the arc ledger — they tell you what each cue family already sounds like.) When the same cue fires several times in a row (a "rack"), use the *same* asset for all of them; that sameness is the point.
2. **Character match.** Among pool assets, pick the timbre that matches what the beat is doing — sharper for snaps, hollower for soft arrivals, brighter for lifts.
3. **Duration fit.** Don't pick an asset longer than the visual moment it punctuates — a 600ms tail on a 200ms landing smears.

```html
<div data-sfx-on-anchor="pop"
     data-sfx-asset="Mister Horse Free SFX/Pop/Hollow Pop 06.wav"
     data-sfx-at-scene-ms="7575">…</div>
```

`tools/sfx-plan` has a deterministic filter+hash resolver that still runs as a *safety net* for any cue that slipped through without a pinned asset — but never rely on it. Falling through produces **timbrally inconsistent scores**, where the same cue family sounds different in scene 1 than in scene 4. Pinning short-circuits only the *asset picker* — the cue still supplies its default volume, lead, and track. Never add a one-off cue to the global catalog just to force a file (catalog pollution); pin per-element instead. For a per-video pool tweak that should apply across *many* cues, the right surface is `sfx-overrides.yml` at the video folder root, not a `data-sfx-asset` on every element.

---

## Volume — the flat-0.5 default and ceiling

Every cue's volume is a **flat 0.5 by default**, set once as `default_volume: 0.5` in `sound-effects/sfx-catalog.yml` (the single source of truth). **Do not write `data-sfx-volume="0.5"` on elements** — that's the default already.

**0.5 is both the default and the ceiling.** A cue never goes above 0.5. Write `data-sfx-volume` on an element **only to duck *below* 0.5** — when the cue is fighting hot VO and needs to sit under it. There is no louder-than-0.5 cue.

---

## Reading `tools/sfx-level` — the VO-amplitude probe

SFX correctness is partly **ear-only** — a snapshot can't show sound, so the human listen-in-preview audit stays the gate each pass. `tools/sfx-level` is the *deterministic backstop*: a VO-amplitude probe (it reuses `tools/cut-snap`'s numpy RMS-envelope DSP) that, given the voiceover and a timestamp, reports the narration's RMS dBFS + peak dBFS in a small window around that time and classifies it **gap** vs. **active-speech**. Invoke it from the video folder with the cue's resolved time:

```bash
uv run --project ../../tools/sfx-level sfx-level audio/voiceover.mp3 --at <t>
```

`<t>` is the **global** time the cue lands at (the anchor word's resolved start, or the host `data-start` + `at-scene-ms` ÷ 1000). Use it for two things per pass:

1. **Confirm the cue times correctly** — that the moment you're scoring is a real narration gap (for cues meant to land in the clear), or that the VO context around it is what you expected. If a cue you *expected* in a gap comes back `active-speech`, re-check your landing math.
2. **Recommend a duck** — when the VO is hot at the cue's landing, bring the cue below the 0.5 default so it doesn't fight the voice.

**Reading the output:**

- **`gap`** — the VO is quiet here; the cue lands in the clear. Leave volume at the 0.5 default. (This also confirms an `at-scene-ms` cue is timed into a real gap, not on top of a word.)
- **`active-speech`** — the VO is carrying words through the window. The tool's `recommended_volume` stays at 0.5 for ordinary speech and only drops (to ~0.42, then ~0.35) when the window approaches the track's loudest-speech level. When it recommends a duck, set `data-sfx-volume` to that value on the cued element so the cue tucks under the voice. Never above 0.5.

At the final reconcile, run `sfx-level` across all cues (`--batch compositions/sfx.html`) to catch any that fight loud VO before handing off.

---

## Worked example — an opening scene's staggered reveal *(generic / illustrative)*

> Illustrative, not a recipe. The reasoning transfers; the scene does not. Copy the *logic* — read the tween, compute the landing, pin the asset, duck if the VO is hot — never these literal numbers or selectors.

A scene's opening beat: three small items reveal one after another as the narration introduces them — the everyday **"a thing appears"** case, three times. The GSAP at the bottom of the scene file:

```js
// from the scene's window.__timelines IIFE
tl.fromTo("#items .item",
  { opacity: 0, x: -40 },
  { opacity: 1, x: 0, duration: 0.55, ease: "expo.out",
    stagger: { each: 1.05, from: 0 } },
  7.3,
);
```

**Mode.** These are *visual* arrivals, so `at-scene-ms` — not an anchor on the spoken word. Anchoring a repeated word here and using a large negative `data-sfx-lead-ms` to "reach back" to where the item is visible would be the forbidden bug: the word drifts if narration is recut, and the negative lead lands the cue before the item is visible.

**Cue.** A light arrival — `pop` (or `ui-tick` if the tone is sharper). Not a boom; nothing here is *the* line the video is about.

**Landing math.** `expo.out` makes opacity arrive fast → 50% of the 550ms duration:

| Item | start (ms) | `data-sfx-at-scene-ms` |
| ---- | ---------- | ---------------------- |
| 1    | 7300       | 7575                   |
| 2    | 8350       | 8625                   |
| 3    | 9400       | 9675                   |

**Asset.** One pinned file reused across all three (a rack reads as one gesture):

```html
<div class="item"
     data-sfx-on-anchor="pop"
     data-sfx-asset="Mister Horse Free SFX/Pop/Hollow Pop 06.wav"
     data-sfx-at-scene-ms="7575">…</div>
<div class="item"
     data-sfx-on-anchor="pop"
     data-sfx-asset="Mister Horse Free SFX/Pop/Hollow Pop 06.wav"
     data-sfx-at-scene-ms="8625">…</div>
<div class="item"
     data-sfx-on-anchor="pop"
     data-sfx-asset="Mister Horse Free SFX/Pop/Hollow Pop 06.wav"
     data-sfx-at-scene-ms="9675">…</div>
```

**Level check.** The items land while the narration is naming them, so probe `sfx-level audio/voiceover.mp3 --at 7.575` (the host `data-start` plus 7.575s, in global time). If it reads `active-speech` with a duck recommended, add `data-sfx-volume="0.35"` so the pops sit under the voice; if it reads `gap`, leave the 0.5 default.

**What's *not* scored here:** any continuous drift-in behind the items (texture, not punctuation); a per-character typewriter or eyebrow metadata (the line is the moment, not each glyph); a swarm of small markers populating in the same window (they ride the visual rhythm — clicking each one turns the scene into a bleep festival and burns the cooldown the next real cue needs). And no `boom`/`riser` anywhere in this pass; those are rationed for a genuine peak elsewhere in the video.
