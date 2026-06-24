# YouTube MCP Write Surface — Plan 1: Foundation + Videos

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lift the `youtube-studio-mcp` v1 scope cap by building the shared write infrastructure (test harness, quota costs, confirm-gate, read-modify-write merge, resumable upload) and the full **videos/Shorts** write surface on top of it (upload, delete, rate, schedule, localizations).

**Architecture:** New tools follow a **dependency-injection core + thin tool wrapper** pattern: each tool's logic lives in a module-level function that takes the googleapiclient service as its first argument (unit-testable with a `MagicMock` service), and the `@app.tool()`-decorated wrapper just calls it with `clients.youtube_data()`. Three shared helpers — `gate.py` (confirm interlock), `mutate.py` (fetch-merge-update so PUT never wipes omitted fields), `uploadmedia.py` (resumable upload loop) — are reused by every later plan (captions, playlists, channel-level).

**Tech Stack:** Python 3.12, `google-api-python-client`, FastMCP (`mcp[cli]`), `pytest` (added here), SQLite quota ledger.

## Global Constraints

- Working dir for all commands: `tools/youtube-studio-mcp/`. Run Python via `uv run`.
- Required Python: `>=3.12` (per `pyproject.toml`).
- Every API call records its cost via `quota.record("<endpoint>")` using a key present in `quota.COSTS`.
- Every tool is decorated `@app.tool()` then `@clients.http_safe` (in that order), and uses `clients.run(lambda y: ..., svc)` so retry/backoff applies.
- **Gate convention:** gated tools take `confirm: bool = False`; when `False` they return `{"error": "confirm_required", "reason": "...", ...}` and make **no** API call.
- **PUT is destructive:** every `*.update` re-sends existing field values via the `mutate.py` merge helper; never send a sparse update body. Source: https://developers.google.com/youtube/v3/docs/videos/update
- OAuth: `youtube.force-ssl` (already granted) authorizes everything; we additively request `youtube.upload`. No token invalidation.
- Field limits (videos): `title` ≤100 chars; `description` ≤5000 **bytes**; `tags` ≤500 chars total. `videos.update` of `snippet` must re-send `id`, `snippet.title`, `snippet.categoryId`. Source: https://developers.google.com/youtube/v3/docs/videos
- Scheduling: `status.publishAt` (ISO-8601) requires `status.privacyStatus=private`, re-sent even if already private; video must never have been published. Source: https://developers.google.com/youtube/v3/docs/videos
- `videos.insert` quota = 1 unit in a separate 100/day Uploads bucket (NOT the 10k pool). Source: https://developers.google.com/youtube/v3/determine_quota_cost

---

## File Structure

- Create: `tools/youtube-studio-mcp/src/youtube_studio_mcp/gate.py` — confirm-gate refusal builder.
- Create: `tools/youtube-studio-mcp/src/youtube_studio_mcp/mutate.py` — fetch-merge-update helper.
- Create: `tools/youtube-studio-mcp/src/youtube_studio_mcp/uploadmedia.py` — resumable upload helper.
- Create: `tools/youtube-studio-mcp/src/youtube_studio_mcp/tools/uploads.py` — `video_upload` (+ later: banner/watermark).
- Modify: `tools/youtube-studio-mcp/src/youtube_studio_mcp/tools/edits.py` — add `video_delete`, `video_rate`, `video_schedule`, `video_set_localizations`; refactor `video_update_metadata` onto `mutate.py`.
- Modify: `tools/youtube-studio-mcp/src/youtube_studio_mcp/quota.py` — add `videos.insert`, channel/playlistImages/watermarks costs; mark upload bucket.
- Modify: `tools/youtube-studio-mcp/src/youtube_studio_mcp/auth.py` — add `youtube.upload` scope.
- Modify: `tools/youtube-studio-mcp/src/youtube_studio_mcp/server.py` — register `uploads`.
- Modify: `tools/youtube-studio-mcp/CLAUDE.md` — rewrite scope cap v1→v2.
- Modify: `tools/youtube-studio-mcp/pyproject.toml` — add pytest dev group + config.
- Create: `tools/youtube-studio-mcp/tests/conftest.py` — config-dir isolation + `svc` MagicMock fixture.
- Create: `tools/youtube-studio-mcp/tests/test_gate.py`, `test_mutate.py`, `test_uploadmedia.py`, `test_edits_videos.py`, `test_uploads.py`.

---

## Task 1: Test harness (pytest + isolated conftest)

**Files:**
- Modify: `pyproject.toml`
- Create: `tests/conftest.py`
- Create: `tests/test_smoke.py`

**Interfaces:**
- Produces: pytest dev dependency; fixtures `isolated_config` (autouse, points `YOUTUBE_STUDIO_MCP_CONFIG_DIR` at a tmp dir so `quota.db` is isolated) and `svc` (a `MagicMock` standing in for a googleapiclient service).

- [ ] **Step 1: Add the pytest dev group + config to `pyproject.toml`**

Append after the `[tool.pyright]` block:

```toml
[dependency-groups]
dev = [
    "pytest>=8.3.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
```

- [ ] **Step 2: Sync the dev group**

Run: `uv sync --group dev`
Expected: resolves and installs `pytest`.

- [ ] **Step 3: Write `tests/conftest.py`**

```python
"""Shared test fixtures.

`isolated_config` redirects the MCP config dir (quota.db etc.) to a tmp path so
tests never touch the real ledger or token. `svc` is a MagicMock that stands in
for a googleapiclient YouTube Data service; configure return values per test:

    svc.videos.return_value.list.return_value.execute.return_value = {...}
"""

from __future__ import annotations

import importlib
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    monkeypatch.setenv("YOUTUBE_STUDIO_MCP_CONFIG_DIR", str(tmp_path))
    # Reload paths so it re-reads the env var for this test.
    from youtube_studio_mcp import paths
    importlib.reload(paths)
    yield tmp_path


@pytest.fixture
def svc():
    return MagicMock(name="youtube_data_service")
```

- [ ] **Step 4: Write `tests/test_smoke.py`**

```python
def test_quota_module_imports_and_records(isolated_config):
    from youtube_studio_mcp import quota
    units = quota.record("videos.update")
    assert units == 50
    assert quota.spent_today() == 50
```

- [ ] **Step 5: Run the smoke test**

Run: `uv run pytest tests/test_smoke.py -v`
Expected: PASS (1 passed).

- [ ] **Step 6: Commit**

```bash
git add tools/youtube-studio-mcp/pyproject.toml tools/youtube-studio-mcp/uv.lock tools/youtube-studio-mcp/tests/conftest.py tools/youtube-studio-mcp/tests/test_smoke.py
git commit -m "test(youtube-mcp): add pytest harness with isolated config + svc fixtures"
```

