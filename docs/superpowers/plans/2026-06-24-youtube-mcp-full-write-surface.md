# YouTube MCP Full Write Surface Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lift the `youtube-studio-mcp` v1 scope cap and expose the complete YouTube Data API v3 write surface — uploads (videos + Shorts), scheduling, captions, localizations, playlists, channel branding, and subscriptions — each grounded in the official docs and guarded by a uniform confirm-gate.

**Architecture:** Tools follow a **dependency-injection core + thin tool wrapper** pattern: each tool's logic lives in a module-level function taking the googleapiclient service first (unit-testable with a `MagicMock`), and the `@app.tool()` wrapper calls it with `clients.youtube_data()`. Three shared helpers — `gate.py` (confirm/quota interlock), `mutate.py` (fetch-merge-update so PUT never wipes omitted fields), `uploadmedia.py` (resumable upload + file validate) — are built once (Part A) and reused everywhere.

**Tech Stack:** Python 3.12, `google-api-python-client`, FastMCP (`mcp[cli]`), `pytest` (added here), SQLite quota ledger.

**Spec:** `docs/superpowers/specs/2026-06-24-youtube-mcp-full-write-surface-design.md`.

## Global Constraints

- Working dir for all commands: `tools/youtube-studio-mcp/`. Run Python via `uv run`.
- Required Python: `>=3.12`.
- Every API call records cost via `quota.record("<endpoint>")` with a key present in `quota.COSTS`.
- Every tool is decorated `@app.tool()` then `@clients.http_safe` (that order), and uses `clients.run(lambda y: ..., svc)` for retry/backoff.
- **Gate convention:** gated tools take `confirm: bool = False`; when `False` they return `{"error": "confirm_required", ...}` and make **no** API call. Expensive writes use `gate.quota_guard`.
- **PUT is destructive:** every `*.update` re-sends existing values via `mutate.fetch_merge_update`; never send a sparse update body. Source: https://developers.google.com/youtube/v3/docs/videos/update
- OAuth: `youtube.force-ssl` (already granted) authorizes everything; we additively request `youtube.upload`. No token invalidation.
- Video field limits: `title` ≤100 chars; `description` ≤5000 **bytes**; `tags` ≤500 chars total. `videos.update` of `snippet` must re-send `id`, `snippet.title`, `snippet.categoryId`. Source: https://developers.google.com/youtube/v3/docs/videos
- Scheduling: `status.publishAt` (ISO-8601) requires `status.privacyStatus=private`, re-sent even if already private; video must never have been published. Source: https://developers.google.com/youtube/v3/docs/videos
- `videos.insert` = 1 unit in a separate 100/day Uploads bucket. `captions.insert` = 400, `captions.update` = 450 (quota-guarded). Source: https://developers.google.com/youtube/v3/determine_quota_cost
- Localizations require `defaultLanguage` set or the API returns `defaultLanguageNotSet`.

---

## File Structure

- Create: `src/youtube_studio_mcp/gate.py` — confirm + quota gate.
- Create: `src/youtube_studio_mcp/mutate.py` — fetch-merge-update helper.
- Create: `src/youtube_studio_mcp/uploadmedia.py` — resumable upload + file validate.
- Create: `src/youtube_studio_mcp/tools/uploads.py` — `video_upload`, `channel_set_banner`, `channel_set_watermark`.
- Create: `src/youtube_studio_mcp/tools/captions.py` — caption list/insert/update/delete/download.
- Create: `src/youtube_studio_mcp/tools/playlists.py` — playlists + playlistItems + playlistImages.
- Create: `src/youtube_studio_mcp/tools/channel_edits.py` — channels.update branding/localizations, channelSections, watermark unset.
- Create: `src/youtube_studio_mcp/tools/subscriptions.py` — subscription add/remove.
- Modify: `src/youtube_studio_mcp/tools/edits.py` — add video delete/rate/schedule/localizations; refactor `video_update_metadata`.
- Modify: `src/youtube_studio_mcp/quota.py` — add new endpoint costs.
- Modify: `src/youtube_studio_mcp/auth.py` — add `youtube.upload` scope.
- Modify: `src/youtube_studio_mcp/server.py` — register new modules.
- Modify: `tools/youtube-studio-mcp/CLAUDE.md` — rewrite scope cap v1→v2.
- Modify: `pyproject.toml` — pytest dev group + config.
- Create: `tests/conftest.py` + per-module test files.

---

# PART A — Shared Foundation

## Task 1: Test harness (pytest + isolated conftest)

**Files:** Modify `pyproject.toml`; Create `tests/conftest.py`, `tests/test_smoke.py`.

**Interfaces:** Produces fixtures `isolated_config` (autouse; redirects `YOUTUBE_STUDIO_MCP_CONFIG_DIR` to tmp so `quota.db` is isolated) and `svc` (`MagicMock` standing in for a YouTube Data service).

- [ ] **Step 1: Add pytest dev group to `pyproject.toml`** (after `[tool.pyright]`):

```toml
[dependency-groups]
dev = [
    "pytest>=8.3.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-q"
```

- [ ] **Step 2: Sync** — Run: `uv sync --group dev` → installs pytest.

- [ ] **Step 3: Write `tests/conftest.py`:**

```python
"""Shared test fixtures. `isolated_config` redirects the config dir (quota.db)
to tmp. `svc` is a MagicMock YouTube Data service; configure per test:
    svc.videos.return_value.list.return_value.execute.return_value = {...}
"""

from __future__ import annotations

import importlib
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    monkeypatch.setenv("YOUTUBE_STUDIO_MCP_CONFIG_DIR", str(tmp_path))
    from youtube_studio_mcp import paths
    importlib.reload(paths)
    yield tmp_path


@pytest.fixture
def svc():
    return MagicMock(name="youtube_data_service")
```

- [ ] **Step 4: Write `tests/test_smoke.py`:**

```python
def test_quota_records(isolated_config):
    from youtube_studio_mcp import quota
    assert quota.record("videos.update") == 50
    assert quota.spent_today() == 50
```

- [ ] **Step 5: Run** — Run: `uv run pytest tests/test_smoke.py -v` → PASS.

- [ ] **Step 6: Commit:**

```bash
git add pyproject.toml uv.lock tests/conftest.py tests/test_smoke.py
git commit -m "test(youtube-mcp): add pytest harness with isolated config + svc fixtures"
```

---

## Task 2: Quota cost additions

**Files:** Modify `src/youtube_studio_mcp/quota.py` (the `COSTS` dict); Test `tests/test_quota_costs.py`.

**Interfaces:** Produces `COSTS` keys for `videos.insert`, `videos.delete`, `playlists.*`, `playlistItems.*`, `playlistImages.*`, `channels.update`, `channelSections.*`, `channelBanners.insert`, `watermarks.set/unset`.

- [ ] **Step 1: Write failing test `tests/test_quota_costs.py`:**

```python
import pytest

from youtube_studio_mcp import quota
from youtube_studio_mcp.quota import _cost_of

EXPECTED = {
    "videos.insert": 1, "videos.delete": 50,
    "playlists.insert": 50, "playlists.update": 50, "playlists.delete": 50,
    "playlistItems.insert": 50, "playlistItems.update": 50, "playlistItems.delete": 50,
    "playlistImages.insert": 50, "playlistImages.update": 50, "playlistImages.delete": 50,
    "channels.update": 50,
    "channelSections.insert": 50, "channelSections.update": 50, "channelSections.delete": 50,
    "channelBanners.insert": 50, "watermarks.set": 50, "watermarks.unset": 50,
}


@pytest.mark.parametrize("endpoint,units", EXPECTED.items())
def test_cost_known(endpoint, units):
    assert quota.cost_of(endpoint) == units
    assert _cost_of(endpoint)[1] is False
```

- [ ] **Step 2: Run to verify fail** — `uv run pytest tests/test_quota_costs.py -v` → FAIL (unknown endpoints default to 1).

- [ ] **Step 3: Add to `COSTS` in `quota.py`.** Under `# writes` add:

```python
    "videos.insert": 1,  # 100/day Uploads bucket; 1 unit/call (NOT the 10k pool)
    "videos.delete": 50,
```

Append a new block before the closing brace:

```python
    # playlists / items / images
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

- [ ] **Step 4: Run to verify pass** — `uv run pytest tests/test_quota_costs.py -v` → PASS.

- [ ] **Step 5: Commit:**

```bash
git add src/youtube_studio_mcp/quota.py tests/test_quota_costs.py
git commit -m "feat(youtube-mcp): add quota costs for full write surface"
```

---

## Task 3: Confirm-gate helper (`gate.py`)

**Files:** Create `src/youtube_studio_mcp/gate.py`; Test `tests/test_gate.py`.

**Interfaces:** Produces `gate.require(confirm, *, effect, **extra) -> dict | None` and `gate.quota_guard(endpoint, multiplier, confirm, *, fraction_limit=0.25) -> dict | None`.

- [ ] **Step 1: Write failing test `tests/test_gate.py`:**

```python
from youtube_studio_mcp import gate, quota


def test_require_blocks_without_confirm():
    r = gate.require(False, effect="This deletes video abc.", video_id="abc")
    assert r["error"] == "confirm_required"
    assert "deletes video abc" in r["reason"]
    assert r["video_id"] == "abc"


def test_require_passes_with_confirm():
    assert gate.require(True, effect="x") is None


def test_quota_guard_blocks_without_confirm():
    r = gate.quota_guard("captions.insert", 1, confirm=False)
    assert r["error"] == "confirm_required"
    assert r["estimated_cost_units"] == 400


def test_quota_guard_refuses_when_over_fraction(isolated_config):
    quota.record("search.list", multiplier=99)  # 9900 spent, 100 remaining
    r = gate.quota_guard("captions.insert", 1, confirm=True)
    assert r["error"] == "quota_safety_refused"


def test_quota_guard_allows_when_affordable(isolated_config):
    assert gate.quota_guard("videos.update", 1, confirm=True) is None
```

- [ ] **Step 2: Run to verify fail** — FAIL "No module named ...gate".

- [ ] **Step 3: Write `src/youtube_studio_mcp/gate.py`:**

```python
"""Confirmation interlocks for irreversible / public-facing / social writes.

A gated tool calls gate.require(...) (or gate.quota_guard(...)) first; if it
returns a dict, the tool returns it unchanged and performs no API call. Mirrors
the existing confirm_publish pattern and the bulk-comment guard.
"""

