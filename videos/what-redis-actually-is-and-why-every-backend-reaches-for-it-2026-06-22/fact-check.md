# Fact check — what-redis-actually-is-and-why-every-backend-reaches-for-it

Script: `script.md` (checked 2026-06-22)
Verified: 18 · Partial: 4 · Unverified: 1 · Contradicted: 0

---

## ✅ Verified

### "Let's start in 2009. A developer named Salvatore Sanfilippo was running a small real-time analytics startup, and the database underneath it kept buckling under the load."
- Source: https://en.wikipedia.org/wiki/Salvatore_Sanfilippo
- Source says: Sanfilippo began Redis development in 2009 to scale his startup LLOOGG, a real-time web log analyser, after MySQL buckled under load.
- Recommendation: keep.

### "Redis stands for REmote DIctionary Server."
- Source: https://redis.io/docs/latest/develop/get-started/faq/
- Source says: Official Redis FAQ confirms the REmote DIctionary Server expansion verbatim.
- Recommendation: keep.

### "It keeps the entire dataset in memory, in RAM, instead of on disk."
- Source: https://redis.io/docs/latest/develop/get-started/faq/
- Source says: Redis is an in-memory data structure store; the primary data store is RAM.
- Recommendation: keep.

### "A plain cache like Memcached hands you back whatever string you put in. Redis hands you a toolbox."
- Source: https://redis.io/docs/latest/develop/get-started/faq/
- Source says: Redis stores lists, sets, sorted sets, hashes, and more — not just opaque strings like Memcached.
- Recommendation: keep.

### "Most commands finish in well under a millisecond."
- Source: https://redis.io/docs/latest/develop/get-started/faq/
- Source says: Redis operates on in-memory data, enabling sub-millisecond read and write latency.
- Recommendation: keep.

### "We have a name for this: single-threaded command execution. Modern versions do hand the network work to extra threads. But the data itself is always touched by one."
- Source: https://medium.com/@prashantgaur/redis-6-0-multithreading-myth-vs-reality-ea390fcf5be4
- Source says: Redis 6.0 introduced I/O threads for reading/writing network data; command execution remains single-threaded on the main thread.
- Recommendation: keep — the script's qualified framing ("single-threaded command execution" + caveat about I/O threads) is accurate and matches the substrate's own instruction to never say a flat "single-threaded."

### "A single instance can still push around a million operations a second."
- Source: https://medium.com/insiderengineering/scaling-redis-to-1m-ops-sec-architecture-sharding-techniques-and-best-practices-0fb1d4e2946e ; https://redis.io/blog/redis-82-ga/
- Source says: Redis 8.2 can exceed 1 million ops/sec on a single instance; pipelining enables 1M+ ops/sec on earlier versions too.
- Recommendation: keep (loose claim; well-supported).

### "You can count millions of unique visitors using about twelve kilobytes of memory."
- Source: https://redis.io/docs/latest/develop/data-types/probabilistic/hyperloglogs/
- Source says: HyperLogLog uses at most 12 KB of memory and achieves a standard error of 0.81%, regardless of cardinality.
- Recommendation: keep.

### "Twitter cached each home timeline as the last eight hundred tweet IDs in Redis, serving around thirty billion deliveries a day."
- Source: https://blogs.vmware.com/tanzu/case-study-staple-yourself-to-a-tweet-to-understand-30-billion-redis-updates-per-day/ ; https://www.slideshare.net/slideshow/raffi-krikorian-twitter-timelines-at-scale/24040648
- Source says: Twitter stored the last 800 tweet IDs per home timeline in Redis; Raffi Krikorian's QCon SF 2012 presentation describes ~30 billion timeline updates/day.
- Recommendation: keep.

### "Stack Overflow once took 5.8 billion cache hits in a single day, on two servers, each sitting under two percent CPU."
- Source: https://nickcraver.com/blog/2016/02/17/stack-overflow-the-architecture-2016-edition/
- Source says: Nick Craver's 2016 post records 5,831,683,114 Redis hits on February 9, 2016; ~160 billion ops/month; every instance below 2% CPU. Post was published Feb 17 2016.
- Recommendation: keep — numbers match precisely.

