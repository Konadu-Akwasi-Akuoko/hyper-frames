"""Channel write tools — metadata edits and thumbnail upload.

Both wrap the ``force-ssl`` half of the Data API. Privacy transitions are
guarded: a private → public transition requires explicit ``confirm_publish=True``
so the model can never make a draft public on its own initiative.
"""

from __future__ import annotations

import struct
from pathlib import Path
from typing import Any

from googleapiclient.http import MediaFileUpload
from mcp.server.fastmcp import FastMCP

from .. import clients, gate, mutate, quota

MAX_THUMBNAIL_BYTES = 2 * 1024 * 1024  # YouTube hard cap
RECOMMENDED_THUMB_W = 1280
RECOMMENDED_THUMB_H = 720
ALLOWED_PRIVACY = {"private", "unlisted", "public"}


def _read_image_dimensions(path: Path) -> tuple[int, int] | None:
    """Return (width, height) for PNG or JPEG. None if unsupported/unparseable."""
    try:
        with path.open("rb") as f:
            head = f.read(24)
            if len(head) < 24:
                return None
            # PNG: 89 50 4E 47 0D 0A 1A 0A then IHDR with width/height at offset 16
            if head[:8] == b"\x89PNG\r\n\x1a\n":
                w, h = struct.unpack(">II", head[16:24])
                return int(w), int(h)
            # JPEG: scan SOF markers
            if head[:2] == b"\xff\xd8":
                f.seek(0)
                f.read(2)
                while True:
                    b = f.read(1)
                    while b and b != b"\xff":
                        b = f.read(1)
                    while b == b"\xff":
                        b = f.read(1)
                    if not b:
                        return None
                    marker = b[0]
                    if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                        f.read(3)
                        h_bytes = f.read(2)
                        w_bytes = f.read(2)
                        h = struct.unpack(">H", h_bytes)[0]
                        w = struct.unpack(">H", w_bytes)[0]
                        return int(w), int(h)
                    size = struct.unpack(">H", f.read(2))[0]
                    f.read(size - 2)
    except Exception:
        return None
    return None


ALLOWED_RATINGS = {"like", "dislike", "none"}


def _video_delete(svc: Any, video_id: str, confirm: bool) -> dict:
    """videos.delete — irreversible, gated.
    Source: https://developers.google.com/youtube/v3/docs/videos/delete"""
    refusal = gate.require(
        confirm, effect=f"This permanently deletes video {video_id}.",
        video_id=video_id)
    if refusal:
        return refusal
    clients.run(lambda y: y.videos().delete(id=video_id), svc)
    quota.record("videos.delete")
    return {"deleted": video_id, "quota_units_spent": 50}


def _video_rate(svc: Any, video_id: str, rating: str, confirm: bool) -> dict:
    """videos.rate — like/dislike/none as the channel; gated (social).
    Source: https://developers.google.com/youtube/v3/docs/videos/rate"""
    if rating not in ALLOWED_RATINGS:
        return {"error": f"rating must be one of {sorted(ALLOWED_RATINGS)}"}
    refusal = gate.require(
        confirm, effect=f"This sets your channel's rating on {video_id} to "
                        f"{rating!r}.", video_id=video_id, rating=rating)
    if refusal:
        return refusal
    clients.run(lambda y: y.videos().rate(id=video_id, rating=rating), svc)
    quota.record("videos.rate")
    return {"rated": video_id, "rating": rating, "quota_units_spent": 50}


def _video_schedule(svc: Any, video_id: str, publish_at: str,
                    confirm: bool) -> dict:
    """Arm a scheduled publish. Gated. Sets status.publishAt + forces
    privacyStatus=private (re-sent even if already private). Video must never
    have been published. Source: https://developers.google.com/youtube/v3/docs/videos"""
    refusal = gate.require(
        confirm, effect=(f"This schedules video {video_id} to go PUBLIC "
                         f"automatically at {publish_at}."),
        video_id=video_id, publish_at=publish_at)
    if refusal:
        return refusal
    try:
        resp = mutate.fetch_merge_update(
            svc, resource="videos", id=video_id, parts="status",
            patch={"status": {"privacyStatus": "private", "publishAt": publish_at}},
            record_list="videos.list", record_update="videos.update")
    except KeyError:
        return {"error": "video_not_found", "video_id": video_id}
    return {"scheduled": video_id, "publish_at": publish_at, "response": resp}


def _video_cancel_schedule(svc: Any, video_id: str) -> dict:
    """Cancel a pending schedule: keep private, clear publishAt. Ungated."""
    try:
        resp = mutate.fetch_merge_update(
            svc, resource="videos", id=video_id, parts="status",
            patch={"status": {"privacyStatus": "private", "publishAt": None}},
            record_list="videos.list", record_update="videos.update")
    except KeyError:
        return {"error": "video_not_found", "video_id": video_id}
    return {"schedule_cancelled": video_id, "response": resp}