from __future__ import annotations

from typing import Any

from . import quota

DEFAULT_FRACTION_LIMIT = 0.25


def require(confirm: bool, *, effect: str, **extra: Any) -> dict | None:
    """Refusal dict when confirm is False, else None. `effect` is one sentence
    describing the action, e.g. 'This permanently deletes video abc123.'"""
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
    """Gate an expensive write on confirmation AND remaining quota."""
    cost = quota.cost_of(endpoint) * multiplier
    if not confirm:
        return {"error": "confirm_required",
                "reason": (f"This costs {cost} quota units. Re-call with "
                           "confirm=True after user approval."),
                "estimated_cost_units": cost}
    rem = quota.remaining()
    if rem > 0 and cost > rem * fraction_limit:
        return {"error": "quota_safety_refused",
                "reason": (f"This would cost {cost} units, more than "
                           f"{int(fraction_limit * 100)}% of the {rem} units "
                           "remaining today. Wait for reset or split the work."),
                "estimated_cost_units": cost, "remaining_quota_units": rem}
    return None
```

- [ ] **Step 4: Run to verify pass** — PASS (5).

- [ ] **Step 5: Commit:**

```bash
git add src/youtube_studio_mcp/gate.py tests/test_gate.py
git commit -m "feat(youtube-mcp): shared confirm-gate + quota guard helper"
```

---

## Task 4: Read-modify-write helper (`mutate.py`)

**Files:** Create `src/youtube_studio_mcp/mutate.py`; Test `tests/test_mutate.py`.

**Interfaces:** Produces `mutate.deep_merge(base, patch) -> dict` and `mutate.fetch_merge_update(svc, *, resource, id, parts, patch, record_list, record_update) -> dict` (raises `KeyError("resource_not_found")` when missing).

- [ ] **Step 1: Write failing test `tests/test_mutate.py`:**

```python
from unittest.mock import MagicMock

import pytest

from youtube_studio_mcp import mutate


def test_deep_merge_overlays_nested():
    base = {"snippet": {"title": "old", "categoryId": "22", "tags": ["a"]}}
    out = mutate.deep_merge(base, {"snippet": {"title": "new"}})
    assert out["snippet"]["title"] == "new"
    assert out["snippet"]["categoryId"] == "22"
    assert out["snippet"]["tags"] == ["a"]


def test_fetch_merge_update_preserves_unsent_fields(isolated_config):
    svc = MagicMock()
    svc.videos.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "vid1", "snippet": {"title": "Old", "categoryId": "28",
                   "description": "keep me", "tags": ["x", "y"]}}]}
    svc.videos.return_value.update.return_value.execute.return_value = {"id": "vid1"}
    resp = mutate.fetch_merge_update(
        svc, resource="videos", id="vid1", parts="snippet",
        patch={"snippet": {"title": "New Title"}},
        record_list="videos.list", record_update="videos.update")
    assert resp == {"id": "vid1"}
    body = svc.videos.return_value.update.call_args.kwargs["body"]
    assert body["id"] == "vid1"
    assert body["snippet"]["title"] == "New Title"
    assert body["snippet"]["categoryId"] == "28"
    assert body["snippet"]["description"] == "keep me"


def test_fetch_merge_update_raises_when_missing(isolated_config):
    svc = MagicMock()
    svc.videos.return_value.list.return_value.execute.return_value = {"items": []}
    with pytest.raises(KeyError):
        mutate.fetch_merge_update(
            svc, resource="videos", id="nope", parts="snippet",
            patch={"snippet": {"title": "x"}},
            record_list="videos.list", record_update="videos.update")
```

- [ ] **Step 2: Run to verify fail** — FAIL "No module named ...mutate".

- [ ] **Step 3: Write `src/youtube_studio_mcp/mutate.py`:**

```python
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
```

- [ ] **Step 4: Run to verify pass** — PASS (3).

- [ ] **Step 5: Commit:**

```bash
git add src/youtube_studio_mcp/mutate.py tests/test_mutate.py
git commit -m "feat(youtube-mcp): fetch-merge-update helper for non-destructive PUT"
```

---

## Task 5: Resumable upload helper (`uploadmedia.py`)

**Files:** Create `src/youtube_studio_mcp/uploadmedia.py`; Test `tests/test_uploadmedia.py`.

**Interfaces:** Produces `uploadmedia.MIME_BY_EXT`, `uploadmedia.validate(path, *, max_bytes, allowed_mimes) -> dict`, `uploadmedia.execute_resumable(request) -> dict`.

- [ ] **Step 1: Write failing test `tests/test_uploadmedia.py`:**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp import uploadmedia


def test_validate_ok(tmp_path):
    f = tmp_path / "clip.mp4"; f.write_bytes(b"\x00" * 10)
    r = uploadmedia.validate(f, max_bytes=1000, allowed_mimes={"video/*"})
    assert r["ok"] and r["mime"] == "video/*" and r["size_bytes"] == 10


def test_validate_missing_file(tmp_path):
    r = uploadmedia.validate(tmp_path / "nope.mp4", max_bytes=1000, allowed_mimes={"video/*"})
    assert r["ok"] is False and r["error"] == "file_not_found"


def test_validate_too_large(tmp_path):
    f = tmp_path / "big.mp4"; f.write_bytes(b"\x00" * 100)
    r = uploadmedia.validate(f, max_bytes=10, allowed_mimes={"video/*"})
    assert r["error"] == "file_too_large"


def test_validate_unsupported(tmp_path):
    f = tmp_path / "doc.txt"; f.write_bytes(b"x")
    r = uploadmedia.validate(f, max_bytes=1000, allowed_mimes={"video/*"})
    assert r["error"] == "unsupported_format"


def test_execute_resumable_loops_until_done():
    request = MagicMock()
    request.next_chunk.side_effect = [
        (MagicMock(progress=lambda: 0.5), None), (None, {"id": "vid123"})]
    assert uploadmedia.execute_resumable(request) == {"id": "vid123"}
    assert request.next_chunk.call_count == 2
```

- [ ] **Step 2: Run to verify fail** — FAIL "No module named ...uploadmedia".

- [ ] **Step 3: Write `src/youtube_studio_mcp/uploadmedia.py`:**

```python
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
```

- [ ] **Step 4: Run to verify pass** — PASS (5).

- [ ] **Step 5: Commit:**

```bash
git add src/youtube_studio_mcp/uploadmedia.py tests/test_uploadmedia.py
git commit -m "feat(youtube-mcp): resumable upload + file-validate helper"
```

---

# PART B — Videos & Shorts

## Task 6: `video_delete` and `video_rate` (edits.py)

**Files:** Modify `src/youtube_studio_mcp/tools/edits.py`; Test `tests/test_edits_videos.py`.

**Interfaces:** Produces module-level `_video_delete(svc, video_id, confirm) -> dict`, `_video_rate(svc, video_id, rating, confirm) -> dict`, and tool wrappers `video_delete`, `video_rate`. Extend the `edits.py` import to `from .. import clients, gate, mutate, quota`.

- [ ] **Step 1: Write failing test `tests/test_edits_videos.py`:**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import edits


def test_video_delete_gated():
    svc = MagicMock()
    assert edits._video_delete(svc, "vidX", confirm=False)["error"] == "confirm_required"
    svc.videos.return_value.delete.assert_not_called()


def test_video_delete_runs(isolated_config):
    svc = MagicMock()
    svc.videos.return_value.delete.return_value.execute.return_value = ""
    assert edits._video_delete(svc, "vidX", confirm=True)["deleted"] == "vidX"
    svc.videos.return_value.delete.assert_called_once_with(id="vidX")


def test_video_rate_rejects_bad_rating():
    svc = MagicMock()
    assert edits._video_rate(svc, "vidX", "love", confirm=True)["error"].startswith("rating must be")


def test_video_rate_gated():
    svc = MagicMock()
    assert edits._video_rate(svc, "vidX", "like", confirm=False)["error"] == "confirm_required"


def test_video_rate_runs(isolated_config):
    svc = MagicMock()
    svc.videos.return_value.rate.return_value.execute.return_value = ""
    r = edits._video_rate(svc, "vidX", "like", confirm=True)
    assert r["rated"] == "vidX" and r["rating"] == "like"
    svc.videos.return_value.rate.assert_called_once_with(id="vidX", rating="like")
```

- [ ] **Step 2: Run to verify fail** — FAIL (functions undefined).

- [ ] **Step 3: Add to `edits.py`.** Extend imports: `from .. import clients, gate, mutate, quota`. Add module-level above `register`:

```python
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
```

Inside `register(app)` (after `video_set_thumbnail`):

```python
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
```

- [ ] **Step 4: Run to verify pass** — PASS (5).

- [ ] **Step 5: Commit:**

```bash
git add src/youtube_studio_mcp/tools/edits.py tests/test_edits_videos.py
git commit -m "feat(youtube-mcp): video_delete + video_rate (gated)"
```

---

## Task 7: `video_schedule` + cancel (edits.py)

**Files:** Modify `edits.py`; Test `tests/test_edits_schedule.py`.

**Interfaces:** Produces `_video_schedule(svc, video_id, publish_at, confirm) -> dict` (gated), `_video_cancel_schedule(svc, video_id) -> dict` (ungated), wrappers `video_schedule`, `video_cancel_schedule`.

- [ ] **Step 1: Write failing test `tests/test_edits_schedule.py`:**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import edits


def _svc(privacy="private", publish_at=None):
    svc = MagicMock()
    status = {"privacyStatus": privacy}
    if publish_at:
        status["publishAt"] = publish_at
    svc.videos.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "vidS", "snippet": {"title": "T", "categoryId": "22"},
                   "status": status}]}
    svc.videos.return_value.update.return_value.execute.return_value = {"id": "vidS"}
    return svc


def test_schedule_gated():
    svc = _svc()
    assert edits._video_schedule(svc, "vidS", "2026-07-01T12:00:00Z", False)["error"] == "confirm_required"
    svc.videos.return_value.update.assert_not_called()


def test_schedule_sets_publishat_and_forces_private(isolated_config):
    svc = _svc()
    r = edits._video_schedule(svc, "vidS", "2026-07-01T12:00:00Z", True)
    body = svc.videos.return_value.update.call_args.kwargs["body"]
    assert body["status"]["publishAt"] == "2026-07-01T12:00:00Z"
    assert body["status"]["privacyStatus"] == "private"
    assert r["scheduled"] == "vidS"


def test_cancel_is_ungated_and_clears(isolated_config):
    svc = _svc(publish_at="2026-07-01T12:00:00Z")
    r = edits._video_cancel_schedule(svc, "vidS")
    body = svc.videos.return_value.update.call_args.kwargs["body"]
    assert body["status"]["privacyStatus"] == "private"
    assert body["status"].get("publishAt") is None
    assert r["schedule_cancelled"] == "vidS"
```

