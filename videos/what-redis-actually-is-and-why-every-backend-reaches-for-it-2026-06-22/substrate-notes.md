# What Redis actually is and why every backend reaches for it — substrate notes

Runtime target: 7 min · ~1190 words · audience: working backend developers
Source idea: studio.db `9578ceae` (kind: long) · seed: pawel_code_stuff "Redis will finally make sense after this video"
All facts below are workflow-verified (52 verified / 10 partly-corrected / 1 refuted). Draft ONLY from this file.

## Named concepts
- REmote DIctionary Server — the name; official FAQ calls it an acronym verbatim. A networked dictionary (keys→values).
- In-memory data structure store — whole dataset kept in RAM, not on disk. Sub-millisecond reads.
- Data structure server — the twist: stores lists, sets, sorted sets, counters, streams — not just opaque strings (vs Memcached, a plain string cache, no persistence).
- Single-threaded command execution — commands run one-at-a-time on one thread → atomic, no locks. QUALIFY: only command execution; 6.0+ uses extra threads for I/O. Never a flat "single-threaded".
- The structures = the win — sorted set → leaderboard; counter → atomic increment; HyperLogLog → millions of uniques in ~12 KB; bitmap → 1 bit/user/day; stream → durable log.
- Cache-aside (look-aside) — app reads Redis first, on a miss loads the DB and writes back with a TTL. The dominant reason backends adopt it.
- The multi-tool thesis — one server = cache + sessions + rate limiter (INCR) + job queue (Sidekiq/BullMQ) + pub/sub + distributed locks.
- Durability is tunable, never strong — snapshots (lose minutes) OR append-only log (lose ~1s); async replication → failover can drop acknowledged writes. Pub/Sub is fire-and-forget (lost if no listener); Streams retain history.
- The license arc — open source (BSD) 2009→2024; March 2024 → source-available (more restrictive, not open source); Redis 8 (May 2025) re-added an OSI-approved open-source license. 2018/2019 changes touched only modules, never core.

## Real dated incidents
- 2009 — Salvatore Sanfilippo (antirez) builds Redis to scale his real-time-analytics startup LLOOGG after MySQL buckled. (Don't pin an exact day; "April 10" is unsourced. Just "2009".)
- 2012 — Twitter: home timeline = last 800 tweet IDs cached in Redis; ~30 billion timeline deliveries/day (Raffi Krikorian, QCon SF 2012).
- 2016 — Stack Overflow: 5.8 billion Redis cache hits in ONE day (Feb 9), 2 servers, each <2% CPU (Nick Craver).
- 2016 — Martin Kleppmann (Cambridge) vs antirez public dispute over whether Redlock distributed locks are safe (Feb 8 / Feb 9).
- 2016 — GitHub outage (Jan 28): Redis had crept into the boot path → slowed recovery. Redis was the amplifier, NOT the root cause (power + firmware bug were).
- 2020 — antirez steps back as maintainer.
- 2024 — license changed to source-available (March); AWS + Google + Oracle fork the last open version into Valkey under the Linux Foundation (March 28); antirez rejoins Redis (Dec).
- 2025 — Redis 8 (May 1) re-adds an OSI-approved open-source license; ships antirez's Vector Sets.

## Concrete numbers and figures
- 2009 — year created (do NOT imply 2008).
- sub-millisecond — typical command latency (in-memory).
- ~1 million ops/sec — single instance with pipelining (FAQ); keep loose, hardware-specific.
- ~12 kilobytes — count millions of unique items (HyperLogLog).
- 800 tweet IDs / ~30 billion/day — Twitter home-timeline cache (2012).
- 5.8 billion hits / 2 servers / under 2% CPU — Stack Overflow single day (2016).
- 300 million entries in 5 gigabytes — Instagram via hash bucketing (~2011).
- ~1 second vs a few minutes — data loss: append-only log vs periodic snapshot.

## Named people and organizations
- Salvatore Sanfilippo (antirez) — Italian programmer; created Redis (2009); designed the single-thread event loop; authored Redlock; stepped back 2020; rejoined Dec 2024.
- LLOOGG — his startup; the MySQL scaling pain that birthed Redis.
- Redis Ltd. — stewards Redis; made the 2024 license change and 2025 reversal.
- Martin Kleppmann — Cambridge CS; "Designing Data-Intensive Applications"; the Redlock critic.
- Linux Foundation + AWS, Google, Oracle — back the Valkey fork.
- Twitter / Stack Overflow / Instagram / Pinterest — named at-scale adopters.

## Load-bearing moments
- The single-thread paradox — the thing under millions of requests does one command at a time, on purpose. Widest expectation-vs-reality gap; the spine and the hook.
- "Reach for the RIGHT structure" — reframes Redis from cache to data-structure server; the payoff beat for a backend audience.
- One dependency collapses six infra pieces — the literal thesis of "why every backend reaches for it," proven by named adopters.
- Tunable-but-never-strong durability — the honest counterweight that defuses "is it a database?".
- The 2024→2025 license whiplash — the fresh, current-events cliffhanger that makes a 2026 video worth watching (incumbents predate it).

## SEO context (seo/research.json, 2026-06-22)
- Anchor title on `redis` + a concept noun: `database` / `caching` are the demand-backed seconds; cache-vs-database tension doubles as the spine.
- Differentiate on FORMAT: the lane is saturated with `course` / `crash` / `tutorial` long-form; a tight conceptual explainer stands apart. Zero saturation patterns; incumbents are old (median ~2.9 yr) — the license saga is untouched territory.
- Hook budget: incumbents are long (peak replay ~319s) with modest early hold (~14% at 5s) → land a concrete beat inside the first ~10 seconds.
