import { Hono } from "hono";
import path from "node:path";
import { readdir } from "node:fs/promises";
import { ApiError, ok } from "../lib/response";
import { VIDEOS_ROOT, SLUG_RE, resolveSlug } from "../lib/paths";

const app = new Hono();

app.get("/", async (c) => {
  const entries = await readdir(VIDEOS_ROOT, { withFileTypes: true });
  const videos = await Promise.all(
    entries
      .filter((e) => e.isDirectory() && SLUG_RE.test(e.name))
      .map(async (e) => {
        const slug = e.name;
        const dir = path.join(VIDEOS_ROOT, slug);
        const [hasAudio, hasTranscript, hasCuts] = await Promise.all([
          Bun.file(path.join(dir, "audio/voiceover.mp3")).exists(),
          Bun.file(path.join(dir, "transcript.json")).exists(),
          Bun.file(path.join(dir, "cuts.json")).exists(),
        ]);
        return { slug, hasAudio, hasTranscript, hasCuts };
      }),
  );
  videos.sort((a, b) => a.slug.localeCompare(b.slug));
  return ok(c, { videos });
});

app.get("/:slug/audio", async (c) => {
  const slug = c.req.param("slug");
  const dir = await resolveSlug(slug);
  const audioPath = path.join(dir, "audio/voiceover.mp3");
  const file = Bun.file(audioPath);
  if (!(await file.exists())) {
    throw new ApiError("NOT_FOUND", "voiceover.mp3 not found", 404);
  }
  // Raw audio stream — intentionally bypasses the ApiResponse envelope.
  return new Response(file, {
    headers: { "Content-Type": "audio/mpeg" },
  });
});

export default app;