- [ ] **Step 2: Run to verify fail** — FAIL.

- [ ] **Step 3: Add to `edits.py` (module-level):**

```python
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
```

Inside `register(app)`:

```python
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
```

- [ ] **Step 4: Run to verify pass** — PASS (3).

- [ ] **Step 5: Commit:**

```bash
git add src/youtube_studio_mcp/tools/edits.py tests/test_edits_schedule.py
git commit -m "feat(youtube-mcp): video_schedule (gated) + cancel (ungated)"
```

---

## Task 8: `video_set_localizations` (edits.py)

**Files:** Modify `edits.py`; Test `tests/test_edits_localizations.py`.

**Interfaces:** Produces `_video_set_localizations(svc, video_id, localizations, default_language) -> dict`, wrapper `video_set_localizations`. `localizations = {lang: {"title": str, "description": str}}`.

- [ ] **Step 1: Write failing test `tests/test_edits_localizations.py`:**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import edits


def _svc():
    svc = MagicMock()
    svc.videos.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "vidL",
                   "snippet": {"title": "T", "categoryId": "22", "defaultLanguage": "en"},
                   "localizations": {"es": {"title": "viejo", "description": "d"}}}]}
    svc.videos.return_value.update.return_value.execute.return_value = {"id": "vidL"}
    return svc


def test_requires_default_language():
    svc = MagicMock()
    svc.videos.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "vidL", "snippet": {"title": "T", "categoryId": "22"}}]}
    r = edits._video_set_localizations(svc, "vidL",
        {"fr": {"title": "x", "description": "y"}}, default_language=None)
    assert r["error"] == "default_language_required"


def test_merge_and_set_default_language(isolated_config):
    svc = _svc()
    r = edits._video_set_localizations(svc, "vidL",
        {"fr": {"title": "Bonjour", "description": "desc"}}, default_language="en")
    body = svc.videos.return_value.update.call_args.kwargs["body"]
    assert body["snippet"]["defaultLanguage"] == "en"
    assert body["localizations"]["fr"]["title"] == "Bonjour"
    assert body["localizations"]["es"]["title"] == "viejo"  # preserved
    assert r["localized"] == "vidL"
```

- [ ] **Step 2: Run to verify fail** — FAIL.

- [ ] **Step 3: Add to `edits.py` (module-level):**

```python
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
```

Inside `register(app)`:

```python
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
```

- [ ] **Step 4: Run to verify pass** — PASS (2).

- [ ] **Step 5: Commit:**

```bash
git add src/youtube_studio_mcp/tools/edits.py tests/test_edits_localizations.py
git commit -m "feat(youtube-mcp): video_set_localizations"
```

---

## Task 9: `video_upload` (uploads.py — resumable)

**Files:** Create `src/youtube_studio_mcp/tools/uploads.py`; Test `tests/test_uploads.py`.

**Interfaces:** Produces `_video_upload(svc, *, path, title, description, tags, category_id, privacy, publish_at, made_for_kids, contains_synthetic_media, confirm, media_factory) -> dict`, wrapper `video_upload`. `media_factory(path, mime)` is injected for testability. Also produces module constants `MAX_VIDEO_BYTES`, `VIDEO_MIMES`, `ALLOWED_PRIVACY`, and `_default_media_factory`.

- [ ] **Step 1: Write failing test `tests/test_uploads.py`:**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import uploads


def _mf(path, mime):
    return MagicMock(name="media")


def test_missing_file(tmp_path):
    r = uploads._video_upload(MagicMock(), path=str(tmp_path / "nope.mp4"),
        title="T", description="", tags=None, category_id="22",
        privacy="private", publish_at=None, made_for_kids=False,
        contains_synthetic_media=None, confirm=False, media_factory=_mf)
    assert r["error"] == "file_not_found"


def test_public_upload_gated(tmp_path):
    f = tmp_path / "c.mp4"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    r = uploads._video_upload(svc, path=str(f), title="T", description="",
        tags=None, category_id="22", privacy="public", publish_at=None,
        made_for_kids=False, contains_synthetic_media=None, confirm=False,
        media_factory=_mf)
    assert r["error"] == "confirm_required"
    svc.videos.return_value.insert.assert_not_called()


def test_private_upload_runs(tmp_path, isolated_config, monkeypatch):
    f = tmp_path / "c.mp4"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    monkeypatch.setattr(uploads.uploadmedia, "execute_resumable",
                        lambda req: {"id": "newVid"})
    r = uploads._video_upload(svc, path=str(f), title="My Title",
        description="desc", tags=["a", "b"], category_id="28", privacy="private",
        publish_at=None, made_for_kids=False, contains_synthetic_media=True,
        confirm=False, media_factory=_mf)
    assert r["uploaded"] == "newVid"
    body = svc.videos.return_value.insert.call_args.kwargs["body"]
    assert body["snippet"]["title"] == "My Title"
    assert body["snippet"]["tags"] == ["a", "b"]
    assert body["status"]["privacyStatus"] == "private"
    assert body["status"]["containsSyntheticMedia"] is True


def test_scheduled_upload_gated_then_runs(tmp_path, isolated_config, monkeypatch):
    f = tmp_path / "c.mp4"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    monkeypatch.setattr(uploads.uploadmedia, "execute_resumable",
                        lambda req: {"id": "schVid"})
    base = dict(path=str(f), title="T", description="", tags=None,
        category_id="22", privacy="private", publish_at="2026-07-01T12:00:00Z",
        made_for_kids=False, contains_synthetic_media=None, media_factory=_mf)
    assert uploads._video_upload(svc, confirm=False, **base)["error"] == "confirm_required"
    r = uploads._video_upload(svc, confirm=True, **base)
    body = svc.videos.return_value.insert.call_args.kwargs["body"]
    assert body["status"]["publishAt"] == "2026-07-01T12:00:00Z"
    assert body["status"]["privacyStatus"] == "private"
    assert r["uploaded"] == "schVid"
```

- [ ] **Step 2: Run to verify fail** — FAIL.

- [ ] **Step 3: Write `src/youtube_studio_mcp/tools/uploads.py`:**

```python
"""Upload tools (resumable): video_upload (videos.insert). Banner and watermark
uploads are added to this module in Part E.

videos.insert costs 1 unit from a separate 100/day Uploads bucket. A Short is
just a vertical video <=3 min uploaded through this same path.
Sources: https://developers.google.com/youtube/v3/docs/videos/insert
https://developers.google.com/youtube/v3/determine_quota_cost
"""

from __future__ import annotations

from typing import Any, Callable

from googleapiclient.http import MediaFileUpload
from mcp.server.fastmcp import FastMCP

from .. import clients, gate, quota, uploadmedia

MAX_VIDEO_BYTES = 256 * 1024 * 1024 * 1024  # 256 GB
VIDEO_MIMES = {"video/*"}
ALLOWED_PRIVACY = {"private", "unlisted", "public"}


def _default_media_factory(path: str, mime: str) -> Any:
    return MediaFileUpload(path, mimetype=mime, resumable=True)


def _video_upload(svc: Any, *, path: str, title: str, description: str,
                  tags: list[str] | None, category_id: str, privacy: str,
                  publish_at: str | None, made_for_kids: bool,
                  contains_synthetic_media: bool | None, confirm: bool,
                  media_factory: Callable[[str, str], Any]) -> dict:
    """videos.insert via resumable upload. Gated only when public-facing."""
    if privacy not in ALLOWED_PRIVACY:
        return {"error": f"privacy must be one of {sorted(ALLOWED_PRIVACY)}"}
    pre = uploadmedia.validate(path, max_bytes=MAX_VIDEO_BYTES,
                               allowed_mimes=VIDEO_MIMES)
    if not pre["ok"]:
        return pre
    if privacy == "public" or publish_at is not None:
        effect = (f"This uploads and SCHEDULES the video to go public at "
                  f"{publish_at}." if publish_at
                  else "This uploads the video as PUBLIC immediately.")
        refusal = gate.require(confirm, effect=effect, title=title,
                               privacy=privacy, publish_at=publish_at)
        if refusal:
            return refusal
    status: dict[str, Any] = {
        "privacyStatus": "private" if publish_at else privacy,
        "selfDeclaredMadeForKids": made_for_kids}
    if publish_at:
        status["publishAt"] = publish_at
    if contains_synthetic_media is not None:
        status["containsSyntheticMedia"] = contains_synthetic_media
    snippet: dict[str, Any] = {"title": title, "categoryId": category_id}
    if description:
        snippet["description"] = description
    if tags:
        snippet["tags"] = tags
    media = media_factory(pre["path"], pre["mime"])
    request = svc.videos().insert(part="snippet,status",
                                  body={"snippet": snippet, "status": status},
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

        Gated ONLY when public-facing: privacy="public" or a publish_at is set.
        Private uploads run ungated. When publish_at is set, privacy is forced to
        private (API requirement) and the video auto-publishes at that time.

        Args: path (mp4/mov/m4v/webm, <=256GB), title (<=100), description
        (<=5000 bytes), tags (<=500 chars total), category_id (e.g. "22"/"28"),
        privacy (private|unlisted|public), publish_at (ISO-8601 to schedule),
        made_for_kids (COPPA flag), contains_synthetic_media (AI disclosure),
        confirm (required for public/scheduled)."""
        return _video_upload(
            clients.youtube_data(), path=path, title=title,
            description=description, tags=tags, category_id=category_id,
            privacy=privacy, publish_at=publish_at, made_for_kids=made_for_kids,
            contains_synthetic_media=contains_synthetic_media, confirm=confirm,
            media_factory=_default_media_factory)
```

- [ ] **Step 4: Run to verify pass** — PASS (4).

- [ ] **Step 5: Commit:**

