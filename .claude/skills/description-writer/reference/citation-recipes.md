# Citation recipes

What claims earn external URLs, how to phrase the WebSearch queries,
and how to dispatch them in parallel.

## What earns a citation

Scan `script.md` for these claim signals. Each one becomes one
WebSearch query.

| Signal | Examples from the captchas script |
|---|---|
| Specific year + named event | "In 1950, Alan Turing proposed…", "In 2024, ETH Zurich…" |
| Named person + specific work | "Luis von Ahn coined CAPTCHA in 2003", "Chad Houck at DEF CON" |
| Named institution + result | "ETH Zurich fine-tuned YOLO", "Google released reCAPTCHA v3" |
| Named paper / model / tool | "YOLO", "GPT-4 System Card", "reCAPTCHA v2" |
| Specific statistic + magnitude | "819 million hours", "31.8%", "six billion dollars" |

What does **not** earn a citation:

- Generic industry phrases ("bad bots account for nearly a third of
  web traffic") — too easy to cherry-pick, and the script's specific
  numbers usually trace to industry reports that are hard to
  authoritatively cite.
- Definitions the script gives ("A CAPTCHA is the Completely
  Automated Public Turing test…") — definition is in the acronym
  itself.
- Pedagogical examples invented for the video.

Soft cap: 6 sources. If the script has more than 6 candidates, pick
the strongest: specific year + named entity > generic claim, primary
source (paper, system card) > secondary (news article).

## Query phrasing patterns

Pattern: `<author or institution> <year> <topic noun> paper` works
best for academic claims.

| Claim | Query |
|---|---|
| Turing proposed the test in 1950 | `Turing 1950 Computing Machinery and Intelligence Mind journal` |
| Luis von Ahn coined CAPTCHA in 2003 | `Luis von Ahn 2003 CAPTCHA paper Carnegie Mellon` |
| Chad Houck broke text CAPTCHA at DEF CON 2010 | `Chad Houck DEF CON 2010 CAPTCHA decoder` |
| Ye et al. 2018 broke 11 schemes | `Ye 2018 CAPTCHA recognition all eleven schemes paper` |
| ETH Zurich solved reCAPTCHA v2 with YOLO 2024 | `ETH Zurich 2024 YOLO reCAPTCHA v2 paper arxiv` |
| GPT-4 hired TaskRabbit worker | `GPT-4 system card TaskRabbit CAPTCHA section OpenAI` |
| 819 million hours / $6B on CAPTCHAs | `819 million hours CAPTCHA economic cost study` |

Tips:

- Add `arxiv` or `paper` to bias toward primary sources.
- Add a specific institution name when known — disambiguates from
  derivative blog posts.
- Avoid vague queries like "how CAPTCHA was broken" — too broad,
  result quality drops.

## Parallel dispatch

Fire all WebSearch calls in a **single message** with multiple tool
calls. Do not chain them sequentially. The parallel dispatch is the
whole reason this step is cheap — ~6 queries finish in roughly the
time of one.

In the assistant turn that does Step 5, the tool block should look
like:

```
<function_calls>
  <WebSearch query="Turing 1950 Computing Machinery and Intelligence Mind">
  <WebSearch query="Luis von Ahn 2003 CAPTCHA paper Carnegie Mellon">
  <WebSearch query="ETH Zurich 2024 YOLO reCAPTCHA v2 paper arxiv">
  <WebSearch query="GPT-4 system card TaskRabbit CAPTCHA OpenAI">
  …
</function_calls>
```

Never split these across multiple assistant turns — the dispatch must
be in one block.

## Choosing the URL to cite

Each WebSearch returns 3–10 results. Pick the URL in this preference
order:

1. **Primary source.** The actual paper (arxiv, journal site,
   system card PDF on the org's domain). Always preferred when
   available.
2. **Official org page.** OpenAI's blog post, ETH Zurich's news
   release, the Wayback Machine snapshot if the original is gone.
3. **Wikipedia.** Acceptable for foundational claims (Turing test,
   definition of CAPTCHA) but never for the specific results — the
   citation chain is what matters.
4. **News article.** Last resort, and only if the article is from a
   reputable outlet (Ars Technica, Wired, MIT Technology Review).
   Avoid SEO-farm rewrites.

Never cite:

- A Medium article summarizing a paper, when the paper itself is
  linked.
- A Reddit thread or Hacker News comment, even if it has good
  context.
- A YouTube video — descriptions cite text/PDF sources, not other
  videos.

## When WebSearch returns nothing useful

If 1–2 queries come back without a strong source, drop those claims
from the sources list rather than citing a weak URL. The
"Sources & further reading" section is optional polish — better to
ship 4 strong citations than 6 with two weak ones.

If a critical citation (e.g., the headline GPT-4 / TaskRabbit
incident in a video that hinges on it) returns nothing, do **one**
follow-up WebFetch on the most promising candidate URL to verify
before citing it. Don't loop on this; one verification is enough.

## Attribution wording

In the description bullet, name the strongest entity tied to the
work. For a paper, use the lead author or institution — not both
unless space allows. For an org publication (system card, news
release), use the org name.

| Source type | Attribution |
|---|---|
| Single-author paper | `Author Lastname` or `Author Lastname et al.` |
| Multi-author paper | Institution name (e.g., "ETH Zurich") |
| Org publication | Org name (e.g., "OpenAI") |
| Wikipedia | "Wikipedia" |
| News article | Outlet name (e.g., "Ars Technica") |