---

## Task 2: Quota cost additions

**Files:**
- Modify: `src/youtube_studio_mcp/quota.py:29-72` (the `COSTS` dict)
- Test: `tests/test_quota_costs.py`

**Interfaces:**
- Produces: `quota.COSTS` keys for `videos.insert`, `videos.delete`, `playlists.*`, `playlistItems.*`, `playlistImages.*`, `channels.update`, `channelSections.*`, `channelBanners.insert`, `watermarks.set`, `watermarks.unset`. (Several already exist — only add missing keys.)

- [ ] **Step 1: Write the failing test `tests/test_quota_costs.py`**

```python
import pytest

from youtube_studio_mcp import quota

EXPECTED = {
    "videos.insert": 1,        # separate 100/day Uploads bucket, 1 unit/call
    "videos.delete": 50,
    "playlists.insert": 50,
    "playlists.update": 50,
    "playlists.delete": 50,
    "playlistItems.insert": 50,
    "playlistItems.update": 50,
    "playlistItems.delete": 50,
    "playlistImages.insert": 50,
    "playlistImages.update": 50,
    "playlistImages.delete": 50,
    "channels.update": 50,
    "channelSections.insert": 50,
    "channelSections.update": 50,
    "channelSections.delete": 50,
    "channelBanners.insert": 50,
    "watermarks.set": 50,
    "watermarks.unset": 50,
}


@pytest.mark.parametrize("endpoint,units", EXPECTED.items())
def test_cost_known(endpoint, units):
    assert quota.cost_of(endpoint) == units
    # cost_of of a known endpoint must not be flagged unknown
    from youtube_studio_mcp.quota import _cost_of
    assert _cost_of(endpoint)[1] is False
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_quota_costs.py -v`
Expected: FAIL — several endpoints default to 1 unit and are flagged unknown.

- [ ] **Step 3: Add the missing keys to `COSTS`**

In `quota.py`, inside the `COSTS` dict, under the `# writes` comment add:

```python
    "videos.insert": 1,  # 100/day Uploads bucket; 1 unit/call (NOT the 10k pool)
    "videos.delete": 50,
```

And append a new block before the closing brace:

```python
    # playlists / playlist items / playlist images
    "playlists.insert": 50,
    "playlists.update": 50,
    "playlists.delete": 50,
    "playlistItems.insert": 50,
    "playlistItems.update": 50,
    "playlistItems.delete": 50,
    "playlistImages.list": 1,
    "playlistImages.insert": 50,
    "playlistImages.update": 50,
    "playlistImages.delete": 50,

    # channel-level
    "channels.update": 50,
    "channelSections.list": 1,
    "channelSections.insert": 50,
    "channelSections.update": 50,
    "channelSections.delete": 50,
    "channelBanners.insert": 50,
    "watermarks.set": 50,
    "watermarks.unset": 50,
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest tests/test_quota_costs.py -v`
Expected: PASS (all parametrized cases).

- [ ] **Step 5: Commit**

```bash
git add tools/youtube-studio-mcp/src/youtube_studio_mcp/quota.py tools/youtube-studio-mcp/tests/test_quota_costs.py
git commit -m "feat(youtube-mcp): add quota costs for full write surface"
```

---

## Task 3: Confirm-gate helper (`gate.py`)

**Files:**
- Create: `src/youtube_studio_mcp/gate.py`
- Test: `tests/test_gate.py`

**Interfaces:**
- Produces:
  - `gate.require(confirm: bool, *, effect: str, **extra) -> dict | None` — returns a refusal dict `{"error": "confirm_required", "reason": effect + " Re-call with confirm=True after user approval.", **extra}` when `confirm` is False, else `None`.
  - `gate.quota_guard(endpoint: str, multiplier: int, confirm: bool, *, fraction_limit: float = 0.25) -> dict | None` — for expensive writes: returns `confirm_required` when `confirm` is False, else `quota_safety_refused` if the cost exceeds `fraction_limit` of remaining quota, else `None`.

- [ ] **Step 1: Write the failing test `tests/test_gate.py`**

```python
from youtube_studio_mcp import gate, quota


def test_require_blocks_without_confirm():
    r = gate.require(False, effect="This deletes video abc.", video_id="abc")
    assert r is not None
    assert r["error"] == "confirm_required"
    assert "deletes video abc" in r["reason"]
    assert r["video_id"] == "abc"


def test_require_passes_with_confirm():
    assert gate.require(True, effect="This deletes video abc.") is None


def test_quota_guard_blocks_without_confirm():
    r = gate.quota_guard("captions.insert", 1, confirm=False)
    assert r["error"] == "confirm_required"
    assert r["estimated_cost_units"] == 400


def test_quota_guard_refuses_when_over_fraction(isolated_config):
    # Burn quota so only 100 units remain; a 400-unit write exceeds 25% of 100.
    quota.record("search.list", multiplier=99)  # 99 * 100 = 9900 spent
    r = gate.quota_guard("captions.insert", 1, confirm=True)
    assert r["error"] == "quota_safety_refused"
    assert r["estimated_cost_units"] == 400


def test_quota_guard_allows_when_affordable(isolated_config):
    assert gate.quota_guard("videos.update", 1, confirm=True) is None
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_gate.py -v`
Expected: FAIL with "No module named 'youtube_studio_mcp.gate'".

- [ ] **Step 3: Write `src/youtube_studio_mcp/gate.py`**

```python
"""Confirmation interlocks for irreversible / public-facing / social writes.

A gated tool calls `gate.require(...)` (or `gate.quota_guard(...)`) first; if it
returns a dict, the tool returns that dict unchanged and performs no API call.
This mirrors the existing `confirm_publish` pattern and the bulk-comment guard.
"""

from __future__ import annotations

from typing import Any

from . import quota

DEFAULT_FRACTION_LIMIT = 0.25


def require(confirm: bool, *, effect: str, **extra: Any) -> dict | None:
    """Return a refusal dict when `confirm` is False, else None.

    Args:
        confirm: caller's confirm flag.
        effect: one sentence describing what the action will do, e.g.
            "This permanently deletes video abc123."
        extra: extra keys folded into the refusal payload (ids, costs).
    """
    if confirm:
        return None
    out: dict[str, Any] = {
        "error": "confirm_required",
        "reason": f"{effect} Re-call with confirm=True after user approval.",
    }
    out.update(extra)
    return out


def quota_guard(endpoint: str, multiplier: int, confirm: bool, *,
                fraction_limit: float = DEFAULT_FRACTION_LIMIT) -> dict | None:
    """Gate an expensive write on both confirmation and remaining quota.

    Returns confirm_required when not confirmed, quota_safety_refused when the
    cost would exceed `fraction_limit` of remaining daily quota, else None.
    """
    cost = quota.cost_of(endpoint) * multiplier
    if not confirm:
        return {
            "error": "confirm_required",
            "reason": (f"This costs {cost} quota units. Re-call with "
                       "confirm=True after user approval."),
            "estimated_cost_units": cost,
        }
    rem = quota.remaining()
    if rem > 0 and cost > rem * fraction_limit:
        return {
            "error": "quota_safety_refused",
            "reason": (f"This would cost {cost} units, more than "
                       f"{int(fraction_limit * 100)}% of the {rem} units "
                       "remaining today. Wait for quota reset or split the work."),
            "estimated_cost_units": cost,
            "remaining_quota_units": rem,
        }
    return None
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest tests/test_gate.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add tools/youtube-studio-mcp/src/youtube_studio_mcp/gate.py tools/youtube-studio-mcp/tests/test_gate.py
git commit -m "feat(youtube-mcp): shared confirm-gate + quota guard helper"
```

