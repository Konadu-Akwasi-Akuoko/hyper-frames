"""CLI entry point for youtube-seo.

Reads a topic from --topic or from outline.md H1 in CWD. Runs the
autocomplete pass + yt-dlp top-N pull, computes signals, writes the
research artifact to <output>/research.json (default <cwd>/seo/research.json).

Exits non-zero on yt-dlp soft-block or when output already exists without --force.
"""

from __future__ import annotations

from pathlib import Path
import argparse
import re
import sys

from youtube_seo.autocomplete import fetch_seed_and_expanded
from youtube_seo.output import build_payload, write_atomic
from youtube_seo.search import YtDlpSoftBlock, fetch_top_videos

DEFAULT_N = 30
DEFAULT_OUTPUT_RELATIVE = Path("seo") / "research.json"

H1_TOPIC_RE = re.compile(r"^#\s+(.+?)\s*(?:—|--)\s*9-beat outline\s*$", re.MULTILINE)


def _read_topic_from_outline(outline_path: Path) -> str | None:
    """Extract the topic from a script-writer outline.md H1.

    H1 shape: '# <topic> — 9-beat outline' (em dash) or '# <topic> -- 9-beat outline'.
    Returns None if the file is missing or the H1 doesn't match.
    """
    if not outline_path.is_file():
        return None
    text = outline_path.read_text(encoding="utf-8")
    match = H1_TOPIC_RE.search(text)
    return match.group(1).strip() if match else None


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="seo-research",
        description=(
            "Mine YouTube autocomplete + top-N video metadata for a topic into "
            "a structured SEO research artifact at <output>/research.json."
        ),
    )
    p.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Explicit topic phrase. If omitted, reads outline.md H1 in CWD.",
    )
    p.add_argument(
        "--n",
        type=int,
        default=DEFAULT_N,
        help=f"Number of top videos to fetch via ytsearchN (default: {DEFAULT_N}).",
    )
    p.add_argument(
        "--region",
        type=str,
        default="us",
        help="Autocomplete region (gl param). Default: us.",
    )
    p.add_argument(
        "--hl",
        type=str,
        default="en",
        help="Autocomplete language (hl param). Default: en.",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Output JSON path. Default: <cwd>/seo/research.json. "
            "Parent directory created if missing."
        ),
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing output file. Default: refuse and exit non-zero.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    cwd = Path.cwd()
    output_path = args.output or (cwd / DEFAULT_OUTPUT_RELATIVE)

    if output_path.exists() and not args.force:
        try:
            import json as _json

            generated_at = _json.loads(output_path.read_text()).get("generated_at", "?")
        except Exception:
            generated_at = "?"
        print(
            f"seo-research: {output_path} already exists "
            f"(generated {generated_at}). Use --force to regenerate.",
            file=sys.stderr,
        )
        return 1

    topic = args.topic or _read_topic_from_outline(cwd / "outline.md")
    if not topic:
        print(
            "seo-research: no --topic given and could not extract one from "
            "outline.md (H1 must match '# <topic> — 9-beat outline').",
            file=sys.stderr,
        )
        return 1

    print(f"seo-research: topic = {topic!r}")
    print(f"seo-research: fetching autocomplete (seed + a-z, ~10s)...")
    autocomplete = fetch_seed_and_expanded(topic, region=args.region, hl=args.hl)
    if autocomplete.failed:
        print("seo-research: autocomplete pass failed; continuing with videos only.")

    print(f"seo-research: fetching top {args.n} videos via yt-dlp (~10s)...")
    try:
        videos = fetch_top_videos(topic, n=args.n)
    except YtDlpSoftBlock as exc:
        print(f"seo-research: {exc}", file=sys.stderr)
        return 2

    print(f"seo-research: assembling payload + writing {output_path}")
    payload = build_payload(
        topic=topic,
        autocomplete=autocomplete,
        videos=videos,
        region=args.region,
        hl=args.hl,
        n=args.n,
    )
    write_atomic(payload, output_path)

    nouns = payload["signals"]["top_nouns"]
    print(
        f"seo-research: done. {len(videos)} videos, "
        f"{sum(1 for s in (autocomplete.expanded.values() if not autocomplete.failed else []) if s)} non-empty letter expansions, "
        f"{len(nouns)} top nouns, {len(payload['signals']['saturation_warnings'])} saturation warnings."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
