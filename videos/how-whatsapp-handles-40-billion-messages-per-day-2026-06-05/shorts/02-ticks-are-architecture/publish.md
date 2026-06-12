# Publish — Short 02 · The ticks are architecture

**Scheduled:** 2026-06-11 (today) — second of the two front-loaded launch-day Shorts.
**File:** `out/02-ticks-are-architecture.mp4` (1080×1920 delivery, rendered at portrait-4k 2160×3840, 63.5s)
**Cover-prepend:** `out/02-ticks-are-architecture-cover.mp4` (same render, the cover held as the first ~1s — for the frame-trick in Path B below; stream-copied, no quality loss)
**Cover:** `thumbnail-vertical-a.png` (1080×1920 — faceless cover, WhatsApp mark + "those two ticks are leaking A SECRET")

---

## Title

> What WhatsApp's ticks are actually telling you

(≤100 chars; an open "what" question the cover's "a secret" sets up without
spoiling. Alternates if A/B testing later: "The hidden meaning of WhatsApp's
ticks" · "WhatsApp's ticks aren't a status — they're architecture".)

## Description

```
Those two ticks aren't a status update. They're WhatsApp's architecture showing through onto your screen — store-and-forward, narrating its own delivery one step at a time.

Full breakdown of how WhatsApp actually handles 40 billion messages a day (persistent connections, the actor model, "let it crash", end-to-end encryption): [PARENT VIDEO URL — paste once the long-form is live]

One grey tick, two grey, two blue — and a queue that holds your message for 30 days. But the server that carries every message can't read a single word of it. How? More Shorts dropping this week.

#Shorts #WhatsApp #SystemDesign
```

## Hashtags

`#Shorts` `#WhatsApp` `#SystemDesign` `#SoftwareEngineering` `#Tech`

---

## The loop (per PLAN.md)

CTA ends on **"that server carries every message you send, and it can't read a
single word of any of them — how is that even possible?"** → opens the
encryption mystery and hands directly to Short 05 (`cant-read-your-messages`),
while pointing back at the parent long-form for the full answer.

## Manual Studio upload (MCP v1 can't upload or schedule)

Two ways to set the custom cover — pick whichever Studio offers for this Short:

**Path A — direct custom thumbnail (simplest, if available):**
1. Studio → **Create → Upload videos** → select `out/02-ticks-are-architecture.mp4` (plain render).
2. **Title / Description:** paste from above — **fill the `[PARENT VIDEO URL]`** once the long-form is live.
3. **Thumbnail:** upload `thumbnail-vertical-a.png`.
4. **Hashtags:** already in the description; confirm `#Shorts` is present.
5. **Visibility → Schedule →** set **2026-06-11**.

**Path B — frame-trick (reliable fallback if Shorts won't accept a custom thumbnail):**
1. Studio → **Create → Upload videos** → select `out/02-ticks-are-architecture-cover.mp4` (cover held as the first ~1s).
2. **Title / Description / Hashtags:** same as Path A.
3. **Thumbnail → Select frame from video →** scrub to **00:00** (the held cover frame) → Save.
4. **Visibility → Schedule →** set **2026-06-11**.
5. Once it's live: **YouTube editor → Trim →** cut the **first ~1 second**. The Short then opens on the hook; the chosen thumbnail persists.

(Optional) After it's live, run `video-publish-qa` against it to catch thin tags / caption gaps.
