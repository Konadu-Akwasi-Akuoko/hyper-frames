import { Hono } from "hono";
import { getDb } from "../lib/db";
import { ok, ApiError } from "../lib/response";
import { IdeaTriageBody, IdeaCreateBody, PruneBody } from "../lib/schemas";
import { mapIdeaRow, nowISO, todayISO, uuid, kebabSlug } from "../lib/util";
import type { IdeaRow } from "../lib/util";

const app = new Hono();

app.get("/", (c) => {
  const db = getDb();
  const statusParam = c.req.query("status");
  const typeParam = c.req.query("type");
  const statuses = statusParam ? statusParam.split(",") : ["new", "keep"];
  const placeholders = statuses.map(() => "?").join(",");
  let sql = `SELECT * FROM ideas WHERE status IN (${placeholders})`;
  const args: (string | null)[] = [...statuses];
  if (typeParam) {
    sql += " AND type=?";
    args.push(typeParam);
  }
  sql += " ORDER BY first_seen DESC";
  const rows = db.query(sql).all(...args) as IdeaRow[];
  return ok(c, rows.map(mapIdeaRow));
});

app.get("/counts", (c) => {
  const rows = getDb()
    .query(
      "SELECT type, count(*) n FROM ideas WHERE status IN ('new','keep') GROUP BY type",
    )
    .all() as { type: string; n: number }[];
  const byType: Record<string, number> = {};
  let total = 0;
  for (const r of rows) {
    byType[r.type] = r.n;
    total += r.n;
  }
  return ok(c, { total, byType });
});

app.post("/", async (c) => {
  const body = IdeaCreateBody.parse(await c.req.json());
  const db = getDb();
  const id = uuid();
  db.run(
    "INSERT INTO ideas (id,type,kind,status,title,rationale,source,source_url,source_title,first_seen,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
    [
      id,
      body.type,
      "unset",
      "new",
      body.title,
      body.rationale ?? null,
      body.source ?? null,
      body.source_url ?? null,
      body.source_title ?? null,
      nowISO(),
      body.notes ?? null,
    ],
  );
  const row = db.query("SELECT * FROM ideas WHERE id=?").get(id) as IdeaRow;
  return ok(c, mapIdeaRow(row), 201);
});

app.patch("/:id", async (c) => {
  const id = c.req.param("id");
  const body = IdeaTriageBody.parse(await c.req.json());
  const db = getDb();
  if (!db.query("SELECT id FROM ideas WHERE id=?").get(id)) {
    throw new ApiError("NOT_FOUND", "idea not found", 404);
  }
  db.run(
    "UPDATE ideas SET status=COALESCE(?,status), notes=COALESCE(?,notes) WHERE id=?",
    [body.status ?? null, body.notes ?? null, id],
  );
  if (body.kind !== undefined) {
    db.run(
      "UPDATE ideas SET kind=?, kind_source=?, kind_why=NULL WHERE id=?",
      [body.kind, body.kind === "unset" ? null : "human", id],
    );
  }
  const row = db.query("SELECT * FROM ideas WHERE id=?").get(id) as IdeaRow;
  return ok(c, mapIdeaRow(row));
});

app.post("/:id/promote", (c) => {
  const id = c.req.param("id");
  const db = getDb();
  const idea = db.query("SELECT * FROM ideas WHERE id=?").get(id) as
    | IdeaRow
    | undefined;
  if (!idea) throw new ApiError("NOT_FOUND", "idea not found", 404);

  const date = todayISO();
  const base = kebabSlug(idea.title) || "idea";
  let slug = `${base}-${date}`;
  let n = 2;
  while (db.query("SELECT slug FROM board_overlay WHERE slug=?").get(slug)) {
    slug = `${base}-${n}-${date}`;
    n++;
  }
  db.run(
    "INSERT INTO board_overlay (slug,title,stage,notes,created_from_idea,kind,kind_source,updated_at) VALUES (?,?,?,?,?,?,?,?)",
    [slug, idea.title, "idea", null, id, idea.kind, idea.kind_source, nowISO()],
  );
  db.run("UPDATE ideas SET status='promoted', promoted_slug=? WHERE id=?", [
    slug,
    id,
  ]);
  return ok(c, { slug, name: slug }, 201);
});

app.post("/prune", async (c) => {
  const raw = await c.req.json().catch(() => ({}));
  const body = PruneBody.parse(raw);
  const cutoff = new Date(
    Date.now() - body.olderThanDays * 86_400_000,
  ).toISOString();
  const res = getDb().run(
    "DELETE FROM raw_signal WHERE judged_at IS NOT NULL AND fetched_at < ?",
    [cutoff],
  );
  return ok(c, { deleted: res.changes });
});

export default app;
