"""Catalog builder pipeline: scan, hash, measure, serialize."""
from __future__ import annotations

import hashlib
import sys
from datetime import datetime, timezone
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


import yaml

from sfx_catalog.core import Catalog, CatalogEntry, CueRecipe
from sfx_catalog.cues import default_cues
from sfx_catalog.metrics import (
    basic_metadata,
    brightness_for,
    measure_envelope_times,
    measure_lufs,
    measure_peak,
    measure_rms,
    measure_spectral,
)
from sfx_catalog.tagging import derive_auto_role, derive_tags


def build_entry(path: Path, root: Path) -> CatalogEntry:
    """Measure one audio file and return its CatalogEntry."""
    rel = path.relative_to(root).as_posix()
    parts = rel.split("/")
    library = parts[0] if parts else ""
    category = parts[-2] if len(parts) >= 2 else library

    basic = basic_metadata(path)
    peak_dbfs, peak_time_s = measure_peak(path)
    rms_dbfs = measure_rms(path)
    integrated_lufs = measure_lufs(path)
    onset_time_s, attack_time_s, tail_time_s = measure_envelope_times(path)
    spectral = measure_spectral(path)
    brightness = brightness_for(spectral["spectral_centroid_hz"])
    tags = derive_tags(
        rel_path=rel,
        duration_s=basic["duration_s"],
        attack_time_s=attack_time_s,
        brightness=brightness,
    )
    auto_role = derive_auto_role(
        category=category,
        duration_s=basic["duration_s"],
        attack_time_s=attack_time_s,
        low_energy_pct=spectral["low_energy_pct"],
        peak_time_s=peak_time_s,
    )

    return CatalogEntry(
        path=rel,
        library=library,
        category=category,
        duration_s=round(basic["duration_s"], 4),
        sample_rate=basic["sample_rate"],
        channels=basic["channels"],
        format=basic["format"],
        bit_depth=basic["bit_depth"],
        sha256=sha256_file(path),
        peak_dbfs=round(peak_dbfs, 2),
        peak_time_s=round(peak_time_s, 4),
        integrated_lufs=round(integrated_lufs, 2) if integrated_lufs != float("-inf") else -999.0,
        rms_dbfs=round(rms_dbfs, 2),
        onset_time_s=round(onset_time_s, 4),
        attack_time_s=round(attack_time_s, 4),
        tail_time_s=round(tail_time_s, 4),
        spectral_centroid_hz=round(spectral["spectral_centroid_hz"], 1),
        brightness=brightness,
        low_energy_pct=spectral["low_energy_pct"],
        mid_energy_pct=spectral["mid_energy_pct"],
        high_energy_pct=spectral["high_energy_pct"],
        tags=tags,
        auto_role=auto_role,
    )


CATALOG_VERSION = 1


def library_digest(root: Path) -> str:
    """SHA-256 over the sorted (path, sha256) pairs in `root`. Stable across runs."""
    h = hashlib.sha256()
    for path in scan_audio_files(root):
        rel = path.relative_to(root).as_posix().encode("utf-8")
        file_sha = sha256_file(path).encode("ascii")
        h.update(rel)
        h.update(b"\x00")
        h.update(file_sha)
        h.update(b"\n")
    return h.hexdigest()


def build_catalog(
    root: Path,
    *,
    previous: Catalog | None = None,
) -> Catalog:
    """Walk `root`, build a Catalog. Reuses entries from `previous` whose sha matches."""
    prev_assets = previous.assets if previous else {}
    assets: dict[str, CatalogEntry] = {}
    for path in scan_audio_files(root):
        rel = path.relative_to(root).as_posix()
        sha = sha256_file(path)
        cached = prev_assets.get(rel)
        if cached is not None and cached.sha256 == sha:
            assets[rel] = cached
            continue
        try:
            assets[rel] = build_entry(path, root=root)
        except Exception as exc:
            print(f"warning: skipping {rel} ({exc.__class__.__name__}: {exc})", file=sys.stderr)
            continue

    return Catalog(
        version=CATALOG_VERSION,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        library_sha=library_digest(root),
        assets=assets,
        cues=default_cues(),
    )


def _catalog_to_dict(cat: Catalog) -> dict[str, object]:
    return {
        "version": cat.version,
        "generated_at": cat.generated_at,
        "library_sha": cat.library_sha,
        "assets": {path: entry.to_dict() for path, entry in cat.assets.items()},
        "cues": {name: cue.to_dict() for name, cue in cat.cues.items()},
    }


def dump_yaml(cat: Catalog, path: Path) -> None:
    """Write `cat` to `path` as YAML with stable, human-readable ordering."""
    data = _catalog_to_dict(cat)
    path.write_text(
        yaml.safe_dump(
            data,
            sort_keys=False,
            allow_unicode=True,
            default_flow_style=False,
            width=120,
        ),
        encoding="utf-8",
    )


def load_yaml(path: Path) -> Catalog:
    """Read a sfx-catalog.yml file back into a Catalog instance."""
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw.get("version") != CATALOG_VERSION:
        raise ValueError(
            f"sfx-catalog.yml version {raw.get('version')!r} does not match "
            f"sfx-catalog version {CATALOG_VERSION}. Rebuild required."
        )
    assets = {
        rel: CatalogEntry(
            path=rel,
            tags=tuple(d.get("tags", [])),
            **{k: v for k, v in d.items() if k not in ("path", "tags")},
        )
        for rel, d in (raw.get("assets") or {}).items()
    }
    cues = {
        name: CueRecipe(name=name, **d)
        for name, d in (raw.get("cues") or {}).items()
    }
    return Catalog(
        version=raw["version"],
        generated_at=raw["generated_at"],
        library_sha=raw["library_sha"],
        assets=assets,
        cues=cues,
    )
