# How JavaScript Quietly Conquered the World — substrate notes

Runtime target: 5 min · ~850 words body

## Body shape (Q&A timeline + iceberg subversion)

The body answers four questions in order, each anchored to a dated incident:

1. **Why did we create JavaScript?** → Brendan Eich, 10 days, May 1995, Netscape.
2. **How did JS get to the server?** → Ryan Dahl, Node.js, JSConf EU Berlin, November 2009.
3. **How did JS get to mobile?** → React Native, Facebook F8, March 2015.
4. **How did JS take over the world?** → Electron (GitHub, 2013) and the surprise — Windows 11 Start menu's "recommended" section is React Native rendering into XAML. Plus the modern compounding factor: LLMs trained on more JS than any other language generate more JS.

Hook: open with a damning real quote about JS, anchor it with a year, then pivot with a single concrete fact (Stack Overflow 2025 rank) that makes the rest of the video feel inevitable.

## Hook-worthy criticism quotes (pick the strongest, drop the rest)

- **danbruc, HN comment, December 2014:** *"We allowed this awful language to escape the browser and infiltrate our servers in form of Node.js."* (https://news.ycombinator.com/item?id=8815155) — **Top candidate.** Uses the word "escape" — literally what JS did. The irony is built in: in 2014 this was a complaint; in 2026, the "escape" is so complete it built the Windows Start menu.
- **Douglas Crockford** (creator of JSON, author of *JavaScript: The Good Parts*): *"JavaScript is built on some very good ideas and a few very bad ones."* — authoritative, balanced.
- **Armin Ronacher, December 9, 2013** (creator of Flask): *"JavaScript is the Wild West of software development. Primarily because it rivals 2003 PHP code in terms of code quality."* (https://lucumr.pocoo.org/2013/12/9/stop-being-clever/) — savage, dated, attributable.
- **Richard Kenneth Eng, January 2016:** JavaScript should be *"the assembly language of the web"* and transpiled to from better languages. (https://medium.com/javascript-non-grata/the-top-10-things-wrong-with-javascript-58f440d6b3d8)
- **icedchai, HN 2014:** *"Developing a web application is basically the act of putting square pegs into round holes, over and over."*

## Real dated incidents

- **May 1995** — Brendan Eich at Netscape builds the JavaScript prototype in **10 days** to meet the Navigator 2.0 Beta release schedule. Originally called **Mocha**.
- **September 1995** — Renamed **LiveScript**.
- **December 1995** — Renamed **JavaScript** in a joint announcement with Sun Microsystems (marketing tie-in with Java's hype).
- **November 7–8, 2009** — Ryan Dahl debuts **Node.js** at JSConf EU Berlin to an audience of 150. Talk title: "Node.js, Evented I/O for V8 Javascript." Received a standing ovation — a conference first.
- **2013** — Cheng Zhao at GitHub creates **Atom Shell** (Chromium + Node) as the backbone of the Atom text editor. The combination that makes Electron possible.
- **April 2014** — Atom editor enters public beta on the Atom Shell runtime.
- **January 2015** — React Native debuts at React.js Conf (technical talk, Jan 28–29).
- **March 2015** — Facebook **open-sources React Native** at F8.
- **April 2015** — Atom Shell renamed **Electron**.
- **~2024** — Microsoft confirms the "recommended" section of the Windows 11 Start menu was built with **React Native rendering into XAML**, and announces a migration to native **WinUI3** for performance/latency (HN item 47463884).

## Concrete numbers and figures

- **10 days** — JavaScript's original prototype timeline (Eich, May 1995). Most legendary number in language history.
- **150 people** — audience size at Node.js's debut talk (JSConf EU Berlin, Nov 2009).
- **#1 / 66%** — JavaScript's rank in the **Stack Overflow Developer Survey 2025**, used by 66% of 49,000+ surveyed developers. JS has been #1 in the survey every year for over a decade.
- **30 years** — 1995–2025; JavaScript's age in 2026.

## Named people and organizations

- **Brendan Eich** — creator of JavaScript at Netscape (1995). Later co-founded Mozilla and Brave.
- **Ryan Dahl** — creator of Node.js (2009) and Deno. Brought JS to the server.
- **Cheng Zhao** — engineer at GitHub, creator of Atom Shell / Electron (2013).
- **Douglas Crockford** — creator of JSON, author of *JavaScript: The Good Parts*. The most quoted critic-defender.
- **Armin Ronacher** — creator of Flask. Outside critic with credibility across languages.
- **Microsoft** — owns the Windows 11 Start menu decision (React Native → XAML, then migration to WinUI3).
- **Meta / Facebook** — origin and largest production user of React Native.
- **Companies on Electron**: Microsoft (VS Code), Slack, Discord, Figma, 1Password, Notion, Obsidian, GitKraken.

## Modern compounding factor — LLMs

> **Hedged claim, not a verified citation.** The argument: LLMs are trained on
> code corpuses dominated by JavaScript (the most-published language on
> GitHub). More JS in training → more JS generated → more JS shipped → more
> JS in the next training set. The substrate compounds. State this as the
> modern reason JS is *still* growing in 2026, not as the reason it
> originally won. Soften with "likely" / "appears to" — the fact-verifier
> will surface a real source or push us to qualify further.

> **Theo Browne reference (UNVERIFIED).** User mentioned a Theo video about
> AI choosing JS when asked which language to start a project in. Search
> couldn't surface that specific video. **Don't reference unless the user
> supplies the URL.** Theo is documented as TypeScript-aligned (creator of
> T3 Stack, runs T3 Chat), so a generic "Theo says AI picks TS/JS" line
> would be plausibly true but unverified — and the fact-verifier would
> catch the missing citation.

## Load-bearing moments

- **The "escape the browser" quote → 2026 reality.** danbruc's 2014 disgust line ("we allowed this awful language to escape the browser") is the spine of the entire video. In 2014 it was a warning. In 2026 the "escape" is so complete it built the Windows Start menu. The hook quotes it; the body honors it; the landing closes the loop on it.
- **The Windows 11 Start menu = React Native moment.** The iceberg subversion. The single most specific, most surprising fact in the entire substrate. It's the punch that makes "JS conquered the world" feel literal rather than rhetorical.
- **The "every company has a website" structural argument.** Explains *why* JS won by default — not by being best at anything, but by being unavoidable for the one thing every company has to ship.

## SEO context

- Top searchable nouns to bias toward: **javascript**, **language**, **web**. Title carries "javascript" and "world" but not "web" — the body must invoke "browser" / "web" early so the search-discovery signal lands.
- Saturation warnings: **none** — the lane is structurally open.
- Hook-time budget: top performers hold **18% / 12% / 14% at 5 / 15 / 30s**. The damning quote + the Stack Overflow pivot must complete before the 15s mark.

## TTS notes (apply during drafting)

- "Node.js" — TTS sometimes mangles. Test; if it does, write "node dot J-S" or "Node JS" (no dot).
- "React Native" / "Electron" / "Three.js" — multi-syllable proper nouns, should be fine but flag if they slip.
- Years: "1995" / "2009" / "2015" — fine; "2024" / "2026" — fine. No decimal numbers in the substrate to worry about.
- "JSConf EU" — likely reads letter-spelled fine; if it slips, write "the JS Conf Europe event".
- "%" and percentage signs: spell as "percent" — already in the gotchas file.
- "JavaScript: The Good Parts" — the colon may produce a long pause. Write "Douglas Crockford's book, JavaScript: The Good Parts," with comma-bracketed phrasing.
