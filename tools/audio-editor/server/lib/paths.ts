import path from "node:path";
import { stat } from "node:fs/promises";
import { ApiError } from "./response";

export const VIDEOS_ROOT = path.resolve(import.meta.dir, "../../../../videos");
export const SLUG_RE = /^[a-z0-9][a-z0-9-]*$/;

export async function resolveSlug(slug: string): Promise<string> {
  if (!SLUG_RE.test(slug)) {
    throw new ApiError("BAD_SLUG", "invalid slug", 400);
  }
  const resolved = path.resolve(VIDEOS_ROOT, slug);
  if (!resolved.startsWith(VIDEOS_ROOT + path.sep)) {
    throw new ApiError("BAD_SLUG", "slug escapes videos root", 400);
  }
  try {
    const s = await stat(resolved);
    if (!s.isDirectory()) {
      throw new ApiError("NOT_FOUND", `video '${slug}' not found`, 404);
    }
  } catch (e: unknown) {
    if (e instanceof ApiError) throw e;
    throw new ApiError("NOT_FOUND", `video '${slug}' not found`, 404);
  }
  return resolved;
}

/**
 * Return the absolute path of the first name in `names` that exists under `dir`,
 * or null if none do. Used to prefer raw-timeline artifacts (raw.mp3,
 * transcript.raw.json) over their cut counterparts so the editor stays aligned
 * with cuts.json after a render.
 */
export async function firstExisting(dir: string, names: string[]): Promise<string | null> {
  for (const name of names) {
    const p = path.join(dir, name);
    if (await Bun.file(p).exists()) return p;
  }
  return null;
}
