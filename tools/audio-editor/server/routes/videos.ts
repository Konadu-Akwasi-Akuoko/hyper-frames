import { Hono } from "hono";
import path from "node:path";
import { readdir } from "node:fs/promises";
import { ApiError, ok } from "../lib/response";
import { VIDEOS_ROOT, SLUG_RE, resolveSlug, firstExisting } from "../lib/paths";

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
          firstExisting(dir, ["audio/raw.mp3", "audio/voiceover.mp3"]).then(Boolean),
          firstExisting(dir, ["transcript.raw.json", "transcript.json"]).then(Boolean),
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
  // Prefer raw.mp3 so the waveform stays on the same timeline as cuts.json;
  // fall back to voiceover.mp3 for videos that only have the cleaned output.
  const audioPath = await firstExisting(dir, ["audio/raw.mp3", "audio/voiceover.mp3"]);
  if (!audioPath) {
    throw new ApiError("NOT_FOUND", "no audio (raw.mp3 / voiceover.mp3) found", 404);
  }
  // Raw audio stream — intentionally bypasses the ApiResponse envelope.
  return new Response(Bun.file(audioPath), {
    headers: { "Content-Type": "audio/mpeg" },
  });
});

export default app;
