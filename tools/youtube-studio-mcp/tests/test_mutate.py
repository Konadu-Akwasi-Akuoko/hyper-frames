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