def _video_update_metadata(svc: Any, video_id: str, title: str | None = None,
                           description: str | None = None,
                           tags: list[str] | None = None,
                           category_id: str | None = None,
                           default_language: str | None = None,
                           default_audio_language: str | None = None,
                           privacy_status: str | None = None,
                           confirm_publish: bool = False) -> dict:
    """Update one or more snippet/status fields on a video via the mutate helper."""
    if privacy_status and privacy_status not in ALLOWED_PRIVACY:
        return {"error": f"privacy_status must be one of {sorted(ALLOWED_PRIVACY)}"}
    current = clients.run(
        lambda y: y.videos().list(part="status", id=video_id), svc)
    quota.record("videos.list")
    items = current.get("items") or []
    if not items:
        return {"error": "video_not_found", "video_id": video_id}
    prev_privacy = (items[0].get("status") or {}).get("privacyStatus")
    if (privacy_status == "public" and prev_privacy != "public"
            and not confirm_publish):
        return {"error": "confirm_publish_required",
                "reason": (f"This would change privacyStatus from "
                           f"{prev_privacy!r} to 'public'. Re-call with "
                           "confirm_publish=True after user approval."),
                "current_privacy": prev_privacy}
    patch: dict[str, Any] = {}
    snippet_patch: dict[str, Any] = {}
    if title is not None:
        snippet_patch["title"] = title
    if description is not None:
        snippet_patch["description"] = description
    if tags is not None:
        snippet_patch["tags"] = tags
    if category_id is not None:
        snippet_patch["categoryId"] = category_id
    if default_language is not None:
        snippet_patch["defaultLanguage"] = default_language
    if default_audio_language is not None:
        snippet_patch["defaultAudioLanguage"] = default_audio_language
    if snippet_patch:
        patch["snippet"] = snippet_patch
    if privacy_status is not None:
        patch["status"] = {"privacyStatus": privacy_status}
    if not patch:
        return {"error": "no_changes_provided"}
    parts = ",".join(k for k in ("snippet", "status") if k in patch)
    try:
        resp = mutate.fetch_merge_update(
            svc, resource="videos", id=video_id, parts=parts, patch=patch,
            record_list="videos.list", record_update="videos.update")
    except KeyError:
        return {"error": "video_not_found", "video_id": video_id}
    return {"updated": video_id, "parts": parts, "response": resp,
            "previous_privacy": prev_privacy}


def _video_set_localizations(svc: Any, video_id: str, localizations: dict,
                             default_language: str | None) -> dict:
    """Set per-language localized title/description. Ungated. Requires
    snippet.defaultLanguage. Existing translations merged, not replaced.
    Source: https://developers.google.com/youtube/v3/docs/videos"""
    if not default_language:
        try:
            current = clients.run(
                lambda y: y.videos().list(part="snippet", id=video_id), svc)
            quota.record("videos.list")
            existing = (current.get("items") or [{}])[0]
            default_language = existing.get("snippet", {}).get("defaultLanguage")
        except Exception:
            default_language = None
        if not default_language:
            return {"error": "default_language_required",
                    "reason": ("Set default_language (the video's primary "
                               "language) — the API rejects localizations "
                               "without it.")}
    try:
        resp = mutate.fetch_merge_update(
            svc, resource="videos", id=video_id, parts="snippet,localizations",
            patch={"snippet": {"defaultLanguage": default_language},
                   "localizations": localizations},
            record_list="videos.list", record_update="videos.update")
    except KeyError:
        return {"error": "video_not_found", "video_id": video_id}
    return {"localized": video_id, "languages": sorted(localizations.keys()),
            "response": resp}


