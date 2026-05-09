# voiceover-elevenlabs Implementation Plan

> **Note (2026-05-09):** The tool and skill described in this plan were renamed to `voiceover-elevenlabs-v3`. See [`../specs/2026-05-09-voiceover-elevenlabs-v2-and-rename-design.md`](../specs/2026-05-09-voiceover-elevenlabs-v2-and-rename-design.md) for the rename + the new v2 default.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `voiceover-elevenlabs` tool + skill that turns an approved `script.md` into both `audio/voiceover.mp3` (via ElevenLabs v3 TTS) and `transcript.json` (via ElevenLabs Scribe v2 on the rendered audio) in one invocation, with an LLM-driven beat-aware annotation step behind a hard checkpoint before any API calls.

**Architecture:** Two pieces — a uv-based Python tool at `tools/voiceover-elevenlabs/` (deterministic, mirrors `tools/narration-map/`) and a skill at `.claude/skills/voiceover-elevenlabs/` (LLM-driven, drives the tool). The tool calls v3 TTS for audio, then Scribe v2 on that audio for the transcript — preserving the project's "transcript-as-timing-truth" invariant. v3-derived alignment is explicitly deferred.

**Tech Stack:** Python 3.12, uv, `elevenlabs` SDK, `python-dotenv`, `pytest` + `pytest-mock` for tests.

**Spec:** `docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-design.md`

---

## Task 1: Scaffold tool package

**Files:**
- Create: `tools/voiceover-elevenlabs/pyproject.toml`
- Create: `tools/voiceover-elevenlabs/.python-version`
- Create: `tools/voiceover-elevenlabs/.gitignore`
- Create: `tools/voiceover-elevenlabs/src/voiceover_elevenlabs/__init__.py`

- [ ] **Step 1: Create the package directory structure**

```bash
mkdir -p tools/voiceover-elevenlabs/src/voiceover_elevenlabs
mkdir -p tools/voiceover-elevenlabs/tests
```

- [ ] **Step 2: Write `tools/voiceover-elevenlabs/pyproject.toml`**

Mirrors `tools/narration-map/pyproject.toml`'s shape, with the dependencies this tool needs.

```toml
[project]
name = "voiceover-elevenlabs"
version = "0.1.0"
description = "Generate voiceover audio (ElevenLabs v3) and word-level transcript (Scribe v2) from an annotated script."
readme = "README.md"
authors = [
    { name = "Akwasi Konadu Akuoko", email = "akwasikonadueverlasting@gmail.com" }
]
requires-python = ">=3.12"
dependencies = [
    "elevenlabs>=1.0.0",
    "python-dotenv>=1.0.0",
]

[project.scripts]
voiceover-elevenlabs = "voiceover_elevenlabs.cli:main"

[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "pytest-mock>=3.12.0",
]

[build-system]
requires = ["uv_build>=0.11.10,<0.12.0"]
build-backend = "uv_build"

[tool.pyright]
venvPath = "."
venv = ".venv"
extraPaths = ["src"]
```

- [ ] **Step 3: Write `tools/voiceover-elevenlabs/.python-version`**

```
3.12
```

- [ ] **Step 4: Write `tools/voiceover-elevenlabs/.gitignore`**

```
.venv/
__pycache__/
*.pyc
*.egg-info/
.pytest_cache/
```

- [ ] **Step 5: Write `tools/voiceover-elevenlabs/src/voiceover_elevenlabs/__init__.py`**

Empty package init. Public exports get added in later tasks as modules land.

```python
"""ElevenLabs v3 TTS + Scribe v2 transcript pipeline for hyper-frames videos."""
```

- [ ] **Step 6: Sync the venv**

```bash
cd tools/voiceover-elevenlabs && uv sync
```

