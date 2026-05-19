"""Lazy-built Google API clients with shared retry behaviour.

Three services are exposed:

- ``youtube_data()``      → YouTube Data API v3
- ``youtube_analytics()`` → YouTube Analytics API v2
- ``youtube_reporting()`` → YouTube Reporting API v1

Each call to a service builder returns a cached client bound to the current
on-disk credentials. ``invalidate()`` drops the cache so a token refresh or
re-auth is picked up on the next call.
"""

from __future__ import annotations

import functools
import json
import logging
import random
import time
from typing import Any, Callable, TypeVar

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from . import auth

logger = logging.getLogger(__name__)

_services: dict[str, Any] = {}

T = TypeVar("T")


def _build(api_name: str, version: str) -> Any:
    key = f"{api_name}:{version}"
    cached = _services.get(key)
    if cached is not None:
        return cached
    creds = auth.load_credentials()
    svc = build(api_name, version, credentials=creds, cache_discovery=False)
    _services[key] = svc
    return svc


def invalidate() -> None:
    _services.clear()


def youtube_data() -> Any:
    return _build("youtube", "v3")


def youtube_analytics() -> Any:
    return _build("youtubeAnalytics", "v2")


def youtube_reporting() -> Any:
    return _build("youtubereporting", "v1")


_RETRYABLE = {429, 500, 502, 503, 504}


def execute_with_retry(request: Any, *, max_attempts: int = 5,
                       base_delay: float = 1.0) -> Any:
    """Call ``request.execute()`` with capped exponential backoff + jitter.

    Retries on HTTP 429 (rate-limit / quotaExceeded for a short-burst quota) and
    5xx server errors. Daily-quota exceeded (``quotaExceeded`` on 403) is not
    retryable — propagated immediately.
    """
    attempt = 0
    while True:
        try:
            return request.execute()
        except HttpError as e:
            status = getattr(e.resp, "status", 0) or 0
            if status not in _RETRYABLE or attempt >= max_attempts - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 0.5)
            logger.warning("HTTP %s on attempt %d; retrying in %.2fs", status, attempt + 1, delay)
            time.sleep(delay)
            attempt += 1


def run(builder: Callable[[Any], Any], svc: Any) -> Any:
    """Convenience: ``run(lambda y: y.channels().list(...), youtube_data())``."""
    return execute_with_retry(builder(svc))


def http_error_payload(e: HttpError) -> dict:
    """Convert a googleapiclient HttpError into a structured MCP-friendly dict.

    Shape matches the existing structured errors used by the warehouse and
    bulk-comment tools — `{error, http_status, reason, details?}`.
    """
    status = getattr(e.resp, "status", 0) or 0
    reason = ""
    details: Any = None
    raw = getattr(e, "content", None)
    if raw:
        try:
            text = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else str(raw)
            parsed = json.loads(text)
            err = (parsed.get("error") or {}) if isinstance(parsed, dict) else {}
            reason = err.get("message") or ""
            details = err.get("errors") or err
        except Exception:
            reason = (raw.decode("utf-8", errors="replace")
                      if isinstance(raw, (bytes, bytearray)) else str(raw))
    if not reason:
        reason = str(e)
    out: dict[str, Any] = {
        "error": "http_error",
        "http_status": int(status),
        "reason": reason,
    }
    if details is not None:
        out["details"] = details
    return out


def http_safe(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator: convert HttpError raised inside an MCP tool into a structured dict.

    Apply *below* `@app.tool()` so FastMCP sees a function that already
    catches the upstream Google API error and returns a JSON-friendly
    payload instead of raising. Idempotent on happy paths — only the
    exception branch changes behaviour.
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except HttpError as e:
            return http_error_payload(e)
    return wrapper
