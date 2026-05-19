"""Filesystem paths for credentials, tokens, and SQLite stores.

Default config directory is ``~/.config/youtube-studio-mcp/`` to match the
documented setup. Two env vars override:

- ``YOUTUBE_STUDIO_MCP_CONFIG_DIR`` — overrides the directory for all files
- ``YOUTUBE_STUDIO_MCP_TOKEN_PATH`` — overrides the token file path specifically
"""

from __future__ import annotations

import os
from pathlib import Path


def config_dir() -> Path:
    override = os.environ.get("YOUTUBE_STUDIO_MCP_CONFIG_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".config" / "youtube-studio-mcp"


def ensure_config_dir() -> Path:
    d = config_dir()
    d.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(d, 0o700)
    except OSError:
        pass
    return d


def client_secret_path() -> Path:
    return config_dir() / "client_secret.json"


def token_path() -> Path:
    override = os.environ.get("YOUTUBE_STUDIO_MCP_TOKEN_PATH")
    if override:
        return Path(override).expanduser()
    return config_dir() / "token.json"


def warehouse_db_path() -> Path:
    return config_dir() / "warehouse.db"


def quota_db_path() -> Path:
    return config_dir() / "quota.db"
