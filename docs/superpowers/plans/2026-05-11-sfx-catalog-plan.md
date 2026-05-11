# tools/sfx-catalog Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `uv`-managed Python CLI that scans `sound-effects/` and emits `sound-effects/sfx-catalog.yml` — a rich per-asset metadata index plus named-cue recipes — used by `tools/sfx-plan` (Plan 2) for deterministic, peak-aligned SFX placement.

**Architecture:** A small library + CLI mirroring `tools/narration-map/`'s shape (`src/sfx_catalog/{core,metrics,catalog,cli}.py`). Audio analysis uses `librosa` (loading, spectral analysis, onset) + `pyloudnorm` (LUFS) + `numpy` (peak/RMS). Incremental rebuild via SHA-256 short-circuit. YAML output is plain PyYAML with a custom safe dumper for stable key ordering.

**Tech Stack:** Python ≥3.12, `uv` build system, `librosa`, `soundfile`, `pyloudnorm`, `numpy`, `PyYAML`, `pytest` (dev).

**Source spec:** `docs/superpowers/specs/2026-05-11-sfx-pipeline-design.md` (Component 1).

## File structure

```
tools/sfx-catalog/
├── pyproject.toml
├── README.md
├── src/sfx_catalog/
│   ├── __init__.py
│   ├── core.py          # dataclasses + types (CatalogEntry, CueRecipe, Catalog)
│   ├── metrics.py       # per-asset audio analysis (peak, LUFS, spectral, etc.)
│   ├── catalog.py       # builder pipeline (scan, hash, incremental, serialize)
│   ├── tagging.py       # auto-tags + auto_role derivation
│   ├── cues.py          # default cue recipe definitions
│   └── cli.py           # argparse entry point
└── tests/
    ├── conftest.py      # synthetic-WAV pytest fixtures
    ├── test_metrics.py
    ├── test_tagging.py
    ├── test_catalog.py
    └── test_cli.py
```

Output written by the CLI lives at `sound-effects/sfx-catalog.yml` (repo-relative, committed to git).

---

### Task 1: Scaffold the `uv` project

**Files:**
- Create: `tools/sfx-catalog/pyproject.toml`
- Create: `tools/sfx-catalog/src/sfx_catalog/__init__.py` (empty)
- Create: `tools/sfx-catalog/README.md` (one-liner; we expand later)

- [ ] **Step 1: Create the directory and pyproject.toml**

```bash
mkdir -p tools/sfx-catalog/src/sfx_catalog tools/sfx-catalog/tests
```

Write `tools/sfx-catalog/pyproject.toml`:

```toml
[project]
name = "sfx-catalog"
version = "0.1.0"
description = "Scan sound-effects/ and emit sfx-catalog.yml — per-asset metadata + named cue recipes for the HyperFrames SFX pipeline."
readme = "README.md"
requires-python = ">=3.12"
authors = [
    { name = "Akwasi Konadu Akuoko", email = "akwasikonadueverlasting@gmail.com" }
]
dependencies = [
    "librosa>=0.10.2",
    "soundfile>=0.12.1",
    "pyloudnorm>=0.1.1",
    "numpy>=1.26",
    "PyYAML>=6.0.1",
]

[project.scripts]
sfx-catalog = "sfx_catalog.cli:main"

[build-system]
requires = ["uv_build>=0.11.10,<0.12.0"]
build-backend = "uv_build"

[tool.pyright]
venvPath = "."
venv = ".venv"
extraPaths = ["src"]

[dependency-groups]
dev = [
    "pytest>=8.2",
]
```

Write `tools/sfx-catalog/README.md`:

```markdown
# sfx-catalog

Scan `sound-effects/` and emit `sound-effects/sfx-catalog.yml` — per-asset metadata (duration, peak, LUFS, spectral character) and named cue recipes (`ui-tick`, `whoosh`, `boom`, `riser`, `pop`) used by `tools/sfx-plan`.

## Usage

```bash
uv run --project tools/sfx-catalog sfx-catalog
```

Flags: `--force` (ignore sha cache), `--dry-run`, `--report`.

See `docs/superpowers/specs/2026-05-11-sfx-pipeline-design.md` for the schema.
```

Write `tools/sfx-catalog/src/sfx_catalog/__init__.py`:

```python
"""sfx-catalog — rich per-asset metadata index for HyperFrames SFX placement."""
```

- [ ] **Step 2: Bootstrap and verify**

Run:
```bash
cd tools/sfx-catalog && uv sync
```

Expected: lockfile generated, all deps installed cleanly. Verify with:
```bash
uv run python -c "import librosa, soundfile, pyloudnorm, numpy, yaml; print('ok')"
```
Expected output: `ok`

- [ ] **Step 3: Commit**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames
git add tools/sfx-catalog/pyproject.toml tools/sfx-catalog/uv.lock tools/sfx-catalog/README.md tools/sfx-catalog/src/sfx_catalog/__init__.py
git commit -m "chore(sfx-catalog): scaffold uv project"
```

---

### Task 2: Synthetic-WAV test fixtures (`conftest.py`)

**Files:**
- Create: `tools/sfx-catalog/tests/__init__.py` (empty)
- Create: `tools/sfx-catalog/tests/conftest.py`

The catalog needs deterministic test inputs. We generate WAVs at test time rather than checking binaries into git.

- [ ] **Step 1: Write the fixture module**

Write `tools/sfx-catalog/tests/conftest.py`:

```python
"""Synthetic-WAV fixtures for sfx-catalog tests."""
from __future__ import annotations

from pathlib import Path
import math

import numpy as np
import pytest
import soundfile as sf

SR = 48000


def _write_wav(path: Path, samples: np.ndarray, sr: int = SR) -> Path:
    sf.write(path, samples.astype(np.float32), sr, subtype="PCM_24")
    return path


@pytest.fixture
def impulse_wav(tmp_path: Path) -> Path:
    """0.5s of silence with a single +0.8 spike at t=0.083s."""
    n = int(0.5 * SR)
    samples = np.zeros(n, dtype=np.float32)
    spike_idx = int(0.083 * SR)
    samples[spike_idx] = 0.8
    return _write_wav(tmp_path / "impulse.wav", samples)


