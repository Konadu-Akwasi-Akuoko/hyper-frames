"""yt-dlp plumbing — pure argv builders kept separate from the subprocess
runners (the inspo-ingest convention). Metadata + top comments only. Serial and
bounded by the caller (cli.py) — never bursts (bot-wall discipline, spec §7.4)."""

from __future__ import annotations

import json
import subprocess
from typing import Any


def channel_videos_argv(channel_url: str, n: int) -> list[str]:
    """Recent videos of a channel as one JSON object per line (no comments)."""
    return [
        "yt-dlp",
        "--skip-download",
        "--dump-json",
        "--playlist-end",
        str(n),
        "--ignore-errors",
        "--no-warnings",
        channel_url,
    ]


def comments_argv(video_url: str, max_comments: int) -> list[str]:
    """Top comments of one video (validated in the Task 0 feasibility spike).

    `max_comments=N,all,N,0` = N total, all parent pages, N top-level, 0 replies.
    """
    return [
        "yt-dlp",
        "--skip-download",
        "--no-warnings",
        "--write-comments",
        "--extractor-args",
        f"youtube:comment_sort=top;max_comments={max_comments},all,{max_comments},0",
        "--dump-single-json",
        video_url,
    ]


def parse_channel_videos(stdout: str, handle: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        vid = d.get("id")
        if not vid:
            continue
        rows.append(
            {
                "source": f"youtube:{handle}",
                "external_id": vid,
                "title": d.get("title") or "",
                "url": d.get("webpage_url") or f"https://www.youtube.com/watch?v={vid}",
                "payload": {
                    "kind": "video",
                    "handle": handle,
                    "channel": d.get("channel") or d.get("uploader"),
                    "views": d.get("view_count"),
                    "duration_s": d.get("duration"),
                    "upload_date": d.get("upload_date"),
                },
            }
        )
    return rows


def parse_comments(data: dict[str, Any], handle: str) -> dict[str, Any] | None:
    vid = data.get("id")
    if not vid:
        return None
    raw_comments = data.get("comments") or []
    comments = [
        {
            "text": (c.get("text") or "")[:600],
            "likes": c.get("like_count"),
            "author": c.get("author"),
        }
        for c in raw_comments
    ]
    return {
        "source": f"youtube-comments:{handle}",
        "external_id": vid,
        "title": data.get("title") or "",
        "url": data.get("webpage_url") or f"https://www.youtube.com/watch?v={vid}",
        "payload": {
            "kind": "comments",
            "handle": handle,
            "video_title": data.get("title"),
            "views": data.get("view_count"),
            "comment_count": data.get("comment_count"),
            "comments": comments,
        },
    }


def _yt_err(proc: subprocess.CompletedProcess[str]) -> str:
    tail = (proc.stderr or "").strip().splitlines()[-1:] or ["unknown error"]
    return f"yt-dlp exit {proc.returncode}: {tail[0]}"


def fetch_channel_videos(
    channel_url: str, handle: str, n: int, timeout: int = 300
) -> tuple[list[dict[str, Any]], str | None]:
    try:
        proc = subprocess.run(
            channel_videos_argv(channel_url, n),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return [], f"timeout after {timeout}s"
    except FileNotFoundError:
        return [], "yt-dlp not found on PATH"
    if proc.returncode != 0 and not proc.stdout.strip():
        return [], _yt_err(proc)
    return parse_channel_videos(proc.stdout, handle), None


def fetch_comments(
    video_url: str, handle: str, max_comments: int, timeout: int = 180
) -> tuple[dict[str, Any] | None, str | None]:
    try:
        proc = subprocess.run(
            comments_argv(video_url, max_comments),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, f"timeout after {timeout}s"
    except FileNotFoundError:
        return None, "yt-dlp not found on PATH"
    if proc.returncode != 0 or not proc.stdout.strip():
        return None, _yt_err(proc)
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return None, "comment JSON parse failed"
    return parse_comments(data, handle), None
