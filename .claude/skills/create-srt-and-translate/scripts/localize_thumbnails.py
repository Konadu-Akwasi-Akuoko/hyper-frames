#!/usr/bin/env python3
"""Localize thumbnail variant HTMLs and the per-language title text files.

Reads `<video-folder>/multi-lingual/translations.json` (authored by hand or
by the skill) and produces:

1. `<video-folder>/multi-lingual/thumbnail-title/<lang>.txt`
   Human-readable text bundle of round-1 + round-2 overlay + YT title for
   each variant. Used as copy-paste material for YouTube Studio's
   "translated titles & descriptions" pane.

2. `<video-folder>/multi-lingual/thumbnails/<lang>/{a,b,c}.html`
   Localized round-2 thumbnail HTML, ready to feed into the
   `tools/thumbnail-render/bin/render.mjs` renderer. The source HTML's
   icon SVG, grid overlay, font-size, and accent styling are preserved;
   only the three `<span class="thumbnail-row">` rows and the `<title>`
   are rewritten with the translation.

Accent regions in the translation are wrapped in `[[ ... ]]` per row;
they map onto `<span class="accent">...</span>` in the output.

Usage:
    python3 localize_thumbnails.py <video-folder> [--source-round round-2]

The default source round is round-2 (the canonical iteration for this
project). Pass a different round name if needed.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

VARIANTS = ("A", "B", "C")

ROW_RX = re.compile(
    r'(<span class="thumbnail-row[^"]*">)(.*?)(</span>)(?=\s*\n)',
)
TITLE_RX = re.compile(r"<title>[^<]*</title>")


def render_row_html(plain_row: str) -> str:
    """Convert `FOO [[BAR]] BAZ` into `FOO <span class="accent">BAR</span> BAZ`."""
    def sub(m: re.Match) -> str:
        return f'<span class="accent">{m.group(1)}</span>'

    return re.sub(r"\[\[(.+?)\]\]", sub, plain_row)


def strip_accent_markers(plain_row: str) -> str:
    return re.sub(r"\[\[(.+?)\]\]", r"\1", plain_row)


def localize_variant_html(source_html: str, rows: list[str], plain_title: str) -> str:
    """Rewrite the three thumbnail-row spans and the <title> with new content."""
    if len(rows) != 3:
        raise ValueError(f"expected 3 rows, got {len(rows)}: {rows}")

    rendered_rows = [render_row_html(r) for r in rows]
    row_iter = iter(rendered_rows)
    replaced_count = [0]

    def replace_row(m: re.Match) -> str:
        idx = replaced_count[0]
        replaced_count[0] += 1
        if idx >= 3:
            return m.group(0)
        new_inner = next(row_iter)
        return f"{m.group(1)}{new_inner}{m.group(3)}"

    out = ROW_RX.sub(replace_row, source_html, count=5)
    if replaced_count[0] < 3:
        raise RuntimeError(
            f"only replaced {replaced_count[0]} of 3 thumbnail-row spans"
        )

    out = TITLE_RX.sub(f"<title>{plain_title}</title>", out, count=1)
    return out


def write_title_text_file(out_path: Path, lang_name: str, video_folder: Path, lang_data: dict, source_round: str) -> None:
    lines: list[str] = []
    lines.append(f"# {lang_name} thumbnail titles")
    lines.append(f"# Source: {video_folder}/thumbnails/")
    lines.append("")

    for round_key, round_label in (("round_1", "round-1"), ("round_2", "round-2")):
        if round_key not in lang_data:
            continue
        lines.append(f"=== {round_label} ===")
        for letter in VARIANTS:
            variant = lang_data[round_key].get(letter)
            if not variant:
                continue
            if "overlay" in variant:
                overlay = variant["overlay"]
            elif "rows" in variant:
                rows = [strip_accent_markers(r) for r in variant["rows"]]
                overlay = " ".join(rows)
            else:
                overlay = ""
            yt = variant.get("yt_title", "")
            lines.append(f"[{letter}] OVERLAY:  {overlay}")
            lines.append(f"    YT TITLE: {yt}")
        lines.append("")

    lines.append(f"# Image source for renders: thumbnails/{source_round}/")
    lines.append("")
    out_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Localize thumbnail HTMLs and title files")
    ap.add_argument("video_folder", type=Path)
    ap.add_argument("--source-round", default="round-2", help="Round directory to localize (default: round-2)")
    args = ap.parse_args()

    video_folder: Path = args.video_folder.resolve()
    translations_path = video_folder / "multi-lingual" / "translations.json"
    if not translations_path.exists():
        print(f"error: {translations_path} not found", file=sys.stderr)
        return 1

    data = json.loads(translations_path.read_text(encoding="utf-8"))
    languages = data.get("languages") or {}
    if not languages:
        print("error: translations.json has no 'languages' key", file=sys.stderr)
        return 1

    source_round_dir = video_folder / "thumbnails" / args.source_round
    if not source_round_dir.is_dir():
        print(f"error: source round dir not found: {source_round_dir}", file=sys.stderr)
        return 1

    source_html: dict[str, str] = {}
    for letter in VARIANTS:
        path = source_round_dir / f"{letter.lower()}.html"
        if not path.exists():
            print(f"error: source variant not found: {path}", file=sys.stderr)
            return 1
        source_html[letter] = path.read_text(encoding="utf-8")

    title_dir = video_folder / "multi-lingual" / "thumbnail-title"
    title_dir.mkdir(parents=True, exist_ok=True)

    thumbs_root = video_folder / "multi-lingual" / "thumbnails"
    thumbs_root.mkdir(parents=True, exist_ok=True)

    written_html = 0
    written_titles = 0

    for lang_code, lang_data in sorted(languages.items()):
        lang_name = lang_data.get("name", lang_code)

        title_path = title_dir / f"{lang_code}.txt"
        write_title_text_file(title_path, lang_name, video_folder, lang_data, args.source_round)
        written_titles += 1

        round_2 = lang_data.get("round_2")
        if not round_2:
            continue
        lang_html_dir = thumbs_root / lang_code
        lang_html_dir.mkdir(parents=True, exist_ok=True)

        for letter in VARIANTS:
            variant = round_2.get(letter)
            if not variant or "rows" not in variant:
                continue
            rows = variant["rows"]
            plain_title = " ".join(strip_accent_markers(r) for r in rows)
            out_html = localize_variant_html(source_html[letter], rows, plain_title)
            out_path = lang_html_dir / f"{letter.lower()}.html"
            out_path.write_text(out_html, encoding="utf-8")
            written_html += 1

    print(f"wrote {written_titles} thumbnail-title text files -> {title_dir}")
    print(f"wrote {written_html} localized thumbnail HTML files -> {thumbs_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
