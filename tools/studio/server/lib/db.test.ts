import { test, expect } from "bun:test";
import { Database } from "bun:sqlite";
import { openDb, migrate } from "./db";
import { rawSignalId } from "./ids";
import { IDEA_KINDS } from "./schemas";

test("migrate creates the four tables", () => {
  const db = openDb(":memory:");
  const tables = db
    .query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    .all()
    .map((r) => (r as { name: string }).name);
  expect(tables).toEqual(["board_overlay", "channels", "ideas", "raw_signal"]);
});

test("ideas table has NO score column (aggregator, never a judge)", () => {
  const db = openDb(":memory:");
  const cols = db
    .query("PRAGMA table_info(ideas)")
    .all()
    .map((r) => (r as { name: string }).name);
  expect(cols).toContain("rationale");
  expect(cols).not.toContain("score");
  expect(cols).not.toContain("rank");
});

test("an idea round-trips with kind defaulting to unset", () => {
  const db = openDb(":memory:");
  db.run(
    "INSERT INTO ideas (id,type,status,title,first_seen) VALUES (?,?,?,?,?)",
    ["i1", "trend", "new", "Test idea", "2026-06-22T00:00:00Z"],
  );
  const row = db.query("SELECT * FROM ideas WHERE id=?").get("i1") as {
    title: string;
    kind: string;
    status: string;
  };
  expect(row.title).toBe("Test idea");
  expect(row.kind).toBe("unset");
  expect(row.status).toBe("new");
});

test("ideas table has kind_source + kind_why columns (AI format provenance)", () => {
  const db = openDb(":memory:");
  const cols = db
    .query("PRAGMA table_info(ideas)")
    .all()
    .map((r) => (r as { name: string }).name);
  expect(cols).toContain("kind_source");
  expect(cols).toContain("kind_why");
});

test("board_overlay table has kind + kind_source columns (promote snapshot)", () => {
  const db = openDb(":memory:");
  const cols = db
    .query("PRAGMA table_info(board_overlay)")
    .all()
    .map((r) => (r as { name: string }).name);
  expect(cols).toContain("kind");
  expect(cols).toContain("kind_source");
});

test("migrate is idempotent — running it twice does not throw or duplicate columns", () => {
  const db = new Database(":memory:");
  migrate(db);
  const before = db
    .query("PRAGMA table_info(ideas)")
    .all()
    .map((r) => (r as { name: string }).name);
  expect(() => migrate(db)).not.toThrow();
  const after = db
    .query("PRAGMA table_info(ideas)")
    .all()
    .map((r) => (r as { name: string }).name);
  expect(after).toEqual(before);
  expect(after.filter((c) => c === "kind_source")).toHaveLength(1);
  expect(after.filter((c) => c === "kind_why")).toHaveLength(1);
});

test("promote carries kind + kind_source from the idea into board_overlay", () => {
  const db = openDb(":memory:");
  db.run(
    "INSERT INTO ideas (id,type,kind,status,title,first_seen,kind_source,kind_why) VALUES (?,?,?,?,?,?,?,?)",
    [
      "i-short",
      "trend",
      "short",
      "keep",
      "Tap-to-pay explainer",
      "2026-06-22T00:00:00Z",
      "ai",
      "single tight mechanism, broad appeal",
    ],
  );
  const idea = db.query("SELECT * FROM ideas WHERE id=?").get("i-short") as {
    title: string;
    kind: string;
    kind_source: string | null;
  };
  // Same INSERT-with-kind SQL the POST /:id/promote route runs.
  db.run(
    "INSERT INTO board_overlay (slug,title,stage,notes,created_from_idea,kind,kind_source,updated_at) VALUES (?,?,?,?,?,?,?,?)",
    [
      "tap-to-pay-explainer-2026-06-22",
      idea.title,
      "idea",
      null,
      "i-short",
      idea.kind,
      idea.kind_source,
      "2026-06-22T00:00:00Z",
    ],
  );
  const overlay = db
    .query("SELECT * FROM board_overlay WHERE created_from_idea=?")
    .get("i-short") as { kind: string; kind_source: string | null };
  expect(overlay.kind).toBe("short");
  expect(overlay.kind_source).toBe("ai");
});

