/** The scanned artifact ladder (mirrors server stages.SCANNED_LADDER). */
export const SCANNED_LADDER = [
  "research",
  "script",
  "voiceover",
  "compose",
  "review",
  "thumbnail",
  "render",
];

/** Stages with no on-disk scan; shown as ON-AIR rather than artifact dots. */
export const ONAIR_STAGES = ["published", "publish-qa"];

export const TYPE_LABEL: Record<string, string> = {
  mirror: "mirror",
  comment_demand: "comment-demand",
  trend: "trend",
  manual: "manual",
};
