"""Unit tests for the v2 CLI."""
from pathlib import Path
from unittest.mock import patch

from voiceover_elevenlabs_v2.cli import build_parser, main


def test_parser_v2_defaults():
    parser = build_parser()
    args = parser.parse_args(["voiceover.txt"])
    assert args.input_path == Path("voiceover.txt")
    assert args.output_audio == Path("audio/voiceover.mp3")
    assert args.output_transcript == Path("transcript.json")
    assert args.voice_id == "IRHApOXLvnW57QJPQH2P"
    assert args.model == "eleven_multilingual_v2"
    assert args.stability == 0.4
    assert args.similarity_boost == 0.75
    assert args.style == 0.35
    assert args.use_speaker_boost is True
    assert args.language_code == "en"
    assert args.generate_transcript is True
    assert args.dry_run is False


def test_dry_run_prints_estimate_and_skips_api(tmp_path, capsys):
    txt = tmp_path / "voiceover.txt"
    txt.write_text("x" * 1000)  # 1000 chars

    with patch("voiceover_elevenlabs_v2.cli.generate") as mock_gen:
        rc = main([str(txt), "--dry-run"])

    assert rc == 0
    mock_gen.assert_not_called()
    out = capsys.readouterr().out
    assert "1000 characters" in out
    assert "v2 TTS" in out


def test_missing_input_returns_2(tmp_path, capsys):
    rc = main([str(tmp_path / "nope.txt")])
    assert rc == 2
    err = capsys.readouterr().err
    assert "not found" in err.lower()


def test_missing_api_key_returns_2(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    txt = tmp_path / "voiceover.txt"
    txt.write_text("hi")

    with patch("voiceover_elevenlabs_v2.cli.load_dotenv"):
        rc = main([str(txt)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "ELEVENLABS_API_KEY" in err


def test_input_over_10k_returns_2_before_api(tmp_path, capsys, monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk_test")
    txt = tmp_path / "voiceover.txt"
    txt.write_text("x" * 10_001)

    with patch("voiceover_elevenlabs_v2.cli.generate") as mock_gen, \
         patch("voiceover_elevenlabs_v2.cli.load_dotenv"):
        rc = main([str(txt)])

    assert rc == 2
    mock_gen.assert_not_called()
    err = capsys.readouterr().err
    assert "10,000" in err or "10000" in err
    assert "split" in err.lower()


def test_main_invokes_generate_with_v2_kwargs(tmp_path, monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk_test")
    txt = tmp_path / "voiceover.txt"
    txt.write_text("hello world")

    with patch("voiceover_elevenlabs_v2.cli.generate") as mock_gen, \
         patch("voiceover_elevenlabs_v2.cli.load_dotenv"):
        rc = main([str(txt), "-o", str(tmp_path / "a.mp3"),
                   "--output-transcript", str(tmp_path / "t.json")])

    assert rc == 0
    kwargs = mock_gen.call_args.kwargs
    assert kwargs["text_path"] == txt
    assert kwargs["audio_path"] == tmp_path / "a.mp3"
    assert kwargs["transcript_path"] == tmp_path / "t.json"
    assert kwargs["voice_id"] == "IRHApOXLvnW57QJPQH2P"
    assert kwargs["api_key"] == "sk_test"
    assert kwargs["model_id"] == "eleven_multilingual_v2"
    assert kwargs["stability"] == 0.4
    assert kwargs["style"] == 0.35
    assert kwargs["language_code"] == "en"


def test_no_speaker_boost_flag(tmp_path, monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "sk_test")
    txt = tmp_path / "voiceover.txt"
    txt.write_text("hi")

    with patch("voiceover_elevenlabs_v2.cli.generate") as mock_gen, \
         patch("voiceover_elevenlabs_v2.cli.load_dotenv"):
        main([str(txt), "--no-use-speaker-boost"])

    assert mock_gen.call_args.kwargs["use_speaker_boost"] is False
