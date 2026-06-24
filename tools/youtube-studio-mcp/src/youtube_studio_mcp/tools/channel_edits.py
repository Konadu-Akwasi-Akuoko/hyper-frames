"""Channel-level writes: branding (channels.update), channel sections, and the
watermark unset. Banner + watermark uploads live in tools/uploads.py (Part E).

channels.update writable parts are restricted to brandingSettings / localizations
(NOT snippet); brandingSettings.channel.title must equal the current title or be
omitted. channelSections cap at 10 shelves.
Sources: https://developers.google.com/youtube/v3/docs/channels/update
https://developers.google.com/youtube/v3/docs/channelSections/insert
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .. import clients, gate, mutate, quota


def _channel_update_branding(svc: Any, *, channel_id: str,
                             description: str | None, keywords: str | None,
                             country: str | None, default_language: str | None,
                             confirm: bool) -> dict:
    """channels.update part=brandingSettings — gated, channel-wide, merge."""
    refusal = gate.require(
        confirm, effect=f"This updates channel {channel_id} branding (visible "
                        "channel-wide).", channel_id=channel_id)
    if refusal:
        return refusal
    channel_patch: dict[str, Any] = {}
    if description is not None:
        channel_patch["description"] = description
    if keywords is not None:
        channel_patch["keywords"] = keywords
    if country is not None:
        channel_patch["country"] = country
    if default_language is not None:
        channel_patch["defaultLanguage"] = default_language
    if not channel_patch:
        return {"error": "no_changes_provided"}
    try:
        resp = mutate.fetch_merge_update(
            svc, resource="channels", id=channel_id, parts="brandingSettings",
            patch={"brandingSettings": {"channel": channel_patch}},
            record_list="channels.list", record_update="channels.update")
    except KeyError:
        return {"error": "channel_not_found", "channel_id": channel_id}
    return {"branding_updated": channel_id, "response": resp}


def _channel_section_create(svc: Any, *, section_type: str,
                            title: str | None = None,
                            playlist_ids: list[str] | None = None) -> dict:
    snippet: dict[str, Any] = {"type": section_type}
    if title is not None:
        snippet["title"] = title
    body: dict[str, Any] = {"snippet": snippet}
    if playlist_ids:
        body["contentDetails"] = {"playlists": playlist_ids}
    part = "snippet,contentDetails" if playlist_ids else "snippet"
    resp = clients.run(
        lambda y: y.channelSections().insert(part=part, body=body), svc)
    quota.record("channelSections.insert")
    return {"section_created": resp.get("id"), "response": resp}


def _channel_section_update(svc: Any, *, section_id: str, section_type: str,
                            title: str | None,
                            playlist_ids: list[str] | None) -> dict:
    snippet: dict[str, Any] = {"type": section_type}
    if title is not None:
        snippet["title"] = title
    body: dict[str, Any] = {"id": section_id, "snippet": snippet}
    if playlist_ids:
        body["contentDetails"] = {"playlists": playlist_ids}
    part = "snippet,contentDetails" if playlist_ids else "snippet"
    resp = clients.run(
        lambda y: y.channelSections().update(part=part, body=body), svc)
    quota.record("channelSections.update")
    return {"section_updated": section_id, "response": resp}


def _channel_section_delete(svc: Any, section_id: str, confirm: bool) -> dict:
    refusal = gate.require(
        confirm, effect=f"This deletes channel section {section_id}.",
        section_id=section_id)
    if refusal:
        return refusal
    clients.run(lambda y: y.channelSections().delete(id=section_id), svc)
    quota.record("channelSections.delete")
    return {"section_deleted": section_id, "quota_units_spent": 50}


def _channel_unset_watermark(svc: Any, channel_id: str, confirm: bool) -> dict:
    refusal = gate.require(
        confirm, effect=f"This removes the watermark from channel {channel_id}.",
        channel_id=channel_id)
    if refusal:
        return refusal
    clients.run(lambda y: y.watermarks().unset(channelId=channel_id), svc)
    quota.record("watermarks.unset")
    return {"watermark_unset": channel_id, "quota_units_spent": 50}


def register(app: FastMCP) -> None:
    @app.tool()
    @clients.http_safe
    def channel_update_branding(channel_id: str, description: str | None = None,
                                keywords: str | None = None,
                                country: str | None = None,
                                default_language: str | None = None,
                                confirm: bool = False) -> dict:
        """Update channel branding (description/keywords/country/default
        language). Quota: ~51 units. Gated (channel-wide). Title is NOT editable
        via API and is preserved automatically. keywords is a space-separated
        string."""
        return _channel_update_branding(
            clients.youtube_data(), channel_id=channel_id, description=description,
            keywords=keywords, country=country, default_language=default_language,
            confirm=confirm)

    @app.tool()
    @clients.http_safe
    def channel_section_create(section_type: str, title: str | None = None,
                               playlist_ids: list[str] | None = None) -> dict:
        """Create a channel section/shelf (max 10). Quota: 50 units. Ungated.
        section_type e.g. multiplePlaylists, singlePlaylist; playlist_ids for
        playlist-backed shelves."""
        return _channel_section_create(clients.youtube_data(),
            section_type=section_type, title=title, playlist_ids=playlist_ids)

    @app.tool()
    @clients.http_safe
    def channel_section_update(section_id: str, section_type: str,
                               title: str | None = None,
                               playlist_ids: list[str] | None = None) -> dict:
        """Update a channel section. Quota: 50 units. Ungated. section_type is
        required by the API."""
        return _channel_section_update(clients.youtube_data(),
            section_id=section_id, section_type=section_type, title=title,
            playlist_ids=playlist_ids)

    @app.tool()
    @clients.http_safe
    def channel_section_delete(section_id: str, confirm: bool = False) -> dict:
        """Delete a channel section. Quota: 50 units. Gated: irreversible."""
        return _channel_section_delete(clients.youtube_data(), section_id, confirm)

    @app.tool()
    @clients.http_safe
    def channel_unset_watermark(channel_id: str, confirm: bool = False) -> dict:
        """Remove the channel branding watermark. Quota: 50 units. Gated."""
        return _channel_unset_watermark(clients.youtube_data(), channel_id, confirm)
