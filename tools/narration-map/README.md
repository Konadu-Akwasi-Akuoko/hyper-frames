# narration-map

Reads a HyperFrames word-level transcript (the ElevenLabs Scribe shape produced
upstream of this repo) and emits a **narration map** — the timing reference an
agent or human authoring a composition needs before keying any animation:

- **Anchor words** — exact `start` for each phrase you supply (case- and
  punctuation-insensitive; reports every occurrence, not just the first)
- **Pause windows** — every gap between consecutive words above a threshold
- **Scene boundaries** — pauses that follow a sentence-ending word (`.`/`!`/`?`),
  the strongest candidates for cuts
- **Emphatic words** — the top-N longest-duration words (often where the voice
  lingers on a key term)

The first video in this repo, `videos/why-text-is-hard-2026-05-07/`, was built
with a hand-rolled Python one-off that did only the first of these. This tool
generalizes that work so the next video starts from a structured map instead
of from `python3 -c '...'`.

## Install

The project uses `uv`. From this directory:

```bash
uv sync
```

## Usage

```bash
# Inside a video folder, with transcript.json + anchors.txt next to each other:
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/narration-map \
  narration-map transcript.json --anchors anchors.txt
```

By default, writes `narration-map.json` next to the input transcript. Use
`--stdout` to print to stdout instead, or `-o PATH` for a custom location.

### Anchor file format

One phrase per line. Blank lines and `#` comments are ignored.

```
# Hook
You open
mathematical nightmare

# Section: vector outlines
Bézier
control point
```

### Tunables

| Flag | Default | Notes |
| --- | --- | --- |
| `--pause-threshold SECS` | `0.4` | Gap size above which a between-word silence becomes a "pause". |
| `--scene-pause-threshold SECS` | `0.6` | Gap size after `.!?` to count as a scene boundary. Should be ≥ pause threshold. |
| `--emphatic-top-n N` | `15` | How many longest-duration words to surface. |

## Output shape

```json
{
  "source": "/abs/path/to/transcript.json",
  "audio_duration_secs": 120.001,
  "language_code": "eng",
  "word_count": 353,
  "config": { "pause_threshold_secs": 0.4, ... },
  "anchors": [
    {
      "phrase": "GPU",
      "matches": [
        { "word_index": 41, "start": 16.74, "end": 17.05, "matched_text": "GPU" }
      ]
    }
  ],
  "pauses": [
    {
      "after_word_index": 32,
      "after_word_text": "handles.",
      "gap_secs": 0.81,
      "start_secs": 26.51,
      "end_secs": 27.32
    }
  ],
  "scene_boundaries": [ /* same shape as pauses */ ],
  "emphatic_words": [
    {
      "word_index": 198,
      "text": "rasterization.",
      "start": 85.82,
      "end": 87.24,
      "duration_secs": 1.42
    }
  ]
}
```

## Library use

The CLI is a thin wrapper around `narration_map.core`:

```python
from pathlib import Path
from narration_map import build_narration_map

m = build_narration_map(
    Path("videos/why-text-is-hard-2026-05-07/transcript.json"),
    phrases=["You open", "mathematical nightmare", "GPU"],
    pause_threshold_secs=0.4,
)
print(m.anchors[0].matches[0].start)
```

## Origin

Distilled from the inaugural video session
(`videos/why-text-is-hard-2026-05-07/`) and the post-production retrospective:

> "Manual timing extraction. I wrote a Python one-off to find word timestamps.
> That should be a tool that ingests the transcript and emits a 'narration map'
> — anchor words, natural pause points (gaps > 400ms), suggested scene
> boundaries."
