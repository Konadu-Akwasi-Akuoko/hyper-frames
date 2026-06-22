import { Hono } from "hono";
import path from "node:path";
import { getDb } from "../lib/db";
import { ok, ApiError } from "../lib/response";

const DISCOVERY_DIR = path.resolve(import.meta.dir, "../../discovery");
const DB_PATH =
  process.env.STUDIO_DB ?? path.resolve(import.meta.dir, "../../studio.db");

function unjudgedCounts() {
  const rows = getDb()
    .query(
      "SELECT source, count(*) n FROM raw_signal WHERE judged_at IS NULL GROUP BY source",
    )
    .all() as { source: string; n: number }[];
  const bySource: Record<string, number> = {};
  let total = 0;
  for (const r of rows) {
    bySource[r.source] = r.n;
    total += r.n;
  }
  return { total, bySource };
}

const app = new Hono();

app.get("/raw-counts", (c) => ok(c, unjudgedCounts()));

interface RunBody {
  sources?: string;
  videosPerChannel?: number;
  commentsPerVideo?: number;
  noComments?: boolean;
}

/**
 * Trigger a serial, bounded discovery run by shelling out to the Python CLI.
 * Runs synchronously (a local single-user tool); the UI shows a spinner. The
 * server never fabricates intelligence — it only writes raw_signal via the CLI.
 */
app.post("/run", async (c) => {
  const body = (await c.req.json().catch(() => ({}))) as RunBody;
  const args = ["run", "studio-discover", "--db", DB_PATH];
  if (body.sources) args.push("--sources", String(body.sources));
  if (body.videosPerChannel)
    args.push("--videos-per-channel", String(body.videosPerChannel));
  if (body.commentsPerVideo)
    args.push("--comments-per-video", String(body.commentsPerVideo));
  if (body.noComments) args.push("--no-comments");

  if (!Bun.which("uv")) {
    throw new ApiError("DISCOVERY_SPAWN", "uv not found on PATH", 500);
  }
  const proc = Bun.spawn(["uv", ...args], {
    cwd: DISCOVERY_DIR,
    stdout: "pipe",
    stderr: "pipe",
  });

  const [out, err] = await Promise.all([
    new Response(proc.stdout).text(),
    new Response(proc.stderr).text(),
  ]);
  const code = await proc.exited;
  if (code !== 0) {
    const lastLine = err.trim().split("\n").slice(-1)[0] || "discovery failed";
    throw new ApiError("DISCOVERY_FAILED", lastLine, 500, {
      stderr: err.slice(-2000),
    });
  }

  return ok(c, { ...unjudgedCounts(), log: out.slice(-4000) });
});

export default app;
