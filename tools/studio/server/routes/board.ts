import { Hono } from "hono";
import { getDb } from "../lib/db";
import { scanVideos } from "../lib/scan";
import { VIDEOS_ROOT } from "../lib/paths";
import { ok, ApiError } from "../lib/response";
import {
  stageProgress,
  stageIndex,
  isStage,
  stageDriftsFrom,
} from "../lib/stages";
import { nowISO } from "../lib/util";
import { BoardCardCreateBody, SetCardBody } from "../lib/schemas";

const DIR_RE = /^(.+)-(\d{4}-\d{2}-\d{2})$/;

interface OverlayRow {
  slug: string;
  title: string | null;
  stage: string | null;
  notes: string | null;
  created_from_idea: string | null;
  kind: string | null;
  kind_source: string | null;
  updated_at: string;
}

async function buildBoard() {
  const db = getDb();
  const scanned = await scanVideos(VIDEOS_ROOT);
  const scannedByName = new Map(scanned.map((s) => [s.name, s]));
  const overlays = db
    .query("SELECT * FROM board_overlay")
    .all() as OverlayRow[];
  const overlayByName = new Map(overlays.map((o) => [o.slug, o]));

  const keys = new Set<string>([
    ...scannedByName.keys(),
    ...overlayByName.keys(),
  ]);

  const cards = [];
  for (const key of keys) {
    const s = scannedByName.get(key);
    const o = overlayByName.get(key);
    const m = key.match(DIR_RE);
    const slug = s?.slug ?? (m ? m[1] : key);
    const date = s?.date ?? (m ? m[2] : "");
    const suggestedStage = s?.suggestedStage ?? null;
    const manualStage = o?.stage ?? null;
    const stage = manualStage ?? suggestedStage ?? "idea";
    const hasDrift =
      manualStage != null &&
      s != null &&
      stageDriftsFrom(manualStage, s.artifacts);
    cards.push({
      slug,
      date,
      name: key,
      stage,
      artifacts: s?.artifacts ?? {},
      suggestedStage,
      hasDrift,
      progress: stageProgress(stage),
      title: o?.title ?? s?.title ?? slug,
      notes: o?.notes ?? null,
      fromIdea: o?.created_from_idea ?? null,
      kind: o?.kind ?? "unset",
      kindSource: o?.kind_source ?? null,
      onDisk: s != null,
    });
  }
  cards.sort(
    (a, b) =>
      stageIndex(a.stage) - stageIndex(b.stage) || a.date.localeCompare(b.date),
  );
  return cards;
}

const app = new Hono();

app.get("/", async (c) => ok(c, await buildBoard()));
app.post("/sync", async (c) => ok(c, await buildBoard()));

app.post("/", async (c) => {
  const body = BoardCardCreateBody.parse(await c.req.json());
  if (body.stage && !isStage(body.stage)) {
    throw new ApiError("BAD_STAGE", `unknown stage '${body.stage}'`, 400);
  }
  const name = `${body.slug}-${body.date}`;
  const db = getDb();
  if (db.query("SELECT slug FROM board_overlay WHERE slug=?").get(name)) {
    throw new ApiError("EXISTS", `card '${name}' already exists`, 409);
  }
  db.run(
    "INSERT INTO board_overlay (slug,title,stage,notes,created_from_idea,updated_at) VALUES (?,?,?,?,?,?)",
    [name, body.title ?? null, body.stage ?? "idea", null, null, nowISO()],
  );
  return ok(c, { name }, 201);
});

app.patch("/:name", async (c) => {
  const name = c.req.param("name");
  const body = SetCardBody.parse(await c.req.json());
  if (body.stage && !isStage(body.stage)) {
    throw new ApiError("BAD_STAGE", `unknown stage '${body.stage}'`, 400);
  }
  const db = getDb();
  const existing = db
    .query("SELECT slug FROM board_overlay WHERE slug=?")
    .get(name);
  if (existing) {
    db.run(
      "UPDATE board_overlay SET stage=COALESCE(?,stage), notes=COALESCE(?,notes), title=COALESCE(?,title), updated_at=? WHERE slug=?",
      [body.stage ?? null, body.notes ?? null, body.title ?? null, nowISO(), name],
    );
  } else {
    db.run(
      "INSERT INTO board_overlay (slug,title,stage,notes,created_from_idea,updated_at) VALUES (?,?,?,?,?,?)",
      [name, body.title ?? null, body.stage ?? null, body.notes ?? null, null, nowISO()],
    );
  }
  return ok(c, { name });
});

app.delete("/:name", (c) => {
  const name = c.req.param("name");
  getDb().run("DELETE FROM board_overlay WHERE slug=?", [name]);
  return ok(c, { name });
});

export default app;
