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
        if privacy_status and privacy_status not in ALLOWED_PRIVACY:
            return {"error": f"privacy_status must be one of {sorted(ALLOWED_PRIVACY)}"}

        current = clients.run(
            lambda y: y.videos().list(part="snippet,status", id=video_id),
            clients.youtube_data(),
        )
        quota.record("videos.list")
        items = current.get("items") or []
        if not items:
            return {"error": "video_not_found", "video_id": video_id}
        existing = items[0]
        existing_snippet = existing.get("snippet") or {}
        existing_status = existing.get("status") or {}
        prev_privacy = existing_status.get("privacyStatus")

        if privacy_status == "public" and prev_privacy != "public" and not confirm_publish:
            return {
                "error": "confirm_publish_required",
                "reason": (f"This would change privacyStatus from "
                           f"{prev_privacy!r} to 'public'. Re-call with "
                           "confirm_publish=True after user approval."),
                "current_privacy": prev_privacy,
            }

        body: dict[str, Any] = {"id": video_id}
        snippet_changed = any(v is not None for v in (
            title, description, tags, category_id, default_language, default_audio_language))
        if snippet_changed:
            snippet: dict[str, Any] = {
                "categoryId": category_id or existing_snippet.get("categoryId") or "22",
            }
            snippet["title"] = title if title is not None else existing_snippet.get("title", "")
            if description is not None:
                snippet["description"] = description
            elif "description" in existing_snippet:
                snippet["description"] = existing_snippet["description"]
            if tags is not None:
                snippet["tags"] = tags
            elif "tags" in existing_snippet:
                snippet["tags"] = existing_snippet["tags"]
            if default_language is not None:
                snippet["defaultLanguage"] = default_language
            elif "defaultLanguage" in existing_snippet:
                snippet["defaultLanguage"] = existing_snippet["defaultLanguage"]
            if default_audio_language is not None:
                snippet["defaultAudioLanguage"] = default_audio_language
            elif "defaultAudioLanguage" in existing_snippet:
                snippet["defaultAudioLanguage"] = existing_snippet["defaultAudioLanguage"]
            body["snippet"] = snippet
        if privacy_status is not None:
            body["status"] = {"privacyStatus": privacy_status}

        if "snippet" not in body and "status" not in body:
            return {"error": "no_changes_provided"}

        parts = ",".join(k for k in ("snippet", "status") if k in body)
        resp = clients.run(
            lambda y: y.videos().update(part=parts, body=body),
            clients.youtube_data(),
        )
        quota.record("videos.update")
        return {"updated": video_id, "parts": parts, "response": resp,
                "previous_privacy": prev_privacy}

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