```bash
git add src/youtube_studio_mcp/tools/uploads.py tests/test_uploads.py
git commit -m "feat(youtube-mcp): video_upload (resumable, gated when public/scheduled)"
```

---

## Task 10: Refactor `video_update_metadata` onto `mutate.py`

**Files:** Modify `edits.py` (existing `video_update_metadata`); Test `tests/test_edits_update_refactor.py`.

**Interfaces:** Produces module-level `_video_update_metadata(svc, video_id, title=None, description=None, tags=None, category_id=None, default_language=None, default_audio_language=None, privacy_status=None, confirm_publish=False) -> dict`; the existing tool delegates to it. External behavior unchanged (still gates private→public).

- [ ] **Step 1: Write failing test `tests/test_edits_update_refactor.py`:**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import edits


def _svc():
    svc = MagicMock()
    svc.videos.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "vidU",
                   "snippet": {"title": "Old", "categoryId": "22",
                               "description": "keep", "tags": ["t1"]},
                   "status": {"privacyStatus": "private"}}]}
    svc.videos.return_value.update.return_value.execute.return_value = {"id": "vidU"}
    return svc


def test_update_title_preserves_other_fields(isolated_config):
    svc = _svc()
    out = edits._video_update_metadata(svc, video_id="vidU", title="New")
    body = svc.videos.return_value.update.call_args.kwargs["body"]
    assert body["snippet"]["title"] == "New"
    assert body["snippet"]["description"] == "keep"
    assert body["snippet"]["tags"] == ["t1"]
    assert out["updated"] == "vidU"


def test_private_to_public_still_gated(isolated_config):
    svc = _svc()
    out = edits._video_update_metadata(svc, video_id="vidU",
        privacy_status="public", confirm_publish=False)
    assert out["error"] == "confirm_publish_required"
    svc.videos.return_value.update.assert_not_called()
```

- [ ] **Step 2: Run to verify fail** — FAIL (`_video_update_metadata` not module-level).

- [ ] **Step 3: Extract `_video_update_metadata` in `edits.py`.** Move the existing tool body to a module-level function with signature `_video_update_metadata(svc, video_id, title=None, description=None, tags=None, category_id=None, default_language=None, default_audio_language=None, privacy_status=None, confirm_publish=False)`. Replace its manual list+rebuild with:

```python
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
```

Make the existing `@app.tool()` `video_update_metadata` wrapper delegate:

```python
        return _video_update_metadata(
            clients.youtube_data(), video_id=video_id, title=title,
            description=description, tags=tags, category_id=category_id,
            default_language=default_language,
            default_audio_language=default_audio_language,
            privacy_status=privacy_status, confirm_publish=confirm_publish)
```

(The guard's `videos.list` plus the one inside `fetch_merge_update` means a
public-transition update lists twice — acceptable at 1 unit each.)

- [ ] **Step 4: Run to verify pass** — PASS (2).

- [ ] **Step 5: Commit:**

```bash
git add src/youtube_studio_mcp/tools/edits.py tests/test_edits_update_refactor.py
git commit -m "refactor(youtube-mcp): video_update_metadata onto mutate helper"
```

---

# PART C — Captions

## Task 11: Caption reads — `caption_list`, `caption_download` (captions.py)

**Files:** Create `src/youtube_studio_mcp/tools/captions.py`; Test `tests/test_captions_reads.py`.

**Interfaces:** Produces `_caption_list(svc, video_id) -> dict`, `_caption_download(svc, caption_id, tfmt, tlang) -> dict`, wrappers `caption_list`, `caption_download`, and `register`. `CAPTION_TFMTS = {"sbv","scc","srt","ttml","vtt"}`.

- [ ] **Step 1: Write failing test `tests/test_captions_reads.py`:**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import captions


def test_caption_list(isolated_config):
    svc = MagicMock()
    svc.captions.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "capA", "snippet": {"language": "en", "name": "English"}}]}
    r = captions._caption_list(svc, "vid1")
    assert r["items"][0]["id"] == "capA"
    svc.captions.return_value.list.assert_called_once()


def test_caption_download_rejects_bad_tfmt():
    svc = MagicMock()
    r = captions._caption_download(svc, "capA", tfmt="docx", tlang=None)
    assert r["error"].startswith("tfmt must be")


def test_caption_download_runs(isolated_config):
    svc = MagicMock()
    svc.captions.return_value.download.return_value.execute.return_value = b"1\n00:00\nhi"
    r = captions._caption_download(svc, "capA", tfmt="srt", tlang=None)
    assert r["caption_id"] == "capA" and r["tfmt"] == "srt"
    assert "content" in r
```

- [ ] **Step 2: Run to verify fail** — FAIL.

- [ ] **Step 3: Write `src/youtube_studio_mcp/tools/captions.py` (reads + register skeleton):**

```python
"""Caption tracks: list/download (reads) + insert/update/delete (writes, Part C).

insert=400, update=450 units — quota-guarded. update/delete/download need the
caption id from caption_list. SRT uploads as application/octet-stream.
Sources: https://developers.google.com/youtube/v3/docs/captions
https://developers.google.com/youtube/v3/determine_quota_cost
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .. import clients, gate, quota, uploadmedia

CAPTION_TFMTS = {"sbv", "scc", "srt", "ttml", "vtt"}
CAPTION_MIMES = {"application/octet-stream", "text/vtt", "text/xml"}
MAX_CAPTION_BYTES = 100 * 1024 * 1024  # 100 MB


def _caption_list(svc: Any, video_id: str) -> dict:
    resp = clients.run(
        lambda y: y.captions().list(part="snippet", videoId=video_id), svc)
    quota.record("captions.list")
    return {"video_id": video_id, "items": resp.get("items") or []}


def _caption_download(svc: Any, caption_id: str, tfmt: str,
                      tlang: str | None) -> dict:
    if tfmt not in CAPTION_TFMTS:
        return {"error": f"tfmt must be one of {sorted(CAPTION_TFMTS)}"}
    kwargs: dict[str, Any] = {"id": caption_id, "tfmt": tfmt}
    if tlang:
        kwargs["tlang"] = tlang
    raw = clients.run(lambda y: y.captions().download(**kwargs), svc)
    quota.record("captions.download")
    content = raw.decode("utf-8", errors="replace") if isinstance(raw, (bytes, bytearray)) else str(raw)
    return {"caption_id": caption_id, "tfmt": tfmt, "tlang": tlang,
            "content": content}


def register(app: FastMCP) -> None:
    @app.tool()
    @clients.http_safe
    def caption_list(video_id: str) -> dict:
        """List caption tracks for a video (ids needed by update/delete/download).
        Quota: 50 units. Ungated."""
        return _caption_list(clients.youtube_data(), video_id)

    @app.tool()
    @clients.http_safe
    def caption_download(caption_id: str, tfmt: str = "srt",
                         tlang: str | None = None) -> dict:
        """Download a caption track. Quota: 200 units. Ungated. tfmt is one of
        sbv/scc/srt/ttml/vtt; tlang requests a machine translation (ISO 639-1)."""
        return _caption_download(clients.youtube_data(), caption_id, tfmt, tlang)
```

- [ ] **Step 4: Run to verify pass** — PASS (3).

- [ ] **Step 5: Commit:**

```bash
git add src/youtube_studio_mcp/tools/captions.py tests/test_captions_reads.py
git commit -m "feat(youtube-mcp): caption_list + caption_download (reads)"
```

---

## Task 12: Caption writes — `caption_insert`, `caption_update`, `caption_delete` (captions.py)

**Files:** Modify `captions.py`; Test `tests/test_captions_writes.py`.

**Interfaces:** Produces `_caption_insert(svc, *, video_id, file_path, language, name, is_draft, confirm, media_factory) -> dict` (quota-guarded, 400), `_caption_update(svc, *, caption_id, file_path, is_draft, confirm, media_factory) -> dict` (quota-guarded, 450), `_caption_delete(svc, caption_id, confirm) -> dict` (gated). `media_factory(path, mime)` injected. Wrappers added in `register`.

- [ ] **Step 1: Write failing test `tests/test_captions_writes.py`:**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import captions


def _mf(path, mime):
    return MagicMock(name="media")


def test_insert_quota_gated(tmp_path):
    f = tmp_path / "en.srt"; f.write_text("1\n00:00,000 --> 00:01,000\nhi\n")
    svc = MagicMock()
    r = captions._caption_insert(svc, video_id="v1", file_path=str(f),
        language="en", name="English", is_draft=False, confirm=False,
        media_factory=_mf)
    assert r["error"] == "confirm_required"
    assert r["estimated_cost_units"] == 400
    svc.captions.return_value.insert.assert_not_called()


def test_insert_runs(tmp_path, isolated_config):
    f = tmp_path / "en.srt"; f.write_text("1\n00:00,000 --> 00:01,000\nhi\n")
    svc = MagicMock()
    svc.captions.return_value.insert.return_value.execute.return_value = {"id": "capN"}
    r = captions._caption_insert(svc, video_id="v1", file_path=str(f),
        language="en", name="English", is_draft=False, confirm=True,
        media_factory=_mf)
    assert r["caption_inserted"] == "capN"
    body = svc.captions.return_value.insert.call_args.kwargs["body"]
    assert body["snippet"]["videoId"] == "v1"
    assert body["snippet"]["language"] == "en"


def test_insert_missing_file(tmp_path):
    svc = MagicMock()
    r = captions._caption_insert(svc, video_id="v1",
        file_path=str(tmp_path / "no.srt"), language="en", name="E",
        is_draft=False, confirm=True, media_factory=_mf)
    assert r["error"] == "file_not_found"


def test_delete_gated():
    svc = MagicMock()
    assert captions._caption_delete(svc, "capA", confirm=False)["error"] == "confirm_required"
    svc.captions.return_value.delete.assert_not_called()


def test_delete_runs(isolated_config):
    svc = MagicMock()
    svc.captions.return_value.delete.return_value.execute.return_value = ""
    assert captions._caption_delete(svc, "capA", confirm=True)["caption_deleted"] == "capA"
