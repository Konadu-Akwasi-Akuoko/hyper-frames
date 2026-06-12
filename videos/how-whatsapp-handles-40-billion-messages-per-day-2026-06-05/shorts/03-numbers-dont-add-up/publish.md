# Publish — Short 03 · The numbers don't add up

**Scheduled:** 2026-06-12 (day 2 — first of the two day-two Shorts, paired with Short 04).
**File:** `out/03-numbers-dont-add-up.mp4` (1080×1920 delivery, rendered at portrait-4k 2160×3840, 74.8s)
**Cover-prepend:** `out/03-numbers-dont-add-up-cover.mp4` (same render, the cover held as the first ~1s — for the frame-trick in Path B below; stream-copied, no quality loss)
**Cover:** `thumbnail-vertical-a.png` (1080×1920 — faceless cover, WhatsApp mark + "20 BILLION SENT BECAME 64 BILLION")

---

## Title

> Why WhatsApp's Message Count Doesn't Add Up

(≤100 chars; the open "why" the cover's +40-billion anomaly sets up without
spoiling the fan-out answer. Alternates if A/B testing later: "WhatsApp's
numbers don't add up — here's why" · "The hidden 40 billion in WhatsApp's day".)

## Description

```
20 billion messages sent. 64 billion delivered. Same day, same messages — so where do the extra 40 billion come from? The answer is server-side fan-out: your phone uploads a group message exactly once, and the server quietly queues a separate copy for every member. One message in, a hundred out.

Full breakdown of how WhatsApp actually handles 40 billion messages a day (persistent connections, the actor model, "let it crash", end-to-end encryption): [PARENT VIDEO URL — paste once the long-form is live]

The gap isn't a bug — it's the architecture made visible. But a few years later they had to flip fan-out completely inside-out, just to let you read your chats on a laptop. Why? More Shorts dropping this week.

#Shorts #WhatsApp #SystemDesign
```

## Hashtags

`#Shorts` `#WhatsApp` `#SystemDesign` `#SoftwareEngineering` `#Tech`

---

## The loop (per PLAN.md)

CTA ends on **"a few years later, they had to flip fan-out completely inside-out
— just to let you read your chats on a laptop. Why? To see it, subscribe."** →
opens the multi-device / Sender Keys mystery and hands forward, while pointing
back at the parent long-form for the full answer.

## Manual Studio upload (MCP v1 can't upload or schedule)

Two ways to set the custom cover — pick whichever Studio offers for this Short:

**Path A — direct custom thumbnail (simplest, if available):**
1. Studio → **Create → Upload videos** → select `out/03-numbers-dont-add-up.mp4` (plain render).
2. **Title / Description:** paste from above — **fill the `[PARENT VIDEO URL]`** once the long-form is live.
3. **Thumbnail:** upload `thumbnail-vertical-a.png`.
4. **Hashtags:** already in the description; confirm `#Shorts` is present.
5. **Visibility → Schedule →** set **2026-06-12**.

**Path B — frame-trick (reliable fallback if Shorts won't accept a custom thumbnail):**
1. Studio → **Create → Upload videos** → select `out/03-numbers-dont-add-up-cover.mp4` (cover held as the first ~1s).
2. **Title / Description / Hashtags:** same as Path A.
3. **Thumbnail → Select frame from video →** scrub to **00:00** (the held cover frame) → Save.
4. **Visibility → Schedule →** set **2026-06-12**.
5. Once it's live: **YouTube editor → Trim →** cut the **first ~1 second**. The Short then opens on the hook; the chosen thumbnail persists.

(Optional) After it's live, run `video-publish-qa` against it to catch thin tags / caption gaps.
