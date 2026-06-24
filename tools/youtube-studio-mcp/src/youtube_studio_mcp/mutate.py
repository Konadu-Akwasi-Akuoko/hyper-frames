"""Read-modify-write helper for YouTube Data API PUT updates.

`update` is a full replace within each requested `part`: any property you omit
that currently has a value is DELETED. So every partial edit must fetch, overlay
only changed keys, and PUT the merged body back.
Source: https://developers.google.com/youtube/v3/docs/videos/update
"""

from __future__ import annotations

import copy
from typing import Any

from . import clients, quota


def deep_merge(base: dict, patch: dict) -> dict:
    """`patch` overlaid on `base`; recurse into nested dicts, replace lists/scalars."""
    out = copy.deepcopy(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def fetch_merge_update(svc: Any, *, resource: str, id: str, parts: str,
                       patch: dict, record_list: str, record_update: str) -> dict:
    """Fetch `id`, deep-merge `patch`, PUT the merged body. Raises KeyError if
    the resource id is not found."""
    current = clients.run(
        lambda y: getattr(y, resource)().list(part=parts, id=id), svc)
    quota.record(record_list)
    items = current.get("items") or []
    if not items:
        raise KeyError("resource_not_found")
    existing = items[0]
    body: dict[str, Any] = {"id": id}
    for part in (p.strip() for p in parts.split(",")):
        existing_part = existing.get(part, {})
        patch_part = patch.get(part, {})
        if existing_part or patch_part:
            body[part] = deep_merge(existing_part, patch_part)
    resp = clients.run(
        lambda y: getattr(y, resource)().update(part=parts, body=body), svc)
    quota.record(record_update)
    return resp
