"""Subscriptions — subscribe/unsubscribe AS the authenticated channel. Both
gated (a public social action). 50 units each.
Sources: https://developers.google.com/youtube/v3/docs/subscriptions/insert
https://developers.google.com/youtube/v3/docs/subscriptions/delete
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .. import clients, gate, quota


def _subscription_add(svc: Any, channel_id: str, confirm: bool) -> dict:
    refusal = gate.require(
        confirm, effect=f"This subscribes your channel to {channel_id} (public).",
        channel_id=channel_id)
    if refusal:
        return refusal
    body = {"snippet": {"resourceId": {"kind": "youtube#channel",
                                       "channelId": channel_id}}}
    resp = clients.run(
        lambda y: y.subscriptions().insert(part="snippet", body=body), svc)
    quota.record("subscriptions.insert")
    return {"subscribed": resp.get("id"), "channel_id": channel_id,
            "response": resp}


def _subscription_remove(svc: Any, subscription_id: str, confirm: bool) -> dict:
    refusal = gate.require(
        confirm, effect=f"This unsubscribes (subscription {subscription_id}).",
        subscription_id=subscription_id)
    if refusal:
        return refusal
    clients.run(lambda y: y.subscriptions().delete(id=subscription_id), svc)
    quota.record("subscriptions.delete")
    return {"unsubscribed": subscription_id, "quota_units_spent": 50}


def register(app: FastMCP) -> None:
    @app.tool()
    @clients.http_safe
    def subscription_add(channel_id: str, confirm: bool = False) -> dict:
        """Subscribe your channel to another channel. Quota: 50 units. Gated
        (public social action). channel_id is the target channel id."""
        return _subscription_add(clients.youtube_data(), channel_id, confirm)

    @app.tool()
    @clients.http_safe
    def subscription_remove(subscription_id: str, confirm: bool = False) -> dict:
        """Unsubscribe. Quota: 50 units. Gated. subscription_id is the
        SUBSCRIPTION id (from subscriptions.list), not the channel id."""
        return _subscription_remove(clients.youtube_data(), subscription_id, confirm)
