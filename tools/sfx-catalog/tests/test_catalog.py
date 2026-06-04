"""Tests for sfx_catalog.catalog scanning + hashing."""
from __future__ import annotations

from pathlib import Path

from sfx_catalog.catalog import (
    build_catalog,
    build_entry,
    dump_yaml,
    library_digest,
    load_yaml,
    scan_audio_files,
    sha256_file,
)


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


def test_build_entry_for_impulse(library_dir: Path) -> None:
    path = library_dir / "Mister Horse " / " Click" / "click-01.wav"
    entry = build_entry(path, root=library_dir)
    assert entry.path == "Mister Horse / Click/click-01.wav"
    assert entry.library == "Mister Horse "
    assert entry.category == " Click"
    assert entry.format == "wav"
    assert entry.duration_s > 0
    assert entry.peak_time_s > 0
    assert "click" in entry.tags
    assert entry.auto_role in ("accent", "impact")
    assert len(entry.sha256) == 64


def test_library_digest_is_stable_across_runs(library_dir: Path) -> None:
    a = library_digest(library_dir)
    b = library_digest(library_dir)
    assert a == b


def test_build_catalog_includes_all_assets_and_cues(library_dir: Path) -> None:
    cat = build_catalog(library_dir)
    assert cat.version == 1
    assert len(cat.assets) == 3
    assert {"ui-tick", "whoosh", "boom", "riser", "pop", "msg-ding", "snap"} <= set(cat.cues.keys())


def test_incremental_short_circuits_unchanged_files(library_dir: Path) -> None:
    first = build_catalog(library_dir)
    second = build_catalog(library_dir, previous=first)
    for path, entry in second.assets.items():
        assert entry.sha256 == first.assets[path].sha256


def test_dump_then_load_roundtrip(library_dir: Path, tmp_path: Path) -> None:
    cat = build_catalog(library_dir)
    out = tmp_path / "sfx-catalog.yml"
    dump_yaml(cat, out)
    loaded = load_yaml(out)
    assert loaded.version == cat.version
    assert loaded.library_sha == cat.library_sha
    assert set(loaded.assets.keys()) == set(cat.assets.keys())
    assert set(loaded.cues.keys()) == set(cat.cues.keys())


def test_dumped_yaml_has_stable_top_level_order(library_dir: Path, tmp_path: Path) -> None:
    cat = build_catalog(library_dir)
    out = tmp_path / "sfx-catalog.yml"
    dump_yaml(cat, out)
    text = out.read_text(encoding="utf-8")
    lines = [line for line in text.splitlines() if line and not line.startswith(" ")]
    keys = [line.split(":", 1)[0] for line in lines if ":" in line]
    assert keys[:5] == ["version", "generated_at", "library_sha", "assets", "cues"]
