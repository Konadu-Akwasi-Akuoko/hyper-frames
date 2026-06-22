"""studio-discover — serial, bounded raw-signal fetch into studio.db.

Decides nothing (no scoring, no judgment). Each source is isolated: one dead
source or walled channel logs and continues, never crashing the run. yt-dlp is
strictly serial with `--sleep`-paced gaps (bot-wall discipline, spec §7.4)."""

from __future__ import annotations

import argparse
import sys
import time
from typing import Callable

from . import aggregators, store, youtube

# Seed list (spec §7.1). Used when neither --channels nor a db channels table is
# available. CleoAbram is mined from /shorts.
DEFAULT_CHANNELS: list[tuple[str, str | None]] = [
    ("@Shadeofcode", None),
    ("@devforgehq", None),
    ("@Fireship", None),
    ("@thecodingkoalaa", None),
    ("@technetiumm", None),
    ("@TheCodingSloth", None),
    ("@awesome-coding", None),
    ("@codehead01", None),
    ("@SwagProfessorExplain", None),
    ("@Latticx", None),
    ("@CleoAbram", "shorts"),
    ("@ByteByteGo", None),
    ("@pawel_code_stuff", None),
    ("@CodeSource", None),
]


def channel_url(handle: str, kind: str | None = None) -> str:
    seg = "shorts" if kind == "shorts" else "videos"
    return f"https://www.youtube.com/{handle}/{seg}"


def _safe(fn: Callable[[], int], label: str) -> int:
    try:
        return fn()
    except Exception as e:  # one dead source never fails the run
        print(f"[{label}] failed: {e}", file=sys.stderr)
        return 0


def resolve_channels(
    channels_arg: str | None, conn
) -> list[tuple[str, str | None]]:
    if channels_arg:
        out: list[tuple[str, str | None]] = []
        for raw in channels_arg.split(","):
            h = raw.strip()
            if not h:
                continue
            out.append((h if h.startswith("@") else f"@{h}", None))
        return out
    db_ch = store.read_active_channels(conn)
    if db_ch:
        return [
            (h, "shorts" if "/shorts" in (u or "") else None) for (h, u) in db_ch
        ]
    return DEFAULT_CHANNELS


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="studio-discover",
        description="Fetch raw signal into studio.db raw_signal (zero AI).",
    )
    ap.add_argument("--db", required=True, help="path to studio.db")
    ap.add_argument(
        "--sources",
        default="youtube,hn,reddit,lobsters,dailydev",
        help="comma list of sources to run",
    )
    ap.add_argument("--channels", default=None, help="comma handles override")
    ap.add_argument("--videos-per-channel", type=int, default=15)
    ap.add_argument("--comments-per-video", type=int, default=30)
    ap.add_argument(
        "--comments-from-top",
        type=int,
        default=5,
        help="fetch comments for the top N videos per channel",
    )
    ap.add_argument("--no-comments", action="store_true")
    ap.add_argument("--max-channels", type=int, default=None)
    ap.add_argument("--sleep", type=float, default=2.0, help="pause between yt-dlp calls")
    args = ap.parse_args(argv)

    sources = {s.strip() for s in args.sources.split(",") if s.strip()}
    conn = store.open_db(args.db)
    summary: dict[str, int] = {}

    if "hn" in sources:
        summary["hn"] = _safe(lambda: store.upsert_raw(conn, aggregators.fetch_hn()), "hn")
    if "reddit" in sources:
        summary["reddit"] = _safe(
            lambda: store.upsert_raw(conn, aggregators.fetch_reddit()), "reddit"
        )
    if "lobsters" in sources:
        summary["lobsters"] = _safe(
            lambda: store.upsert_raw(conn, aggregators.fetch_lobsters()), "lobsters"
        )
    if "dailydev" in sources:
        summary["dailydev"] = _safe(
            lambda: store.upsert_raw(conn, aggregators.fetch_dailydev()), "dailydev"
        )

    if "youtube" in sources:
        channels = resolve_channels(args.channels, conn)
        if args.max_channels:
            channels = channels[: args.max_channels]
        yt_videos = 0
        yt_comments = 0
        for i, (handle, kind) in enumerate(channels):
            url = channel_url(handle, kind)
            vids, err = youtube.fetch_channel_videos(
                url, handle, args.videos_per_channel
            )
            if err:
                print(f"[youtube] {handle}: {err}", file=sys.stderr)
            yt_videos += store.upsert_raw(conn, vids)
            print(f"[youtube] {handle}: {len(vids)} videos", file=sys.stderr)

            if not args.no_comments and vids:
                for v in vids[: args.comments_from_top]:
                    time.sleep(args.sleep)
                    crow, cerr = youtube.fetch_comments(
                        v["url"], handle, args.comments_per_video
                    )
                    if cerr:
                        # walled / age-gated video → metadata-only, keep going
                        print(
                            f"[youtube-comments] {handle}/{v['external_id']}: {cerr}",
                            file=sys.stderr,
                        )
                        continue
                    if crow:
                        yt_comments += store.upsert_raw(conn, [crow])
            if i < len(channels) - 1:
                time.sleep(args.sleep)
        summary["youtube:videos"] = yt_videos
        summary["youtube:comments"] = yt_comments

    conn.close()

    print("discovery complete:")
    for k, v in summary.items():
        print(f"  {k}: +{v}")
    print(f"  total new raw_signal: +{sum(summary.values())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
