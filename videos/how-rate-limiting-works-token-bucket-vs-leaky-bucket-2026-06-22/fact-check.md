# Fact check — how-rate-limiting-works-token-bucket-vs-leaky-bucket

Script: `script.md` (checked 2026-06-22)
Verified: 14 · Partial: 4 · Unverified: 1 · Contradicted: 1

---

## Verified

### "In 2023, Google absorbed a flood that peaked right there, around three hundred and ninety-eight million requests every second"
- Source: https://cloud.google.com/blog/products/identity-security/google-cloud-mitigated-largest-ddos-attack-peaking-above-398-million-rps/
- Source says: Google Cloud blog confirms the peak at "above 398 million rps" during the HTTP/2 Rapid Reset campaign in August 2023.
- Recommendation: keep.

### "an attack called Rapid Reset, and Cloudflare and Amazon were hit in the same wave"
- Source: https://cloud.google.com/blog/products/identity-security/google-cloud-mitigated-largest-ddos-attack-peaking-above-398-million-rps/ and https://blog.cloudflare.com/technical-breakdown-http2-rapid-reset-ddos-attack/
- Source says: Google, Cloudflare (201M rps), and AWS (155M rps) disclosed the attack jointly on October 10, 2023 under CVE-2023-44487.
- Recommendation: keep.

### "In 2015, one of these took Amazon's DynamoDB down for about five hours, with more than half of all requests failing"
- Source: https://aws.amazon.com/message/5467D2/
- Source says: The AWS postmortem states errors stabilized at approximately 55%, which is "more than half." Major disruption ran from ~2:13 AM to ~7:10 AM PDT on September 20, 2015 — approximately 4 hours 57 minutes, which rounds legitimately to "about five hours."
- Recommendation: keep.

### "dragging Netflix and Reddit dark with it"
- Source: https://www.itpro.com/infrastructure/363576/aws-outage-cuts-off-netflix-medium-reddit-and-others
- Source says: Netflix and Reddit (and others including Tinder, Airbnb, IMDb) were confirmed affected by the September 2015 DynamoDB outage.
- Recommendation: keep.

### "Five services deep, each retrying three times, and the database at the bottom sees two hundred and forty-three times the original load"
- Source: https://www.emergentmind.com/topics/retry-storms and https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
- Source says: 3 retries per hop across 5 hops = 3^5 = 243x amplification; this math is confirmed by multiple sources including the AWS Builders' Library, which describes the compounding retry load at each layer.
- Recommendation: keep.

### "There is even a name for the end state ... Congestive collapse. Amazon used that exact phrase in October 2025"
- Source: https://aws.amazon.com/message/101925/
- Source says: AWS's official postmortem uses the phrase "congestive collapse" — exact quote: "At this point, DWFM had entered a state of congestive collapse and was unable to make forward progress in recovering droplet leases."
- Recommendation: keep.

### "a fourteen-hour outage that took down more than a hundred and forty of its own services"
- Source: https://thundergolfer.com/blog/aws-us-east-1-outage-oct20 and multiple secondary analyses
- Source says: The outage affected exactly 140 AWS services; duration was over 14 hours (DynamoDB failed at 6:48 AM UTC Oct 20, EC2 recovered approximately 8:50 PM UTC — ~14 hours). The official AWS postmortem at aws.amazon.com/message/101925/ confirms congestive collapse and the scale.
- Recommendation: keep. Note: AWS's own postmortem says ~14.5 hours total; "fourteen-hour" is a fair round.

### "This is the gate Stripe runs on its API, capped near a hundred requests a second"
- Source: https://docs.stripe.com/rate-limits
- Source says: Stripe's live-mode global API rate limit is 100 requests per second per account; test/sandbox mode is 25/sec. The script says "capped near a hundred" which is accurate.
- Recommendation: keep.

### "the gate inside Amazon's API Gateway, ten thousand a second, with five thousand held in the bucket for a spike"
- Source: https://docs.aws.amazon.com/apigateway/latest/developerguide/limits.html
- Source says: Default account-level throttle quota is 10,000 RPS with a maximum token bucket capacity of 5,000 requests (most Regions; 13 named Regions default to 2,500/1,250).
- Recommendation: keep.

### "This is how the web server Nginx paces traffic. One request every hundred milliseconds, the rest waiting politely in line"
- Source: https://blog.nginx.org/blog/rate-limiting-nginx and https://nginx.org/en/docs/http/ngx_http_limit_req_module.html
- Source says: Nginx limit_req module uses the leaky-bucket algorithm; at 10r/s, NGINX processes one request every 100 ms. Excess requests queue (if burst is set) or are rejected.
- Recommendation: keep.

### "Shopify advertises a 'leaky bucket,' forty requests deep, leaking two a second. But it lets you spend all forty in one burst and runs each request immediately. That's a token bucket wearing a leaky bucket's coat."
- Source: https://shopify.dev/docs/api/admin-rest/usage/rate-limits
- Source says: Shopify confirms the REST Admin API bucket is 40 requests (standard), drains at 2/sec; crucially, "If there is available capacity in your bucket, then the request is executed without queueing or processing delays." Bursts up to the bucket size execute immediately — functionally a token bucket despite the "leaky bucket" label.
- Recommendation: keep.

### "Fire your whole limit in the last second of one minute, then your whole limit again in the first second of the next, and you've pushed double the rate through a seam the counter can't see"
- Source: https://blog.cloudflare.com/counting-things-a-lot-of-different-things/ and https://dev.to/animir/biased-fixed-window-rate-limiting-algorithm-explained-1d91
- Source says: The fixed-window boundary burst (2x the limit) is a well-documented, universally confirmed flaw, cited verbatim by Cloudflare in its sliding-window post.
- Recommendation: keep.

