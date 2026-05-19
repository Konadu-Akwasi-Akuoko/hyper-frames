"""YouTube Reporting API → local SQLite warehouse.

The Reporting API publishes one CSV per day per scheduled job. After a job is
created it takes ~24h for the first CSV to appear; from then on a new CSV lands
daily and is available for ~60 days. We ingest each CSV exactly once into a
per-report-type table inside ``warehouse.db`` and track what we've already
imported in ``_synced_reports``.

SQL queries from the model run against a read-only SQLite handle through
``query()``, with a ``sqlglot``-based validator that allows ``SELECT`` only.
"""

from __future__ import annotations

import csv
import io
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator

import sqlglot
import sqlglot.expressions as exp
from google.auth.transport.requests import AuthorizedSession

from . import auth, clients, paths

logger = logging.getLogger(__name__)

STANDARD_CHANNEL_REPORT_TYPES: list[str] = [
    "channel_basic_a3",
    "channel_province_a3",
    "channel_playback_location_a3",
    "channel_traffic_source_a3",
    "channel_device_os_a3",
    "channel_demographics_a1",
    "channel_sharing_service_a2",
    "channel_annotations_a2",
    "channel_cards_a1",
    "channel_end_screens_a2",
    "channel_subtitles_a3",
    "channel_combined_a3",
    "channel_reach_basic_a1",
    "channel_reach_combined_a1",
]


@contextmanager
def _db(readonly: bool = False) -> Iterator[sqlite3.Connection]:
    paths.ensure_config_dir()
    db_path = paths.warehouse_db_path()
    if readonly:
        if not db_path.exists():
            db_path.touch()
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    else:
        conn = sqlite3.connect(db_path)
        conn.execute(
            "CREATE TABLE IF NOT EXISTS _synced_reports ("
            "  report_id TEXT PRIMARY KEY,"
            "  job_id TEXT NOT NULL,"
            "  report_type TEXT NOT NULL,"
            "  start_time TEXT,"
            "  end_time TEXT,"
            "  ingested_at TEXT NOT NULL,"
            "  row_count INTEGER NOT NULL"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS _meta ("
            "  key TEXT PRIMARY KEY,"
            "  value TEXT"
            ")"
        )
    try:
        yield conn
        if not readonly:
            conn.commit()
    finally:
        conn.close()


def list_report_types() -> list[dict]:
    """Discover available report types for this account."""
    resp = clients.run(
        lambda r: r.reportTypes().list(),
        clients.youtube_reporting(),
    )
    return resp.get("reportTypes") or []


def list_jobs() -> list[dict]:
    resp = clients.run(
        lambda r: r.jobs().list(),
        clients.youtube_reporting(),
    )
    return resp.get("jobs") or []


def create_job(report_type_id: str, name: str | None = None) -> dict:
    body = {"reportTypeId": report_type_id,
            "name": name or report_type_id}
    return clients.run(
        lambda r: r.jobs().create(body=body),
        clients.youtube_reporting(),
    )


def delete_job(job_id: str) -> None:
    clients.run(
        lambda r: r.jobs().delete(jobId=job_id),
        clients.youtube_reporting(),
    )


def ensure_standard_jobs() -> list[dict]:
    """Idempotently create the standard channel report jobs.

    Returns the list of jobs that were *created* (not the ones that already
    existed).
    """
    existing = {j["reportTypeId"]: j for j in list_jobs()}
    available = {rt["id"] for rt in list_report_types()}
    created: list[dict] = []
    for rtid in STANDARD_CHANNEL_REPORT_TYPES:
        if rtid in existing:
            continue
        if rtid not in available:
            logger.info("Report type %s not available for this account; skipping", rtid)
            continue
        created.append(create_job(rtid))
    return created


def list_reports_for_job(job_id: str, on_behalf_of_content_owner: str | None = None) -> list[dict]:
    kwargs = {"jobId": job_id}
    if on_behalf_of_content_owner:
        kwargs["onBehalfOfContentOwner"] = on_behalf_of_content_owner
    resp = clients.run(
        lambda r: r.jobs().reports().list(**kwargs),
        clients.youtube_reporting(),
    )
    return resp.get("reports") or []


def _table_name_for(report_type_id: str) -> str:
    return "".join(c if c.isalnum() or c == "_" else "_" for c in report_type_id)


def _ingest_csv(conn: sqlite3.Connection, report_type_id: str,
                csv_text: str) -> int:
    reader = csv.reader(io.StringIO(csv_text))
    try:
        headers = next(reader)
    except StopIteration:
        return 0
    table = _table_name_for(report_type_id)
    col_defs = ", ".join(f'"{h}" TEXT' for h in headers)
    conn.execute(f'CREATE TABLE IF NOT EXISTS "{table}" ({col_defs})')
    placeholders = ", ".join("?" for _ in headers)
    cols = ", ".join(f'"{h}"' for h in headers)
    rows = list(reader)
    if rows:
        conn.executemany(
            f'INSERT INTO "{table}" ({cols}) VALUES ({placeholders})',
            rows,
        )
    return len(rows)


def _download(url: str) -> str:
    creds = auth.load_credentials()
    session = AuthorizedSession(creds)
    r = session.get(url)
    r.raise_for_status()
    return r.text


def sync() -> int:
    """Pull every new report since the last sync. Returns reports ingested."""
    ingested = 0
    with _db() as conn:
        known = {row[0] for row in conn.execute(
            "SELECT report_id FROM _synced_reports").fetchall()}
        jobs = list_jobs()
        for job in jobs:
            job_id = job["id"]
            rtid = job["reportTypeId"]
            reports = list_reports_for_job(job_id)
            for rep in reports:
                rid = rep["id"]
                if rid in known:
                    continue
                try:
                    text = _download(rep["downloadUrl"])
                except Exception as e:
                    logger.warning("Failed to download report %s: %s", rid, e)
                    continue
                n = _ingest_csv(conn, rtid, text)
                conn.execute(
                    "INSERT INTO _synced_reports(report_id, job_id, report_type, "
                    "start_time, end_time, ingested_at, row_count) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (rid, job_id, rtid, rep.get("startTime"), rep.get("endTime"),
                     datetime.now(timezone.utc).isoformat(), n),
                )
                ingested += 1
        conn.execute(
            "INSERT OR REPLACE INTO _meta(key, value) VALUES (?, ?)",
            ("last_sync_at", datetime.now(timezone.utc).isoformat()),
        )
    return ingested


