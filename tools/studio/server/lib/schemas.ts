import { z } from "zod";

export const IDEA_TYPES = ["mirror", "comment_demand", "trend", "manual"] as const;
export const IDEA_KINDS = ["unset", "long", "short", "series"] as const;
export const IDEA_STATUSES = ["new", "keep", "rejected", "promoted"] as const;

export const IdeaTriageBody = z.object({
  status: z.enum(["new", "keep", "rejected"]).optional(),
  kind: z.enum(IDEA_KINDS).optional(),
  notes: z.string().optional(),
});
export type IdeaTriageBody = z.infer<typeof IdeaTriageBody>;

export const IdeaCreateBody = z.object({
  title: z.string().min(1),
  type: z.enum(IDEA_TYPES).default("manual"),
  rationale: z.string().optional(),
  source: z.string().optional(),
  source_url: z.string().optional(),
  source_title: z.string().optional(),
  notes: z.string().optional(),
});
export type IdeaCreateBody = z.infer<typeof IdeaCreateBody>;

export const PruneBody = z.object({
  olderThanDays: z.number().int().positive().default(90),
});

export const BoardCardCreateBody = z.object({
  slug: z.string().regex(/^[a-z0-9][a-z0-9-]*$/),
  title: z.string().optional(),
  date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  stage: z.string().default("idea"),
});

export const SetCardBody = z.object({
  stage: z.string().optional(),
  notes: z.string().optional(),
  title: z.string().optional(),
});

export const ChannelBody = z.object({
  handle: z.string().min(1),
  url: z.string().optional(),
  note: z.string().optional(),
  active: z.boolean().optional(),
});