---

## Task 4: Read-modify-write helper (`mutate.py`)

**Files:**
- Create: `src/youtube_studio_mcp/mutate.py`
- Test: `tests/test_mutate.py`

**Interfaces:**
- Consumes: `clients.run`, `quota.record`.
- Produces: `mutate.fetch_merge_update(svc, *, resource, id, parts, patch, list_part=None, record_list, record_update) -> dict`. Fetches the current resource (`svc.<resource>().list(part=..., id=...)`), deep-merges `patch` over the existing parts, re-includes `id`, and PUTs (`svc.<resource>().update(part=..., body=...)`). `patch` is a nested dict like `{"snippet": {"title": "x"}}`. Returns the API response. Raises `KeyError("resource_not_found")` if the list returns no items.
- Produces: `mutate.deep_merge(base: dict, patch: dict) -> dict` (pure).

- [ ] **Step 1: Write the failing test `tests/test_mutate.py`**

```python
from unittest.mock import MagicMock

import pytest

from youtube_studio_mcp import mutate


def test_deep_merge_overlays_nested():
    base = {"snippet": {"title": "old", "categoryId": "22", "tags": ["a"]}}
    patch = {"snippet": {"title": "new"}}
    out = mutate.deep_merge(base, patch)
    assert out["snippet"]["title"] == "new"
    assert out["snippet"]["categoryId"] == "22"   # preserved
    assert out["snippet"]["tags"] == ["a"]         # preserved


def test_fetch_merge_update_preserves_unsent_fields(isolated_config):
    svc = MagicMock()
    svc.videos.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "vid1",
                   "snippet": {"title": "Old", "categoryId": "28",
                               "description": "keep me", "tags": ["x", "y"]}}]
    }
    svc.videos.return_value.update.return_value.execute.return_value = {"id": "vid1"}

    resp = mutate.fetch_merge_update(
        svc, resource="videos", id="vid1", parts="snippet",
        patch={"snippet": {"title": "New Title"}},
        record_list="videos.list", record_update="videos.update",
    )

    assert resp == {"id": "vid1"}
    body = svc.videos.return_value.update.call_args.kwargs["body"]
    assert body["id"] == "vid1"
    assert body["snippet"]["title"] == "New Title"
    assert body["snippet"]["categoryId"] == "28"        # required field preserved
    assert body["snippet"]["description"] == "keep me"  # unsent field preserved
    assert body["snippet"]["tags"] == ["x", "y"]


def test_fetch_merge_update_raises_when_missing(isolated_config):
    svc = MagicMock()
    svc.videos.return_value.list.return_value.execute.return_value = {"items": []}
    with pytest.raises(KeyError):
        mutate.fetch_merge_update(
            svc, resource="videos", id="nope", parts="snippet",
            patch={"snippet": {"title": "x"}},
            record_list="videos.list", record_update="videos.update",
        )
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_mutate.py -v`
Expected: FAIL with "No module named 'youtube_studio_mcp.mutate'".

- [ ] **Step 3: Write `src/youtube_studio_mcp/mutate.py`**

```python
"""Read-modify-write helper for YouTube Data API PUT updates.

The Data API treats `update` as a full replace within each requested `part`:
any property you omit that currently has a value is DELETED. So every partial
edit must fetch the current resource, overlay only the changed keys, and PUT the
merged body back. This helper centralizes that fetch-merge-PUT cycle.

Source: https://developers.google.com/youtube/v3/docs/videos/update
"""

from __future__ import annotations

import copy
from typing import Any

from . import clients, quota


def deep_merge(base: dict, patch: dict) -> dict:
    """Return a new dict: `patch` overlaid on `base`, recursing into nested dicts.

    Lists and scalars in `patch` replace those in `base` wholesale (intentional —
    a tag-list edit is a full replacement). Only dict values merge recursively.
    """
    out = copy.deepcopy(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def fetch_merge_update(svc: Any, *, resource: str, id: str, parts: str,
                       patch: dict, record_list: str, record_update: str) -> dict:
    """Fetch `id`, deep-merge `patch`, and PUT the merged body back.

    Args:
        svc: googleapiclient YouTube Data service.
        resource: resource collection name, e.g. "videos", "playlists".
        id: resource id to update.
        parts: comma-separated parts to fetch and update, e.g. "snippet,status".
        patch: nested dict of changes, e.g. {"snippet": {"title": "x"}}.
        record_list / record_update: quota endpoint keys to record.

    Raises:
        KeyError: if the resource id is not found.
    """
    collection = getattr(svc, resource)
    current = clients.run(lambda y: getattr(y, resource)().list(part=parts, id=id), svc)
    quota.record(record_list)
    items = current.get("items") or []
    if not items:
        raise KeyError("resource_not_found")
    existing = items[0]

    body: dict[str, Any] = {"id": id}
    for part in parts.split(","):
        part = part.strip()
        existing_part = existing.get(part, {})
        patch_part = patch.get(part, {})
        if existing_part or patch_part:
            body[part] = deep_merge(existing_part, patch_part)

    resp = clients.run(
        lambda y: getattr(y, resource)().update(part=parts, body=body), svc)
    quota.record(record_update)
    return resp
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest tests/test_mutate.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add tools/youtube-studio-mcp/src/youtube_studio_mcp/mutate.py tools/youtube-studio-mcp/tests/test_mutate.py
git commit -m "feat(youtube-mcp): fetch-merge-update helper for non-destructive PUT"
```

---

## Task 5: Resumable upload helper (`uploadmedia.py`)

**Files:**
- Create: `src/youtube_studio_mcp/uploadmedia.py`
- Test: `tests/test_uploadmedia.py`