### "Instagram squeezed three hundred million entries into five gigabytes."
- Source: https://topic.alibabacloud.com/a/memory-saving-instagram-redis-practices_1_47_31899123.html ; https://gist.github.com/quiver/4967086
- Source says: Instagram used Redis hash bucketing to store ~300 million photo-to-user-ID entries in ~5 GB (vs ~21 GB naive), by encoding first 4 digits of the image ID as hash key with max 1,000 entries per hash.
- Recommendation: keep.

### "Pinterest held its entire follower graph — millions of users, billions of connections — in memory."
- Source: https://blogs.vmware.com/tanzu/using-redis-at-pinterest-for-billions-of-relationships/
- Source says: Pinterest stored its follower graph (millions of nodes, billions of edges) in Redis in-memory, sharded by user IDs.
- Recommendation: keep.

### "In 2016, a Cambridge computer scientist named Martin Kleppmann picked a fight with Redis's own creator."
- Source: https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html ; https://www.cst.cam.ac.uk/people/mk428
- Source says: Kleppmann published "How to do distributed locking" on February 8, 2016, critiquing Redlock; antirez (Sanfilippo) responded on February 9, 2016. Kleppmann was a PhD student and Research Associate at the University of Cambridge Computer Laboratory at the time.
- Recommendation: keep. "Computer scientist" is accurate; "Cambridge" is correct.

### "The question: is a Redis lock actually safe enough to trust?"
- Source: https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html
- Source says: Kleppmann argued Redlock lacks fencing tokens and is unsafe for correctness-critical applications; antirez disputed the analysis, arguing Redlock is safe for practical use cases.
- Recommendation: keep.

### "That same year, GitHub stayed down longer than it should have, because Redis had crept into its boot path. It did not cause the outage."
- Source: https://github.blog/2016-02-03-january-28th-incident-report
- Source says: January 28, 2016 — power disruption caused servers to reboot; GitHub's incident report states: "We had inadvertently added a hard dependency on our Redis cluster being available within the boot path of our application code." The root cause was a known firmware bug that prevented drives from being recognised after power-cycling. Redis was not the root cause.
- Recommendation: keep — factually correct. (See partial note below on "made recovery slow" framing.)

### "For its first fifteen years, Redis was open source."
- Source: https://en.wikipedia.org/wiki/Redis ; https://redis.io/blog/agplv3/
- Source says: Redis was released under the BSD license starting in 2009; the license changed to source-available (SSPL + RSALv2) in March 2024. 2009 to 2024 = 15 years.
- Recommendation: keep.

### "In 2024, the company behind it changed the license to something more restrictive, and the community revolted. Amazon, Google, and Oracle took the last open version and forked it into a new project called Valkey, run by the Linux Foundation."
- Source: https://www.linuxfoundation.org/press/linux-foundation-launches-open-source-valkey-community ; https://www.infoq.com/news/2024/03/redis-license-open-source/
- Source says: Redis Ltd. changed to SSPL + RSALv2 dual license in March 2024; Linux Foundation announced Valkey on March 28, 2024, backed by AWS, Google Cloud, Oracle, Ericsson, and Snap, forking from Redis 7.2.4.
- Recommendation: keep.

### "And in 2025, Redis reversed course and shipped under a fully open-source license once more."
- Source: https://redis.io/blog/agplv3/ ; https://www.infoq.com/news/2025/05/redis-agpl-license/
- Source says: Redis 8.0 released May 1, 2025 with AGPLv3 as an additional OSI-approved license, alongside SSPL and RSALv2 (tri-license model).
- Recommendation: keep — "fully open-source license" is accurate in that AGPLv3 is OSI-approved; the script does not claim it dropped the other licenses, so "shipped under a fully open-source license" is fair.

