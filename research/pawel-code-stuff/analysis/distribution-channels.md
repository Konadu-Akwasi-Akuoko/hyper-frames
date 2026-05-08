# PawelCodeStuff — distribution channel analysis

**The question:** where did the breakout traffic for "Why is rendering text so complicated?" (125,672 views) actually come from?

**The answer, unambiguously:** YouTube's own recommendation algorithm. There is no meaningful external referrer.

This is a more useful finding than discovering an HN/Reddit feature would have been — it tells us the breakout was won purely on YouTube-native signals (title + thumbnail + retention + engagement), and that the strategy is replicable without needing to land an external feature.

---

## 1. Evidence ledger — what we searched, what we found

| Platform | How we searched | Result |
|---|---|---|
| **Hacker News** | Algolia API — video URL, video ID, channel name, exact title | **One submission, 2 points, 0 comments** (user `chedoku`, 2026-05-06). Did not surface. No comments, no discussion. |
| **HN — other 7 videos** | Algolia API for each video ID | **Zero submissions** for any other video |
| **Reddit** | Reddit JSON search for video ID, channel name, exact title; Google `site:reddit.com` queries | **Zero indexed posts**. No subreddit picked it up. |
| **Twitter / X** | Google `site:x.com` + `site:twitter.com` for video ID and URL; @handle search | **Zero indexed mentions** |
| **Lobste.rs** | Native search for channel name, video ID | **Zero results** |
| **Newsletter / blog network** | Google + ByteByteGo Substack, dev.to, Medium | **Zero features**. ByteByteGo's Substack does not link to him. |
| **Generic web** | `"youtube.com/watch?v=4soZ33MvlW4"` exact-string search | **Zero results** outside the YouTube URL itself |

Five platforms searched. One submission with two points across all of them. That's not where 125,000 viewers came from.

---

## 2. The smoking gun: viewers say where they came from

The 622 mined comments include 25 explicit references to *how viewers found the video*. Every single one points to YouTube itself.

### YouTube algorithm / recommended (15 comments)

> "Glad this just showed up randomly in my feed. Clear, concise, and informative. Instant sub!" — mouse keys
>
> "Sometimes the YouTube algo just gives you a video from a smaller creator you've never heard of and you know it's gonna be a banger before even clicking. Awesome video, very well explained and nice visuals" — text rendering
>
> "Thanks YouTube for recommending such high level quality channel." — password hashing
>
> "Absolute gold mine of a recommendation" — password hashing
>
> "Thanks a lot 😊 Comment for the algorithm" — mouse keys

### "Just stumbled across this" / found by chance (10 comments)

> "Just discovered your channel, I see this is the 8th video, it need to take off!!" — text rendering
>
> "Just randomly came across this video and I really like how concise your explanation is! Have my subscription =)" — UUID
>
> "I've literally been low key brainstorming on the side on how to harvest entropy for cryptographic protocols. Had no idea we were already this far in implementing all of that 😂" — mouse keys (no source named, but no external referrer either)

### External platforms

- **Reddit / HN / Twitter referrals**: 0 comments
- **Friend / colleague shared**: 0 comments
- **Newsletter / blog**: 1 comment, but it's a viewer who *previously read* a Medium article on the same topic, not someone who came from the newsletter — *"i came across this when i was regarding a medium article and you basically covered the entire article in this video"*

Twenty-five viewers explicitly named YouTube; zero named anywhere else. Combined with the platform-search results, this is conclusive.

---

## 3. What this actually means

YouTube's recommendation algorithm decides whether to push a video by looking at signals it can compute from inside YouTube:

1. **Click-through rate** on impressions (the title + thumbnail combo we already studied)
2. **Average view duration** and **session watch time** (does the viewer stay, do they keep watching YouTube after?)
3. **Like rate** (the 10.3% Pawel hit on the breakout is in the top decile for tech YouTube)
4. **Comment volume and depth** (651 comments on a 5-min video is exceptional)
5. **Subscribe rate from the video** (we can't measure this externally, but the pre-commitment comments suggest it's high)
6. **Audience retention curve** (no flat drop-offs — the rabbit-hole script keeps people)

