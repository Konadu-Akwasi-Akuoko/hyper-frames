"""CLI entry-point tests."""
from pathlib import Path
from unittest.mock import patch

from voiceover_elevenlabs_v3.cli import build_parser, main


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

    with (
        patch.dict("os.environ", {"ELEVENLABS_API_KEY": "sk_test"}, clear=True),
        patch("voiceover_elevenlabs_v3.cli.load_dotenv"),
    ):
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
        patch("voiceover_elevenlabs_v3.cli.load_dotenv"),
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
        patch("voiceover_elevenlabs_v3.cli.load_dotenv"),
        patch("voiceover_elevenlabs_v3.cli.generate") as mock_generate,
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
