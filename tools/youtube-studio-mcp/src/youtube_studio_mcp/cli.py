"""Command-line entry point.

Subcommands:

- ``auth``  — run the browser OAuth flow and write a refresh token.
- ``serve`` — start the MCP server over stdio (used by Claude Code).
- ``sync``  — pull new Reporting API CSVs into the local SQLite warehouse.
"""

from __future__ import annotations

import argparse
import logging
import sys

from . import logging_setup

logger = logging.getLogger(__name__)


def _cmd_auth(_args: argparse.Namespace) -> int:
    from . import auth, paths
    try:
        creds = auth.run_installed_app_flow()
    except auth.AuthError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    print(f"Authorized. Token written to {paths.token_path()}")
    print(f"Scopes granted: {', '.join(creds.scopes or [])}")
    return 0


def _cmd_serve(_args: argparse.Namespace) -> int:
    from .server import app
    app.run(transport="stdio")
    return 0


def _cmd_sync(args: argparse.Namespace) -> int:
    from . import warehouse
    if args.ensure_jobs:
        created = warehouse.ensure_standard_jobs()
        print(f"Ensured {len(created)} standard report jobs.")
    n = warehouse.sync()
    print(f"Sync complete. Ingested {n} new reports.")
    return 0


def main(argv: list[str] | None = None) -> int:
    logging_setup.configure()
    parser = argparse.ArgumentParser(prog="youtube-studio-mcp")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_auth = sub.add_parser("auth", help="Run OAuth flow and persist refresh token.")
    p_auth.set_defaults(func=_cmd_auth)

    p_serve = sub.add_parser("serve", help="Start MCP server over stdio.")
    p_serve.set_defaults(func=_cmd_serve)

    p_sync = sub.add_parser("sync", help="Sync Reporting API CSVs into local warehouse.")
    p_sync.add_argument("--ensure-jobs", action="store_true",
                        help="Idempotently create the standard channel report jobs first.")
    p_sync.set_defaults(func=_cmd_sync)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