### "Salvatore, who had stepped away back in 2020, came back at the end of 2024."
- Source: https://redis.io/blog/welcome-back-to-redis-antirez/ ; https://www.theregister.com/2020/06/30/redis_creator_antirez_quits/
- Source says: Sanfilippo announced stepping down as maintainer on June 30, 2020; he returned in December 2024 as Redis evangelist.
- Recommendation: keep.

---

## ⚠️ Partial

### "Redis runs your commands on a single thread, one after another."
- Source: https://dev.to/deepin/is-redis-really-single-threaded-a-comprehensive-analysis-from-source-code-perspective-211
- Source says: Command execution is single-threaded; since Redis 6.0, background threads also handle persistence (RDB snapshots, AOF rewrites) and lazy deletion — not just I/O. The script correctly qualifies this a few sentences later ("Modern versions do hand the network work to extra threads"), so the overall paragraph is accurate when read together.
- Delta: The initial unqualified sentence ("Redis runs your commands on a single thread") is strictly true for command execution, but a reader could misread it as "Redis is entirely single-threaded" before the qualifier arrives. The qualifier does arrive promptly in the same paragraph.
- Recommendation: The script handles this well with the explicit qualifier. No change required, but the proximity of the qualification could be tightened if desired.

### "That same year, GitHub stayed down longer than it should have, because Redis had crept into its boot path. It just made recovery slow."
- Source: https://github.blog/2016-02-03-january-28th-incident-report
- Source says: Redis was a *blocking* dependency — app servers could not start at all without Redis being available, not merely slower. The incident report says: "We had inadvertently added a hard dependency on our Redis cluster being available within the boot path of our application code." The outage lasted ~2 hours 6 minutes. Redis did not cause it; power disruption + firmware bug did.
- Delta: "Made recovery slow" understates the situation. Redis didn't merely slow recovery — it blocked application servers from starting. "Made recovery slow" is technically not wrong (recovery was slow as a result), but it elides the hard dependency.
- Recommendation: Soften to "it blocked the recovery" or "it had become a hard dependency in the boot path, so nothing could start until Redis came back up." The current phrasing is not false but is misleadingly mild.

### "The background job systems you already lean on, like Sidekiq and BullMQ, are really just Redis underneath."
- Source: https://github.com/sidekiq/sidekiq ; https://github.com/taskforcesh/bullmq
- Source says: Both Sidekiq and BullMQ use Redis as their backend queue store. However, Sidekiq 7+ introduced a built-in SQLite-backed storage option alongside Redis, and BullMQ also supports alternative backends. The core claim — that they rely on Redis — is correct for the dominant default.
- Delta: The word "just" slightly overstates the exclusivity; both now have Redis alternatives, though Redis remains the default and dominant backend.
- Recommendation: Soften to "lean heavily on Redis" or "were built on Redis" to avoid implying there is no alternative at all.

### "The big cloud providers were selling Redis as a paid service without giving much back."
- Source: https://www.missioncloud.com/blog/redis-licensing-change-what-aws-customers-need-to-know ; https://www.infoq.com/news/2024/03/redis-license-open-source/
- Source says: This is Redis Ltd.'s stated rationale and is widely reported. It is a characterisation, not a falsifiable fact — it is the company's perspective, not an independently verified accounting of cloud provider contributions.
- Delta: Framing is accurate as a characterisation of the dispute but is one-sided. No source contradicts it as a summary of why the change was made.
- Recommendation: Keep as written — it accurately reflects the public rationale. No change needed for a scripted explainer.

---

## ❌ Unverified

### "You can ask which scooters are within a mile of someone on a street corner, because Redis can index points on a map."
- Searched: "Redis geospatial index" "GEOSEARCH command" "Redis geo radius"; "Redis geo scooter example"
- Result: Redis does have geospatial indexing (GEOADD, GEOSEARCH commands) — that part is well-documented. The specific scooter-proximity example is an illustrative analogy, not a reported real-world case. No source names an actual scooter company using Redis geo commands for this exact use case.
- Recommendation: Keep as an illustrative example (it accurately demonstrates the capability); no citation needed since it is presented as a hypothetical, not a named case study. No change required.

---

## 🚫 Contradicted

*(none)*
