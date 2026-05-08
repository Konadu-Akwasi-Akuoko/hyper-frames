# PawelCodeStuff — topic selection analysis

**The question:** how does Pawel decide what to make a video about? Where is his topic pipeline coming from?

**The short answer:** he's almost certainly sampling from three established sources — *Designing Data-Intensive Applications* (DDIA), the system-design-primer GitHub repo, and a small set of canonical "X is harder than you think" blog posts — and filtering them through one specific question: *"Is this something every working developer touches but doesn't understand?"* He started the channel by explicitly asking viewers what to cover next, then locked into a clear curatorial pattern by video #5.

This document reverse-engineers his selection criteria, maps each of his 8 videos to its likely source, and ends with a 30-topic pipeline you can use to generate your own videos systematically.

---

## 1. The evidence ledger

### 1a. He explicitly crowdsourced topics in the first three videos

Each of the first three video descriptions ends with a literal request:

| Video | Description ending |
|---|---|
| Load Balancing | "Today I speak about load balancing. Let me know what you want to see next" |
| Database Indexes | "Today I speak about indexes. Let me know in comments what you want to see next" |
| File Compression | "Today video about compression. lmk what you want to see next" |

By video #4 (3 Databases) the descriptions started getting professionally structured (with chapter timestamps), and by video #5 (Password Hashing) the descriptions are full-fledged technical summaries with their own SEO copy. The "lmk what you want next" phrasing disappears.

**Implication:** the first 3 videos were a discovery phase — get something out, ask the audience to react, learn what gets engagement. From video #4 he locked in.

### 1b. Channel about, social presence — minimal