```

- [ ] **Step 2: Run to verify fail** — FAIL.

- [ ] **Step 3: Add to `captions.py` (module-level):**

```python
def _caption_insert(svc: Any, *, video_id: str, file_path: str, language: str,
                    name: str, is_draft: bool, confirm: bool,
                    media_factory) -> dict:
    """captions.insert — 400 units, quota-guarded. Media body = caption file."""
    refusal = gate.quota_guard("captions.insert", 1, confirm)
    if refusal:
        return refusal
    pre = uploadmedia.validate(file_path, max_bytes=MAX_CAPTION_BYTES,
                               allowed_mimes=CAPTION_MIMES)
    if not pre["ok"]:
        return pre
    media = media_factory(pre["path"], pre["mime"])
    body = {"snippet": {"videoId": video_id, "language": language,
                        "name": name, "isDraft": is_draft}}
    resp = clients.run(
        lambda y: y.captions().insert(part="snippet", body=body, media_body=media),
        svc)
    quota.record("captions.insert")
    return {"caption_inserted": resp.get("id"), "response": resp}


def _caption_update(svc: Any, *, caption_id: str, file_path: str | None,
                    is_draft: bool | None, confirm: bool, media_factory) -> dict:
    """captions.update — 450 units, quota-guarded. Replace file and/or draft."""
    refusal = gate.quota_guard("captions.update", 1, confirm)
    if refusal:
        return refusal
    body: dict[str, Any] = {"id": caption_id}
    if is_draft is not None:
        body["snippet"] = {"isDraft": is_draft}
    media = None
    if file_path is not None:
        pre = uploadmedia.validate(file_path, max_bytes=MAX_CAPTION_BYTES,
                                   allowed_mimes=CAPTION_MIMES)
        if not pre["ok"]:
            return pre
        media = media_factory(pre["path"], pre["mime"])
    part = "snippet" if "snippet" in body else "id"
    resp = clients.run(
        lambda y: y.captions().update(part=part, body=body, media_body=media),
        svc)
    quota.record("captions.update")
    return {"caption_updated": caption_id, "response": resp}


def _caption_delete(svc: Any, caption_id: str, confirm: bool) -> dict:
    """captions.delete — gated, irreversible."""
    refusal = gate.require(
        confirm, effect=f"This permanently deletes caption track {caption_id}.",
        caption_id=caption_id)
    if refusal:
        return refusal
    clients.run(lambda y: y.captions().delete(id=caption_id), svc)
    quota.record("captions.delete")
    return {"caption_deleted": caption_id, "quota_units_spent": 50}
```

Add wrappers inside `register(app)`:

```python
    @app.tool()
    @clients.http_safe
    def caption_insert(video_id: str, file_path: str, language: str,
                       name: str = "", is_draft: bool = False,
                       confirm: bool = False) -> dict:
        """Upload a caption track (e.g. your SRT) for a video. Quota: 400 units —
        gated on cost. language is BCP-47 (e.g. "en"); name is the viewer-facing
        label. Accepts .srt/.sbv/.vtt/.xml."""
        from googleapiclient.http import MediaFileUpload
        return _caption_insert(
            clients.youtube_data(), video_id=video_id, file_path=file_path,
            language=language, name=name or language, is_draft=is_draft,
            confirm=confirm,
            media_factory=lambda p, m: MediaFileUpload(p, mimetype=m, resumable=True))

    @app.tool()
    @clients.http_safe
    def caption_update(caption_id: str, file_path: str | None = None,
                       is_draft: bool | None = None, confirm: bool = False) -> dict:
        """Replace a caption track's file and/or draft status. Quota: 450 units —
        gated on cost. Get caption_id from caption_list."""
        from googleapiclient.http import MediaFileUpload
        return _caption_update(
            clients.youtube_data(), caption_id=caption_id, file_path=file_path,
            is_draft=is_draft, confirm=confirm,
            media_factory=lambda p, m: MediaFileUpload(p, mimetype=m, resumable=True))

    @app.tool()
    @clients.http_safe
    def caption_delete(caption_id: str, confirm: bool = False) -> dict:
        """Delete a caption track. Quota: 50 units. Gated: irreversible."""
        return _caption_delete(clients.youtube_data(), caption_id, confirm)
```

- [ ] **Step 4: Run to verify pass** — PASS (5).

- [ ] **Step 5: Commit:**

```bash
git add src/youtube_studio_mcp/tools/captions.py tests/test_captions_writes.py
git commit -m "feat(youtube-mcp): caption insert/update/delete (gated)"
```

---

# PART D — Playlists

## Task 13: Playlists CRUD (playlists.py)

**Files:** Create `src/youtube_studio_mcp/tools/playlists.py`; Test `tests/test_playlists.py`.

**Interfaces:** Produces `_playlist_create(svc, *, title, description, privacy)`, `_playlist_update(svc, *, playlist_id, title, description, privacy)`, `_playlist_delete(svc, playlist_id, confirm)`, wrappers + `register`.

- [ ] **Step 1: Write failing test `tests/test_playlists.py`:**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import playlists


def test_create(isolated_config):
    svc = MagicMock()
    svc.playlists.return_value.insert.return_value.execute.return_value = {"id": "PL1"}
    r = playlists._playlist_create(svc, title="Series", description="d", privacy="public")
    assert r["playlist_created"] == "PL1"
    body = svc.playlists.return_value.insert.call_args.kwargs["body"]
    assert body["snippet"]["title"] == "Series"
    assert body["status"]["privacyStatus"] == "public"


def test_update_merges(isolated_config):
    svc = MagicMock()
    svc.playlists.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "PL1", "snippet": {"title": "Old", "description": "keep"},
                   "status": {"privacyStatus": "private"}}]}
    svc.playlists.return_value.update.return_value.execute.return_value = {"id": "PL1"}
    r = playlists._playlist_update(svc, playlist_id="PL1", title="New",
                                   description=None, privacy=None)
    body = svc.playlists.return_value.update.call_args.kwargs["body"]
    assert body["snippet"]["title"] == "New"
    assert body["snippet"]["description"] == "keep"
    assert r["playlist_updated"] == "PL1"


def test_delete_gated():
    svc = MagicMock()
    assert playlists._playlist_delete(svc, "PL1", confirm=False)["error"] == "confirm_required"


def test_delete_runs(isolated_config):
    svc = MagicMock()
    svc.playlists.return_value.delete.return_value.execute.return_value = ""
    assert playlists._playlist_delete(svc, "PL1", confirm=True)["playlist_deleted"] == "PL1"
```

- [ ] **Step 2: Run to verify fail** — FAIL.

- [ ] **Step 3: Write `src/youtube_studio_mcp/tools/playlists.py`:**

```python
"""Playlists + playlist items + playlist images.

All writes cost 50 units. playlistItems.insert needs both playlistId and
resourceId. PUT updates merge (re-send title). playlist delete + item remove +
image delete are gated.
Sources: https://developers.google.com/youtube/v3/docs/playlists
https://developers.google.com/youtube/v3/docs/playlistItems
https://developers.google.com/youtube/v3/docs/playlistImages
"""

from __future__ import annotations

from typing import Any

from googleapiclient.http import MediaFileUpload
from mcp.server.fastmcp import FastMCP

from .. import clients, gate, mutate, quota, uploadmedia

IMAGE_MIMES = {"image/jpeg", "image/png"}
MAX_PLAYLIST_IMAGE_BYTES = 2 * 1024 * 1024  # 2 MB, 1:1


def _playlist_create(svc: Any, *, title: str, description: str,
                     privacy: str) -> dict:
    body = {"snippet": {"title": title, "description": description},
            "status": {"privacyStatus": privacy}}
    resp = clients.run(
        lambda y: y.playlists().insert(part="snippet,status", body=body), svc)
    quota.record("playlists.insert")
    return {"playlist_created": resp.get("id"), "response": resp}


def _playlist_update(svc: Any, *, playlist_id: str, title: str | None,
                     description: str | None, privacy: str | None) -> dict:
    snippet: dict[str, Any] = {}
    if title is not None:
        snippet["title"] = title
    if description is not None:
        snippet["description"] = description
    patch: dict[str, Any] = {}
    if snippet:
        patch["snippet"] = snippet
    if privacy is not None:
        patch["status"] = {"privacyStatus": privacy}
    if not patch:
        return {"error": "no_changes_provided"}
    parts = ",".join(k for k in ("snippet", "status") if k in patch)
    try:
        resp = mutate.fetch_merge_update(
            svc, resource="playlists", id=playlist_id, parts=parts, patch=patch,
            record_list="playlists.list", record_update="playlists.update")
    except KeyError:
        return {"error": "playlist_not_found", "playlist_id": playlist_id}
    return {"playlist_updated": playlist_id, "response": resp}


def _playlist_delete(svc: Any, playlist_id: str, confirm: bool) -> dict:
    refusal = gate.require(
        confirm, effect=f"This permanently deletes playlist {playlist_id}.",
        playlist_id=playlist_id)
    if refusal:
        return refusal
    clients.run(lambda y: y.playlists().delete(id=playlist_id), svc)
    quota.record("playlists.delete")
    return {"playlist_deleted": playlist_id, "quota_units_spent": 50}


def register(app: FastMCP) -> None:
    @app.tool()
    @clients.http_safe
    def playlist_create(title: str, description: str = "",
                        privacy: str = "private") -> dict:
        """Create a playlist. Quota: 50 units. Ungated."""
        return _playlist_create(clients.youtube_data(), title=title,
                                description=description, privacy=privacy)

    @app.tool()
    @clients.http_safe
    def playlist_update(playlist_id: str, title: str | None = None,
                        description: str | None = None,
                        privacy: str | None = None) -> dict:
        """Edit a playlist's title/description/privacy (merge — unsent fields
        kept). Quota: ~51 units. Ungated."""
        return _playlist_update(clients.youtube_data(), playlist_id=playlist_id,
                                title=title, description=description, privacy=privacy)

    @app.tool()
    @clients.http_safe
    def playlist_delete(playlist_id: str, confirm: bool = False) -> dict:
        """Delete a playlist. Quota: 50 units. Gated: irreversible."""
        return _playlist_delete(clients.youtube_data(), playlist_id, confirm)
```

- [ ] **Step 4: Run to verify pass** — PASS (4).

- [ ] **Step 5: Commit:**

```bash
git add src/youtube_studio_mcp/tools/playlists.py tests/test_playlists.py
git commit -m "feat(youtube-mcp): playlist create/update/delete"
```

---

## Task 14: Playlist items + images (playlists.py)

**Files:** Modify `playlists.py`; Test `tests/test_playlist_items.py`.

