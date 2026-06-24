# Thumbnail↔title pairing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Capture each `thumbnailInspo/` reference's real YouTube title in the catalog, classify it into a `title_shape` + `title_pattern`, surface both in the README, and teach the skill to use the chosen reference's title shape as a prior for the paired title it writes.

**Architecture:** Three new fields per catalog entry. `title` is a deterministic join from the per-channel `_manifest.json` (already harvested by `fetch.py`). `title_shape`/`title_pattern` are classified by a one-agent-per-catalog-file workflow fan-out (judgment), then applied to the JSONs by a deterministic merge script (the agents return data; a script mutates the files, avoiding 54 parallel file-editors). `build_readme.py` surfaces the new fields; two skill docs + the cataloging contract describe the prior-not-mandate behavior and the forward path.

**Tech Stack:** Python 3 standalone scripts under `tools/thumbnail-inspo/` (no package — plain `python3 script.py`, tests are plain-assert scripts run with `python3`). The classification fan-out uses the Workflow tool.

## Global Constraints

- **`title_shape` enum (exactly these 14):** `speed-primer`, `x-explained`, `every-x-explained`, `comparison-vs`, `what-is-x`, `open-why-how`, `listicle-n`, `assumption-flip`, `panic-threat`, `curiosity-reversal`, `scale-story`, `first-person-feat`, `identity-advice`, `meme-skit`.
- **`title_pattern` enum (exactly these 5, machine-slug forms of `title-engine.md`'s 5 patterns):** `concrete-noun-verb`, `curiosity-gap-reversal`, `open-what-why-how`, `assumption-flip`, `identity-status`.
- **Caveat shapes:** `every-x-explained` (rigid completeness — wins only on max-searched nouns) and `meme-skit` (documented corpus floor) must always be surfaced with their warnings; never inherited blindly.
- **Non-verbatim rule:** the catalogued title is a *shape prior + worked example*, never copied. Replicate the title shape, swap the words — the same rule that governs layout pixels.
- **Title already captured:** `fetch.py` already writes `item.title` into each `_manifest.json`. No `fetch.py` change. The forward path = the reusable backfill script (re-run after any catalog change) + the cataloging-contract doc.
- **Catalog↔manifest join key:** catalog entry `channel` → folder `thumbnailInspo/<channel>/_manifest.json`; match `entry["file"]` to `item["file"]`. Verified 0 mismatches across all 389 entries.
- **Scope:** 54 catalog files in `tools/thumbnail-inspo/catalog/*.json`, 389 entries total.
- **The dedicated title corpus (`research/thumbnail-title-corpus-*/ANALYSIS.md`) stays the title engine.** The catalogued title never becomes a competing source.

---

### Task 1: Deterministic title backfill tool

**Files:**
- Create: `tools/thumbnail-inspo/backfill_titles.py`
- Test: `tools/thumbnail-inspo/test_backfill_titles.py`

**Interfaces:**
- Produces: `inject_titles(catalog_dir: Path, lib_dir: Path) -> int` — adds a `title` key to every catalog entry by joining the matching manifest, returns the count of entries updated. Idempotent (re-running is a no-op if titles already match). `main() -> int` runs it against the real dirs and prints the count.

- [ ] **Step 1: Write the failing test**

```python
# tools/thumbnail-inspo/test_backfill_titles.py
"""Plain-assert tests for backfill_titles. Run: python3 tools/thumbnail-inspo/test_backfill_titles.py"""
import json
import tempfile
from pathlib import Path

import backfill_titles as bt


def test_inject_titles_joins_by_channel_and_file():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        catalog = root / "catalog"
        catalog.mkdir()
        lib = root / "lib"
        (lib / "fireship").mkdir(parents=True)

        (lib / "fireship" / "_manifest.json").write_text(json.dumps({
            "slug": "fireship",
            "items": [{"file": "06-U3aXWizDbQ4.jpg", "title": "C in 100 Seconds"}],
        }))
        (catalog / "fireship-1.json").write_text(json.dumps([
            {"slug": "fireship-c", "channel": "fireship", "file": "06-U3aXWizDbQ4.jpg"},
        ]))

        updated = bt.inject_titles(catalog, lib)
        assert updated == 1, updated

        entry = json.loads((catalog / "fireship-1.json").read_text())[0]
        assert entry["title"] == "C in 100 Seconds", entry

        # idempotent: a second run updates nothing
        assert bt.inject_titles(catalog, lib) == 0


def test_inject_titles_skips_unmatched_file():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        catalog = root / "catalog"
        catalog.mkdir()
        lib = root / "lib"
        (lib / "fireship").mkdir(parents=True)
        (lib / "fireship" / "_manifest.json").write_text(json.dumps({
            "slug": "fireship", "items": [{"file": "99-other.jpg", "title": "X"}],
        }))
        (catalog / "fireship-1.json").write_text(json.dumps([
            {"slug": "fireship-c", "channel": "fireship", "file": "06-U3aXWizDbQ4.jpg"},
        ]))
        assert bt.inject_titles(catalog, lib) == 0
        entry = json.loads((catalog / "fireship-1.json").read_text())[0]
        assert "title" not in entry


if __name__ == "__main__":
    test_inject_titles_joins_by_channel_and_file()
    test_inject_titles_skips_unmatched_file()
    print("ok")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd tools/thumbnail-inspo && python3 test_backfill_titles.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'backfill_titles'`

- [ ] **Step 3: Write minimal implementation**

```python
#!/usr/bin/env python3
"""Inject each catalog entry's real YouTube title from the per-channel manifest.

Deterministic, idempotent join: for every entry in tools/thumbnail-inspo/catalog/*.json,
look up thumbnailInspo/<channel>/_manifest.json and copy the matching item's `title`
(keyed by `file`). fetch.py already harvests the title into the manifest, so this
never touches the network. Re-run any time the catalog changes.

Usage:
    python3 tools/thumbnail-inspo/backfill_titles.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG_DIR = Path(__file__).resolve().parent / "catalog"
LIB_DIR = ROOT / "thumbnailInspo"


def _manifest_titles(lib_dir: Path, channel: str) -> dict[str, str]:
    man = lib_dir / channel / "_manifest.json"
    if not man.exists():
        return {}
    data = json.loads(man.read_text())
    return {i["file"]: i.get("title", "") for i in data.get("items", []) if i.get("file")}


def inject_titles(catalog_dir: Path, lib_dir: Path) -> int:
    updated = 0
    cache: dict[str, dict[str, str]] = {}
    for fp in sorted(catalog_dir.glob("*.json")):
        entries = json.loads(fp.read_text())
        if not isinstance(entries, list):
            continue
        changed = False
        for e in entries:
            ch, fn = e.get("channel"), e.get("file")
            if not ch or not fn:
                continue
            titles = cache.setdefault(ch, _manifest_titles(lib_dir, ch))
            title = titles.get(fn)
            if title and e.get("title") != title:
                e["title"] = title
                updated += 1
                changed = True
        if changed:
            fp.write_text(json.dumps(entries, indent=2) + "\n")
    return updated


def main() -> int:
    n = inject_titles(CATALOG_DIR, LIB_DIR)
    print(f"injected/updated {n} titles across catalog entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd tools/thumbnail-inspo && python3 test_backfill_titles.py`
Expected: `ok`

- [ ] **Step 5: Apply to the real catalog and sanity-check**

Run: `cd tools/thumbnail-inspo && python3 backfill_titles.py`
Expected: `injected/updated 389 titles across catalog entries`

Run: `python3 -c "import json,glob; n=sum('title' in e for f in glob.glob('tools/thumbnail-inspo/catalog/*.json') for e in json.load(open(f))); print('entries with title:', n)"`
Expected: `entries with title: 389`

- [ ] **Step 6: Commit**

```bash
git add tools/thumbnail-inspo/backfill_titles.py tools/thumbnail-inspo/test_backfill_titles.py tools/thumbnail-inspo/catalog/
git commit -m "feat(thumbnail-inspo): backfill reference titles from manifests into catalog"
```

---

### Task 2: Deterministic classification merge tool

**Files:**
- Create: `tools/thumbnail-inspo/apply_classifications.py`
- Test: `tools/thumbnail-inspo/test_apply_classifications.py`

**Interfaces:**
- Consumes: a JSON file shaped `[{"slug": str, "title_shape": str, "title_pattern": str}, ...]` (the flattened output the Task 3 workflow returns).
- Produces: `apply(classifications: list[dict], catalog_dir: Path) -> tuple[int, list[str]]` — writes `title_shape`/`title_pattern` into the matching catalog entry by `slug`, validating each value against the enums; returns `(applied_count, errors)`. `errors` lists slugs whose shape/pattern was not in the enum or whose slug was not found. `main(argv)` reads the JSON path from argv and applies against the real catalog dir.

- [ ] **Step 1: Write the failing test**

```python
# tools/thumbnail-inspo/test_apply_classifications.py
"""Plain-assert tests. Run: python3 tools/thumbnail-inspo/test_apply_classifications.py"""
import json
import tempfile
from pathlib import Path

import apply_classifications as ac


def test_apply_writes_fields_by_slug():
    with tempfile.TemporaryDirectory() as td:
        catalog = Path(td) / "catalog"
        catalog.mkdir()
        (catalog / "fireship-1.json").write_text(json.dumps([
            {"slug": "fireship-c", "channel": "fireship", "file": "06.jpg", "title": "C in 100 Seconds"},
        ]))
        applied, errors = ac.apply(
            [{"slug": "fireship-c", "title_shape": "speed-primer",
              "title_pattern": "concrete-noun-verb"}], catalog)
        assert applied == 1, applied
        assert errors == [], errors
        e = json.loads((catalog / "fireship-1.json").read_text())[0]
        assert e["title_shape"] == "speed-primer"
        assert e["title_pattern"] == "concrete-noun-verb"


def test_apply_rejects_unknown_enum_value():
    with tempfile.TemporaryDirectory() as td:
        catalog = Path(td) / "catalog"
        catalog.mkdir()
        (catalog / "x.json").write_text(json.dumps([{"slug": "a", "channel": "c", "file": "1.jpg"}]))
        applied, errors = ac.apply(
            [{"slug": "a", "title_shape": "made-up", "title_pattern": "concrete-noun-verb"}], catalog)
        assert applied == 0, applied
        assert any("made-up" in msg for msg in errors), errors


def test_apply_reports_missing_slug():
    with tempfile.TemporaryDirectory() as td:
        catalog = Path(td) / "catalog"
        catalog.mkdir()
        (catalog / "x.json").write_text(json.dumps([{"slug": "a", "channel": "c", "file": "1.jpg"}]))
        applied, errors = ac.apply(
            [{"slug": "ghost", "title_shape": "speed-primer", "title_pattern": "concrete-noun-verb"}], catalog)
        assert applied == 0
        assert any("ghost" in msg for msg in errors), errors


if __name__ == "__main__":
    test_apply_writes_fields_by_slug()
    test_apply_rejects_unknown_enum_value()
    test_apply_reports_missing_slug()
    print("ok")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd tools/thumbnail-inspo && python3 test_apply_classifications.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'apply_classifications'`

- [ ] **Step 3: Write minimal implementation**

```python
#!/usr/bin/env python3
"""Apply title_shape/title_pattern classifications (from the workflow) to the catalog.

The classification workflow returns judgment only; this deterministic merge does the
file mutation — one writer, validated against the fixed enums, keyed by slug. This
keeps 54 parallel agents from hand-editing JSON.

Usage:
    python3 tools/thumbnail-inspo/apply_classifications.py <classifications.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CATALOG_DIR = Path(__file__).resolve().parent / "catalog"

TITLE_SHAPES = {
    "speed-primer", "x-explained", "every-x-explained", "comparison-vs",
    "what-is-x", "open-why-how", "listicle-n", "assumption-flip",
    "panic-threat", "curiosity-reversal", "scale-story", "first-person-feat",
    "identity-advice", "meme-skit",
}
TITLE_PATTERNS = {
    "concrete-noun-verb", "curiosity-gap-reversal", "open-what-why-how",
    "assumption-flip", "identity-status",
}


def apply(classifications: list[dict], catalog_dir: Path) -> tuple[int, list[str]]:
    by_slug: dict[str, dict] = {}
    errors: list[str] = []
    for c in classifications:
        slug = c.get("slug")
        shape = c.get("title_shape")
        pattern = c.get("title_pattern")
        if shape not in TITLE_SHAPES:
            errors.append(f"{slug}: bad title_shape {shape!r}")
            continue
        if pattern not in TITLE_PATTERNS:
            errors.append(f"{slug}: bad title_pattern {pattern!r}")
            continue
        by_slug[slug] = c

    applied = 0
    seen: set[str] = set()
    for fp in sorted(catalog_dir.glob("*.json")):
        entries = json.loads(fp.read_text())
        if not isinstance(entries, list):
            continue
        changed = False
        for e in entries:
            c = by_slug.get(e.get("slug"))
            if not c:
                continue
            e["title_shape"] = c["title_shape"]
            e["title_pattern"] = c["title_pattern"]
            seen.add(e["slug"])
            applied += 1
            changed = True
        if changed:
            fp.write_text(json.dumps(entries, indent=2) + "\n")

    for slug in by_slug:
        if slug not in seen:
            errors.append(f"{slug}: slug not found in catalog")
    return applied, errors


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("usage: apply_classifications.py <classifications.json>", file=sys.stderr)
        return 2
    data = json.loads(Path(argv[1]).read_text())
    applied, errors = apply(data, CATALOG_DIR)
    print(f"applied {applied} classifications")
    for msg in errors:
        print(f"  ! {msg}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd tools/thumbnail-inspo && python3 test_apply_classifications.py`
Expected: `ok`

- [ ] **Step 5: Commit**

```bash
git add tools/thumbnail-inspo/apply_classifications.py tools/thumbnail-inspo/test_apply_classifications.py
git commit -m "feat(thumbnail-inspo): deterministic title_shape/pattern merge tool"
```

---

### Task 3: Classify all entries via the workflow, then apply

**Files:**
- Create (scratchpad, not committed): the workflow script + the workflow's returned classifications JSON.
- Modify: `tools/thumbnail-inspo/catalog/*.json` (via `apply_classifications.py`)

**Interfaces:**
- Consumes: `inject_titles` output (entries already carry `title`), `apply()` from Task 2.
- Produces: every catalog entry carries a valid `title_shape` + `title_pattern`.

- [ ] **Step 1: Generate the list of catalog files to fan out over**

Run: `python3 -c "import glob; print('\n'.join(sorted(glob.glob('tools/thumbnail-inspo/catalog/*.json'))))"`
Expected: 54 paths. Capture them — they get baked into the workflow script as a literal array (workflow args do not pass reliably via scriptPath; the JS sandbox has no filesystem, so the list must be inline; each agent then Reads its own file).

- [ ] **Step 2: Author the classification workflow script**

Write this to the scratchpad (`<scratchpad>/classify-titles.workflow.js`), substituting the real 54-path list into `CATALOG_FILES`:

```javascript
export const meta = {
  name: 'classify-title-shapes',
  description: 'Classify each thumbnailInspo reference title into title_shape + title_pattern',
  phases: [{ title: 'Classify' }, { title: 'Critic' }],
}

const CATALOG_FILES = [
  // ... 54 absolute paths from Step 1, one string per line ...
]

const SHAPES = "speed-primer | x-explained | every-x-explained | comparison-vs | what-is-x | open-why-how | listicle-n | assumption-flip | panic-threat | curiosity-reversal | scale-story | first-person-feat | identity-advice | meme-skit"
const PATTERNS = "concrete-noun-verb | curiosity-gap-reversal | open-what-why-how | assumption-flip | identity-status"

const CLS_SCHEMA = {
  type: "object",
  required: ["classifications"],
  properties: {
    classifications: {
      type: "array",
      items: {
        type: "object",
        required: ["slug", "title_shape", "title_pattern", "rationale"],
        properties: {
          slug: { type: "string" },
          title_shape: { type: "string", enum: SHAPES.split(" | ") },
          title_pattern: { type: "string", enum: PATTERNS.split(" | ") },
          rationale: { type: "string" },
        },
      },
    },
  },
}

const guide = `You classify YouTube thumbnail TITLES into a fixed taxonomy.

title_shape — surface formula, EXACTLY one of: ${SHAPES}
  speed-primer: "X in N seconds/minutes", "Learn X in 5 minutes"
  x-explained: "X Explained [in N min]"
  every-x-explained: "Every X Explained in N Minutes!" (rigid completeness)
  comparison-vs: "X vs Y"
  what-is-x: "What is X?"
  open-why-how: open "Why does X…?" / "How does X work?"
  listicle-n: "N things/tools/concepts…", "Top N…"
  assumption-flip: contrarian belief flip — "X is dead", "Frameworks don't matter anymore"
  panic-threat: doom/news fallout — "X is in big trouble…", "AI bubble is popping"
  curiosity-reversal: trailing gap paying off in a reversal/named stake — "… Until It Couldn't"
  scale-story: "How [Company] handles TRILLIONS / makes $200M"
  first-person-feat: "I built/tried/gave X…"
  identity-advice: advice to a tribe / status — "CS students need to hear this", "think like a GENIUS programmer"
  meme-skit: "If programming was an anime" (documented weak shape)

title_pattern — the title-engine pattern it rides, EXACTLY one of: ${PATTERNS}
  concrete-noun-verb, curiosity-gap-reversal, open-what-why-how, assumption-flip, identity-status

Pick the SINGLE best shape per title even if imperfect; note the imperfect fit in rationale.`

const perFile = (path) => agent(
  `${guide}\n\nRead the catalog file at ${path}. It is a JSON array of entries, each with a "slug" and a "title". For EVERY entry, classify its "title" and return {slug, title_shape, title_pattern, rationale}. Do NOT edit the file.`,
  { label: `classify:${path.split('/').pop()}`, phase: 'Classify', schema: CLS_SCHEMA }
)

const results = await parallel(CATALOG_FILES.map((p) => () => perFile(p)))
const flat = results.filter(Boolean).flatMap((r) => r.classifications)

const critic = await agent(
  `Here are title classifications as JSON:\n${JSON.stringify(flat)}\n\n` +
  `Find obvious misclassifications: a title containing " vs " not tagged comparison-vs; ` +
  `a title ending in "…" with a reversal not tagged curiosity-reversal; ` +
  `an "X in N seconds/minutes" not tagged speed-primer; an "Every X Explained" not tagged every-x-explained. ` +
  `Return the FULL corrected list (same shape: {slug,title_shape,title_pattern,rationale}).`,
  { label: 'critic', phase: 'Critic', schema: CLS_SCHEMA }
)

return critic.classifications
```

- [ ] **Step 3: Run the workflow**

Invoke the Workflow tool with `{ scriptPath: "<scratchpad>/classify-titles.workflow.js" }`. Wait for the completion notification. The tool result returns the corrected classifications array (389 objects).

- [ ] **Step 4: Save the workflow output and apply it**

Write the returned array to `<scratchpad>/classifications.json`, then:

Run: `python3 tools/thumbnail-inspo/apply_classifications.py <scratchpad>/classifications.json`
Expected: `applied 389 classifications` and no `!` error lines.

- [ ] **Step 5: Verify every entry is classified and no files were stray-deleted**

Run: `git diff --stat tools/thumbnail-inspo/catalog/ | tail -3`
Expected: only `catalog/*.json` modified, 0 deletions of files (54 files still present: `ls tools/thumbnail-inspo/catalog/*.json | wc -l` → 54).

Run: `python3 -c "import json,glob; bad=[e['slug'] for f in glob.glob('tools/thumbnail-inspo/catalog/*.json') for e in json.load(open(f)) if 'title_shape' not in e or 'title_pattern' not in e]; print('unclassified:', len(bad), bad[:5])"`
Expected: `unclassified: 0 []`

- [ ] **Step 6: Commit**

```bash
git add tools/thumbnail-inspo/catalog/
git commit -m "feat(thumbnail-inspo): classify all reference titles into title_shape + title_pattern"
```

---

### Task 4: Surface title + title_shape in the README

**Files:**
- Modify: `tools/thumbnail-inspo/build_readme.py:99-127` (the `render` function)
- Test: `tools/thumbnail-inspo/test_build_readme.py`
- Modify (regenerated): `thumbnailInspo/README.md`

**Interfaces:**
- Consumes: catalog entries now carrying `title`, `title_shape`, `title_pattern`.
- Produces: Quick-index gains a `title_shape` column; each Entries block gains an `Original title` line (labeled "shape to mimic, not copy") and the shape/pattern.

- [ ] **Step 1: Write the failing test**

```python
# tools/thumbnail-inspo/test_build_readme.py
"""Plain-assert tests for the renderer. Run: python3 tools/thumbnail-inspo/test_build_readme.py"""
import build_readme as br

ENTRY = {
    "slug": "fireship-c", "channel": "fireship", "file": "06-x.jpg",
    "archetype": "big-text", "layout": "centered-stack", "device": ["big-text"],
    "face": False, "accent": "blue", "text": "low",
    "reads_as": "one giant C", "layout_map": "C centered", "why_it_works": "minimal",
    "mimic_for": "a quick primer", "watch_url": "https://yt/x",
    "title": "C in 100 Seconds", "title_shape": "speed-primer",
    "title_pattern": "concrete-noun-verb",
}


def test_quick_index_has_title_shape_column():
    out = br.render([ENTRY])
    header = [l for l in out.splitlines() if l.startswith("| slug |")][0]
    assert "title_shape" in header, header
    row = [l for l in out.splitlines() if l.startswith("| [fireship-c]")][0]
    assert "speed-primer" in row, row


def test_entry_block_has_original_title_labeled_not_copy():
    out = br.render([ENTRY])
    assert "C in 100 Seconds" in out
    assert "shape to mimic, not copy" in out
    assert "title_shape=speed-primer" in out


if __name__ == "__main__":
    test_quick_index_has_title_shape_column()
    test_entry_block_has_original_title_labeled_not_copy()
    print("ok")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd tools/thumbnail-inspo && python3 test_build_readme.py`
Expected: FAIL with `AssertionError` on the header (no `title_shape` column yet).

- [ ] **Step 3: Edit `render()` to add the column and the Entries lines**

Replace the `render` function body (`build_readme.py:98-128`) with:

```python
def render(entries: list[dict]) -> str:
    out = [HEADER, "\n## Quick index\n"]
    out.append("| slug | channel | archetype | layout | device | face | accent | title_shape | use-when |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    for e in entries:
        slug = e["slug"]
        dev = ", ".join(as_list(e.get("device")))
        out.append(
            f"| [{slug}](#{slug}) | {e.get('channel','')} | {e.get('archetype','')} "
            f"| {e.get('layout','')} | {dev} | {face_str(e.get('face'))} "
            f"| {e.get('accent','')} | {e.get('title_shape','')} "
            f"| {e.get('mimic_for', e.get('use_when','')).replace(chr(10),' ')} |"
        )

    out.append("\n## Entries\n")
    for e in entries:
        slug = e["slug"]
        dev = ", ".join(as_list(e.get("device")))
        img = f"{e.get('channel','')}/{e.get('file','')}"
        out.append(f"### {slug}")
        out.append(f"- Image: `{img}` · Source: {e.get('watch_url','')}")
        out.append(
            f"- Tags: archetype={e.get('archetype','')} · layout={e.get('layout','')} "
            f"· device=[{dev}] · face={face_str(e.get('face'))} "
            f"· accent={e.get('accent','')} · text={e.get('text','')}"
        )
        out.append(f"- Reads as: {e.get('reads_as','')}")
        out.append(f"- Layout map: {e.get('layout_map','')}")
        out.append(f"- Why it works: {e.get('why_it_works','')}")
        out.append(f"- Mimic for: {e.get('mimic_for','')}")
        if e.get("title"):
            out.append(
                f"- Original pair (shape to mimic, not copy): \"{e.get('title','')}\" "
                f"· title_shape={e.get('title_shape','')} · title_pattern={e.get('title_pattern','')}"
            )
        out.append("")
    return "\n".join(out) + "\n"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd tools/thumbnail-inspo && python3 test_build_readme.py`
Expected: `ok`

- [ ] **Step 5: Regenerate the real README**

Run: `python3 tools/thumbnail-inspo/build_readme.py`
Expected: `wrote .../thumbnailInspo/README.md with 389 entries`

Run: `grep -c "shape to mimic, not copy" thumbnailInspo/README.md`
Expected: `389`

- [ ] **Step 6: Commit**

```bash
git add tools/thumbnail-inspo/build_readme.py tools/thumbnail-inspo/test_build_readme.py thumbnailInspo/README.md
git commit -m "feat(thumbnail-inspo): surface title + title_shape in the README index"
```

---

### Task 5: Wire the docs — cataloging contract + skill behavior

**Files:**
- Modify: `thumbnailInspo/CLAUDE.md` (tagging vocabulary + adding-references sections)
- Modify: `.claude/skills/thumbnail-and-title-generator/reference/title-engine.md`
- Modify: `.claude/skills/thumbnail-and-title-generator/reference/inspiration-mimicry.md`

**Interfaces:** documentation only; no code. Encodes the forward path and the prior-not-mandate behavior.

- [ ] **Step 1: Add the title fields to the cataloging contract**

In `thumbnailInspo/CLAUDE.md`, under "## Adding references", after the `**You** (judgment)` bullet, add:

```markdown
- **Titles + title shape** (mechanical + judgment): `fetch.py` already records each
  thumbnail's real YouTube `title` in the manifest. After cataloging, run
  `python3 tools/thumbnail-inspo/backfill_titles.py` to inject `title` into every
  catalog entry, then classify each into `title_shape` (surface formula) +
  `title_pattern` (the title-engine pattern it rides). These let the skill pair a
  proven title shape with the layout — the shape is a prior, not a script to copy.
```

And append a new subsection to "## Tagging vocabulary":

```markdown
- **title_shape** (the title's surface formula, exactly one of 14):
  `speed-primer`, `x-explained`, `every-x-explained`, `comparison-vs`,
  `what-is-x`, `open-why-how`, `listicle-n`, `assumption-flip`, `panic-threat`,
  `curiosity-reversal`, `scale-story`, `first-person-feat`, `identity-advice`,
  `meme-skit`. Two carry corpus caveats: `every-x-explained` wins only on
  maximally-searched nouns; `meme-skit` is a documented floor.
- **title_pattern** (which of `title-engine.md`'s 5 patterns it rides):
  `concrete-noun-verb`, `curiosity-gap-reversal`, `open-what-why-how`,
  `assumption-flip`, `identity-status`.
```

- [ ] **Step 2: Add the prior-not-mandate rule to `title-engine.md`**

After the "## Per-variant writing routine" section, insert:

```markdown
## Reference title shape — a prior, not a mandate

Every `thumbnailInspo/` entry now carries the real title that ran with that
layout, classified as `title_shape` + `title_pattern`. When you pick a reference
for a variant, read its `title_shape` and **default to writing the paired title in
that shape** — the layout and the title shape are a proven pair, so they should
move together.

But the shape is a *prior*, not a lock. Override it when the engine says so:

- If SEO data (`signals.top_nouns`, `signals.saturation_warnings`) or one of the
  five winning patterns makes a different shape stronger for OUR noun, take it.
- Never inherit `every-x-explained` unless the noun is maximally searched, and
  never inherit `meme-skit` for our lane — both are documented floors.
- **Never copy the reference's actual title words.** The shape transfers; the words
  are always ours, grounded and searchable per the rules above. This is the title
  analogue of "lift the layout, never the pixels."
```

- [ ] **Step 3: Extend `inspiration-mimicry.md` to titles**

After the "## Relationship to the Specimen signature" section, insert:

```markdown
## The same principle applies to the title

The reference drives the **title shape** the same way it drives the layout: we copy
the *shape* (the skeleton — `speed-primer`, `comparison-vs`, `assumption-flip`, …)
and swap the *words* (the flesh — our noun, our claim). The reference's real title,
catalogued as `title_shape` + `title_pattern`, is a worked example of the
claim/ground split, not a script to copy. See `title-engine.md` →
"Reference title shape — a prior, not a mandate" for how strongly it binds.
```

- [ ] **Step 4: Verify the docs reference real, consistent values**

Run: `grep -l "title_shape" thumbnailInspo/CLAUDE.md .claude/skills/thumbnail-and-title-generator/reference/title-engine.md .claude/skills/thumbnail-and-title-generator/reference/inspiration-mimicry.md`
Expected: all three paths listed.

Run: `grep -o "speed-primer\|comparison-vs\|meme-skit" thumbnailInspo/CLAUDE.md | sort -u | wc -l`
Expected: `3` (enum strings match the data exactly).

- [ ] **Step 5: Commit**

```bash
git add thumbnailInspo/CLAUDE.md .claude/skills/thumbnail-and-title-generator/reference/title-engine.md .claude/skills/thumbnail-and-title-generator/reference/inspiration-mimicry.md
git commit -m "docs(thumbnail): wire title-shape pairing into cataloging contract + skill"
```

---

## Self-Review

**Spec coverage:**
- Schema (3 fields) → Task 1 (title) + Task 3 (shape/pattern). ✓
- 14-shape / 5-pattern enums → Global Constraints + Task 2 validation + Task 3 schema. ✓
- Author-time prior-not-mandate → Task 5 Step 2. ✓
- Workflow shape (Phase 0 join, fan-out classify, critic, regen+docs) → Tasks 1, 3 (fan-out + critic), 4, 5. ✓
- `build_readme.py` column + labels → Task 4. ✓
- Forward path → Task 5 Step 1 (backfill step + classification in cataloging contract). Note: spec's "`fetch.py` change" was dropped — title is already captured in manifests; documented in Global Constraints. ✓
- `title-engine.md` + `inspiration-mimicry.md` → Task 5. ✓
- Success criteria (389 entries classified, README labels, spot-check) → Task 3 Step 5, Task 4 Step 5. ✓

**Placeholder scan:** the only intentional placeholder is the `CATALOG_FILES` literal in the Task 3 workflow script, filled from Task 3 Step 1's command output — not a code gap.

**Type consistency:** `inject_titles(catalog_dir, lib_dir)`, `apply(classifications, catalog_dir) -> (int, list)`, `render(entries) -> str` are referenced consistently across tasks and tests. Enum string sets in `apply_classifications.py` match the workflow schema `enum` lists and the doc lists verbatim.