@pytest.fixture
def sine_1k_wav(tmp_path: Path) -> Path:
    """3s of 1kHz sine at −20 dBFS peak, mono."""
    duration_s = 3.0
    t = np.arange(int(duration_s * SR)) / SR
    samples = 0.1 * np.sin(2 * math.pi * 1000 * t)  # −20 dBFS peak
    return _write_wav(tmp_path / "sine_1k.wav", samples)


@pytest.fixture
def sine_4k_wav(tmp_path: Path) -> Path:
    """3s of 4kHz sine at −20 dBFS peak."""
    duration_s = 3.0
    t = np.arange(int(duration_s * SR)) / SR
    samples = 0.1 * np.sin(2 * math.pi * 4000 * t)
    return _write_wav(tmp_path / "sine_4k.wav", samples)


@pytest.fixture
def swell_wav(tmp_path: Path) -> Path:
    """1s tone with a slow attack — peaks at t=0.7s. Used for attack-time tests."""
    n = int(1.0 * SR)
    t = np.arange(n) / SR
    envelope = np.minimum(t / 0.7, 1.0) * np.exp(-3.0 * np.maximum(t - 0.7, 0))
    samples = (0.6 * envelope * np.sin(2 * math.pi * 800 * t)).astype(np.float32)
    return _write_wav(tmp_path / "swell.wav", samples)


@pytest.fixture
def library_dir(tmp_path: Path, impulse_wav, sine_1k_wav, swell_wav) -> Path:
    """A miniature sound-effects/ tree with three categorized files."""
    root = tmp_path / "lib"
    (root / "Whooshes").mkdir(parents=True)
    (root / "Mister Horse / Click").mkdir(parents=True)
    # Move the fixture files into the library structure.
    (root / "Mister Horse / Click" / "click-01.wav").write_bytes(impulse_wav.read_bytes())
    (root / "Whooshes" / "swell-01.wav").write_bytes(swell_wav.read_bytes())
    (root / "Whooshes" / "tone-01.wav").write_bytes(sine_1k_wav.read_bytes())
    return root
```

Also create the empty `tests/__init__.py`:
```bash
touch tools/sfx-catalog/tests/__init__.py
```

- [ ] **Step 2: Verify fixtures load**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/conftest.py --collect-only -q
```

Expected: 0 tests collected, no import errors.

- [ ] **Step 3: Commit**

```bash
git add tools/sfx-catalog/tests/conftest.py tools/sfx-catalog/tests/__init__.py
git commit -m "test(sfx-catalog): add synthetic-WAV fixtures"
```

---

### Task 3: Core dataclasses (`core.py`)

**Files:**
- Create: `tools/sfx-catalog/src/sfx_catalog/core.py`
- Create: `tools/sfx-catalog/tests/test_core.py`

Define the data shapes the rest of the package uses. Frozen dataclasses, no business logic.

- [ ] **Step 1: Write the failing test**

Write `tools/sfx-catalog/tests/test_core.py`:

```python
"""Tests for sfx_catalog.core dataclasses."""
from __future__ import annotations

from sfx_catalog.core import CatalogEntry, CueRecipe, Catalog


def test_catalog_entry_roundtrips_to_dict():
    entry = CatalogEntry(
        path="Whooshes/swell-01.wav",
        library="Whooshes",
        category="Whooshes",
        duration_s=1.0,
        sample_rate=48000,
        channels=1,
        format="wav",
        bit_depth=24,
        sha256="abc",
        peak_dbfs=-4.4,
        peak_time_s=0.7,
        integrated_lufs=-18.2,
        rms_dbfs=-22.0,
        onset_time_s=0.0,
        attack_time_s=0.7,
        tail_time_s=0.25,
        spectral_centroid_hz=820.0,
        brightness="dark",
        low_energy_pct=70,
        mid_energy_pct=25,
        high_energy_pct=5,
        tags=("whoosh", "swell"),
        auto_role="transition",
    )
    d = entry.to_dict()
    assert d["path"] == "Whooshes/swell-01.wav"
    assert d["tags"] == ["whoosh", "swell"]
    assert d["auto_role"] == "transition"


def test_cue_recipe_filter_defaults_to_empty():
    cue = CueRecipe(name="boom", default_lead_ms=0, default_volume=1.0)
    assert cue.filter == {}


def test_catalog_holds_entries_keyed_by_path():
    entry = CatalogEntry(
        path="x.wav", library="X", category="X", duration_s=0.1,
        sample_rate=48000, channels=1, format="wav", bit_depth=24,
        sha256="z", peak_dbfs=-1.0, peak_time_s=0.05,
        integrated_lufs=-14.0, rms_dbfs=-18.0,
        onset_time_s=0.0, attack_time_s=0.05, tail_time_s=0.05,
        spectral_centroid_hz=3000.0, brightness="bright",
        low_energy_pct=10, mid_energy_pct=40, high_energy_pct=50,
        tags=(), auto_role="accent",
    )
    cat = Catalog(version=1, generated_at="2026-05-11T00:00:00Z",
                  library_sha="lib-sha", assets={"x.wav": entry}, cues={})
    assert cat.assets["x.wav"].path == "x.wav"
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_core.py -v
```

Expected: FAIL with `ModuleNotFoundError` or `ImportError` (core module not implemented).

- [ ] **Step 3: Write the core dataclasses**

Write `tools/sfx-catalog/src/sfx_catalog/core.py`:

```python
"""Catalog data shapes."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


Brightness = str  # one of: "dark", "warm", "bright", "airy"
AutoRole = str    # one of: "transition", "accent", "impact", "riser", "ambience", "foley"


@dataclass(frozen=True)
class CatalogEntry:
    """One audio asset's full metadata, as stored under `assets:` in sfx-catalog.yml."""

    path: str
    library: str
    category: str
    duration_s: float
    sample_rate: int
    channels: int
    format: str
    bit_depth: int | None
    sha256: str
    peak_dbfs: float
    peak_time_s: float
    integrated_lufs: float
    rms_dbfs: float
    onset_time_s: float
    attack_time_s: float
    tail_time_s: float
    spectral_centroid_hz: float
    brightness: Brightness
    low_energy_pct: int
    mid_energy_pct: int
    high_energy_pct: int
    tags: tuple[str, ...]
    auto_role: AutoRole

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["tags"] = list(self.tags)
        return d


@dataclass(frozen=True)
class CueRecipe:
    """Named cue, with a filter applied against catalog entries to find candidates."""

    name: str
    default_lead_ms: int | None
    default_volume: float
    filter: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "filter": dict(self.filter),
            "default_lead_ms": self.default_lead_ms,
            "default_volume": self.default_volume,
        }


@dataclass(frozen=True)
class Catalog:
    """Top-level catalog: metadata + assets + cues."""

    version: int
    generated_at: str
    library_sha: str
    assets: dict[str, CatalogEntry]
    cues: dict[str, CueRecipe]
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_core.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-catalog/src/sfx_catalog/core.py tools/sfx-catalog/tests/test_core.py
git commit -m "feat(sfx-catalog): core dataclasses for catalog entries and cues"
```

