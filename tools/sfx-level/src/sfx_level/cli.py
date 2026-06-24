"""CLI entry point for sfx-level.

Probe the voiceover's loudness at a moment so you can see whether an SFX cue
lands in a real narration gap or on top of a spoken word. Two modes:

  sfx-level audio/voiceover.mp3 --at 12.84
  sfx-level audio/voiceover.mp3 --batch compositions/sfx.html

Advisory only. SFX volume is a fixed 0.4 hard peg, applied uniformly in
`tools/sfx-plan` (PEG_VOLUME) — every cue plays at 0.4 "no matter the sfx", and a
`data-sfx-volume` override is ignored. This tool no longer recommends a volume;
it reports the VO level and classifies the window (gap vs. active-speech) so you
can decide whether a cue's PLACEMENT is clean, not its loudness. A cue landing
over hot VO is fixed by retiming or rechoosing the cue, never by changing volume.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

from sfx_level.dsp import db, decode_pcm, rms_envelope, window_levels

SAMPLE_RATE = 22050
FRAME_MS = 20.0
HOP_MS = 10.0
GAP_MARGIN_DB = 8.0  # a window within +8 dB of the room-tone floor reads as a gap

_DATA_START = re.compile(r'data-start="([0-9.]+)"')
_ID_ATTR = re.compile(r'id="([^"]+)"')


class FloorRef:
    """Per-file loudness reference: the room-tone floor and a typical-speech level."""

    def __init__(self, pcm: np.ndarray, sample_rate: int) -> None:
        frame = max(int(FRAME_MS / 1000 * sample_rate), 1)
        hop = max(int(HOP_MS / 1000 * sample_rate), 1)
        rms, _ = rms_envelope(pcm, frame, hop)
        if rms.size == 0:
            self.floor_db = -120.0
            self.speech_db = -120.0
        else:
            self.floor_db = db(float(np.percentile(rms, 10)))
            self.speech_db = db(float(np.percentile(rms, 90)))
        self.gap_threshold_db = self.floor_db + GAP_MARGIN_DB


def classify(rms_db: float, ref: FloorRef) -> str:
    """Is this window a narration gap or active speech?"""
    return "gap" if rms_db < ref.gap_threshold_db else "active-speech"


def probe(pcm: np.ndarray, ref: FloorRef, t: float, window_ms: float) -> dict:
    """Advisory loudness probe at a moment. Reports the VO level and whether the
    window is a narration gap or active speech — no volume recommendation, since
    SFX volume is hard-pegged at 0.4 in tools/sfx-plan."""
    rms_db, peak_db = window_levels(pcm, SAMPLE_RATE, t, window_ms)
    return {
        "at_s": round(t, 4),
        "rms_dbfs": round(rms_db, 1),
        "peak_dbfs": round(peak_db, 1),
        "classification": classify(rms_db, ref),
    }


def _parse_cues(sfx_html: Path) -> list[tuple[str, float]]:
    """Return (id, data_start) for each cue behind a generated sfx.html.

    Prefers a sibling `sfx.cues.json` (written by `sfx-plan --bake`, when the
    HTML holds a single baked `<audio>` and per-cue timing lives only in the
    manifest). Falls back to scanning the `<audio>` tags of a per-cue sfx.html.
    """
    manifest = sfx_html.parent / "sfx.cues.json"
    if manifest.exists():
        data = json.loads(manifest.read_text(encoding="utf-8"))
        cues = [(c["id"], float(c["data_start"])) for c in data.get("cues", [])]
        return sorted(cues, key=lambda c: c[1])

    text = sfx_html.read_text(encoding="utf-8")
    cues: list[tuple[str, float]] = []
    for block in re.split(r"<audio", text)[1:]:
        ms = _DATA_START.search(block)
        if not ms:
            continue
        mid = _ID_ATTR.search(block)
        cues.append((mid.group(1) if mid else "?", float(ms.group(1))))
    return sorted(cues, key=lambda c: c[1])


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="sfx-level",
        description="Probe voiceover loudness at a timestamp (or every cue) for SFX placement.",
    )
    p.add_argument("voiceover", type=Path, help="Path to the voiceover audio (e.g. audio/voiceover.mp3).")
    p.add_argument("--at", type=float, default=None, help="Timestamp in seconds to probe.")
    p.add_argument(
        "--batch", type=Path, default=None,
        help="A generated compositions/sfx.html — report VO level at every cue's data-start.",
    )
    p.add_argument("--window-ms", type=float, default=120.0, help="Half-window radius in ms (default 120).")
    p.add_argument("--json", action="store_true", help="Emit JSON instead of a table.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    if args.at is None and args.batch is None:
        print("error: pass --at <seconds> or --batch <sfx.html>", file=sys.stderr)
        return 2
    if not args.voiceover.exists():
        print(f"error: voiceover not found: {args.voiceover}", file=sys.stderr)
        return 2

    pcm = decode_pcm(str(args.voiceover), SAMPLE_RATE)
    ref = FloorRef(pcm, SAMPLE_RATE)

    if args.batch is not None:
        if not args.batch.exists():
            print(f"error: sfx.html not found: {args.batch}", file=sys.stderr)
            return 2
        rows = [
            {"id": cid, **probe(pcm, ref, t, args.window_ms)}
            for cid, t in _parse_cues(args.batch)
        ]
        if args.json:
            print(json.dumps({"floor_dbfs": round(ref.floor_db, 1),
                              "speech_dbfs": round(ref.speech_db, 1), "cues": rows}, indent=2))
        else:
            print(f"\nVO floor {ref.floor_db:.1f} dBFS · typical speech {ref.speech_db:.1f} dBFS "
                  f"· gap < {ref.gap_threshold_db:.1f} dBFS\n")
            for r in rows:
                flag = "" if r["classification"] == "gap" else "  ⚠ over speech"
                print(f"  {r['at_s']:>7.2f}s  {r['rms_dbfs']:>6.1f} dBFS  "
                      f"{r['classification']:<13}{flag}  {r['id']}")
        return 0

    result = probe(pcm, ref, args.at, args.window_ms)
    if args.json:
        print(json.dumps({"floor_dbfs": round(ref.floor_db, 1),
                          "speech_dbfs": round(ref.speech_db, 1), **result}, indent=2))
    else:
        print(f"\n  at {result['at_s']}s   rms {result['rms_dbfs']} dBFS   peak {result['peak_dbfs']} dBFS")
        print(f"  → {result['classification']}   (volume is pegged at 0.4 — advisory only)")
        print(f"  ref: floor {ref.floor_db:.1f} dBFS · typical speech {ref.speech_db:.1f} dBFS\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