**Interfaces:** Produces `_playlist_add_video(svc, *, playlist_id, video_id, position)`, `_playlist_item_remove(svc, item_id, confirm)`, `_playlist_set_image(svc, *, playlist_id, file_path, confirm, media_factory)`, `_playlist_delete_image(svc, image_id, confirm)`, plus wrappers.

- [ ] **Step 1: Write failing test `tests/test_playlist_items.py`:**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import playlists


def _mf(path, mime):
    return MagicMock(name="media")


def test_add_video(isolated_config):
    svc = MagicMock()
    svc.playlistItems.return_value.insert.return_value.execute.return_value = {"id": "PLI1"}
    r = playlists._playlist_add_video(svc, playlist_id="PL1", video_id="vidA", position=None)
    body = svc.playlistItems.return_value.insert.call_args.kwargs["body"]
    assert body["snippet"]["playlistId"] == "PL1"
    assert body["snippet"]["resourceId"] == {"kind": "youtube#video", "videoId": "vidA"}
    assert r["item_added"] == "PLI1"


def test_add_video_with_position(isolated_config):
    svc = MagicMock()
    svc.playlistItems.return_value.insert.return_value.execute.return_value = {"id": "PLI1"}
    playlists._playlist_add_video(svc, playlist_id="PL1", video_id="vidA", position=0)
    body = svc.playlistItems.return_value.insert.call_args.kwargs["body"]
    assert body["snippet"]["position"] == 0


def test_item_remove_gated():
    svc = MagicMock()
    assert playlists._playlist_item_remove(svc, "PLI1", confirm=False)["error"] == "confirm_required"


def test_item_remove_runs(isolated_config):
    svc = MagicMock()
    svc.playlistItems.return_value.delete.return_value.execute.return_value = ""
    assert playlists._playlist_item_remove(svc, "PLI1", confirm=True)["item_removed"] == "PLI1"


def test_set_image_runs(tmp_path, isolated_config, monkeypatch):
    f = tmp_path / "cover.png"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    monkeypatch.setattr(playlists.uploadmedia, "execute_resumable",
                        lambda req: {"id": "IMG1"})
    r = playlists._playlist_set_image(svc, playlist_id="PL1", file_path=str(f),
                                      confirm=False, media_factory=_mf)
    assert r["image_set"] == "IMG1"


def test_delete_image_gated():
    svc = MagicMock()
    assert playlists._playlist_delete_image(svc, "IMG1", confirm=False)["error"] == "confirm_required"
```

- [ ] **Step 2: Run to verify fail** — FAIL.

- [ ] **Step 3: Add to `playlists.py` (module-level):**

```python
def _playlist_add_video(svc: Any, *, playlist_id: str, video_id: str,
                        position: int | None) -> dict:
    snippet: dict[str, Any] = {
        "playlistId": playlist_id,
        "resourceId": {"kind": "youtube#video", "videoId": video_id}}
    if position is not None:
        snippet["position"] = position
    resp = clients.run(
        lambda y: y.playlistItems().insert(part="snippet",
                                           body={"snippet": snippet}), svc)
    quota.record("playlistItems.insert")
    return {"item_added": resp.get("id"), "response": resp}


def _playlist_item_remove(svc: Any, item_id: str, confirm: bool) -> dict:
    refusal = gate.require(
        confirm, effect=f"This removes playlist item {item_id}.", item_id=item_id)
    if refusal:
        return refusal
    clients.run(lambda y: y.playlistItems().delete(id=item_id), svc)
    quota.record("playlistItems.delete")
    return {"item_removed": item_id, "quota_units_spent": 50}


def _playlist_set_image(svc: Any, *, playlist_id: str, file_path: str,
                        confirm: bool, media_factory) -> dict:
    """playlistImages.insert — square 1:1 JPEG/PNG <=2 MB."""
    refusal = gate.require(
        confirm, effect=f"This sets the cover image for playlist {playlist_id}.",
        playlist_id=playlist_id)
    if refusal:
        return refusal
    pre = uploadmedia.validate(file_path, max_bytes=MAX_PLAYLIST_IMAGE_BYTES,
                               allowed_mimes=IMAGE_MIMES)
    if not pre["ok"]:
        return pre
    media = media_factory(pre["path"], pre["mime"])
    body = {"snippet": {"playlistId": playlist_id, "type": "hero"}}
    request = svc.playlistImages().insert(part="snippet", body=body,
                                          media_body=media)
    resp = uploadmedia.execute_resumable(request)
    quota.record("playlistImages.insert")
    return {"image_set": resp.get("id"), "response": resp}


def _playlist_delete_image(svc: Any, image_id: str, confirm: bool) -> dict:
    refusal = gate.require(
        confirm, effect=f"This deletes playlist image {image_id}.",
        image_id=image_id)
    if refusal:
        return refusal
    clients.run(lambda y: y.playlistImages().delete(id=image_id), svc)
    quota.record("playlistImages.delete")
    return {"image_deleted": image_id, "quota_units_spent": 50}
```

Add wrappers inside `register(app)`:

```python
    @app.tool()
    @clients.http_safe
    def playlist_add_video(playlist_id: str, video_id: str,
                           position: int | None = None) -> dict:
        """Add a video to a playlist. Quota: 50 units. Ungated. position is
        0-indexed (requires a manual-sort playlist)."""
        return _playlist_add_video(clients.youtube_data(),
                                   playlist_id=playlist_id, video_id=video_id,
                                   position=position)

    @app.tool()
    @clients.http_safe
    def playlist_item_remove(item_id: str, confirm: bool = False) -> dict:
        """Remove an item from a playlist. Quota: 50 units. Gated. item_id is the
        PLAYLIST ITEM id (from playlistItems.list), not the video id."""
        return _playlist_item_remove(clients.youtube_data(), item_id, confirm)

    @app.tool()
    @clients.http_safe
    def playlist_set_image(playlist_id: str, file_path: str,
                           confirm: bool = False) -> dict:
        """Set a playlist cover image (square 1:1 JPEG/PNG <=2 MB). Quota: 50
        units. Gated (channel-visible)."""
        return _playlist_set_image(
            clients.youtube_data(), playlist_id=playlist_id, file_path=file_path,
            confirm=confirm,
            media_factory=lambda p, m: MediaFileUpload(p, mimetype=m, resumable=True))

    @app.tool()
    @clients.http_safe
    def playlist_delete_image(image_id: str, confirm: bool = False) -> dict:
        """Delete a playlist cover image. Quota: 50 units. Gated: irreversible."""
        return _playlist_delete_image(clients.youtube_data(), image_id, confirm)
```

- [ ] **Step 4: Run to verify pass** — PASS (6).

- [ ] **Step 5: Commit:**

```bash
git add src/youtube_studio_mcp/tools/playlists.py tests/test_playlist_items.py
git commit -m "feat(youtube-mcp): playlist items + cover images"
```

---

# PART E — Channel-level

## Task 15: `channel_update_branding` + channelSections (channel_edits.py)

**Files:** Create `src/youtube_studio_mcp/tools/channel_edits.py`; Test `tests/test_channel_edits.py`.

**Interfaces:** Produces `_channel_update_branding(svc, *, channel_id, description, keywords, country, default_language, confirm)` (gated, merge `brandingSettings`), `_channel_section_create/_update/_delete`, wrappers + `register`. `channels.update` writable parts restricted to `brandingSettings`/`localizations`. Source: https://developers.google.com/youtube/v3/docs/channels/update

- [ ] **Step 1: Write failing test `tests/test_channel_edits.py`:**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import channel_edits


def _svc():
    svc = MagicMock()
    svc.channels.return_value.list.return_value.execute.return_value = {
        "items": [{"id": "UC1", "brandingSettings": {
            "channel": {"title": "Chan", "description": "old", "keywords": "a b"}}}]}
    svc.channels.return_value.update.return_value.execute.return_value = {"id": "UC1"}
    return svc


def test_branding_gated():
    svc = _svc()
    r = channel_edits._channel_update_branding(svc, channel_id="UC1",
        description="new", keywords=None, country=None, default_language=None,
        confirm=False)
    assert r["error"] == "confirm_required"
    svc.channels.return_value.update.assert_not_called()


def test_branding_merges_and_keeps_title(isolated_config):
    svc = _svc()
    r = channel_edits._channel_update_branding(svc, channel_id="UC1",
        description="new", keywords=None, country=None, default_language=None,
        confirm=True)
    body = svc.channels.return_value.update.call_args.kwargs["body"]
    assert body["brandingSettings"]["channel"]["description"] == "new"
    assert body["brandingSettings"]["channel"]["title"] == "Chan"  # preserved
    assert body["brandingSettings"]["channel"]["keywords"] == "a b"  # preserved
    assert r["branding_updated"] == "UC1"


def test_section_delete_gated():
    svc = MagicMock()
    assert channel_edits._channel_section_delete(svc, "S1", confirm=False)["error"] == "confirm_required"


def test_section_create(isolated_config):
    svc = MagicMock()
    svc.channelSections.return_value.insert.return_value.execute.return_value = {"id": "S1"}
    r = channel_edits._channel_section_create(svc, section_type="multiplePlaylists",
        title="Best", playlist_ids=["PL1"])
    assert r["section_created"] == "S1"
    body = svc.channelSections.return_value.insert.call_args.kwargs["body"]
    assert body["snippet"]["type"] == "multiplePlaylists"
```

- [ ] **Step 2: Run to verify fail** — FAIL.

- [ ] **Step 3: Write `src/youtube_studio_mcp/tools/channel_edits.py`:**

```python
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
```

- [ ] **Step 4: Run to verify pass** — PASS (5).

- [ ] **Step 5: Commit:**

```bash
git add src/youtube_studio_mcp/tools/channel_edits.py tests/test_channel_edits.py
git commit -m "feat(youtube-mcp): channel branding + sections"
```

---

## Task 16: Banner + watermark uploads (uploads.py + channel_edits.py)

**Files:** Modify `uploads.py` (add banner/watermark); Modify `channel_edits.py` (add `channel_unset_watermark`); Test `tests/test_channel_media.py`.

**Interfaces:** Produces `_channel_set_banner(svc, *, image_path, confirm, media_factory)` (two-step: channelBanners.insert → channels.update brandingSettings.image.bannerExternalUrl), `_channel_set_watermark(svc, *, image_path, timing_type, offset_ms, duration_ms, confirm, media_factory)`, and in `channel_edits.py` `_channel_unset_watermark(svc, channel_id, confirm)`. Wrappers `channel_set_banner`, `channel_set_watermark` in uploads.register; `channel_unset_watermark` in channel_edits.register.

