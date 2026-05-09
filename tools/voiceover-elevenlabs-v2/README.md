# voiceover-elevenlabs-v2

Generate voiceover audio (ElevenLabs Multilingual v2) and a word-level
transcript (Scribe v2 on the rendered audio) from an annotated script,
in a single command. The **project default** for hyper-frames YouTube
videos — long-form stable per the official models page, plain-prose
match for the project's house style.

The companion `voiceover-elevenlabs-v3` tool stays available for content
that genuinely benefits from per-beat audio tags. See the design doc at
`docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-v2-and-rename-design.md`.

## Install

```bash
uv sync
```

Set `ELEVENLABS_API_KEY` in `.env` at the repo root.

## Usage

```bash
# Inside a video folder, with voiceover.txt at the folder root:
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/voiceover-elevenlabs-v2 \
  voiceover-elevenlabs-v2 voiceover.txt
```

Writes `audio/voiceover.mp3` and `transcript.json` next to the input.

### Flags

| Flag | Default | Notes |
| --- | --- | --- |
| `-o`, `--output-audio PATH` | `audio/voiceover.mp3` | MP3 destination. |
| `--output-transcript PATH` | `transcript.json` | Transcript destination (project schema). |
| `--voice-id ID` | `IRHApOXLvnW57QJPQH2P` | ElevenLabs voice ID (distinct from v3's default). |
| `--model ID` | `eleven_multilingual_v2` | Locked model — flag exists for symmetry. |
| `--stability FLOAT` | `0.4` | Long-form sweet spot per docs (0.35–0.4). |
| `--similarity-boost FLOAT` | `0.75` | Same as v3 default. |
| `--style FLOAT` | `0.35` | v2-only param; docs recommend 0.3–0.5. |
| `--use-speaker-boost / --no-use-speaker-boost` | `True` | v2-only param. |
| `--language-code STR` | `en` | Locks generation language; mitigates v2's tendency to switch accent on individual words. |
| `--no-transcript` | off | Skip Scribe call; produce audio only. |
| `--dry-run` | off | Print char count + cost estimate; no API call. |

### Input format

`voiceover.txt` is plain UTF-8 text — typically the output from the
`voiceover-elevenlabs-v2` skill, with ALL-CAPS on anchor terms and
optional SSML `<break time="Xs"/>` tags at structural pauses. **No audio
tags** — v2 doesn't support them. The tool sends the file contents to
v2 verbatim.

### Char limit

v2's per-request limit is **10,000 characters** (~10 minutes audio per
the official models page). The tool errors loudly past this; chunked +
stitched generation is not yet implemented. For 10+ min scripts, split
`voiceover.txt` into parts and run twice.

## Library use

```python
from pathlib import Path
from voiceover_elevenlabs_v2 import generate

generate(
    text_path=Path("voiceover.txt"),
    audio_path=Path("audio/voiceover.mp3"),
    transcript_path=Path("transcript.json"),
    voice_id="IRHApOXLvnW57QJPQH2P",
    api_key="sk_...",
)
```

## Testing

```bash
uv run pytest tests/ -v
```

All wrapper code is unit-tested with mocked SDK clients. The Scribe →
project-schema mapping has full coverage including the defensive cases.

## Origin

Spec: `docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-v2-and-rename-design.md`.
