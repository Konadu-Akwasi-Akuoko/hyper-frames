# Translation style for SRT and thumbnail-title files

This skill produces subtitles and thumbnail-title localizations for a
technical-explainer channel. The audience is mid-to-senior engineers in each
target language. Apply these conventions consistently across every output.

## Terms to keep in Latin script across all 13 languages

These are brand names, product names, or technical acronyms with established
English forms in tech-literate communities. Keep them in Latin script even in
non-Latin target languages (Arabic, Hindi, Japanese, Russian).

**Brands and products**
- CAPTCHA, reCAPTCHA, hCAPTCHA, Cloudflare Turnstile
- GPT-4, ChatGPT, GPT (and successor model names)
- TaskRabbit, PayPal, Microsoft, Wikipedia, eBay, Reddit, Google, Duolingo
- YouTube, X (Twitter), LinkedIn, GitHub
- HyperFrames

**Technical acronyms and terms**
- AI, API, URL, HTTP, HTTPS, CSS, HTML, JS, JSON, SRT, SDK
- VPN, DNS, CDN, IP, TCP, UDP
- YOLO (the model), GAN, LLM, ML, NLP, RL
- DEF CON, ETH Zurich
- V3 (version designator, e.g. "reCAPTCHA V3")

**Why:** these forms are how the target audience search-engines, talks, and
reads about the topic in their own language. Transliterating "GPT-4" into
Devanagari or Cyrillic produces a string nobody searches for.

## Proper names

Personal names stay in their original Latin form across all 13 target
languages — that is how Wikipedia and tech press in each language refers to
them. Examples: Alan Turing, Luis von Ahn, Jonathan Wilkins, Chad Houck.

## Numbers

The English source captions intentionally spell numbers out (e.g. "nineteen
fifty") because they mirror the spoken voiceover. **In foreign-language SRT
files, switch to digits** (`1950`, `2003`, `18%`, `100%`). This is standard
SRT convention and improves readability in a tight subtitle window.

**Hindi exception — use native Indian numbering for very large numbers.** The
Indian numbering system (lakh / crore / arab) is the natural way Hindi
speakers read big quantities.

- `819 million` → `81.9 करोड़` (1 crore = 10 million, so 819 million = 81.9 crore)
- `6 billion` → `6 अरब` (1 arab = 1 billion)

Small integers (`2003`, `14,000`, `69%`) stay in Western digits — Hindi tech
content uses these directly.

For all other languages, use Western digits with the language's own
thousands separator convention where natural (e.g. German `14.000`,
Spanish `14.000`, French `14 000`).

## ALL-CAPS anchors

The voiceover.txt may contain ALL-CAPS words used as TTS emphasis anchors
(e.g. `BAD BOTS`, `PAYPAL`, `TASKRABBIT`). These are not preserved in the
SRT — use normal title casing or sentence casing in the target language.
The emphasis is already carried by the audio.

## RTL languages (Arabic)

SRT supports right-to-left text natively when the file is UTF-8 encoded.
Write the translated text in normal reading order (right-to-left logically,
displayed left-to-right in the file) — YouTube's player handles directionality
automatically. No special markers or `‎` overrides needed.

Punctuation: Arabic uses `،` (Arabic comma, U+060C) and `؟` (Arabic
question mark, U+061F). Use these instead of `,` and `?` in fully Arabic
sentences. Latin acronyms (CAPTCHA, etc.) embedded inside an Arabic sentence
follow the surrounding directionality — leave them in Latin script as-is.

## Quotation marks

Use the target language's natural quotation style:
- Spanish, Portuguese, Italian, English: `"…"` (double straight) or `« »`
- French: `« … »` with non-breaking spaces inside
- German, Polish: `„ … "` (low-9 + high-double) — common in subtitle work
- Russian: `« … »`
- Japanese: `「 … 」`
- Vietnamese, Turkish, Indonesian: `"…"` standard
- Arabic: `« … »` or `"…"`
- Hindi: `"…"` standard

Pick one style per language file and stay consistent.

## Tone register

Match the source's register: explanatory, plain prose, no slang, no jargon
that wouldn't already be in a technical reader's vocabulary in that language.
Avoid formal/archaic registers (`vous` in French is correct for a YouTube
viewer; `usted` is fine for Spanish; `Sie` is fine for German — all match
the source's neutral-respectful tone).

The source uses second person ("you click", "your browser") throughout. Keep
it. Don't switch to passive voice or impersonal constructions in
translation just because they're more "literary" — directness is the
register.

## Thumbnail overlay text (variant-text)

This text is rendered ONTO the thumbnail image. It's usually 4-8 words and
all-caps in English. Translate the meaning, but adapt for visual fit:

- Stay close to the source word count. If the source is 6 words, aim for
  4-8 words in translation.
- Long compound words (German) or longer-than-source phrasing (French,
  Spanish often need 20-30% more characters) are fine — the thumbnail
  layout will accommodate.
- Some languages don't naturally take all-caps (Arabic, Hindi, Japanese,
  Chinese). For those, render in the language's natural casing — the
  thumbnail's visual punch comes from layout and color, not letterforms.

## YouTube title (variant-yt-text)

This is the title that appears under the video and in search results.

- Stay under ~60 characters in the target language where natural.
- Lead with the keyword. If the English title leads with `How a CAPTCHA…`,
  the translation should also lead with the local "CAPTCHA" form (which
  for all 13 target languages is just `CAPTCHA`).
- Keep the curiosity hook of the source. Don't summarize it away.

## Things to avoid

- Don't translate proper names, brand names, or tech acronyms.
- Don't preserve the spelled-out number form from the English SRT — switch
  to digits.
- Don't insert emojis. The source has none; translations should have none.
- Don't add explanatory parentheticals that aren't in the source. If the
  source says "DEF CON", the translation says "DEF CON" — not "DEF CON
  (a hacker conference)".
- Don't over-localize cultural references that are already universal in
  tech. "Reddit", "Wikipedia", "GitHub" are recognized globally; leave
  them alone.
