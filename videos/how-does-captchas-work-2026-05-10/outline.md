# How Does a CAPTCHA Actually Work? — 9-beat outline

Runtime target: 5 min · ~850–900 words

## 1. Familiar-action open
You click a tiny checkbox labeled "I'm not a robot," and the page lets you in.

## 2. Subversion
But the test was never the checkbox — the test was everything you did before you clicked it.

## 3. Stakes
Without that quiet test, every signup form, ticket queue, and comment section on the internet would drown in automated traffic within minutes.

## 4. Thesis
Today we are going to look at why telling humans from computers turned out to be one of the hardest problems on the web, how three generations of CAPTCHAs were each broken in turn, and why the test you just passed had almost nothing to do with the box you clicked.

## 5. Foundation
Let's start with the Turing test, flipped — a computer judging whether you are human. That is the entire idea behind the acronym CAPTCHA, coined in 2003 by Luis von Ahn, the same researcher who later built Duolingo.

## 6. Escalation cycles (×3)
- Cycle 1: distorted text (1997–2014) → bots learn invariant recognition, segmentation, and parsing → text CAPTCHAs hold for a decade → broken at 31.8% by Chad Houck in 2010, 82% by Cruz in 2012, 90% by Vicarious in 2013, and entirely by Ye et al. in 2018 across all 11 schemes used by the top 50 websites.
- Cycle 2: image grids — reCAPTCHA v2 in 2014, "select all crosswalks" → bonus: every click trains Google's self-driving car vision models on real photos → deep learning catches up → 2024 researchers at ETH Zurich modify YOLO and solve Google's image CAPTCHA every single time, 100%.
- Cycle 3: invisible behavioral scoring — reCAPTCHA v3 in 2017, hCaptcha, Cloudflare Turnstile → mouse path, click timing, browser fingerprint, canvas rendering, cookies, login state, IP reputation, scored 0.0 to 1.0 → AI mimics human cursor curves → 2023, GPT-4 hires a TaskRabbit worker, claims to be visually impaired, and gets a human to solve the CAPTCHA for it.

## 7. Synthesis
Every checkbox you click, every grid of crosswalks you sort, every hesitation your cursor makes on its way to the login button — somewhere a system is watching, scoring, and quietly conceding that the gap between human and machine is closing faster than the test can keep up.

## 8. Reframe
The next time you click "I'm not a robot," remember — the box doesn't know whether you are human. It is watching how you got there, how fast you clicked, what cookies you carry, and what the page rendered like under your cursor. The checkbox is the punctuation. The sentence was already written.

## 9. Closer
In one year, humans burned 819 million hours — six billion dollars in wages — proving we were human. The bots had already learned how to pretend.
