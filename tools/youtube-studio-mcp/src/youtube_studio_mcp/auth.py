"""Google OAuth installed-app flow and token persistence.

The browser-based consent flow runs out-of-band via ``youtube-studio-mcp auth``
so the MCP serve loop never blocks on user input. The refresh token persists at
``~/.config/youtube-studio-mcp/token.json`` (mode 0600) and is auto-refreshed on
every API call.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from . import paths

logger = logging.getLogger(__name__)

SCOPES: list[str] = [
    "https://www.googleapis.com/auth/yt-analytics.readonly",
    "https://www.googleapis.com/auth/yt-analytics-monetary.readonly",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/youtube.upload",
]


class AuthError(Exception):
    """Raised when credentials are missing, invalid, or unrefreshable."""


@dataclass(frozen=True)
class AuthStatus:
    authorized: bool
    reason: str | None = None
    scopes_granted: list[str] | None = None
    token_expires_at: str | None = None
    token_path: str | None = None


def _read_token_file(path: Path) -> Credentials | None:
    if not path.exists():
        return None
    try:
        return Credentials.from_authorized_user_file(str(path), SCOPES)
    except Exception as e:
        logger.warning("Failed to load token file at %s: %s", path, e)
        return None


def _write_token_file(creds: Credentials, path: Path) -> None:
    paths.ensure_config_dir()
    path.write_text(creds.to_json())
    try:
        os.chmod(path, 0o600)
    except OSError as e:
        logger.warning("Could not chmod 0600 on %s: %s", path, e)


def load_credentials() -> Credentials:
    """Load + refresh credentials from disk. Raises ``AuthError`` if missing."""
    path = paths.token_path()
    creds = _read_token_file(path)
    if creds is None:
        raise AuthError(
            f"No credentials at {path}. Run `youtube-studio-mcp auth` first."
        )
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                _write_token_file(creds, path)
            except Exception as e:
                raise AuthError(f"Failed to refresh token: {e}") from e
        else:
            raise AuthError(
                "Stored credentials are invalid and cannot be refreshed. "
                "Run `youtube-studio-mcp auth` to re-authenticate."
            )
    return creds


def run_installed_app_flow() -> Credentials:
    """Run the browser-based OAuth consent flow and persist the token."""
    secret = paths.client_secret_path()
    if not secret.exists():
        raise AuthError(
            f"OAuth client secret not found at {secret}. "
            "Download a Desktop OAuth client JSON from Google Cloud Console and "
            "save it to that path (see README)."
        )
    try:
        flow = InstalledAppFlow.from_client_secrets_file(str(secret), SCOPES)
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        raise AuthError(
            f"{secret} is not a valid OAuth Desktop client JSON ({e}). "
            "Download the JSON file by clicking the download icon next to "
            "your client at https://console.cloud.google.com/auth/clients — "
            "do not copy the client ID text. The file should start with "
            '`{"installed":{ ... }}`.'
        ) from e
    creds = flow.run_local_server(port=0, prompt="consent")
    _write_token_file(creds, paths.token_path())
    return creds


def get_status() -> AuthStatus:
    """Inspect credentials without raising — safe to call before any tool."""
    path = paths.token_path()
    if not path.exists():
        return AuthStatus(authorized=False, reason=f"No token file at {path}",
                          token_path=str(path))
    try:
        raw = json.loads(path.read_text())
    except Exception as e:
        return AuthStatus(authorized=False, reason=f"Token file unreadable: {e}",
                          token_path=str(path))
    try:
        creds = load_credentials()
    except AuthError as e:
        return AuthStatus(authorized=False, reason=str(e),
                          scopes_granted=raw.get("scopes"),
                          token_path=str(path))
    return AuthStatus(
        authorized=True,
        scopes_granted=list(creds.scopes or []),
        token_expires_at=(creds.expiry.isoformat() if creds.expiry else None),
        token_path=str(path),
    )


def has_monetary_scope() -> bool:
    try:
        creds = load_credentials()
    except AuthError:
        return False
    return "https://www.googleapis.com/auth/yt-analytics-monetary.readonly" in (creds.scopes or [])