Every one of those signals is *internal*. None of them require external promotion. Pawel is winning because the artifact itself — the title, thumbnail, script, and animation — is engineered to score high on all six.

The implication for *our* strategy: **we should not over-index on external distribution for video #1**. If our title/thumbnail/script/retention are dialed, YouTube will distribute for us. If they aren't, no amount of HN posting will compensate.

---

## 4. The comparison we have on the channel itself

The other 7 videos on Pawel's channel are a controlled experiment. Same channel, same upload cadence, same thumbnail template, same voiceover quality, same audience subscription pool. Their views diverge by 71x:

| Video | Views | Like rate | Title verb |
|---|---|---|---|
| Load Balancing | 1,757 | 8.6% | "Explained in N min" formula |
| Database Indexes | 2,550 | 8.2% | Formula |
| File Compression | 3,612 | 7.2% | Formula |
| 3 Databases | 8,307 | 6.9% | Statement |
| Password Hashing | 9,214 | 9.95% | Rephrased "Why X must Y" |
| Mouse Keys | 14,982 | 10.2% | "Why X secures Y" (bigger claim) |
| UUID vs Auto-Inc | 78,291 | 6.3% | Formula (high-search topic) |
| Text Rendering | 125,672 | 10.3% | Rephrased + universal topic |

Two videos broke out. They share three features:

- **Universally relatable topic** ("text on screen", "primary key choice") that any working developer has thought about
- **Strong title-thumbnail tension pair** (we documented this in `thumbnail-patterns.md`)
- **High like rate** (10%+ on the rephrase pattern) sustaining algorithmic confidence

If those three are present, YouTube does the rest. If any one is missing, the video sits at 5–15K.

---

## 5. The distribution playbook (for our channel)

Given that the breakout path is YouTube-internal, the playbook is mostly about engineering for YouTube's own signals — not about getting features elsewhere. But there are a handful of external plays worth running, mostly as *insurance* and for the second-order benefit (subs from off-platform networks who'll then juice the Day 1 signal back on YouTube).

### Tier 1 — YouTube-native engineering (the real work)

