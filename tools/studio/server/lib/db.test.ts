import { test, expect } from "bun:test";
import { openDb } from "./db";
import { rawSignalId } from "./ids";

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
