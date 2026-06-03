# Iteration 3 — skill tuning (imagery push), pre-authoring

This records the **skill changes made between iteration 2 and iteration 3**, driven by the
human's scene-by-scene verdict on the iteration-2 batch. No scenes are authored here — the
human re-authors next, and that batch becomes iteration 3's gradable output.

## What the iteration-2 grade surfaced

Iteration 2 landed 5 of 6 findings; the holdout was **imagery** (#3 / #6b). Crucially, the
director didn't forget it — it *consciously declined*, calling all three opening beats
"text-driven," which the skill's soft wording permitted. The human's verdict:

- Scene 1 (HN quote card): fine, leave it.
- Scene 2: **loved the full-bleed kinetic type — want more of it.** But the payoff line
  ("the language nobody wanted now runs the world's infrastructure") is genuinely **ironic
  and funny** — a prime imagery beat. The human web-searched "celebrity laughing," picked a
  **Steve-Harvey-laughing** reaction shot, and wants a laughing cutout there to make it
  funnier / more watchable / lower click-away (the reference creator's signature move).
- **Craft discovery:** when a reaction image carries the beat, the image *is* the contrast,
  so **don't also dim the opposing text and don't draw a divider line** — those were
  split-contrast crutches that become competing over-decoration with a face present.

So the lever this iteration: **push the skill's imagery guidance from a neutral question
the director answers "no" to → a signal-driven default it reaches for** — without
overfitting (no forcing faces onto genuine text beats, no scene-number rules).

## How the tuning was produced

Used a `/workflows` design panel (run `wf_79999e15-891`, 9 agents): four candidate
rewrites from distinct strategies (trigger-list, show-don't-tell ratio, comedic-payoff,
reference-creator-voice), each scored by a skeptic judge weighted hard on **anti-overfit**,
then one synthesizer grafted the winners into drop-in edits. All four candidates scored
**push 5 / anti-overfit 4 / generality 5 / voice 4**; `trigger-list` ranked first. The
synthesizer's consolidated edits were applied **serially by hand** (parallel agents are not
allowed to mutate the skill files — see the workflow-editor stray-delete gotcha in memory).

## The five edits (all generalizing, none scene-specific)

| # | File | Change |
|---|---|---|
| 1 | `SKILL.md` Step D | Replaced the neutral "does this beat want real imagery?" yes/no with a **signal-list default-flip**: a named emotion / irony-comedy-punchline / human reaction / named "who" / concrete recognisable thing → **default to declaring an asset box, reach for it**. Pure text on a signal beat becomes the *justified exception*; text-only stays legitimate for genuinely typographic beats. Closes with "the test is the signal in the sentence, **not the scene number, and never a quota**." |
| 2 | `reference/visual-language.md` §2 | Appended the **"let the image carry — don't double up"** rule: when a reaction/emotion image carries a contrast beat, don't *also* dim the opposing text or draw a divider line; pick one device, not both. |
| 3 | `reference/assets-and-media.md` (Declaring a box) | One-line pointer to §2 once a reaction box is in play on a contrast beat. |
| 4 | `reference/assets-and-media.md` (When not to use imagery) | Reframed into a **two-sided "when imagery earns its place — and when it doesn't"** section with a **video-agnostic** worked case (ironic payoff → laughing-reaction cutout, with the do-not-dim/do-not-divide note), keeping the typographic/code-drawable counterweight. Phrased as a beat *category* ("an ironic payoff"), never "scene 2." |
| 5 | `reference/verify-and-preview.md` (Imagery fit) | Rewrote the trigger to key on the imagery signals (matching Step D) **and added a run-level flag**: a stretch of several consecutive bare-text beats is itself worth surfacing — which catches the exact iteration-2 failure (three text-driven beats in a row) at the layer where it's visible, without mandating imagery on any single frame. |

## Overfitting guards (the thing we explicitly protected)

- Every trigger is a **content property of the sentence**, never a scene index.
- Text-only is affirmed as legitimate (and forcing a face onto a typographic beat is named
  "as wrong as never reaching for one").
- The run-level check is a *balance*, not a quota — no numeric threshold, no per-frame mandate.
- The worked example is a reusable **beat category** ("ironic payoff"), not "the JS video scene 2."

## What iteration 3 tests

The human re-authors (scene 2 at minimum) against the tuned skill. Success =
- a **laughing reaction cutout** (or another fitting image) appears on the ironic
  "infrastructure" payoff — i.e. the director now *reaches* for imagery on a signal beat;
- it's done **without** dimming the opposing line or drawing a divider (the craft rule held);
- the full-bleed kinetic type the human loved is preserved/expanded;
- **no regression**: text-first beats (e.g. the scene-1 quote, the scene-3 pivot question)
  do **not** suddenly grow gratuitous faces. That last point is the overfitting check — if
  faces appear everywhere, the push went too hard and the wording needs to pull back.

Asset handoff unchanged: the director declares a labeled box + emits a shopping list; the
human supplies the Steve-Harvey-laughing file; `tools/image-prep --remove-bg --preset
grain,duotone` produces the treated cutout the box swaps to.

## Closing the sourcing loop — the `image-sourcer` agent (added post-tuning)

After the five edits landed, the human pushed further: the *box mechanism* isn't the
bottleneck — the **human round-trip to find the file** is. So we automated the fill. The box
stays as the spec (it still reserves the footprint and records intent so layout verifies
before the asset exists); a new agent now sources the image instead of the human.

**Mechanism proven live before writing the agent** (this repo's verify-then-crystallize
pattern, à la cut-snap/dup-detect). Drove Chrome through the real Steve-Harvey case:

- Pinterest search loads logged-in (user = Coded_KAA) — **no login wall** on the search grid.
- One `javascript_tool` query extracts every candidate's full-res URL from the grid: filter to
  real pins (`/pin/` ancestor + sized thumbnail, which drops `75x75_RS` profile avatars),
  rewrite the thumbnail path `/236x|474x|564x|736x/` → `/originals/`, dedupe, then **probe each
  by loading it as an `Image()`** so dead URLs never get returned.
- `/originals/` **resolves at full res** — verified 1080×892, 1200×978, 1484×1397 — and each
  pin's `alt` ("two men laughing, one holding his mouth wide open") gives a match string. No
  per-pin clicking, no proxy dance.

**NEW `.claude/agents/image-sourcer.md`** (`model: sonnet`, medium-effort budget) encodes that
verified procedure: Pinterest-first → web-image-search fallback → pick the best emotion-matched,
cutout-able shot from the screenshot + alt/dimensions → `curl` the original → `image-prep`
`--remove-bg --preset <treatment>` → return a structured report (source, URL, dims, treated
path, **confidence + why**, runner-ups, flags). Advisory: the director weighs confidence and
swaps the pick in, or falls back to the shopping list on low-confidence / no-suitable-asset.

**Wiring:** `reference/assets-and-media.md` gains a "Filling a box yourself — the `image-sourcer`
agent" section (auto-source is the default; the shopping list is reframed as *the fallback* for
the hard cases); `SKILL.md`'s delegation map gains an `image-sourcer` row above `tools/image-prep`.

