# voiceover-elevenlabs-v3

Generate voiceover audio (ElevenLabs v3) and a word-level transcript
(ElevenLabs Scribe v2 on the rendered audio) from an annotated script,
in a single command. Built for the hyper-frames video pipeline; produces
the canonical `audio/voiceover.mp3` + `transcript.json` shape the rest
of the project consumes.

> **Renamed from `voiceover-elevenlabs` on 2026-05-09** so the engine
> version is explicit. The companion `voiceover-elevenlabs-v2` tool is
> the project default for YouTube videos; this v3 tool stays available
> for content that genuinely benefits from per-beat audio tags.
> See `docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-v2-and-rename-design.md`.

The transcript is generated from Scribe v2, **not** v3's native
character alignment. See the original spec at
`docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-design.md` for
why (timing-truth invariant, v3-derived alignment unverified).

## Install

The project uses `uv`. From this directory:

```bash
uv sync
```

Set `ELEVENLABS_API_KEY` in `.env` at the repo root. The same key serves
both v3 and Scribe v2.

## Usage

```bash
# Inside a video folder, with voiceover.txt at the folder root:
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/voiceover-elevenlabs-v3 \
  voiceover-elevenlabs-v3 voiceover.txt
```

Writes `audio/voiceover.mp3` and `transcript.json` next to the input.

### Flags

| Flag | Default | Notes |
| --- | --- | --- |
| `-o`, `--output-audio PATH` | `audio/voiceover.mp3` | MP3 destination. |
| `--output-transcript PATH` | `transcript.json` | Transcript destination (project schema). |
| `--voice-id ID` | `UgBBYS2sOqTuMpoF3BR0` | ElevenLabs voice ID. |
| `--model ID` | `eleven_v3` | TTS model. |
| `--stability FLOAT` | `0.5` (Natural) | v3 stability slider. |
| `--similarity-boost FLOAT` | `0.75` | v3 similarity boost. |
| `--no-transcript` | off | Skip Scribe call; produce audio only. |
| `--dry-run` | off | Print char count + cost estimate; no API call. |

### Input format

`voiceover.txt` is plain UTF-8 text — typically the LLM-annotated output
from the `voiceover-elevenlabs-v3` skill, with v3 audio tags (`[sighs]`),
ellipses (`…`), and ALL-CAPS emphasis applied. The tool sends the file
contents to v3 verbatim.

## Library use

```python
from pathlib import Path
from voiceover_elevenlabs_v3 import generate

generate(
    text_path=Path("voiceover.txt"),
    audio_path=Path("audio/voiceover.mp3"),
    transcript_path=Path("transcript.json"),
    voice_id="UgBBYS2sOqTuMpoF3BR0",
    api_key="sk_...",
)
```

## Testing

```bash
uv run pytest tests/ -v
```

All wrapper code is unit-tested with mocked SDK clients. The Scribe →
project-schema mapping has full coverage including the defensive cases
(missing `audio_duration_secs`, undefined per-word timestamps).

## Origin

Spec: `docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-design.md`.
Replaces the `hyperframes-media tts` (Kokoro) path for this project's
videos. The Kokoro skill stays untouched and parallel for any non-v3
use case.