/** Mirrors the PATCH /:id route's kind branch: a kind change stamps provenance
 *  (kind_source='human', or NULL when 'unset') and clears kind_why. `kind` is
 *  typed as the enum union exactly like the route's `body.kind`. */
function patchKind(db: Database, id: string, kind: (typeof IDEA_KINDS)[number]): void {
  db.run("UPDATE ideas SET kind=?, kind_source=?, kind_why=NULL WHERE id=?", [
    kind,
    kind === "unset" ? null : "human",
    id,
  ]);
}

test("PATCH kind stamps kind_source='human' and clears kind_why", () => {
  const db = openDb(":memory:");
  db.run(
    "INSERT INTO ideas (id,type,kind,status,title,first_seen,kind_source,kind_why) VALUES (?,?,?,?,?,?,?,?)",
    ["i2", "trend", "short", "new", "Test idea", "2026-06-22T00:00:00Z", "ai", "ai guessed short"],
  );
  patchKind(db, "i2", "long");
  const row = db.query("SELECT * FROM ideas WHERE id=?").get("i2") as {
    kind: string;
    kind_source: string | null;
    kind_why: string | null;
  };
  expect(row.kind).toBe("long");
  expect(row.kind_source).toBe("human");
  expect(row.kind_why).toBeNull();
});

test("PATCH kind='unset' sets kind_source=NULL", () => {
  const db = openDb(":memory:");
  db.run(
    "INSERT INTO ideas (id,type,kind,status,title,first_seen,kind_source,kind_why) VALUES (?,?,?,?,?,?,?,?)",
    ["i3", "trend", "short", "new", "Test idea", "2026-06-22T00:00:00Z", "ai", "ai guessed short"],
  );
  patchKind(db, "i3", "unset");
  const row = db.query("SELECT * FROM ideas WHERE id=?").get("i3") as {
    kind: string;
    kind_source: string | null;
    kind_why: string | null;
  };
  expect(row.kind).toBe("unset");
  expect(row.kind_source).toBeNull();
  expect(row.kind_why).toBeNull();
});

test("PATCH with only status/notes leaves kind_source + kind_why untouched", () => {
  const db = openDb(":memory:");
  db.run(
    "INSERT INTO ideas (id,type,kind,status,title,first_seen,kind_source,kind_why) VALUES (?,?,?,?,?,?,?,?)",
    ["i4", "trend", "short", "new", "Test idea", "2026-06-22T00:00:00Z", "ai", "ai guessed short"],
  );
  // Mirrors the always-run status/notes UPDATE of the PATCH /:id route; the
  // kind branch is skipped when body.kind is undefined.
  db.run(
    "UPDATE ideas SET status=COALESCE(?,status), notes=COALESCE(?,notes) WHERE id=?",
    ["keep", null, "i4"],
  );
  const row = db.query("SELECT * FROM ideas WHERE id=?").get("i4") as {
    status: string;
    kind: string;
    kind_source: string | null;
    kind_why: string | null;
  };
  expect(row.status).toBe("keep");
  expect(row.kind).toBe("short");
  expect(row.kind_source).toBe("ai");
  expect(row.kind_why).toBe("ai guessed short");
});

test("raw_unjudged partial index exists for the delta read", () => {
  const db = openDb(":memory:");
  const idx = db
    .query("SELECT name FROM sqlite_master WHERE type='index' AND name=?")
    .get("idx_raw_unjudged");
  expect(idx).toBeTruthy();
});

test("rawSignalId matches the Python keyspace (known vectors)", () => {
  // Computed identically by studio_discovery.ids.raw_signal_id (asserted there).
  expect(rawSignalId("hn", "abc123")).toBe("2e7b7faaccf5c9f4");
  expect(rawSignalId("youtube:@Fireship", "Sntj4HmuykI")).toBe(
    "dd759ac2d09788e3",
  );
});
