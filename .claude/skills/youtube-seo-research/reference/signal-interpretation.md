# Signal interpretation

How to read each section of the SEO research digest, and when to ignore it.

## `top_nouns`

The top-frequency content nouns across the top-N video titles, after stopwords are dropped. Tells you what searchable anchor your title needs to carry.

- **Use when:** picking the searchable noun for a paired YouTube title or working title H1. At least one of the top 3 should appear in any title that wants search reach.
- **Ignore when:** the top noun is the literal topic phrase you already used (it's just confirming you got the keyword right). Look at #2 and #3 for the secondary anchor.
- **Don't trust** counts under 3. With a 30-video corpus, a count of 1–2 is noise.

## `demand_phrases`

Autocomplete suggestions that surfaced in 3+ adjacent letter expansions. These are real, recurring queries — what people actually type into YouTube's search bar.

- **Use when:** picking the title's exact phrasing. A demand phrase that fits naturally is gold — it's the literal query that brings viewers.
- **Ignore when:** the list is empty (sparse niche; autocomplete returned little). Empty is informative — it means you're early in the niche, and the searchable-noun strategy from `top_nouns` matters more.

## `saturation_warnings`

3-to-6-word patterns that appear in 3+ recent (last 18 months) high-view (>100K) videos. Tells you which framings the niche has already collapsed onto.

- **Use when:** sanity-checking a draft title. If your title matches a saturation pattern verbatim, you're competing head-on with established incumbents.
- **Differentiate** the pattern, OR commit to the lane only if your thumbnail claim is genuinely sharper than the incumbents'. The script's iceberg-arc reframing is a structural way to differentiate even when the topic is saturated.
- **Ignore when:** the warning's `match_count` is exactly 3 and the niche is small — could be coincidence. Treat 5+ matches as a hard signal.

## `hook_patterns`

Median peak-position and intensity-at-T-seconds across videos that returned heatmap data (the most-replayed segments).

- **Use when:** drafting beat 1 of the script (the open). The peak position tells you the budget for getting viewers hooked before they drop off — usually 8–15s for top performers.
- **Use when:** scoping the open + subversion combined. If `median_intensity_at_15s` is below 0.6, top performers are already losing 40% of viewers by 15s — your open + subversion together must finish before then.
- **Ignore when:** `hook_patterns` is `null` (fewer than 5 videos in the corpus had heatmap data — happens for low-view niches).

## The saturated-keyword trap

The biggest failure mode of any keyword research workflow: the data tells you "demand exists for phrasing X", you adopt phrasing X, and you compete head-on with a 2M-view incumbent that already owns it.

The signal is telling you **demand exists**, not **that exact phrasing will win for you**. Use the research to find the **adjacent under-served phrasing** — long-tail demand phrases with no saturation warning attached — and pair that with a thumbnail or script angle that claims something the incumbents don't.

## When to ignore the digest entirely

- The corpus is empty or near-empty (`top_videos: []` or 1–2 entries). The niche doesn't exist on YouTube yet, or your topic phrasing is too unusual to surface results. Try a related broader phrasing.
- All signals are empty AND the topic is one you know is searched-for. The autocomplete pass likely 429'd — check `autocomplete: null` in the JSON and re-run with `--force` later.
- You have a strong editorial reason to use a phrasing the data discourages. Editorial taste beats SEO when the trade-off is real (e.g., the channel's voice).
