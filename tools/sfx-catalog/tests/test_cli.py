"""Smoke tests for the sfx-catalog CLI."""
from __future__ import annotations

from pathlib import Path

from sfx_catalog.cli import main


def test_cli_writes_catalog_yml(library_dir: Path, capsys) -> None:
    out = library_dir / "sfx-catalog.yml"
    rc = main([str(library_dir), "-o", str(out)])
    assert rc == 0
    assert out.exists()
    captured = capsys.readouterr()
    assert "3 assets" in captured.out


def test_cli_dry_run_does_not_write(library_dir: Path, capsys) -> None:
    out = library_dir / "sfx-catalog.yml"
    rc = main([str(library_dir), "-o", str(out), "--dry-run"])
    assert rc == 0
    assert not out.exists()


def test_cli_report_flag_prints_summary(library_dir: Path, capsys) -> None:
    out = library_dir / "sfx-catalog.yml"
    rc = main([str(library_dir), "-o", str(out), "--report"])
    assert rc == 0
    captured = capsys.readouterr()
    assert "By role" in captured.out
    assert "By brightness" in captured.out