---

### Task 4: File scanner + SHA-256 hashing

**Files:**
- Create: `tools/sfx-catalog/src/sfx_catalog/catalog.py` (start it; expand in later tasks)
- Modify: `tools/sfx-catalog/tests/test_catalog.py` (new file)

- [ ] **Step 1: Write the failing tests**

Write `tools/sfx-catalog/tests/test_catalog.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_catalog.py -v
```

Expected: FAIL — `catalog` module not implemented.

- [ ] **Step 3: Implement scan + hash**

Write `tools/sfx-catalog/src/sfx_catalog/catalog.py`:

```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_catalog.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-catalog/src/sfx_catalog/catalog.py tools/sfx-catalog/tests/test_catalog.py
git commit -m "feat(sfx-catalog): recursive audio file scan + sha256 hashing"
```

---

### Task 5: Basic audio metadata (`metrics.basic_metadata`)

**Files:**
- Create: `tools/sfx-catalog/src/sfx_catalog/metrics.py`
- Create: `tools/sfx-catalog/tests/test_metrics.py`

- [ ] **Step 1: Write the failing test**

Write `tools/sfx-catalog/tests/test_metrics.py`:

```python
"""Tests for sfx_catalog.metrics — audio analysis primitives."""
from __future__ import annotations

import math
from pathlib import Path

from sfx_catalog.metrics import basic_metadata


def test_basic_metadata_reports_duration_and_format(sine_1k_wav: Path) -> None:
    m = basic_metadata(sine_1k_wav)
    assert math.isclose(m["duration_s"], 3.0, rel_tol=0.01)
    assert m["sample_rate"] == 48000
    assert m["channels"] == 1
    assert m["format"] == "wav"
    assert m["bit_depth"] == 24
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_metrics.py::test_basic_metadata_reports_duration_and_format -v
```

Expected: FAIL — `metrics` module not implemented.

- [ ] **Step 3: Implement `basic_metadata`**

Write `tools/sfx-catalog/src/sfx_catalog/metrics.py`:

```python
"""Per-asset audio analysis: peak, LUFS, spectral, onset/attack/tail."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import soundfile as sf

# Maps soundfile subtype strings to nominal bit depths. None for floats / non-PCM.
_SUBTYPE_BIT_DEPTH: dict[str, int | None] = {
    "PCM_S8": 8, "PCM_16": 16, "PCM_24": 24, "PCM_32": 32,
    "PCM_U8": 8, "FLOAT": None, "DOUBLE": None,
    "ALAW": None, "ULAW": None,
}


def basic_metadata(path: Path) -> dict[str, Any]:
    """Return {duration_s, sample_rate, channels, format, bit_depth} for `path`.

    Uses soundfile.info() for wav (cheap header read). For mp3, soundfile lacks
    header-only access on some platforms — fall back to loading samples via
    soundfile.read() if needed.
    """
    suffix = path.suffix.lower().lstrip(".")
    try:
        info = sf.info(path)
        duration_s = info.duration
        sample_rate = info.samplerate
        channels = info.channels
        bit_depth = _SUBTYPE_BIT_DEPTH.get(info.subtype)
    except RuntimeError:
        # Fallback: full read (slower; only hits on mp3 + old libsndfile).
        data, sr = sf.read(path, dtype="float32", always_2d=True)
        duration_s = data.shape[0] / sr
        sample_rate = sr
        channels = data.shape[1]
        bit_depth = None
    return {
        "duration_s": float(duration_s),
        "sample_rate": int(sample_rate),
        "channels": int(channels),
        "format": suffix,
        "bit_depth": bit_depth,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_metrics.py -v
```

Expected: 1 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-catalog/src/sfx_catalog/metrics.py tools/sfx-catalog/tests/test_metrics.py
git commit -m "feat(sfx-catalog): basic audio metadata (duration, sr, channels, format, bit_depth)"
```

---

### Task 6: Peak + RMS measurement

**Files:**
- Modify: `tools/sfx-catalog/src/sfx_catalog/metrics.py`
- Modify: `tools/sfx-catalog/tests/test_metrics.py`

- [ ] **Step 1: Write the failing tests**

Append to `tools/sfx-catalog/tests/test_metrics.py`:

```python
from sfx_catalog.metrics import measure_peak, measure_rms


def test_peak_detection_locates_known_impulse(impulse_wav: Path) -> None:
    peak_dbfs, peak_time_s = measure_peak(impulse_wav)
    assert math.isclose(peak_time_s, 0.083, abs_tol=0.001)
    # 0.8 sample value → 20*log10(0.8) ≈ -1.94 dBFS
    assert math.isclose(peak_dbfs, -1.94, abs_tol=0.05)


def test_rms_of_sine_at_neg20_dbfs(sine_1k_wav: Path) -> None:
    rms_dbfs = measure_rms(sine_1k_wav)
    # Sine peak 0.1 → RMS 0.1/sqrt(2) ≈ 0.0707 → 20*log10(0.0707) ≈ -23.0 dBFS
    assert math.isclose(rms_dbfs, -23.0, abs_tol=0.1)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_metrics.py -v
```

Expected: FAIL — `measure_peak` and `measure_rms` not defined.

- [ ] **Step 3: Implement `measure_peak` and `measure_rms`**

Append to `tools/sfx-catalog/src/sfx_catalog/metrics.py`:

```python
def _load_mono(path: Path) -> tuple[np.ndarray, int]:
    """Load audio as float32 mono, downmixing if needed."""
    data, sr = sf.read(path, dtype="float32", always_2d=True)
    mono = data.mean(axis=1)  # channel-average downmix
    return mono, int(sr)


