# Transcript pause finder

Layer crossfades hide best inside natural narration pauses. The transcript at
`transcript.json` is the source of truth — pull every word's `start`/`end`
and look at the gaps between consecutive words.

Run these snippets via `python3 -c '...'` from inside the video folder. Do
not `Read` `transcript.json` directly — it's ~1500+ word entries and floods
context.

## 1. Find pauses ≥ 0.3s inside a target window

Use this to locate crossfade-eligible silence near a planned boundary.
Adjust `lo` and `hi` (seconds, global to the audio) to your window:

```bash
python3 -c "
import json
t = json.load(open('transcript.json'))
words = [w for w in t['words'] if w['type'] == 'word']
LO, HI = 95.0, 110.0  # widen if you don't find a 0.6s+ gap
prev = None
gaps = []
for w in words:
    if prev is not None and prev['end'] <= HI and w['start'] >= LO:
        gap = w['start'] - prev['end']
        if gap >= 0.3:
            midpoint = (prev['end'] + w['start']) / 2
            gaps.append((gap, midpoint, prev['text'], w['text']))
    prev = w
for g, mp, p, n in sorted(gaps, reverse=True):
    print(f'gap={g:.2f}s  midpoint={mp:.2f}s  {p!r} | {n!r}')
"
```

Prefer **sentence-boundary gaps** (the preceding word ends with `.`, `?`,
`!`) over mid-sentence gaps of the same length — the listener already
expects silence between sentences, so the crossfade reads as breath.

## 2. Map a narrative beat to a timestamp window

The brainstorm gives you intent like "the boundary lives just before the
synthesis beat" or "right after the YOLO defeat reveal." Translate that to
a numeric window by grepping for an anchor phrase:

```bash
python3 -c "
import json
t = json.load(open('transcript.json'))
words = [w for w in t['words'] if w['type'] == 'word']
# Hunt the first word of the target sentence. Use whatever phrase the
# script actually contains — strip trailing punctuation for the match.
ANCHORS = ('Every', 'In', \"Let's\")  # adjust to your script
for i, w in enumerate(words):
    if w['text'].rstrip('.,?!') in ANCHORS:
        ctx = ' '.join(x['text'] for x in words[max(0,i-3):i+4])
        print(f'{w[\"start\"]:6.2f}s  {w[\"text\"]:14s}  ...{ctx}...')
"
```

Once you have the anchor timestamp, set the window in snippet 1 to roughly
`[anchor - 6, anchor + 2]` to catch the preceding pause.

## 3. Check source-length constraints

With an N-layer bed and 2-second outer crossfades, each layer must span at
least `(boundary_out - boundary_in + 2)` seconds. For the inner layers,
both `boundary_in` and `boundary_out` are crossfade midpoints. The first
layer starts at 0; the last layer ends at the VO duration.

For layer K with input length `L[k]` and crossfade midpoints `T[k-1]` (in)
and `T[k]` (out):

```
L[k] >= T[k] - T[k-1] + 2     for inner layers
L[0] >= T[0] + 1              for the first layer  (1s for half a crossfade)
L[N-1] >= VO_duration - T[N-2] + 1   for the last layer
```

Quick validator:

```bash
python3 -c "
VO = 387.6                    # total bed duration in seconds
T  = [99.59, 273.75]          # crossfade midpoints (N-1 of them)
L  = [101.0, 155.3, 121.8]    # input source lengths per layer
N  = len(L)
for k in range(N):
    if k == 0:
        need = T[0] + 1
    elif k == N - 1:
        need = VO - T[-1] + 1
    else:
        need = T[k] - T[k-1] + 2
    ok = '✓' if L[k] >= need else '✗ short by %.2fs' % (need - L[k])
    print(f'layer {k}: have {L[k]:.2f}s, need {need:.2f}s  {ok}')
"
```

If a layer fails: either shift the failing boundary to a different pause
that satisfies the math, **or** bridge the layer by concatenating two
files from its own folder with a 2s inner crossfade (effective length
becomes `L_a + L_b - 2`). Bridging stays musically natural when the two
sources are variants of the same composition (main + short, main + loop,
stem + stem).

## 4. Output the boundary plan

Always surface the plan to the human as a small table before baking. At
minimum, show: layer index, source filename(s), in-midpoint, out-midpoint,
and the actual pause text the crossfade hides in (e.g. `0.70s "in. | The"`).
The user should be able to scan the table and verify that each cut sits
where they expect narratively.