**Interfaces:**
- Produces:
  - `uploadmedia.validate(path, *, max_bytes, allowed_mimes) -> dict` — returns `{"ok": True, "path": str, "size_bytes": int, "mime": str}` or `{"ok": False, "error": ..., ...}`. Pure file-stat + extension→mime check.
  - `uploadmedia.MIME_BY_EXT` — mapping `{".mp4": "video/*", ".jpg": "image/jpeg", ".png": "image/png", ".srt": "application/octet-stream", ".vtt": "text/vtt", ".xml": "text/xml"}`.
  - `uploadmedia.execute_resumable(request) -> dict` — drives `request.next_chunk()` until done, returns the final response body.

- [ ] **Step 1: Write the failing test `tests/test_uploadmedia.py`**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp import uploadmedia


def test_validate_ok(tmp_path):
    f = tmp_path / "clip.mp4"
    f.write_bytes(b"\x00" * 10)
    r = uploadmedia.validate(f, max_bytes=1_000, allowed_mimes={"video/*"})
    assert r["ok"] is True
    assert r["mime"] == "video/*"
    assert r["size_bytes"] == 10


def test_validate_missing_file(tmp_path):
    r = uploadmedia.validate(tmp_path / "nope.mp4", max_bytes=1_000,
                             allowed_mimes={"video/*"})
    assert r["ok"] is False
    assert r["error"] == "file_not_found"


def test_validate_too_large(tmp_path):
    f = tmp_path / "big.mp4"
    f.write_bytes(b"\x00" * 100)
    r = uploadmedia.validate(f, max_bytes=10, allowed_mimes={"video/*"})
    assert r["ok"] is False
    assert r["error"] == "file_too_large"


def test_validate_unsupported_ext(tmp_path):
    f = tmp_path / "doc.txt"
    f.write_bytes(b"x")
    r = uploadmedia.validate(f, max_bytes=1_000, allowed_mimes={"video/*"})
    assert r["ok"] is False
    assert r["error"] == "unsupported_format"


def test_execute_resumable_loops_until_done():
    request = MagicMock()
    request.next_chunk.side_effect = [
        (MagicMock(progress=lambda: 0.5), None),
        (None, {"id": "vid123"}),
    ]
    resp = uploadmedia.execute_resumable(request)
    assert resp == {"id": "vid123"}
    assert request.next_chunk.call_count == 2
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_uploadmedia.py -v`
Expected: FAIL with "No module named 'youtube_studio_mcp.uploadmedia'".

- [ ] **Step 3: Write `src/youtube_studio_mcp/uploadmedia.py`**

```python
"""Resumable media-upload helper shared by video / banner / watermark / caption
/ playlist-image upload tools.

`validate` does the pre-flight file checks; `execute_resumable` drives the
googleapiclient `next_chunk()` loop so an interrupted upload resumes (the client
library handles the 308 protocol internally).

Source: https://developers.google.com/youtube/v3/guides/using_resumable_upload_protocol
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

MIME_BY_EXT: dict[str, str] = {
    ".mp4": "video/*",
    ".mov": "video/*",
    ".m4v": "video/*",
    ".webm": "video/*",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".srt": "application/octet-stream",
    ".sbv": "application/octet-stream",
    ".vtt": "text/vtt",
    ".xml": "text/xml",
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest tests/test_uploadmedia.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add tools/youtube-studio-mcp/src/youtube_studio_mcp/uploadmedia.py tools/youtube-studio-mcp/tests/test_uploadmedia.py
git commit -m "feat(youtube-mcp): resumable upload + file-validate helper"
```

---

## Task 6: `video_delete` and `video_rate` (edits.py)

**Files:**
- Modify: `src/youtube_studio_mcp/tools/edits.py`
- Test: `tests/test_edits_videos.py`

**Interfaces:**
- Consumes: `gate.require`, `clients.run`, `quota.record`.
- Produces (module-level, testable): `_video_delete(svc, video_id, confirm) -> dict`, `_video_rate(svc, video_id, rating, confirm) -> dict`. Plus `@app.tool()` wrappers `video_delete`, `video_rate`.

- [ ] **Step 1: Write the failing test `tests/test_edits_videos.py`**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import edits


def test_video_delete_gated_without_confirm():
    svc = MagicMock()
    r = edits._video_delete(svc, "vidX", confirm=False)
    assert r["error"] == "confirm_required"
    svc.videos.return_value.delete.assert_not_called()


def test_video_delete_runs_with_confirm(isolated_config):
    svc = MagicMock()
    svc.videos.return_value.delete.return_value.execute.return_value = ""
    r = edits._video_delete(svc, "vidX", confirm=True)
    assert r["deleted"] == "vidX"
    svc.videos.return_value.delete.assert_called_once_with(id="vidX")


def test_video_rate_rejects_bad_rating():
    svc = MagicMock()
    r = edits._video_rate(svc, "vidX", "love", confirm=True)
    assert r["error"].startswith("rating must be")
    svc.videos.return_value.rate.assert_not_called()


def test_video_rate_gated_without_confirm():
    svc = MagicMock()
    r = edits._video_rate(svc, "vidX", "like", confirm=False)
    assert r["error"] == "confirm_required"


def test_video_rate_runs_with_confirm(isolated_config):
    svc = MagicMock()
    svc.videos.return_value.rate.return_value.execute.return_value = ""
    r = edits._video_rate(svc, "vidX", "like", confirm=True)
    assert r["rated"] == "vidX"
    assert r["rating"] == "like"
    svc.videos.return_value.rate.assert_called_once_with(id="vidX", rating="like")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_edits_videos.py -v`
Expected: FAIL — `_video_delete` / `_video_rate` do not exist.

- [ ] **Step 3: Add the core functions + tool wrappers to `edits.py`**

At the top of `edits.py`, extend the imports:

```python
from .. import clients, gate, mutate, quota
```

Add these module-level functions **above** `register`:

```python
ALLOWED_RATINGS = {"like", "dislike", "none"}


def _video_delete(svc: Any, video_id: str, confirm: bool) -> dict:
    """videos.delete — irreversible, gated. Source:
    https://developers.google.com/youtube/v3/docs/videos/delete"""
    refusal = gate.require(
        confirm, effect=f"This permanently deletes video {video_id}.",
        video_id=video_id)
    if refusal:
        return refusal
    clients.run(lambda y: y.videos().delete(id=video_id), svc)
    quota.record("videos.delete")
    return {"deleted": video_id, "quota_units_spent": 50}


