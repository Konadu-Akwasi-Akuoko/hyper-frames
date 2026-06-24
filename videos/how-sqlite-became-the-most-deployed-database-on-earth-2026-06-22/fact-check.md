# Fact check — how-sqlite-became-the-most-deployed-database-on-earth

Script: `script.md` (checked 2026-06-22)
Verified: 16 · Partial: 3 · Unverified: 0 · Contradicted: 0

---

## Verified

### "an engineer named D. Richard Hipp was writing software for the US Navy — specifically for a guided-missile destroyer called the USS Oscar Austin"
- Source: https://en.wikipedia.org/wiki/D._Richard_Hipp and https://corecursive.com/066-sqlite-with-richard-hipp/
- Source says: Hipp designed SQLite while working for General Dynamics on contract with the US Navy; the ship was USS Oscar Austin DDG-79, an Arleigh Burke-class guided-missile destroyer.
- Recommendation: keep. "Guided-missile destroyer" is exact and correct; the script avoids the host's erroneous "battleship" usage.

### "His program had a serious job. It told the crew which valves to open and close to seal off damage when the ship was hit."
- Source: https://corecursive.com/066-sqlite-with-richard-hipp/ and dossier §2 (Automated Common Diagrams)
- Source says: The program was called "Automated Common Diagrams" and told sailors which valves to open/close to isolate battle damage; pipe-routing and valve-location data lived in an on-ship database.
- Recommendation: keep.

### "On August seventeenth, 2000, the first version of SQLite shipped — two days before the Oscar Austin was even commissioned."
- Source: https://en.wikipedia.org/wiki/SQLite (initial release 17 August 2000) and https://en.wikipedia.org/wiki/USS_Oscar_Austin (commissioned 19 August 2000, Norfolk, Virginia)
- Source says: SQLite 1.0 released 2000-08-17; USS Oscar Austin commissioned 2000-08-19 — a two-day gap confirmed by both Wikipedia articles.
- Recommendation: keep.

### "He didn't choose MIT. He didn't choose BSD. He gave SQLite away to the public domain. No copyright. No terms. No strings."
- Source: https://sqlite.org/copyright.html
- Source says: "All of the code and documentation in SQLite has been dedicated to the public domain by the authors." / "No claim of copyright is made on any part of the core source code."
- Recommendation: keep.

### "SQLite does not compete with Oracle. It competes with fopen"
- Source: https://sqlite.org/whentouse.html
- Source says: Exact verbatim quote from the page: "SQLite does not compete with client/server databases. SQLite competes with fopen()."
- Recommendation: keep. The script drops the parentheses after fopen for readability, which is fine for voiceover.

### "For every line of code in the actual library, the project maintains around five hundred and ninety lines of test code."
- Source: https://sqlite.org/testing.html
- Source says: "As of version 3.42.0 (2023-05-16), the SQLite library consists of approximately 155.8 KSLOC of C code. By comparison, the project has 590 times as much test code and test scripts — 92053.1 KSLOC."
- Recommendation: keep.

### "The core is checked to a standard called M-C-D-C — the same bar the aviation industry demands for software that flies."
- Source: https://sqlite.org/th3.html and https://sqlite.org/testing.html
- Source says: TH3 achieves "100% branch coverage and 100% MC/DC (Modified Condition/Decision Coverage)" and was designed "to support the rigorous testing standards of DO-178B" — the aviation software certification standard whose hallmark requirement is 100% MC/DC.
- Recommendation: keep.

### "Four independent testing systems hammer at it constantly."
- Source: https://sqlite.org/testing.html
- Source says: Four independent test harnesses are listed: TCL Tests, TH3, SQL Logic Test, and dbsqlfuzz. The dossier also explicitly flags "FOUR independent harnesses (see corrections — not three)."
- Recommendation: keep. The script correctly says four, matching the current testing.html.

### "a single fuzzing tool throws roughly a billion mangled inputs at it every day"
- Source: https://sqlite.org/testing.html
- Source says: "dbsqlfuzz...runs about one billion test mutations per day."
- Recommendation: keep.

### "Every Android phone, every iPhone, every Mac and every Windows machine, every copy of Chrome, Firefox, and Safari — all of them carry the same small database"
- Source: https://sqlite.org/mostdeployed.html
- Source says: Verbatim from the page: "Every Android device, every iPhone and iOS device, every Mac, every Windows10 machine, and every Firefox, Chrome, and Safari web browser" ships SQLite.
- Recommendation: keep.

### "by their own estimate — and they are careful to call it an estimate — there are probably more than one trillion SQLite databases in active use"
- Source: https://sqlite.org/mostdeployed.html
- Source says: "it seems likely that there are over one trillion (1e12) SQLite databases in active use." The hedge ("seems likely") is explicit on the page. The script correctly frames this as SQLite's own hedged estimate.
- Recommendation: keep. The script's "by their own estimate — and they are careful to call it an estimate" is an accurate and responsible framing.

### "when an Airbus A350 lands, the log telling the ground crew what to repair runs on SQLite"
- Source: https://sqlite.org/famous.html (verbatim: "Airbus confirms that SQLite is being used in the flight software for the A350 XWB family of aircraft.") and dossier §8 (Hipp on record that the use is maintenance logging, not safety-critical flight control)
- Source says: SQLite is used in A350 flight software; Hipp's on-record clarification per the dossier is that it logs maintenance activities so ground crews get a printout of what needs fixing. The script frames this specifically as a maintenance log to the ground crew, which is the correct, non-safety-critical framing.
- Recommendation: keep. The script's phrasing ("the log telling the ground crew what to repair") is exactly right and avoids the flight-critical overstatement. Do not change it to "flight-critical" or "avionics."