def measure_peak(path: Path) -> tuple[float, float]:
    """Return (peak_dbfs, peak_time_s) — the absolute peak and its time."""
    mono, sr = _load_mono(path)
    if mono.size == 0:
        return -math.inf, 0.0
    peak_idx = int(np.argmax(np.abs(mono)))
    peak_sample = float(abs(mono[peak_idx]))
    peak_dbfs = 20.0 * math.log10(max(peak_sample, 1e-9))
    peak_time_s = peak_idx / sr
    return peak_dbfs, peak_time_s


def measure_rms(path: Path) -> float:
    """Return integrated RMS in dBFS over the whole file (mono-summed)."""
    mono, _sr = _load_mono(path)
    if mono.size == 0:
        return -math.inf
    rms = float(np.sqrt(np.mean(np.square(mono))))
    return 20.0 * math.log10(max(rms, 1e-9))
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_metrics.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-catalog/src/sfx_catalog/metrics.py tools/sfx-catalog/tests/test_metrics.py
git commit -m "feat(sfx-catalog): peak detection and RMS measurement"
```

---

### Task 7: Integrated LUFS via `pyloudnorm`

**Files:**
- Modify: `tools/sfx-catalog/src/sfx_catalog/metrics.py`
- Modify: `tools/sfx-catalog/tests/test_metrics.py`

- [ ] **Step 1: Write the failing test**

Append to `tools/sfx-catalog/tests/test_metrics.py`:

```python
from sfx_catalog.metrics import measure_lufs


def test_lufs_of_known_sine(sine_1k_wav: Path) -> None:
    # A 1kHz sine at -20 dBFS peak comes out close to -23 LUFS integrated
    # (EBU R128 K-weighting at 1kHz contributes ~0 dB; -20 dBFS sine has
    #  RMS ~-23 dBFS, which matches LUFS within K-weighting tolerance).
    lufs = measure_lufs(sine_1k_wav)
    assert math.isclose(lufs, -23.0, abs_tol=1.0)
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_metrics.py::test_lufs_of_known_sine -v
```

Expected: FAIL — `measure_lufs` not defined.

- [ ] **Step 3: Implement `measure_lufs`**

Append to `tools/sfx-catalog/src/sfx_catalog/metrics.py`:

```python
import pyloudnorm as pyln


def measure_lufs(path: Path) -> float:
    """Integrated loudness in LUFS (EBU R128) of the whole file.

    Returns -inf for clips shorter than ~400ms (BS.1770 gating window).
    """
    data, sr = sf.read(path, dtype="float32", always_2d=True)
    if data.shape[0] < int(0.4 * sr):
        return -math.inf
    # pyloudnorm wants (samples, channels) for stereo or (samples,) for mono.
    audio = data[:, 0] if data.shape[1] == 1 else data
    meter = pyln.Meter(sr)
    return float(meter.integrated_loudness(audio))
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_metrics.py::test_lufs_of_known_sine -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-catalog/src/sfx_catalog/metrics.py tools/sfx-catalog/tests/test_metrics.py
git commit -m "feat(sfx-catalog): integrated LUFS measurement via pyloudnorm"
```

---

### Task 8: Onset, attack, and tail times

**Files:**
- Modify: `tools/sfx-catalog/src/sfx_catalog/metrics.py`
- Modify: `tools/sfx-catalog/tests/test_metrics.py`

- [ ] **Step 1: Write the failing tests**

Append to `tools/sfx-catalog/tests/test_metrics.py`:

```python
from sfx_catalog.metrics import measure_envelope_times


def test_envelope_times_on_impulse(impulse_wav: Path) -> None:
    onset, attack, tail = measure_envelope_times(impulse_wav)
    # Impulse: onset arrives at the spike, attack ~0 (already at peak),
    # tail short (silence after).
    assert math.isclose(onset, 0.083, abs_tol=0.02)
    assert attack < 0.01
    assert tail < 0.05


def test_envelope_times_on_swell(swell_wav: Path) -> None:
    onset, attack, tail = measure_envelope_times(swell_wav)
    # Swell: attack should be substantial (close to 0.7s), tail decays after peak.
    assert 0.4 < attack < 0.9
    assert tail > 0.05
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_metrics.py -v
```

Expected: FAIL — `measure_envelope_times` not defined.

- [ ] **Step 3: Implement `measure_envelope_times`**

Append to `tools/sfx-catalog/src/sfx_catalog/metrics.py`:

```python
def measure_envelope_times(path: Path) -> tuple[float, float, float]:
    """Return (onset_time_s, attack_time_s, tail_time_s).

    - onset_time_s: time at which the signal first crosses 1% of its peak.
    - attack_time_s: peak_time_s − onset_time_s.
    - tail_time_s: time from the peak until the signal envelope (10ms-windowed
      RMS, smoothed) drops below -20 dB relative to peak.
    """
    mono, sr = _load_mono(path)
    if mono.size == 0:
        return 0.0, 0.0, 0.0

    abs_signal = np.abs(mono)
    peak_idx = int(np.argmax(abs_signal))
    peak_val = float(abs_signal[peak_idx])
    if peak_val < 1e-9:
        return 0.0, 0.0, 0.0

    onset_threshold = 0.01 * peak_val
    above = np.where(abs_signal >= onset_threshold)[0]
    onset_idx = int(above[0]) if above.size else 0
    onset_time_s = onset_idx / sr
    peak_time_s = peak_idx / sr
    attack_time_s = max(peak_time_s - onset_time_s, 0.0)

    # Tail: 10ms-window RMS envelope after peak; find first crossing of -20 dB.
    win = max(int(0.010 * sr), 1)
    pad = np.concatenate([np.square(mono), np.zeros(win)])
    csum = np.cumsum(pad)
    window_energy = csum[win:] - csum[:-win]
    rms_env = np.sqrt(np.maximum(window_energy / win, 0.0))
    peak_env = float(rms_env[peak_idx]) if peak_idx < rms_env.size else peak_val
    threshold = 0.1 * peak_env  # -20 dB
    after = rms_env[peak_idx:]
    drop_rel = np.where(after < threshold)[0]
    tail_samples = int(drop_rel[0]) if drop_rel.size else after.size
    tail_time_s = tail_samples / sr
    return onset_time_s, attack_time_s, tail_time_s
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_metrics.py -v
```

Expected: 5 passed total.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-catalog/src/sfx_catalog/metrics.py tools/sfx-catalog/tests/test_metrics.py
git commit -m "feat(sfx-catalog): onset, attack, and tail envelope times"
```