def _video_rate(svc: Any, video_id: str, rating: str, confirm: bool) -> dict:
    """videos.rate — like/dislike/none as the channel; gated (social). Source:
    https://developers.google.com/youtube/v3/docs/videos/rate"""
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
```

Inside `register(app)`, add the wrappers (after the existing `video_set_thumbnail` tool):

```python
    @app.tool()
    @clients.http_safe
    def video_delete(video_id: str, confirm: bool = False) -> dict:
        """Permanently delete a video. Quota: 50 units. Gated: irreversible —
        re-call with confirm=True after user approval."""
        return _video_delete(clients.youtube_data(), video_id, confirm)

    @app.tool()
    @clients.http_safe
    def video_rate(video_id: str, rating: str, confirm: bool = False) -> dict:
        """Set your channel's like/dislike on a video. Quota: 50 units. Gated:
        acts socially as your channel. rating is like, dislike, or none."""
        return _video_rate(clients.youtube_data(), video_id, rating, confirm)
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest tests/test_edits_videos.py -v`
Expected: PASS (5 passed).

- [ ] **Step 5: Commit**

```bash
git add tools/youtube-studio-mcp/src/youtube_studio_mcp/tools/edits.py tools/youtube-studio-mcp/tests/test_edits_videos.py
git commit -m "feat(youtube-mcp): video_delete + video_rate (gated)"
```

---

## Task 7: `video_schedule` (edits.py)

**Files:**
- Modify: `src/youtube_studio_mcp/tools/edits.py`
- Test: `tests/test_edits_schedule.py`

**Interfaces:**
- Consumes: `gate.require`, `mutate.fetch_merge_update`.
- Produces: `_video_schedule(svc, video_id, publish_at, confirm) -> dict` (arm a schedule — gated), `_video_cancel_schedule(svc, video_id) -> dict` (ungated; sets private, clears publishAt). Tool wrappers `video_schedule`, `video_cancel_schedule`.

- [ ] **Step 1: Write the failing test `tests/test_edits_schedule.py`**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import edits


def _svc_with_video(privacy="private", publish_at=None):
    svc = MagicMock()
    status = {"privacyStatus": privacy}
    if publish_at:
        status["publishAt"] = publish_at
    svc.videos.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "vidS", "snippet": {"title": "T", "categoryId": "22"},
                   "status": status}]
    }
    svc.videos.return_value.update.return_value.execute.return_value = {"id": "vidS"}
    return svc


def test_schedule_gated_without_confirm():
    svc = _svc_with_video()
    r = edits._video_schedule(svc, "vidS", "2026-07-01T12:00:00Z", confirm=False)
    assert r["error"] == "confirm_required"
    svc.videos.return_value.update.assert_not_called()


def test_schedule_sets_publishat_and_forces_private(isolated_config):
    svc = _svc_with_video()
    r = edits._video_schedule(svc, "vidS", "2026-07-01T12:00:00Z", confirm=True)
    body = svc.videos.return_value.update.call_args.kwargs["body"]
    assert body["status"]["publishAt"] == "2026-07-01T12:00:00Z"
    assert body["status"]["privacyStatus"] == "private"
    assert r["scheduled"] == "vidS"


def test_cancel_schedule_is_ungated_and_clears_publishat(isolated_config):
    svc = _svc_with_video(publish_at="2026-07-01T12:00:00Z")
    r = edits._video_cancel_schedule(svc, "vidS")
    body = svc.videos.return_value.update.call_args.kwargs["body"]
    assert body["status"]["privacyStatus"] == "private"
    assert body["status"].get("publishAt") is None
    assert r["schedule_cancelled"] == "vidS"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_edits_schedule.py -v`
Expected: FAIL — functions undefined.

- [ ] **Step 3: Add to `edits.py` (module-level, above `register`)**

```python
def _video_schedule(svc: Any, video_id: str, publish_at: str,
                    confirm: bool) -> dict:
    """Arm a scheduled publish. Gated. Sets status.publishAt + forces
    privacyStatus=private (required, re-sent even if already private). The video
    must never have been published. Source:
    https://developers.google.com/youtube/v3/docs/videos"""
    refusal = gate.require(
        confirm,
        effect=(f"This schedules video {video_id} to go PUBLIC automatically at "
                f"{publish_at}."),
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
    """Cancel a pending schedule: keep the video private, clear publishAt.
    Ungated — only ever makes the video less public."""
    try:
        resp = mutate.fetch_merge_update(
            svc, resource="videos", id=video_id, parts="status",
            patch={"status": {"privacyStatus": "private", "publishAt": None}},
            record_list="videos.list", record_update="videos.update")
    except KeyError:
        return {"error": "video_not_found", "video_id": video_id}
    return {"schedule_cancelled": video_id, "response": resp}
```

Inside `register(app)`, add wrappers:

```python
    @app.tool()
    @clients.http_safe
    def video_schedule(video_id: str, publish_at: str,
                       confirm: bool = False) -> dict:
        """Schedule a private video to auto-publish at publish_at (ISO-8601, e.g.
        2026-07-01T12:00:00Z). Quota: ~51 units. Gated: arms a future PUBLIC
        release. The video must be private and never previously published.
        To reschedule, call again with a new publish_at."""
        return _video_schedule(clients.youtube_data(), video_id, publish_at, confirm)

    @app.tool()
    @clients.http_safe
    def video_cancel_schedule(video_id: str) -> dict:
        """Cancel a pending scheduled publish — keeps the video private and
        clears publishAt. Quota: ~51 units. Ungated (only makes it less public)."""
        return _video_cancel_schedule(clients.youtube_data(), video_id)
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest tests/test_edits_schedule.py -v`
Expected: PASS (3 passed).

- [ ] **Step 5: Commit**

```bash
git add tools/youtube-studio-mcp/src/youtube_studio_mcp/tools/edits.py tools/youtube-studio-mcp/tests/test_edits_schedule.py
git commit -m "feat(youtube-mcp): video_schedule (gated) + cancel (ungated)"
```

---

## Task 8: `video_set_localizations` (edits.py)

**Files:**
- Modify: `src/youtube_studio_mcp/tools/edits.py`
- Test: `tests/test_edits_localizations.py`

**Interfaces:**
- Consumes: `mutate.fetch_merge_update`.
- Produces: `_video_set_localizations(svc, video_id, localizations, default_language) -> dict`. Tool wrapper `video_set_localizations`. `localizations` is `{lang: {"title": str, "description": str}}`.

- [ ] **Step 1: Write the failing test `tests/test_edits_localizations.py`**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import edits


def _svc():
    svc = MagicMock()
    svc.videos.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "vidL",
                   "snippet": {"title": "T", "categoryId": "22",
                               "defaultLanguage": "en"},
                   "localizations": {"es": {"title": "viejo", "description": "d"}}}]
    }
    svc.videos.return_value.update.return_value.execute.return_value = {"id": "vidL"}
    return svc


