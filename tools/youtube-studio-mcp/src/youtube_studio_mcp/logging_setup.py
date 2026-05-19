"""Stderr-only logging with credential redaction.

MCP stdio servers must not write to stdout (it would corrupt the JSON-RPC
stream). This module installs a stderr handler and a filter that scrubs
``Authorization``, ``access_token``, ``refresh_token``, ``client_secret``,
and Bearer tokens from log records before they're emitted.
"""

from __future__ import annotations

import logging
import re
import sys

_REDACT_PATTERNS = [
    re.compile(r'("(?:access_token|refresh_token|client_secret|client_id|id_token)"\s*:\s*)"[^"]*"'),
    re.compile(r"(Authorization:\s*Bearer\s+)\S+", re.IGNORECASE),
    re.compile(r"(Bearer\s+)[A-Za-z0-9._\-]+"),
    re.compile(r"(ya29\.[A-Za-z0-9_\-]+)"),
]


def _redact(text: str) -> str:
    for pat in _REDACT_PATTERNS:
        text = pat.sub(lambda m: m.group(1) + "[REDACTED]" if m.lastindex else "[REDACTED]", text)
    return text


class RedactionFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        try:
            record.msg = _redact(str(record.msg))
            if record.args:
                record.args = tuple(_redact(str(a)) for a in record.args)
        except Exception:
            pass
        return True


def configure(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    if getattr(root, "_yt_mcp_configured", False):
        return
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    handler.addFilter(RedactionFilter())
    root.handlers = [handler]
    root.setLevel(level)
    root._yt_mcp_configured = True  # type: ignore[attr-defined]
