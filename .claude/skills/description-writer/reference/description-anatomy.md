# Description anatomy

The 5-section structure, in fixed order, with the captchas video
(`videos/how-does-captchas-work-2026-05-10/`) as the worked example.

Total target: 1500–3500 chars. Hard cap: 5000.

## Section 1 — Hook (~145 chars)

YouTube's feed card collapses the description to roughly the first
145 characters (varies a bit by surface — mobile feed vs. watch page).
The hook is what earns the "show more" tap. Lift it from the
script's strongest curiosity-gap line — usually Beat 2's subversion
sentence, occasionally Beat 1.

Rules:

- Single paragraph, no bullet, no emoji, no markdown.
- Reads as a hook, not a teaser. Bans: "In this video we explore",
  "Today we'll talk about", "Have you ever wondered", "Welcome back".
- Present tense or rhetorical question form. Active voice.
- Rewrite for written prose: drop spoken hedges ("you know", "kind
  of"), sharpen the verb, cut filler.

Captchas example (138 chars):

> The "I'm not a robot" checkbox doesn't actually test you when you
> click it. The test happens in the seconds before — and you don't
> see any of it.

## Section 2 — Explainer (1–2 short paragraphs)

What the video is about, why it matters, what specific angle it
takes. This is the section that earns the watch — once the hook gets
the expand, the explainer gets the play.

Rules:

- 1–2 short paragraphs. Each paragraph ≤ ~3 sentences.
- Must contain `signals.top_nouns[:3]` verbatim if SEO data was
  loaded — these are the searchable nouns (see
  `seo-integration.md`).
- May include the top `signals.demand_phrases` entry if it fits
  naturally. Drop it if forcing the phrase reads awkwardly.
- Names the video's specific angle — the thing this video does that
  generic "how CAPTCHAs work" videos don't.

Captchas example (~350 chars; top nouns: `captcha`, `recaptcha`,
`google`):

> This video walks through how three generations of CAPTCHA were each
> broken in turn — distorted text, image grids, and the invisible
> behavioral scoring that runs underneath reCAPTCHA v3, hCaptcha, and
> Cloudflare Turnstile today.
>
> It's the story of a wall that keeps getting taller, and machines
> that keep learning to climb it — from a 1997 trick that held for a
> decade, to Google's image grids quietly training self-driving cars,
> to a GPT-4 model that hired a human on TaskRabbit to solve the
> CAPTCHA for it.

## Section 3 — Chapters

Format:

```
Chapters
0:00  Intro
2:05  How distorted-text CAPTCHAs broke
3:18  Image grids and the self-driving training pipeline
4:34  Invisible behavioral scoring (reCAPTCHA v3)
…
```

Rules:

- Plain text header "Chapters" — no `#`, no `##`.
- One chapter per beat in narration order, with Beat 6's cycles
  expanded into one chapter per cycle.
- Timestamp format: `M:SS` (or `MM:SS` past 9:59). Two spaces between
  timestamp and label.
- Labels rephrase the beat heading as imperative-ish or descriptive
  ("Intro" not "Familiar-action open"). Keep under ~50 chars.
- `0:00` is mandatory — YouTube requires it for chapter UI to render.
- Never round to 30s buckets; always use the real word's start time
  from `transcript.json`.

## Section 4 — Sources & further reading

Format:

```
Sources & further reading
• The Turing Test (1950) — Alan Turing: https://academic.oup.com/mind/article/LIX/236/433/986238
• Solving Google's reCAPTCHA v2 with YOLO (2024) — ETH Zurich: https://arxiv.org/abs/2409.08831
• GPT-4 System Card (TaskRabbit incident, 2023) — OpenAI: https://cdn.openai.com/papers/gpt-4-system-card.pdf
• …
```

Rules:

- One source per line, bullet character `•` (or `-` if `•` causes
  copy-paste issues). No markdown asterisks.
- Format: `<title or paper> — <attribution>: <URL>`. The em-dash
  separates title from attribution; the colon separates from URL.
- URLs on the same line; YouTube auto-links them.
- Soft cap 6 sources. Trim to 5 then 4 if length is over budget.

## Section 5 — Hashtags

Format:

```
#Captchas #Recaptcha #Bots
```

Rules:

- Exactly 3.
- Single line at the very end of the description.
- Space-separated.
- CamelCase multi-word tags. `#ImageRecognition`, not
  `#image-recognition` or `#image_recognition`.
- Derived from `signals.top_nouns[:3]` if SEO data present; otherwise
  ask the user for 3 topic nouns.

YouTube only renders the first 3 hashtags above the title bar. Any
extras are noise — exactly 3 is the discipline.

## Full assembled example shape

```
The "I'm not a robot" checkbox doesn't actually test you when you click it. The test happens in the seconds before — and you don't see any of it.

This video walks through how three generations of CAPTCHA were each broken in turn — distorted text, image grids, and the invisible behavioral scoring that runs underneath reCAPTCHA v3, hCaptcha, and Cloudflare Turnstile today.

It's the story of a wall that keeps getting taller, and machines that keep learning to climb it — from a 1997 trick that held for a decade, to Google's image grids quietly training self-driving cars, to a GPT-4 model that hired a human on TaskRabbit to solve the CAPTCHA for it.

Chapters
0:00  Intro
0:25  The test was never the checkbox
…

Sources & further reading
• The Turing Test (1950) — Alan Turing: https://...
• Solving Google's reCAPTCHA v2 with YOLO (2024) — ETH Zurich: https://...
• …

#Captchas #Recaptcha #Bots
```

Blank line between every section. No section headers other than
"Chapters" and "Sources & further reading" — the hook, explainer, and
hashtags need no labels.