### "Cloudflare split the difference ... They checked it against the exact method across four hundred million real requests. It got the answer wrong three times in a hundred thousand."
- Source: https://blog.cloudflare.com/counting-things-a-lot-of-different-things/
- Source says: Cloudflare validated the sliding-window-counter approximation against the exact method on 400 million requests from 270,000 distinct sources; 0.003% of requests were miscategorized (3 in 100,000), zero false positives.
- Recommendation: keep.

### "In 2016, Amazon taught its own software to stop doing exactly that, by putting a token bucket on its retries"
- Source: https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/
- Source says: The AWS Builders' Library article explicitly states "AWS added this behavior to the AWS SDK in 2016," referring to token-bucket-based client-side retry throttling.
- Recommendation: keep.

---

## Partial

### "roughly seven times the worst it had ever seen"
- Source: https://cloud.google.com/blog/products/identity-security/google-cloud-mitigated-largest-ddos-attack-peaking-above-398-million-rps/
- Source says: Google's own blog says the attack was "7½ times larger" than the previous largest recorded DDoS (46 million rps in 2022), not "roughly seven times."
- Delta: Script rounds down to "roughly seven"; primary source says "7½ times." The exact math is 398/46 ≈ 8.65x, and Google's own text says 7½x (comparing the campaign, not the single-peak moment). Saying "roughly seven" understates the figure relative to the primary source's "7½."
- Recommendation: change "roughly seven times" to "roughly seven and a half times" or "more than seven times" to stay accurate without overstating.

### "Jonathan S. Turner first described the LEAKY BUCKET in 1986"
- Source: https://en.wikipedia.org/wiki/Leaky_bucket and https://en.wikipedia.org/wiki/Token_bucket
- Source says: Turner's 1986 IEEE Communications Magazine paper is cited under *both* the leaky bucket and token bucket Wikipedia articles, creating genuine scholarly ambiguity. Turner's mechanism — a counter that increments on packet arrival and decrements periodically, discarding non-conformant packets — is functionally the leaky-bucket-as-meter (policing form). However, secondary sources frequently attribute the *token bucket* to Turner as well, describing his mechanism as a "leaky-token bucket." The substrate notes acknowledge this ambiguity and correctly conclude Turner described the leaky bucket (meter form), not the token bucket. The script itself does not explicitly name Turner or attribute the 1986 origin to either algorithm, so there is no direct scriptual error — the substrate corrected itself before writing.
- Delta: No Turner attribution claim appears verbatim in the script voiceover. This is a substrate note risk that was handled correctly; no correction needed in script.
- Recommendation: No script change needed. Substrate-notes correction is already in place. If a "who invented this?" screen card is planned, ensure it credits Turner with the leaky bucket (meter form), not the token bucket.

### "more than half of all requests failing" (2015 DynamoDB outage)
- Source: https://aws.amazon.com/message/5467D2/
- Source says: Postmortem states errors "stabilized at approximately 55%." "More than half" is technically accurate (55% > 50%).
- Delta: The substrate notes this as ~55%; the script says "more than half." The script's phrase is a valid paraphrase that cannot be fact-checked as wrong, but it omits the precision that was available.
- Recommendation: keep as-is, or optionally sharpen to "more than half — around fifty-five percent" for the audience.

### "a single counter that resets every minute" (fixed window)
- Source: https://blog.cloudflare.com/counting-things-a-lot-of-different-things/
- Source says: The fixed-window period is configurable (could be 1 minute, 1 hour, etc.); "resets every minute" is used as an illustrative example, not a universal property.
- Delta: The script uses "minute" as the canonical example, which is the most common illustration in the literature and not a wrong claim, but it is a simplification. The vulnerability applies equally to any fixed window length.
- Recommendation: keep as a pedagogical example; the claim is not factually wrong.

---

## Unverified

### "In 2016, Amazon taught its own software to stop doing exactly that, by putting a token bucket on its retries. Free to retry while there are tokens, then strictly paced once they run out."
- Note: The year 2016 is confirmed by the AWS Builders' Library (see Verified section). However, the specific behavioral detail "free to retry while there are tokens, then strictly paced once they run out" describes the standard-mode retry quota behavior. The Builders' Library describes it as failing fast (returning errors, not pacing) once the bucket empties — not "strictly paced." The distinction is: when tokens are exhausted the SDK returns an error immediately rather than throttling the rate. The "strictly paced" phrasing implies a rate-limiter queuing behavior that is more accurately described as an error-fast circuit-breaker.
- Searched: "AWS SDK retry quota token bucket behavior empty bucket" and AWS Builders' Library and AWS SDK retry docs.
- Result: No source confirms "strictly paced once they run out"; sources indicate the SDK returns errors (fails fast) when the token bucket is empty, rather than pacing retries at a reduced rate.
- Recommendation: Soften to "free to retry while there are tokens, then blocked — the SDK returns the error immediately rather than waiting through more retries." The underlying 2016 date and token-bucket mechanism are verified; only the "strictly paced" characterization overstates how smoothly the throttle works.

---

## Contradicted

### "roughly seven times the worst it had ever seen"
- Source: https://cloud.google.com/blog/products/identity-security/google-cloud-mitigated-largest-ddos-attack-peaking-above-398-million-rps/
- Source says: Google's primary blog post states "7½ times larger," not "roughly seven times." Previous record was 46 million rps (2022). 398/46 ≈ 8.65x at the single-peak level; Google chose "7½" for the overall campaign comparison.
- Recommendation: Correct to "roughly seven and a half times" or "more than seven times." As written, "roughly seven" is in direct conflict with the primary source that says "7½."
