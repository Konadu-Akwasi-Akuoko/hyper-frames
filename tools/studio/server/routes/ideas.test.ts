// Route-level tests for the kind-suggestion provenance + promote carry-through.
// These drive the REAL Hono handlers (not a hand-copied SQL mirror) so a
// regression in routes/ideas.ts is actually caught. An in-memory singleton DB
// is shared between the test and the handlers via STUDIO_DB.
process.env.STUDIO_DB = ":memory:";

import { test, expect } from "bun:test";
import app from "./ideas";
import { getDb } from "../lib/db";

interface KindRow {
  status?: string;
  kind: string;
  kind_source: string | null;
  kind_why: string | null;
}

function insertIdea(
  id: string,
  fields: { kind?: string; kind_source?: string | null; kind_why?: string | null; status?: string } = {},
): void {
  getDb().run(
    "INSERT INTO ideas (id,type,kind,kind_source,kind_why,status,title,first_seen) VALUES (?,?,?,?,?,?,?,?)",
    [
      id,
      "trend",
      fields.kind ?? "unset",
      fields.kind_source ?? null,
      fields.kind_why ?? null,
      fields.status ?? "new",
      "Route idea " + id,
      "2026-06-22T00:00:00Z",
    ],
  );
}

function patch(id: string, body: unknown): Promise<Response> {
  return Promise.resolve(
    app.request(`/${id}`, {
      method: "PATCH",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(body),
    }),
  );
}

test("PATCH kind stamps human provenance and clears kind_why", async () => {
  insertIdea("r1", { kind: "short", kind_source: "ai", kind_why: "tight single-mechanism" });
  const res = await patch("r1", { kind: "long" });
  expect(res.status).toBe(200);
  const row = getDb()
    .query("SELECT kind, kind_source, kind_why FROM ideas WHERE id=?")
    .get("r1") as KindRow;
  expect(row.kind).toBe("long");
  expect(row.kind_source).toBe("human");
  expect(row.kind_why).toBeNull();
});

test("PATCH kind='unset' clears provenance", async () => {
  insertIdea("r2", { kind: "long", kind_source: "human" });
  const res = await patch("r2", { kind: "unset" });
  expect(res.status).toBe(200);
  const row = getDb()
    .query("SELECT kind, kind_source FROM ideas WHERE id=?")
    .get("r2") as KindRow;
  expect(row.kind).toBe("unset");
  expect(row.kind_source).toBeNull();
});

test("PATCH with only status leaves kind provenance untouched", async () => {
  insertIdea("r3", { kind: "short", kind_source: "ai", kind_why: "why short" });
  const res = await patch("r3", { status: "keep" });
  expect(res.status).toBe(200);
  const row = getDb()
    .query("SELECT status, kind, kind_source, kind_why FROM ideas WHERE id=?")
    .get("r3") as KindRow;
  expect(row.status).toBe("keep");
  expect(row.kind).toBe("short");
  expect(row.kind_source).toBe("ai");
  expect(row.kind_why).toBe("why short");
});

test("promote carries kind + kind_source into board_overlay", async () => {
  insertIdea("r4", { kind: "series", kind_source: "ai" });
  const res = await app.request("/r4/promote", { method: "POST" });
  expect(res.status).toBe(201);
  const { data } = (await res.json()) as { data: { slug: string } };
  const overlay = getDb()
    .query("SELECT kind, kind_source FROM board_overlay WHERE slug=?")
    .get(data.slug) as KindRow;
  expect(overlay.kind).toBe("series");
  expect(overlay.kind_source).toBe("ai");
  const idea = getDb()
    .query("SELECT status FROM ideas WHERE id=?")
    .get("r4") as { status: string };
  expect(idea.status).toBe("promoted");
});
