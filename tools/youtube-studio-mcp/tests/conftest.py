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