Expected: `uv sync` succeeds, creates `.venv/`, `uv.lock`. No errors. The `elevenlabs` package downloads (it's the only non-stdlib runtime dep besides `python-dotenv`).

- [ ] **Step 7: Verify the package is installable**

```bash
cd tools/voiceover-elevenlabs && uv run python -c "import voiceover_elevenlabs; print('ok')"
```

Expected: prints `ok`.

- [ ] **Step 8: Commit**

```bash
git add tools/voiceover-elevenlabs/
git commit -m "feat(voiceover-elevenlabs): scaffold tool package"
```

---

## Task 2: Verify SDK shape (no code changes)

This task resolves the four open questions in spec §13 before locking method names in subsequent tasks. All findings get recorded inline as comments in the modules they pertain to.

**Files:**
- No file changes. Output is knowledge that informs Tasks 3–7.

- [ ] **Step 1: Inspect the `elevenlabs` SDK's TTS surface**

```bash
cd tools/voiceover-elevenlabs && uv run python -c "
from elevenlabs.client import ElevenLabs
client = ElevenLabs(api_key='fake')
print('text_to_speech methods:', [m for m in dir(client.text_to_speech) if not m.startswith('_')])
print('speech_to_text methods:', [m for m in dir(client.speech_to_text) if not m.startswith('_')])
"
```

Expected output: a list of methods. Look for the TTS plain-convert method (working assumption: `convert`) and the Scribe convert method (working assumption: `convert`). Record exact method names.

- [ ] **Step 2: Inspect the `convert` method signatures**

```bash
cd tools/voiceover-elevenlabs && uv run python -c "
import inspect
from elevenlabs.client import ElevenLabs
client = ElevenLabs(api_key='fake')
print('TTS convert sig:', inspect.signature(client.text_to_speech.convert))
print('STT convert sig:', inspect.signature(client.speech_to_text.convert))
"
```

Record the exact parameter names. Specifically verify:
- TTS: `voice_id`, `text`, `model_id`, `voice_settings`, `output_format`.
- STT: `model_id`, `file`, `timestamps_granularity`, `diarize`, `tag_audio_events`.

If parameter names differ from these working assumptions, **update Tasks 5 and 6's code blocks accordingly before implementing them.**

- [ ] **Step 3: Inspect the `VoiceSettings` shape**

```bash
cd tools/voiceover-elevenlabs && uv run python -c "
from elevenlabs import VoiceSettings
import inspect
print('VoiceSettings fields:', VoiceSettings.model_fields if hasattr(VoiceSettings, 'model_fields') else inspect.signature(VoiceSettings.__init__))
"
```

Record which fields are valid for v3. Working assumption: `stability`, `similarity_boost`, `style`, `use_speaker_boost`, `speed`. If v3 uses a different shape, note it.

- [ ] **Step 4: Look up v3's per-request character limit**

```bash
# Open in browser; record the documented limit. Working assumption: 10,000.
echo "Visit: https://elevenlabs.io/docs/api-reference/text-to-speech/convert"
echo "Visit: https://elevenlabs.io/docs/models#eleven-v3"
```

If the docs state a number, record it. If not, the working assumption stays at 10,000 (well under any plausible v3 limit for the scripts we'll send) and the implementation includes a comment noting the assumption.

- [ ] **Step 5: Look up Scribe v2 cost per second**

```bash
echo "Visit: https://elevenlabs.io/pricing"
```

Record the per-character or per-second rate for Scribe v2. The CLI uses this for its cost-estimate print. Working assumption: ~$0.40/hour of audio.

- [ ] **Step 6: Note findings**

Hold the four answers (TTS method, STT method, voice settings shape, char limit, Scribe rate) in working memory for the next tasks. No commit needed — this task produces no file changes.

---

## Task 3: Define types for transcript.py (TDD setup)

The mapping function in `transcript.py` consumes the SDK's Scribe response and emits the project's `transcript.json` shape. Defining both types up front makes the mapping function trivial to test.

**Files:**
- Create: `tools/voiceover-elevenlabs/src/voiceover_elevenlabs/transcript.py`
- Create: `tools/voiceover-elevenlabs/tests/__init__.py` (empty)
- Create: `tools/voiceover-elevenlabs/tests/conftest.py`

- [ ] **Step 1: Write empty test package init**

```bash
touch tools/voiceover-elevenlabs/tests/__init__.py
```

- [ ] **Step 2: Write `tools/voiceover-elevenlabs/tests/conftest.py` with fixtures**

```python
"""Shared test fixtures.

The `scribe_response_minimal` fixture mimics the SDK's Scribe v2 response
shape using a plain SimpleNamespace. We don't import the SDK's response
class because pinning to its internal types makes tests fragile across
SDK versions; the wrapper code only reads the attribute names listed here.
"""
from types import SimpleNamespace

import pytest


def _word(text: str, type_: str, start: float, end: float, logprob: float = 0.0, speaker_id: str | None = "speaker_0"):
    """Build a SimpleNamespace mimicking one entry in Scribe's words array."""
    base = {
        "text": text,
        "type": type_,
        "start": start,
        "end": end,
        "logprob": logprob,
    }
    if speaker_id is not None:
        base["speakerId"] = speaker_id
    return SimpleNamespace(**base)


@pytest.fixture
def scribe_response_minimal():
    """A minimal valid Scribe v2 response: 'You open' (2 words + 1 spacing)."""
    return SimpleNamespace(
        languageCode="eng",
        languageProbability=0.95,
        text="You open",
        audioDurationSecs=0.48,
        words=[
            _word("You", "word", 0.18, 0.26, logprob=-7.15e-7),
            _word(" ", "spacing", 0.26, 0.27, speaker_id=None),
            _word("open", "word", 0.27, 0.48, logprob=-2.03e-6),
        ],
    )


@pytest.fixture
def scribe_response_with_audio_event():
    """Includes an audio_event word type — the third 'type' Scribe emits."""
    return SimpleNamespace(
        languageCode="eng",
        languageProbability=0.92,
        text="You open",
        audioDurationSecs=0.6,
        words=[
            _word("You", "word", 0.18, 0.26, logprob=0.0),
            _word("[breath]", "audio_event", 0.26, 0.4, speaker_id=None),
            _word("open", "word", 0.4, 0.6, logprob=0.0),
        ],
    )
```

- [ ] **Step 3: Write the type definitions in `transcript.py` (no logic yet)**

```python
"""Schema mapping: ElevenLabs Scribe v2 SDK response → project transcript.json.

The project's transcript.json shape (snake_case) is the canonical timing
source for every video. The SDK returns camelCase. This module is the only
place that knows about both shapes.
"""
from typing import Literal, TypedDict


class TranscriptWord(TypedDict, total=False):
    text: str
    type: Literal["word", "spacing", "audio_event"]
    start: float
    end: float
    logprob: float
    speaker_id: str


class Transcript(TypedDict):
    audio_duration_secs: float
    language_code: str
    language_probability: float
    text: str
    words: list[TranscriptWord]


def to_transcript(response: object) -> Transcript:
    """Map the SDK's Scribe v2 response into the project's snake_case shape.

    Implemented in Task 4.
    """
    raise NotImplementedError
```

- [ ] **Step 4: Verify the package still imports cleanly**

```bash
cd tools/voiceover-elevenlabs && uv run python -c "from voiceover_elevenlabs import transcript; print(transcript.Transcript)"
```

Expected: prints `<class 'voiceover_elevenlabs.transcript.Transcript'>`.

- [ ] **Step 5: Commit**

```bash
git add tools/voiceover-elevenlabs/src/voiceover_elevenlabs/transcript.py tools/voiceover-elevenlabs/tests/
git commit -m "feat(voiceover-elevenlabs): scaffold transcript schema types"
```

---

## Task 4: Implement transcript mapping function (TDD)

**Files:**
- Modify: `tools/voiceover-elevenlabs/src/voiceover_elevenlabs/transcript.py`
- Create: `tools/voiceover-elevenlabs/tests/test_transcript.py`

- [ ] **Step 1: Write failing tests in `tests/test_transcript.py`**

```python
"""Unit tests for the Scribe v2 → transcript.json mapping."""
import pytest

from voiceover_elevenlabs.transcript import to_transcript


def test_minimal_response_maps_to_project_shape(scribe_response_minimal):
    out = to_transcript(scribe_response_minimal)
    assert out["audio_duration_secs"] == 0.48
    assert out["language_code"] == "eng"
    assert out["language_probability"] == 0.95
    assert out["text"] == "You open"
    assert len(out["words"]) == 3


def test_word_entries_have_full_shape(scribe_response_minimal):
    out = to_transcript(scribe_response_minimal)
    word = out["words"][0]
    assert word["text"] == "You"
    assert word["type"] == "word"
    assert word["start"] == 0.18
    assert word["end"] == 0.26
    assert word["logprob"] == -7.15e-7
    assert word["speaker_id"] == "speaker_0"


def test_spacing_entries_omit_logprob_and_speaker(scribe_response_minimal):
    out = to_transcript(scribe_response_minimal)
    spacing = out["words"][1]
    assert spacing["text"] == " "
    assert spacing["type"] == "spacing"
    assert spacing["start"] == 0.26
    assert spacing["end"] == 0.27
    assert "logprob" not in spacing
    assert "speaker_id" not in spacing


def test_audio_event_entries_treated_like_spacing(scribe_response_with_audio_event):
    out = to_transcript(scribe_response_with_audio_event)
    event = out["words"][1]
    assert event["type"] == "audio_event"
    assert "logprob" not in event
    assert "speaker_id" not in event


def test_missing_audio_duration_raises():
    """The TS reference raises if audioDurationSecs is missing — match that."""
    from types import SimpleNamespace
    bad = SimpleNamespace(
        languageCode="eng",
        languageProbability=0.9,
        text="x",
        audioDurationSecs=None,
        words=[],
    )
    with pytest.raises(ValueError, match="audio_duration_secs"):
        to_transcript(bad)


def test_undefined_word_timestamps_coerced_to_zero():
    """Match the TS reference: missing per-word start/end → 0.0 (defensive)."""
    from types import SimpleNamespace
    response = SimpleNamespace(
        languageCode="eng",
        languageProbability=0.9,
        text="x",
        audioDurationSecs=1.0,
        words=[
            SimpleNamespace(text="x", type="word", start=None, end=None, logprob=0.0, speakerId="speaker_0"),
        ],
    )
    out = to_transcript(response)
    assert out["words"][0]["start"] == 0.0
    assert out["words"][0]["end"] == 0.0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd tools/voiceover-elevenlabs && uv run pytest tests/test_transcript.py -v
```

Expected: all six tests FAIL with `NotImplementedError`.

- [ ] **Step 3: Implement `to_transcript` in `transcript.py`**

Replace the body of `to_transcript`:

```python
def to_transcript(response: object) -> Transcript:
    """Map the SDK's Scribe v2 response into the project's snake_case shape.

    Mirrors the defensive choices in
    learn-motion-canvas/skills/clean-audio/scripts/transcribe.ts:
    - Missing audioDurationSecs → ValueError (downstream tooling needs it).
    - Missing per-word start/end → coerced to 0.0 (Scribe always emits both
      for word/spacing/audio_event types in practice; if it doesn't, the
      defensive default keeps the file parseable rather than crashing here).
    """
    duration = getattr(response, "audioDurationSecs", None)
    if duration is None:
        raise ValueError(
            "Scribe response is missing audio_duration_secs — cannot validate cuts against duration."
        )

    words: list[TranscriptWord] = []
    for w in response.words:
        if w.type == "word":
            entry: TranscriptWord = {
                "text": w.text,
                "type": "word",
                "start": w.start if w.start is not None else 0.0,
                "end": w.end if w.end is not None else 0.0,
                "logprob": w.logprob,
            }
            speaker = getattr(w, "speakerId", None)
            if speaker is not None:
                entry["speaker_id"] = speaker
            words.append(entry)
        else:
            words.append({
                "text": w.text,
                "type": w.type,
                "start": w.start if w.start is not None else 0.0,
                "end": w.end if w.end is not None else 0.0,
            })

    return {
        "audio_duration_secs": duration,
        "language_code": response.languageCode,
        "language_probability": response.languageProbability,
        "text": response.text,
        "words": words,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd tools/voiceover-elevenlabs && uv run pytest tests/test_transcript.py -v
```

Expected: all six tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/voiceover-elevenlabs/src/voiceover_elevenlabs/transcript.py tools/voiceover-elevenlabs/tests/test_transcript.py
git commit -m "feat(voiceover-elevenlabs): map Scribe v2 response to project transcript schema"
```

---

## Task 5: Implement TTS wrapper with retry (TDD)

**Files:**
- Create: `tools/voiceover-elevenlabs/src/voiceover_elevenlabs/tts.py`
- Create: `tools/voiceover-elevenlabs/tests/test_tts.py`

> **Note:** This task assumes Task 2 confirmed the SDK method is `client.text_to_speech.convert(...)` and that it accepts `voice_id`, `text`, `model_id`, `voice_settings`, `output_format`. If Task 2 found different names, update the code below before running.

- [ ] **Step 1: Write the failing tests in `tests/test_tts.py`**

```python
"""Unit tests for the v3 TTS wrapper."""
from unittest.mock import MagicMock, patch

import pytest

from voiceover_elevenlabs.tts import V3_CHAR_LIMIT, synthesize


def _stub_convert_returns(audio_bytes: bytes):
    """Build a MagicMock whose convert() returns an iterable yielding audio_bytes once."""
    return MagicMock(return_value=iter([audio_bytes]))


def test_synthesize_calls_convert_with_expected_args():
    fake_audio = b"\xff\xfb\x90\x00fake-mp3-bytes"
    with patch("voiceover_elevenlabs.tts.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        mock_client.text_to_speech.convert = _stub_convert_returns(fake_audio)
        mock_client_class.return_value = mock_client

        result = synthesize(
            "Hello world.",
            voice_id="VOICE",
            api_key="sk_test",
        )

        mock_client_class.assert_called_once_with(api_key="sk_test")
        call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
        assert call_kwargs["voice_id"] == "VOICE"
        assert call_kwargs["text"] == "Hello world."
        assert call_kwargs["model_id"] == "eleven_v3"
        assert call_kwargs["output_format"] == "mp3_44100_128"
        assert result == fake_audio


def test_synthesize_passes_voice_settings():
    with patch("voiceover_elevenlabs.tts.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        mock_client.text_to_speech.convert = _stub_convert_returns(b"x")
        mock_client_class.return_value = mock_client

        synthesize(
            "x",
            voice_id="V",
            stability=0.7,
            similarity_boost=0.8,
            api_key="sk_test",
        )

        call_kwargs = mock_client.text_to_speech.convert.call_args.kwargs
        settings = call_kwargs["voice_settings"]
        assert settings.stability == 0.7
        assert settings.similarity_boost == 0.8


def test_synthesize_rejects_text_over_char_limit():
    long_text = "x" * (V3_CHAR_LIMIT + 1)
    with pytest.raises(ValueError, match="character limit"):
        synthesize(long_text, voice_id="V", api_key="sk_test")


def test_synthesize_concatenates_streamed_chunks():
    """The SDK's convert() returns an iterator of bytes chunks; we join them."""
    with patch("voiceover_elevenlabs.tts.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        mock_client.text_to_speech.convert = MagicMock(return_value=iter([b"abc", b"def", b"ghi"]))
        mock_client_class.return_value = mock_client

        result = synthesize("hi", voice_id="V", api_key="sk_test")
        assert result == b"abcdefghi"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd tools/voiceover-elevenlabs && uv run pytest tests/test_tts.py -v
```

Expected: all four tests FAIL with `ModuleNotFoundError: No module named 'voiceover_elevenlabs.tts'`.

- [ ] **Step 3: Implement `tts.py`**

```python
"""ElevenLabs v3 Text-to-Speech wrapper.

Thin layer over the official `elevenlabs` SDK. Single responsibility:
take a string of text + voice/model/settings, return MP3 bytes. No I/O,
no retries beyond the SDK's own — the calling code (core.py) handles
file writes and retry orchestration.
"""
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs

# v3 per-request character limit. Working assumption pending Task 2 verification;
# update inline if ElevenLabs documents a different number.
V3_CHAR_LIMIT = 10_000


def synthesize(
    text: str,
    *,
    voice_id: str,
    model_id: str = "eleven_v3",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    output_format: str = "mp3_44100_128",
    api_key: str,
) -> bytes:
    """Render text to MP3 bytes via ElevenLabs v3.

    Raises:
        ValueError: if `text` exceeds the v3 per-request character limit.
        elevenlabs.core.api_error.ApiError: on API failures (caller decides retry).
    """
    if len(text) > V3_CHAR_LIMIT:
        raise ValueError(
            f"Text is {len(text)} characters; v3 character limit is {V3_CHAR_LIMIT}. "
            f"Split the script into parts and re-run."
        )

    client = ElevenLabs(api_key=api_key)
    audio_iter = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id=model_id,
        voice_settings=VoiceSettings(
            stability=stability,
            similarity_boost=similarity_boost,
        ),
        output_format=output_format,
    )
    return b"".join(audio_iter)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd tools/voiceover-elevenlabs && uv run pytest tests/test_tts.py -v
```

Expected: all four tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/voiceover-elevenlabs/src/voiceover_elevenlabs/tts.py tools/voiceover-elevenlabs/tests/test_tts.py
git commit -m "feat(voiceover-elevenlabs): v3 TTS wrapper with char-limit pre-check"
```

---

## Task 6: Implement Scribe wrapper with retry + defensive checks (TDD)

**Files:**
- Create: `tools/voiceover-elevenlabs/src/voiceover_elevenlabs/scribe.py`
- Create: `tools/voiceover-elevenlabs/tests/test_scribe.py`

> **Note:** Mirrors the proven `transcribe.ts` from `learn-motion-canvas/skills/clean-audio/scripts/transcribe.ts`, ported to Python.

- [ ] **Step 1: Write failing tests in `tests/test_scribe.py`**

```python
"""Unit tests for the Scribe v2 wrapper."""
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from voiceover_elevenlabs.scribe import RETRY_BACKOFF_SECS, transcribe


@pytest.fixture
def fake_audio(tmp_path: Path) -> Path:
    p = tmp_path / "voiceover.mp3"
    p.write_bytes(b"\xff\xfb\x90\x00fake")
    return p


def _scribe_response():
    return SimpleNamespace(
        languageCode="eng",
        languageProbability=0.95,
        text="hi",
        audioDurationSecs=1.0,
        words=[],
    )


def test_transcribe_calls_convert_with_expected_args(fake_audio):
    with patch("voiceover_elevenlabs.scribe.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        mock_client.speech_to_text.convert = MagicMock(return_value=_scribe_response())
        mock_client_class.return_value = mock_client

        transcribe(fake_audio, api_key="sk_test")

        mock_client_class.assert_called_once_with(api_key="sk_test")
        call_kwargs = mock_client.speech_to_text.convert.call_args.kwargs
        assert call_kwargs["model_id"] == "scribe_v2"
        assert call_kwargs["timestamps_granularity"] == "word"
        assert call_kwargs["diarize"] is True
        assert call_kwargs["tag_audio_events"] is True


def test_transcribe_returns_response_object(fake_audio):
    with patch("voiceover_elevenlabs.scribe.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        expected = _scribe_response()
        mock_client.speech_to_text.convert = MagicMock(return_value=expected)
        mock_client_class.return_value = mock_client

        result = transcribe(fake_audio, api_key="sk_test")
        assert result is expected


def test_transcribe_rejects_multichannel_response(fake_audio):
    with patch("voiceover_elevenlabs.scribe.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        # Multichannel responses have a 'transcripts' attribute (per the TS reference).
        bad = SimpleNamespace(transcripts=[_scribe_response()])
        mock_client.speech_to_text.convert = MagicMock(return_value=bad)
        mock_client_class.return_value = mock_client

        with pytest.raises(ValueError, match="Multichannel"):
            transcribe(fake_audio, api_key="sk_test")


def test_transcribe_rejects_webhook_response(fake_audio):
    with patch("voiceover_elevenlabs.scribe.ElevenLabs") as mock_client_class:
        mock_client = MagicMock()
        # Webhook responses have a 'requestId' attribute and no inline transcript.
        bad = SimpleNamespace(requestId="req_123")
        mock_client.speech_to_text.convert = MagicMock(return_value=bad)
        mock_client_class.return_value = mock_client

        with pytest.raises(ValueError, match="Webhook"):
            transcribe(fake_audio, api_key="sk_test")


def test_transcribe_raises_for_missing_file(tmp_path: Path):
    missing = tmp_path / "nope.mp3"
    with pytest.raises(FileNotFoundError):
        transcribe(missing, api_key="sk_test")


def test_retry_backoff_constants_match_reference():
    """The TS reference uses [5_000, 25_000] ms — Python uses seconds."""
    assert RETRY_BACKOFF_SECS == [5, 25]
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd tools/voiceover-elevenlabs && uv run pytest tests/test_scribe.py -v
```

Expected: all six tests FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `scribe.py`**

```python
"""ElevenLabs Scribe v2 wrapper.

Thin layer over the official `elevenlabs` SDK. Mirrors the proven defensive
choices in learn-motion-canvas/skills/clean-audio/scripts/transcribe.ts:
- Reject multichannel responses (we only support single-channel narration).
- Reject webhook responses (we need the transcript inline).
- Require single audio file path; SDK's `file` parameter handles the upload.
"""
from pathlib import Path

from elevenlabs.client import ElevenLabs

# Mirrors the TS reference's retry policy: 5s backoff on first 429, 25s on second.
# The CLI applies these via core.py — this module is a single-shot wrapper.
RETRY_BACKOFF_SECS = [5, 25]


def transcribe(audio_path: Path, *, api_key: str) -> object:
    """Transcribe an audio file with Scribe v2 at word granularity.

    Returns the raw SDK response (camelCase). Use `transcript.to_transcript`
    to convert to the project's snake_case shape.

    Raises:
        FileNotFoundError: if `audio_path` doesn't exist.
        ValueError: if the response is multichannel or webhook-mode (unsupported).
        elevenlabs.core.api_error.ApiError: on API failures.
    """
    if not audio_path.exists():
        raise FileNotFoundError(f"Input audio not found: {audio_path}")

    client = ElevenLabs(api_key=api_key)
    with audio_path.open("rb") as f:
        response = client.speech_to_text.convert(
            model_id="scribe_v2",
            file=f,
            timestamps_granularity="word",
            diarize=True,
            tag_audio_events=True,
        )

    if hasattr(response, "transcripts"):
        raise ValueError(
            "Multichannel transcripts are not supported. Provide single-channel audio."
        )
    if hasattr(response, "requestId"):
        raise ValueError(
            "Webhook mode is not supported — the tool needs the transcript inline."
        )

    return response
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd tools/voiceover-elevenlabs && uv run pytest tests/test_scribe.py -v
```

Expected: all six tests PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/voiceover-elevenlabs/src/voiceover_elevenlabs/scribe.py tools/voiceover-elevenlabs/tests/test_scribe.py
git commit -m "feat(voiceover-elevenlabs): Scribe v2 wrapper with multichannel/webhook rejection"
```

---

## Task 7: Implement core orchestrator (TDD)

**Files:**
- Create: `tools/voiceover-elevenlabs/src/voiceover_elevenlabs/core.py`
- Create: `tools/voiceover-elevenlabs/tests/test_core.py`
- Modify: `tools/voiceover-elevenlabs/src/voiceover_elevenlabs/__init__.py`

- [ ] **Step 1: Write failing tests in `tests/test_core.py`**

```python
"""End-to-end tests for the core orchestrator (with mocked SDK)."""
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from voiceover_elevenlabs.core import generate


@pytest.fixture
def temp_video_dir(tmp_path: Path) -> Path:
    (tmp_path / "audio").mkdir()
    return tmp_path


def _scribe_response():
    return SimpleNamespace(
        languageCode="eng",
        languageProbability=0.95,
        text="Hello world",
        audioDurationSecs=1.5,
        words=[
            SimpleNamespace(text="Hello", type="word", start=0.0, end=0.5, logprob=0.0, speakerId="speaker_0"),
            SimpleNamespace(text=" ", type="spacing", start=0.5, end=0.6),
            SimpleNamespace(text="world", type="word", start=0.6, end=1.5, logprob=0.0, speakerId="speaker_0"),
        ],
    )


def test_generate_writes_audio_and_transcript(temp_video_dir: Path):
    text_path = temp_video_dir / "voiceover.txt"
    text_path.write_text("Hello world.")
    audio_path = temp_video_dir / "audio" / "voiceover.mp3"
    transcript_path = temp_video_dir / "transcript.json"

    with (
        patch("voiceover_elevenlabs.core.synthesize") as mock_synth,
        patch("voiceover_elevenlabs.core.transcribe") as mock_transcribe,
    ):
        mock_synth.return_value = b"\xff\xfb\x90\x00fake-mp3"
        mock_transcribe.return_value = _scribe_response()

        generate(
            text_path=text_path,
            audio_path=audio_path,
            transcript_path=transcript_path,
            voice_id="VOICE",
            api_key="sk_test",
        )

        assert audio_path.read_bytes() == b"\xff\xfb\x90\x00fake-mp3"
        transcript = json.loads(transcript_path.read_text())
        assert transcript["audio_duration_secs"] == 1.5
        assert transcript["language_code"] == "eng"
        assert len(transcript["words"]) == 3


def test_generate_skips_transcript_when_disabled(temp_video_dir: Path):
    text_path = temp_video_dir / "voiceover.txt"
    text_path.write_text("hi")
    audio_path = temp_video_dir / "audio" / "voiceover.mp3"
    transcript_path = temp_video_dir / "transcript.json"

    with (
        patch("voiceover_elevenlabs.core.synthesize") as mock_synth,
        patch("voiceover_elevenlabs.core.transcribe") as mock_transcribe,
    ):
        mock_synth.return_value = b"audio"

        generate(
            text_path=text_path,
            audio_path=audio_path,
            transcript_path=transcript_path,
            voice_id="V",
            api_key="sk",
            generate_transcript=False,
        )

        assert audio_path.exists()
        assert not transcript_path.exists()
        mock_transcribe.assert_not_called()


def test_generate_creates_audio_parent_dir(tmp_path: Path):
    text_path = tmp_path / "voiceover.txt"
    text_path.write_text("hi")
    audio_path = tmp_path / "fresh-dir" / "voiceover.mp3"
    transcript_path = tmp_path / "transcript.json"

    with (
        patch("voiceover_elevenlabs.core.synthesize") as mock_synth,
        patch("voiceover_elevenlabs.core.transcribe") as mock_transcribe,
    ):
        mock_synth.return_value = b"a"
        mock_transcribe.return_value = _scribe_response()

        generate(
            text_path=text_path,
            audio_path=audio_path,
            transcript_path=transcript_path,
            voice_id="V",
            api_key="sk",
        )

        assert audio_path.exists()


def test_generate_overwrites_existing_files(temp_video_dir: Path):
    text_path = temp_video_dir / "voiceover.txt"
    text_path.write_text("hi")
    audio_path = temp_video_dir / "audio" / "voiceover.mp3"
    transcript_path = temp_video_dir / "transcript.json"
    audio_path.write_bytes(b"old-audio")
    transcript_path.write_text("{}")

    with (
        patch("voiceover_elevenlabs.core.synthesize") as mock_synth,
        patch("voiceover_elevenlabs.core.transcribe") as mock_transcribe,
    ):
        mock_synth.return_value = b"new-audio"
        mock_transcribe.return_value = _scribe_response()

        generate(
            text_path=text_path,
            audio_path=audio_path,
            transcript_path=transcript_path,
            voice_id="V",
            api_key="sk",
        )

        assert audio_path.read_bytes() == b"new-audio"
        assert json.loads(transcript_path.read_text())["language_code"] == "eng"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd tools/voiceover-elevenlabs && uv run pytest tests/test_core.py -v
```

Expected: all four tests FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `core.py`**

```python
"""High-level orchestrator: text file → audio + transcript on disk.

Orchestrates the two API calls (v3 TTS, then Scribe v2 on the rendered
audio) and the schema mapping. Intentionally simple — no retry logic
beyond what the wrappers do; no parallelism (Scribe needs the audio).
"""
import json
from pathlib import Path

from voiceover_elevenlabs.scribe import transcribe
from voiceover_elevenlabs.transcript import to_transcript
from voiceover_elevenlabs.tts import synthesize


def generate(
    *,
    text_path: Path,
    audio_path: Path,
    transcript_path: Path,
    voice_id: str,
    api_key: str,
    model_id: str = "eleven_v3",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    output_format: str = "mp3_44100_128",
    generate_transcript: bool = True,
) -> None:
    """Read text, render audio via v3, transcribe via Scribe v2, write both files.

    Overwrites existing files at `audio_path` and `transcript_path` without
    prompting (per spec §Q3). Creates parent directories as needed.
    """
    text = text_path.read_text()

    audio_bytes = synthesize(
        text,
        voice_id=voice_id,
        model_id=model_id,
        stability=stability,
        similarity_boost=similarity_boost,
        output_format=output_format,
        api_key=api_key,
    )
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    audio_path.write_bytes(audio_bytes)

    if not generate_transcript:
        return

    response = transcribe(audio_path, api_key=api_key)
    transcript_data = to_transcript(response)
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_path.write_text(json.dumps(transcript_data, indent=2))
```

- [ ] **Step 4: Update `__init__.py` to export the public API**

```python
"""ElevenLabs v3 TTS + Scribe v2 transcript pipeline for hyper-frames videos."""
from voiceover_elevenlabs.core import generate
from voiceover_elevenlabs.scribe import transcribe
from voiceover_elevenlabs.transcript import to_transcript
from voiceover_elevenlabs.tts import synthesize

__all__ = ["generate", "synthesize", "transcribe", "to_transcript"]
```

- [ ] **Step 5: Run all tests to verify everything passes**

```bash
cd tools/voiceover-elevenlabs && uv run pytest tests/ -v
```

Expected: all tests across `test_transcript.py`, `test_tts.py`, `test_scribe.py`, `test_core.py` PASS.

- [ ] **Step 6: Commit**

```bash
git add tools/voiceover-elevenlabs/src/voiceover_elevenlabs/core.py tools/voiceover-elevenlabs/src/voiceover_elevenlabs/__init__.py tools/voiceover-elevenlabs/tests/test_core.py
git commit -m "feat(voiceover-elevenlabs): orchestrator that wires TTS + Scribe + schema mapping"
```

---

## Task 8: Implement CLI entry point

**Files:**
- Create: `tools/voiceover-elevenlabs/src/voiceover_elevenlabs/cli.py`
- Create: `tools/voiceover-elevenlabs/tests/test_cli.py`

- [ ] **Step 1: Write tests in `tests/test_cli.py`**

```python
"""CLI entry-point tests."""
from pathlib import Path
from unittest.mock import patch

import pytest

from voiceover_elevenlabs.cli import build_parser, main


def test_parser_accepts_required_input_path():
    parser = build_parser()
    args = parser.parse_args(["voiceover.txt"])
    assert args.input_path == Path("voiceover.txt")


def test_parser_default_output_paths():
    parser = build_parser()
    args = parser.parse_args(["voiceover.txt"])
    assert args.output_audio == Path("audio/voiceover.mp3")
    assert args.output_transcript == Path("transcript.json")


def test_parser_default_voice_id_is_project_voice():
    parser = build_parser()
    args = parser.parse_args(["voiceover.txt"])
    assert args.voice_id == "UgBBYS2sOqTuMpoF3BR0"


def test_parser_default_model_is_v3():
    parser = build_parser()
    args = parser.parse_args(["voiceover.txt"])
    assert args.model == "eleven_v3"


def test_parser_no_transcript_flag():
    parser = build_parser()
    args = parser.parse_args(["voiceover.txt", "--no-transcript"])
    assert args.generate_transcript is False


def test_parser_dry_run_flag():
    parser = build_parser()
    args = parser.parse_args(["voiceover.txt", "--dry-run"])
    assert args.dry_run is True


def test_main_dry_run_prints_cost_estimate(tmp_path: Path, capsys):
    text_path = tmp_path / "voiceover.txt"
    text_path.write_text("Hello world.")

    with patch.dict("os.environ", {"ELEVENLABS_API_KEY": "sk_test"}):
        exit_code = main([str(text_path), "--dry-run"])

    assert exit_code == 0
    captured = capsys.readouterr()
    assert "characters" in captured.out
    assert "credits" in captured.out


def test_main_errors_when_api_key_missing(tmp_path: Path, capsys):
    text_path = tmp_path / "voiceover.txt"
    text_path.write_text("hi")

    # Patch load_dotenv so a real .env in the dev environment doesn't bleed in.
    with (
        patch.dict("os.environ", {}, clear=True),
        patch("voiceover_elevenlabs.cli.load_dotenv"),
    ):
        exit_code = main([str(text_path)])

    assert exit_code == 2
    captured = capsys.readouterr()
    assert "ELEVENLABS_API_KEY" in captured.err


def test_main_invokes_generate_with_resolved_paths(tmp_path: Path):
    text_path = tmp_path / "voiceover.txt"
    text_path.write_text("hi")
    audio_path = tmp_path / "audio" / "voiceover.mp3"
    transcript_path = tmp_path / "transcript.json"

    with (
        patch.dict("os.environ", {"ELEVENLABS_API_KEY": "sk_test"}, clear=True),
        patch("voiceover_elevenlabs.cli.load_dotenv"),
        patch("voiceover_elevenlabs.cli.generate") as mock_generate,
    ):
        exit_code = main([
            str(text_path),
            "-o", str(audio_path),
            "--output-transcript", str(transcript_path),
        ])

        assert exit_code == 0
        kwargs = mock_generate.call_args.kwargs
        assert kwargs["text_path"] == text_path
        assert kwargs["audio_path"] == audio_path
        assert kwargs["transcript_path"] == transcript_path
        assert kwargs["api_key"] == "sk_test"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd tools/voiceover-elevenlabs && uv run pytest tests/test_cli.py -v
```

Expected: all nine tests FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `cli.py`**

```python
"""Command-line entry point.

Usage:
    voiceover-elevenlabs voiceover.txt
    voiceover-elevenlabs voiceover.txt --dry-run
    voiceover-elevenlabs voiceover.txt --no-transcript -o audio/v.mp3
"""
import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from voiceover_elevenlabs.core import generate

# v3 cost per 1k characters in credits. Used only for the dry-run estimate.
V3_CREDITS_PER_1K_CHARS = 30
# Scribe v2 cost in USD per hour of audio. Used only for the dry-run estimate.
SCRIBE_USD_PER_HOUR = 0.40
# Words per minute (project house style — 170 wpm per CLAUDE.md).
WORDS_PER_MINUTE = 170


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="voiceover-elevenlabs",
        description="Generate v3 voiceover + Scribe v2 transcript from an annotated script.",
    )
    parser.add_argument("input_path", type=Path, help="Path to the annotated script (e.g. voiceover.txt).")
    parser.add_argument("-o", "--output-audio", type=Path, default=Path("audio/voiceover.mp3"))
    parser.add_argument("--output-transcript", type=Path, default=Path("transcript.json"))
    parser.add_argument("--voice-id", default="UgBBYS2sOqTuMpoF3BR0")
    parser.add_argument("--model", default="eleven_v3")
    parser.add_argument("--stability", type=float, default=0.5)
    parser.add_argument("--similarity-boost", type=float, default=0.75)
    parser.add_argument("--no-transcript", dest="generate_transcript", action="store_false")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print char count + cost estimate without calling any API.")
    return parser


def _estimate_cost(text: str) -> str:
    chars = len(text)
    words = len(text.split())
    minutes = words / WORDS_PER_MINUTE
    credits = chars * V3_CREDITS_PER_1K_CHARS / 1000
    scribe_usd = minutes * SCRIBE_USD_PER_HOUR / 60
    return (
        f"{chars} characters · ~{words} words · ~{minutes:.1f} min audio\n"
        f"v3 TTS: ~{credits:.0f} credits\n"
        f"Scribe v2: ~${scribe_usd:.2f}"
    )


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.input_path.exists():
        print(f"Input not found: {args.input_path}", file=sys.stderr)
        return 2

    text = args.input_path.read_text()

    if args.dry_run:
        print(_estimate_cost(text))
        return 0

    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        print(
            "ELEVENLABS_API_KEY is not set. Add it to .env at the repo root.",
            file=sys.stderr,
        )
        return 2

    print(_estimate_cost(text))
    print(f"Generating audio → {args.output_audio}", file=sys.stderr)

    try:
        generate(
            text_path=args.input_path,
            audio_path=args.output_audio,
            transcript_path=args.output_transcript,
            voice_id=args.voice_id,
            api_key=api_key,
            model_id=args.model,
            stability=args.stability,
            similarity_boost=args.similarity_boost,
            generate_transcript=args.generate_transcript,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"API error: {e}", file=sys.stderr)
        return 1

    print(f"Audio    → {args.output_audio}")
    if args.generate_transcript:
        print(f"Transcript → {args.output_transcript}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd tools/voiceover-elevenlabs && uv run pytest tests/test_cli.py -v
```

Expected: all nine tests PASS.

- [ ] **Step 5: Verify the installed entry point works**

```bash
cd tools/voiceover-elevenlabs && uv sync && uv run voiceover-elevenlabs --help
```

Expected: prints argparse help, exit code 0.

- [ ] **Step 6: Commit**

```bash
git add tools/voiceover-elevenlabs/src/voiceover_elevenlabs/cli.py tools/voiceover-elevenlabs/tests/test_cli.py
git commit -m "feat(voiceover-elevenlabs): CLI with dry-run cost estimate"
```

---

## Task 9: Write tool README

**Files:**
- Create: `tools/voiceover-elevenlabs/README.md`

- [ ] **Step 1: Write `tools/voiceover-elevenlabs/README.md`**

```markdown
# voiceover-elevenlabs

Generate voiceover audio (ElevenLabs v3) and a word-level transcript
(ElevenLabs Scribe v2 on the rendered audio) from an annotated script,
in a single command. Built for the hyper-frames video pipeline; produces
the canonical `audio/voiceover.mp3` + `transcript.json` shape the rest
of the project consumes.

The transcript is generated from Scribe v2, **not** v3's native
character alignment. See the spec at
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
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/voiceover-elevenlabs \
  voiceover-elevenlabs voiceover.txt
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
from the `voiceover-elevenlabs` skill, with v3 audio tags (`[sighs]`),
ellipses (`…`), and ALL-CAPS emphasis applied. The tool sends the file
contents to v3 verbatim.

## Library use

```python
from pathlib import Path
from voiceover_elevenlabs import generate

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
(missing `audioDurationSecs`, undefined per-word timestamps).

## Origin

Spec: `docs/superpowers/specs/2026-05-09-voiceover-elevenlabs-design.md`.
Replaces the `hyperframes-media tts` (Kokoro) path for this project's
videos. The Kokoro skill stays untouched and parallel for any non-v3
use case.
```

- [ ] **Step 2: Commit**

```bash
git add tools/voiceover-elevenlabs/README.md
git commit -m "docs(voiceover-elevenlabs): tool README"
```

---

## Task 10: Verify .env / .gitignore coverage

**Files:**
- Modify (maybe): `.gitignore` at repo root

- [ ] **Step 1: Check whether `.env` is already gitignored**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames && grep -n "^\.env" .gitignore || echo "NOT IGNORED"
```

If output is `NOT IGNORED`, proceed to Step 2. If `.env` is already there, skip Step 2.

- [ ] **Step 2: Add `.env` to repo root `.gitignore` if missing**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames && printf '\n# ElevenLabs API key (loaded by tools/voiceover-elevenlabs)\n.env\n' >> .gitignore
```

- [ ] **Step 3: Verify the `.env` file (if it exists) is not tracked**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames && git ls-files .env
```

Expected: empty output (file not tracked). If output shows `.env` is tracked, ask the user before doing anything — accidentally committed secrets need rotation, not just `.gitignore` edits.

- [ ] **Step 4: Commit `.gitignore` change (if any)**

```bash
git add .gitignore && git diff --cached --quiet || git commit -m "chore: gitignore .env for ElevenLabs API key"
```

---

## Task 11: End-to-end manual smoke test

This is a manual integration test against the real ElevenLabs API. It uses a tiny test input (one sentence) to keep cost negligible (~3 credits, ~$0.001 in Scribe).

**Files:**
- Create (temporary): `/tmp/smoke-voiceover.txt`
- No persistent file changes from this task.

- [ ] **Step 1: Verify `ELEVENLABS_API_KEY` is set in `.env`**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames && grep -c "ELEVENLABS_API_KEY=" .env
```

Expected: `1`. If `0`, ask the user to add the key to `.env` before proceeding.

- [ ] **Step 2: Run the dry-run on a tiny script**

```bash
mkdir -p /tmp/voiceover-smoke && cd /tmp/voiceover-smoke && \
  printf 'You open a text editor.\n' > voiceover.txt && \
  uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/voiceover-elevenlabs \
    voiceover-elevenlabs voiceover.txt --dry-run
```

Expected: prints char count, word count, cost estimate. Exit 0. No API call made.

- [ ] **Step 3: Run for real against ElevenLabs**

```bash
cd /tmp/voiceover-smoke && \
  uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/voiceover-elevenlabs \
    voiceover-elevenlabs voiceover.txt
```

Expected output:
- Cost estimate printed.
- "Generating audio → audio/voiceover.mp3"
- "Audio    → audio/voiceover.mp3"
- "Transcript → transcript.json"
- Exit 0.

- [ ] **Step 4: Inspect the outputs**

```bash
cd /tmp/voiceover-smoke && \
  ls -la audio/voiceover.mp3 transcript.json && \
  python3 -c "import json; t = json.load(open('transcript.json')); print('duration:', t['audio_duration_secs']); print('first word:', t['words'][0])"
```

Expected:
- `audio/voiceover.mp3` exists, non-empty (typically 5–20 KB for one sentence).
- `transcript.json` parses; has `audio_duration_secs > 0`; first word is `"You"` with non-zero `start` and `end` times.

If the duration looks wrong, the first word's `text` mismatches "You", or the timestamps look fake, **stop and investigate before moving on**. The spec's invariant is that this transcript is the source of truth for the rest of the pipeline.

- [ ] **Step 5: Clean up the smoke-test directory**

```bash
rm -rf /tmp/voiceover-smoke
```

- [ ] **Step 6: No commit — this task produces no persistent changes.**

---

## Task 12: Write the skill

**Files:**
- Create: `.claude/skills/voiceover-elevenlabs/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p .claude/skills/voiceover-elevenlabs
```

- [ ] **Step 2: Write `.claude/skills/voiceover-elevenlabs/SKILL.md`**

```markdown
---
name: voiceover-elevenlabs
description: Turn an approved script.md into a voiceover (ElevenLabs v3) and a word-level transcript (Scribe v2) in one run, with an LLM-driven beat-aware annotation step (curated audio tags, ellipses, anchor-driven ALL-CAPS) behind a hard checkpoint before any API credits are spent. Use when the user says "generate the voiceover", "voice this script", "tts the script", "make the audio", or after the script-writer skill's handoff prompt. Replaces the hyperframes-media (Kokoro) TTS path for this project; hyperframes-media stays untouched for any other use case. Outputs land at the canonical project locations: audio/voiceover.mp3 and transcript.json at the video folder root.
---

# voiceover-elevenlabs

You are turning an approved `script.md` into both `audio/voiceover.mp3`
and `transcript.json` for a hyper-frames video, in one checkpointed flow.
The intelligence is in the **annotation** step: a beat-aware preprocessor
that selectively inserts v3 audio tags, pacing ellipses, and ALL-CAPS
emphasis to make the rendered audio land for YouTube viewers without
fighting the project's plain-prose house style.

The deterministic work — calling ElevenLabs v3, calling Scribe v2 on the
rendered audio, mapping the response to the project's transcript schema —
lives in `tools/voiceover-elevenlabs/`. This skill drives that tool.

## What this skill does and doesn't do

**Does:**
- Locate the target video folder (`videos/<slug>-<date>/`) from the user's
  message, CWD, or by asking.
- Read `script.md` (required) and `anchors.txt` (optional but strongly
  preferred — it's the source for ALL-CAPS candidates).
- Produce `voiceover.txt` with curated v3 annotations per the taxonomy in §3.
- Run a hard checkpoint: show char count, cost estimate, annotation summary,
  and a list of additions. Wait for explicit `approve and generate` /
  `edit` / `regenerate` before any API call.
- Invoke `tools/voiceover-elevenlabs/` to render audio and transcript.
- Confirm both outputs exist and report duration + word count.

**Does not:**
- Generate compositions, run `hyperframes preview`, or invoke
  `hyperframes render`. Same boundary as `script-writer`.
- Generate `narration-map.json`. The user runs that separately after this
  skill completes (the skill prints the next-step command).
- Touch `hyperframes-media`. The Kokoro path stays parallel.
- Use multi-voice / `text-to-dialogue`. Single-narrator only.
- Auto-chunk over-limit scripts. Errors loudly with a "split into parts"
  message; user splits manually.

## The flow

### Step 1 — Locate inputs

Resolve the target video folder, in this priority order:

1. Explicit path in the user's message (e.g. `videos/<slug>-<date>/`).
2. Current working directory if it matches `**/videos/<slug>-<date>/`.
3. Ask the user. List existing `videos/*` folders to make the choice
   concrete.

Once resolved (call it `<video-dir>`), read:

- `<video-dir>/script.md` — required. If missing, error and tell the user
  to run `script-writer` first.
- `<video-dir>/anchors.txt` — optional. Parse it as one phrase per line,
  ignore `#` comments and blank lines.

Note whether `<!-- BEAT n: <name> -->` markers are present in `script.md`.
Their presence drives the annotation posture in step 2.

### Step 2 — Annotate

Produce `<video-dir>/voiceover.txt` per the taxonomy in §3. **Strip
`<!-- BEAT n -->` HTML comments from the output** — they would be spoken
otherwise. The output is plain UTF-8 text, no markdown, no headers.

Posture: **conservative + beat-aware**. Specific rules:

- Use the `<!-- BEAT -->` markers to know which beat each sentence belongs to.
- Apply the per-beat rubric in §3.1.
- Honor the hard caps in §3.2 — no exceptions.
- If there are no `<!-- BEAT -->` markers, fall back to per-sentence
  beat-blind annotation with the same hard caps. Warn the user.

Write `voiceover.txt` to disk before showing it to the user — they may want
to inspect the file directly.

### Step 3 — Hard checkpoint

Show the user, in one message:

1. **Char count** of `voiceover.txt`.
2. **Estimated cost**:
   - v3 TTS: `chars × 0.030` credits (v3 rate).
   - Scribe v2: `(words / 170) / 60 × $0.40` USD.
3. **Annotation summary**: e.g. "Added 2 audio tags ([sighs] × 1, [curious]
   × 1), 5 ellipses (3 between escalation moves, 2 in beat 4 thesis), 7
   ALL-CAPS terms from anchors.txt".
4. **Numbered list of additions** (since real diff rendering isn't reliable
   in this terminal). Format: `Beat N · Line excerpt · Addition`.

End with three explicit options:

- `approve and generate` — proceed to step 4.
- `edit` — user gives free-form feedback; you revise `voiceover.txt` and
  re-show the checkpoint.
- `regenerate` — you redo `voiceover.txt` from scratch with a different
  posture (e.g. more conservative). Re-show the checkpoint.

**Do not proceed to step 4 until the user explicitly approves.** Cost is
real (~150 credits per 5-minute video).

### Step 4 — Generate

Invoke the tool:

```bash
uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/voiceover-elevenlabs \
  voiceover-elevenlabs <video-dir>/voiceover.txt \
  -o <video-dir>/audio/voiceover.mp3 \
  --output-transcript <video-dir>/transcript.json
```

Stream the output. On success, verify:

- `<video-dir>/audio/voiceover.mp3` exists and is non-empty.
- `<video-dir>/transcript.json` exists, parses as JSON, has the expected
  top-level keys (`audio_duration_secs`, `language_code`, `words`).

Report to the user: audio duration (from `transcript.json`'s
`audio_duration_secs`), word count, file sizes.

### Step 5 — Done

Tell the user the next step is theirs:

> Audio + transcript are ready. Next:
> ```bash
> uv run --project ../../tools/narration-map narration-map \
>   transcript.json --anchors anchors.txt
> ```
> then start authoring compositions against `narration-map.json`.

This skill stops at `transcript.json`.

## Annotation taxonomy

### 3.1 Per-beat rubric

| Beat | What gets added |
|---|---|
| 1 — Open | Light. Maybe one `…` after the opening clause for breathing room. No tags. |
| 2 — Subversion | Natural home for one `[sighs]` or `[curious]` on the "but" pivot. Single tag, max. |
| 3 — Stakes | ALL-CAPS on named systems/numbers if they appear in `anchors.txt`. |
| 4 — Thesis | ALL-CAPS on the three anchor terms in the three-part list. `…` between the three parts if present. |
| 5 — Foundation | Plain. Optionally ALL-CAPS on the named concept being defined (if in `anchors.txt`). |
| 6 — Escalation cycles | `…` between naive→flaw→smarter→new flaw moves within each cycle. ALL-CAPS on the smarter solution's name (anchor). |
| 7 — Synthesis | If the script personifies a system, allow `[thoughtful]` once. Otherwise plain. |
| 8 — Reframe | `…` after "The next time you…" for the gear-shift moment. |
| 9 — Closer | `…` for deliberate slow-down. No tags — let the prose carry the weight. |

### 3.2 Hard caps (no exceptions)

- **≤ 3 audio tags total in a 5-minute script. ≤ 5 in a 10-minute script.**
- **ALL-CAPS only on terms that appear in `anchors.txt`.** No ad-hoc
  capitalization. If `anchors.txt` is missing, no ALL-CAPS at all.
- **`…` is unbounded** but used only at structural transitions (between
  three-part list items, between escalation moves, before reframes), never
  mid-clause.
- **Banned tags**: `[laughs]`, `[applause]`, `[gunshot]`, `[explosion]`,
  `[strong X accent]`, `[sings]`, `[fart]`, `[woo]`. These don't fit
  narrative essay style.
- **Allowed tags** (use sparingly, max one per beat where applicable):
  `[sighs]`, `[curious]`, `[thoughtful]`, `[exhales]`. That's the whole
  list; resist the temptation to expand it.

## Edge cases

- **No `<!-- BEAT -->` markers in `script.md`**: fall back to per-sentence
  beat-blind annotation, same hard caps. Warn the user that `anchors.txt`
  ALL-CAPS still works but beat-specific tag placement won't.
- **No `anchors.txt`**: skip ALL-CAPS entirely. Annotation becomes
  punctuation + sparse tags only. Warn the user.
- **Script over v3 char limit**: the tool errors at the API call. Tell the
  user to split `voiceover.txt` into parts and re-run; offer to do the
  split.
- **API key missing**: the tool errors with a clear message. Tell the user
  to add `ELEVENLABS_API_KEY=...` to `.env` at the repo root.
- **User wants to skip annotation entirely**: respect that. Copy `script.md`
  → `voiceover.txt` (stripping `<!-- BEAT -->` comments), show the
  checkpoint, proceed.

## Done condition

You're done when:

- `<video-dir>/voiceover.txt` exists with the user-approved annotated text.
- `<video-dir>/audio/voiceover.mp3` exists and is non-empty.
- `<video-dir>/transcript.json` exists, parses, and has `audio_duration_secs > 0`.
- The user has been told the next step is `narration-map`.
```

- [ ] **Step 3: Verify the skill is discoverable**

```bash
ls -la /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/.claude/skills/voiceover-elevenlabs/SKILL.md
```

Expected: file exists, non-empty.

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/voiceover-elevenlabs/
git commit -m "feat(skill): voiceover-elevenlabs (LLM-driven annotation + tool driver)"
```

---

## Task 13: Edit script-writer handoff

**Files:**
- Modify: `.claude/skills/script-writer/SKILL.md` (specifically the "Done condition" block at line 200+)

- [ ] **Step 1: Read the current Done condition block**

```bash
sed -n '198,208p' /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/.claude/skills/script-writer/SKILL.md
```

Expected output:

```
## Done condition

You're done when:

- `videos/<slug>-<YYYY-MM-DD>/` exists with `outline.md`, `script.md`, `anchors.txt`.
- The user has approved the full script end-to-end.
- The script reads at the target runtime (count words / 170 to verify).
- Any TTS gotchas surfaced during the session have been appended to `reference/tts-gotchas.md`.

Tell the user the next step is theirs: generate the TTS audio with `npx hyperframes-media tts` (or whichever TTS the project standardizes on), drop it into `audio/`, then run the user's transcript pipeline to produce `transcript.json`, then run `narration-map` with `anchors.txt`. This skill stops at `script.md`.
```

- [ ] **Step 2: Apply the handoff edit**

Use the Edit tool to replace the final paragraph (the "Tell the user the next step is theirs..." line):

**Old string:**

```
Tell the user the next step is theirs: generate the TTS audio with `npx hyperframes-media tts` (or whichever TTS the project standardizes on), drop it into `audio/`, then run the user's transcript pipeline to produce `transcript.json`, then run `narration-map` with `anchors.txt`. This skill stops at `script.md`.
```

**New string:**

```
Once `script.md`, `outline.md`, and `anchors.txt` are written and approved, ask the user: *"Script is locked. Want me to generate the voiceover with ElevenLabs v3 now? (invokes the `voiceover-elevenlabs` skill)"* If yes, hand off to that skill — it produces both `audio/voiceover.mp3` and `transcript.json` in one run. If no, tell the user the next step is theirs (`uv run --project ../../tools/voiceover-elevenlabs voiceover-elevenlabs voiceover.txt`), then run `narration-map` with `anchors.txt`. This skill stops at `script.md`.
```

- [ ] **Step 3: Verify the edit landed cleanly**

```bash
grep -n "voiceover-elevenlabs" /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/.claude/skills/script-writer/SKILL.md
```

Expected: at least two matches (the skill name reference and the tool path).

- [ ] **Step 4: Commit**

```bash
git add .claude/skills/script-writer/SKILL.md
git commit -m "feat(script-writer): hand off to voiceover-elevenlabs skill at done condition"
```

---

## Task 14: Update CLAUDE.md to surface the new skill

**Files:**
- Modify: `CLAUDE.md` at repo root

- [ ] **Step 1: Read the relevant section of CLAUDE.md**

```bash
grep -n "hyperframes-media" /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/CLAUDE.md
```

Find the section that lists project skills. The skill list lives in the "Authoring workflow" section (around the `.claude/skills/` enumeration).

- [ ] **Step 2: Add `voiceover-elevenlabs` to the skill list**

Find the line that lists installed skills (something like "The full skill set lives under `.claude/skills/` — `hyperframes`, `hyperframes-cli`, `hyperframes-media`, ...") and add `voiceover-elevenlabs` to it.

Use the Edit tool. The exact existing text and replacement depend on the current file — read it first, then make a minimal targeted edit that adds `voiceover-elevenlabs` to the enumeration.

- [ ] **Step 3: Verify the edit**

```bash
grep -n "voiceover-elevenlabs" /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/CLAUDE.md
```

Expected: at least one match.

- [ ] **Step 4: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(claude.md): list voiceover-elevenlabs in project skill set"
```

---

## Task 15: Final verification

- [ ] **Step 1: Run the full test suite**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/voiceover-elevenlabs && uv run pytest tests/ -v
```

Expected: all tests across all four test modules PASS. No skips, no warnings beyond known SDK deprecations.

- [ ] **Step 2: Verify the CLI is callable from a clean shell**

```bash
cd /tmp && uv run --project /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/tools/voiceover-elevenlabs voiceover-elevenlabs --help
```

Expected: argparse help prints, exit 0.

- [ ] **Step 3: Verify the skill metadata is loadable**

```bash
head -5 /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames/.claude/skills/voiceover-elevenlabs/SKILL.md
```

Expected: starts with `---\nname: voiceover-elevenlabs\ndescription: ...`.

- [ ] **Step 4: Verify git log is clean**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames && git log --oneline -15
```

Expected: ~13 commits from this plan, each with a clear message. No "WIP" or "fix" commits.

- [ ] **Step 5: Tell the user the work is complete**

Report what was built, list the commits, and tell them the next-best-thing is to actually use the skill on a new video. Don't claim "tested end-to-end with the real API" unless Task 11 actually ran with real credits (i.e., the user explicitly approved the real-API run in Step 3 of Task 11).

---

## Self-review notes

- **Spec coverage**: every section of the spec maps to one or more tasks.
  §3 (inputs/outputs) → Tasks 7, 8. §4 (architecture) → file structure
  pre-task and Tasks 1–8. §5 (CLI surface) → Task 8. §6 (tool internals)
  → Tasks 3–8. §7 (skill flow) → Task 12. §8 (annotation taxonomy) →
  Task 12 (in SKILL.md §3). §9 (script-writer handoff) → Task 13.
  §10 (cost handling) → Task 8 (CLI dry-run) and Task 12 (skill checkpoint).
  §11 (out-of-scope) → not implemented (correctly).
- **No placeholders**: every step has either runnable commands, complete
  code, or explicit verification text. The "depends on Task 2 findings"
  notes are explicit dependencies, not TBDs.
- **Type consistency**: `to_transcript`, `synthesize`, `transcribe`,
  `generate` are the four public functions and their signatures match
  across the test files and implementation files.
