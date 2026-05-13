#!/usr/bin/env python3
"""Convert a Scribe v2 transcript.json into an SRT caption file.

Chunking rules (see references/srt-chunking-rules.md for the why):
- Max 84 characters per block (~42 chars * 2 lines).
- Max 7.0 seconds per block.
- Min 1.2 seconds on screen (prevents flash for short utterances).
- Prefer breaks at sentence-end punctuation (.!?) once a block has
  enough material (>= ~4 words or >= 25 chars).
- Long blocks wrap onto two lines at a space near the midpoint.

Usage:
    python3 transcript_to_srt.py <transcript.json> [-o captions.srt]

The default output path is captions.srt next to the input file.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MAX_CHARS = 84
MAX_DUR = 7.0
MIN_DUR = 1.2
SENT_END = re.compile(r'[.!?]["\')\]]?$')


def fmt_ts(seconds: float) -> str:
    ms = int(round(seconds * 1000))
    h, ms = divmod(ms, 3_600_000)
    m, ms = divmod(ms, 60_000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def wrap_two_lines(text: str, soft_limit: int = 42) -> str:
    if len(text) <= soft_limit:
        return text
    mid = len(text) // 2
    left = text.rfind(" ", 0, mid + 1)
    right = text.find(" ", mid)
    if left == -1 and right == -1:
        return text
    if left == -1:
        split = right
    elif right == -1:
        split = left
    else:
        split = left if (mid - left) <= (right - mid) else right
    return text[:split].rstrip() + "\n" + text[split + 1:].lstrip()


def chunk_words(words: list[dict]) -> list[tuple[float, float, str]]:
    blocks: list[tuple[float, float, str]] = []
    cur: list[dict] = []
    cur_chars = 0

    def flush() -> None:
        nonlocal cur, cur_chars
        if not cur:
            return
        text = " ".join(w["text"] for w in cur).strip()
        start = cur[0]["start"]
        end = cur[-1]["end"]
        if end - start < MIN_DUR:
            end = start + MIN_DUR
        blocks.append((start, end, text))
        cur = []
        cur_chars = 0

    for w in words:
        tok = w["text"]
        add_len = len(tok) + (1 if cur else 0)
        next_chars = cur_chars + add_len
        dur_so_far = (w["end"] - cur[0]["start"]) if cur else 0.0
        will_overflow = next_chars > MAX_CHARS or dur_so_far > MAX_DUR

        if will_overflow and cur:
            flush()
            cur.append(w)
            cur_chars = len(tok)
            continue

        cur.append(w)
        cur_chars = next_chars

        if SENT_END.search(tok) and (len(cur) >= 4 or cur_chars >= 25):
            flush()

    flush()
    return blocks


def render_srt(blocks: list[tuple[float, float, str]]) -> str:
    parts: list[str] = []
    for i, (start, end, text) in enumerate(blocks, 1):
        parts.append(str(i))
        parts.append(f"{fmt_ts(start)} --> {fmt_ts(end)}")
        parts.append(wrap_two_lines(text))
        parts.append("")
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description="Scribe v2 transcript.json -> SRT")
    ap.add_argument("transcript", type=Path, help="Path to transcript.json")
    ap.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output SRT path (default: captions.srt next to transcript.json)",
    )
    args = ap.parse_args()

    if not args.transcript.exists():
        print(f"error: transcript not found: {args.transcript}", file=sys.stderr)
        return 1

    data = json.loads(args.transcript.read_text())
    words = [w for w in data["words"] if w["type"] == "word"]
    if not words:
        print("error: no word entries found in transcript", file=sys.stderr)
        return 1

    blocks = chunk_words(words)
    out = render_srt(blocks)

    output = args.output or args.transcript.parent / "captions.srt"
    output.write_text(out)
    print(f"wrote {output}: {len(blocks)} blocks, {len(out)} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
