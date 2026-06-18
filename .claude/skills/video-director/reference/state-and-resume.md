# State detection and resume

The whole point of authoring a few sentences at a time is that any session — a
fresh one, or yours after a `/compact` — can pick up where the last left off.
There is **no sidecar progress file**. The mounted scene hosts in `index.html`
ARE the durable state. This file is the engine for reading that state and finding
the next uncovered sentence.

## Reading index.html into a frontier

1. Parse `index.html` and collect the **scene** hosts: `<div>`s with
   `data-composition-src="compositions/..."` that sit on a scene track. For each,
   capture `{id, composition-id, src, start, duration, track-index}`. When a
   talking-head source is present, the per-chunk **MODE is not a sidecar** — it is
   re-derived from the mounted hosts (whether a graphics scene covers the chunk,
   plus the `face-layer`'s reveal/hide state at that time), so the hosts stay the
   single source of truth (`talking-head.md`).
2. **Exclude non-scenes:** the voiceover `<audio>`, the `substrate-layer`
   (track-index ~7), `sfx-layer` (~19), `music-layer`, and — when a talking-head
   source is present — the `face-layer` host (track-index 8). These span the full
   audio and would otherwise look like "everything is covered." The `face-layer`
   in particular runs the whole runtime, so leaving it in would peg the frontier
   at full duration and break resume (`talking-head.md`).
3. The **frontier** = `max(start + duration)` over the scene hosts. That's the
   global audio time the video is authored up to. A scaffold-only index (root +
   voiceover + maybe substrate, zero scene hosts) has frontier = 0.

## Mapping the frontier back to a script sentence

The frontier is a timestamp; the resume point is a sentence. Bridge them through
the transcript (never `Read` the transcript whole — use the filter from
`reference/transcript-timing.md`):

1. Find the first transcript word at or after the frontier time.
2. Locate that word's text in `script.md`. Everything from there on is uncovered.
3. The next 1-2 sentences after that point are your next chunk.

Quote the resume sentence back to the user so they can confirm you picked up in
the right place.

## Batching across sessions

A session is just "run the loop until you choose to stop." Stop on a **block
boundary** — never mid-block — when context is getting large or you've authored a
comfortable batch. Because Step A re-derives everything from `index.html`, there
is nothing to checkpoint: the next session re-reads the mounted hosts and
continues.

Optionally, drop a one-line hint at the frontier so the next session's first read
is trivial:

```html
<!-- director: covered through 150.68s / "...and he chose JavaScript." -->
```

Treat the mounted hosts as the source of truth and the comment as a convenience —
if they ever disagree (e.g. the comment is stale), believe the hosts.

## Resume edge cases

- **Mid-video gap.** If two scene hosts don't tile (host N ends before host N+1
  starts, with uncovered transcript words in between), that gap is unfinished
  work, not the frontier. Prefer filling an interior gap before extending past
  the frontier — a hole mid-timeline means a stretch of narration with no
  visuals. Detect it by sorting hosts by `start` and checking each
  `start[i+1] ≤ start[i] + duration[i]` (allowing the 0.5s overlap).
- **Timing gap at the seam.** A block whose `data-duration` doesn't reach the
  next chunk's first word leaves a flash of empty frame. When you wire host N,
  set its duration to run into chunk N+1's first word (the overlap covers the
  transition); when you author N+1, confirm it starts 0.5s before its first word.
- **Talking-head gap.** When a talking-head source is present, an uncovered
  frontier stretch is not a blank flash — the continuous `face-layer` shows the
  FACE through it. It is still **owed mode authoring** (graphics/PIP on top, or a
  deliberate FACE beat), so treat it as unfinished work, not as covered
  (`talking-head.md`).
- **Script edited after authoring.** If `script.md` no longer matches the
  transcript (the user rewrote a line after you'd already animated it), the
  transcript timings won't line up with the new text. **Flag this to the user —
  do not silently re-author.** The transcript is the timing truth; a script edit
  that postdates the recording needs a re-record/re-transcribe, or an explicit
  decision to animate against the old timing. In **talking-head mode** the
  transcript is the take's *own* audio, so a post-record script edit also desyncs
  the revealed face from the spoken words — a re-record/re-transcribe is the only
  fix (`talking-head.md`).
- **Reordered scenes.** If the user wants scenes reordered, the host `data-start`
  values (tied to transcript time) are the constraint — you can't freely reorder
  without breaking sync. Reordering means re-anchoring, which is a deliberate
  re-author, not a wiring tweak.
