#!/usr/bin/env python3
"""Download top-N YouTube thumbnails per channel into thumbnailInspo/<slug>/.

Bot-wall discipline (this IP has tripped YouTube's tab-extractor wall before):
the only calls that hit YouTube's bot-walled tab extractor are ONE flat metadata
dump per channel, run strictly serially with a sleep between channels. The
thumbnail bitmaps themselves are pulled straight from the i.ytimg.com CDN with
curl — a plain image GET that is NOT bot-walled — so the bulk of the traffic
never touches the wall.

Ranking: for `videos` channels we read the channel's *Popular* system playlist
(``UULP`` + channel-id suffix), which YouTube returns view-sorted, so entry 0 is
the channel's single most-watched upload. For `shorts` channels we read the
``/shorts`` tab (newest-first; Shorts have no public popular sort).

Resumable: an already-present ``<rank>-<id>.jpg`` is skipped, so a re-run only
fills gaps. Deterministic apart from the live view-ranking and what each channel
has published — no RNG, no clock-derived output.

Usage:
    python3 tools/thumbnail-inspo/fetch.py [--count N] [--only slug,slug] [--list FILE]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LIB_DIR = REPO_ROOT / "thumbnailInspo"
DEFAULT_LIST = Path(__file__).resolve().parent / "channels.txt"

# CDN qualities tried in order; first one that returns a real bitmap wins.
THUMB_QUALITIES = ("maxresdefault", "sddefault", "hqdefault")
MIN_BYTES = 2000  # a 404/placeholder is a few hundred bytes; a real frame is >2KB
SLEEP_BETWEEN_CHANNELS = 4.0  # serial metadata pacing — bot-wall guard


def run(argv: list[str], timeout: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout)


def resolve_channel_id(handle: str) -> str | None:
    """Resolve an @handle to its UC… channel id via one cheap single-item dump."""
    cp = run([
        "yt-dlp", "--flat-playlist", "--playlist-items", "1",
        "--dump-single-json", "--sleep-requests", "1",
        f"https://www.youtube.com/@{handle}/videos",
    ])
    if cp.returncode != 0:
        return None
    try:
        data = json.loads(cp.stdout)
    except json.JSONDecodeError:
        return None
    return data.get("channel_id") or data.get("uploader_id")


def flat_entries(url: str, count: int) -> list[dict]:
    """Flat-dump up to `count` entries (id + title) from a playlist/tab URL."""
    cp = run([
        "yt-dlp", "--flat-playlist", "--playlist-end", str(count),
        "--dump-json", "--sleep-requests", "1", url,
    ])
    entries: list[dict] = []
    for line in cp.stdout.splitlines():
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
        entries.append({"id": vid, "title": (d.get("title") or "").strip()})
    return entries


def channel_targets(handle: str, mode: str, count: int) -> list[dict]:
    """Top-N entries for a channel, popularity-ranked for videos, newest for shorts."""
    if mode == "shorts":
        return flat_entries(f"https://www.youtube.com/@{handle}/shorts", count)

    cid = resolve_channel_id(handle)
    if cid and cid.startswith("UC"):
        popular = f"https://www.youtube.com/playlist?list=UULP{cid[2:]}"
        entries = flat_entries(popular, count)
        if entries:
            return entries
    # Fallbacks: uploads playlist, then the plain /videos tab (both newest-first).
    if cid and cid.startswith("UC"):
        uploads = f"https://www.youtube.com/playlist?list=UU{cid[2:]}"
        entries = flat_entries(uploads, count)
        if entries:
            return entries
    return flat_entries(f"https://www.youtube.com/@{handle}/videos", count)


def fetch_thumbnail(vid: str, dest: Path) -> tuple[bool, str]:
    """Pull the best available CDN thumbnail for a video id. Returns (ok, quality)."""
    if dest.exists() and dest.stat().st_size >= MIN_BYTES:
        return True, "cached"
    for q in THUMB_QUALITIES:
        url = f"https://i.ytimg.com/vi/{vid}/{q}.jpg"
        tmp = dest.with_suffix(".tmp")
        cp = run(["curl", "-fsSL", "-o", str(tmp), url], timeout=60)
        if cp.returncode == 0 and tmp.exists() and tmp.stat().st_size >= MIN_BYTES:
            tmp.replace(dest)
            return True, q
        if tmp.exists():
            tmp.unlink()
    return False, "missing"


def parse_channels(list_path: Path) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for line in list_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 3:
            continue
        rows.append((parts[0], parts[1], parts[2]))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--count", type=int, default=30, help="thumbnails per channel")
    ap.add_argument("--only", default="", help="comma-separated slugs to limit to")
    ap.add_argument("--list", default=str(DEFAULT_LIST), help="channel list file")
    args = ap.parse_args()

    only = {s.strip() for s in args.only.split(",") if s.strip()}
    channels = parse_channels(Path(args.list))
    if only:
        channels = [c for c in channels if c[2] in only]

    LIB_DIR.mkdir(parents=True, exist_ok=True)
    grand_total = 0

    for idx, (handle, mode, slug) in enumerate(channels):
        out_dir = LIB_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"\n=== [{idx + 1}/{len(channels)}] @{handle} ({mode}) -> {slug}/ ===",
              flush=True)
        try:
            entries = channel_targets(handle, mode, args.count)
        except subprocess.TimeoutExpired:
            print(f"  ! metadata timeout for @{handle}; skipping", flush=True)
            entries = []

        if not entries:
            print(f"  ! no entries resolved for @{handle}", flush=True)
        manifest = []
        got = 0
        for rank, e in enumerate(entries, start=1):
            fname = f"{rank:02d}-{e['id']}.jpg"
            dest = out_dir / fname
            ok, quality = fetch_thumbnail(e["id"], dest)
            if ok:
                got += 1
                manifest.append({
                    "rank": rank,
                    "id": e["id"],
                    "title": e["title"],
                    "file": fname,
                    "quality": quality,
                    "watch_url": f"https://www.youtube.com/watch?v={e['id']}",
                })
            else:
                print(f"  ! no thumbnail for {e['id']} ({e['title'][:40]})", flush=True)
        (out_dir / "_manifest.json").write_text(
            json.dumps({"handle": handle, "mode": mode, "slug": slug,
                        "items": manifest}, indent=2) + "\n")
        print(f"  got {got}/{len(entries)} thumbnails", flush=True)
        grand_total += got

        if idx < len(channels) - 1:
            time.sleep(SLEEP_BETWEEN_CHANNELS)

    print(f"\n=== DONE: {grand_total} thumbnails across {len(channels)} channels ===",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