### "the United States Library of Congress lists SQLite's format as one it recommends for data meant to outlive us all"
- Source: https://www.loc.gov/preservation/digital/formats/fdd/fdd000461.shtml and https://sqlite.org/locrsf.html; the 2024-2025 and 2025-2026 RFS editions both retain the designation.
- Source says: SQLite (FDD000461) is a recommended storage format for long-term digital preservation of datasets, most recently confirmed in the 2025-2026 Recommended Formats Statement PDF.
- Recommendation: keep.

### "It's maintained by a tiny company in North Carolina — in practice, a husband and wife and a small team."
- Source: https://www.hwaci.com/ and https://en.wikipedia.org/wiki/D._Richard_Hipp
- Source says: Hwaci (Hipp, Wyrick & Company, Inc.) is a small North Carolina S-corporation; Richard Hipp and Ginger Wyrick are the husband-and-wife co-owners; Ginger Wyrick is president. Charlotte, NC is their location.
- Recommendation: keep.

### "The source code isn't even hosted on GitHub. It sits in a version-control system Hipp built himself."
- Source: https://sqlite.org/whynotgit.html and https://en.wikipedia.org/wiki/Fossil_(software)
- Source says: Fossil SCM was created by D. Richard Hipp beginning in 2007; SQLite moved to Fossil from CVS in 2009. GitHub holds only a read-only mirror updated hourly. The canonical source lives in the Fossil repository.
- Recommendation: keep.

### "they turn down most outside contributions on purpose, because an accepted patch might carry a copyright — and then SQLite would no longer be fully in the public domain"
- Source: https://sqlite.org/copyright.html
- Source says: "In order to keep SQLite in the public domain and ensure that the code does not become contaminated with proprietary or licensed content, the project does not accept patches from people who have not submitted an affidavit dedicating their contribution into the public domain." Signed affidavits are stored in a firesafe at Hwaci.
- Recommendation: keep.

### "It now compiles straight into your web browser, so a web app can run a real database with no server behind it."
- Source: https://devclass.com/2022/11/17/sqlite-3-40-released-with-official-support-for-wasm-web-sql-reborn/
- Source says: SQLite 3.40.0 (released 2022-11-16) was the first release to ship official WebAssembly/JS components; sqlite.org/wasm went live October 2022.
- Recommendation: keep.

---

## Partial

### "A startup called Turso forked it to push it out to the edge."
- Source: https://github.com/tursodatabase/libsql and https://turso.tech/
- Source says: Turso created libSQL, an "open source, open contribution fork of SQLite." Turso also announced in 2025 a separate Rust rewrite (codenamed "Turso") which is not a fork but a clean-room reimplementation. The fork description is accurate for the libSQL project specifically; Turso as a company now ships both libSQL (fork) and the Rust rewrite.
- Delta: The script says Turso "forked it," which is accurate for libSQL but understates the current situation — Turso is in the process of moving to a full Rust rewrite that is no longer a fork. For a 2026 video, this may be slightly dated.
- Recommendation: soften to "A startup called Turso built on SQLite to push it out to the edge" to cover both the fork and rewrite without becoming inaccurate.

### "to keep SQLite supported, and its files readable, through the year 2050"
- Source: https://sqlite.org/lts.html
- Source says: "The intent of the developers is to support SQLite through the year 2050" and "we plan as if we will be supporting SQLite until 2050" — but the page explicitly adds: "we cannot absolutely promise that SQLite will be viable or useful that far out." The promise that is unconditional is backwards compatibility with the C API and on-disk format, not support itself.
- Delta: The script implies a firm "promise" ("a promise almost no software makes: to keep SQLite supported ... through the year 2050"). The lts.html page frames it as intent/plan, not a guarantee. The backwards-compatibility commitment is the binding piece; the "supported" part is aspirational.
- Recommendation: soften to "a pledge — almost unheard-of in software — to plan as if SQLite will be supported through the year 2050." This matches the source's own language and is still compelling.

### "Cloudflare rents it as a service called D1"
- Source: https://blog.cloudflare.com/making-full-stack-easier-d1-ga-hyperdrive-queues/ (D1 GA: 2024-04-01)
- Source says: Cloudflare D1 uses SQLite's SQL semantics and reached general availability April 1, 2024. The characterization "rents it as a service" is loose — D1 is a managed serverless database built on SQLite semantics, not a direct SQLite rental.
- Delta: "rents it as a service" is accurate in spirit (it is a paid managed service), but purists may note D1 is not literally serving SQLite files — it uses SQLite-compatible semantics on Cloudflare's distributed infrastructure.
- Recommendation: keep as-is for a general audience video; the phrasing is clear and not materially wrong. If precision is wanted, "Cloudflare built a managed database service called D1 on top of it."

---

## Unverified

(None — all concrete claims were resolved by primary sources.)

---

## Contradicted

(None — no source clearly disagreed with any claim in the script.)

---

## Framing notes (not claim failures, but editorial flags)

**A350 framing is correct and important to preserve.** The script says "the log telling the ground crew what to repair runs on SQLite." This is the right level of specificity. Famous.html says "flight software for the A350 XWB family," which sounds more alarming; Hipp's own on-record clarification (per the dossier, CoRecursive interview) is that it is maintenance logging, not safety-critical flight control. The script's phrasing is the most defensible version of this fact. Do not soften it further; do not harden it toward "flight controls."

**The trillion claim framing is responsible.** The script says "by their own estimate — and they are careful to call it an estimate." This exactly matches the source ("seems likely"). No correction needed.

**"A promise almost no software makes"** — this phrase precedes the 2050 claim. Given that lts.html frames it as a plan/intent rather than a promise, the phrase "a promise almost no software makes" applies to the backwards-compatibility pledge (which is a real commitment), not the support horizon per se. The script blends both into one sentence. See the Partial entry above for the recommended softening.
