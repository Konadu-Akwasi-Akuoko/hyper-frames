"""Playlists + playlist items + playlist images.

All writes cost 50 units. playlistItems.insert needs both playlistId and
resourceId. PUT updates merge (re-send title). playlist delete + item remove +
image delete are gated.
Sources: https://developers.google.com/youtube/v3/docs/playlists
https://developers.google.com/youtube/v3/docs/playlistItems
https://developers.google.com/youtube/v3/docs/playlistImages
"""

from __future__ import annotations

from typing import Any

from googleapiclient.http import MediaFileUpload
from mcp.server.fastmcp import FastMCP

from .. import clients, gate, mutate, quota, uploadmedia

IMAGE_MIMES = {"image/jpeg", "image/png"}
MAX_PLAYLIST_IMAGE_BYTES = 2 * 1024 * 1024  # 2 MB, 1:1


def _playlist_create(svc: Any, *, title: str, description: str,
                     privacy: str) -> dict:
    body = {"snippet": {"title": title, "description": description},
            "status": {"privacyStatus": privacy}}
    resp = clients.run(
        lambda y: y.playlists().insert(part="snippet,status", body=body), svc)
    quota.record("playlists.insert")
    return {"playlist_created": resp.get("id"), "response": resp}


def _playlist_update(svc: Any, *, playlist_id: str, title: str | None,
                     description: str | None, privacy: str | None) -> dict:
    snippet: dict[str, Any] = {}
    if title is not None:
        snippet["title"] = title
    if description is not None:
        snippet["description"] = description
    patch: dict[str, Any] = {}
    if snippet:
        patch["snippet"] = snippet
    if privacy is not None:
        patch["status"] = {"privacyStatus": privacy}
    if not patch:
        return {"error": "no_changes_provided"}
    parts = ",".join(k for k in ("snippet", "status") if k in patch)
    try:
        resp = mutate.fetch_merge_update(
            svc, resource="playlists", id=playlist_id, parts=parts, patch=patch,
            record_list="playlists.list", record_update="playlists.update")
    except KeyError:
        return {"error": "playlist_not_found", "playlist_id": playlist_id}
    return {"playlist_updated": playlist_id, "response": resp}


def _playlist_delete(svc: Any, playlist_id: str, confirm: bool) -> dict:
    refusal = gate.require(
        confirm, effect=f"This permanently deletes playlist {playlist_id}.",
        playlist_id=playlist_id)
    if refusal:
        return refusal
    clients.run(lambda y: y.playlists().delete(id=playlist_id), svc)
    quota.record("playlists.delete")
    return {"playlist_deleted": playlist_id, "quota_units_spent": 50}


def register(app: FastMCP) -> None:
    @app.tool()
    @clients.http_safe
    def playlist_create(title: str, description: str = "",
                        privacy: str = "private") -> dict:
        """Create a playlist. Quota: 50 units. Ungated."""
        return _playlist_create(clients.youtube_data(), title=title,
                                description=description, privacy=privacy)

    @app.tool()
    @clients.http_safe
    def playlist_update(playlist_id: str, title: str | None = None,
                        description: str | None = None,
                        privacy: str | None = None) -> dict:
        """Edit a playlist's title/description/privacy (merge — unsent fields
        kept). Quota: ~51 units. Ungated."""
        return _playlist_update(clients.youtube_data(), playlist_id=playlist_id,
                                title=title, description=description, privacy=privacy)

    @app.tool()
    @clients.http_safe
    def playlist_delete(playlist_id: str, confirm: bool = False) -> dict:
        """Delete a playlist. Quota: 50 units. Gated: irreversible."""
        return _playlist_delete(clients.youtube_data(), playlist_id, confirm)
