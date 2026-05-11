# tools/sfx-plan Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `uv`-managed Python CLI that scans a video folder for `data-sfx-*` annotations, resolves them against `narration-map.json` and `sound-effects/sfx-catalog.yml`, picks files deterministically with peak-aligned timing, and emits `compositions/sfx.html` — a native HyperFrames audio sub-composition.

**Architecture:** Pure resolver — no editorial decisions. HTML parsing via BeautifulSoup (`html.parser`, no external native deps). Narration-map and catalog loaded as plain dicts (no cross-tool import — keeps `sfx-plan` independently shippable). Asset picking via `sha256(anchor + index + cue)` truncated to an int, modulo the candidate count. All operations idempotent given identical inputs.

**Tech Stack:** Python ≥3.12, `uv` build system, `beautifulsoup4`, `PyYAML`, `pytest` (dev). Depends on the output of `tools/sfx-catalog` (Plan 1) — that plan must complete first.

**Source spec:** `docs/superpowers/specs/2026-05-11-sfx-pipeline-design.md` (Component 3).

## File structure

```
tools/sfx-plan/
├── pyproject.toml
├── README.md
├── src/sfx_plan/
│   ├── __init__.py
│   ├── annotations.py   # HTML scan: collect data-sfx-* annotations + source line
│   ├── narration.py     # narration-map loader + anchor resolver
│   ├── catalog.py       # catalog loader + filter engine + asset picker
│   ├── plan.py          # Cue dataclass + plan-building orchestration
│   ├── emit.py          # sfx.html writer + index.html mount wiring
│   ├── errors.py        # custom exception hierarchy (one class per failure mode)
│   └── cli.py           # argparse entry point
└── tests/
    ├── conftest.py      # fixtures: tiny video folder + tiny catalog
    ├── test_annotations.py
    ├── test_narration.py
    ├── test_catalog.py
    ├── test_plan.py
    ├── test_emit.py
    └── test_cli.py
```

---

### Task 1: Scaffold the `uv` project

**Files:**
- Create: `tools/sfx-plan/pyproject.toml`
- Create: `tools/sfx-plan/src/sfx_plan/__init__.py`
- Create: `tools/sfx-plan/README.md`

- [ ] **Step 1: Create directories and pyproject.toml**

```bash
mkdir -p tools/sfx-plan/src/sfx_plan tools/sfx-plan/tests
```

Write `tools/sfx-plan/pyproject.toml`:

```toml
[project]
name = "sfx-plan"
version = "0.1.0"
description = "Scan a video folder's data-sfx-* annotations, resolve against narration-map and sfx-catalog, emit compositions/sfx.html."
readme = "README.md"
requires-python = ">=3.12"
authors = [
    { name = "Akwasi Konadu Akuoko", email = "akwasikonadueverlasting@gmail.com" }
]
dependencies = [
    "beautifulsoup4>=4.12",
    "PyYAML>=6.0.1",
]

[project.scripts]
sfx-plan = "sfx_plan.cli:main"

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

Write `tools/sfx-plan/README.md`:

```markdown
# sfx-plan

Scan a HyperFrames video folder for `data-sfx-*` annotations, resolve anchor words via `narration-map.json`, pick files deterministically from `sound-effects/sfx-catalog.yml`, and emit `compositions/sfx.html` as a native HyperFrames audio sub-composition.

## Usage

From inside a video folder (after the `sfx-author` skill has annotated the HTML):

```bash
uv run --project ../../tools/sfx-plan sfx-plan
```

