import { Hono } from "hono";
import { getDb } from "../lib/db";
import { ok, ApiError } from "../lib/response";
import { ChannelBody } from "../lib/schemas";

const app = new Hono();

interface ChannelRow {
  handle: string;
  url: string;
  note: string | null;
  active: number;
}

app.get("/", (c) => {
  const rows = getDb()
    .query("SELECT handle,url,note,active FROM channels ORDER BY handle")
    .all() as ChannelRow[];
  return ok(
    c,
    rows.map((r) => ({ ...r, active: !!r.active })),
  );
});

app.post("/", async (c) => {
  const b = ChannelBody.parse(await c.req.json());
  const url = b.url ?? `https://www.youtube.com/${b.handle}/videos`;
  getDb().run(
    "INSERT OR REPLACE INTO channels (handle,url,note,active) VALUES (?,?,?,?)",
    [b.handle, url, b.note ?? null, b.active === false ? 0 : 1],
  );
  return ok(c, { handle: b.handle }, 201);
});

app.patch("/:handle", async (c) => {
  const handle = c.req.param("handle");
  const db = getDb();
  if (!db.query("SELECT handle FROM channels WHERE handle=?").get(handle)) {
    throw new ApiError("NOT_FOUND", "channel not found", 404);
  }
  const b = ChannelBody.partial().parse(await c.req.json());
  db.run(
    "UPDATE channels SET url=COALESCE(?,url), note=COALESCE(?,note), active=COALESCE(?,active) WHERE handle=?",
    [
      b.url ?? null,
      b.note ?? null,
      b.active === undefined ? null : b.active ? 1 : 0,
      handle,
    ],
  );
  return ok(c, { handle });
});

app.delete("/:handle", (c) => {
  const handle = c.req.param("handle");
  getDb().run("DELETE FROM channels WHERE handle=?", [handle]);
  return ok(c, { handle });
});

export default app;
