import { Hono } from "hono";
import { logger } from "hono/logger";
import { ZodError } from "zod";
import sessionRoutes from "./routes/session";
import videoRoutes from "./routes/videos";
import { ApiError, fail } from "./lib/response";

const app = new Hono();
app.use(logger());

app.route("/api/session", sessionRoutes);
app.route("/api/videos", videoRoutes);

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

export default { port: 3001, fetch: app.fetch };