def test_localizations_require_default_language():
    svc = MagicMock()
    svc.videos.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "vidL", "snippet": {"title": "T", "categoryId": "22"}}]
    }
    r = edits._video_set_localizations(
        svc, "vidL", {"fr": {"title": "x", "description": "y"}},
        default_language=None)
    assert r["error"] == "default_language_required"


def test_localizations_merge_and_set_default_language(isolated_config):
    svc = _svc()
    r = edits._video_set_localizations(
        svc, "vidL", {"fr": {"title": "Bonjour", "description": "desc"}},
        default_language="en")
    body = svc.videos.return_value.update.call_args.kwargs["body"]
    assert "snippet,localizations" in svc.videos.return_value.update.call_args.kwargs["part"]
    assert body["snippet"]["defaultLanguage"] == "en"
    assert body["localizations"]["fr"]["title"] == "Bonjour"
    assert body["localizations"]["es"]["title"] == "viejo"   # existing preserved
    assert r["localized"] == "vidL"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_edits_localizations.py -v`
Expected: FAIL — function undefined.

- [ ] **Step 3: Add to `edits.py` (module-level)**

```python
def _video_set_localizations(svc: Any, video_id: str, localizations: dict,
                             default_language: str | None) -> dict:
    """Set per-language localized title/description. Ungated. Requires
    snippet.defaultLanguage (or defaultLanguageNotSet error). Existing
    translations are merged, not replaced. Source:
    https://developers.google.com/youtube/v3/docs/videos"""
    if not default_language:
        # The API rejects localizations without a default language; surface early.
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
```

Inside `register(app)`:

```python
    @app.tool()
    @clients.http_safe
    def video_set_localizations(video_id: str, localizations: dict,
                                default_language: str | None = None) -> dict:
        """Set localized title/description per language. Quota: ~51 units.
        Ungated. localizations = {lang: {"title": ..., "description": ...}}.
        default_language is the video's primary language (e.g. "en") — required
        by the API; if omitted it is read from the video. Existing translations
        are preserved and merged."""
        return _video_set_localizations(
            clients.youtube_data(), video_id, localizations, default_language)
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest tests/test_edits_localizations.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add tools/youtube-studio-mcp/src/youtube_studio_mcp/tools/edits.py tools/youtube-studio-mcp/tests/test_edits_localizations.py
git commit -m "feat(youtube-mcp): video_set_localizations"
```

---

## Task 9: `video_upload` (uploads.py — resumable)

**Files:**
- Create: `src/youtube_studio_mcp/tools/uploads.py`
- Test: `tests/test_uploads.py`

**Interfaces:**
- Consumes: `gate.require`, `uploadmedia.validate`, `uploadmedia.execute_resumable`, `quota.record`, `clients.youtube_data`.
- Produces: `_video_upload(svc, *, path, title, description, tags, category_id, privacy, publish_at, made_for_kids, contains_synthetic_media, confirm, media_factory) -> dict`. Tool wrapper `video_upload`. `media_factory(path, mime)` builds the `MediaFileUpload` (injected so tests don't touch disk-backed upload objects).

- [ ] **Step 1: Write the failing test `tests/test_uploads.py`**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import uploads


def _media_factory(path, mime):
    return MagicMock(name="media")


def test_upload_missing_file_errors(tmp_path):
    svc = MagicMock()
    r = uploads._video_upload(
        svc, path=str(tmp_path / "nope.mp4"), title="T", description="",
        tags=None, category_id="22", privacy="private", publish_at=None,
        made_for_kids=False, contains_synthetic_media=None, confirm=False,
        media_factory=_media_factory)
    assert r["error"] == "file_not_found"


def test_public_upload_gated(tmp_path):
    f = tmp_path / "clip.mp4"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    r = uploads._video_upload(
        svc, path=str(f), title="T", description="", tags=None,
        category_id="22", privacy="public", publish_at=None,
        made_for_kids=False, contains_synthetic_media=None, confirm=False,
        media_factory=_media_factory)
    assert r["error"] == "confirm_required"
    svc.videos.return_value.insert.assert_not_called()


def test_private_upload_runs_ungated(tmp_path, isolated_config, monkeypatch):
    f = tmp_path / "clip.mp4"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    monkeypatch.setattr(uploads.uploadmedia, "execute_resumable",
                        lambda req: {"id": "newVid", "status": {"privacyStatus": "private"}})
    r = uploads._video_upload(
        svc, path=str(f), title="My Title", description="desc", tags=["a", "b"],
        category_id="28", privacy="private", publish_at=None,
        made_for_kids=False, contains_synthetic_media=True, confirm=False,
        media_factory=_media_factory)
    assert r["uploaded"] == "newVid"
    body = svc.videos.return_value.insert.call_args.kwargs["body"]
    assert body["snippet"]["title"] == "My Title"
    assert body["snippet"]["tags"] == ["a", "b"]
    assert body["status"]["privacyStatus"] == "private"
    assert body["status"]["containsSyntheticMedia"] is True


def test_scheduled_upload_is_gated_and_forces_private(tmp_path, isolated_config, monkeypatch):
    f = tmp_path / "clip.mp4"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    monkeypatch.setattr(uploads.uploadmedia, "execute_resumable",
                        lambda req: {"id": "schVid"})
    # gated because publish_at set
    r0 = uploads._video_upload(
        svc, path=str(f), title="T", description="", tags=None,
        category_id="22", privacy="private", publish_at="2026-07-01T12:00:00Z",
        made_for_kids=False, contains_synthetic_media=None, confirm=False,
        media_factory=_media_factory)
    assert r0["error"] == "confirm_required"
    # confirmed → runs, publishAt present, privacy forced private
    r1 = uploads._video_upload(
        svc, path=str(f), title="T", description="", tags=None,
        category_id="22", privacy="private", publish_at="2026-07-01T12:00:00Z",
        made_for_kids=False, contains_synthetic_media=None, confirm=True,
        media_factory=_media_factory)
    body = svc.videos.return_value.insert.call_args.kwargs["body"]
    assert body["status"]["publishAt"] == "2026-07-01T12:00:00Z"
    assert body["status"]["privacyStatus"] == "private"
    assert r1["uploaded"] == "schVid"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_uploads.py -v`
Expected: FAIL — module/function undefined.

- [ ] **Step 3: Write `src/youtube_studio_mcp/tools/uploads.py`**

