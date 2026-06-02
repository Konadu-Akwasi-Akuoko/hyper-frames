# cut-snap

Refines `audio-cut-decider` cut boundaries onto the **true silence plateau
edges** of the source audio, so splices keep the previous word's decay and the
next word's lead-in instead of clipping onsets or leaving dead air.

The agent decides *which* word-span to cut (judgment); cut-snap places the
*exact* boundaries (DSP). It is deterministic — identical input yields identical
output, as required by the render-safe pipeline.

## How it works

For each cut, per boundary:

1. Find the removed word-span and its flanking **kept** words from the transcript.
2. Decode the source audio to mono PCM (ffmpeg) and compute a short-time RMS
   envelope across the inter-word gap.
3. Calibrate an **adaptive** threshold `floor + --floor-db` relative to the
   quietest frame in the gap (room tone), then find the plateau edge:
   - `cut.start` = where the previous kept word decays into the floor.
   - `cut.end` = just before the next kept word's energy rises.
4. Snap to the nearest zero-crossing (de-click).
5. **Fallback:** if no detectable silence exists (words run together), use the
   capped-pad rule `edge ± min(0.30, gap/2)`.

## Usage

```bash
uv run --project tools/cut-snap cut-snap \
  <video-dir>/transcript.json \
  <video-dir>/cuts.json \
  <video-dir>/audio/raw.mp3 \
  -o <video-dir>/cuts.json
```

Prints a before → after table. Tunables: `--floor-db` (default 8),
`--frame-ms`, `--hop-ms`, `--sustain-ms`, `--zero-cross-ms`, `--sample-rate`.

Requires `ffmpeg` on PATH.