def register(app: FastMCP) -> None:
    @app.tool()
    @clients.http_safe
    def video_update_metadata(video_id: str,
                              title: str | None = None,
                              description: str | None = None,
                              tags: list[str] | None = None,
                              category_id: str | None = None,
                              default_language: str | None = None,
                              default_audio_language: str | None = None,
                              privacy_status: str | None = None,
                              confirm_publish: bool = False) -> dict:
        """Update one or more snippet/status fields on a video.

        Quota: 50 units. Required scope: ``youtube.force-ssl``.

        Snippet fields are patched together — only fields you pass are changed.
        ``category_id`` is required by the API whenever ``snippet`` is touched,
        so this tool fetches the existing ``categoryId`` and reuses it if you
        don't supply one.

        Privacy guard: ``private → public`` and ``unlisted → public``
        transitions require ``confirm_publish=True``.

        Args:
            video_id: 11-char video ID.
            title: New title (≤100 chars).
            description: New description (≤5000 chars).
            tags: Replacement tag list (entire list, not additive).
            category_id: New category (e.g. "22" for People & Blogs).
            default_language: ISO 639-1 code for the snippet language.
            default_audio_language: ISO 639-1 code for the audio language.
            privacy_status: ``private``, ``unlisted``, or ``public``.
            confirm_publish: Must be True if going to ``public``.
        """
        return _video_update_metadata(
            clients.youtube_data(), video_id=video_id, title=title,
            description=description, tags=tags, category_id=category_id,
            default_language=default_language,
            default_audio_language=default_audio_language,
            privacy_status=privacy_status, confirm_publish=confirm_publish)

    @app.tool()
    @clients.http_safe
    def video_set_thumbnail(video_id: str, path: str) -> dict:
        """Upload a custom thumbnail for a video.

        Quota: 50 units. Required scope: ``youtube.force-ssl``.

        Validates: file exists, ≤2 MB, content type is JPEG/PNG. Warns (but does
        not refuse) if dimensions aren't 1280×720 — YouTube re-encodes to that
        resolution server-side anyway.

        Args:
            video_id: 11-char video ID.
            path: Absolute or repo-relative path to the thumbnail file.
        """
        p = Path(path).expanduser().resolve()
        if not p.exists() or not p.is_file():
            return {"error": "file_not_found", "path": str(p)}
        size = p.stat().st_size
        if size > MAX_THUMBNAIL_BYTES:
            return {
                "error": "file_too_large",
                "path": str(p),
                "size_bytes": size,
                "max_bytes": MAX_THUMBNAIL_BYTES,
            }
        ext = p.suffix.lower()
        mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".png": "image/png"}.get(ext)
        if not mime:
            return {"error": "unsupported_format", "path": str(p),
                    "reason": "thumbnail must be JPEG or PNG"}

        warnings: list[str] = []
        dims = _read_image_dimensions(p)
        if dims and dims != (RECOMMENDED_THUMB_W, RECOMMENDED_THUMB_H):
            warnings.append(
                f"Thumbnail is {dims[0]}x{dims[1]}; YouTube recommends "
                f"{RECOMMENDED_THUMB_W}x{RECOMMENDED_THUMB_H}."
            )

        media = MediaFileUpload(str(p), mimetype=mime)
        resp = clients.run(
            lambda y: y.thumbnails().set(videoId=video_id, media_body=media),
            clients.youtube_data(),
        )
        quota.record("thumbnails.set")
        out: dict[str, Any] = {"updated": video_id, "path": str(p),
                               "size_bytes": size, "mime": mime,
                               "response": resp}
        if warnings:
            out["warnings"] = warnings
        return out

    @app.tool()
    @clients.http_safe
    def video_delete(video_id: str, confirm: bool = False) -> dict:
        """Permanently delete a video. Quota: 50 units. Gated: irreversible."""
        return _video_delete(clients.youtube_data(), video_id, confirm)

    @app.tool()
    @clients.http_safe
    def video_rate(video_id: str, rating: str, confirm: bool = False) -> dict:
        """Set your channel's like/dislike on a video. Quota: 50 units. Gated
        (social). rating is like, dislike, or none."""
        return _video_rate(clients.youtube_data(), video_id, rating, confirm)

    @app.tool()
    @clients.http_safe
    def video_schedule(video_id: str, publish_at: str,
                       confirm: bool = False) -> dict:
        """Schedule a private video to auto-publish at publish_at (ISO-8601, e.g.
        2026-07-01T12:00:00Z). Quota ~51 units. Gated: arms a future PUBLIC
        release. Video must be private and never previously published. To
        reschedule, call again with a new publish_at."""
        return _video_schedule(clients.youtube_data(), video_id, publish_at, confirm)

    @app.tool()
    @clients.http_safe
    def video_cancel_schedule(video_id: str) -> dict:
        """Cancel a pending scheduled publish (keeps it private, clears
        publishAt). Quota ~51 units. Ungated."""
        return _video_cancel_schedule(clients.youtube_data(), video_id)

    @app.tool()
    @clients.http_safe
    def video_set_localizations(video_id: str, localizations: dict,
                                default_language: str | None = None) -> dict:
        """Set localized title/description per language. Quota ~51 units. Ungated.
        localizations = {lang: {"title": ..., "description": ...}}.
        default_language is the video's primary language (e.g. "en"); required by
        the API; read from the video if omitted. Existing translations merged."""
        return _video_set_localizations(
            clients.youtube_data(), video_id, localizations, default_language)