- [ ] **Step 1: Write failing test `tests/test_channel_media.py`:**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import uploads, channel_edits


def _mf(path, mime):
    return MagicMock(name="media")


def test_set_banner_gated(tmp_path):
    f = tmp_path / "banner.png"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    r = uploads._channel_set_banner(svc, image_path=str(f), confirm=False,
                                    media_factory=_mf)
    assert r["error"] == "confirm_required"


def test_set_banner_two_step(tmp_path, isolated_config, monkeypatch):
    f = tmp_path / "banner.png"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    monkeypatch.setattr(uploads.uploadmedia, "execute_resumable",
                        lambda req: {"url": "http://banner/url"})
    svc.channels.return_value.update.return_value.execute.return_value = {"id": "UC1"}
    r = uploads._channel_set_banner(svc, image_path=str(f), confirm=True,
                                    media_factory=_mf)
    body = svc.channels.return_value.update.call_args.kwargs["body"]
    assert body["brandingSettings"]["image"]["bannerExternalUrl"] == "http://banner/url"
    assert r["banner_set"] is True


def test_set_watermark_gated(tmp_path):
    f = tmp_path / "wm.png"; f.write_bytes(b"\x00" * 4)
    svc = MagicMock()
    r = uploads._channel_set_watermark(svc, image_path=str(f),
        timing_type="offsetFromEnd", offset_ms=0, duration_ms=15000,
        confirm=False, media_factory=_mf)
    assert r["error"] == "confirm_required"


def test_unset_watermark_gated():
    svc = MagicMock()
    assert channel_edits._channel_unset_watermark(svc, "UC1", confirm=False)["error"] == "confirm_required"


def test_unset_watermark_runs(isolated_config):
    svc = MagicMock()
    svc.watermarks.return_value.unset.return_value.execute.return_value = ""
    assert channel_edits._channel_unset_watermark(svc, "UC1", confirm=True)["watermark_unset"] == "UC1"
```

- [ ] **Step 2: Run to verify fail** — FAIL.

- [ ] **Step 3a: Add to `uploads.py`** — the existing import (`from .. import clients, gate, quota, uploadmedia`) is sufficient; do not add `mutate` (banner/watermark use `clients.run` directly, not the merge helper). Add module-level constants + functions:

```python
MAX_BANNER_BYTES = 6 * 1024 * 1024  # 6 MB, 16:9, >=2048x1152
MAX_WATERMARK_BYTES = 10 * 1024 * 1024  # 10 MB
WATERMARK_TIMINGS = {"offsetFromStart", "offsetFromEnd"}


def _channel_set_banner(svc: Any, *, image_path: str, confirm: bool,
                        media_factory: Callable[[str, str], Any]) -> dict:
    """Two-step: channelBanners.insert (upload) -> channels.update
    brandingSettings.image.bannerExternalUrl."""
    refusal = gate.require(
        confirm, effect="This replaces your channel banner (visible channel-wide).")
    if refusal:
        return refusal
    pre = uploadmedia.validate(image_path, max_bytes=MAX_BANNER_BYTES,
                               allowed_mimes={"image/jpeg", "image/png"})
    if not pre["ok"]:
        return pre
    media = media_factory(pre["path"], pre["mime"])
    request = svc.channelBanners().insert(media_body=media)
    banner = uploadmedia.execute_resumable(request)
    quota.record("channelBanners.insert")
    url = banner.get("url")
    if not url:
        return {"error": "banner_upload_failed", "response": banner}
    current = clients.run(lambda y: y.channels().list(part="id", mine=True), svc)
    quota.record("channels.list")
    channel_id = (current.get("items") or [{}])[0].get("id")
    body = {"id": channel_id,
            "brandingSettings": {"image": {"bannerExternalUrl": url}}}
    resp = clients.run(
        lambda y: y.channels().update(part="brandingSettings", body=body), svc)
    quota.record("channels.update")
    return {"banner_set": True, "channel_id": channel_id, "banner_url": url,
            "response": resp}


def _channel_set_watermark(svc: Any, *, image_path: str, timing_type: str,
                           offset_ms: int, duration_ms: int, confirm: bool,
                           media_factory: Callable[[str, str], Any]) -> dict:
    """watermarks.set — branding watermark overlay (topRight). Gated."""
    if timing_type not in WATERMARK_TIMINGS:
        return {"error": f"timing_type must be one of {sorted(WATERMARK_TIMINGS)}"}
    refusal = gate.require(
        confirm, effect="This sets a channel watermark on all your videos.")
    if refusal:
        return refusal
    pre = uploadmedia.validate(image_path, max_bytes=MAX_WATERMARK_BYTES,
                               allowed_mimes={"image/jpeg", "image/png"})
    if not pre["ok"]:
        return pre
    media = media_factory(pre["path"], pre["mime"])
    current = clients.run(lambda y: y.channels().list(part="id", mine=True), svc)
    quota.record("channels.list")
    channel_id = (current.get("items") or [{}])[0].get("id")
    body = {"timing": {"type": timing_type, "offsetMs": offset_ms,
                       "durationMs": duration_ms},
            "position": {"type": "corner", "cornerPosition": "topRight"}}
    request = svc.watermarks().set(channelId=channel_id, body=body,
                                   media_body=media)
    uploadmedia.execute_resumable(request)
    quota.record("watermarks.set")
    return {"watermark_set": channel_id}
```

- [ ] **Step 3b: Add wrappers in `uploads.py` `register(app)`:**

```python
    @app.tool()
    @clients.http_safe
    def channel_set_banner(image_path: str, confirm: bool = False) -> dict:
        """Set the channel banner (JPEG/PNG, 16:9, >=2048x1152, <=6 MB). Quota:
        ~101 units (upload + channels.update). Gated (channel-wide)."""
        return _channel_set_banner(
            clients.youtube_data(), image_path=image_path, confirm=confirm,
            media_factory=_default_media_factory)

    @app.tool()
    @clients.http_safe
    def channel_set_watermark(image_path: str, timing_type: str = "offsetFromEnd",
                              offset_ms: int = 0, duration_ms: int = 15000,
                              confirm: bool = False) -> dict:
        """Set the channel branding watermark (JPEG/PNG <=10 MB, shown topRight).
        Quota: ~51 units. Gated. timing_type is offsetFromStart or offsetFromEnd."""
        return _channel_set_watermark(
            clients.youtube_data(), image_path=image_path, timing_type=timing_type,
            offset_ms=offset_ms, duration_ms=duration_ms, confirm=confirm,
            media_factory=_default_media_factory)
```

- [ ] **Step 3c: Add to `channel_edits.py` (module-level + wrapper):**

```python
def _channel_unset_watermark(svc: Any, channel_id: str, confirm: bool) -> dict:
    refusal = gate.require(
        confirm, effect=f"This removes the watermark from channel {channel_id}.",
        channel_id=channel_id)
    if refusal:
        return refusal
    clients.run(lambda y: y.watermarks().unset(channelId=channel_id), svc)
    quota.record("watermarks.unset")
    return {"watermark_unset": channel_id, "quota_units_spent": 50}
```

In `channel_edits.py` `register(app)`:

```python
    @app.tool()
    @clients.http_safe
    def channel_unset_watermark(channel_id: str, confirm: bool = False) -> dict:
        """Remove the channel branding watermark. Quota: 50 units. Gated."""
        return _channel_unset_watermark(clients.youtube_data(), channel_id, confirm)
```

- [ ] **Step 4: Run to verify pass** — Run: `uv run pytest tests/test_channel_media.py -v` → PASS (5).

- [ ] **Step 5: Commit:**

```bash
git add src/youtube_studio_mcp/tools/uploads.py src/youtube_studio_mcp/tools/channel_edits.py tests/test_channel_media.py
git commit -m "feat(youtube-mcp): channel banner + watermark set/unset"
```

---

# PART F — Subscriptions

## Task 17: `subscription_add` / `subscription_remove` (subscriptions.py)

**Files:** Create `src/youtube_studio_mcp/tools/subscriptions.py`; Test `tests/test_subscriptions.py`.

**Interfaces:** Produces `_subscription_add(svc, channel_id, confirm)`, `_subscription_remove(svc, subscription_id, confirm)`, wrappers + `register`. Both gated (social).

- [ ] **Step 1: Write failing test `tests/test_subscriptions.py`:**

```python
from unittest.mock import MagicMock

from youtube_studio_mcp.tools import subscriptions


def test_add_gated():
    svc = MagicMock()
    assert subscriptions._subscription_add(svc, "UCabc", confirm=False)["error"] == "confirm_required"
    svc.subscriptions.return_value.insert.assert_not_called()


def test_add_runs(isolated_config):
    svc = MagicMock()
    svc.subscriptions.return_value.insert.return_value.execute.return_value = {"id": "SUB1"}
    r = subscriptions._subscription_add(svc, "UCabc", confirm=True)
    body = svc.subscriptions.return_value.insert.call_args.kwargs["body"]
    assert body["snippet"]["resourceId"] == {"kind": "youtube#channel", "channelId": "UCabc"}
    assert r["subscribed"] == "SUB1"


def test_remove_gated():
    svc = MagicMock()
    assert subscriptions._subscription_remove(svc, "SUB1", confirm=False)["error"] == "confirm_required"


def test_remove_runs(isolated_config):
    svc = MagicMock()
    svc.subscriptions.return_value.delete.return_value.execute.return_value = ""
    assert subscriptions._subscription_remove(svc, "SUB1", confirm=True)["unsubscribed"] == "SUB1"
