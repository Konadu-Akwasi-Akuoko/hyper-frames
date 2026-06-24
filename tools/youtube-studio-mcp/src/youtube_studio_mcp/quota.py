"""Per-day Data API quota ledger.

The YouTube Data API v3 enforces a daily cap (default 10,000 units) that
resets at midnight Pacific Time. We track every call locally in
``quota.db`` so we can:

- Report current spend to the model via ``quota_status``.
- Preview the cost of a write before executing it (``cost_preview``).
- Refuse bulk writes that would exceed a configurable safety threshold.

Cost values come from
<https://developers.google.com/youtube/v3/determine_quota_cost>.
"""

from __future__ import annotations

import datetime as dt
import sqlite3
from contextlib import contextmanager
from typing import Iterator

from . import paths

DAILY_CAP_DEFAULT = 10_000
PT_OFFSET_HOURS = -8  # Pacific Standard Time. YouTube uses PT for quota reset.

# Per-call cost in units. Read endpoints are 1; writes are 50; search 100;
# captions are special. Keys are stable identifiers we use throughout the code.
COSTS: dict[str, int] = {
    # channels / videos / playlists reads
    "channels.list": 1,
    "videos.list": 1,
    "playlists.list": 1,
    "playlistItems.list": 1,
    "videoCategories.list": 1,
    "i18nLanguages.list": 1,
    "i18nRegions.list": 1,

    # writes
    "videos.insert": 1,  # 100/day Uploads bucket; 1 unit/call (NOT the 10k pool)
    "videos.delete": 50,
    "videos.update": 50,
    "videos.rate": 50,
    "videos.reportAbuse": 50,
    "videos.getRating": 1,
    "thumbnails.set": 50,

    # comments
    "commentThreads.list": 1,
    "commentThreads.insert": 50,
    "comments.list": 1,
    "comments.insert": 50,
    "comments.update": 50,
    "comments.setModerationStatus": 50,
    "comments.delete": 50,

    # captions (defer-to-v2 but documented for cost_preview)
    "captions.list": 50,
    "captions.download": 200,
    "captions.insert": 400,
    "captions.update": 450,
    "captions.delete": 50,

    # search — the trap
    "search.list": 100,

    # subscriptions
    "subscriptions.list": 50,
    "subscriptions.insert": 50,
    "subscriptions.delete": 50,

    # members
    "members.list": 1,

    # playlists / items / images
    "playlists.insert": 50,
    "playlists.update": 50,
    "playlists.delete": 50,
    "playlistItems.insert": 50,
    "playlistItems.update": 50,
    "playlistItems.delete": 50,
    "playlistImages.list": 1,
    "playlistImages.insert": 50,
    "playlistImages.update": 50,
    "playlistImages.delete": 50,

    # channel-level
    "channels.update": 50,
    "channelSections.list": 1,
    "channelSections.insert": 50,
    "channelSections.update": 50,
    "channelSections.delete": 50,
    "channelBanners.insert": 50,
    "watermarks.set": 50,
    "watermarks.unset": 50,
}


def _today_pt() -> str:
    """ISO date for the current day in Pacific Time."""
    now_utc = dt.datetime.now(dt.timezone.utc)
    pt = now_utc + dt.timedelta(hours=PT_OFFSET_HOURS)
    return pt.date().isoformat()


def _next_reset_iso() -> str:
    now_utc = dt.datetime.now(dt.timezone.utc)
    pt = now_utc + dt.timedelta(hours=PT_OFFSET_HOURS)
    next_pt = dt.datetime.combine(pt.date() + dt.timedelta(days=1),
                                   dt.time.min, tzinfo=dt.timezone.utc)
    return (next_pt - dt.timedelta(hours=PT_OFFSET_HOURS)).isoformat()


@contextmanager
def _conn() -> Iterator[sqlite3.Connection]:
    paths.ensure_config_dir()
    conn = sqlite3.connect(paths.quota_db_path())
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS spend ("
            "  day TEXT NOT NULL,"
            "  endpoint TEXT NOT NULL,"
            "  units INTEGER NOT NULL,"
            "  ts TEXT NOT NULL"
            ")"
        )
        conn.execute("CREATE INDEX IF NOT EXISTS spend_day_idx ON spend(day)")
        yield conn
        conn.commit()
    finally:
        conn.close()


def _cost_of(endpoint: str) -> tuple[int, bool]:
    """Internal: return (units, is_unknown).

    Unknown endpoints default to 1 unit but flag the caller so
    `cost_preview` can surface a warning instead of under-reporting silently.
    """
    if endpoint in COSTS:
        return COSTS[endpoint], False
    return 1, True


def cost_of(endpoint: str) -> int:
    """Look up the per-call quota cost for an endpoint. Unknown → 1."""
    return _cost_of(endpoint)[0]


def record(endpoint: str, multiplier: int = 1) -> int:
    """Record one call and return the units it cost."""
    units = cost_of(endpoint) * multiplier
    with _conn() as c:
        c.execute(
            "INSERT INTO spend(day, endpoint, units, ts) VALUES (?, ?, ?, ?)",
            (_today_pt(), endpoint, units, dt.datetime.now(dt.timezone.utc).isoformat()),
        )
    return units


def spent_today() -> int:
    with _conn() as c:
        row = c.execute(
            "SELECT COALESCE(SUM(units), 0) FROM spend WHERE day = ?",
            (_today_pt(),),
        ).fetchone()
    return int(row[0])


def remaining(cap: int = DAILY_CAP_DEFAULT) -> int:
    return max(0, cap - spent_today())


def status(cap: int = DAILY_CAP_DEFAULT) -> dict:
    s = spent_today()
    return {
        "data_api_spent_today": s,
        "data_api_remaining": max(0, cap - s),
        "data_api_cap": cap,
        "day_pt": _today_pt(),
        "day_resets_at": _next_reset_iso(),
    }


def preview(endpoint: str, multiplier: int = 1, cap: int = DAILY_CAP_DEFAULT) -> dict:
    cost_per, unknown = _cost_of(endpoint)
    cost = cost_per * multiplier
    rem = remaining(cap)
    out = {
        "endpoint": endpoint,
        "multiplier": multiplier,
        "estimated_cost": cost,
        "remaining_before": rem,
        "remaining_after": max(0, rem - cost),
        "would_exceed_cap": cost > rem,
    }
    if unknown:
        out["endpoint_unknown"] = True
        out["warning"] = (
            f"Unknown endpoint {endpoint!r}; defaulted cost to 1 unit. "
            "Check spelling against the YouTube Data API v3 endpoint list."
        )
    return out
