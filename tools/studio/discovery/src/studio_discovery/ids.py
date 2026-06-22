"""Stable raw_signal ids — MUST match server/lib/ids.ts byte-for-byte."""

from __future__ import annotations

import hashlib

# unit separator (0x1f) — keeps source/external_id boundaries unambiguous
_US = "\x1f"


def raw_signal_id(source: str, external_id: str) -> str:
    """sha1(source + 0x1f + external_id), first 16 hex chars."""
    return hashlib.sha1(f"{source}{_US}{external_id}".encode()).hexdigest()[:16]
