import { readdir, stat, readFile } from "node:fs/promises";
import path from "node:path";
import { computeSuggested } from "./stages";

export type ArtifactStatus = "present" | "partial" | "missing" | "unknown";

export interface ScannedVideo {
  slug: string;
  date: string;
  /** folder name `<slug>-<date>` */
  name: string;
  artifacts: Record<string, ArtifactStatus>;
  suggestedStage: string;
  title?: string;
}

const DIR_RE = /^(.+)-(\d{4}-\d{2}-\d{2})$/;

function isENOENT(e: unknown): boolean {
  return (
    typeof e === "object" && e !== null && (e as { code?: string }).code === "ENOENT"
  );
}

async function exists(dir: string, rel: string): Promise<ArtifactStatus> {
  try {
    await stat(path.join(dir, rel));
    return "present";
  } catch (e) {
    return isENOENT(e) ? "missing" : "unknown";
  }
}

/** present iff mp3 + transcript + narration-map; partial if mp3+transcript; else missing. */
async function voiceoverStatus(dir: string): Promise<ArtifactStatus> {
  const mp3 = await exists(dir, "audio/voiceover.mp3");
  const tx = await exists(dir, "transcript.json");
  const nm = await exists(dir, "narration-map.json");
  if (mp3 === "missing" && tx === "missing") return "missing";
  if (mp3 === "present" && tx === "present" && nm === "present") return "present";
  return "partial";
}

/**
 * present iff index.html has real mounted content — a `.clip` element or a
 * `data-composition-src` host — outside HTML comments. An empty `hyperframes
 * init` scaffold (whose only such markers live inside its placeholder comment)
 * is `partial`, never present; a missing file is `missing`.
 */
async function composeStatus(dir: string): Promise<ArtifactStatus> {
  let html: string;
  try {
    html = await readFile(path.join(dir, "index.html"), "utf8");
  } catch (e) {
    return isENOENT(e) ? "missing" : "unknown";
  }
  const withoutComments = html.replace(/<!--[\s\S]*?-->/g, "");
  const hasRealContent =
    /class\s*=\s*["'][^"']*\bclip\b/.test(withoutComments) ||
    /data-composition-src\s*=/.test(withoutComments);
  return hasRealContent ? "present" : "partial";
}

/** present if either compositions/sfx.html or compositions/music.html exists. */
async function reviewStatus(dir: string): Promise<ArtifactStatus> {
  const sfx = await exists(dir, "compositions/sfx.html");
  const music = await exists(dir, "compositions/music.html");
  if (sfx === "present" || music === "present") return "present";
  if (sfx === "unknown" || music === "unknown") return "unknown";
  return "missing";
}

/** 3 of thumbnail-{a,b,c}.png → present; 1-2 → partial; 0 → missing. */
async function thumbnailStatus(dir: string): Promise<ArtifactStatus> {
  let count = 0;
  for (const name of ["thumbnail-a.png", "thumbnail-b.png", "thumbnail-c.png"]) {
    if ((await exists(dir, name)) === "present") count++;
  }
  if (count === 0) return "missing";
  if (count === 3) return "present";
  return "partial";
}

/** any *.mp4 under renders/ or output/. */
async function renderStatus(dir: string): Promise<ArtifactStatus> {
  for (const folder of ["renders", "output"]) {
    try {
      const entries = await readdir(path.join(dir, folder));
      if (entries.some((n) => n.toLowerCase().endsWith(".mp4"))) return "present";
    } catch (e) {
      if (!isENOENT(e)) return "unknown";
    }
  }
  return "missing";
}

async function readOutlineH1(dir: string): Promise<string | undefined> {
  try {
    const text = await readFile(path.join(dir, "outline.md"), "utf8");
    const m = text.match(/^#\s+(.+?)(?:\s+—\s+9-beat outline)?\s*$/m);
    return m ? m[1].trim() : undefined;
  } catch {
    return undefined;
  }
}

/** Walk `videos/<slug>-<date>/` and infer artifact completion from real files. */
export async function scanVideos(root: string): Promise<ScannedVideo[]> {
  let names: string[];
  try {
    names = await readdir(root);
  } catch {
    return [];
  }
  const out: ScannedVideo[] = [];
  for (const name of names.sort()) {
    const m = name.match(DIR_RE);
    if (!m) continue;
    const full = path.join(root, name);
    try {
      if (!(await stat(full)).isDirectory()) continue;
    } catch {
      continue;
    }
    const artifacts: Record<string, ArtifactStatus> = {
      research: await exists(full, "seo/research.json"),
      script: await exists(full, "script.md"),
      voiceover: await voiceoverStatus(full),
      compose: await composeStatus(full),
      review: await reviewStatus(full),
      thumbnail: await thumbnailStatus(full),
      render: await renderStatus(full),
    };
    out.push({
      slug: m[1],
      date: m[2],
      name,
      artifacts,
      suggestedStage: computeSuggested(artifacts),
      title: await readOutlineH1(full),
    });
  }
  return out;
}
