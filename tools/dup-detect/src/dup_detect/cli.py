"""dup-detect CLI: find duplicate takes in a transcript and emit flagged cuts.

Standalone, the tool prints/writes only the duplicate cuts it finds. With
``--cuts`` it merges into an existing ``cuts.json`` from the audio-cut-decider
agent: every duplicate that the agent did not already cover is added (flagged),
existing cuts are preserved, and the whole list is re-sorted and re-numbered.
Run cut-snap afterwards to refine the bracketed boundaries onto true silence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import detect


def _overlaps(a: dict, b: dict) -> bool:
    return a["start"] < b["end"] and b["start"] < a["end"]


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Detect duplicate takes and emit them as flagged cuts."
    )
    ap.add_argument("transcript", help="Scribe v2 transcript.json")
    ap.add_argument(
        "--cuts",
        help="existing cuts.json to merge into (add only duplicates not already cut)",
    )
    ap.add_argument("-o", "--out", help="output path (default: print table only)")
    ap.add_argument(
        "--window",
        type=float,
        default=30.0,
        help="max seconds between the two takes' onsets (default: 30)",
    )
    ap.add_argument(
        "--min-words",
        type=int,
        default=3,
        help="minimum identical-word run length to count (default: 3)",
    )
    ap.add_argument(
        "--slack-margin",
        type=float,
        default=detect.DEFAULT_SLACK_MARGIN,
        help="keep the earlier take only if it is tighter by more than this many "
        "seconds; otherwise keep the later take (default: 0.15)",
    )
    ap.add_argument(
        "--pause-restart",
        type=float,
        default=detect.PAUSE_RESTART,
        help="re-take test: silence (s) before the 2nd take that marks a real "
        "redo; rhetorical cadence pauses are shorter (default: 0.7)",
    )
    ap.add_argument(
        "--long-match",
        type=int,
        default=detect.LONG_MATCH,
        help="re-take test: identical-word run length that is too long to be "
        "coincidental (default: 5)",
    )
    args = ap.parse_args()

    transcript = json.loads(Path(args.transcript).read_text())
    tokens = detect.word_tokens(transcript)
    dups = detect.find_duplicates(
        tokens,
        args.window,
        args.min_words,
        args.pause_restart,
        args.long_match,
    )
    dup_cuts = [detect.to_cut(d, tokens, args.slack_margin) for d in dups]

    existing: list[dict] = []
    if args.cuts:
        existing = json.loads(Path(args.cuts).read_text()).get("cuts", [])

    merged = [dict(c) for c in existing]
    added, skipped = [], []
    for dc in dup_cuts:
        if any(_overlaps(dc, ec) for ec in existing):
            skipped.append(dc)  # agent already cut this span
        else:
            merged.append(dc)
            added.append(dc)

    merged.sort(key=lambda c: c["start"])
    for n, c in enumerate(merged, 1):
        c["id"] = f"cut_{n:04d}"
    result = {"version": 1, "cuts": merged}

    print(f"detected {len(dups)} duplicate take(s):")
    for d, dc in zip(dups, dup_cuts):
        keep = "last" if d.keep_last(args.slack_margin) else "first"
        status = "skip (already cut)" if dc in skipped else "add"
        print(
            f'  [{status:18}] "{d.phrase}"  ({d.length} words)\n'
            f"      take A {tokens[d.a_lo].start:7.3f}-{tokens[d.a_hi].end:7.3f} "
            f"slack {d.a_slack*1000:5.0f}ms   "
            f"take B {tokens[d.b_lo].start:7.3f}-{tokens[d.b_hi].end:7.3f} "
            f"slack {d.b_slack*1000:5.0f}ms   -> keep {keep}\n"
            f"      cut {dc['start']:7.3f}-{dc['end']:7.3f}"
        )
    if args.cuts:
        print(
            f"\nmerge: {len(existing)} existing + {len(added)} added "
            f"({len(skipped)} already covered) = {len(merged)} total"
        )

    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=2))
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