**Reload caveat (load-bearing for iteration 3):** agent `.md` files load at **session start**,
not live-watched. `image-sourcer` is therefore dispatchable starting the *next* session — which
is exactly when the human re-authors iteration 3, so the timing is fine. (The five skill edits,
by contrast, are live-watched and already active.)

**What this adds to the iteration-3 test:** beyond "does the director reach for imagery on the
ironic beat," iteration 3 now also tests whether it **dispatches `image-sourcer` to fill the
box** rather than emitting a shopping list — i.e. the laughing cutout should appear *sourced and
treated*, with the human only confirming the pick (or correcting a low-confidence one), not
hunting the file.

## Referent imagery — a second category + multi-source routing (added post-tuning)

The human pushed once more: reaction shots are only *one* kind of imagery. When the script
**names a concrete recognisable thing** (JavaScript, infrastructure, a company, a place), you can
show *that thing* — its logo, an icon, a real photo. Different category, different sources. The
human named the sources: **Wikimedia Commons** (photos of notable real things), **Iconify** (SVG
logos/icons), open-web as catch-all. Asked to use `/workflows` since there was nothing to measure
against.

**Verify-then-crystallize again.** Before the workflow, proved both new mechanisms live:
- **Iconify** — `GET https://api.iconify.design/logos/javascript.svg` returns the real coloured JS
  brand mark; the `logos:` set = brand marks, `mdi`/`lucide`/`solar`/`tabler` = concept glyphs
  (`mdi:server` etc.); `/search?query=` resolves slugs.
