"""Tests for cue parsing — prefer the bake manifest, fall back to the <audio> regex."""
from __future__ import annotations

import json
from pathlib import Path

from sfx_level.cli import _parse_cues


_PER_CUE_HTML = """<!doctype html>
<html><body><template id="sfx-layer-template"><div data-composition-id="sfx-layer">
  <audio id="sfx-002-boom-foo" class="clip" data-start="3.0" data-track-index="22" src="../assets/sfx/boom.wav"></audio>
  <audio id="sfx-001-ui-tick-foo" class="clip" data-start="1.5" data-track-index="20" src="../assets/sfx/click.wav"></audio>
</div></template></body></html>
"""

_BAKED_HTML = """<!doctype html>
<html><body><template id="sfx-layer-template"><div data-composition-id="sfx-layer">
  <audio id="sfx-mix" class="clip" data-start="0" data-track-index="19" src="../audio/sfx-mix.mp3"></audio>
</div></template></body></html>
"""


def test_regex_fallback_reads_per_cue_html(tmp_path: Path) -> None:
    sfx = tmp_path / "sfx.html"
    sfx.write_text(_PER_CUE_HTML, encoding="utf-8")
    cues = _parse_cues(sfx)
    # Sorted by data_start, ids recovered from the tags.
    assert cues == [("sfx-001-ui-tick-foo", 1.5), ("sfx-002-boom-foo", 3.0)]


def test_manifest_preferred_over_single_baked_audio(tmp_path: Path) -> None:
    sfx = tmp_path / "sfx.html"
    sfx.write_text(_BAKED_HTML, encoding="utf-8")  # holds only the baked element
    (tmp_path / "sfx.cues.json").write_text(
        json.dumps({
            "version": 1,
            "total_duration_s": 60.0,
            "cues": [
                {"id": "sfx-002-boom-foo", "data_start": 3.0},
                {"id": "sfx-001-ui-tick-foo", "data_start": 1.5},
            ],
        }),
        encoding="utf-8",
    )
    cues = _parse_cues(sfx)
    # Recovers all per-cue timing from the manifest, not the single baked <audio>.
    assert cues == [("sfx-001-ui-tick-foo", 1.5), ("sfx-002-boom-foo", 3.0)]
