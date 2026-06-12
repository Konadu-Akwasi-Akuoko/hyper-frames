# Publish — Short 01 · 32 engineers, 40 billion

**Scheduled:** 2026-06-11 (today) — first of the two front-loaded launch-day Shorts.
**File:** `out/01-32-engineers-40-billion.mp4` (1080×1920, portrait-4k 2160×3840 master, ~66s)
**Cover-prepend:** `out/01-32-engineers-40-billion-cover.mp4` (same render, the cover held as the first ~1s — for the frame-trick in Path B below; stream-copied, no quality loss)
**Cover:** `thumbnail-vertical-a.png` (1080×1920 — faceless number-contrast cover with the WhatsApp mark)

---

## Title

> How 32 engineers handle 40 billion messages a day

(≤100 chars; leads with the shock contrast the cover sets up. Alternates if A/B
testing later: "The tiny team behind 40 billion daily messages" · "How WhatsApp
scaled with only 32 engineers".)

## Description

```
32 engineers. 40 billion messages a day. ~14 million users each. Here's the architecture that made the math possible.

Full breakdown of how WhatsApp actually handles 40 billion messages a day (persistent connections, the actor model, "let it crash", end-to-end encryption): [PARENT VIDEO URL — paste once the long-form is live]

A team that small is also a bus factor waiting to happen. Where does it crack? More Shorts dropping this week.

#Shorts #WhatsApp #SystemDesign
```

## Hashtags

`#Shorts` `#WhatsApp` `#SystemDesign` `#SoftwareEngineering` `#Tech`

---

## The loop (per PLAN.md)

CTA ends on the **bus-factor crack** → curiosity about the limits of that
leverage. Hands forward to the rest of the batch (and points back at the parent
long-form for the full answer).

## Manual Studio upload (MCP v1 can't upload or schedule)

Two ways to set the custom cover — pick whichever Studio offers for this Short:

**Path A — direct custom thumbnail (simplest, if available):**
1. Studio → **Create → Upload videos** → select `out/01-32-engineers-40-billion.mp4` (plain render).
2. **Title / Description:** paste from above — **fill the `[PARENT VIDEO URL]`** once the long-form is live.
3. **Thumbnail:** upload `thumbnail-vertical-a.png`.
4. **Hashtags:** already in the description; confirm `#Shorts` is present.
5. **Visibility → Schedule →** set **2026-06-11**.

**Path B — frame-trick (reliable fallback if Shorts won't accept a custom thumbnail):**
1. Studio → **Create → Upload videos** → select `out/01-32-engineers-40-billion-cover.mp4` (cover held as the first ~1s).
2. **Title / Description / Hashtags:** same as Path A.
3. **Thumbnail → Select frame from video →** scrub to **00:00** (the held cover frame) → Save.
4. **Visibility → Schedule →** set **2026-06-11**.
5. Once it's live: **YouTube editor → Trim →** cut the **first ~1 second**. The Short then opens on the hook; the chosen thumbnail persists.

(Optional) After it's live, run `video-publish-qa` against it to catch thin tags / caption gaps.
