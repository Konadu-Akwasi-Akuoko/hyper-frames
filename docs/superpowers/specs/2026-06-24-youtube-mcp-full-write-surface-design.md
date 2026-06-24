# youtube-studio-mcp — full write surface (v2) — design spec

**Date:** 2026-06-24
**Status:** approved (brainstorm), pending implementation plan
**Supersedes:** the "Scope cap (locked)" section of `tools/youtube-studio-mcp/CLAUDE.md`

## 1. Goal

Lift the deliberately-locked "v1" scope cap on the `youtube-studio-mcp` server so the
MCP can **post and edit the complete metadata + content write surface that the YouTube
Data API v3 actually exposes** — uploads (videos + Shorts), scheduling, captions,
localizations, thumbnails, playlists, and channel-level branding — each grounded in the
official API docs and guarded by a uniform confirmation gate for irreversible /
public-facing / social actions.

Every endpoint in this spec carries its **official source URL** so the costs, scopes,
writable fields, and constraints can be verified independently. All facts were fetched
from `developers.google.com` on 2026-06-24.

## 2. Scope

### In scope
The full set of YouTube Data API v3 **write** methods for a single creator channel:
videos (insert/update/delete/rate), thumbnails, captions, video localizations,
playlists + playlistItems + playlistImages, channels.update (branding/localizations),
channelSections, channelBanners, watermarks, subscriptions. (comments.* writes already
exist and are unchanged.)

### Out of scope (and why)
- **A/B "Test & Compare" (titles + thumbnails)** — **no public API exists.** It is a
  YouTube Studio web-UI-only feature; there is no endpoint to create a test, read its
  winner, or roll one out. Confirmed against the
  [YouTube Data API reference](https://developers.google.com/youtube/v3/docs) (no A/B
  resource) and the
  [A/B test help page](https://support.google.com/youtube/answer/16391400) ("only
  available on computers through YouTube Studio"). The 2026 expansion (up to 5 variants,
  auto-rollout) is still Studio-only. Revisit only via browser automation if ever wanted.
- **Studio-only video settings with no API:** comment settings (allow/hold/disable/sort),
  end screens, info cards (the old `invideoPromotion` was retired), age restriction,
  monetization (ad formats/mid-rolls/suitability), multi-language **audio** dubs (only
  *text* localizations are writable), recording **location** (deprecated — only
  `recordingDate` remains), notify-subscribers, Premiere settings.
- **Live streaming** (`liveBroadcasts`/`liveStreams`), **CMS/content-owner reports**,
  **multi-channel** — remain deferred; not part of "post + edit metadata."
- **Creator-heart / comment-pinning** — no API (already documented gaps).

