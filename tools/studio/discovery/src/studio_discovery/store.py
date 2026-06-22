"""SQLite writer for raw_signal — stdlib sqlite3, WAL, same file the Hono server
owns. Writes only raw_signal (judged_at = NULL); never touches ideas/board."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any, Iterable

from .ids import raw_signal_id

RAW_SCHEMA = """
CREATE TABLE IF NOT EXISTS raw_signal (
  id             TEXT PRIMARY KEY,
  source         TEXT NOT NULL,
  external_id    TEXT NOT NULL,
  title          TEXT,
  url            TEXT,
  payload_json   TEXT NOT NULL,
  fetched_at     TEXT NOT NULL,
  judged_at      TEXT,
  judged_verdict TEXT
);
CREATE INDEX IF NOT EXISTS idx_raw_unjudged ON raw_signal(judged_at) WHERE judged_at IS NULL;
"""


def open_db(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    if path != ":memory:":
        conn.execute("PRAGMA journal_mode = WAL;")
    conn.executescript(RAW_SCHEMA)
    conn.commit()
    return conn


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def upsert_raw(conn: sqlite3.Connection, rows: Iterable[dict[str, Any]]) -> int:
    """INSERT OR IGNORE normalized rows. Returns the count newly inserted."""
    now = _now()
    inserted = 0
    for r in rows:
        rid = raw_signal_id(r["source"], r["external_id"])
        cur = conn.execute(
            "INSERT OR IGNORE INTO raw_signal "
            "(id,source,external_id,title,url,payload_json,fetched_at) "
            "VALUES (?,?,?,?,?,?,?)",
            (
                rid,
                r["source"],
                r["external_id"],
                r.get("title"),
                r.get("url"),
                json.dumps(r.get("payload") or {}, ensure_ascii=False),
                now,
            ),
        )
        inserted += cur.rowcount
    conn.commit()
    return inserted


def read_active_channels(conn: sqlite3.Connection) -> list[tuple[str, str | None]]:
    """(handle, url) for active channels, or [] if the table doesn't exist yet."""
    try:
        cur = conn.execute(
            "SELECT handle, url FROM channels WHERE active=1 ORDER BY handle"
        )
        return [(row[0], row[1]) for row in cur.fetchall()]
    except sqlite3.OperationalError:
        return []
