# Cue vocabulary — when each cue earns a hit

This page is intent-by-intent. Use it to pick a cue *after* you've identified
a moment that deserves one — never to scan for elements that "should have" one.

---

## `ui-tick` — discrete arrival

**Timing mode:** usually `at-scene-ms` (the tick scores the visual landing).
Use `anchor` only when the tick punctuates a spoken label, not a visual entry.

**Character:** sharp, bright, ≤ 0.5s, fast attack. The sound of a *thing
landing*.

**Earns a tick:**
- A headline or label that fades in from opacity 0 on a spoken word.
- A diagram element that snaps into final position (a connector arrow lands,
  a vertex appears, a label resolves).
- A list item revealed in step with the line that names it.

**Doesn't earn a tick:**
- A typewriter that runs per-character (the line is the moment, not each glyph).
- An element that drifts in continuously (drift is texture; tick is event).
- An element whose entrance is masked by a louder cue (e.g. mid-whoosh).

**Failure modes:**
- Too many ticks in a row → density collapse. Honor the 2s cooldown ruthlessly.
- Tick on every reveal in a high-density scene → use one tick on the *headline*
  reveal and let the other reveals ride.

---

## `whoosh` — spatial motion / threshold cross

**Timing mode:** almost always `at-scene-ms` — a whoosh scores motion, and
motion is a visual event. Anchor-mode whooshes are rare (only when the whoosh
is tied to the *word* of a transition, not the visual cut).

**Character:** 0.4–1.5s, swelling attack ≥ 0.1s, peaks toward the middle.
The sound of *something passing through*.

**Earns a whoosh:**
- Scene-boundary cuts at narration-map's scene-boundary candidates (pauses
  >600ms after `.!?`).
- A large element traversing the frame.
- A camera-like move (zoom out, push in) implemented in the composition.

**Doesn't earn a whoosh:**
- Small element entrances — use `ui-tick` or `pop` instead.
- Opening scene (the start of a video already has the user's full attention; a
  whoosh out of silence feels jarring).
- Scenes that end on a *deliberate* silence (the whoosh would steal the beat).

**Failure modes:**
- Whoosh on every scene boundary → wears thin by scene 4. Reserve for boundaries
  with a real visual cross; let some boundaries fall silent.

---

## `pop` — playful arrival

**Timing mode:** usually `at-scene-ms` (the pop scores the rhythmic arrival of
a visual). Anchor-mode is fine when the pop genuinely lands on a spoken word.

**Character:** ≤ 0.3s, warm-to-bright spectrum, soft attack. Lighter than tick,
less authoritative.

**Earns a pop:**
- Rhythmic reveals where ticks would feel too sharp (icons appearing on a beat).
- Playful or whimsical moments — explainer/essay videos with a lighter tone.
- Reveals inside an already-scored scene where adding another tick would crowd.

**Doesn't earn a pop:**
- Serious or technical moments — feels too cute. Use tick.
- Anything that needs presence — a pop won't carry weight; use tick or boom.

---

## `boom` — weight / finality

**Timing mode:** follows the moment — `anchor` if the boom is the *word*
landing, `at-scene-ms` if it's the *visual reveal* of the thing the word
describes.

**Character:** sub-bass-dominated, peak near the start (≤ 0.2s), 0.3–2s tail.
The sound of *something landing with weight*.

**Earns a boom:**
- The line that the whole video is about, when it lands.
- A reveal of a huge number or scale (the dollar amount, the year, the body count).
- The *final* word of a key sentence, when paired with a major visual reveal.

**Doesn't earn a boom:**
- More than once per 30s. Booms wear out instantly when overused.
- The wrong word. A boom on "is" or "a" is comedic; a boom on the noun lands.
- On a beat that's already heavy from music or ambience (Phase B/C concern —
  in Phase A there's no music, so this is less of a worry).

**Failure modes:**
- Mistaking a number for a "boom moment." Not every number is a hit. "The page
  is 800 pixels wide" doesn't need a boom; "two billion lines of code" might.

---

## `riser` — build-to-payoff

**Timing mode:** `at-scene-ms` is the safe default — risers are timed to end
on a visual payoff, and visual timing is the source of truth for that math.

**Character:** ≥ 1.5s, slow attack, ends on the payoff. The sound of *tension
climbing toward release*.

**Earns a riser:**
- A 1.5–3s build before a major reveal.
- A scene's final tension-into-revelation movement.

**Doesn't earn a riser:**
- More than once per scene. Two risers per scene cheapens both.
- Adjacent scenes both ending in risers. The pattern reads as filler.

**Failure modes:**
- Riser ending in silence (no payoff cue) → feels unfinished. Pair with the
  reveal's own cue (often a `boom` or `whoosh`).

---

## Silence — the unused cue

The absence of sound is itself a tool. Use it when:

- The line is so emphatic that any sound would dilute it.
- The moment immediately precedes a big payoff (deliberate negative space).
- The texture is the texture (typewriter, ambient drift, background motion).

If you're tempted to add a cue but can't say *what the moment is doing*, leave
it silent.
