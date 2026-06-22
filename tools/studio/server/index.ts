import { Hono } from "hono";
import { logger } from "hono/logger";
import { ZodError } from "zod";
import { ApiError, ok, fail } from "./lib/response";
import { getDb } from "./lib/db";
import { STAGES } from "./lib/stages";
import boardRoutes from "./routes/board";
import ideasRoutes from "./routes/ideas";
import channelsRoutes from "./routes/channels";
import discoveryRoutes from "./routes/discovery";

// Open + migrate the local SQLite file at boot.
getDb();

const app = new Hono();
app.use(logger());

app.get("/api/health", (c) => ok(c, { ok: true }));
app.get("/api/stages", (c) => ok(c, STAGES));

app.route("/api/board", boardRoutes);
app.route("/api/ideas", ideasRoutes);
app.route("/api/channels", channelsRoutes);
app.route("/api/discovery", discoveryRoutes);

app.notFound((c) => fail(c, "NOT_FOUND", "route not found", 404));

app.onError((err, c) => {
  if (err instanceof ApiError) {
    return fail(c, err.code, err.message, err.httpStatus, err.details);
  }
  if (err instanceof ZodError) {
    return fail(c, "VALIDATION", "validation failed", 400, err.issues);
  }
  console.error("[api] uncaught error:", err);
  return fail(c, "INTERNAL", "internal error", 500);
});

const PORT = Number(process.env.STUDIO_API_PORT ?? 3273);
export default { port: PORT, fetch: app.fetch };
