"""Resumable media-upload helper shared by video / banner / watermark / caption
/ playlist-image upload tools.
Source: https://developers.google.com/youtube/v3/guides/using_resumable_upload_protocol
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

MIME_BY_EXT: dict[str, str] = {
    ".mp4": "video/*", ".mov": "video/*", ".m4v": "video/*", ".webm": "video/*",
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
    ".srt": "application/octet-stream", ".sbv": "application/octet-stream",
    ".vtt": "text/vtt", ".xml": "text/xml",
}


def validate(path: Any, *, max_bytes: int, allowed_mimes: set[str]) -> dict:
    """Pre-flight a file for upload. Returns {"ok": bool, ...}."""
    p = Path(path).expanduser().resolve()
    if not p.exists() or not p.is_file():
        return {"ok": False, "error": "file_not_found", "path": str(p)}
    size = p.stat().st_size
    if size > max_bytes:
        return {"ok": False, "error": "file_too_large", "path": str(p),
                "size_bytes": size, "max_bytes": max_bytes}
    mime = MIME_BY_EXT.get(p.suffix.lower())
    if mime is None or mime not in allowed_mimes:
        return {"ok": False, "error": "unsupported_format", "path": str(p),
                "suffix": p.suffix, "allowed_mimes": sorted(allowed_mimes)}
    return {"ok": True, "path": str(p), "size_bytes": size, "mime": mime}


def execute_resumable(request: Any) -> dict:
    """Drive a resumable upload request to completion; return the final body."""
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status is not None:
            logger.info("upload progress: %d%%", int(status.progress() * 100))
    return response
