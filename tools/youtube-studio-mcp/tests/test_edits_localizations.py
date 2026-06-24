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