```

- [ ] **Step 2: Run to verify fail** — FAIL.

- [ ] **Step 3: Write `src/youtube_studio_mcp/tools/subscriptions.py`:**

```python
"""Subscriptions — subscribe/unsubscribe AS the authenticated channel. Both
gated (a public social action). 50 units each.
Sources: https://developers.google.com/youtube/v3/docs/subscriptions/insert
https://developers.google.com/youtube/v3/docs/subscriptions/delete
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .. import clients, gate, quota


def _subscription_add(svc: Any, channel_id: str, confirm: bool) -> dict:
    refusal = gate.require(
        confirm, effect=f"This subscribes your channel to {channel_id} (public).",
        channel_id=channel_id)
    if refusal:
        return refusal
    body = {"snippet": {"resourceId": {"kind": "youtube#channel",
                                       "channelId": channel_id}}}
    resp = clients.run(
        lambda y: y.subscriptions().insert(part="snippet", body=body), svc)
    quota.record("subscriptions.insert")
    return {"subscribed": resp.get("id"), "channel_id": channel_id,
            "response": resp}


def _subscription_remove(svc: Any, subscription_id: str, confirm: bool) -> dict:
    refusal = gate.require(
        confirm, effect=f"This unsubscribes (subscription {subscription_id}).",
        subscription_id=subscription_id)
    if refusal:
        return refusal
    clients.run(lambda y: y.subscriptions().delete(id=subscription_id), svc)
    quota.record("subscriptions.delete")
    return {"unsubscribed": subscription_id, "quota_units_spent": 50}


def register(app: FastMCP) -> None:
    @app.tool()
    @clients.http_safe
    def subscription_add(channel_id: str, confirm: bool = False) -> dict:
        """Subscribe your channel to another channel. Quota: 50 units. Gated
        (public social action). channel_id is the target channel id."""
        return _subscription_add(clients.youtube_data(), channel_id, confirm)

    @app.tool()
    @clients.http_safe
    def subscription_remove(subscription_id: str, confirm: bool = False) -> dict:
        """Unsubscribe. Quota: 50 units. Gated. subscription_id is the
        SUBSCRIPTION id (from subscriptions.list), not the channel id."""
        return _subscription_remove(clients.youtube_data(), subscription_id, confirm)
```

- [ ] **Step 4: Run to verify pass** — PASS (4).

- [ ] **Step 5: Commit:**

```bash
git add src/youtube_studio_mcp/tools/subscriptions.py tests/test_subscriptions.py
git commit -m "feat(youtube-mcp): subscription add/remove (gated)"
```

---

# PART G — Wiring & Docs

## Task 18: Register all modules + add upload scope + v2 docs

**Files:** Modify `auth.py`, `server.py`, `tools/youtube-studio-mcp/CLAUDE.md`; Test `tests/test_wiring.py`.

**Interfaces:** Produces `youtube.upload` in `auth.SCOPES`; `uploads`, `captions`, `playlists`, `channel_edits`, `subscriptions` registered on the app.

- [ ] **Step 1: Write failing test `tests/test_wiring.py`:**

```python
import asyncio


def test_upload_scope_present():
    from youtube_studio_mcp import auth
    assert "https://www.googleapis.com/auth/youtube.upload" in auth.SCOPES


def test_all_new_tools_registered():
    from youtube_studio_mcp.server import app
    names = set(asyncio.run(_names(app)))
    for t in ("video_upload", "video_delete", "video_rate", "video_schedule",
              "video_cancel_schedule", "video_set_localizations",
              "caption_list", "caption_insert", "caption_update", "caption_delete",
              "caption_download", "playlist_create", "playlist_update",
              "playlist_delete", "playlist_add_video", "playlist_item_remove",
              "playlist_set_image", "playlist_delete_image",
              "channel_update_branding", "channel_section_create",
              "channel_section_update", "channel_section_delete",
              "channel_set_banner", "channel_set_watermark",
              "channel_unset_watermark", "subscription_add",
              "subscription_remove"):
        assert t in names, f"{t} not registered"


async def _names(app):
    return [t.name for t in await app.list_tools()]
```

- [ ] **Step 2: Run to verify fail** — FAIL (scope missing, modules unregistered).

- [ ] **Step 3a: Add the scope in `auth.py`** — after the `youtube.force-ssl` entry in `SCOPES`:

```python
    "https://www.googleapis.com/auth/youtube.upload",
```

- [ ] **Step 3b: Register modules in `server.py`** — change the tools import to:

```python
from .tools import (analytics, captions, channel_edits, comments, data, edits,
                    meta, playlists, reporting, subscriptions, uploads)
```

And after `edits.register(app)` add:

```python
uploads.register(app)
captions.register(app)
playlists.register(app)
channel_edits.register(app)
subscriptions.register(app)
```

- [ ] **Step 3c: Rewrite the scope-cap section of `tools/youtube-studio-mcp/CLAUDE.md`.** Replace "## Scope cap (locked)" with:

```markdown
## Scope (v2 — full write surface open)

Exposed write tools (all gated writes need `confirm=True`):
- Videos/Shorts: video_upload (resumable), video_update_metadata, video_set_thumbnail,
  video_delete, video_rate, video_schedule / video_cancel_schedule,
  video_set_localizations.
- Captions: caption_list, caption_insert (400u), caption_update (450u),
  caption_delete, caption_download.
- Playlists: playlist_create/update/delete, playlist_add_video,
  playlist_item_remove, playlist_set_image / playlist_delete_image.
- Channel: channel_update_branding, channel_section_create/update/delete,
  channel_set_banner, channel_set_watermark / channel_unset_watermark.
- Subscriptions: subscription_add / subscription_remove.

Gated (confirm=True): all deletes, video_rate, public/scheduled upload,
video_schedule, private->public, channel branding/banner/watermark,
subscriptions. captions insert/update are quota-guarded (cost gate).

Still NO API anywhere (do not attempt; no endpoint exists): A/B Test & Compare,
comment settings (allow/hold/disable), end screens, info cards, age restriction,
monetization, multi-language AUDIO dubs (only text localizations are writable),
recording location. Still deferred by choice: live streaming
(liveBroadcasts/liveStreams), CMS/content-owner, multi-channel.

OAuth: `youtube.force-ssl` (already granted) authorizes every write; we also
request `youtube.upload`. No re-consent required for existing tokens.
```

- [ ] **Step 4: Run to verify pass** — Run: `uv run pytest tests/test_wiring.py -v` → PASS (2).

- [ ] **Step 5: Run the full suite** — Run: `uv run pytest -q` → all green.

- [ ] **Step 6: Commit:**

```bash
git add src/youtube_studio_mcp/auth.py src/youtube_studio_mcp/server.py tools/youtube-studio-mcp/CLAUDE.md tests/test_wiring.py
git commit -m "feat(youtube-mcp): register full write surface + upload scope + v2 docs"
```

**Operator note:** the new scope does not invalidate the existing `force-ssl`
token. To grant it explicitly, run `uv run youtube-studio-mcp auth` once.

---

## Task 19: Correct downstream skill notes

**Files:** Modify `.claude/skills/video-publish-qa/SKILL.md`, `.claude/skills/shorts-creator/SKILL.md`, `.claude/skills/youtube-studio/SKILL.md` (only the lines claiming the MCP can't upload/schedule/write captions).

**Interfaces:** Docs-only; no code, no test. (Folded here as the doc-consistency deliverable.)

- [ ] **Step 1: Find the stale claims**

Run: `grep -rn "can.t upload\|can.t schedule\|can.t write captions\|cannot upload\|v1 MCP\|MCP can.t" .claude/skills/video-publish-qa .claude/skills/shorts-creator .claude/skills/youtube-studio`
Expected: a handful of lines asserting the MCP cannot upload, schedule, or write captions.

- [ ] **Step 2: Update each hit**

For each matched line, replace the "can't upload / schedule / write captions"
claim with the v2 reality, e.g.:
- video-publish-qa: captions are now writable via `caption_insert` (hand-off no
  longer required); note the 400-unit cost gate.
- shorts-creator: the MCP can now `video_upload` (private by default) and
  `video_schedule`; the manual Studio upload hand-off becomes optional.
- youtube-studio: add the new write tools to the tool inventory.

Keep edits minimal and factual — change only the now-false sentences.

- [ ] **Step 3: Verify no stale claims remain**

Run: `grep -rn "can.t upload\|can.t schedule\|can.t write captions" .claude/skills/video-publish-qa .claude/skills/shorts-creator .claude/skills/youtube-studio`
Expected: no matches (or only matches that are now correctly scoped, e.g. "can't schedule via the A/B test UI").

- [ ] **Step 4: Commit:**

```bash
git add .claude/skills/video-publish-qa/SKILL.md .claude/skills/shorts-creator/SKILL.md .claude/skills/youtube-studio/SKILL.md
git commit -m "docs(skills): correct MCP upload/schedule/caption claims for v2 write surface"
```

---

## Self-Review

**Spec coverage (spec §7):**
- §6.1 read-modify-write → Task 4. §6.2 resumable upload → Task 5. §6.3 confirm-gate → Task 3. §4 quota → Task 2. ✓
- §7.1 videos: upload (Task 9), delete+rate (Task 6), schedule+cancel (Task 7), localizations (Task 8), update refactor (Task 10). ✓
- §7.2 captions: list+download (Task 11), insert+update+delete (Task 12). ✓
- §7.3 playlists: CRUD (Task 13), items+images (Task 14). ✓
- §7.4 channel: branding+sections (Task 15), banner+watermark (Task 16). ✓
- §7.5 subscriptions → Task 17. ✓
- §3 OAuth scope + §8 docs → Tasks 18–19. ✓
- A/B testing excluded (no API) — stated in CLAUDE.md (Task 18). ✓

**Placeholder scan:** No TBD/TODO. Every code step has complete code; every test has assertions. Task 19 is intentionally a doc-edit task with a grep-guided procedure (no invented file contents) since the exact stale lines are discovered at execution time.

**Type consistency:**
- `gate.require(confirm, *, effect, **extra)` — identical across Tasks 6, 7, 9, 11, 12, 13, 14, 15, 16, 17.
- `gate.quota_guard(endpoint, multiplier, confirm)` — Tasks 3, 12.
- `mutate.fetch_merge_update(svc, *, resource, id, parts, patch, record_list, record_update)` — identical across Tasks 4, 7, 8, 10, 13, 15.
- `uploadmedia.validate(path, *, max_bytes, allowed_mimes)` + `execute_resumable(request)` — Tasks 5, 9, 12, 14, 16.
- `_default_media_factory(path, mime)` defined in `uploads.py` (Task 9), reused for banner/watermark (Task 16).
- All `_<tool>` cores take `svc` first and return `dict`; all wrappers call `clients.youtube_data()`.

**Wiring check:** every module created (uploads, captions, playlists, channel_edits, subscriptions) is registered in Task 18; `edits.py` is already registered. `video_set_thumbnail` unchanged. ✓
