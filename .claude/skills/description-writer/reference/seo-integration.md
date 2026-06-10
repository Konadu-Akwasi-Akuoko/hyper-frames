# SEO integration

Which fields of `<video-dir>/seo/research.json` drive which part of
the description, and how to use them without contortion.

## The probe contract

Identical to `script-writer` and `thumbnail-and-title-generator` — see
`.claude/skills/youtube-seo-research/reference/consumer-integration.md`
for the canonical hook. Three rules carry over verbatim:

- **Never block on missing data.** If the user declines or research
  was never run, the description still ships using fallback logic
  (ask for 3 nouns at the hashtag step; skip the noun-rotation
  discipline in the explainer).
- **Never invent signals.** Read only what's in the JSON. Empty
  arrays mean empty.
- **Re-run only via the `youtube-seo-research` skill.** This skill
  consumes; it never edits `seo/research.json`.

## Field map for this skill

| Step | Field | How it's used |
|---|---|---|
| 6 — Explainer | `signals.top_nouns[:3]` | All three nouns must appear verbatim in the explainer, naturally placed. These are what earns the YouTube search match. |
| 6 — Explainer | `signals.demand_phrases[0]` | The top demand phrase, included only if it fits without contortion. Optional polish. |
| 7 — Hashtags | `signals.top_nouns[:3]` | The three hashtags. Same nouns as the explainer, but CamelCased and prefixed with `#`. |

Other fields (`saturation_warnings`, `hook_patterns`, `top_videos`)
are not used directly here — they shaped the script's framing
upstream in `script-writer`. By the time this skill runs, those
choices are baked into the script and don't need re-applying.

## Noun-rotation discipline (Step 6)

Take the top 3 nouns from `signals.top_nouns[:3]`. Place each one
naturally in the explainer body — not as a keyword stuffing run, but
as the words you'd naturally use to describe the video.

Captchas example (top nouns: `captcha`, `recaptcha`, `google`):

> This video walks through how three generations of **CAPTCHA** were
> each broken in turn — distorted text, image grids, and the
> invisible behavioral scoring that runs underneath **reCAPTCHA** v3,
> hCaptcha, and Cloudflare Turnstile today. It's the story of a wall
> that keeps getting taller, and machines that keep learning to
> climb it — from a 1997 trick that held for a decade, to **Google**'s
> image grids quietly training self-driving cars, to a GPT-4 model
> that hired a human on TaskRabbit to solve the CAPTCHA for it.

Each top noun is in there once, in lowercase or proper case as the
sentence demands. The bolding is for illustration — never bold in
the actual description.

If a top noun is a stop-word-ish duplicate (e.g., `work` is in the
captchas top-nouns at position 2 because the autocomplete queries
were "how captcha **work**"), skip it and use position 4 instead.
The rotation only matters for nouns that are actual topic anchors.

## Demand phrase placement

The top `signals.demand_phrases[0]` is usually a literal user search
("how captcha works"). If it fits as a clause in the explainer's
first paragraph, include it verbatim — YouTube's search loves exact
matches. If forcing it reads awkwardly (the captchas top demand
phrase is "how to work on 2captcha", which is irrelevant to the
video's actual content), drop it.

A demand phrase is a polish move, not a requirement. The top-3 nouns
are the requirement.

## Hashtag derivation

```
signals.top_nouns[:3]  →  ['captcha', 'work', 'recaptcha']
                          ↓ skip stop-word-ish
                          ['captcha', 'recaptcha', 'google']
                          ↓ CamelCase, prefix #
                          ['#Captchas', '#Recaptcha', '#Google']
```

Pluralize the first noun if the topic is naturally plural
(`#Captchas` not `#Captcha`). The third hashtag often pulls from
`top_nouns[3]` rather than `top_nouns[2]` because the second
position is frequently a generic word like `work` or `online`.

## Fallback when SEO data is absent

If `seo/research.json` is missing and the user declined to run
research:

- **Explainer:** write it naturally without enforced noun rotation.
  The video's actual topic words appear because they're what the
  video is about — that's good enough.
- **Hashtags:** at Step 6, ask the user once: "Give me 3 topic
  nouns for the hashtags." Apply the same CamelCase rule. Cache the
  answer for any iteration in the same session.

Never invent SEO signals to fill the gap. Never write a hashtag like
`#Tutorial` or `#Explained` to pad the count — exactly 3 topic
nouns, not generics.

## When SEO signals conflict with the script

If the top nouns include a word that the script deliberately doesn't
use (e.g., the script reframes "captcha" as "the test" throughout),
prefer the script's wording in the explainer body but keep the SEO
noun in **one** sentence so the search match still lands. The
explainer is the place to make that compromise — the hook stays
true to the script's voice.
