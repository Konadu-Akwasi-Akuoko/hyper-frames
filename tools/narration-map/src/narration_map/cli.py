"""CLI entry point for narration-map."""

from __future__ import annotations

from pathlib import Path
import argparse
import json
import sys

from narration_map.core import (
    DEFAULT_EMPHATIC_TOP_N,
    DEFAULT_PAUSE_THRESHOLD_SECS,
    DEFAULT_SCENE_PAUSE_THRESHOLD_SECS,
    build_narration_map,
)


def _read_anchors(path: Path) -> list[str]:
    """One phrase per line. Blank lines and `#` comments are ignored."""
    phrases: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        phrases.append(line)
    return phrases


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="narration-map",
        description=(
            "Read a HyperFrames word-level transcript and emit a narration map: "
            "anchor words, pause windows, scene boundaries, emphatic words."
        ),
    )
    p.add_argument(
        "transcript",
        type=Path,
        help="Path to transcript.json (ElevenLabs Scribe shape).",
    )
    p.add_argument(
        "--anchors",
        type=Path,
        default=None,
        help="File with anchor phrases (one per line, # for comments).",
    )
    p.add_argument(
        "--pause-threshold",
        type=float,
        default=DEFAULT_PAUSE_THRESHOLD_SECS,
        metavar="SECS",
        help=f"Minimum gap between words to count as a pause (default: {DEFAULT_PAUSE_THRESHOLD_SECS}).",
    )
    p.add_argument(
        "--scene-pause-threshold",
        type=float,
        default=DEFAULT_SCENE_PAUSE_THRESHOLD_SECS,
        metavar="SECS",
        help=(
            "Minimum gap after a sentence-ending word (.!?) to count as a scene "
            f"boundary (default: {DEFAULT_SCENE_PAUSE_THRESHOLD_SECS})."
        ),
    )
    p.add_argument(
        "--emphatic-top-n",
        type=int,
        default=DEFAULT_EMPHATIC_TOP_N,
        metavar="N",
        help=f"Number of longest-duration words to surface (default: {DEFAULT_EMPHATIC_TOP_N}).",
    )
    p.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Where to write narration-map.json (default: alongside the transcript).",
    )
    p.add_argument(
        "--stdout",
        action="store_true",
        help="Write JSON to stdout instead of a file.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if not args.transcript.is_file():
        print(f"error: transcript not found: {args.transcript}", file=sys.stderr)
        return 1

    phrases: list[str] = []
    if args.anchors is not None:
        if not args.anchors.is_file():
            print(f"error: anchors file not found: {args.anchors}", file=sys.stderr)
            return 1
        phrases = _read_anchors(args.anchors)

    narration_map = build_narration_map(
        args.transcript,
        phrases=phrases,
        pause_threshold_secs=args.pause_threshold,
        scene_pause_threshold_secs=args.scene_pause_threshold,
        emphatic_top_n=args.emphatic_top_n,
    )

    payload = json.dumps(narration_map.to_dict(), indent=2)

    if args.stdout:
        print(payload)
        return 0

    output_path = args.output or args.transcript.with_name("narration-map.json")
    output_path.write_text(payload + "\n", encoding="utf-8")

    unmatched = [a.phrase for a in narration_map.anchors if not a.matches]
    print(
        f"narration-map: {narration_map.word_count} words, "
        f"{len(narration_map.pauses)} pauses (>{args.pause_threshold}s), "
        f"{len(narration_map.scene_boundaries)} scene boundaries (>{args.scene_pause_threshold}s after .!?), "
        f"{len(narration_map.emphatic_words)} emphatic words"
    )
    if phrases:
        matched = sum(1 for a in narration_map.anchors if a.matches)
        print(f"narration-map: {matched}/{len(phrases)} anchor phrases matched")
        if unmatched:
            print("narration-map: unmatched phrases:")
            for p in unmatched:
                print(f"  - {p!r}")
    print(f"narration-map: wrote {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
