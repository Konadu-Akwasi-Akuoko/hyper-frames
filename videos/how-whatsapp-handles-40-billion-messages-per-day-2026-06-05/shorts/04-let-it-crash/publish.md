# Publish — Short 04 · Let it crash

**Scheduled:** 2026-06-12 (day 2 — second of the two day-two Shorts, paired with Short 03).
**File:** `out/04-let-it-crash.mp4` (1080×1920 delivery, rendered at portrait-4k 2160×3840, 67.3s)
**Cover-prepend:** `out/04-let-it-crash-cover.mp4` (same render, the cover held as the first ~1s — for the frame-trick in Path B below; stream-copied, no quality loss)
**Cover (chosen):** `thumbnail-vertical-a.png` (1080×1920 — faceless, WhatsApp mark + "WHATSAPP WANTS ITS CODE TO CRASH"). Alternates exported: `-b.png` ("CRASHING IS THE FEATURE"), `-c.png` ("LET IT CRASH").

---

## Title

> Why WhatsApp Wants Its Code to Crash

(≤100 chars; the open "why" the cover's paradox sets up without spoiling the
let-it-crash / Erlang answer. Alternates if A/B testing later: "WhatsApp's code
is built to crash — on purpose" · "The crash that keeps WhatsApp running".)

## Description

```
WhatsApp's engineers wanted their code to crash — on purpose. It's an actual philosophy called "let it crash." Most systems wrap everything in safety nets and try to recover from every error. WhatsApp's backend does the opposite: every phone gets its own tiny isolated process on Erlang's BEAM VM — millions running at once. When one breaks, it doesn't try to heal. It just dies, alone. A supervisor spawns a fresh copy, and the other million never feel it.

Full breakdown of how WhatsApp actually handles 40 billion messages a day (persistent connections, the actor model, "let it crash", end-to-end encryption): [PARENT VIDEO URL — paste once the long-form is live]

None of it comes free — Erlang is a niche language and was never built for raw speed. So what does a tiny team actually buy by betting everything on it? More Shorts dropping this week.

#Shorts #WhatsApp #SystemDesign
```

## Hashtags

`#Shorts` `#WhatsApp` `#SystemDesign` `#Erlang` `#SoftwareEngineering`

---

## The loop (per PLAN.md)

CTA ends on **"So what does a tiny team actually buy by betting everything on a
language almost nobody hires for? To find out, subscribe."** → opens the
trade-off mystery (why bet on niche Erlang at all) and hands forward, while
pointing back at the parent long-form for the full answer.

## Manual Studio upload (MCP v1 can't upload or schedule)

Two ways to set the custom cover — pick whichever Studio offers for this Short:

**Path A — direct custom thumbnail (simplest, if available):**
1. Studio → **Create → Upload videos** → select `out/04-let-it-crash.mp4` (plain render).
2. **Title / Description:** paste from above — **fill the `[PARENT VIDEO URL]`** once the long-form is live.
3. **Thumbnail:** upload `thumbnail-vertical-a.png` (the chosen pick; `-b`/`-c` are alternates).
4. **Hashtags:** already in the description; confirm `#Shorts` is present.
5. **Visibility → Schedule →** set **2026-06-12**.

**Path B — frame-trick (reliable fallback if Shorts won't accept a custom thumbnail):**
1. Studio → **Create → Upload videos** → select `out/04-let-it-crash-cover.mp4` (cover held as the first ~1s).
2. **Title / Description / Hashtags:** same as Path A.
3. **Thumbnail → Select frame from video →** scrub to **00:00** (the held cover frame) → Save.
4. **Visibility → Schedule →** set **2026-06-12**.
5. Once it's live: **YouTube editor → Trim →** cut the **first ~1 second**. The Short then opens on the hook; the chosen thumbnail persists.

(Optional) After it's live, run `video-publish-qa` against it to catch thin tags / caption gaps.
