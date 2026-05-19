# transcribe-elevenlabs

Transcribe an audio file to the project's word-level `transcript.json` shape
(Scribe v2). Pure transcription — no TTS, no cut planning. Intended to be
driven by the `transcribe-and-plan-cuts` skill, but usable on its own.

## Usage

```bash
# From inside a videos/<slug>/ folder:
uv run --project ../../tools/transcribe-elevenlabs \
  transcribe-elevenlabs audio/raw.mp3 -o transcript.json

# Cost preview only (no API call):
uv run --project ../../tools/transcribe-elevenlabs \
  transcribe-elevenlabs audio/raw.mp3 --dry-run

# Skip the mono-16k-64k re-encode (upload original file):
uv run --project ../../tools/transcribe-elevenlabs \
  transcribe-elevenlabs audio/raw.mp3 --no-reencode
```

By default the input is re-encoded to mono 16 kHz 64 kbps MP3 before upload
(Scribe doesn't need anything richer; this just shrinks the request). The
original file is never modified.

## Requirements

- `ELEVENLABS_API_KEY` in `.env` at the repo root (or in the environment).
- `ffmpeg` + `ffprobe` on PATH (for duration probe and re-encode).

## Output

The written `transcript.json` matches the repo-standard Scribe v2 shape
documented in the root `CLAUDE.md`: discriminated entries on `type`
(`word` / `spacing` / `audio_event`), global timestamps, `audio_duration_secs`
at the top level. Cost is ~$0.40/hour of audio.
