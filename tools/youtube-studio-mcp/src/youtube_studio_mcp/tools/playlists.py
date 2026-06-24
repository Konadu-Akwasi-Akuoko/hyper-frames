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


def _playlist_add_video(svc: Any, *, playlist_id: str, video_id: str,
                        position: int | None) -> dict:
    snippet: dict[str, Any] = {
        "playlistId": playlist_id,
        "resourceId": {"kind": "youtube#video", "videoId": video_id}}
    if position is not None:
        snippet["position"] = position
    resp = clients.run(
        lambda y: y.playlistItems().insert(part="snippet",
                                           body={"snippet": snippet}), svc)
    quota.record("playlistItems.insert")
    return {"item_added": resp.get("id"), "response": resp}


def _playlist_item_remove(svc: Any, item_id: str, confirm: bool) -> dict:
    refusal = gate.require(
        confirm, effect=f"This removes playlist item {item_id}.", item_id=item_id)
    if refusal:
        return refusal
    clients.run(lambda y: y.playlistItems().delete(id=item_id), svc)
    quota.record("playlistItems.delete")
    return {"item_removed": item_id, "quota_units_spent": 50}


def _playlist_set_image(svc: Any, *, playlist_id: str, file_path: str,
                        confirm: bool, media_factory) -> dict:
    """playlistImages.insert — square 1:1 JPEG/PNG <=2 MB."""
    refusal = gate.require(
        confirm,
        effect=f"This sets the cover image for playlist {playlist_id} (channel-visible).",
        playlist_id=playlist_id)
    if refusal:
        return refusal
    pre = uploadmedia.validate(file_path, max_bytes=MAX_PLAYLIST_IMAGE_BYTES,
                               allowed_mimes=IMAGE_MIMES)
    if not pre["ok"]:
        return pre
    media = media_factory(pre["path"], pre["mime"])
    body = {"snippet": {"playlistId": playlist_id, "type": "hero"}}
    request = svc.playlistImages().insert(part="snippet", body=body,
                                          media_body=media)
    resp = uploadmedia.execute_resumable(request)
    quota.record("playlistImages.insert")
    return {"image_set": resp.get("id"), "response": resp}


def _playlist_delete_image(svc: Any, image_id: str, confirm: bool) -> dict:
    refusal = gate.require(
        confirm, effect=f"This deletes playlist image {image_id}.",
        image_id=image_id)
    if refusal:
        return refusal
    clients.run(lambda y: y.playlistImages().delete(id=image_id), svc)
    quota.record("playlistImages.delete")
    return {"image_deleted": image_id, "quota_units_spent": 50}


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

    @app.tool()
    @clients.http_safe
    def playlist_add_video(playlist_id: str, video_id: str,
                           position: int | None = None) -> dict:
        """Add a video to a playlist. Quota: 50 units. Ungated. position is
        0-indexed (requires a manual-sort playlist)."""
        return _playlist_add_video(clients.youtube_data(),
                                   playlist_id=playlist_id, video_id=video_id,
                                   position=position)

    @app.tool()
    @clients.http_safe
    def playlist_item_remove(item_id: str, confirm: bool = False) -> dict:
        """Remove an item from a playlist. Quota: 50 units. Gated. item_id is the
        PLAYLIST ITEM id (from playlistItems.list), not the video id."""
        return _playlist_item_remove(clients.youtube_data(), item_id, confirm)

    @app.tool()
    @clients.http_safe
    def playlist_set_image(playlist_id: str, file_path: str,
                           confirm: bool = False) -> dict:
        """Set a playlist cover image (square 1:1 JPEG/PNG <=2 MB). Quota: 50
        units. Gated (channel-visible)."""
        return _playlist_set_image(
            clients.youtube_data(), playlist_id=playlist_id, file_path=file_path,
            confirm=confirm,
            media_factory=lambda p, m: MediaFileUpload(p, mimetype=m, resumable=True))

    @app.tool()
    @clients.http_safe
    def playlist_delete_image(image_id: str, confirm: bool = False) -> dict:
        """Delete a playlist cover image. Quota: 50 units. Gated: irreversible."""
        return _playlist_delete_image(clients.youtube_data(), image_id, confirm)
