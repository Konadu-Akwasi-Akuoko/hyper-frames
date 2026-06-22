import path from "node:path";
import { stat } from "node:fs/promises";
import { ApiError } from "./response";

/** Repo `videos/` root: server/lib → tools/studio → tools → repo → videos. */
export const VIDEOS_ROOT = path.resolve(import.meta.dir, "../../../../videos");
export const SLUG_RE = /^[a-z0-9][a-z0-9-]*$/;

export function assertSlug(slug: string): void {
  if (!SLUG_RE.test(slug)) {
    throw new ApiError("BAD_SLUG", "invalid slug", 400);
  }
}

/** Resolve a `<slug>-<date>` folder under VIDEOS_ROOT, guarding traversal. */
export async function resolveVideoDir(name: string): Promise<string | null> {
  const resolved = path.resolve(VIDEOS_ROOT, name);
  if (
    resolved !== VIDEOS_ROOT &&
    !resolved.startsWith(VIDEOS_ROOT + path.sep)
  ) {
    throw new ApiError("BAD_SLUG", "path escapes videos root", 400);
  }
  try {
    const s = await stat(resolved);
    return s.isDirectory() ? resolved : null;
  } catch {
    return null;
  }
}
