"""Parse YouTube json3 auto-caption files into clean and timed transcripts.

YouTube json3 format: events[] each with optional segs[] of {utf8, tOffsetMs}.
Each seg's absolute time = event.tStartMs + seg.tOffsetMs.
Newline-only segs are layout breaks, not words.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def fmt_ts(ms: int) -> str:
    s, ms_rem = divmod(int(ms), 1000)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h:02d}:{m:02d}:{s:02d}.{ms_rem:03d}"
    return f"{m:02d}:{s:02d}.{ms_rem:03d}"


def extract_words(path: Path) -> list[tuple[int, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    words: list[tuple[int, str]] = []
    for event in data.get("events", []):
        segs = event.get("segs")
        if not segs:
            continue
        t_start = event.get("tStartMs", 0)
        for seg in segs:
            text = seg.get("utf8", "")
            if not text or text == "\n":
                continue
            t_abs = t_start + seg.get("tOffsetMs", 0)
            words.append((t_abs, text))
    return words


def write_clean(words: list[tuple[int, str]], out_path: Path) -> None:
    raw = "".join(w for _, w in words).strip()
    # Sentence-ish line wrapping: break after . ? ! and after long commas
    out_lines: list[str] = []
    buf: list[str] = []
    sentence_terminators = (".", "?", "!")
    for token in raw.replace("\n", " ").split(" "):
        if not token:
            continue
        buf.append(token)
        if token.endswith(sentence_terminators):
            out_lines.append(" ".join(buf).strip())
            buf = []
    if buf:
        out_lines.append(" ".join(buf).strip())
    out_path.write_text("\n".join(out_lines) + "\n", encoding="utf-8")


def write_timed(words: list[tuple[int, str]], out_path: Path, window_s: float = 5.0) -> None:
    """Group words into ~window_s chunks, prefix each chunk with [mm:ss]."""
    lines: list[str] = []
    buf: list[str] = []
    chunk_start: int | None = None
    window_ms = int(window_s * 1000)
    for t, w in words:
        if chunk_start is None:
            chunk_start = t
        # Flush at sentence boundary OR after window elapses
        buf.append(w)
        elapsed = t - chunk_start
        text_so_far = "".join(buf)
        if elapsed >= window_ms and text_so_far.rstrip().endswith((".", "?", "!")):
            lines.append(f"[{fmt_ts(chunk_start)}] {text_so_far.strip()}")
            buf = []
            chunk_start = None
    if buf and chunk_start is not None:
        lines.append(f"[{fmt_ts(chunk_start)}] {''.join(buf).strip()}")
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    raw_dir = root / "transcripts" / "raw"
    clean_dir = root / "transcripts" / "clean"
    timed_dir = root / "transcripts" / "timed"
    clean_dir.mkdir(parents=True, exist_ok=True)
    timed_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(raw_dir.glob("*.en.json3"))
    if not files:
        print(f"No .en.json3 files found in {raw_dir}", file=sys.stderr)
        return 1

    for src in files:
        slug = src.name.removesuffix(".en.json3")
        words = extract_words(src)
        clean_out = clean_dir / f"{slug}.txt"
        timed_out = timed_dir / f"{slug}.txt"
        write_clean(words, clean_out)
        write_timed(words, timed_out, window_s=5.0)
        n_words = len(words)
        first_t = words[0][0] if words else 0
        last_t = words[-1][0] if words else 0
        runtime_s = (last_t - first_t) / 1000.0
        wpm = n_words / (runtime_s / 60.0) if runtime_s else 0.0
        print(
            f"{slug}: {n_words} words | runtime ~{runtime_s:6.1f}s | {wpm:5.1f} wpm | "
            f"-> {clean_out.name}, {timed_out.name}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
