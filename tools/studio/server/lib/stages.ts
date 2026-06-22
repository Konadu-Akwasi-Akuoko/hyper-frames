export type Who = "human" | "ai";
export interface StageDef {
  id: string;
  label: string;
  who: Who;
}

/** The 12 production stages, ids + labels ported verbatim from kanban.html. */
export const STAGES: StageDef[] = [
  { id: "idea", label: "Idea", who: "human" },
  { id: "research", label: "Research", who: "human" },
  { id: "script", label: "Script", who: "ai" },
  { id: "voiceover", label: "Voiceover", who: "ai" },
  { id: "compose", label: "Compose", who: "ai" },
  { id: "review", label: "Review", who: "human" },
  { id: "thumbnail", label: "Thumbnail", who: "ai" },
  { id: "translate", label: "Captions", who: "ai" },
  { id: "render", label: "Render", who: "ai" },
  { id: "published", label: "Published", who: "human" },
  { id: "publish-qa", label: "Publish QA", who: "ai" },
  { id: "shorts", label: "Shorts", who: "ai" },
];

export const STAGE_IDS: string[] = STAGES.map((s) => s.id);

export function stageIndex(id: string): number {
  return STAGE_IDS.indexOf(id);
}

export function isStage(id: string): boolean {
  return STAGE_IDS.includes(id);
}

/** Post-render milestones are human-moved, never scanned; exempt from drift. */
export const MILESTONE_STAGES = ["published", "publish-qa", "shorts"];

/**
 * The scanned artifact ladder, in order. `translate`/`published`/`publish-qa`/
 * `shorts` are stage-derived (not probed on disk), so they are not here — this
 * matches kanban.html's `computeSuggested` reachable set.
 */
export const SCANNED_LADDER = [
  "research",
  "script",
  "voiceover",
  "compose",
  "review",
  "thumbnail",
  "render",
];

/** Last ladder stage that is `present`, else `idea` (kanban computeSuggested). */
export function computeSuggested(
  artifacts: Record<string, string>,
): string {
  let suggested = "idea";
  for (const stage of SCANNED_LADDER) {
    if (artifacts[stage] === "present") suggested = stage;
  }
  return suggested;
}

/** Desk-meter fill fraction: cold idea (0) climbing to red on-air (1). */
export function stageProgress(stage: string): number {
  const idx = stageIndex(stage);
  if (idx < 0) return 0;
  return idx / (STAGES.length - 1);
}