---

### Task 9: Spectral centroid, brightness, band-energy percentages

**Files:**
- Modify: `tools/sfx-catalog/src/sfx_catalog/metrics.py`
- Modify: `tools/sfx-catalog/tests/test_metrics.py`

- [ ] **Step 1: Write the failing tests**

Append to `tools/sfx-catalog/tests/test_metrics.py`:

```python
from sfx_catalog.metrics import measure_spectral, brightness_for


def test_spectral_centroid_near_sine_frequency(sine_1k_wav: Path, sine_4k_wav: Path) -> None:
    s1 = measure_spectral(sine_1k_wav)
    s4 = measure_spectral(sine_4k_wav)
    assert math.isclose(s1["spectral_centroid_hz"], 1000.0, rel_tol=0.1)
    assert math.isclose(s4["spectral_centroid_hz"], 4000.0, rel_tol=0.1)


def test_band_energy_percents_sum_to_100(sine_1k_wav: Path) -> None:
    s = measure_spectral(sine_1k_wav)
    total = s["low_energy_pct"] + s["mid_energy_pct"] + s["high_energy_pct"]
    assert abs(total - 100) <= 1


def test_brightness_buckets_map_centroid_to_enum() -> None:
    assert brightness_for(500.0) == "dark"
    assert brightness_for(2000.0) == "warm"
    assert brightness_for(4500.0) == "bright"
    assert brightness_for(8000.0) == "airy"
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_metrics.py -v
```

Expected: FAIL — `measure_spectral` and `brightness_for` not defined.

- [ ] **Step 3: Implement spectral analysis**

Append to `tools/sfx-catalog/src/sfx_catalog/metrics.py`:

```python
import librosa


def measure_spectral(path: Path) -> dict[str, Any]:
    """Compute spectral centroid (Hz) and energy percentages in three bands.

    Bands: low (<250 Hz), mid (250–2000 Hz), high (>2000 Hz). Percentages
    are rounded to ints summing to ≈100.
    """
    mono, sr = _load_mono(path)
    if mono.size == 0:
        return {
            "spectral_centroid_hz": 0.0,
            "low_energy_pct": 0,
            "mid_energy_pct": 0,
            "high_energy_pct": 0,
        }

    n_fft = min(2048, len(mono))
    if n_fft < 32:
        return {
            "spectral_centroid_hz": 0.0,
            "low_energy_pct": 33, "mid_energy_pct": 34, "high_energy_pct": 33,
        }

    centroid = float(np.mean(librosa.feature.spectral_centroid(y=mono, sr=sr, n_fft=n_fft)))

    spec = np.abs(librosa.stft(mono, n_fft=n_fft, hop_length=n_fft // 4))
    power = np.square(spec).sum(axis=1)  # power per frequency bin
    freqs = librosa.fft_frequencies(sr=sr, n_fft=n_fft)
    total = float(power.sum())
    if total <= 0:
        low = mid = high = 0.0
    else:
        low = float(power[freqs < 250].sum()) / total
        mid = float(power[(freqs >= 250) & (freqs < 2000)].sum()) / total
        high = float(power[freqs >= 2000].sum()) / total

    # Round to ints summing to 100.
    raw = np.array([low, mid, high]) * 100
    rounded = np.round(raw).astype(int)
    drift = 100 - int(rounded.sum())
    if drift != 0:
        idx = int(np.argmax(raw - rounded))
        rounded[idx] += drift
    return {
        "spectral_centroid_hz": centroid,
        "low_energy_pct": int(rounded[0]),
        "mid_energy_pct": int(rounded[1]),
        "high_energy_pct": int(rounded[2]),
    }


def brightness_for(centroid_hz: float) -> str:
    """Map spectral centroid to a coarse brightness enum."""
    if centroid_hz < 1000:
        return "dark"
    if centroid_hz < 3000:
        return "warm"
    if centroid_hz < 6000:
        return "bright"
    return "airy"
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_metrics.py -v
```

Expected: 8 passed total.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-catalog/src/sfx_catalog/metrics.py tools/sfx-catalog/tests/test_metrics.py
git commit -m "feat(sfx-catalog): spectral centroid, brightness enum, band-energy percentages"
```

---

### Task 10: Auto-tagging + auto_role derivation

**Files:**
- Create: `tools/sfx-catalog/src/sfx_catalog/tagging.py`
- Create: `tools/sfx-catalog/tests/test_tagging.py`

- [ ] **Step 1: Write the failing tests**

Write `tools/sfx-catalog/tests/test_tagging.py`:

```python
"""Tests for sfx_catalog.tagging — auto tag and auto_role derivation."""
from __future__ import annotations

from sfx_catalog.tagging import derive_tags, derive_auto_role


def test_tags_include_folder_lineage() -> None:
    tags = derive_tags(
        rel_path="Mister Horse Free SFX/Click/click-bright-01.wav",
        duration_s=0.4,
        attack_time_s=0.04,
        brightness="bright",
    )
    assert "click" in tags
    assert "mister-horse" in tags
    assert "bright" in tags
    assert "short" in tags  # duration < 0.5s


def test_tags_include_snappy_for_fast_attack() -> None:
    tags = derive_tags(
        rel_path="Whooshes/snap.wav",
        duration_s=0.2,
        attack_time_s=0.01,
        brightness="bright",
    )
    assert "snappy" in tags


def test_auto_role_transition_for_whoosh_swell() -> None:
    role = derive_auto_role(
        category="Whooshes",
        duration_s=0.8,
        attack_time_s=0.2,
        low_energy_pct=20,
        peak_time_s=0.5,
    )
    assert role == "transition"


def test_auto_role_impact_for_short_bass_hit() -> None:
    role = derive_auto_role(
        category="Bass",
        duration_s=0.4,
        attack_time_s=0.05,
        low_energy_pct=70,
        peak_time_s=0.1,
    )
    assert role == "impact"


def test_auto_role_accent_for_short_click() -> None:
    role = derive_auto_role(
        category="Click",
        duration_s=0.3,
        attack_time_s=0.02,
        low_energy_pct=10,
        peak_time_s=0.05,
    )
    assert role == "accent"


def test_auto_role_riser_for_long_swell() -> None:
    role = derive_auto_role(
        category="Drone",
        duration_s=2.5,
        attack_time_s=1.8,
        low_energy_pct=40,
        peak_time_s=2.0,
    )
    assert role == "riser"


