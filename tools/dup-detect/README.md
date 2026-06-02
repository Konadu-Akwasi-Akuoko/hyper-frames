# dup-detect

Deterministically find **duplicate takes** in a Scribe v2 transcript and emit
them as flagged candidate cuts. Transcript-only — no model, no audio, zero
run-to-run variance.

## Why this exists

The `audio-cut-decider` agent does the editorial judgment that needs language
understanding (fillers, false starts, varying/escalating rhetoric). But it was
unreliable at one specific thing: spotting a line that was spoken, then spoken
again near-verbatim a moment later (a re-take). Across repeated runs it would
silently classify the *same* repeat as "rhetorical doubling, keep both" on some
runs and "re-take, cut" on others — a recall coin-flip.

Detecting an identical repeat is pure mechanics, not judgment, so it belongs in
code. This mirrors `cut-snap`, which took boundary placement out of the agent
for the same reason.

> Note on the split: the agent's *detection* of repeats is actually 100%
> reliable (it always notices them). What varies is the *classification*
> (rhetorical vs re-take) and the *which-take-to-keep* call. dup-detect removes
> both unstable decisions by using a hard rule (textually identical => re-take)
> and a measurable signal (delivery tightness) instead of a judgment call.

## What it does

1. **Detect.** Normalize each word (lowercase, strip punctuation) and find
   non-overlapping identical word-runs (>= `--min-words`, default 3) whose two
   occurrences begin within `--window` seconds (default 30). Identical text is
   the first discriminator: a genuine re-take repeats verbatim, while rhetorical
   repetition almost always *varies or escalates* ("not twice, not ten times, a
   million") and so won't match.
2. **Re-take test.** An identical match is only treated as a re-take if at least
   one of these holds, else it is a coincidental phrase overlap OR deliberate
   rhetorical repetition (anadiplosis / anaphora) and is left alone:
   - **take A is truncated** — it contains a word fragment ("con...",
     "sourced--", "re-"), the classic speech-repair interruption marker. A
     truncated first attempt is a near-certain re-take; rhetorical repeats are
     never truncated. (Most reliable signal.)
   - the verbatim match is **long** (`--long-match`, default 5 words) — neither a
     coincidence nor a rhetorical reuse usually spans that many identical words;
   - a **restart pause** precedes the second occurrence (`--pause-restart`,
     default 0.7s) — a real redo restarts after a beat, whereas a deliberate
     cadence pause is shorter (~0.5s).

   Without this test two failure modes slip through: a short function-word run
   matching across unrelated sentences ("the browser. And" vs "...the browser
   and..."), and deliberate repetition ("...the most generated. The most
   generated becomes..."). Tuned so every human-confirmed re-take in a
   full-length transcript (16 candidate repeats) passes and every coincidental /
   rhetorical match is rejected.
3. **Pick the keeper.** Score each take by its internal *slack* — the total gap
   between its words. The flubbed take carries extra hesitation, so the tighter
   take is kept and the looser one cut. On a tie, keep the later take (speakers
   re-record because the first attempt was off).
4. **Bracket the cut.** Emit a word-edge span that also absorbs the inter-take
   pause, so the splice lands on the kept take's onset. Boundary precision
   (snapping onto true silence, breath padding) is left to `cut-snap`.

Every emitted cut is **flagged** `flag: duplicate_or_rhetorical: "<phrase>"` so
the human can verify (or flip the kept take) in `tools/audio-editor`.

## Usage

Standalone — see what it finds:

```bash
uv run --project tools/dup-detect \
  dup-detect <video-dir>/transcript.json
```

Merge into the agent's cuts (adds only duplicates the agent missed; preserves
existing cuts; re-sorts and re-numbers ids):

```bash
uv run --project tools/dup-detect \
  dup-detect <video-dir>/transcript.json \
  --cuts <video-dir>/cuts.json \
  -o <video-dir>/cuts.json
```

Then refine boundaries:

```bash
uv run --project tools/cut-snap \
  cut-snap <video-dir>/transcript.json <video-dir>/cuts.json <video-dir>/audio/raw.mp3 \
  -o <video-dir>/cuts.json
```

## Options

| flag | default | meaning |
| --- | --- | --- |
| `--window` | `30.0` | max seconds between the two takes' onsets |
| `--min-words` | `3` | minimum identical-word run length (shorter repeats are stutters — the agent's job) |
| `--pause-restart` | `0.7` | re-take test: silence (s) before the 2nd take marking a real redo |
| `--long-match` | `5` | re-take test: identical-word run length too long to be coincidental |
| `--cuts` | — | existing `cuts.json` to merge into |
| `-o` / `--out` | — | output path (omit to print the table only) |

## Limitations

- Catches only **textually-identical** repeats. Non-verbatim re-takes (different
  words across the two attempts) stay the agent's job.
- The re-take test is tuned on one full-length transcript (16 candidate repeats).
  The truncation signal depends on the transcriber marking word fragments (Scribe
  v2 does, reliably). The pause threshold is the one hand-set knob (`--pause-restart`).
- Every emitted cut is flagged for human verification — the tool favours recall
  (catching missed re-takes) and leaves final precision to the editor pass.

## Pipeline position

```
audio-cut-decider (agent)  ->  dup-detect (add missed re-takes)  ->  cut-snap (refine edges)  ->  editor
        judgment                     mechanics                          DSP                       human
```
