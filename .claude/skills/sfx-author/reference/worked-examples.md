# Worked examples — `videos/why-text-is-hard-2026-05-07/`

These examples teach the editorial reasoning by demonstration. Each shows: the
moment, the cue, the anchor, and *why* — including why nearby elements were
*not* scored.

---

## Example 1 — "mathematical NIGHTMARE" (Scene 1)

**Context.** The hook scene. A typewriter types `~/draft.txt`, then the line
"A MATHEMATICAL NIGHTMARE." resolves with NIGHTMARE in amber.

**Annotation.**

```html
<div id="s1-nightmare"
     class="nightmare-stack"
     data-sfx-anchor="nightmare"
     data-sfx-on-anchor="ui-tick">
  <div class="eyebrow ns-eyebrow">UNDER THE HOOD</div>
  <div class="ns-line">A <span class="ns-amber">MATHEMATICAL</span></div>
  <div class="ns-line ns-amber">NIGHTMARE.</div>
  <div class="ns-foot">/// translating one keystroke into pixels</div>
</div>
```

**Reasoning.** "NIGHTMARE" is where the line lands. The element entrance peaks
emotionally there. A `ui-tick` at `-50ms` lead lands the click on the syllable.

**What was *not* scored:**

- `#s1-typed` (typewriter) — texture. Per-character clicks would crowd the
  word that's actually the moment.
- `.eyebrow.ns-eyebrow` ("UNDER THE HOOD") — scene metadata, ambient. No tick.
- `.ns-foot` (the slash-comment footer) — atmosphere, not punctuation.

---

## Example 2 — Scene 2→3 boundary at "control point"

**Context.** Scene 2 closes on the Bézier glyph with control-point markers
appearing. Scene 3 begins describing control points in detail. The first
spoken word of scene 3 is "control."

**Annotation.**

```html
<div id="s3" class="scene"
     data-sfx-anchor="control"
     data-sfx-on-anchor="whoosh">
  ...
</div>
```

**Reasoning.** A scene-boundary `whoosh` keyed to the first emphatic word of
the next scene. Lead `-150ms` (the default) so the whoosh peaks on "con-".

**What was *not* scored:**

- Each individual control-point marker in scene 2 — they're a swarm reveal,
  not threshold crosses. Clicking each one would turn the scene into a UI
  bleep festival and crowd the upcoming "Bézier" tick.
- The exact transition frame between scenes — the *anchor* is the spoken word,
  not a visual cut. `tools/sfx-plan` handles peak alignment from there.

---

## Example 3 — "Bézier" tick (Scene 2 mid)

**Context.** Mid-scene 2, the glyph "A" is broken down into Bézier curves;
control points pop on. The narration says "Bézier" as the first marker appears.

**Annotation.**

```html
<svg id="s2-overlay" class="glyph-overlay"
     data-sfx-anchor="Bézier"
     data-sfx-on-anchor="ui-tick">
  ...
</svg>
```

**Reasoning.** "Bézier" is the conceptual landing word — it's the term the
viewer is supposed to register. A single `ui-tick` punctuates the conceptual
reveal. The 12 control-point markers that follow are scored *only* by the
silence-after-the-tick (they ride the visual rhythm, no audio).

**What was *not* scored:**

- The 12 control-point markers individually. Bezier's tick is the punctuation;
  the markers are texture.

---

## Anti-example — what NOT to do

If a video has a list of three competing definitions appearing in sequence, the
tempting move is one `ui-tick` per item:

```
✗ tick on item 1
✗ tick on item 2
✗ tick on item 3
```

Don't. Honor the 2s cooldown — if the three items appear within ~3s, you get
one tick on the *list heading* and let the three items ride on visual rhythm.
Three ticks in 3s smear into perceptual mud.

---

## How to use these examples

When you're producing a proposal for a new video, **reference these examples
explicitly in your reasoning lines**. For example:

> ✓ 00:08.4 anchor="nightmare" ui-tick on #s1-nightmare (Example 1 pattern —
>          punctuates the landing word; skips the typewriter texture)

That referent makes your editorial logic legible to the user and links back to
the canonical bar.