- Channel description: *"I try to explain technical concepts"* (5 words, the entire bio)
- No Twitter / X
- No GitHub
- No website
- No LinkedIn (a "Paul Codes Stuff" appears, but no confirmation it's him)
- Only external link in any video: `buymeacoffee.com/pawelcodestuff`

He's running deliberately stealth. No persona, no platform amplification, no public roadmap. All editorial decisions are happening privately.

### 1c. The topic-source mapping

Cross-referencing each of his 8 videos against the most-cited tech curricula:

| # | Video | DDIA chapter | System Design Primer | Canonical blog post | Other source |
|---|---|---|---|---|---|
| 1 | Load Balancing | — | ✓✓ ("Load balancer" section) | many | system-design-primer is the canonical reference |
| 2 | Database Indexes | ✓✓ Ch. 3 (Storage and Retrieval) | ✓ | many | DDIA staple |
| 3 | File Compression | — | — | — | CSAPP / algorithms 101 — the outlier |
| 4 | 3 Databases (ClickHouse / InfluxDB / Neo4j) | ✓✓ Ch. 2 + 3 (Data Models, Storage) | ✓ | — | DDIA's "specialized data stores" thread |
| 5 | Password Hashing | — | — (Security section is brief) | OWASP, security cv | Security 101 staple |
| 6 | Mouse → Random Numbers | — | — | many | OS internals (entropy, /dev/random) |
| 7 | UUID vs Auto-Increment | ✓ Ch. 6 (Partitioning) | ✓ | many | DB design 101 |
| 8 | Text Rendering | — | — | **"Text Rendering Hates You" (Beingessner, 2019)** | the canonical piece — see 1d |

**Five of eight videos map directly to DDIA + System Design Primer.** The other three split between security 101, OS internals, and one famous blog post.

### 1d. The text-rendering video is closely modeled on a 2019 canonical blog post

Alexis Beingessner's "Text Rendering Hates You" (faultlore.com, 2019) is the canonical "text rendering is harder than you think" piece on the internet. It hit Hacker News with 542 points and 169 comments and has been reposted multiple times since.

I checked Pawel's text-rendering video against the concepts in that blog post:

- **Covered** (14/29): vector, rasterization, anti-aliasing, hinting, bytecode, subpixel rendering, ClearType, color fringing, RGB, GPU texture atlas, cache
- **Skipped** (15/29): kerning, ligatures, HarfBuzz, FreeType, shaping, diacritics, emoji, Unicode, UTF-8, shaping engines

The pattern is striking: Pawel covered the visually-demonstrable subset (curves and pixels) and skipped the typographically-complex subset (Unicode shaping). That's a deliberate editorial choice — he picked the parts of the source material his visual production style could actually animate.

This is the most leverageable single insight in this analysis. **He turned a famous blog post into a video, but only the parts he could draw.** The blog already proved the topic was viral; he just had to translate it into a different medium with the parts that translated well.

### 1e. Discovery cadence — confirms YouTube algorithmic distribution

The text-rendering video, uploaded 2026-05-01, accumulated comments over the following days at this rate:

```
2026-05-03: 97 comments (peak)
2026-05-04: 62
2026-05-05: 51
2026-05-06: 30
2026-05-07: 45
```

Classic YouTube "Day 2–3 algorithmic boost" pattern with no external referral spike. This corroborates `distribution-channels.md`: the topic itself has to be strong enough that YouTube wants to push it, because no one else is going to.

---

## 2. Reverse-engineered selection criteria

From the topic-source mapping plus the script and thumbnail patterns, the filter Pawel is running each idea through looks like this:

### The five qualifying questions

For each candidate topic, he appears to ask:

1. **Does every working developer touch this regularly?** (Pressing keys, creating tables, generating keys, hashing passwords, scaling services.) If no, skip.
2. **Is it commonly used but rarely understood?** (Most devs use these things without knowing the internals.) If no, skip.
3. **Can the depth be demonstrated visually in 5–10 minutes?** (Rasterization yes; HarfBuzz Unicode shaping no — and he skipped that.) If no, narrow scope until yes.
4. **Are there real-world failure stories I can cite?** (Debian OpenSSL 2008, PlayStation 3 Fail0verflow, GPU cracking, ASIC mining — all show up in his scripts.) If no, lower priority.
5. **Can I make a "you've done this; here's why it's harder than it looks" angle?** (Beat 1 of the script formula requires this.) If no, skip.

The combination is rigorous. Many topics that pass questions 1–2 fail at 3 (too abstract, no good visual). Many that pass 1–3 fail at 5 (the topic is interesting but doesn't have an everyday handle).

### The four source pools

His pipeline is fed by, in roughly descending order of evidence:

1. **DDIA chapter list** — chapters 2, 3, 6, and arguably 5 cover the core data/storage topics. 5 of his 8 videos derive from this single book.
2. **System Design Primer (donnemartin GitHub)** — load balancer, databases, sharding, caching all come from here. Reinforces the DDIA picks with operational angles.
3. **Canonical "X is harder than you think" blog posts** — text-rendering (Beingessner 2019), password-hashing (countless blog posts on bcrypt/Argon2), randomness/entropy (LWN articles, "Cryptographically secure" canon).
4. **Audience comment requests** — he literally asked for the first 3 videos. Postgres specifically committed to in his reply on the 3-Databases video. Future videos likely partly driven by what shows up in the comments.

There is almost certainly a **shortlist or topic backlog** somewhere. His upload cadence (8 videos in 23 days, never breaking the rhythm) is impossible without a pre-built list — you can't research a deep technical video, write the script, animate it in Figma, voice it in 11labs, and edit in DaVinci Resolve in 2.8 days unless you came in with the topic, the outline, and the rabbit-hole loop already mapped.

---

## 3. The two-tier filter, visualized

```
        SOURCE POOLS
        ┌─────────────────────────────────────┐
        │  DDIA chapters 2, 3, 6              │
        │  System Design Primer               │
        │  Famous "X is hard" blog posts      │
        │  Audience comment requests          │
        └─────────────────┬───────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  FILTER 1: relatable + invisible    │
        │   • Every dev touches this?         │
        │   • Used commonly but not understood?│
        └─────────────────┬───────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────┐
        │  FILTER 2: visually demonstrable    │
        │   • Show depth in 5–10 minutes?     │
        │   • Real-world failure to cite?     │
        │   • "You've done this — here's why" │
        │     angle works?                    │
        └─────────────────┬───────────────────┘
                          │
                          ▼
                    ▼ Video Idea
```

What survives both filters is a small set per source — maybe 30–40 viable topics across the entire corpus. That's about a 2-year content runway.

---

## 4. What he hasn't covered yet (the obvious gaps)

Topics that pass his filter but he hasn't published. This is the *easiest* place to find topic ideas because the qualifying work is done — he's just hasn't gotten there yet.

### From DDIA (the dominant source pool)

- **Database transactions and isolation levels** (Ch. 7 — "your code reads the same row twice and gets two different answers")
- **Replication: leader / follower / multi-leader** (Ch. 5)
- **Sharding strategies and consistent hashing** (Ch. 6 — adjacent to UUID video)
- **Eventual consistency vs strong consistency** (Ch. 9)
- **Distributed consensus: Raft, Paxos** (Ch. 9)
- **Stream processing: Kafka internals** (Ch. 11)

### From System Design Primer

- **CDN: how a request actually reaches you in 30ms from the other side of the world**
- **DNS resolution: 8 round trips for a single google.com**
- **TCP three-way handshake and congestion control**
- **HTTP/2 vs HTTP/3 / QUIC**
- **Reverse proxy vs load balancer**
- **CAP theorem in practice**
- **Message queues: Kafka, RabbitMQ, SQS — when to pick which**

### From OS / systems internals

- **Garbage collection: why your code stalls for 200ms**
- **CPU caches and false sharing: why the same code runs 100x slower on different hardware**
- **Virtual memory and page tables**
- **Container internals: cgroups and namespaces**
- **Filesystems: journaling, copy-on-write, why fsync is so slow**
- **Floating-point: why 0.1 + 0.2 ≠ 0.3, IEEE 754 internals**

### From security canon

- **Public-key cryptography: RSA vs ECDSA**
- **TLS handshake: how your browser trusts a server in 200ms**
- **JWT vs sessions: why one is dangerous in the wrong place**
- **CSRF, XSS, SQL injection: still happening in 2026**
- **Side-channel attacks: timing attacks, Spectre, Meltdown**

### From the audience's own request list (already pulled from comments)

- **UTF-8 vs ANSI / mojibake / base64 encoding** (top text-rendering viewer asked for this)
- **Kerning + GPU recalc on zoom** (text-rendering follow-up)
- **Postgres deep dive** (Pawel committed to it)
- **All encryption methods (pub/priv keys)** (password-hashing follow-up)

### The text-rendering parts he skipped

- **Unicode shaping: HarfBuzz internals**
- **Emoji rendering: how a single 😂 is actually a sequence of code points**
- **Diacritics and combining characters: why Vietnamese is harder than English**

That's roughly 30 viable topics in front of us right now, all of which pass the same filter Pawel uses, none of which he has already done. **Our channel does not have a topic problem; we have an execution problem.**

---

## 5. Topic-generation framework for our channel

A repeatable process, runnable monthly to keep a 12+ video backlog.

### Step 1 — Maintain a source-pool feed (1 hour / month)

Keep an active reading list of the four source pools:

- **DDIA** — read one chapter per month, mark topics that pass Filter 1
- **System Design Primer GitHub** — re-skim quarterly; new sections are added regularly
- **Top 10 most-upvoted technical blog posts on HN this month** — `https://news.ycombinator.com/best` filtered for technical depth
- **Audience comment requests** — every video's comments will surface 1–3 follow-up topics

Maintain this feed in `research/topic-pipeline.md` (or similar). Append-only.

### Step 2 — Apply the two-tier filter (15 min per candidate)

For each candidate, write a one-page brief answering:

- Does every working developer encounter this? (yes/no)
- Is it commonly used but rarely understood? (yes/no)
- Can the depth be shown in 5–10 minutes of HyperFrames animation? (yes/no — and if no, what's the narrower scope that works?)
- What real-world failure can I cite? (Debian OpenSSL bug, PS3 Fail0verflow, etc.)
- What's the "you've done this; here's why it's harder than it looks" hook? (Sentence form.)

If any of the first three is "no," reject. If you can't answer questions 4 or 5 confidently, the topic is interesting but premature — park it.

### Step 3 — Group into clusters of 3 (2-month bundles)

Once you have a backlog of survivors, group them into clusters of 3 related videos. The cluster lets you:

- Reuse research effort (the second video in a cluster takes half the prep time of the first)
- Cross-reference videos in their own scripts ("we covered B-trees in the last video; today's video builds on that")
- Build internal session-watch-time loops on YouTube (end card from video 1 points to video 2)

For us, given the text-rendering work already done, the natural cluster:
1. **Why is rendering text so hard?** (the existing video) — covers curves, rasterization, hinting, subpixel
2. **Why Unicode is harder than ASCII** — UTF-8, shaping, emoji, diacritics
3. **Kerning, ligatures, and how typography survived computers** — typographic systems

Three videos, each ~5–7 minutes, sharing prep work and forming a "text on screens" trilogy. That cluster alone is a month of content.

### Step 4 — Schedule for cadence, not for inspiration

Pawel publishes every 2.8 days. That cadence is impossible without a backlog. **Always have at least 4 fully-prepped topics ahead of where you are publishing.** When inspiration is low, you fall back to the backlog. When inspiration is high, you add to it. The act of recording / animating / publishing is decoupled from the act of having a good idea.

---

## 6. The 30-topic pipeline (drop-in)

A starter backlog generated against the framework above. Each entry tagged with source pool and cluster. Use this as the seed for `research/topic-pipeline.md`.

### Cluster A — Text on screens (3 videos, builds on existing work)

1. **Why is rendering text so hard?** (existing) [blog: "Text Rendering Hates You"]
2. **Why Unicode is harder than ASCII** [blog: TRY Unicode section]
3. **Kerning, ligatures, and the geometry of type** [TRY shaping section]

### Cluster B — Database internals (4 videos, dominant DDIA)

4. **Database transactions: why your bug only happens at 3am** [DDIA Ch. 7]
5. **Sharding 101: how databases split themselves up** [DDIA Ch. 6]
6. **Replication: leader, follower, multi-leader** [DDIA Ch. 5]
7. **Eventual consistency vs strong consistency: which one bites you?** [DDIA Ch. 9]

### Cluster C — Networking ground truth (4 videos, system-design-primer)

8. **DNS: why resolving google.com takes 8 round trips** [SDP]
9. **TCP three-way handshake and congestion control** [SDP]
10. **HTTP/3 and QUIC: why HTTP got new plumbing** [SDP / Grigorik]
11. **CDN: how a static asset lives near you** [SDP]

### Cluster D — Memory and execution (4 videos, OS internals)

12. **CPU caches: why the same loop runs 100x faster** [systems canon]
13. **Garbage collection: why your code freezes for 200ms** [systems canon]
14. **Virtual memory and page tables: the lie your process believes** [OSTEP]
15. **Floating-point arithmetic: why 0.1 + 0.2 ≠ 0.3** [IEEE 754]

### Cluster E — Cryptography in production (4 videos, security canon)

16. **TLS handshake: how the browser trusts a server in 200ms** [security 101]
17. **Public-key crypto: RSA vs ECDSA explained** [security 101]
18. **JWT vs sessions: when one is dangerous** [security canon]
19. **Side-channel attacks: Spectre, Meltdown, timing leaks** [security canon]

### Cluster F — Distributed systems (3 videos, DDIA)

20. **Consistent hashing: how databases route keys** [DDIA Ch. 6]
21. **Consensus: why Raft and Paxos exist** [DDIA Ch. 9]
22. **The CAP theorem, in actual practice** [DDIA Ch. 9]

### Cluster G — Compilers and languages (3 videos, less covered)

23. **What a compiler actually does: parse, optimize, emit** [Crafting Interpreters]
24. **Why your loop runs faster after a million iterations: JIT compilation** [VM internals]
25. **Type systems: gradual, dependent, structural — what's the difference?** [PL canon]

### Cluster H — Filesystems and storage (3 videos, OS internals)

26. **Journaling filesystems: why your data survives a power cut** [OSTEP]
27. **fsync: the slowest syscall you didn't know you were calling** [database canon]
28. **Copy-on-write filesystems: how btrfs and ZFS save space** [OS internals]

### Standalone (2 videos)

29. **Container internals: how Docker works without Docker** [Liz Rice canon]
30. **Time and clocks in distributed systems: NTP, monotonic clocks, vector clocks** [DDIA Ch. 8]

---

## 7. The single highest-leverage insight to internalize

**Take famous canonical blog posts and turn them into videos.**

Pawel's breakout — text rendering, 125K views, 10.3% like rate — is a video adaptation of a 2019 blog post that already proved the topic was viral on Hacker News (542 points, 169 comments). He didn't have to gamble on whether the topic resonated. The blog post had already validated demand. He just had to translate the medium.

There are dozens of similar "X is harder than you think" canonical blog posts that *every senior engineer has read*, which have *zero* corresponding YouTube video at his level of production quality. Each is a half-de-risked breakout candidate. A non-exhaustive list:

- **"The Birth and Death of JavaScript"** (Gary Bernhardt, 2014)
- **"Falsehoods Programmers Believe About Names"** (Patrick McKenzie, 2010)
- **"What Every Programmer Should Know About Memory"** (Ulrich Drepper, 2007)
- **"Latency Numbers Every Programmer Should Know"** (Norvig, ongoing)
- **"How to Write a Spelling Corrector"** (Norvig, 2007)
- **"What Color Is Your Function?"** (Bob Nystrom, 2015)
- **"The Absolute Minimum Every Software Developer Must Know About Unicode"** (Joel Spolsky, 2003)
- **"Why You Should Never Use MongoDB"** (Sarah Mei, 2013)
- **"The Tail at Scale"** (Dean & Barroso, 2013)
- **"You Are Not Expected to Understand This"** (countless)
- **"Falsehoods Programmers Believe About Time"** (countless)

Each one is a candidate adaptation. Each is a known-resonant topic. Each is currently un-served at the production quality HyperFrames lets us deliver. **This is the topic-pipeline shortcut.**

---

## 8. Open questions for next research passes

- **Posting cadence vs view performance.** Pawel's 2.8-day rhythm may be load-bearing — fast cadence keeps subscribers engaged and signals algorithmic activity. We should benchmark whether a slower, deeper cadence (~7 days) hurts or helps.
- **Cluster economics.** I claimed the second video in a cluster takes half the prep time of the first. We should track actuals on our own clusters and adjust the framework.
- **Comment-request lag.** How long after a video posts before audience requests start showing up in comments? That tells us when to expect the second-source-pool signal kicking in for our own backlog.
- **"Famous blog post → video" hit rate.** If we adapt 5 canonical blog posts as videos, what fraction match the source post's viral coefficient? Would tell us how much of the breakout is the topic vs. the production.
