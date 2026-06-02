#!/usr/bin/env python3
"""Deterministic boundary snapper for cut-decider output.

The agent picks WHICH word-span to cut (judgment). This snaps each cut's
boundaries into the flanking silence valley (arithmetic), using the capped-pad
rule validated against the human grader:

    pad       = min(0.30, gap / 2)
    cut.start = last_kept_word.end    + pad   # leave kept decay; start in silence
    cut.end   = first_kept_word.start - pad   # leave next lead-in; end in silence

Usage: snap_boundaries.py <transcript.json> <cuts.json> [out.json]
Prints a before -> after table; writes snapped cuts to out.json (default stdout-only).
"""

import json
import sys
from pathlib import Path

PAD = 0.30


def snap(transcript: dict, cuts: dict) -> dict:
    words = [w for w in transcript["words"] if w["type"] == "word"]
    dur = transcript["audio_duration_secs"]
    out = []
    for c in cuts["cuts"]:
        s, e = c["start"], c["end"]
        removed = [w for w in words if w["start"] < e and w["end"] > s]
        if not removed:
            out.append(dict(c))
            continue
        first_rm, last_rm = removed[0], removed[-1]
        kept_before = [w for w in words if w["end"] <= first_rm["start"]]
        kept_after = [w for w in words if w["start"] >= last_rm["end"]]

        if kept_before:
            gap = first_rm["start"] - kept_before[-1]["end"]
            new_s = kept_before[-1]["end"] + min(PAD, max(gap, 0) / 2)
        else:
            new_s = max(0.0, first_rm["start"] - PAD)

        if kept_after:
            gap = kept_after[0]["start"] - last_rm["end"]
            new_e = kept_after[0]["start"] - min(PAD, max(gap, 0) / 2)
        else:
            new_e = min(dur, last_rm["end"] + PAD)

        snapped = dict(c)
        snapped["start"] = round(new_s, 6)
        snapped["end"] = round(new_e, 6)
        out.append(snapped)
    return {"version": 1, "cuts": out}


def main() -> None:
    transcript = json.loads(Path(sys.argv[1]).read_text())
    cuts = json.loads(Path(sys.argv[2]).read_text())
    snapped = snap(transcript, cuts)
    print(f"{'id':10} {'before':>17}   {'after':>17}   Δstart  Δend")
    for a, b in zip(cuts["cuts"], snapped["cuts"]):
        print(f"{a['id']:10} {a['start']:7.3f}-{a['end']:7.3f}   "
              f"{b['start']:7.3f}-{b['end']:7.3f}   "
              f"{b['start']-a['start']:+.3f} {b['end']-a['end']:+.3f}")
    if len(sys.argv) > 3:
        Path(sys.argv[3]).write_text(json.dumps(snapped, indent=2))
        print(f"\nwrote {sys.argv[3]}")


if __name__ == "__main__":
    main()
