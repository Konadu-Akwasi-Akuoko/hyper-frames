# How rate limiting works: token bucket vs leaky bucket — substrate notes

Runtime target: **7 min · ~1190 words** · **system-design style** (mechanism + comparison + real production systems + the motivating stakes). Seed: ByteByteGo "Rate Limiter System Design" (youtu.be/YXkOdWBwqaA, ~72k). Confidence tags: (high) sourced to a primary doc/RFC/postmortem, (med) widely reported, secondary.

Verification: substrate built from an 8-dimension research fan-out + 36-claim adversarial fact-check (32 confirmed / 4 partial / 0 refuted). Corrections baked in below.

## Named concepts

### The two buckets (the spine)
- **Token bucket** — a bucket of fixed capacity `b` tokens, refilled at a steady rate `r` (one token every 1/r seconds, capped at `b`). Each request spends a token; empty bucket → request rejected (HTTP 429). Idle time accumulates tokens, so it **allows bursts up to the bucket depth** while pinning the long-run average to `r`. Two clean knobs: **sustained rate** (refill `r`) and **burst size** (capacity `b`). Forwards a conforming request *immediately* — no added delay. (high — Wikipedia/Token_bucket, Go x/time/rate, Stripe, AWS)
- **Leaky bucket — TWO formulations** (the analytic edge over the seed, which only shows the queue):
  - **As a queue (traffic shaping)** — a FIFO buffer; requests pour in, drain out at a *fixed* rate. Smooths bursty input into a **perfectly constant** output stream; accepted requests may be **delayed/queued**. Overflow when the buffer is full → dropped. This is the canonical "bucket with a hole" picture. (high — Nginx limit_req, Wikipedia/Leaky_bucket)
  - **As a meter (policing)** — a counter *outside* the traffic path that increments per request and leaks at a fixed rate; immediate accept/reject, **no queue, no delay**. (high — Wikipedia/Leaky_bucket, GCRA)
- **Duals / mirror images** — the leaky-bucket-*as-meter* and the token bucket are the **same algorithm run two ways**: one counts down from a ceiling and refills up, the other counts up to a ceiling and leaks down. Given equivalent parameters they admit the *exact same* sequence of requests. The "mirror image" framing is accurate **only** for the meter form, not the queue form. (high — Wikipedia)
- **Burst limit vs rate limit** — token bucket's two knobs, exposed cleanly by AWS API Gateway: *rate* = tokens added per second (steady-state); *burst* = bucket capacity (the momentary spike ceiling). (high)
- **GCRA (Generic Cell Rate Algorithm)** — the ATM-network formalization of the leaky-bucket-as-meter; tracks a "not-before" timestamp instead of a draining counter, so it needs no background drain worker. The form many Redis limiters actually use. *Keep light — no tau arithmetic in script (the τ worked number was not sourced).* (med)

### The other algorithms (depth nod, not the spine)
- **Fixed window counter** — one integer per key per clock-aligned window; reset at the boundary. **Flaw: the boundary burst** — full limit just before the reset + full limit just after = **2× the limit** in a span far shorter than a window. (high — Cloudflare)
- **Sliding window log** — store a timestamp per request (e.g. Redis sorted set), count those inside the trailing window. Exact, but **memory-heavy** — ~1000 stored timestamps for a key doing 1000 req/min. (high)
- **Sliding window counter** — keep just two numbers (previous + current window), weight the previous window by how much of it is still in view. Cloudflare's practical compromise. (high)