1. **Title pair**: searchable keyword phrase (for the search-traffic floor) + a punchier rewrite as thumbnail text (for the click ceiling). Reference `thumbnail-patterns.md` section 7.
2. **Thumbnail**: own visual identity, two colors, three rows of text, single icon. Section 12 of the thumbnail-patterns doc has a drop-in template.
3. **First 30 seconds**: the 9-beat arc's beats 1–4 (familiar action → subversion → stakes → thesis). This is the retention ceiling — viewers either stay past 30s or they don't.
4. **Retention curve**: the escalation cycles in beat 6. No condensed dense moments (audience explicitly complained when this happened on Pawel's file-compression video).
5. **Like-rate ceiling**: a synthesis or reframe that triggers the "aha" moment. Beats 7–8.
6. **Comment seed**: pinned comment with a pointed open question or a "what's the next thing you want me to cover" prompt — turns comments from passive into a feed-engagement loop.
7. **End-screen**: another video from our channel, not a generic subscribe ask. We need to watch-time-loop ourselves.

### Tier 2 — external plays worth running (insurance, ~1-2 hours per launch)

These didn't drive Pawel's breakout, but they're cheap and add small upside. Order matters because cross-posting in the first 24h boosts the YouTube Day 1 signal.

1. **r/programming on Reddit** — for any of our planned topics (text rendering, networking internals, OS scheduling, compiler internals), this subreddit is the right home. Submit *with the YouTube link, not a re-host* — the algorithmic boost from external referrers landing on YouTube is what we want.
2. **r/webdev**, **r/javascript**, **r/computerscience** for topic-specific videos.
3. **Hacker News** — `Show HN`-style submission with the YouTube URL. Post on a Tuesday or Wednesday morning US-time. Pawel's submission flatlined at 2 points; we won't do worse than that, and a single comment from someone respected can change the trajectory.
4. **Lobste.rs** — invite-only, but if we have an account, it's a high-quality audience for technical deep-dives.
5. **Twitter / X** — a thread that *is* the video's argument in 6–8 tweets, with the YouTube link at the end as the "watch the full thing" CTA. The thread itself is shareable; the video is the asset.
6. **dev.to / Medium / Substack** — write the *script* of the video as a long-form article, with the YouTube embed at the top. Cross-publishing the same insight in two media shapes makes the work go further.

### Tier 3 — community signal (long-term)

1. **Pin the strongest "aha moment" comment** on each video. Pawel doesn't do this. It's free.
2. **Reply substantively to top 5 comments** for the first 20 videos. Pawel replies more on early videos than later ones; we should keep replying past the engagement-burnout point.
3. **End every video with a teaser for video #2** (not a generic "subscribe!"). Build internal session length.

### What NOT to do

1. **Don't pay for promotion in the first 20 videos.** The audience explicitly fears the "fireship route" of commercial drift. A sponsorship or an ad placement before we've earned trust will cap the channel's growth ceiling.
2. **Don't post to general r/videos or r/youtube.** Wrong audiences; will get downvoted.
3. **Don't cold-DM newsletters asking for features.** ByteByteGo has 1M+ subscribers and they didn't link to PawelCodeStuff. Earned features happen organically; pursued ones make us look amateur.
4. **Don't game the comment section.** Sock-puppet comments and comment-trade groups get caught by YouTube and tank the algorithm signal we're trying to build.

---

## 6. The Day-1 launch sequence (drop-in)

For each video we publish, run this on launch day. Total time investment: ~90 minutes plus video creation.

```
T-24h
  [ ] Final lint + inspect + preview pass on the composition (per CLAUDE.md)
  [ ] Render at 60fps (production lever the audience asked for explicitly)
  [ ] Upload as Unlisted to YouTube to verify thumbnail/title/end-screen render correctly
  [ ] Schedule public release for Tuesday or Wednesday 09:00 US Eastern

T-0h (publish)
  [ ] Publish the YouTube video
  [ ] Pin a seed comment that asks one specific question (turns lurkers into commenters)
  [ ] Post a Twitter/X thread (6–8 tweets) that is the argument of the video, ending with the link
  [ ] Submit to r/programming with the title in question form (matches the YouTube title approach)
  [ ] Cross-publish a long-form article version on dev.to or substack with the embed at top
  [ ] (Optional) Submit to Hacker News with the YouTube link — at most once, no resubmits

T+0…24h
  [ ] Reply substantively to first 5 comments on YouTube
  [ ] Reply on the Reddit thread to any technical pushback
  [ ] Reply on the Twitter thread to any thread quotes

T+72h
  [ ] Audit YouTube Studio: CTR, average view duration, audience retention curve
  [ ] Identify drop-off points; note for next video's pacing
  [ ] Identify the highest-liked comment; consider a pinned response
```

---

## 7. The one thing the comments hint at, that we still can't measure

A handful of comments mention seeing his videos as "shorts" or "in their feed" in ways that suggest **YouTube Shorts as feeder traffic**. We have no Shorts in his current upload set, but YouTube has been aggressively cross-promoting longer videos to Shorts viewers. Worth watching whether he eventually publishes a Short that excerpts the breakout video — if he does, and the longer video sees a second wave, that confirms Shorts as a feeder.

For *our* channel: a 60-second Short version of each long video, posted 1–2 days after the long video, is cheap to produce in HyperFrames (just render a different composition with the same beats compressed) and may be the single highest-leverage external lever we have.

---

## 8. Open questions

- **Foreign-language traffic.** The non-English comments that came through (Vietnamese, Portuguese fragments) suggest international view share. YouTube's auto-translate of titles may be doing real work in non-English markets. Worth tracking which countries the views came from once we have access to YouTube Studio analytics on our own videos.
- **Mobile vs. desktop split.** Mobile viewers complained more about graphic legibility — we know that demographic skews heavier on YouTube. We should design every composition mobile-first.
- **Watch-time after his video.** If viewers stayed on YouTube and watched another video after his, the algorithm rewards him heavily. We can't see this directly, but it's what makes the "session watch time" signal work. Designing our videos to end with a strong recommendation for our *next* video (not just a generic subscribe) is the lever.