### Shorts note
A Short is **not a distinct resource**. It is a vertical video ≤3 min uploaded through
the identical `videos.insert` flow; YouTube classifies it server-side by aspect
ratio + duration. There are **no Shorts-only writable metadata fields** in the API, so
every video tool in this spec applies identically to Shorts. You cannot toggle
"is a Short" via API. Source (absence of any Shorts field):
[videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert),
[videos resource](https://developers.google.com/youtube/v3/docs/videos).

## 3. OAuth scope analysis — no re-consent required

The locked cap stated "`youtube.upload` is NOT requested." Research shows the upload
scope was never **technically** required: **`youtube.force-ssl` — already granted in the
current token — is an accepted scope for every write method in this spec, including
`videos.insert`, `channelBanners.insert`, and `watermarks.set`.**

| Method | Accepted scopes (force-ssl always present) | Source |
|---|---|---|
| videos.insert | youtube.upload, youtube, youtubepartner, **force-ssl** | [insert](https://developers.google.com/youtube/v3/docs/videos/insert) |
| thumbnails.set | youtubepartner, youtube.upload, youtube, **force-ssl** | [set](https://developers.google.com/youtube/v3/docs/thumbnails/set) |
| channelBanners.insert | youtube.upload, youtube, **force-ssl** | [insert](https://developers.google.com/youtube/v3/docs/channelBanners/insert) |
| watermarks.set | youtubepartner, youtube.upload, youtube, **force-ssl** | [set](https://developers.google.com/youtube/v3/docs/watermarks/set) |
| subscriptions.* | youtubepartner, youtube, **force-ssl** (not upload) | [insert](https://developers.google.com/youtube/v3/docs/subscriptions/insert) |
| all others (videos.update/delete/rate, captions.*, playlists.*, channels.update, channelSections.*) | youtube, youtubepartner, **force-ssl** | per-method pages, §6 |

**Decision:** lifting the cap requires **zero re-authentication** — the existing
`force-ssl` token authorizes the whole surface. We will additionally add
`https://www.googleapis.com/auth/youtube.upload` to the requested `SCOPES` list in
`auth.py` as a least-surprise marker for upload intent, but this is optional and does not
invalidate the current token. Scope strings reference:
[OAuth scopes registry](https://developers.google.com/identity/protocols/oauth2/scopes).

## 4. Quota model

Default allocation: **10,000 units/day** for the general pool, resetting at **midnight
Pacific Time**, plus a **separate 100-uploads/day bucket** for `videos.insert` (1 quota
per call) and a separate 100 bucket for `search.list`. Source:
[determine_quota_cost](https://developers.google.com/youtube/v3/determine_quota_cost)
(verified verbatim 2026-06-24: *"videos.insert — 100 quota per day. Each call costs 1
quota."*). The historical "1600 units" figure for `videos.insert` is **stale** — uploads
do **not** draw on the 10k pool.

Per-method costs (all verified against `determine_quota_cost` unless noted):

| Method | Units | Method | Units |
|---|---|---|---|
| videos.insert | **1** (100/day bucket) | playlists.insert/update/delete | 50 each |
| videos.update | 50 | playlistItems.insert/update/delete | 50 each |
| videos.delete | 50 | playlistImages.insert/update/delete | 50 each |
| videos.rate | 50 | channels.update | 50 |
| thumbnails.set | 50 | channelSections.insert/update/delete | 50 each |
| captions.list | 50 | channelBanners.insert | 50 |
| captions.insert | **400** | watermarks.set/unset | 50 each |
| captions.update | **450** | subscriptions.insert/delete | 50 each |
| captions.delete | 50 | comments.* (existing) | 50 each |
| captions.download | 200 | | |

The two expensive writes (`captions.insert` 400, `captions.update` 450) get a
remaining-quota guard mirroring the existing bulk-comment guard in `comments.py`
(refuse if the call would consume > 25% of remaining daily quota without `confirm=True`).
All new endpoint costs are added to the `quota.py` ledger cost table.

## 5. Module organization

New tool modules mirror the API resources; each is registered in `server.py`.

```
src/youtube_studio_mcp/tools/
  edits.py         (exists)  → + video_delete, video_rate, video_schedule, video_set_localizations
  uploads.py       (new)     → video_upload (resumable), channel_set_banner, channel_set_watermark
  captions.py      (new)     → caption_list, caption_insert, caption_update, caption_delete, caption_download
  playlists.py     (new)     → playlist_create/update/delete, playlist_add_video/item_update/item_remove,
                               playlist_set_image/update_image/delete_image
  channel_edits.py (new)     → channel_update_branding, channel_section_create/update/delete, channel_unset_watermark
  subscriptions.py (new)     → subscription_add, subscription_remove
```

## 6. Shared infrastructure (built once, reused by all tools)

### 6.1 Read-modify-write helper (`clients.py` or a new `mutate.py`)
Every `*.update` is an HTTP **PUT** that **deletes any field omitted within the part you
send** (verbatim on each update page: *"If your request does not specify a value for a
property that already has a value, the property's existing value will be deleted."* —
[videos.update](https://developers.google.com/youtube/v3/docs/videos/update),
[playlists.update](https://developers.google.com/youtube/v3/docs/playlists/update),
[channels.update](https://developers.google.com/youtube/v3/docs/channels/update),
[channelSections.update](https://developers.google.com/youtube/v3/docs/channelSections/update),
[captions.update](https://developers.google.com/youtube/v3/docs/captions/update)). A
shared `fetch_merge_update(resource, id, part, patch)` helper does list → deep-merge
patch → update so partial edits never wipe data. The existing hand-rolled merge in
`video_update_metadata` is refactored onto this helper.

Constraint baked in: `videos.update` of `snippet` **requires** re-sending `id`,
`snippet.title`, and `snippet.categoryId` ([videos.update](https://developers.google.com/youtube/v3/docs/videos/update));
the helper re-supplies them from the fetched resource. Localizations require
`defaultLanguage` set or the API returns `defaultLanguageNotSet`.

### 6.2 Resumable upload helper (`uploads.py`)
`MediaFileUpload(path, mimetype, resumable=True)` + a `request.next_chunk()` loop that
reports progress and survives interruption (308 resume). Shared by `video_upload`,
`channel_set_banner`, `channel_set_watermark`, `caption_insert/update`,
`playlist_set_image`. Protocol reference:
[resumable upload guide](https://developers.google.com/youtube/v3/guides/using_resumable_upload_protocol).
`videos.insert` accepts `video/*` / `application/octet-stream`, max 256 GB
([insert](https://developers.google.com/youtube/v3/docs/videos/insert)).

### 6.3 Unified confirm-gate
Extend the existing `confirm_publish` convention into a consistent `confirm: bool = False`
parameter. When `False`, a gated tool **does not execute** — it returns a structured
`{"error": "confirm_required", "reason": "...", ...}` describing the exact effect, and
runs only when re-called with `confirm=True`. Three gate categories:

- **Irreversible:** `video_delete`, `caption_delete`, `playlist_delete`,
  `channel_section_delete`, `playlist_delete_image`.
- **Public-facing / channel-wide:** `video_upload` (only when `privacyStatus=public` or a
  `publishAt` is set), `video_schedule` (arming the schedule), private→public transitions
  (existing), `channel_update_branding`, `channel_set_banner`, `channel_set_watermark` /
  `channel_unset_watermark`.
- **Acts socially as the channel:** `subscription_add`, `subscription_remove`,
  `video_rate`.

**Ungated** (trivially reversible): editing a draft's snippet/status, `thumbnails.set`,
adding/removing a playlist item, rescheduling or cancelling a schedule (it only ever makes
a video *less* public), localizations.

## 7. Per-tool specs

Notation: **G** = gated, **U** = ungated. Every method's quota/scope/source is in §4 / §6.

### 7.1 Videos — `edits.py` (extend) + `uploads.py`
- `video_update_metadata` (exists, U except publish gate) — refactor onto §6.1 helper.
- `video_upload(path, title, description=…, tags=…, category_id=…, privacy="private", publish_at=None, made_for_kids=False, contains_synthetic_media=None, confirm=False)` — **videos.insert**, resumable (§6.2). **G** only if `privacy=public` or `publish_at` set. Source: [insert](https://developers.google.com/youtube/v3/docs/videos/insert).
- `video_schedule(video_id, publish_at, confirm=False)` — **G**. Sets `status.publishAt` + `status.privacyStatus=private` (must re-send private even if already private); video must never have been published. Reschedule (new `publish_at`) and cancel (private, no `publish_at`) are **U**. Source: [videos resource — publishAt](https://developers.google.com/youtube/v3/docs/videos).
- `video_delete(video_id, confirm=False)` — **G**, irreversible. 204 on success. Source: [delete](https://developers.google.com/youtube/v3/docs/videos/delete).
- `video_rate(video_id, rating, confirm=False)` — **G**, social. `rating ∈ {like, dislike, none}`. Source: [rate](https://developers.google.com/youtube/v3/docs/videos/rate).
- `video_set_localizations(video_id, localizations, default_language, confirm=False)` — **U**. videos.update `part=localizations` + `snippet.defaultLanguage`; send the **complete** set each call (PUT replaces the part). Source: [videos resource — localizations](https://developers.google.com/youtube/v3/docs/videos).

Writable snippet/status fields (for reference, all via videos.update):
`title` (≤100 chars), `description` (≤5000 **bytes**), `tags` (≤500 chars total),
`categoryId`, `defaultLanguage`, `defaultAudioLanguage`, `privacyStatus`, `publishAt`,
`embeddable`, `license`, `publicStatsViewable`, `selfDeclaredMadeForKids`,
`containsSyntheticMedia`, `recordingDetails.recordingDate`. Source:
[videos resource](https://developers.google.com/youtube/v3/docs/videos).

### 7.2 Captions — `captions.py`
- `caption_list(video_id)` — **U**. Returns track ids (required input to update/delete/download). Source: [list](https://developers.google.com/youtube/v3/docs/captions/list).
- `caption_insert(video_id, file_path, language, name, is_draft=False, confirm=False)` — **400 units**, quota-guard gated. Media body = caption file (`text/xml` / `application/octet-stream` / `*/*`, ≤100 MB); SRT uploads fine as octet-stream. Source: [insert](https://developers.google.com/youtube/v3/docs/captions/insert).
- `caption_update(caption_id, file_path=None, is_draft=None, confirm=False)` — **450 units**, quota-guard gated. Replaces the track's file and/or draft status; needs `caption_id` from `caption_list`. Source: [update](https://developers.google.com/youtube/v3/docs/captions/update).
- `caption_delete(caption_id, confirm=False)` — **G**, irreversible. Source: [delete](https://developers.google.com/youtube/v3/docs/captions/delete).
- `caption_download(caption_id, tfmt="srt", tlang=None)` — **U**, 200 units. `tfmt ∈ {sbv, scc, srt, ttml, vtt}`; `tlang` = machine-translation target. Source: [download](https://developers.google.com/youtube/v3/docs/captions/download).

This is the natural consumer of the `create-srt-and-translate` skill output (English SRT
+ 13 dubs → one `caption_insert` per language).

### 7.3 Playlists — `playlists.py`
- `playlist_create(title, description=…, privacy="private", localizations=None)` — **U**. Required: `snippet.title`. Source: [insert](https://developers.google.com/youtube/v3/docs/playlists/insert).
- `playlist_update(playlist_id, …, confirm-not-required)` — **U** (read-modify-write; re-send `snippet.title`). Source: [update](https://developers.google.com/youtube/v3/docs/playlists/update).
- `playlist_delete(playlist_id, confirm=False)` — **G**, irreversible. Cannot delete system playlists. Source: [delete](https://developers.google.com/youtube/v3/docs/playlists/delete).
- `playlist_add_video(playlist_id, video_id, position=None)` — **U**. Body needs `snippet.playlistId` + `snippet.resourceId{kind:"youtube#video", videoId}`; `position` 0-indexed and requires manual-sort playlists. Source: [playlistItems.insert](https://developers.google.com/youtube/v3/docs/playlistItems/insert).
- `playlist_item_update(item_id, …)` — **U**. Re-send `snippet.playlistId` + `resourceId`. Source: [update](https://developers.google.com/youtube/v3/docs/playlistItems/update).
- `playlist_item_remove(item_id, confirm=False)` — **G**, irreversible-ish. `id` = **playlist item id**, not video id. Source: [delete](https://developers.google.com/youtube/v3/docs/playlistItems/delete).
- `playlist_set_image / update_image / delete_image` — playlistImages.* (square 1:1 JPEG/PNG ≤2 MB; delete **G**). Source: [playlistImages](https://developers.google.com/youtube/v3/docs/playlistImages).

### 7.4 Channel-level — `channel_edits.py` + `uploads.py`
- `channel_update_branding(description=None, keywords=None, country=None, unsubscribed_trailer=None, default_language=None, localizations=None, confirm=False)` — **G**, channel-wide. channels.update `part=brandingSettings` (or `localizations`) — **only `brandingSettings` / `invideoPromotion` / `localizations` parts are writable**; `snippet`/title is **not** arbitrarily settable (`brandingSettings.channel.title` must equal current title or be omitted). Read-modify-write. Source: [channels.update](https://developers.google.com/youtube/v3/docs/channels/update).
- `channel_set_banner(image_path, confirm=False)` — **G**. Two-step: channelBanners.insert (≥2048×1152, 16:9, ≤6 MB) → read `url` → channels.update `brandingSettings.image.bannerExternalUrl`. Sources: [channelBanners.insert](https://developers.google.com/youtube/v3/docs/channelBanners/insert) + channels.update.
- `channel_section_create/update/delete(…, confirm on delete)` — channelSections.*; max 10 shelves; `snippet.type` required. Sources: [insert](https://developers.google.com/youtube/v3/docs/channelSections/insert), [update](https://developers.google.com/youtube/v3/docs/channelSections/update), [delete](https://developers.google.com/youtube/v3/docs/channelSections/delete).
- `channel_set_watermark(image_path, timing_type, offset_ms, duration_ms, confirm=False)` / `channel_unset_watermark(confirm=False)` — **G**. set: media-upload, JPEG/PNG ≤10 MB, `position.cornerPosition` only `topRight` documented, `timing.type ∈ {offsetFromStart, offsetFromEnd}`; returns 204. Sources: [set](https://developers.google.com/youtube/v3/docs/watermarks/set), [unset](https://developers.google.com/youtube/v3/docs/watermarks/unset).

### 7.5 Subscriptions — `subscriptions.py`
- `subscription_add(channel_id, confirm=False)` — **G**, social. Body `snippet.resourceId{kind:"youtube#channel", channelId}`. Source: [insert](https://developers.google.com/youtube/v3/docs/subscriptions/insert).
- `subscription_remove(subscription_id, confirm=False)` — **G**, social. `id` = subscription id. Source: [delete](https://developers.google.com/youtube/v3/docs/subscriptions/delete).

## 8. Downstream documentation updates

- Rewrite the "Scope cap (locked)" section of `tools/youtube-studio-mcp/CLAUDE.md` v1→v2:
  uploads, captions, scheduling, localizations, playlists, channel branding now exposed;
  the remaining deferrals (live, CMS, multi-channel, A/B, comment settings, end screens,
  cards) stated as either no-API or out-of-scope.
- Correct the "MCP can't upload / schedule / write captions" notes in the
  `video-publish-qa`, `shorts-creator`, and `youtube-studio` skills.
- Update `quota.py` cost table + `quota_status` / `cost_preview` to include all new
  endpoints.

## 9. Testing strategy

- Per-module unit tests with the googleapiclient service mocked (no live quota spend),
  asserting: request body shape, read-modify-write merge correctness, gate refusal when
  `confirm=False`, quota-guard refusal on captions when over budget.
- A `test_driver.py`-style smoke path (manual, opt-in, real quota) documented but not run
  in CI.
- Gate-matrix test: every gated tool refuses without `confirm`, executes with it.

## 10. Open questions resolved during brainstorm

- **A/B testing:** excluded — no API.
- **Re-auth:** not needed — `force-ssl` covers everything.
- **Gating split:** gate irreversible + public-facing + social; ungate draft edits,
  thumbnails, playlist membership, reschedule/cancel.
- **videos.insert quota:** 1 unit in a separate 100/day bucket, not 1600 against the pool.

## 11. Source index (for independent verification)

- Quota: https://developers.google.com/youtube/v3/determine_quota_cost
- Scopes: https://developers.google.com/identity/protocols/oauth2/scopes
- Resumable upload: https://developers.google.com/youtube/v3/guides/using_resumable_upload_protocol
- videos: [resource](https://developers.google.com/youtube/v3/docs/videos) ·
  [insert](https://developers.google.com/youtube/v3/docs/videos/insert) ·
  [update](https://developers.google.com/youtube/v3/docs/videos/update) ·
  [delete](https://developers.google.com/youtube/v3/docs/videos/delete) ·
  [rate](https://developers.google.com/youtube/v3/docs/videos/rate)
- thumbnails: https://developers.google.com/youtube/v3/docs/thumbnails/set
- captions: [list](https://developers.google.com/youtube/v3/docs/captions/list) ·
  [insert](https://developers.google.com/youtube/v3/docs/captions/insert) ·
  [update](https://developers.google.com/youtube/v3/docs/captions/update) ·
  [delete](https://developers.google.com/youtube/v3/docs/captions/delete) ·
  [download](https://developers.google.com/youtube/v3/docs/captions/download)
- playlists: [insert](https://developers.google.com/youtube/v3/docs/playlists/insert) ·
  [update](https://developers.google.com/youtube/v3/docs/playlists/update) ·
  [delete](https://developers.google.com/youtube/v3/docs/playlists/delete)
- playlistItems: [insert](https://developers.google.com/youtube/v3/docs/playlistItems/insert) ·
  [update](https://developers.google.com/youtube/v3/docs/playlistItems/update) ·
  [delete](https://developers.google.com/youtube/v3/docs/playlistItems/delete)
- playlistImages: https://developers.google.com/youtube/v3/docs/playlistImages
- channels.update: https://developers.google.com/youtube/v3/docs/channels/update
- channelSections: [insert](https://developers.google.com/youtube/v3/docs/channelSections/insert) ·
  [update](https://developers.google.com/youtube/v3/docs/channelSections/update) ·
  [delete](https://developers.google.com/youtube/v3/docs/channelSections/delete)
- channelBanners.insert: https://developers.google.com/youtube/v3/docs/channelBanners/insert
- watermarks: [set](https://developers.google.com/youtube/v3/docs/watermarks/set) ·
  [unset](https://developers.google.com/youtube/v3/docs/watermarks/unset)
- subscriptions: [insert](https://developers.google.com/youtube/v3/docs/subscriptions/insert) ·
  [delete](https://developers.google.com/youtube/v3/docs/subscriptions/delete)
- A/B testing (no API): [API reference](https://developers.google.com/youtube/v3/docs) ·
  [Studio-only help](https://support.google.com/youtube/answer/16391400)
