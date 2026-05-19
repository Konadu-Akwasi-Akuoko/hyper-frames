"""Reporting API + local SQLite warehouse tools.

The Reporting API publishes one CSV per day per scheduled job, with ~24h lag
to first report and ~60 days of retention server-side. We mirror everything
into a local SQLite warehouse so long-range trend queries don't burn live
Analytics quota and survive video deletions.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .. import warehouse


def register(app: FastMCP) -> None:
    @app.tool()
    def report_types_list() -> dict:
        """Discover Reporting API report types available for this account."""
        return {"items": warehouse.list_report_types()}

    @app.tool()
    def report_jobs_list() -> dict:
        """List scheduled Reporting API jobs."""
        return {"items": warehouse.list_jobs()}

    @app.tool()
    def report_jobs_ensure_standard() -> dict:
        """Idempotently create the standard channel report jobs.

        Creates jobs for the 14 ``channel_*`` report types if they don't already
        exist. First CSV arrives ~24h after job creation; backfill is ~60 days.
        Safe to re-call.
        """
        created = warehouse.ensure_standard_jobs()
        return {"created": created, "created_count": len(created)}

    @app.tool()
    def report_job_delete(job_id: str) -> dict:
        """Delete a Reporting API job. Already-ingested data stays in the warehouse."""
        warehouse.delete_job(job_id)
        return {"deleted_job_id": job_id}

    @app.tool()
    def warehouse_sync() -> dict:
        """Download new CSVs from all jobs and ingest into the local warehouse.

        Idempotent — only fetches reports we haven't already seen. Wire this
        into cron/launchd for nightly updates.
        """
        n = warehouse.sync()
        return {"ingested_reports": n}

    @app.tool()
    def warehouse_status() -> dict:
        """Inspect warehouse state: jobs, last sync time, row counts per table."""
        return warehouse.warehouse_status_payload()

    @app.tool()
    def warehouse_query(sql: str, max_rows: int = 1000) -> dict:
        """Run a read-only SQL query against the local warehouse.

        Hot path for long-range trend questions ("how have my CTRs trended over
        18 months"). Validated: only a single ``SELECT``/``WITH``/``UNION`` is
        allowed; ``INSERT``/``UPDATE``/``DELETE``/``DROP``/``CREATE``/``ATTACH``/
        ``PRAGMA`` are refused. Connects in read-only mode regardless.

        Args:
            sql: SQLite-dialect SELECT.
            max_rows: 1-10000.
        """
        try:
            return warehouse.query(sql, max_rows=max(1, min(10000, max_rows)))
        except warehouse.SqlValidationError as e:
            return {"error": "sql_refused", "reason": str(e)}
