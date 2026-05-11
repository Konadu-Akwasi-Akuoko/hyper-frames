"""Tests for sfx_catalog.catalog scanning + hashing."""
from __future__ import annotations

from pathlib import Path

from sfx_catalog.catalog import scan_audio_files, sha256_file


def test_scan_finds_wav_and_mp3_recursively(library_dir: Path) -> None:
    found = sorted(scan_audio_files(library_dir))
    rel = [p.relative_to(library_dir).as_posix() for p in found]
    assert rel == [
        "Mister Horse / Click/click-01.wav",
        "Whooshes/swell-01.wav",
        "Whooshes/tone-01.wav",
    ]


def test_scan_ignores_non_audio_files(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("not audio")
    (tmp_path / "track.wav").write_bytes(b"RIFF\x00\x00\x00\x00WAVE")
    found = list(scan_audio_files(tmp_path))
    assert len(found) == 1
    assert found[0].name == "track.wav"


def test_sha256_is_stable_for_same_bytes(tmp_path: Path) -> None:
    p = tmp_path / "a.bin"
    p.write_bytes(b"hello world")
    h1 = sha256_file(p)
    h2 = sha256_file(p)
    assert h1 == h2
    assert len(h1) == 64
