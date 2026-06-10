# bytebytego-chat-system — pacing report (mechanical)

- Source: https://www.youtube.com/watch?v=okrR1KXNLtA
- Title: FAANG System Design Interview: Design A Chat System (WhatsApp, Facebook Messenger, Discord, Slack)
- Channel: ByteByteGo
- Upload date: 20250922
- Proxy: <=1080p, 524.72s
- Subtitles: en-orig (auto, word_level=True, punctuated=True, 1345 words)

## Aggregates

- scene_count: 21
- cuts_per_minute: 1.94
- soft_transition_count: 3
- scene_duration_s: median 9.00 · p25 5.68 · p75 24.44 · min 0.62 · max 165.44
- longest_hold_s: 165.44
- words_per_s_mean: 2.41
- pct_cuts_in_pause: 0.05
- pct_sentence_aligned: 0.35

## Scenes

Contact-sheet tiles are row-major, 10 per row, in the table's scene order (no on-image labels).

| # | start | end | dur_s | boundary | score | words | wps | pause_before_s | ¶ | text |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.00 | 4.32 | 4.32 | start | - | 9 | 2.08 | 0.56 | n | WhatsApp and Facebook Messenger process billions of messages daily. |
| 2 | 4.32 | 10.00 | 5.68 | cut | 0.078 | 14 | 2.46 | 0.00 | n | Behind every message is a distributed system delivering text instantly across the… |
| 3 | 10.00 | 15.84 | 5.84 | cut | 0.164 | 20 | 3.42 | 0.00 | y | do we design a test system that can handle real-time messaging at… |
| 4 | 15.84 | 35.80 | 19.96 | cut | 0.080 | 55 | 2.76 | 0.00 | n | lot to cover when designing a test system, so let's focus on… |
| 5 | 35.80 | 139.68 | 103.88 | cut | 0.056 | 254 | 2.45 | 0.00 | y | also show online presence with that familiar green dot. We're designing for… |
| 6 | 139.68 | 167.64 | 27.96 | cut | 0.051 | 65 | 2.32 | 0.00 | y | services handle authentication, user profiles, and message sending through REST APIs. Load… |
| 7 | 167.64 | 333.08 | 165.44 | cut | 0.062 | 446 | 2.70 | 0.00 | n | This capacity determines how many servers we need as we scale. When… |
| 8 | 333.08 | 355.60 | 22.52 | cut | 0.055 | 61 | 2.71 | 0.00 | n | One-on-one messages works smoothly now, but group chat introduce a new complexity.… |
| 9 | 355.60 | 362.64 | 7.04 | cut | 0.294 | 21 | 2.98 | 0.00 | n | This works well for a requirement of up to 100 members since… |
| 10 | 362.64 | 403.72 | 41.08 | cut | 0.296 | 109 | 2.65 | 0.00 | y | messaging sorted out, let's work on another feature, online presence. The green… |
| 11 | 403.72 | 412.72 | 9.00 | cut | 0.098 | 23 | 2.56 | 0.00 | y | built a working chat system, but success brings new problems. As our… |
| 12 | 412.72 | 420.44 | 7.72 | cut | 0.073 | 20 | 2.59 | 0.00 | n | connections likely becomes the first bottleneck. As user count grows, we need… |
| 13 | 420.44 | 444.88 | 24.44 | cut | 0.059 | 64 | 2.62 | 0.00 | y | database can also hit limits as we scale. As millions of users… |
| 14 | 444.88 | 470.40 | 25.52 | cut | 0.092 | 60 | 2.35 | 0.00 | y | This covers the core chat system architecture. There are other areas worth… |
| 15 | 470.40 | 489.72 | 19.32 | cut | 0.063 | 46 | 2.38 | 0.00 | n | Media handling is its own beast. Sharing images and videos requires compression,… |
| 16 | 489.72 | 507.76 | 18.04 | cut | 0.061 | 48 | 2.66 | 0.00 | n | One more, we need ray limiting and abuse prevention. Stopping spams and… |
| 17 | 507.76 | 508.80 | 1.04 | cut | 0.086 | 4 | 3.85 | 0.00 | n | Ready to ace your |
| 18 | 508.80 | 513.50 | 4.70 | soft | 0.309 | 13 | 2.77 | 0.00 | n | next technical interview? Join our community where we offer comprehensive courses on… |
| 19 | 513.50 | 519.84 | 6.34 | soft | 0.263 | 11 | 1.74 | 0.00 | n | design, coding, behavioral questions, machine learning, and object-oriented design. Learn more |
| 20 | 519.84 | 524.10 | 4.26 | cut | 0.079 | 2 | 0.47 | 0.00 | n | at bitebico.com. |
| 21 | 524.10 | 524.72 | 0.62 | soft | 0.166 | 0 | 0.00 | 3.74 | n | - |
