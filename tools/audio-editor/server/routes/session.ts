import { Hono } from "hono";
import path from "node:path";
import { rename } from "node:fs/promises";
import { ApiError, ok } from "../lib/response";
import { resolveSlug, firstExisting } from "../lib/paths";
import { transcriptSchema, cutsFileSchema } from "../lib/schemas";

const app = new Hono();

app.get("/:slug", async (c) => {
  const slug = c.req.param("slug");
  const dir = await resolveSlug(slug);

  const transcriptPath = await firstExisting(dir, ["transcript.raw.json", "transcript.json"]);
  if (!transcriptPath) {
    throw new ApiError("NOT_FOUND", "no transcript (transcript.raw.json / transcript.json) found", 404);
  }
  const transcript = transcriptSchema.parse(await Bun.file(transcriptPath).json());

  const cutsFile = Bun.file(path.join(dir, "cuts.json"));
  const cuts = (await cutsFile.exists())
    ? cutsFileSchema.parse(await cutsFile.json())
    : null;

  return ok(c, {
    slug,
    transcript,
    cuts,
    audioUrl: `/api/videos/${slug}/audio`,
  });
});

app.put("/:slug/cuts", async (c) => {
  const slug = c.req.param("slug");
  const dir = await resolveSlug(slug);

  const body = await c.req.json();
  const parsed = cutsFileSchema.parse(body);

  const finalPath = path.join(dir, "cuts.json");
  const tmpPath = `${finalPath}.tmp`;
  await Bun.write(tmpPath, JSON.stringify(parsed, null, 2));
  await rename(tmpPath, finalPath);

  return ok(c, { slug, savedAt: new Date().toISOString() });
});

export default app;