def warehouse_status_payload() -> dict:
    jobs = list_jobs()
    with _db(readonly=True) as conn:
        last_sync_row = conn.execute(
            "SELECT value FROM _meta WHERE key = 'last_sync_at'"
        ).fetchone()
        last_sync = last_sync_row[0] if last_sync_row else None
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE '\\_%' ESCAPE '\\'"
        ).fetchall()]
        counts: dict[str, int] = {}
        for t in tables:
            counts[t] = conn.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0]
    return {
        "jobs": [{"id": j["id"], "reportTypeId": j["reportTypeId"],
                  "name": j.get("name"), "createTime": j.get("createTime")}
                 for j in jobs],
        "last_sync_at": last_sync,
        "row_counts_by_table": counts,
    }


# -------- SQL validation + query --------------------------------------------

_DISALLOWED_NODES = (
    exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create, exp.Alter,
    exp.TruncateTable, exp.Pragma, exp.Attach, exp.Detach, exp.Command,
    exp.Transaction, exp.Commit, exp.Rollback,
)


class SqlValidationError(ValueError):
    """Raised when a query is not a single read-only SELECT."""


def _validate_select(sql: str) -> exp.Expression:
    try:
        parsed = sqlglot.parse(sql, read="sqlite")
    except Exception as e:
        raise SqlValidationError(f"could not parse SQL: {e}") from e
    parsed = [p for p in parsed if p is not None]
    if len(parsed) != 1:
        raise SqlValidationError("only a single statement is allowed")
    stmt = parsed[0]
    if not isinstance(stmt, (exp.Select, exp.Union, exp.With)):
        raise SqlValidationError(f"only SELECT/WITH/UNION allowed, got {type(stmt).__name__}")
    for node in stmt.walk():
        if isinstance(node, _DISALLOWED_NODES):
            raise SqlValidationError(f"disallowed expression: {type(node).__name__}")
    return stmt


def query(sql: str, max_rows: int = 1000) -> dict:
    """Run a validated read-only SELECT against the warehouse."""
    _validate_select(sql)
    with _db(readonly=True) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(sql)
        rows = [dict(r) for r in cur.fetchmany(max_rows)]
        columns = [d[0] for d in cur.description] if cur.description else []
        truncated = len(rows) == max_rows and cur.fetchone() is not None
    return {"columns": columns, "rows": rows, "truncated": truncated,
            "row_count": len(rows)}