```python
"""Upload tools (resumable). Currently: video_upload (videos.insert). Banner and
watermark uploads land here in a later plan.

videos.insert costs 1 unit from a separate 100/day Uploads bucket — not the 10k
pool. A Short is just a vertical video <=3 min uploaded through this same path;
there is no Shorts-specific field. Sources:
https://developers.google.com/youtube/v3/docs/videos/insert
https://developers.google.com/youtube/v3/determine_quota_cost
"""

from __future__ import annotations

from typing import Any, Callable

from googleapiclient.http import MediaFileUpload
from mcp.server.fastmcp import FastMCP

from .. import clients, gate, quota, uploadmedia

MAX_VIDEO_BYTES = 256 * 1024 * 1024 * 1024  # 256 GB hard cap
VIDEO_MIMES = {"video/*"}
ALLOWED_PRIVACY = {"private", "unlisted", "public"}


def _default_media_factory(path: str, mime: str) -> Any:
    return MediaFileUpload(path, mimetype=mime, resumable=True)


def _video_upload(svc: Any, *, path: str, title: str, description: str,
                  tags: list[str] | None, category_id: str, privacy: str,
                  publish_at: str | None, made_for_kids: bool,
                  contains_synthetic_media: bool | None, confirm: bool,
                  media_factory: Callable[[str, str], Any]) -> dict:
    """videos.insert via resumable upload. Gated only when the result is
    immediately or eventually PUBLIC (privacy=public or a publish_at is set)."""
    if privacy not in ALLOWED_PRIVACY:
        return {"error": f"privacy must be one of {sorted(ALLOWED_PRIVACY)}"}

    pre = uploadmedia.validate(path, max_bytes=MAX_VIDEO_BYTES,
                               allowed_mimes=VIDEO_MIMES)
    if not pre["ok"]:
        return pre

    is_public_facing = privacy == "public" or publish_at is not None
    if is_public_facing:
        effect = (f"This uploads and SCHEDULES the video to go public at "
                  f"{publish_at}." if publish_at
                  else "This uploads the video as PUBLIC immediately.")
        refusal = gate.require(confirm, effect=effect, title=title,
                               privacy=privacy, publish_at=publish_at)
        if refusal:
            return refusal

    status: dict[str, Any] = {
        "privacyStatus": "private" if publish_at else privacy,
        "selfDeclaredMadeForKids": made_for_kids,
    }
    if publish_at:
        status["publishAt"] = publish_at
    if contains_synthetic_media is not None:
        status["containsSyntheticMedia"] = contains_synthetic_media

    snippet: dict[str, Any] = {"title": title, "categoryId": category_id}
    if description:
        snippet["description"] = description
    if tags:
        snippet["tags"] = tags

    body = {"snippet": snippet, "status": status}
    media = media_factory(pre["path"], pre["mime"])
    request = svc.videos().insert(part="snippet,status", body=body,
                                  media_body=media)
    resp = uploadmedia.execute_resumable(request)
    quota.record("videos.insert")
    return {"uploaded": resp.get("id"), "privacy": status["privacyStatus"],
            "publish_at": publish_at, "response": resp}


def register(app: FastMCP) -> None:
    @app.tool()
    @clients.http_safe
    def video_upload(path: str, title: str, description: str = "",
                     tags: list[str] | None = None, category_id: str = "22",
                     privacy: str = "private", publish_at: str | None = None,
                     made_for_kids: bool = False,
                     contains_synthetic_media: bool | None = None,
                     confirm: bool = False) -> dict:
        """Upload a video or Short (resumable). Quota: 1 unit (100/day Uploads
        bucket). A Short is just a vertical video <=3 min — same call.

        Gated ONLY when the upload is public-facing: privacy="public", or a
        publish_at is set (which schedules a public release). A private upload
        runs ungated. When publish_at is set, privacy is forced to private (the
        API requirement) and the video auto-publishes at that time.

        Args:
            path: local video file (mp4/mov/m4v/webm), <=256 GB.
            title: <=100 chars. description: <=5000 bytes. tags: <=500 chars total.
            category_id: e.g. "22" People & Blogs, "28" Science & Tech.
            privacy: private | unlisted | public.
            publish_at: ISO-8601 (e.g. 2026-07-01T12:00:00Z) to schedule.
            made_for_kids: self-declared COPPA flag.
            contains_synthetic_media: the "contains AI/altered content" disclosure.
            confirm: required for public or scheduled uploads.
        """
        return _video_upload(
            clients.youtube_data(), path=path, title=title,
            description=description, tags=tags, category_id=category_id,
            privacy=privacy, publish_at=publish_at, made_for_kids=made_for_kids,
            contains_synthetic_media=contains_synthetic_media, confirm=confirm,
            media_factory=_default_media_factory)
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest tests/test_uploads.py -v`
Expected: PASS (4 passed).

- [ ] **Step 5: Commit**

```bash
git add tools/youtube-studio-mcp/src/youtube_studio_mcp/tools/uploads.py tools/youtube-studio-mcp/tests/test_uploads.py
git commit -m "feat(youtube-mcp): video_upload (resumable, gated when public/scheduled)"
```

---

## Task 10: Wire scope + register uploads module

**Files:**
- Modify: `src/youtube_studio_mcp/auth.py:25-30` (SCOPES)
- Modify: `src/youtube_studio_mcp/server.py:14,20-26`
- Test: `tests/test_wiring.py`

**Interfaces:**
- Consumes: `server.app`.
- Produces: `youtube.upload` in `auth.SCOPES`; `uploads.register(app)` called; all new tools discoverable on the app.

- [ ] **Step 1: Write the failing test `tests/test_wiring.py`**

```python
import asyncio


def test_upload_scope_present():
    from youtube_studio_mcp import auth
    assert "https://www.googleapis.com/auth/youtube.upload" in auth.SCOPES


def test_new_tools_registered():
    from youtube_studio_mcp.server import app
    names = set(asyncio.run(_tool_names(app)))
    for t in ("video_upload", "video_delete", "video_rate", "video_schedule",
              "video_cancel_schedule", "video_set_localizations"):
        assert t in names, f"{t} not registered"


async def _tool_names(app):
    tools = await app.list_tools()
    return [t.name for t in tools]
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_wiring.py -v`
Expected: FAIL — scope missing and `video_upload` not registered.

- [ ] **Step 3: Add the scope in `auth.py`**

In the `SCOPES` list, after the `youtube.force-ssl` entry add:

```python
    "https://www.googleapis.com/auth/youtube.upload",
```

- [ ] **Step 4: Register the uploads module in `server.py`**

Change the tools import line to include `uploads`:

```python
from .tools import analytics, comments, data, edits, meta, reporting, uploads
```

And after `edits.register(app)` add:

