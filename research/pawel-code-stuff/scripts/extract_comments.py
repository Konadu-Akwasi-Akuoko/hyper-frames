"""Extract comments from yt-dlp info.json files into clean per-video JSON
plus a flat aggregate CSV for cross-video analysis.

Per-comment fields written:
  id, parent, depth, text, like_count, author, is_uploader, is_pinned,
  reply_count (for top-level), timestamps_cited (regex on body), char_len.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

TIMESTAMP_RE = re.compile(r"\b(\d{1,2}):([0-5]\d)(?::([0-5]\d))?\b")


def find_timestamps(text: str) -> list[str]:
    return [m.group(0) for m in TIMESTAMP_RE.finditer(text or "")]


def extract_video(info_path: Path) -> dict:
    data = json.loads(info_path.read_text(encoding="utf-8"))
    video_id = data.get("id")
    title = data.get("title")
    raw_comments = data.get("comments") or []

    # Build reply counts per top-level comment
    reply_counts: dict[str, int] = {}
    for c in raw_comments:
        parent = c.get("parent") or "root"
        if parent != "root":
            reply_counts[parent] = reply_counts.get(parent, 0) + 1

    # Compute depth (only top-level=0 vs. reply=1 in YT)
    cleaned: list[dict] = []
    for c in raw_comments:
        parent = c.get("parent") or "root"
        depth = 0 if parent == "root" else 1
        text = (c.get("text") or "").strip()
        cleaned.append({
            "id": c.get("id"),
            "parent": parent,
            "depth": depth,
            "text": text,
            "like_count": c.get("like_count") or 0,
            "author": c.get("author"),
            "is_uploader": bool(c.get("author_is_uploader")),
            "is_pinned": bool(c.get("is_pinned")),
            "reply_count": reply_counts.get(c.get("id"), 0),
            "timestamps_cited": find_timestamps(text),
            "char_len": len(text),
        })

    return {
        "video_id": video_id,
        "title": title,
        "view_count": data.get("view_count"),
        "like_count": data.get("like_count"),
        "comment_count_total": data.get("comment_count"),
        "comment_count_pulled": len(cleaned),
        "comments": cleaned,
    }


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    raw_dir = root / "comments" / "raw"
    clean_dir = root / "comments" / "clean"
    clean_dir.mkdir(parents=True, exist_ok=True)

    info_files = sorted(raw_dir.glob("*.info.json"))
    if not info_files:
        print(f"No .info.json files found in {raw_dir}", file=sys.stderr)
        return 1

    aggregate_rows: list[dict] = []
    summary_rows: list[dict] = []

    for src in info_files:
        slug = src.name.removesuffix(".info.json")
        record = extract_video(src)
        out_json = clean_dir / f"{slug}.comments.json"
        out_json.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")

        comments = record["comments"]
        top_level = [c for c in comments if c["depth"] == 0]
        replies = [c for c in comments if c["depth"] == 1]

        for c in comments:
            aggregate_rows.append({
                "video_slug": slug,
                "video_id": record["video_id"],
                "comment_id": c["id"],
                "depth": c["depth"],
                "parent": c["parent"],
                "author": c["author"],
                "is_uploader": int(c["is_uploader"]),
                "is_pinned": int(c["is_pinned"]),
                "like_count": c["like_count"],
                "reply_count": c["reply_count"],
                "char_len": c["char_len"],
                "timestamps_cited": "|".join(c["timestamps_cited"]),
                "text": c["text"].replace("\n", " "),
            })

        summary_rows.append({
            "slug": slug,
            "video_id": record["video_id"],
            "title": record["title"],
            "views": record["view_count"],
            "likes": record["like_count"],
            "total_comments_on_yt": record["comment_count_total"],
            "comments_pulled": record["comment_count_pulled"],
            "top_level": len(top_level),
            "replies": len(replies),
            "uploader_replies": sum(1 for c in comments if c["is_uploader"]),
            "pinned": sum(1 for c in comments if c["is_pinned"]),
            "comments_with_timestamp_cite": sum(1 for c in comments if c["timestamps_cited"]),
        })

        print(f"{slug}: pulled={len(comments)} top={len(top_level)} replies={len(replies)} "
              f"uploader_replies={summary_rows[-1]['uploader_replies']} "
              f"with_ts_cite={summary_rows[-1]['comments_with_timestamp_cite']}")

    # Write aggregate CSV
    agg_csv = clean_dir / "_all-comments.csv"
    if aggregate_rows:
        fieldnames = list(aggregate_rows[0].keys())
        with agg_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(aggregate_rows)

    # Write summary CSV
    sum_csv = clean_dir / "_summary.csv"
    if summary_rows:
        fieldnames = list(summary_rows[0].keys())
        with sum_csv.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(summary_rows)

    print()
    print(f"Aggregate CSV: {agg_csv} ({len(aggregate_rows)} rows)")
    print(f"Summary CSV:   {sum_csv} ({len(summary_rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
