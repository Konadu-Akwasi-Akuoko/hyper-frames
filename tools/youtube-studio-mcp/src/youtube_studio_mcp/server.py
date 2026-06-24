"""FastMCP server entry point.

Imports each tool/resource module and lets it register against the shared
``FastMCP`` app. Started over stdio by ``youtube-studio-mcp serve`` (the CLI
sub-command); never invoked directly by users.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from . import logging_setup
from .resources import workflows
from .tools import (analytics, captions, channel_edits, comments, data, edits,
                    meta, playlists, reporting, subscriptions, uploads)

logging_setup.configure()

app = FastMCP(name="youtube-studio")

meta.register(app)
data.register(app)
analytics.register(app)
comments.register(app)
edits.register(app)
uploads.register(app)
captions.register(app)
playlists.register(app)
channel_edits.register(app)
subscriptions.register(app)
reporting.register(app)
workflows.register(app)