def test_auto_role_ambience_for_long_low_energy() -> None:
    role = derive_auto_role(
        category="Drone",
        duration_s=8.0,
        attack_time_s=0.2,
        low_energy_pct=60,
        peak_time_s=4.0,
    )
    assert role == "ambience"
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_tagging.py -v
```

Expected: FAIL — `tagging` module not implemented.

- [ ] **Step 3: Implement `tagging`**

Write `tools/sfx-catalog/src/sfx_catalog/tagging.py`:

```python
"""Auto-tagging + auto_role derivation.

These are heuristics — they get the catalog 90% of the way and leave headroom
for hand overrides via per-video sfx-overrides.yml (planned, not built here).
"""
from __future__ import annotations

import re
from pathlib import PurePosixPath

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _slugify(s: str) -> str:
    return _NON_ALNUM.sub("-", s.lower()).strip("-")


def derive_tags(
    rel_path: str,
    duration_s: float,
    attack_time_s: float,
    brightness: str,
) -> tuple[str, ...]:
    """Build a tag tuple from folder lineage + duration + attack + brightness."""
    parts = PurePosixPath(rel_path).parts
    folder_tags: list[str] = []
    if len(parts) >= 2:
        # Top-level library, e.g. "Mister Horse Free SFX" → "mister-horse"
        lib = _slugify(parts[0]).replace("-free-sfx", "").replace("-sfx", "")
        if lib:
            folder_tags.append(lib)
    if len(parts) >= 3:
        # Category, e.g. "Click" → "click"
        cat = _slugify(parts[-2])
        if cat:
            folder_tags.append(cat)

    duration_tag = "short" if duration_s < 0.5 else "long" if duration_s > 1.5 else "medium"
    attack_tag = "snappy" if attack_time_s < 0.05 else "swelling" if attack_time_s > 0.2 else None

    tags = list(dict.fromkeys(folder_tags + [duration_tag, brightness]))
    if attack_tag:
        tags.append(attack_tag)
    return tuple(tags)


def derive_auto_role(
    category: str,
    duration_s: float,
    attack_time_s: float,
    low_energy_pct: int,
    peak_time_s: float,
) -> str:
    """Derive an auto_role from category + envelope + spectral data.

    Priority order:
      ambience > riser > impact > transition > accent > foley
    """
    cat = category.lower()

    # Ambience: long, mostly steady, often dronelike.
    if duration_s >= 5.0:
        return "ambience"

    # Riser: long with a clearly delayed peak (attack > 1s).
    if duration_s >= 1.5 and attack_time_s >= 1.0:
        return "riser"

    # Impact: short, low-frequency-dominated, fast attack near the start.
    if duration_s <= 0.6 and low_energy_pct >= 50 and peak_time_s <= 0.2:
        return "impact"

    # Transition: medium-length with a clear swell (attack > 0.1s).
    if 0.3 <= duration_s <= 2.0 and attack_time_s >= 0.1:
        return "transition"

    # Accent: short, snappy, bright-ish.
    if duration_s < 0.6 and attack_time_s < 0.1:
        return "accent"

    # Foley fallback: anything else (rustles, mid-length textures).
    if any(k in cat for k in ("rustle", "paper", "foley", "crumple")):
        return "foley"

    return "accent"
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_tagging.py -v
```

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-catalog/src/sfx_catalog/tagging.py tools/sfx-catalog/tests/test_tagging.py
git commit -m "feat(sfx-catalog): auto-tag + auto_role heuristics"
```

---

### Task 11: Default cue recipes (`cues.py`)

**Files:**
- Create: `tools/sfx-catalog/src/sfx_catalog/cues.py`
- Create: `tools/sfx-catalog/tests/test_cues.py`

- [ ] **Step 1: Write the failing test**

Write `tools/sfx-catalog/tests/test_cues.py`:

```python
"""Tests for default cue recipes."""
from __future__ import annotations

from sfx_catalog.cues import default_cues


def test_default_cues_includes_required_set() -> None:
    cues = default_cues()
    names = set(cues.keys())
    assert names == {"ui-tick", "whoosh", "boom", "riser", "pop"}


def test_ui_tick_filter_prefers_short_bright_accents() -> None:
    cue = default_cues()["ui-tick"]
    assert cue.filter.get("auto_role") == "accent"
    assert cue.filter.get("duration_s_max") == 0.5
    assert "bright" in cue.filter.get("brightness_in", [])
    assert cue.default_lead_ms == -50


def test_whoosh_filter_targets_transitions() -> None:
    cue = default_cues()["whoosh"]
    assert cue.filter.get("auto_role") == "transition"
    assert cue.default_lead_ms == -150
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_cues.py -v
```

Expected: FAIL — `cues` module not implemented.

- [ ] **Step 3: Implement `default_cues`**

Write `tools/sfx-catalog/src/sfx_catalog/cues.py`:

```python
"""Default cue recipes baked into every catalog.

A cue's filter is a flat dict; each key is a filter operator applied against
CatalogEntry fields. Operators:
  <field>            — exact match
  <field>_min        — entry[field] >= value
  <field>_max        — entry[field] <= value
  <field>_in         — entry[field] in value
"""
from __future__ import annotations

from sfx_catalog.core import CueRecipe


def default_cues() -> dict[str, CueRecipe]:
    return {
        "ui-tick": CueRecipe(
            name="ui-tick",
            default_lead_ms=-50,
            default_volume=0.8,
            filter={
                "auto_role": "accent",
                "duration_s_max": 0.5,
                "brightness_in": ["bright", "airy"],
            },
        ),
        "whoosh": CueRecipe(
            name="whoosh",
            default_lead_ms=-150,
            default_volume=0.9,
            filter={
                "auto_role": "transition",
                "duration_s_min": 0.4,
                "duration_s_max": 1.5,
                "attack_time_s_min": 0.1,
            },
        ),
        "boom": CueRecipe(
            name="boom",
            default_lead_ms=0,
            default_volume=1.0,
            filter={
                "auto_role": "impact",
                "low_energy_pct_min": 50,
                "peak_time_s_max": 0.2,
            },
        ),
        "riser": CueRecipe(
            name="riser",
            default_lead_ms=None,  # null sentinel — tool computes -(duration)
            default_volume=0.85,
            filter={
                "auto_role": "riser",
                "duration_s_min": 1.5,
            },
        ),
        "pop": CueRecipe(
            name="pop",
            default_lead_ms=-50,
            default_volume=0.8,
            filter={
                "auto_role": "accent",
                "duration_s_max": 0.3,
                "brightness_in": ["warm", "bright"],
            },
        ),
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_cues.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-catalog/src/sfx_catalog/cues.py tools/sfx-catalog/tests/test_cues.py
git commit -m "feat(sfx-catalog): default cue recipes (ui-tick, whoosh, boom, riser, pop)"
```

