"""SQLite-backed result cache for read endpoints.

Keyed by ``(endpoint, params_hash, day_bucket)``. Daily aggregates from the
YouTube APIs don't change after their day closes in PT, so closed-day rows are
cached indefinitely; today's bucket expires after 15 minutes to keep the model's
view fresh while still amortizing repeated calls within a single Claude turn.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import sqlite3
from contextlib import contextmanager
from typing import Any, Iterator

from . import paths, quota

CURRENT_DAY_TTL_SECONDS = 15 * 60


def params_hash(params: Any) -> str:
    payload = json.dumps(params, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@contextmanager
def _conn() -> Iterator[sqlite3.Connection]:
    paths.ensure_config_dir()
    db = paths.config_dir() / "cache.db"
    conn = sqlite3.connect(db)
    try:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS results ("
            "  endpoint TEXT NOT NULL,"
            "  params_hash TEXT NOT NULL,"
            "  day_bucket TEXT NOT NULL,"
            "  is_current_day INTEGER NOT NULL,"
            "  stored_at TEXT NOT NULL,"
            "  payload TEXT NOT NULL,"
            "  PRIMARY KEY (endpoint, params_hash, day_bucket)"
            ")"
        )
        yield conn
        conn.commit()
    finally:
        conn.close()


def _now_utc() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def _is_current_day(day_bucket: str) -> bool:
    today_pt = quota._today_pt()  # noqa: SLF001 — same package
    return day_bucket == today_pt


def get(endpoint: str, params: Any, day_bucket: str | None = None) -> Any | None:
    """Return cached payload or ``None`` if missing/expired."""
    bucket = day_bucket or quota._today_pt()  # noqa: SLF001
    ph = params_hash(params)
    with _conn() as c:
        row = c.execute(
            "SELECT is_current_day, stored_at, payload FROM results "
            "WHERE endpoint = ? AND params_hash = ? AND day_bucket = ?",
            (endpoint, ph, bucket),
        ).fetchone()
    if row is None:
        return None
    is_current, stored_at, payload = row
    if is_current:
        age = (_now_utc() - dt.datetime.fromisoformat(stored_at)).total_seconds()
        if age > CURRENT_DAY_TTL_SECONDS:
            return None
    return json.loads(payload)


def put(endpoint: str, params: Any, payload: Any, day_bucket: str | None = None) -> None:
    bucket = day_bucket or quota._today_pt()  # noqa: SLF001
    ph = params_hash(params)
    is_current = 1 if _is_current_day(bucket) else 0
    with _conn() as c:
        c.execute(
            "INSERT OR REPLACE INTO results(endpoint, params_hash, day_bucket, "
            "is_current_day, stored_at, payload) VALUES (?, ?, ?, ?, ?, ?)",
            (endpoint, ph, bucket, is_current, _now_utc().isoformat(),
             json.dumps(payload, default=str)),
        )


def clear() -> int:
    """Drop the entire cache. Returns rows deleted."""
    with _conn() as c:
        before = c.execute("SELECT COUNT(*) FROM results").fetchone()[0]
        c.execute("DELETE FROM results")
    return int(before)
