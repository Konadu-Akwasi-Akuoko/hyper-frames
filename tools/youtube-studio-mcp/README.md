# youtube-studio-mcp

MCP server that exposes the **YouTube Analytics API**, **YouTube Reporting
API**, and **YouTube Data API v3** to Claude Code so the model can read your
channel data and act on it (reply to comments, moderate, fix metadata, upload
thumbnails).

## Install

```bash
cd tools/youtube-studio-mcp
uv sync
```

## Set up Google Cloud

You need a Google Cloud project with the three YouTube APIs enabled and an OAuth
desktop client ID. This is a one-time setup.

Google replaced the old single "OAuth consent screen" page with the **Google
Auth Platform**, which splits the same settings across Branding, Audience, Data
access, and Clients sub-pages. The steps below match the current UI.

1. Go to <https://console.cloud.google.com/> and create a new project (or pick
   an existing one).
2. **Enable APIs** at <https://console.cloud.google.com/apis/library>:
   - YouTube Data API v3
   - YouTube Analytics API
   - YouTube Reporting API
3. **Configure the Google Auth Platform** at
   <https://console.cloud.google.com/auth/overview>:
   - First visit only: click **GET STARTED** and fill the onboarding wizard:
     - App name: anything (e.g. `youtube-studio-mcp`)
     - User support email: your address
     - Audience: **External**
     - Contact email: your address
   - After onboarding, open **Audience** in the left nav and add your own
     Google account under **Test users**. The project stays in **Testing**
     publishing status — only listed test users can authenticate, which is
     fine for a single-creator setup.
4. **Create an OAuth client** at
   <https://console.cloud.google.com/auth/clients>:
   - Click **CREATE CLIENT**.
   - Application type: **Desktop app**.
   - Name: anything.
   - Click **CREATE**. The new client appears in the list with its client ID
     shown inline — **do not copy that text into a file.** Click the
     **download icon** (↓) at the end of the client's row and save the
     downloaded JSON. The file should be a few hundred bytes and start with
     `{"installed":{ ... }}`.
5. Save the downloaded file as:

   ```
   ~/.config/youtube-studio-mcp/client_secret.json
   ```

## First-run OAuth

```bash
uv run youtube-studio-mcp auth
```

This opens your browser, asks you to consent to the four scopes:

- `yt-analytics.readonly`
- `yt-analytics-monetary.readonly`
- `youtube.readonly`
- `youtube.force-ssl`

Then writes a refresh token to `~/.config/youtube-studio-mcp/token.json`
(`chmod 0600`). The MCP server uses this token from then on.

> **Note — Testing-mode refresh tokens expire after 7 days.** While the project
> sits in **Testing** publishing status, Google revokes test-user
> authorizations 7 days after consent. If `auth_status` starts reporting an
> invalid refresh token, re-run `uv run youtube-studio-mcp auth`. To remove
> the 7-day cap, move the project to **In production** under Google Auth
> Platform → **Audience**. The four scopes requested here are all sensitive
> YouTube scopes, so production verification is non-trivial — most
> single-creator setups just live with the periodic re-auth.

## Register with Claude Code

Add to your project's `.mcp.json` (at the repo root):

```json
{
  "mcpServers": {
    "youtube-studio": {
      "command": "uv",
      "args": [
        "--directory",
        "tools/youtube-studio-mcp",
        "run",
        "youtube-studio-mcp",
        "serve"
      ]
    }
  }
}
```

## Verify with MCP Inspector

```bash
npx @modelcontextprotocol/inspector \
  uv --directory tools/youtube-studio-mcp run youtube-studio-mcp serve
```

Lists all tools and resources. Try `auth_status` first — it should report your
channel ID and granted scopes.

## Daily warehouse sync (optional)

After your first `auth`, run once to create the Reporting API jobs:

```bash
uv run youtube-studio-mcp sync --ensure-jobs
```

Jobs take ~24h to produce their first CSV. After that:

```bash
uv run youtube-studio-mcp sync
```

ingests any new daily reports into `~/.config/youtube-studio-mcp/warehouse.db`.
Wire it into cron / launchd for nightly updates.

## What this exposes

See `CLAUDE.md` for the full tool roster, quota cost table, and call-order
guidance.

## What this does NOT expose

- Video uploads (`videos.insert`) — defer to v2
- Caption CRUD — defer to v2
- Livestream scheduling — defer to v2
- Comment heart / pin — **YouTube API does not expose these**; use Studio UI