---

### Task 12: Build a single catalog entry from a file

**Files:**
- Modify: `tools/sfx-catalog/src/sfx_catalog/catalog.py`
- Modify: `tools/sfx-catalog/tests/test_catalog.py`

This is the per-file pipeline that stitches together everything from Tasks 5–10.

- [ ] **Step 1: Write the failing test**

Append to `tools/sfx-catalog/tests/test_catalog.py`:

```python
from sfx_catalog.catalog import build_entry


def test_build_entry_for_impulse(library_dir: Path) -> None:
    path = library_dir / "Mister Horse / Click / click-01.wav"
    entry = build_entry(path, root=library_dir)
    assert entry.path == "Mister Horse / Click/click-01.wav"
    assert entry.library == "Mister Horse "
    assert entry.category == "Click "
    assert entry.format == "wav"
    assert entry.duration_s > 0
    assert entry.peak_time_s > 0
    assert "click" in entry.tags
    assert entry.auto_role in ("accent", "impact")
    assert len(entry.sha256) == 64
```

(Note: the fixture intentionally uses folder names like `"Mister Horse / Click"` because that's how the real `sound-effects/` library is structured — spaces in folder names. Tests assert against the verbatim path.)

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_catalog.py::test_build_entry_for_impulse -v
```

Expected: FAIL — `build_entry` not defined.

- [ ] **Step 3: Implement `build_entry`**

Append to `tools/sfx-catalog/src/sfx_catalog/catalog.py`:

```python
from sfx_catalog.core import CatalogEntry
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
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_catalog.py -v
```

Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-catalog/src/sfx_catalog/catalog.py tools/sfx-catalog/tests/test_catalog.py
git commit -m "feat(sfx-catalog): per-file pipeline — build CatalogEntry from path"
```

---

### Task 13: Incremental builder with SHA-256 cache + library digest

**Files:**
- Modify: `tools/sfx-catalog/src/sfx_catalog/catalog.py`
- Modify: `tools/sfx-catalog/tests/test_catalog.py`

The builder must skip files whose `sha256` matches the previous run. It also computes a `library_sha` (a stable digest over `path,sha` pairs) so consumers can detect catalog drift.

- [ ] **Step 1: Write the failing tests**

Append to `tools/sfx-catalog/tests/test_catalog.py`:

```python
from sfx_catalog.catalog import build_catalog, library_digest


def test_library_digest_is_stable_across_runs(library_dir: Path) -> None:
    a = library_digest(library_dir)
    b = library_digest(library_dir)
    assert a == b


def test_build_catalog_includes_all_assets_and_cues(library_dir: Path) -> None:
    cat = build_catalog(library_dir)
    assert cat.version == 1
    assert len(cat.assets) == 3
    assert set(cat.cues.keys()) == {"ui-tick", "whoosh", "boom", "riser", "pop"}


def test_incremental_short_circuits_unchanged_files(library_dir: Path) -> None:
    first = build_catalog(library_dir)
    # Pretend we already have `first` in memory; the incremental call should
    # return the same entries (by sha) without re-measuring.
    second = build_catalog(library_dir, previous=first)
    for path, entry in second.assets.items():
        assert entry.sha256 == first.assets[path].sha256
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_catalog.py -v
```

Expected: FAIL — `build_catalog` and `library_digest` not defined.

- [ ] **Step 3: Implement the builder**

Append to `tools/sfx-catalog/src/sfx_catalog/catalog.py`:

```python
import hashlib
from datetime import datetime, timezone

from sfx_catalog.core import Catalog
from sfx_catalog.cues import default_cues


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
        assets[rel] = build_entry(path, root=root)

    return Catalog(
        version=CATALOG_VERSION,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        library_sha=library_digest(root),
        assets=assets,
        cues=default_cues(),
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_catalog.py -v
```

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-catalog/src/sfx_catalog/catalog.py tools/sfx-catalog/tests/test_catalog.py
git commit -m "feat(sfx-catalog): incremental builder with sha cache + library digest"
```

---

### Task 14: YAML serialization (`catalog.dump_yaml` / `load_yaml`)

**Files:**
- Modify: `tools/sfx-catalog/src/sfx_catalog/catalog.py`
- Modify: `tools/sfx-catalog/tests/test_catalog.py`

- [ ] **Step 1: Write the failing tests**

Append to `tools/sfx-catalog/tests/test_catalog.py`:

```python
from sfx_catalog.catalog import dump_yaml, load_yaml


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
    # Top-level keys in this order: version, generated_at, library_sha, assets, cues.
    keys = [line.split(":", 1)[0] for line in lines if ":" in line]
    assert keys[:5] == ["version", "generated_at", "library_sha", "assets", "cues"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_catalog.py -v
```

Expected: FAIL — `dump_yaml`/`load_yaml` not defined.

- [ ] **Step 3: Implement YAML I/O**

Append to `tools/sfx-catalog/src/sfx_catalog/catalog.py`:

```python
import yaml

from sfx_catalog.core import CueRecipe


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
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_catalog.py -v
```

Expected: 9 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-catalog/src/sfx_catalog/catalog.py tools/sfx-catalog/tests/test_catalog.py
git commit -m "feat(sfx-catalog): yaml serialization + version check on load"
```

---

### Task 15: CLI entry point (`cli.py`)

**Files:**
- Create: `tools/sfx-catalog/src/sfx_catalog/cli.py`
- Create: `tools/sfx-catalog/tests/test_cli.py`

- [ ] **Step 1: Write the failing test**

Write `tools/sfx-catalog/tests/test_cli.py`:

```python
"""Smoke tests for the sfx-catalog CLI."""
from __future__ import annotations

from pathlib import Path

from sfx_catalog.cli import main


def test_cli_writes_catalog_yml(library_dir: Path, capsys, monkeypatch) -> None:
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_cli.py -v
```

Expected: FAIL — `cli.main` not defined.

- [ ] **Step 3: Implement the CLI**

Write `tools/sfx-catalog/src/sfx_catalog/cli.py`:

```python
"""CLI entry point for sfx-catalog."""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys

from sfx_catalog.catalog import build_catalog, dump_yaml, load_yaml
from sfx_catalog.core import Catalog


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sfx-catalog",
        description=(
            "Scan a sound-effects library and emit sfx-catalog.yml — per-asset "
            "metadata + named cue recipes for the HyperFrames SFX pipeline."
        ),
    )
    p.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path("sound-effects"),
        help="Path to the sound-effects/ library root (default: ./sound-effects).",
    )
    p.add_argument(
        "-o", "--output",
        type=Path,
        default=None,
        help="Output path for sfx-catalog.yml (default: <root>/sfx-catalog.yml).",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Ignore sha cache; re-measure every asset.",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Measure everything but do not write the output file.",
    )
    p.add_argument(
        "--report",
        action="store_true",
        help="Print a per-role / per-brightness asset count.",
    )
    return p


def _report(cat: Catalog) -> str:
    role_counter: Counter[str] = Counter(e.auto_role for e in cat.assets.values())
    brightness_counter: Counter[str] = Counter(e.brightness for e in cat.assets.values())
    lib_counter: Counter[str] = Counter(e.library for e in cat.assets.values())
    lines = ["By role:"]
    for k, v in role_counter.most_common():
        lines.append(f"  {k:<12} {v}")
    lines.append("By brightness:")
    for k, v in brightness_counter.most_common():
        lines.append(f"  {k:<12} {v}")
    lines.append("By library:")
    for k, v in lib_counter.most_common():
        lines.append(f"  {k:<24} {v}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    root: Path = args.root
    out: Path = args.output or (root / "sfx-catalog.yml")

    previous: Catalog | None = None
    if out.exists() and not args.force:
        try:
            previous = load_yaml(out)
        except (ValueError, KeyError) as exc:
            print(f"warning: ignoring existing catalog ({exc}); rebuilding from scratch.", file=sys.stderr)

    cat = build_catalog(root, previous=previous)
    print(f"{len(cat.assets)} assets, {len(cat.cues)} cues  (library_sha={cat.library_sha[:12]})")
    if args.report:
        print(_report(cat))
    if not args.dry_run:
        dump_yaml(cat, out)
        print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd tools/sfx-catalog && uv run pytest tests/test_cli.py -v
```

Expected: 3 passed.

- [ ] **Step 5: Run all tests to confirm nothing regressed**

Run:
```bash
cd tools/sfx-catalog && uv run pytest -v
```

Expected: all 25+ tests pass.

- [ ] **Step 6: Commit**

```bash
git add tools/sfx-catalog/src/sfx_catalog/cli.py tools/sfx-catalog/tests/test_cli.py
git commit -m "feat(sfx-catalog): CLI entry point with --force/--dry-run/--report flags"
```

---

### Task 16: Build the real catalog against `sound-effects/` and commit it

**Files:**
- Create: `sound-effects/sfx-catalog.yml` (generated, committed)

- [ ] **Step 1: Run the catalog builder against the real library**

From the repo root:

```bash
uv run --project tools/sfx-catalog sfx-catalog --report
```

Expected:
- Builder runs for ~5–10 minutes on first invocation against the full ~1416 audio files (1357 wav + 59 mp3).
- Output ends with `wrote sound-effects/sfx-catalog.yml`.
- A `--report` summary prints role/brightness/library breakdowns.

If a file fails to decode (rare — e.g. corrupt mp3), the builder must not crash. If it does crash, file an inline fix to catch the exception in `build_entry`, skip the file with a warning, and continue. Re-run.

- [ ] **Step 2: Spot-check the output**

Run:
```bash
head -40 sound-effects/sfx-catalog.yml
```

Expected: first 5 top-level keys are `version`, `generated_at`, `library_sha`, `assets`, `cues` in that order.

Run:
```bash
grep -c '^  ".*":$' sound-effects/sfx-catalog.yml
```

Expected: roughly 1416 (one line per top-level asset key inside `assets:`).

- [ ] **Step 3: Verify incremental re-run is fast and stable**

Run the builder again:
```bash
time uv run --project tools/sfx-catalog sfx-catalog
```

Expected: completes in under 60 seconds (every file matches its previous sha, so every entry is reused). The newly written file should differ from the previous one only on the `generated_at` timestamp.

Confirm with:
```bash
git diff sound-effects/sfx-catalog.yml | head -10
```

Expected: only `generated_at` differs.

- [ ] **Step 4: Commit the catalog**

```bash
git add sound-effects/sfx-catalog.yml
git commit -m "feat(sfx): build initial sfx-catalog.yml from sound-effects/ library"
```

---

## Self-review against the spec

Spec coverage check (Component 1):

- ✅ Schema with `version`, `generated_at`, `library_sha`, `assets:`, `cues:` (Task 14)
- ✅ Per-asset identification & shape (Tasks 5, 12)
- ✅ Loudness & timing — peak, peak_time, LUFS, RMS, onset, attack, tail (Tasks 6, 7, 8, 12)
- ✅ Spectral character — centroid, brightness, band-energy percents (Task 9)
- ✅ Authoring hints — tags, auto_role (Task 10)
- ✅ `cues:` section with default recipes for `ui-tick`, `whoosh`, `boom`, `riser`, `pop` (Task 11)
- ✅ Incremental build via sha256 (Task 13)
- ✅ CLI with `--force` / `--dry-run` / `--report` (Task 15)
- ✅ Catalog committed to git (Task 16)

Placeholder scan: no `TBD`, `TODO`, or "fill in details" left. Every step ships complete code.

Type consistency: `CatalogEntry`, `CueRecipe`, `Catalog` defined in Task 3 and used unchanged in Tasks 12, 13, 14, 15. `brightness` enum values (`dark`/`warm`/`bright`/`airy`) and `auto_role` values (`transition`/`accent`/`impact`/`riser`/`ambience`/`foley`) consistent across tagging, metrics, and tests.

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-11-sfx-catalog-plan.md`. Two execution options:

**1. Subagent-Driven (recommended)** — dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — execute tasks in this session using executing-plans, batch execution with checkpoints.

Plans 2 and 3 (sfx-plan tool, sfx-author skill) are next.
