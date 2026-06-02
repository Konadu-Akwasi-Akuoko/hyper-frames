"""cut-snap CLI: refine cut boundaries onto true silence plateau edges.

The audio-cut-decider agent decides WHICH word-span to cut (judgment); this
tool places the exact boundaries (DSP). For each cut it finds the silence
plateau flanking the removed span and lands the boundary at the plateau edge —
keeping the previous word's decay and the next word's lead-in — then snaps to a
zero-crossing. Where there is no detectable silence (words run together) it
falls back to the deterministic capped-pad rule.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import dsp

PAD = 0.30  # capped-pad fallback ceiling, seconds


def _words(transcript: dict[str, Any]) -> list[dict[str, Any]]:
    return [w for w in transcript["words"] if w["type"] == "word"]


def _span(cut: dict[str, Any], words: list[dict[str, Any]]):
    """Return (first_removed, last_removed, kept_before, kept_after) for a cut."""
    s, e = cut["start"], cut["end"]
    removed = [w for w in words if w["start"] < e and w["end"] > s]
    if not removed:
        return None
    before = [w for w in words if w["end"] <= removed[0]["start"]]
    after = [w for w in words if w["start"] >= removed[-1]["end"]]
    return removed[0], removed[-1], (before[-1] if before else None), (
        after[0] if after else None
    )


def _capped(edge: float, other: float, sign: int) -> float:
    """Capped-pad fallback: edge +/- min(PAD, gap/2)."""
    gap = abs(other - edge)
    return edge + sign * min(PAD, gap / 2)


def snap_cut(
    cut: dict[str, Any],
    words: list[dict[str, Any]],
    x,
    sr: int,
    args: argparse.Namespace,
    duration: float,
) -> dict[str, Any]:
    """Return a copy of `cut` with start/end refined to silence plateau edges."""
    out = dict(cut)
    span = _span(cut, words)
    if span is None:
        return out
    first_rm, last_rm, kept_before, kept_after = span

    # The plateau edge (or the transcript label, on fallback) is the true word
    # edge; capped-pad then leaves a breath of silence between it and the cut.
    if kept_before is not None:
        edge = dsp.plateau_edge(
            x, sr, kept_before["end"], first_rm["start"], kept_before["end"],
            "forward", args.floor_db, args.frame_ms, args.hop_ms, args.sustain_ms,
        )
        anchor = edge if edge is not None else kept_before["end"]
        new_s = _capped(anchor, first_rm["start"], +1)
        new_s = dsp.nearest_zero_crossing(x, sr, new_s, args.zero_cross_ms)
    else:
        new_s = max(0.0, first_rm["start"] - PAD)

    if kept_after is not None:
        edge = dsp.plateau_edge(
            x, sr, last_rm["end"], kept_after["start"], kept_after["start"],
            "backward", args.floor_db, args.frame_ms, args.hop_ms, args.sustain_ms,
        )
        anchor = edge if edge is not None else kept_after["start"]
        new_e = _capped(anchor, last_rm["end"], -1)
        new_e = dsp.nearest_zero_crossing(x, sr, new_e, args.zero_cross_ms)
    else:
        new_e = min(duration, last_rm["end"] + PAD)

    out["start"] = round(max(0.0, new_s), 6)
    out["end"] = round(min(duration, new_e), 6)
    return out


def _dedupe(cuts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort by start and clamp any overlap introduced by snapping."""
    cuts = sorted(cuts, key=lambda c: c["start"])
    for prev, cur in zip(cuts, cuts[1:]):
        if cur["start"] < prev["end"]:
            cur["start"] = prev["end"]
    return [c for c in cuts if c["end"] > c["start"]]


def main() -> None:
    ap = argparse.ArgumentParser(description="Refine cut boundaries onto silence.")
    ap.add_argument("transcript", help="Scribe v2 transcript.json")
    ap.add_argument("cuts", help="cuts.json from the audio-cut-decider agent")
    ap.add_argument("audio", help="source audio (raw.mp3) on the cuts' timeline")
    ap.add_argument("-o", "--out", help="output path (default: print table only)")
    ap.add_argument("--sample-rate", type=int, default=16000)
    ap.add_argument("--floor-db", type=float, default=8.0,
                    help="dB above the per-gap RMS floor to call speech")
    ap.add_argument("--frame-ms", type=float, default=10.0)
    ap.add_argument("--hop-ms", type=float, default=5.0)
    ap.add_argument("--sustain-ms", type=float, default=20.0,
                    help="silence must persist this long to count as the floor")
    ap.add_argument("--zero-cross-ms", type=float, default=5.0)
    args = ap.parse_args()

    transcript = json.loads(Path(args.transcript).read_text())
    cuts = json.loads(Path(args.cuts).read_text())
    words = _words(transcript)
    duration = float(transcript["audio_duration_secs"])
    x = dsp.decode_pcm(args.audio, args.sample_rate)

    snapped = _dedupe([
        snap_cut(c, words, x, args.sample_rate, args, duration) for c in cuts["cuts"]
    ])
    result = {"version": 1, "cuts": snapped}

    print(f"{'id':10} {'before':>17}   {'after':>17}   Δstart  Δend")
    for a, b in zip(cuts["cuts"], snapped):
        print(f"{a['id']:10} {a['start']:7.3f}-{a['end']:7.3f}   "
              f"{b['start']:7.3f}-{b['end']:7.3f}   "
              f"{b['start']-a['start']:+.3f} {b['end']-a['end']:+.3f}")

    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=2))
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
