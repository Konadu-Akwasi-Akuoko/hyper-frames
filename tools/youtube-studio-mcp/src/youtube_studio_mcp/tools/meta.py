"""Self-diagnosis tools: auth_status, quota_status, cost_preview.

These never error on missing credentials — they're the first calls Claude
should make when something downstream returns ``authRequired``.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .. import auth, clients, quota


def register(app: FastMCP) -> None:
    @app.tool()
    def auth_status() -> dict:
        """Report whether credentials are loaded and which scopes are granted.

        Always returns a structured payload — never raises. Use this first when
        diagnosing 401/403 errors from any other tool.

        Returns:
            ``{ authorized: bool, reason?: str, scopes_granted?: [str],
            token_expires_at?: str, token_path: str, channel_id?: str,
            channel_title?: str }``
        """
        s = auth.get_status()
        out: dict[str, Any] = {
            "authorized": s.authorized,
            "token_path": s.token_path,
        }
        if s.reason:
            out["reason"] = s.reason
        if s.scopes_granted:
            out["scopes_granted"] = s.scopes_granted
        if s.token_expires_at:
            out["token_expires_at"] = s.token_expires_at
        if s.authorized:
            try:
                ch = clients.run(
                    lambda y: y.channels().list(part="id,snippet", mine=True),
                    clients.youtube_data(),
                )
                quota.record("channels.list")
                items = ch.get("items") or []
                if items:
                    out["channel_id"] = items[0]["id"]
                    out["channel_title"] = items[0]["snippet"]["title"]
            except Exception as e:
                out["channel_lookup_error"] = str(e)
        return out

    @app.tool()
    def quota_status() -> dict:
        """Report current Data API v3 spend for today (Pacific Time).

        YouTube quotas reset at midnight PT. The local ledger tracks every Data
        API call this server has made today; Analytics and Reporting APIs use
        separate quotas and are effectively unbounded for a single creator.

        Returns:
            ``{ data_api_spent_today, data_api_remaining, data_api_cap,
            day_pt, day_resets_at }``
        """
        return quota.status()

    @app.tool()
    def cost_preview(endpoint: str, multiplier: int = 1) -> dict:
        """Estimate the Data API quota cost of an endpoint without executing.

        Use before any bulk operation (comment moderation, batched updates) so
        the user can see what's about to be spent.

        Args:
            endpoint: Dotted Data API endpoint name, e.g. ``comments.setModerationStatus``.
            multiplier: How many calls of this endpoint you intend to make.

        Returns:
            ``{ endpoint, multiplier, estimated_cost, remaining_before,
            remaining_after, would_exceed_cap }``
        """
        return quota.preview(endpoint, multiplier=multiplier)
