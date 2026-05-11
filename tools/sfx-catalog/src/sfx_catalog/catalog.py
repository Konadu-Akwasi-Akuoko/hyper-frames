"""Catalog builder pipeline: scan, hash, measure, serialize."""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable

AUDIO_EXTENSIONS = {".wav", ".mp3"}


def scan_audio_files(root: Path) -> Iterable[Path]:
    """Yield every audio file under `root`, sorted, in path order."""
    if not root.exists():
        return
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS:
            yield path


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    """Stream a SHA-256 over the file in 1 MiB chunks."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()