```python
uploads.register(app)
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `uv run pytest tests/test_wiring.py -v`
Expected: PASS (2 passed).

- [ ] **Step 6: Run the full suite**

Run: `uv run pytest -q`
Expected: all green.

- [ ] **Step 7: Commit**

```bash
git add tools/youtube-studio-mcp/src/youtube_studio_mcp/auth.py tools/youtube-studio-mcp/src/youtube_studio_mcp/server.py tools/youtube-studio-mcp/tests/test_wiring.py
git commit -m "feat(youtube-mcp): request youtube.upload scope + register uploads tools"
```

**Note for the operator:** adding a scope does not invalidate the existing
`force-ssl` token (which already authorizes all these writes), so re-auth is
optional. To grant the new scope explicitly, run
`uv run youtube-studio-mcp auth` once.

---

## Task 11: Refactor `video_update_metadata` onto `mutate.py` + docs

**Files:**
- Modify: `src/youtube_studio_mcp/tools/edits.py` (the existing `video_update_metadata`)
- Modify: `tools/youtube-studio-mcp/CLAUDE.md` (scope cap section)
- Test: `tests/test_edits_update_refactor.py`

**Interfaces:**
- Consumes: `mutate.fetch_merge_update`.
- Produces: unchanged external behavior of `video_update_metadata` (still gates private→public via `confirm_publish`), now sharing the merge helper.

- [ ] **Step 1: Write the failing test `tests/test_edits_update_refactor.py`**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import edits


def _svc():
    svc = MagicMock()
    svc.videos.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "vidU",
                   "snippet": {"title": "Old", "categoryId": "22",
                               "description": "keep", "tags": ["t1"]},
                   "status": {"privacyStatus": "private"}}]
    }
    svc.videos.return_value.update.return_value.execute.return_value = {"id": "vidU"}
    return svc


def test_update_title_preserves_description_and_tags(isolated_config):
    svc = _svc()
    out = edits._video_update_metadata(svc, video_id="vidU", title="New")
    body = svc.videos.return_value.update.call_args.kwargs["body"]
    assert body["snippet"]["title"] == "New"
    assert body["snippet"]["description"] == "keep"   # preserved by merge
    assert body["snippet"]["tags"] == ["t1"]
    assert out["updated"] == "vidU"


def test_private_to_public_still_gated(isolated_config):
    svc = _svc()
    out = edits._video_update_metadata(svc, video_id="vidU",
                                       privacy_status="public",
                                       confirm_publish=False)
    assert out["error"] == "confirm_publish_required"
    svc.videos.return_value.update.assert_not_called()
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_edits_update_refactor.py -v`
Expected: FAIL — `_video_update_metadata` (module-level) does not exist yet (logic is currently inline in the tool).

- [ ] **Step 3: Extract `_video_update_metadata(svc, ...)` in `edits.py`**

Move the existing body of `video_update_metadata` into a module-level
`_video_update_metadata(svc, video_id, title=None, description=None, tags=None,
category_id=None, default_language=None, default_audio_language=None,
privacy_status=None, confirm_publish=False)`, replacing the two hand-rolled
`clients.run(... list ...)` + manual snippet rebuild with a single
`mutate.fetch_merge_update` call. Keep the privacy-guard and `ALLOWED_PRIVACY`
check verbatim. The build of the `patch` dict:

```python
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
```

The privacy guard needs `prev_privacy`; fetch it once before the patch build:

```python
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
```

Then make the `@app.tool()` `video_update_metadata` wrapper delegate:

```python
        return _video_update_metadata(
            clients.youtube_data(), video_id=video_id, title=title,
            description=description, tags=tags, category_id=category_id,
            default_language=default_language,
            default_audio_language=default_audio_language,
            privacy_status=privacy_status, confirm_publish=confirm_publish)
```

(The extra `videos.list` in the guard plus the one inside `fetch_merge_update`
means a public-transition update lists twice; acceptable at 1 unit each and
keeps the guard independent of the merge helper.)

- [ ] **Step 4: Run the test to verify it passes**

Run: `uv run pytest tests/test_edits_update_refactor.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Rewrite the scope-cap section of `tools/youtube-studio-mcp/CLAUDE.md`**

Replace the "## Scope cap (locked)" section with:

```markdown
## Scope (v2 — write surface open)

The video/Short write surface is fully exposed: `video_upload` (videos.insert,
resumable), `video_delete`, `video_rate`, `video_schedule` /
`video_cancel_schedule`, `video_set_localizations`, plus the existing
`video_update_metadata` / `video_set_thumbnail`. Gated (need `confirm=True`):
delete, rate, public/scheduled upload, schedule, private->public.

Still deferred (separate plans): captions, playlists, channel branding,
subscriptions. Still NO API anywhere (do not attempt): A/B Test & Compare,
comment settings, end screens, info cards, age restriction, monetization,
multi-language audio dubs, live streaming, CMS/content-owner, multi-channel.

OAuth: `youtube.force-ssl` already authorizes every write; `youtube.upload` is
also requested as a least-surprise marker. No re-consent required for existing
tokens.
```

- [ ] **Step 6: Run the full suite**

Run: `uv run pytest -q`
Expected: all green.

- [ ] **Step 7: Commit**

```bash
git add tools/youtube-studio-mcp/src/youtube_studio_mcp/tools/edits.py tools/youtube-studio-mcp/tests/test_edits_update_refactor.py tools/youtube-studio-mcp/CLAUDE.md
git commit -m "refactor(youtube-mcp): video_update_metadata onto mutate helper + v2 scope docs"
```

---

## Self-Review

**Spec coverage (spec §7.1 + §6):**
- Read-modify-write helper (§6.1) → Task 4. ✓
- Resumable upload helper (§6.2) → Task 5. ✓
- Confirm-gate (§6.3) → Task 3. ✓
- Quota table (§4) → Task 2. ✓
- `video_upload` → Task 9; `video_delete` → Task 6; `video_rate` → Task 6; `video_schedule` (+reschedule/cancel) → Task 7; `video_set_localizations` → Task 8; `video_update_metadata` refactor → Task 11. ✓
- OAuth scope analysis (§3) → Task 10. ✓
- Downstream CLAUDE.md update (§8, partial — this plan's surface only) → Task 11. ✓
- Captions / playlists / channel-level / subscriptions → **out of scope for Plan 1** (Plans 2–4).

**Placeholder scan:** No TBD/TODO; every code step has complete code; every test has assertions.

**Type consistency:** `fetch_merge_update(svc, *, resource, id, parts, patch, record_list, record_update)` signature is identical across Tasks 4, 7, 8, 11. `gate.require(confirm, *, effect, **extra)` identical across Tasks 3, 6, 7, 9. `_video_*` cores all take `svc` first and return `dict`. `uploadmedia.validate(path, *, max_bytes, allowed_mimes)` and `execute_resumable(request)` match between Task 5 and Task 9.

**Note on `mutate` `videos.list` part:** Task 7/8 fetch `status` / `snippet,localizations` parts respectively; the merge helper fetches exactly the parts it will PUT, so required fields (`snippet.title`, `snippet.categoryId`) are always present in the fetched body before merge. ✓