### The stakes vocabulary (why the gate exists)
- **Retry storm** — clients/services retry a struggling dependency, and the retry traffic itself keeps it saturated, turning a transient blip into a multi-hour outage. (high — AWS)
- **Retry amplification** — in a 5-deep stack each retrying 3×, load multiplies layer by layer (3→9→27…): the database sees **~243×** the original load. (high — AWS Builders' Library)
- **Congestive collapse** — so much queued/retried work the system can't make forward progress; throughput falls toward zero. AWS used this exact term in the Oct 2025 postmortem. (high)
- **Noisy neighbor** — one tenant without per-tenant limits starves the rest (triples p99, exhausts the shared connection pool). (high)
- **Load shedding** — deliberately dropping low-priority work near capacity so critical work survives; the last-resort sibling of rate limiting. (high — Stripe)
- **Defense in depth / first gate** — rate limiting sits at the edge, before auth, logic, and the DB. (high)
- **429 Too Many Requests + Retry-After / X-RateLimit-*** — the standard client-facing contract; HTTP 429 was defined in **RFC 6585 (2012)**. (high)

## Real dated incidents
- **1986** — Jonathan S. Turner first describes the **leaky bucket** (the meter form), "New directions in communications", IEEE Communications Magazine 24(10):8–15. *Correction from fact-check: Turner is credited with the LEAKY BUCKET specifically, NOT the token bucket. Do not attribute token bucket to Turner.* (high)
- **April 1996 / ITU-T I.371** — GCRA standardized for ATM traffic policing (ATM Forum TM 4.0). (high)
- **1999** — DiffServ token-bucket markers **RFC 2697 (srTCM)** and **RFC 2698 (trTCM)** formalize token buckets for IP traffic conditioning. (high)
- **2012** — **RFC 6585** defines HTTP **429 Too Many Requests**. (high)
- **Sept 20, 2015** — AWS **DynamoDB US-East** outage: a network blip made storage servers all re-fetch oversized membership lists; the metadata service fell behind, failed servers **retried relentlessly**, error rates hit **~55%**, ~5 hours, took down Netflix, Reddit, IMDb, Nest. AWS had to *pause* requests to cut retries. (high — aws.amazon.com/message/5467D2)
- **2016** — AWS adds **token-bucket retry limiting to its own SDK**: retries run freely while tokens remain, then only at a fixed rate. *The same algorithm we're explaining, used to stop the storm.* (high)
- **Aug–Oct 2023** — **HTTP/2 Rapid Reset** (CVE-2023-44487), an app-layer (L7) DDoS abusing stream-cancel cost asymmetry. Google mitigated a peak of **398 million requests/second** (~**7×** its prior 46M record); Cloudflare **201M rps**, AWS **155M rps**. Disclosed jointly Oct 10, 2023. (high — Google/Cloudflare blogs)
- **Apr 29 – Sept 2023** — **23andMe** credential-stuffing campaign ran undetected; rate-limiting failed because attackers **rotated thousands of IPs**. ~**14,000** accounts cracked directly → ~**5.5M** profiles exposed via DNA Relatives. UK ICO fined **£2.31M (June 5, 2025)**, citing inadequate login/rate-limiting controls. (high)
- **2023** — AWS ships **Lambda Recursive Loop Detection** after runaway cost loops (an S3-triggered Lambda writing back into the same bucket = infinite invocations, thousands of dollars). (med)
- **Oct 19–20, 2025** — AWS **US-EAST-1** outage: a DNS race emptied DynamoDB's endpoint record; the EC2 DropletWorkflow Manager hit **"congestive collapse"** under retry load and couldn't recover until engineers throttled incoming work. **~14.5 hours**, **140+ AWS services**, **6.5M+ Downdetector reports**. (high — aws.amazon.com/message/101925)

## Concrete numbers and figures
- **b = 10, r = 2/sec** — token bucket worked example: after idle, **10 requests fire instantly** (the burst); the 11th waits ~half a second for the next token; thereafter paced at 2/sec. Over a 10-second window the cap is r·T + b = **30** requests. (high — constructed from verified mechanics)
- **r·T + b** — the formal bound: max conformant requests in any window of length T. The +b term amortizes away, so the long-run average is pinned to `r`. (high)
- **Stripe** — token bucket; **100 requests/sec** live mode, **25/sec** sandbox; returns 429. Runs 4 layered limiters + 2 load shedders; reserves **20%** of fleet capacity for critical requests. (high — stripe.com/blog/rate-limiters, docs.stripe.com/rate-limits)
- **AWS API Gateway** — token bucket; default **10,000 RPS** steady-state + **5,000** burst per Region (most Regions; ~13 Regions default to 2,500/1,250). (high, with fact-check caveat)
- **Nginx limit_req** — leaky bucket *as a queue*; rate e.g. `10r/s` = leak one request every **100 ms**; `burst` sets the queue depth; excess is delayed then rejected (503, often reconfigured to 429). (high)
- **Shopify REST Admin** — calls itself "leaky bucket": **40-request** bucket, leak **2/sec** (standard); **400** / **20/sec** (Plus). *Gotcha: it actually behaves like a credit-counter / token bucket — allows bursts up to bucket size, executes immediately, no queue.* (high — shopify.dev)
- **GitHub REST API** — fixed quota: **5,000 req/hour** authenticated, **60/hour** unauthenticated, + secondary limits (≤100 concurrent). Explicitly "to prevent abuse and denial-of-service". (high)
- **Discord** — **50 req/sec** global per bot + per-route buckets; 429 + Retry-After. (high)
- **Slack** — tier-based per-method per-minute; 429 + Retry-After. (high)
- **Cloudflare sliding window counter** — `rate = previous·((period−elapsed)/period) + current`; worked: 42·0.75 + 18 = **49.5** against a 50 req/min limit. Validated over **400 million requests / 270,000 sources**: only **0.003%** miscategorized, mean error **6%**. (high)
- **Fixed window boundary burst** — **2× the limit** (e.g. 100 at 12:00:59, 100 at 12:01:00). (high)

## Named people and organizations
- **Jonathan S. Turner** — first described the leaky bucket (1986); the origin point. (high)
- **Stripe** — published the canonical engineering account of production token-bucket rate limiting ("Scaling your API with rate limiters"). (high)
- **Cloudflare** — published the sliding-window-counter approximation + its 400M-request validation. (high)
- **AWS** — both the cautionary tale (2015/2025 retry-storm outages) and the fix (token-bucket SDK retries, 2016). (high)
- **Nginx, Shopify, GitHub, Discord, Slack** — the concrete "where these live in the wild" roster. (high)

## Load-bearing moments
- **The invisible gate is personal.** Every viewer has hit "429 / you're doing that too much / slow down." That wall *is* a rate limiter. Opening + closing on it is the personal-context bridge. — without it the algorithms float free of the viewer.
- **The twist: there are two leaky buckets.** The seed glosses this; it's the single most clarifying fact in the topic. The queue *smooths and delays*; the meter *rejects immediately* and is the **mirror image of the token bucket**. This is the synthesis the whole comparison turns on. — if cut, the video is just another five-algorithm list.
- **The recursion: AWS uses a token bucket to stop the retry storm that took it down.** The algorithm in the gate is the same algorithm that fixes the outage. — the closing loop that makes it land.

## SEO context
- Bias the working title toward the searchable nouns: **rate limiting / system design / token bucket / leaky bucket** (the promoted title already nails all four). Autocomplete pull: "rate limiting algorithms", "rate limiter leaky bucket", "rate limiting vs throttling", "sliding window".
- Saturation: 0 flagged, but the **"design a rate limiter INTERVIEW"** framing is everywhere (7/30 videos >100K). Differentiate as a clean *mechanism* explainer with real production numbers and the two-leaky-buckets twist — not interview drills.
- The Redis-rate-limiting video is the runaway (3.0M views) — viewers care about real implementation; the Stripe/AWS/Nginx concrete numbers feed that appetite. Hook-time is generous in this lane (heatmaps peak late), but we still cold-open hard.