- **Wikimedia Commons** — `action=query&generator=search&gsrnamespace=6&prop=imageinfo&iiprop=url|extmetadata`
  returns CC-licensed photo URLs + license metadata (proven: "data center server room" →
  BalticServers data center.jpg, CC BY-SA 3.0). **Attribution is a real constraint** the design
  must carry.

**Workflow ran but its return failed twice** (`wf_90c299e8-1d1`): first a network error, then the
final synthesizer agent didn't emit StructuredOutput (the synth schema demanded giant verbatim
prose blocks + full taxonomy + routing in one structured call — too heavy). **The 8 design+judge
agents succeeded**, so recovered their `StructuredOutput` payloads directly from the agent
transcripts (`subagents/workflows/wf_90c299e8-1d1/agent-*.jsonl`) and **synthesized by hand** —
which is the safer path anyway (parallel editors stray-delete). All four candidates scored
anti-overfit 5 / technical 5; they converged hard, so the synthesis was graft-the-consensus.

**The consensus design (applied):**
- **Threshold (3-part AND gate):** a named thing earns a picture only when it (1) *is the beat's
  subject*, (2) is *recognisable on sight* (if you'd label it, it fails), and (3) *adds meaning the
  words can't*. Tie-breaker: a diagram/stat/kinetic-type that says it clearer wins. Rationing: a
  run of logo-drops = the same inertia smell as a run of bare-text cards. Triggers are sentence
  properties, never scene index, never quota.
- **Taxonomy + routing:** `logo` → local `assets/icons/` first → Iconify `logos:` (static SVG, no
  recolour, no image-prep); `glyph` → Iconify mono sets, `currentColor`-tinted (static SVG);
  `photo` → Wikimedia (capture artist+license+URL) → web, image-prep (skip `--remove-bg` for a
  *place* to keep context); `reaction` → Pinterest → web (unchanged). Plus an explicit *none* lane
  (text/diagram/stat) as a first-class outcome.
- **Hard rules:** determinism (author-time static fetch, never a runtime `<iconify-icon>`/CDN
  `src`); license capture for Wikimedia; **box-on-failure — never delete the box** (the director's
  rule: a failed source leaves the placeholder standing).

**Edits applied (by hand, serially):**
- `.claude/agents/image-sourcer.md` — added Inputs `class`/`referent` (emotion → reaction-only);
  a "Route by class" gate + a full **Referent lane** (R0 local-first / R1 Iconify logo / R2 Iconify
  glyph / R3 Wikimedia photo + catch-all); report gains `class`/`kind`/`source`(local|iconify|
  wikimedia|pinterest|web)/`license`/`tintable`; effort budget gains a referent cap; constraints
  allow `assets/icons/` writes + Wikimedia license capture. (Header had been pre-edited to the
  two-lane framing; this closed the body contradiction the candidates flagged.)
- `reference/visual-language.md` §2 — a "Referent mark / inset" archetype-menu row + a
  "show the thing you name" subsection carrying the 3-part gate.
- `reference/assets-and-media.md` — `data-asset-class`/`data-asset-referent` in the box example +
  bullets; a class-aware `image-sourcer` dispatch; a **"Two kinds of image, and where each comes
  from"** routing table (the determinism / icons-aren't-photos / attribution rules); an explicit
  director-side box-on-failure paragraph; a referent worked case in "when imagery earns its place";
  an SVG-swap variant (inline for tintable glyphs).
- `SKILL.md` — Step D threads `data-asset-class` routing onto the existing "concrete recognisable
  thing" signal; delegation-map `image-sourcer` row names the per-class sources.
- `reference/verify-and-preview.md` — "Imagery fit" gains an **overfit inverse** check (logo on a
  non-subject noun / adjacent logo-drops) and an **asset-determinism** check (flag runtime/CDN
  image references).

**Iteration-3 test now also watches:** referent imagery appears on genuinely-named-subject beats
(a logo on "JavaScript", a real photo on "infrastructure") sourced via the right lane; text-first
and non-subject nouns stay text (the overfit inverse); and no composition references a network
image at render time (determinism).

---

## Iteration-3 graded → iteration-4 hardening (the lever)

**Grade (Opus `/workflows` run `wf_7a11fd45-ff4` + human):** the imagery push **failed — zero
images rendered** across all five beats; the human never saw an image and flagged the HN-quote
frame as "off, the iteration-2 problem persists." Mechanics **A**, visual-design **B**, imagery
**D**. Full report: `iteration-3/grading.md` (+ `iteration-3/frames/`).

**Decisive diagnostic — failure class = JUDGMENT, not detection or mechanism.** The author *saw*
the signals (its own thinking named the irony and the HN source) and consciously routed them to
typographic treatments — "the quote itself is the design, no side imagery needed." `image-sourcer`
was never dispatched; box-on-failure never reached. Root cause is structural: **Step D has two
halves — archetype-variety and imagery-as-default — and an author can fully satisfy Step D through
variety alone**, so the imagery check is silently skippable. Iteration 3 added *more* signals and
*more* routing; a louder default that can be bypassed without an auditable step gets bypassed.
Second defect: the verbatim HN quote rendered in Inter, not the reserved Excalifont — and the
verify rubric had **no type-role check** to catch it.

**The lever (don't shout signals — raise the cost of declining).** Make the imagery + type-role
decision an **auditable, quoted-back, per-chunk verdict**, mirroring Step B's chunk quote-back that
already works. Declining must **name the candidate it rejected** ("HN logo weighed, rejected
because …"), so a silent "just typographic" is no longer reachable; text-only stays first-class as
a *named* rejection, never a quota. Taught by **multi-shot worked examples** (the user's ask — the
reasoning trace is the product).

**Built via a dynamic `/workflows` run (`wf_1c5cd93f-f1f`, 25 agents):** 12 example slots, each
**drafted then adversarially vetted** (correctness · generalization/anti-overfit · the
decline-names-a-candidate discipline · format · dispatch-readiness), then synthesized. Returned as
plain text (synth on no schema — the failure mode that sank the two prior runs); edits applied by
hand.

**Edits applied:**
- NEW `reference/decision-examples.md` — two multi-shot sets, 6 each, all **video-agnostic** (CDN/
  Cloudflare, hyperscale data center, productivity app, distributed tracing, central banking, Suez
  Canal, lighthouse keeper, monetary policy, Docker, fintech wordmark, submarine cables — zero
  js-king). Set A (does this beat earn an image: logo/photo/reaction/glyph YES + two candidate-named
  `text-only`); Set B (which font carries each role: verbatim quote → human-voice font, narrator
  paraphrase → system, hand-annotation → human, code → mono, wordmark → system, caption → muted).
- `SKILL.md` Step D — the **per-chunk verdict block** requirement (imagery + type-role, quote it
  back before authoring) + the iron rule + pointer to the example bank; Step G gains a **Verdict
  check** ("type-role fidelity" added to the reviewer rubric list, plus a verdict-emitted
  checkpoint); reference-files list links `decision-examples.md`.
- `reference/verify-and-preview.md` — NEW **Type-role fidelity** rubric bullet (flag verbatim quote
  in system font, and the human-voice font on system narration) — closes the gap that let the
  Excalifont miss through.

**Deviation from plan:** dropped the "missed-verdict note on Imagery fit" — the frame reviewer
can't see the author's written verdict, so that check belongs director-side (the Step G verdict
checkpoint) not in the Sonnet frame rubric. The Imagery-fit bullet already flags bare-text signal
beats from the frame alone.

**What did NOT change** (working halves preserved): the signal list (detection works), the 3-part
gate, the archetype-variety guidance, `image-sourcer.md`. No new signals, no quota.

**Iteration-4 (next, user re-authors in a fresh session — agent + skill both reload there):** win
= the two gate-passing referents land (HN logo *sourced*, a real photo on the concrete-subject
beat) + the verbatim quote renders in Excalifont, while abstract pivots and non-subject nouns stay
text. Watch the inverse (face/logo on every noun) as the overfit failure.
