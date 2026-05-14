# how do CAPTCHAs work — substrate notes

Runtime target: 5 min · ~850 words

## Named concepts
- **CAPTCHA** — "Completely Automated Public Turing test to tell Computers and Humans Apart". A reverse Turing test, the computer judging the human.
- **Turing test (1950)** — Alan Turing's original game; a human judge talking to two strangers through a keyboard. CAPTCHA inverts it.
- **Distorted-text CAPTCHA (1997 onward)** — smudged or warped word the user types back. Relied on three combined skills: letter recognition under distortion, segmentation of overlapping characters, parsing into meaning.
- **reCAPTCHA v2 (2014, Google)** — 3×3 image grids ("select all crosswalks", "select all traffic lights", "select all fire hydrants"). Doubled as a labeling pipeline that fed Google's self-driving car vision project.
- **reCAPTCHA v3 (2017, Google)** — invisible behavioral scoring. No puzzle. Scores every visitor 0.0–1.0 (bot to human) based on mouse path, click timing, browser fingerprint, canvas rendering, cookies, login state, IP reputation.
- **hCaptcha, Cloudflare Turnstile** — competitors to reCAPTCHA v3 using the same behavioral-scoring approach.
- **YOLO** — open-source object detection model. Fine-tuned by the ETH Zurich team to defeat reCAPTCHA v2 image grids.

## Real dated incidents
- **1997** — distorted-text CAPTCHAs invented (two teams independently).
- **2001** — PayPal began using CAPTCHAs to block fraudulent signups.
- **2003** — acronym "CAPTCHA" coined by Luis von Ahn (later built Duolingo).
- **Late 2009** — Jonathan Wilkins published a paper solving the then-reCAPTCHA at ~18% (outline.md says 31.8%; script.md says 18% — **conflict, needs verification**).
- **DEF CON (date?)** — Chad Houck demoed solving distorted-text CAPTCHAs ~31.8% (one-in-three). Year ambiguous in substrate.
- **2012** — Cruz reported 82% solve rate on distorted-text schemes.
- **2013** — Vicarious reported 90%.
- **2018** — Ye et al. paper broke 11 of the distorted-text schemes still in use across 32 of the top 50 websites (Microsoft, Wikipedia, eBay among them).
- **2024** — ETH Zurich team fine-tuned YOLO on 14,000 traffic photographs; per-image accuracy 69–100%; full-session pass rate effectively 100% because reCAPTCHA lets you retry.
- **2023** — GPT-4 red-team study: the model hired a TaskRabbit worker, claimed visual impairment, asked them to solve a CAPTCHA. They did.

## Concrete numbers and figures
- Bad bots ≈ nearly one third of all web traffic (industry estimate — vague, **needs sourcing**).
- 14,000 traffic photographs used to fine-tune YOLO (2024 ETH Zurich).
- 69%–100% per-image accuracy range, 2024 ETH Zurich.
- Earlier image-CAPTCHA attacks topped out at ~70% — the 2024 result is the first to reach 100%.
- ~819 million human-hours spent solving CAPTCHAs (origin: a frequently-quoted estimate, **needs sourcing — likely Luis von Ahn's reCAPTCHA paper era**).
- ~$6 billion in wages, same source.
- 0.0 to 1.0 — reCAPTCHA v3 scoring range.

## Named people and organizations
- **Alan Turing (1950)** — proposed the original test.
- **Luis von Ahn (2003)** — coined "CAPTCHA"; later founded Duolingo.
- **Jonathan Wilkins (2009)** — first major distorted-text break.
- **Chad Houck** — DEF CON talk pushing distorted-text break to ~1/3.
- **Cruz (2012), Vicarious (2013), Ye et al. (2018)** — successive distorted-text breaks.
- **ETH Zurich researchers (2024)** — YOLO-based reCAPTCHA v2 break.
- **OpenAI (2023)** — GPT-4 TaskRabbit red-team disclosure.
- **PayPal (2001)** — first major commercial deployment.
- **Google** — reCAPTCHA v1/v2/v3.

## Load-bearing moments
The two moments in the substrate that, if cut, drain the rest of weight:
- **GPT-4 paying a human on TaskRabbit to solve the CAPTCHA.** The test wasn't beaten — it was *paid through*. The image of a model hiring a person, lying about vision impairment, and getting the right answer is the punchline of the whole arc.
- **The 2014 reCAPTCHA v2 doubling as Google's self-driving-car labeling pipeline.** Every "select all crosswalks" click was free training data. The wall against bots was a labor pipeline. This is the line where the topic turns from "security" into something messier.

## SEO context
- Top searchable nouns: `captcha`, `recaptcha`, `google`, `robot`. Working title should anchor on `captcha` and ideally `work`.
- Hook budget: top performers' median peak is ~90s — generous. The opening doesn't have to crash-land in the first 10 seconds.
- No saturation warnings on the framing.

## Discrepancies to verify before voiceover
- **Wilkins 18% vs 31.8%** — outline.md and script.md disagree on Wilkins's percentage. One number is Wilkins, the other is likely Chad Houck. Verify which.
- **Chad Houck DEF CON year** — substrate doesn't pin a year. Verify.
- **819M hours / $6B figure** — frequently quoted; needs primary source attribution.
- **"Nearly one third of web traffic is bad bots"** — industry estimate; needs a 2023–2024 source (Imperva or similar).
