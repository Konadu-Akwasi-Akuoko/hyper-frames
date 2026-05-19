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
