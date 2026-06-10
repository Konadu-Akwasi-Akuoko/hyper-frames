# Consumer integration

How other skills consume `<video-dir>/seo/research.json` via the shared hook pattern.

## The hook (3 steps)

Any skill that benefits from SEO context follows this hook at its decision point:

1. **Probe** for `<video-dir>/seo/research.json`.
2. **Missing** → invoke the `youtube-seo-research` skill via the `Skill` tool, with one-line user confirmation. If the user declines, proceed without it. **Never block on missing data.**
3. **Present** → load it. Read the fields the consumer skill cares about (see field map below). Optionally surface a consumer-specific compressed digest at the consumer's decision point.

The full canonical 5-line digest is printed once by `youtube-seo-research` when it runs. Consumer-specific digests are compressed reminders printed at consumer decision moments (e.g., thumbnail-and-title-generator's title-pairing step) that may happen hours or days after the original research.

## Field map per consumer

| Consumer | Decision point | Fields used |
|---|---|---|
| `script-writer` | Step 2.5 (research checkpoint) + Step 3 (outline) | `signals.top_nouns` (working title), `signals.saturation_warnings` (framing), `signals.hook_patterns` (beat 1 budget), `top_videos[].chapters` (coverage check) |
| `thumbnail-and-title-generator` | Step 2 (probe) + Step 4 (paired title) | `signals.top_nouns`, `signals.demand_phrases`, `signals.saturation_warnings`, `top_videos[].upload_date` (recency context) |

## Adding a new consumer

1. Identify the decision point in the consumer skill's flow — the moment a SEO-aware decision is being made.
2. Add the probe + invoke-or-fall-back at that point. Use the same prompt shape: "No SEO research found. Run it now via the youtube-seo-research skill (~25s)? [Y/n/skip]". On Y, invoke `youtube-seo-research` via the `Skill` tool.
3. Document which fields you read in this table.
4. Decide whether to print a consumer-specific compressed digest at your decision point, or rely on the canonical digest the youtube-seo-research skill prints at fetch time. Print one if your decision point is plausibly hours/days after the original research (the user has likely forgotten the digest).

## Hard rules for consumers

- **Never block on missing data.** If the user declines to run research, the consumer skill must still complete its job using its existing logic.
- **Never invent signals.** Only read what's in the JSON. Empty arrays mean empty — don't fabricate signals to fill the digest.
- **Re-run only via the youtube-seo-research skill.** Never edit `seo/research.json` directly. Consumer skills consume; they don't write.