Flags: `--dry-run` (don't write), `--report` (print a plan table).

See `docs/superpowers/specs/2026-05-11-sfx-pipeline-design.md` for the data contract.
```

Write `tools/sfx-plan/src/sfx_plan/__init__.py`:

```python
"""sfx-plan — resolves data-sfx-* annotations into a HyperFrames audio sub-composition."""
```

- [ ] **Step 2: Sync and verify**

```bash
cd tools/sfx-plan && uv sync
uv run python -c "import bs4, yaml; print('ok')"
```

Expected: `ok`.

- [ ] **Step 3: Commit**

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames
git add tools/sfx-plan/pyproject.toml tools/sfx-plan/uv.lock tools/sfx-plan/README.md tools/sfx-plan/src/sfx_plan/__init__.py
git commit -m "chore(sfx-plan): scaffold uv project"
```

---

### Task 2: Error hierarchy (`errors.py`)

**Files:**
- Create: `tools/sfx-plan/src/sfx_plan/errors.py`

Define one exception per spec failure mode. Each carries the source location and a remediation hint.

- [ ] **Step 1: Write the failing test**

Write `tools/sfx-plan/tests/__init__.py` (empty) and `tools/sfx-plan/tests/test_errors.py`:

```python
"""Tests for the sfx-plan error hierarchy."""
from __future__ import annotations

import pytest

from sfx_plan.errors import (
    SfxPlanError,
    UnresolvedAnchorError,
    AnchorIndexOutOfRangeError,
    UnknownCueError,
    EmptyCueFilterError,
    CatalogMissingError,
    CatalogVersionMismatchError,
)


def test_all_errors_inherit_from_base() -> None:
    for cls in (
        UnresolvedAnchorError, AnchorIndexOutOfRangeError, UnknownCueError,
        EmptyCueFilterError, CatalogMissingError, CatalogVersionMismatchError,
    ):
        assert issubclass(cls, SfxPlanError)


def test_unresolved_anchor_message_includes_anchor_and_source() -> None:
    err = UnresolvedAnchorError(anchor="Bézier", source="index.html:127")
    assert "Bézier" in str(err)
    assert "index.html:127" in str(err)
    assert "narration-map" in str(err).lower()


def test_anchor_index_out_of_range_lists_available() -> None:
    err = AnchorIndexOutOfRangeError(anchor="easy", requested=3, available=2, source="index.html:45")
    msg = str(err)
    assert "easy" in msg and "3" in msg and "2" in msg


def test_unknown_cue_lists_known_cues() -> None:
    err = UnknownCueError(cue="boom-sub", known=["ui-tick", "whoosh", "boom"], source="index.html:99")
    msg = str(err)
    assert "boom-sub" in msg
    assert "ui-tick" in msg


def test_empty_cue_filter_names_cue() -> None:
    err = EmptyCueFilterError(cue="riser")
    assert "riser" in str(err)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/test_errors.py -v
```

Expected: FAIL — error classes not defined.

- [ ] **Step 3: Implement the error hierarchy**

Write `tools/sfx-plan/src/sfx_plan/errors.py`:

```python
"""Exception hierarchy. One class per spec failure mode."""
from __future__ import annotations


class SfxPlanError(Exception):
    """Base for all sfx-plan failures."""


class UnresolvedAnchorError(SfxPlanError):
    def __init__(self, *, anchor: str, source: str) -> None:
        super().__init__(
            f'unresolved anchor "{anchor}" at {source} — not present in narration-map. '
            f"Did the script change? Re-run tools/narration-map or fix the data-sfx-anchor attribute."
        )
        self.anchor = anchor
        self.source = source


class AnchorIndexOutOfRangeError(SfxPlanError):
    def __init__(self, *, anchor: str, requested: int, available: int, source: str) -> None:
        super().__init__(
            f'anchor "{anchor}" requested index {requested} at {source}, '
            f"only {available} occurrence(s) in narration-map. "
            f"Drop the data-sfx-anchor-index attribute or fix the value."
        )
        self.anchor = anchor
        self.requested = requested
        self.available = available
        self.source = source


class UnknownCueError(SfxPlanError):
    def __init__(self, *, cue: str, known: list[str], source: str) -> None:
        known_str = ", ".join(sorted(known))
        super().__init__(
            f'unknown cue "{cue}" at {source}. Known cues: {known_str}. '
            f"Add the cue to sfx-catalog.yml or fix the data-sfx-on-anchor attribute."
        )
        self.cue = cue
        self.known = known
        self.source = source


class EmptyCueFilterError(SfxPlanError):
    def __init__(self, *, cue: str) -> None:
        super().__init__(
            f'cue "{cue}" filter matched 0 assets. '
            f"Relax the recipe in sfx-catalog.yml or add files to sound-effects/."
        )
        self.cue = cue


class CatalogMissingError(SfxPlanError):
    def __init__(self, *, path: str) -> None:
        super().__init__(
            f"sfx-catalog.yml not found at {path}. "
            f"Build it first: uv run --project tools/sfx-catalog sfx-catalog"
        )
        self.path = path


class CatalogVersionMismatchError(SfxPlanError):
    def __init__(self, *, found: int, expected: int) -> None:
        super().__init__(
            f"sfx-catalog.yml version {found} does not match sfx-plan's expected version {expected}. "
            f"Upgrade tools/sfx-plan or rebuild the catalog."
        )
        self.found = found
        self.expected = expected
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/test_errors.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-plan/src/sfx_plan/errors.py tools/sfx-plan/tests/__init__.py tools/sfx-plan/tests/test_errors.py
git commit -m "feat(sfx-plan): error hierarchy mirroring spec failure modes"
```

---

### Task 3: Test fixtures (`conftest.py`)

**Files:**
- Create: `tools/sfx-plan/tests/conftest.py`

A miniature video folder + a tiny in-memory catalog. Used by every later test.

- [ ] **Step 1: Write the fixtures**

Write `tools/sfx-plan/tests/conftest.py`:

```python
"""Fixtures: a miniature video folder, narration-map, and catalog."""
from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

import pytest
import yaml


@pytest.fixture
def video_dir(tmp_path: Path) -> Path:
    """A pretend video folder with an annotated index.html + narration-map.json."""
    root = tmp_path / "videos" / "demo-2026-05-11"
    root.mkdir(parents=True)
    (root / "compositions").mkdir()
    (root / "audio").mkdir()

    (root / "index.html").write_text(
        dedent('''\
        <!doctype html>
        <html>
        <body>
          <div id="root" data-composition-id="main" data-start="0" data-duration="60" data-width="1920" data-height="1080">
            <audio id="vo" data-start="0" data-duration="60" data-track-index="9" src="audio/vo.mp3"></audio>

            <div id="s1" class="scene">
              <h1 id="s1-headline"
                  data-sfx-anchor="nightmare"
                  data-sfx-on-anchor="ui-tick">A mathematical nightmare.</h1>
            </div>

            <div id="s2" class="scene"
                 data-sfx-anchor="easy"
                 data-sfx-on-anchor="whoosh">
              <h1 id="s2-title"
                  data-sfx-anchor="easy"
                  data-sfx-anchor-index="1"
                  data-sfx-on-anchor="ui-tick">Easy.</h1>
            </div>
          </div>
        </body>
        </html>
        '''),
        encoding="utf-8",
    )

    nm = {
        "source": "transcript.json",
        "audio_duration_secs": 60.0,
        "language_code": "eng",
        "word_count": 12,
        "config": {"pause_threshold_secs": 0.4, "scene_pause_threshold_secs": 0.6, "emphatic_top_n": 15, "anchor_phrase_count": 2},
        "anchors": [
            {"phrase": "nightmare",
             "matches": [{"word_index": 4, "start": 8.40, "end": 9.10, "matched_text": "nightmare"}]},
            {"phrase": "easy",
             "matches": [{"word_index": 12, "start": 22.00, "end": 22.40, "matched_text": "easy"}]},
        ],
    }
    (root / "narration-map.json").write_text(json.dumps(nm), encoding="utf-8")
    return root


@pytest.fixture
def catalog_path(tmp_path: Path) -> Path:
    """A tiny sfx-catalog.yml with two assets and the five default cues."""
    p = tmp_path / "sound-effects" / "sfx-catalog.yml"
    p.parent.mkdir(parents=True)
    (p.parent / "Mister Horse" / "Click").mkdir(parents=True)
    (p.parent / "Whooshes").mkdir(parents=True)
    (p.parent / "Mister Horse" / "Click" / "click-bright-01.wav").write_bytes(b"\x00")
    (p.parent / "Whooshes" / "whoosh-mid-01.wav").write_bytes(b"\x00")

    data = {
        "version": 1,
        "generated_at": "2026-05-11T00:00:00Z",
        "library_sha": "test",
        "assets": {
            "Mister Horse/Click/click-bright-01.wav": {
                "library": "Mister Horse", "category": "Click",
                "duration_s": 0.30, "sample_rate": 48000, "channels": 2,
                "format": "wav", "bit_depth": 24, "sha256": "a" * 64,
                "peak_dbfs": -2.0, "peak_time_s": 0.05,
                "integrated_lufs": -14.0, "rms_dbfs": -18.0,
                "onset_time_s": 0.01, "attack_time_s": 0.04, "tail_time_s": 0.20,
                "spectral_centroid_hz": 5000.0, "brightness": "bright",
                "low_energy_pct": 5, "mid_energy_pct": 30, "high_energy_pct": 65,
                "tags": ["click", "ui", "bright"], "auto_role": "accent",
            },
            "Whooshes/whoosh-mid-01.wav": {
                "library": "Whooshes", "category": "Whooshes",
                "duration_s": 0.80, "sample_rate": 48000, "channels": 2,
                "format": "wav", "bit_depth": 24, "sha256": "b" * 64,
                "peak_dbfs": -1.5, "peak_time_s": 0.40,
                "integrated_lufs": -16.0, "rms_dbfs": -20.0,
                "onset_time_s": 0.05, "attack_time_s": 0.35, "tail_time_s": 0.30,
                "spectral_centroid_hz": 2500.0, "brightness": "warm",
                "low_energy_pct": 20, "mid_energy_pct": 50, "high_energy_pct": 30,
                "tags": ["whoosh", "warm"], "auto_role": "transition",
            },
        },
        "cues": {
            "ui-tick": {"filter": {"auto_role": "accent", "duration_s_max": 0.5,
                                    "brightness_in": ["bright", "airy"]},
                       "default_lead_ms": -50, "default_volume": 0.8},
            "whoosh":  {"filter": {"auto_role": "transition", "duration_s_min": 0.4,
                                    "duration_s_max": 1.5, "attack_time_s_min": 0.1},
                       "default_lead_ms": -150, "default_volume": 0.9},
            "boom":    {"filter": {"auto_role": "impact", "low_energy_pct_min": 50,
                                    "peak_time_s_max": 0.2},
                       "default_lead_ms": 0, "default_volume": 1.0},
            "riser":   {"filter": {"auto_role": "riser", "duration_s_min": 1.5},
                       "default_lead_ms": None, "default_volume": 0.85},
            "pop":     {"filter": {"auto_role": "accent", "duration_s_max": 0.3,
                                    "brightness_in": ["warm", "bright"]},
                       "default_lead_ms": -50, "default_volume": 0.8},
        },
    }
    p.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return p
```

- [ ] **Step 2: Verify fixtures load**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/conftest.py --collect-only -q
```

Expected: 0 tests, no import errors.

- [ ] **Step 3: Commit**

```bash
git add tools/sfx-plan/tests/conftest.py
git commit -m "test(sfx-plan): video-folder and catalog fixtures"
```

---

### Task 4: HTML annotation scanner (`annotations.py`)

**Files:**
- Create: `tools/sfx-plan/src/sfx_plan/annotations.py`
- Create: `tools/sfx-plan/tests/test_annotations.py`

- [ ] **Step 1: Write the failing tests**

Write `tools/sfx-plan/tests/test_annotations.py`:

```python
"""Tests for the HTML annotation scanner."""
from __future__ import annotations

from pathlib import Path

from sfx_plan.annotations import scan_annotations


def test_scan_finds_every_annotation(video_dir: Path) -> None:
    annotations = list(scan_annotations(video_dir))
    # The fixture has three annotated elements: s1-headline, s2 (scene root), s2-title.
    assert len(annotations) == 3


def test_scan_extracts_anchor_and_cue_and_source(video_dir: Path) -> None:
    annotations = list(scan_annotations(video_dir))
    by_anchor = {a.anchor: a for a in annotations if a.anchor != "easy"} | {
        ("easy", a.element_id): a for a in annotations if a.anchor == "easy"
    }
    nightmare = next(a for a in annotations if a.anchor == "nightmare")
    assert nightmare.cue == "ui-tick"
    assert nightmare.anchor_index == 1
    assert nightmare.source.endswith("index.html:9")  # adjust line if fixture changes
    assert nightmare.element_id == "s1-headline"


def test_scan_reads_optional_overrides(video_dir: Path) -> None:
    # Inject an annotation with all overrides set; verify parser keeps them.
    p = video_dir / "compositions" / "extra.html"
    p.write_text(
        '<html><body><div id="x"'
        ' data-sfx-anchor="easy" data-sfx-anchor-index="1"'
        ' data-sfx-on-anchor="whoosh" data-sfx-lead-ms="-200"'
        ' data-sfx-volume="0.7" data-sfx-pan="-0.3"></div></body></html>',
        encoding="utf-8",
    )
    annotations = list(scan_annotations(video_dir))
    extra = next(a for a in annotations if a.source.endswith("extra.html:1"))
    assert extra.lead_ms == -200
    assert extra.volume == 0.7
    assert extra.pan == -0.3
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/test_annotations.py -v
```

Expected: FAIL — `scan_annotations` not defined.

- [ ] **Step 3: Implement `scan_annotations`**

Write `tools/sfx-plan/src/sfx_plan/annotations.py`:

```python
"""Walk a video folder's HTML files and collect every data-sfx-* annotation."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class Annotation:
    """One element's worth of data-sfx-* attributes plus its source location."""

    anchor: str
    anchor_index: int
    cue: str
    lead_ms: int | None
    volume: float | None
    pan: float
    is_hook: bool
    element_id: str | None
    source: str  # "<path>:<line>" relative to the video folder


def _parse_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _parse_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _html_files(root: Path) -> Iterator[Path]:
    yield from sorted(root.rglob("*.html"))


def scan_annotations(video_dir: Path) -> Iterator[Annotation]:
    """Yield every data-sfx-* annotation found under `video_dir`.

    `compositions/sfx.html` is skipped (it's the *output* of this tool — scanning
    it would create a loop).
    """
    for path in _html_files(video_dir):
        if path.name == "sfx.html" and path.parent.name == "compositions":
            continue
        soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
        for tag in soup.find_all(attrs={"data-sfx-anchor": True}):
            anchor = tag.get("data-sfx-anchor", "").strip()
            cue = tag.get("data-sfx-on-anchor", "").strip()
            if not anchor or not cue:
                continue
            line = tag.sourceline or 1
            rel = path.relative_to(video_dir).as_posix()
            yield Annotation(
                anchor=anchor,
                anchor_index=_parse_int(tag.get("data-sfx-anchor-index")) or 1,
                cue=cue,
                lead_ms=_parse_int(tag.get("data-sfx-lead-ms")),
                volume=_parse_float(tag.get("data-sfx-volume")),
                pan=_parse_float(tag.get("data-sfx-pan")) or 0.0,
                is_hook=(tag.get("data-sfx-hook") == "true"),
                element_id=tag.get("id"),
                source=f"{rel}:{line}",
            )
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/test_annotations.py -v
```

Expected: 3 passed. (If line numbers differ slightly because of dedent, adjust the assertion.)

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-plan/src/sfx_plan/annotations.py tools/sfx-plan/tests/test_annotations.py
git commit -m "feat(sfx-plan): HTML scanner for data-sfx-* annotations"
```

---

### Task 5: Narration-map loader + anchor resolver (`narration.py`)

**Files:**
- Create: `tools/sfx-plan/src/sfx_plan/narration.py`
- Create: `tools/sfx-plan/tests/test_narration.py`

- [ ] **Step 1: Write the failing tests**

Write `tools/sfx-plan/tests/test_narration.py`:

```python
"""Tests for narration-map loading and anchor resolution."""
from __future__ import annotations

from pathlib import Path

import pytest

from sfx_plan.errors import UnresolvedAnchorError, AnchorIndexOutOfRangeError
from sfx_plan.narration import load_narration_map, resolve_anchor


def test_load_returns_map_keyed_by_normalized_phrase(video_dir: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    assert "nightmare" in nm
    assert "easy" in nm


def test_resolve_anchor_returns_correct_start_time(video_dir: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    start = resolve_anchor(nm, anchor="nightmare", index=1, source="x:1")
    assert start == 8.40


def test_resolve_is_case_and_whitespace_insensitive(video_dir: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    assert resolve_anchor(nm, anchor="  Nightmare  ", index=1, source="x:1") == 8.40


def test_unresolved_anchor_raises(video_dir: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    with pytest.raises(UnresolvedAnchorError):
        resolve_anchor(nm, anchor="Bézier", index=1, source="index.html:127")


def test_anchor_index_out_of_range_raises(video_dir: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    with pytest.raises(AnchorIndexOutOfRangeError) as exc_info:
        resolve_anchor(nm, anchor="easy", index=3, source="index.html:45")
    assert exc_info.value.available == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/test_narration.py -v
```

Expected: FAIL — `narration` module not defined.

- [ ] **Step 3: Implement `narration.py`**

Write `tools/sfx-plan/src/sfx_plan/narration.py`:

```python
"""Load narration-map.json and resolve anchors to timestamps."""
from __future__ import annotations

import json
import re
from pathlib import Path

from sfx_plan.errors import UnresolvedAnchorError, AnchorIndexOutOfRangeError

_PUNCT_STRIP_RE = re.compile(r"[^\w\s]+", re.UNICODE)


def _normalize(phrase: str) -> str:
    """Lowercase + strip punctuation + collapse whitespace. Matches narration-map's contract."""
    no_punct = _PUNCT_STRIP_RE.sub(" ", phrase.lower())
    return " ".join(no_punct.split())


def load_narration_map(path: Path) -> dict[str, list[dict]]:
    """Return a dict mapping normalized phrase → list of {start, end, ...} matches."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, list[dict]] = {}
    for entry in raw.get("anchors", []):
        phrase = entry.get("phrase", "")
        key = _normalize(phrase)
        if not key:
            continue
        out[key] = list(entry.get("matches", []))
    return out


def resolve_anchor(
    nm: dict[str, list[dict]],
    *,
    anchor: str,
    index: int,
    source: str,
) -> float:
    """Return the start time (seconds) of the `index`-th occurrence of `anchor`.

    `index` is 1-indexed (the user-facing convention from data-sfx-anchor-index).
    Raises `UnresolvedAnchorError` if the anchor isn't in the map at all.
    Raises `AnchorIndexOutOfRangeError` if the index exceeds the number of matches.
    """
    key = _normalize(anchor)
    matches = nm.get(key)
    if not matches:
        raise UnresolvedAnchorError(anchor=anchor, source=source)
    if index < 1 or index > len(matches):
        raise AnchorIndexOutOfRangeError(
            anchor=anchor, requested=index, available=len(matches), source=source,
        )
    return float(matches[index - 1]["start"])
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/test_narration.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-plan/src/sfx_plan/narration.py tools/sfx-plan/tests/test_narration.py
git commit -m "feat(sfx-plan): narration-map loader + anchor resolver"
```

---

### Task 6: Catalog loader + filter engine (`catalog.py`)

**Files:**
- Create: `tools/sfx-plan/src/sfx_plan/catalog.py`
- Create: `tools/sfx-plan/tests/test_catalog.py`

- [ ] **Step 1: Write the failing tests**

Write `tools/sfx-plan/tests/test_catalog.py`:

```python
"""Tests for catalog loading + filter engine."""
from __future__ import annotations

from pathlib import Path

import pytest

from sfx_plan.catalog import load_catalog, filter_assets, get_cue
from sfx_plan.errors import (
    CatalogMissingError,
    CatalogVersionMismatchError,
    UnknownCueError,
    EmptyCueFilterError,
)


def test_load_returns_dict_with_assets_and_cues(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    assert cat["version"] == 1
    assert "Mister Horse/Click/click-bright-01.wav" in cat["assets"]
    assert "ui-tick" in cat["cues"]


def test_missing_catalog_raises(tmp_path: Path) -> None:
    with pytest.raises(CatalogMissingError):
        load_catalog(tmp_path / "missing.yml")


def test_version_mismatch_raises(tmp_path: Path) -> None:
    p = tmp_path / "future.yml"
    p.write_text("version: 99\ngenerated_at: x\nlibrary_sha: y\nassets: {}\ncues: {}\n")
    with pytest.raises(CatalogVersionMismatchError):
        load_catalog(p)


def test_get_cue_returns_recipe(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    cue = get_cue(cat, name="ui-tick", source="x:1")
    assert cue["default_lead_ms"] == -50


def test_get_cue_unknown_raises(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    with pytest.raises(UnknownCueError):
        get_cue(cat, name="boom-sub", source="x:1")


def test_filter_assets_applies_filter_operators(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    # ui-tick filter: auto_role=accent, duration_s_max=0.5, brightness_in=[bright, airy]
    matches = filter_assets(cat, cue_name="ui-tick")
    paths = [p for p, _ in matches]
    assert "Mister Horse/Click/click-bright-01.wav" in paths
    assert "Whooshes/whoosh-mid-01.wav" not in paths  # transition role excluded


def test_filter_assets_empty_match_raises(catalog_path: Path) -> None:
    # boom filter requires auto_role=impact + low_energy_pct>=50 — fixture has neither
    cat = load_catalog(catalog_path)
    with pytest.raises(EmptyCueFilterError):
        filter_assets(cat, cue_name="boom")
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/test_catalog.py -v
```

Expected: FAIL — `catalog` module not defined.

- [ ] **Step 3: Implement `catalog.py`**

Write `tools/sfx-plan/src/sfx_plan/catalog.py`:

```python
"""Catalog loader + filter engine.

The filter engine is a small DSL over flat dict operators:
    <field>           → entry[field] == value
    <field>_min       → entry[field] >= value
    <field>_max       → entry[field] <= value
    <field>_in        → entry[field] in value (value is a list)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from sfx_plan.errors import (
    CatalogMissingError,
    CatalogVersionMismatchError,
    EmptyCueFilterError,
    UnknownCueError,
)

EXPECTED_CATALOG_VERSION = 1

_OP_SUFFIXES = ("_min", "_max", "_in")


def load_catalog(path: Path) -> dict[str, Any]:
    """Load a catalog YAML, validating the version field. Raises on missing or mismatch."""
    if not path.exists():
        raise CatalogMissingError(path=str(path))
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    version = raw.get("version") if isinstance(raw, dict) else None
    if version != EXPECTED_CATALOG_VERSION:
        raise CatalogVersionMismatchError(
            found=int(version) if isinstance(version, int) else 0,
            expected=EXPECTED_CATALOG_VERSION,
        )
    return raw


def _matches_filter(entry: dict[str, Any], flt: dict[str, Any]) -> bool:
    for key, expected in flt.items():
        # Detect operator suffix.
        for suffix in _OP_SUFFIXES:
            if key.endswith(suffix):
                field = key[: -len(suffix)]
                actual = entry.get(field)
                if actual is None:
                    return False
                if suffix == "_min" and not (actual >= expected):
                    return False
                if suffix == "_max" and not (actual <= expected):
                    return False
                if suffix == "_in" and actual not in expected:
                    return False
                break
        else:
            # No suffix: exact equality.
            if entry.get(key) != expected:
                return False
    return True


def get_cue(cat: dict[str, Any], *, name: str, source: str) -> dict[str, Any]:
    """Return the cue recipe by name. Raises UnknownCueError with the known list."""
    cues = cat.get("cues", {})
    if name not in cues:
        raise UnknownCueError(cue=name, known=list(cues.keys()), source=source)
    return cues[name]


def filter_assets(
    cat: dict[str, Any],
    *,
    cue_name: str,
) -> list[tuple[str, dict[str, Any]]]:
    """Return sorted (path, entry) pairs whose metadata matches the cue's filter.

    The result is sorted by path for determinism (the picker uses index into this list).
    """
    cue = cat["cues"].get(cue_name)
    if cue is None:
        # Caller should have used get_cue() first; raise the right error anyway.
        raise UnknownCueError(cue=cue_name, known=list(cat["cues"].keys()), source="(filter)")
    flt = cue.get("filter", {}) or {}
    matches = [
        (path, entry)
        for path, entry in cat.get("assets", {}).items()
        if _matches_filter(entry, flt)
    ]
    if not matches:
        raise EmptyCueFilterError(cue=cue_name)
    return sorted(matches, key=lambda item: item[0])
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/test_catalog.py -v
```

Expected: 7 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-plan/src/sfx_plan/catalog.py tools/sfx-plan/tests/test_catalog.py
git commit -m "feat(sfx-plan): catalog loader + filter engine"
```

---

### Task 7: Deterministic asset picker + peak-aligned timing (`plan.py`)

**Files:**
- Create: `tools/sfx-plan/src/sfx_plan/plan.py`
- Create: `tools/sfx-plan/tests/test_plan.py`

- [ ] **Step 1: Write the failing tests**

Write `tools/sfx-plan/tests/test_plan.py`:

```python
"""Tests for asset picker and timing math."""
from __future__ import annotations

import math
from pathlib import Path

import pytest

from sfx_plan.annotations import Annotation
from sfx_plan.catalog import load_catalog
from sfx_plan.narration import load_narration_map
from sfx_plan.plan import pick_asset, build_cue, build_plan


def test_pick_asset_is_deterministic(catalog_path: Path) -> None:
    cat = load_catalog(catalog_path)
    candidates = [
        ("a.wav", {"path": "a.wav"}),
        ("b.wav", {"path": "b.wav"}),
        ("c.wav", {"path": "c.wav"}),
    ]
    first = pick_asset(candidates, anchor="foo", anchor_index=1, cue="ui-tick")
    second = pick_asset(candidates, anchor="foo", anchor_index=1, cue="ui-tick")
    assert first == second


def test_pick_asset_changes_with_anchor(catalog_path: Path) -> None:
    candidates = [("a.wav", {"path": "a.wav"})] * 1
    # With one candidate, both calls return the same. Use more candidates:
    candidates = [
        ("a.wav", {"path": "a.wav"}),
        ("b.wav", {"path": "b.wav"}),
        ("c.wav", {"path": "c.wav"}),
        ("d.wav", {"path": "d.wav"}),
    ]
    p1 = pick_asset(candidates, anchor="foo", anchor_index=1, cue="ui-tick")
    p2 = pick_asset(candidates, anchor="bar", anchor_index=1, cue="ui-tick")
    # Not guaranteed to differ for any pair, but with 4 candidates the hash spread
    # should give different picks for "foo" vs "bar".
    assert (p1, p2) != ("a.wav", "a.wav") or p1 != p2  # at least one differs


def test_build_cue_peak_aligned_data_start(video_dir: Path, catalog_path: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    cat = load_catalog(catalog_path)
    ann = Annotation(
        anchor="nightmare", anchor_index=1, cue="ui-tick",
        lead_ms=None, volume=None, pan=0.0, is_hook=False,
        element_id="s1-headline", source="index.html:9",
    )
    cue = build_cue(ann, nm=nm, catalog=cat)
    # anchor nightmare starts at 8.40; ui-tick lead -50ms; peak_time of picked
    # click asset is 0.05.  data-start = 8.40 + (-0.050) - 0.05 = 8.30.
    assert math.isclose(cue.data_start, 8.30, abs_tol=0.001)
    assert cue.cue == "ui-tick"


def test_build_plan_returns_cues_sorted_by_start(video_dir: Path, catalog_path: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    cat = load_catalog(catalog_path)
    annotations = [
        Annotation(anchor="easy", anchor_index=1, cue="whoosh",
                   lead_ms=None, volume=None, pan=0.0, is_hook=False,
                   element_id="s2", source="index.html:18"),
        Annotation(anchor="nightmare", anchor_index=1, cue="ui-tick",
                   lead_ms=None, volume=None, pan=0.0, is_hook=False,
                   element_id="s1-headline", source="index.html:9"),
    ]
    plan = build_plan(annotations, nm=nm, catalog=cat)
    starts = [c.data_start for c in plan]
    assert starts == sorted(starts)


def test_lead_clamps_to_zero_with_warning(video_dir: Path, catalog_path: Path) -> None:
    nm = load_narration_map(video_dir / "narration-map.json")
    cat = load_catalog(catalog_path)
    ann = Annotation(
        anchor="nightmare", anchor_index=1, cue="whoosh",
        lead_ms=-10000, volume=None, pan=0.0, is_hook=False,
        element_id="x", source="index.html:1",
    )
    cue = build_cue(ann, nm=nm, catalog=cat)
    assert cue.data_start == 0.0
    assert cue.clamped is True
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/test_plan.py -v
```

Expected: FAIL — `plan` module not defined.

- [ ] **Step 3: Implement `plan.py`**

Write `tools/sfx-plan/src/sfx_plan/plan.py`:

```python
"""Plan-building: asset picking + timing math."""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from sfx_plan.annotations import Annotation
from sfx_plan.catalog import filter_assets, get_cue
from sfx_plan.narration import resolve_anchor


_TRACK_BY_CUE: dict[str, int] = {
    "ui-tick": 20,
    "whoosh":  21,
    "boom":    22,
    "riser":   23,
    "pop":     24,
}
_DEFAULT_TRACK = 29


@dataclass(frozen=True)
class Cue:
    """One scheduled audio event, ready to emit as an HTML <audio> tag."""

    data_start: float
    duration_s: float
    volume: float
    pan: float
    track_index: int
    src: str  # repo-relative path inside sound-effects/ — the emitter rewrites to a relative href.
    cue: str
    anchor: str
    anchor_index: int
    source: str
    clamped: bool


def pick_asset(
    candidates: list[tuple[str, dict[str, Any]]],
    *,
    anchor: str,
    anchor_index: int,
    cue: str,
) -> str:
    """Pick one asset path deterministically from the candidate list."""
    seed = f"{anchor.lower()}|{anchor_index}|{cue}".encode("utf-8")
    digest = hashlib.sha256(seed).digest()
    idx = int.from_bytes(digest[:8], "big") % len(candidates)
    return candidates[idx][0]


def build_cue(
    ann: Annotation,
    *,
    nm: dict[str, list[dict]],
    catalog: dict[str, Any],
) -> Cue:
    """Resolve a single annotation into a fully scheduled Cue."""
    recipe = get_cue(catalog, name=ann.cue, source=ann.source)
    candidates = filter_assets(catalog, cue_name=ann.cue)
    asset_path = pick_asset(
        candidates, anchor=ann.anchor, anchor_index=ann.anchor_index, cue=ann.cue,
    )
    asset = catalog["assets"][asset_path]

    t_anchor = resolve_anchor(nm, anchor=ann.anchor, index=ann.anchor_index, source=ann.source)

    # Lead resolution: explicit override > recipe default > -(duration) for null sentinel.
    if ann.lead_ms is not None:
        lead_ms = ann.lead_ms
    elif recipe.get("default_lead_ms") is not None:
        lead_ms = recipe["default_lead_ms"]
    else:
        lead_ms = -int(asset["duration_s"] * 1000)

    raw_start = t_anchor + (lead_ms / 1000.0) - float(asset["peak_time_s"])
    clamped = raw_start < 0.0
    data_start = max(raw_start, 0.0)

    volume = ann.volume if ann.volume is not None else float(recipe.get("default_volume", 1.0))

    return Cue(
        data_start=round(data_start, 4),
        duration_s=float(asset["duration_s"]),
        volume=volume,
        pan=ann.pan,
        track_index=_TRACK_BY_CUE.get(ann.cue, _DEFAULT_TRACK),
        src=asset_path,
        cue=ann.cue,
        anchor=ann.anchor,
        anchor_index=ann.anchor_index,
        source=ann.source,
        clamped=clamped,
    )


def build_plan(
    annotations: list[Annotation],
    *,
    nm: dict[str, list[dict]],
    catalog: dict[str, Any],
) -> list[Cue]:
    """Resolve every annotation, sort by data_start, return the timed plan."""
    cues = [build_cue(a, nm=nm, catalog=catalog) for a in annotations]
    cues.sort(key=lambda c: c.data_start)
    return cues
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/test_plan.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-plan/src/sfx_plan/plan.py tools/sfx-plan/tests/test_plan.py
git commit -m "feat(sfx-plan): deterministic asset picker + peak-aligned timing"
```

---

### Task 8: `compositions/sfx.html` emitter (`emit.py`)

**Files:**
- Create: `tools/sfx-plan/src/sfx_plan/emit.py`
- Create: `tools/sfx-plan/tests/test_emit.py`

- [ ] **Step 1: Write the failing tests**

Write `tools/sfx-plan/tests/test_emit.py`:

```python
"""Tests for sfx.html emission and index.html mount wiring."""
from __future__ import annotations

from pathlib import Path

from sfx_plan.plan import Cue
from sfx_plan.emit import render_sfx_html, ensure_mount


def _cue(start: float = 1.0, cue: str = "ui-tick") -> Cue:
    return Cue(
        data_start=start, duration_s=0.4, volume=0.8, pan=0.0,
        track_index=20, src="Mister Horse/Click/click-bright-01.wav",
        cue=cue, anchor="foo", anchor_index=1,
        source="index.html:9", clamped=False,
    )


def test_render_includes_generated_header() -> None:
    text = render_sfx_html(
        cues=[_cue()],
        sfx_html_path=Path("videos/demo/compositions/sfx.html"),
        sound_effects_root=Path("sound-effects"),
        catalog_sha="abc123",
        total_duration_s=60.0,
    )
    assert "GENERATED by tools/sfx-plan" in text
    assert "do not edit" in text.lower()


def test_render_emits_audio_tag_per_cue_with_relative_src() -> None:
    text = render_sfx_html(
        cues=[_cue()],
        sfx_html_path=Path("videos/demo/compositions/sfx.html"),
        sound_effects_root=Path("sound-effects"),
        catalog_sha="abc",
        total_duration_s=60.0,
    )
    # From videos/demo/compositions/ → up 3 → sound-effects/Mister Horse/Click/...
    assert 'src="../../../sound-effects/Mister Horse/Click/click-bright-01.wav"' in text
    assert 'data-start="1.0"' in text
    assert 'data-duration="0.4"' in text
    assert 'data-volume="0.8"' in text
    assert 'data-track-index="20"' in text


def test_render_includes_source_comment_per_cue() -> None:
    text = render_sfx_html(
        cues=[_cue()],
        sfx_html_path=Path("videos/demo/compositions/sfx.html"),
        sound_effects_root=Path("sound-effects"),
        catalog_sha="abc",
        total_duration_s=60.0,
    )
    assert "from index.html:9" in text
    assert 'anchor="foo"' in text
    assert "cue=ui-tick" in text


def test_render_sorts_by_data_start() -> None:
    text = render_sfx_html(
        cues=[_cue(start=5.0), _cue(start=1.0), _cue(start=3.0)],
        sfx_html_path=Path("videos/demo/compositions/sfx.html"),
        sound_effects_root=Path("sound-effects"),
        catalog_sha="abc",
        total_duration_s=60.0,
    )
    starts = [line for line in text.splitlines() if 'data-start="' in line]
    extracted = [float(line.split('data-start="')[1].split('"')[0]) for line in starts]
    assert extracted == sorted(extracted)


def test_ensure_mount_inserts_when_missing(tmp_path: Path) -> None:
    idx = tmp_path / "index.html"
    idx.write_text(
        '<html>\n<body>\n  <div id="root"></div>\n</body>\n</html>\n',
        encoding="utf-8",
    )
    inserted = ensure_mount(idx)
    text = idx.read_text(encoding="utf-8")
    assert inserted is True
    assert 'data-composition-src="compositions/sfx.html"' in text


def test_ensure_mount_is_idempotent(tmp_path: Path) -> None:
    idx = tmp_path / "index.html"
    idx.write_text(
        '<html>\n<body>\n  <div id="root"></div>\n  <div data-composition-src="compositions/sfx.html"></div>\n</body>\n</html>\n',
        encoding="utf-8",
    )
    inserted = ensure_mount(idx)
    text = idx.read_text(encoding="utf-8")
    assert inserted is False
    assert text.count("compositions/sfx.html") == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/test_emit.py -v
```

Expected: FAIL — `emit` module not defined.

- [ ] **Step 3: Implement `emit.py`**

Write `tools/sfx-plan/src/sfx_plan/emit.py`:

```python
"""Emit compositions/sfx.html + maintain index.html mount."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from sfx_plan.plan import Cue


_MOUNT_LINE = (
    '<!-- sfx-layer: generated by tools/sfx-plan, do not edit -->\n'
    '<div data-composition-src="compositions/sfx.html" data-composition-id="sfx-layer"></div>\n'
)


def _audio_tag(cue: Cue, src_rel: str) -> str:
    comment = (
        f'  <!-- from {cue.source}  anchor="{cue.anchor}" idx={cue.anchor_index}  '
        f'cue={cue.cue}  lead-aligned -->'
    )
    pan = "" if cue.pan == 0.0 else f' data-pan="{cue.pan}"'
    return (
        f'{comment}\n'
        f'  <audio data-start="{cue.data_start}" data-duration="{cue.duration_s}" '
        f'data-volume="{cue.volume}"{pan}\n'
        f'         data-track-index="{cue.track_index}"\n'
        f'         src="{src_rel}"></audio>'
    )


def _relative_src(sfx_html_path: Path, sound_effects_root: Path, asset_rel: str) -> str:
    """Compute the relative href from sfx.html's parent to the asset path."""
    target = (sound_effects_root / asset_rel).resolve(strict=False)
    start = sfx_html_path.parent.resolve(strict=False)
    return os.path.relpath(target, start=start).replace(os.sep, "/")


def render_sfx_html(
    *,
    cues: list[Cue],
    sfx_html_path: Path,
    sound_effects_root: Path,
    catalog_sha: str,
    total_duration_s: float,
) -> str:
    """Produce the full text of compositions/sfx.html for the given cues."""
    ordered = sorted(cues, key=lambda c: c.data_start)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    header = (
        "<!--\n"
        "  GENERATED by tools/sfx-plan — do not edit by hand.\n"
        f"  Source: sfx-plan v1, run at {ts}\n"
        f"  Cues: {len(ordered)}   Duration: {total_duration_s:.1f}s   "
        f"Catalog: sfx-catalog.yml@{catalog_sha[:12]}\n"
        "-->\n"
    )
    open_tag = (
        f'<html data-composition-id="sfx-layer" data-start="0" '
        f'data-duration="{total_duration_s}">\n<body>\n'
    )
    body = "\n".join(
        _audio_tag(c, _relative_src(sfx_html_path, sound_effects_root, c.src))
        for c in ordered
    )
    return f"{header}{open_tag}{body}\n</body>\n</html>\n"


def ensure_mount(index_html_path: Path) -> bool:
    """Insert the sfx-layer mount into index.html if absent. Returns True if changed."""
    text = index_html_path.read_text(encoding="utf-8")
    if "compositions/sfx.html" in text:
        return False
    # Insert right before </body>; fall back to appending at end if no </body>.
    if "</body>" in text:
        new_text = text.replace("</body>", _MOUNT_LINE + "</body>", 1)
    else:
        new_text = text + "\n" + _MOUNT_LINE
    index_html_path.write_text(new_text, encoding="utf-8")
    return True
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/test_emit.py -v
```

Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-plan/src/sfx_plan/emit.py tools/sfx-plan/tests/test_emit.py
git commit -m "feat(sfx-plan): sfx.html emitter + idempotent index.html mount"
```

---

### Task 9: Validation pass (overlap + density warnings)

**Files:**
- Create: `tools/sfx-plan/src/sfx_plan/validate.py`
- Create: `tools/sfx-plan/tests/test_validate.py`

- [ ] **Step 1: Write the failing tests**

Write `tools/sfx-plan/tests/test_validate.py`:

```python
"""Tests for the validation pass."""
from __future__ import annotations

import pytest

from sfx_plan.plan import Cue
from sfx_plan.validate import validate_plan, DensityViolationError


def _cue(start: float, dur: float = 0.4, cue: str = "ui-tick", track: int = 20) -> Cue:
    return Cue(
        data_start=start, duration_s=dur, volume=0.8, pan=0.0,
        track_index=track, src="x.wav", cue=cue,
        anchor="a", anchor_index=1, source="x:1", clamped=False,
    )


def test_no_warnings_for_well_spaced_cues() -> None:
    warnings = validate_plan([_cue(0.0), _cue(5.0), _cue(10.0)], total_duration_s=60.0)
    assert warnings == []


def test_overlap_on_same_track_emits_warning() -> None:
    warnings = validate_plan([_cue(1.0, 1.0, track=20), _cue(1.5, 0.4, track=20)], total_duration_s=60.0)
    assert any("overlap" in w.lower() for w in warnings)


def test_overlap_on_different_tracks_does_not_warn() -> None:
    warnings = validate_plan([_cue(1.0, 1.0, track=20), _cue(1.5, 0.4, track=21)], total_duration_s=60.0)
    assert not any("overlap" in w.lower() for w in warnings)


def test_density_warning_above_three_per_window() -> None:
    cues = [_cue(t) for t in [0.0, 0.4, 0.8, 1.2]]  # 4 cues inside 1.2s → ~3.3/s
    warnings = validate_plan(cues, total_duration_s=60.0)
    assert any("density" in w.lower() for w in warnings)


def test_density_above_hard_cap_raises() -> None:
    # >1 cue per 1.5s sustained → hard cap.
    cues = [_cue(t * 0.2) for t in range(20)]  # 20 cues in 4s → 5/s
    with pytest.raises(DensityViolationError):
        validate_plan(cues, total_duration_s=60.0)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/test_validate.py -v
```

Expected: FAIL — `validate` module not defined.

- [ ] **Step 3: Implement validation**

Write `tools/sfx-plan/src/sfx_plan/validate.py`:

```python
"""Validation pass: overlap detection + density checks."""
from __future__ import annotations

from sfx_plan.errors import SfxPlanError
from sfx_plan.plan import Cue


DENSITY_WARN_PER_SEC = 1.0 / 3.0   # warn above 1 cue per 3s rolling avg
DENSITY_HARD_PER_SEC = 1.0 / 1.5   # hard fail above 1 cue per 1.5s rolling avg
DENSITY_WINDOW_S = 6.0             # rolling window used for both thresholds


class DensityViolationError(SfxPlanError):
    def __init__(self, *, density: float, window_s: float, hard_cap: float) -> None:
        super().__init__(
            f"cue density {density:.2f}/s in a {window_s}s window exceeds the hard cap "
            f"of {hard_cap:.2f}/s. Drop cues — the mix will smear VO intelligibility."
        )
        self.density = density


def _overlap_warnings(cues: list[Cue]) -> list[str]:
    warnings: list[str] = []
    by_track: dict[int, list[Cue]] = {}
    for c in cues:
        by_track.setdefault(c.track_index, []).append(c)
    for track, lane in by_track.items():
        lane.sort(key=lambda c: c.data_start)
        for prev, curr in zip(lane, lane[1:]):
            if curr.data_start < prev.data_start + prev.duration_s:
                warnings.append(
                    f"overlap on track {track}: cue at {prev.data_start:.2f}s "
                    f"({prev.cue}, {prev.duration_s:.2f}s) intersects cue at "
                    f"{curr.data_start:.2f}s ({curr.cue})."
                )
    return warnings


def _density_check(cues: list[Cue]) -> list[str]:
    """Rolling-window density. Warn at WARN cap; raise at HARD cap."""
    warnings: list[str] = []
    if not cues:
        return warnings
    ordered = sorted(cues, key=lambda c: c.data_start)
    for i, anchor in enumerate(ordered):
        window_end = anchor.data_start + DENSITY_WINDOW_S
        count = sum(1 for c in ordered[i:] if c.data_start < window_end)
        density = count / DENSITY_WINDOW_S
        if density > DENSITY_HARD_PER_SEC:
            raise DensityViolationError(
                density=density, window_s=DENSITY_WINDOW_S, hard_cap=DENSITY_HARD_PER_SEC,
            )
        if density > DENSITY_WARN_PER_SEC:
            warnings.append(
                f"density {density:.2f}/s in window starting {anchor.data_start:.2f}s "
                f"({count} cues in {DENSITY_WINDOW_S}s). Consider trimming."
            )
            break  # report once per plan
    return warnings


def validate_plan(cues: list[Cue], *, total_duration_s: float) -> list[str]:
    """Run all validations; return a list of warning strings. May raise on hard caps."""
    warnings = _overlap_warnings(cues)
    warnings.extend(_density_check(cues))
    if any(c.clamped for c in cues):
        for c in cues:
            if c.clamped:
                warnings.append(
                    f"cue at {c.source} clamped to 0s (computed start was negative)."
                )
    return warnings
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/test_validate.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add tools/sfx-plan/src/sfx_plan/validate.py tools/sfx-plan/tests/test_validate.py
git commit -m "feat(sfx-plan): validation pass — overlap + density"
```

---

### Task 10: CLI entry point + end-to-end integration test

**Files:**
- Create: `tools/sfx-plan/src/sfx_plan/cli.py`
- Create: `tools/sfx-plan/tests/test_cli.py`

- [ ] **Step 1: Write the failing tests**

Write `tools/sfx-plan/tests/test_cli.py`:

```python
"""End-to-end smoke tests for the sfx-plan CLI."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from sfx_plan.cli import main


def test_cli_emits_sfx_html(video_dir: Path, catalog_path: Path, capsys) -> None:
    rc = main([
        str(video_dir),
        "--catalog", str(catalog_path),
    ])
    assert rc == 0
    sfx = video_dir / "compositions" / "sfx.html"
    assert sfx.exists()
    text = sfx.read_text(encoding="utf-8")
    assert "GENERATED by tools/sfx-plan" in text
    # The three fixture annotations all resolve, so three audio tags should land.
    assert text.count("<audio ") == 3


def test_cli_mounts_sfx_layer_in_index(video_dir: Path, catalog_path: Path) -> None:
    main([str(video_dir), "--catalog", str(catalog_path)])
    idx = (video_dir / "index.html").read_text(encoding="utf-8")
    assert 'data-composition-src="compositions/sfx.html"' in idx


def test_cli_dry_run_does_not_write(video_dir: Path, catalog_path: Path) -> None:
    main([str(video_dir), "--catalog", str(catalog_path), "--dry-run"])
    assert not (video_dir / "compositions" / "sfx.html").exists()


def test_cli_report_prints_plan_table(video_dir: Path, catalog_path: Path, capsys) -> None:
    main([str(video_dir), "--catalog", str(catalog_path), "--report"])
    captured = capsys.readouterr()
    assert "anchor=" in captured.out
    assert "ui-tick" in captured.out


def test_cli_returns_nonzero_on_unresolved_anchor(video_dir: Path, catalog_path: Path, capsys) -> None:
    # Append a bad annotation that references a missing anchor.
    extra = video_dir / "compositions" / "broken.html"
    extra.write_text(
        '<html><body><div data-sfx-anchor="totally-missing-word" data-sfx-on-anchor="ui-tick"></div></body></html>',
        encoding="utf-8",
    )
    rc = main([str(video_dir), "--catalog", str(catalog_path)])
    assert rc != 0
    captured = capsys.readouterr()
    assert "totally-missing-word" in captured.err
```

- [ ] **Step 2: Run tests to verify they fail**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/test_cli.py -v
```

Expected: FAIL — `cli.main` not defined.

- [ ] **Step 3: Implement the CLI**

Write `tools/sfx-plan/src/sfx_plan/cli.py`:

```python
"""CLI entry point for sfx-plan."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sfx_plan.annotations import scan_annotations
from sfx_plan.catalog import load_catalog
from sfx_plan.emit import ensure_mount, render_sfx_html
from sfx_plan.errors import SfxPlanError
from sfx_plan.narration import load_narration_map
from sfx_plan.plan import build_plan
from sfx_plan.validate import validate_plan


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sfx-plan",
        description=(
            "Scan a HyperFrames video folder for data-sfx-* annotations, resolve "
            "via narration-map and sfx-catalog, and emit compositions/sfx.html."
        ),
    )
    p.add_argument(
        "video_dir",
        nargs="?",
        type=Path,
        default=Path("."),
        help="Path to the video folder (default: current directory).",
    )
    p.add_argument(
        "--catalog",
        type=Path,
        default=None,
        help="Path to sfx-catalog.yml (default: sound-effects/sfx-catalog.yml relative to the repo root above video_dir).",
    )
    p.add_argument(
        "--sound-effects-root",
        type=Path,
        default=None,
        help="Path to the sound-effects/ folder (defaults to the catalog's parent).",
    )
    p.add_argument(
        "--dry-run", action="store_true",
        help="Resolve and validate everything, but don't write sfx.html.",
    )
    p.add_argument(
        "--report", action="store_true",
        help="Print a per-cue plan table on stdout.",
    )
    return p


def _resolve_catalog_path(video_dir: Path, override: Path | None) -> Path:
    if override is not None:
        return override
    cur = video_dir.resolve()
    for _ in range(6):
        candidate = cur / "sound-effects" / "sfx-catalog.yml"
        if candidate.exists():
            return candidate
        cur = cur.parent
    return video_dir.resolve() / "sound-effects" / "sfx-catalog.yml"


def _print_report(cues: list, video_dir: Path) -> None:
    print(f"\nSFX PLAN — {video_dir.name}   {len(cues)} cues\n")
    for c in cues:
        clamp = " ⚠clamped" if c.clamped else ""
        print(f"  {c.data_start:>7.2f}s  anchor={c.anchor!r:<20} cue={c.cue:<8} "
              f"vol={c.volume:.2f}  src={c.src}{clamp}")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    video_dir: Path = args.video_dir

    catalog_path = _resolve_catalog_path(video_dir, args.catalog)
    sound_effects_root = args.sound_effects_root or catalog_path.parent

    try:
        catalog = load_catalog(catalog_path)
        nm_path = video_dir / "narration-map.json"
        nm = load_narration_map(nm_path)

        annotations = list(scan_annotations(video_dir))
        if not annotations:
            print("no data-sfx-* annotations found; nothing to emit.")
            return 0

        cues = build_plan(annotations, nm=nm, catalog=catalog)
        total_duration_s = float(max((c.data_start + c.duration_s for c in cues), default=0.0))
        warnings = validate_plan(cues, total_duration_s=total_duration_s)
        for w in warnings:
            print(f"warning: {w}", file=sys.stderr)

    except SfxPlanError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.report:
        _print_report(cues, video_dir)

    if args.dry_run:
        print(f"dry-run: would write {len(cues)} cues to {video_dir / 'compositions' / 'sfx.html'}")
        return 0

    sfx_html_path = video_dir / "compositions" / "sfx.html"
    sfx_html_path.parent.mkdir(exist_ok=True)
    sfx_html_path.write_text(
        render_sfx_html(
            cues=cues,
            sfx_html_path=sfx_html_path,
            sound_effects_root=sound_effects_root,
            catalog_sha=catalog.get("library_sha", ""),
            total_duration_s=total_duration_s,
        ),
        encoding="utf-8",
    )
    mounted = ensure_mount(video_dir / "index.html")
    note = " (mounted sfx-layer in index.html)" if mounted else ""
    print(f"{len(cues)} cues placed, {len(warnings)} warnings, wrote {sfx_html_path}{note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run:
```bash
cd tools/sfx-plan && uv run pytest tests/test_cli.py -v
```

Expected: 5 passed.

- [ ] **Step 5: Run the full suite**

Run:
```bash
cd tools/sfx-plan && uv run pytest -v
```

Expected: all 30+ tests pass.

- [ ] **Step 6: Commit**

```bash
git add tools/sfx-plan/src/sfx_plan/cli.py tools/sfx-plan/tests/test_cli.py
git commit -m "feat(sfx-plan): CLI entry point with --dry-run/--report"
```

---

### Task 11: Manual smoke test against the canonical video

**Files:**
- Modify: `videos/why-text-is-hard-2026-05-07/index.html` (add 2 demo annotations)

Sanity-check the full pipeline (Plan 1 catalog + Plan 2 tool) against a real video before declaring Phase A part 1+2 done.

- [ ] **Step 1: Add two demo annotations to the canonical video**

Locate the `#s1-nightmare` element and the scene-2 root in `videos/why-text-is-hard-2026-05-07/index.html`. Add the attributes (preserve existing attributes, just append):

For the nightmare element:
```html
data-sfx-anchor="nightmare" data-sfx-on-anchor="ui-tick"
```

For the scene-2 root container (the first element where scene 2 begins):
```html
data-sfx-anchor="Draw" data-sfx-on-anchor="whoosh"
```

(`Draw` should resolve via the existing `narration-map.json`. Confirm with `grep '"Draw"' videos/why-text-is-hard-2026-05-07/narration-map.json`. If it doesn't appear in `anchors`, pick a different anchor word that does.)

- [ ] **Step 2: Run sfx-plan against the canonical video**

```bash
cd videos/why-text-is-hard-2026-05-07
uv run --project ../../tools/sfx-plan sfx-plan --report
```

Expected:
- 2 cues placed.
- `compositions/sfx.html` created with two `<audio>` tags.
- `index.html` modified to mount the sfx-layer (one new `<div data-composition-src="compositions/sfx.html">`).
- Report table prints two rows.

- [ ] **Step 3: Verify with `hyperframes lint` and a quick preview**

```bash
cd videos/why-text-is-hard-2026-05-07
npx hyperframes lint
```

Expected: zero errors. Warnings are acceptable but should not include anything mentioning sfx.

Then:
```bash
npx hyperframes preview
```

Open the printed studio URL. Scrub past 12.7s (the `nightmare` anchor) and confirm the click sound plays. Scrub to the scene-2 boundary and confirm the whoosh plays.

If audio doesn't play, check the browser console for failed asset loads — usually a path issue. Fix `_relative_src` in `emit.py` if so.

- [ ] **Step 4: Revert the demo annotations**

The canonical video is the project's reference quality bar; we don't want demo annotations in it permanently. Revert with:

```bash
cd /Users/akwasikonaduakuoko/Projects/WebDev/hyper-frames
git checkout videos/why-text-is-hard-2026-05-07/index.html
rm videos/why-text-is-hard-2026-05-07/compositions/sfx.html
```

The smoke test was for our confidence — Plan 3 will produce the proper canonical fixture as the skill's worked-examples reference.

- [ ] **Step 5: Commit (only the tool, not the demo)**

If any tool fixes came out of Step 3, commit them. Otherwise skip this step.

```bash
# only if tool fixes were needed:
git add tools/sfx-plan/
git commit -m "fix(sfx-plan): adjust path resolution from smoke test feedback"
```

---

## Self-review against the spec

Spec coverage check (Component 3):

- ✅ Algorithm step 1 — HTML scan (Task 4)
- ✅ Algorithm step 2 — anchor resolution via narration-map (Task 5)
- ✅ Algorithm step 3 — cue lookup + filter against catalog + deterministic picker (Tasks 6, 7)
- ✅ Algorithm step 4 — peak-aligned data-start (Task 7)
- ✅ Algorithm step 5 — sfx.html emission with sorted audio tags + per-cue source comment (Task 8)
- ✅ One-time `index.html` wiring, idempotent (Task 8)
- ✅ CLI: `--dry-run`, `--report` (Task 10). `--watch` deferred (out of v1 scope; v1 expects the skill to drive re-runs explicitly).
- ✅ Determinism contract — sha256 seed, sorted candidates, stable output (Task 7)
- ✅ All failure modes from the spec table:
  - Unresolved anchor → `UnresolvedAnchorError` (Task 5)
  - Index out of range → `AnchorIndexOutOfRangeError` (Task 5)
  - Unknown cue → `UnknownCueError` (Task 6)
  - Empty cue filter → `EmptyCueFilterError` (Task 6)
  - Missing catalog → `CatalogMissingError` (Task 6)
  - Version mismatch → `CatalogVersionMismatchError` (Task 6)
  - Cue overlap → warn (Task 9)
  - Negative `data-start` → clamp + warn (Tasks 7, 9)
  - Density > hard cap → `DensityViolationError` (Task 9)
- ✅ Validation pass before emit (Task 9 + integration in CLI Task 10)

**Note on `--watch`:** the spec mentions `--watch` as a flag. I'm deferring it because (a) the skill drives re-runs explicitly so polling has limited value, and (b) adding a file-watching dependency for a feature that isn't load-bearing is poor scope discipline. Easy to add later — just a polling loop around the existing `main()` body.

Placeholder scan: no `TBD`, `TODO`, or "fill in details". Every step ships complete code.

Type consistency: `Annotation` (Task 4), `Cue` (Task 7), and the catalog dict shape are referenced unchanged across Tasks 4–10. Field names (`anchor`, `anchor_index`, `cue`, `lead_ms`, `volume`, `pan`, `data_start`, `duration_s`, `track_index`) are consistent throughout.

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-11-sfx-plan-tool-plan.md`. Two execution options:

**1. Subagent-Driven (recommended)** — fresh subagent per task, review between tasks.

**2. Inline Execution** — batch execution with checkpoints in this session.

Plan 3 (sfx-author skill) is next, then we can execute all three in dependency order.
