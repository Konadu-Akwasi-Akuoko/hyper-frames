import { z } from "zod";

// Scribe v2 emits two row shapes: "word" rows carry speaker_id + logprob;
// "spacing" rows are bare timing markers. Modeled as a discriminated union
// so neither shape leaks optional fields it never has.
export const transcriptWordEntrySchema = z.object({
  text: z.string(),
  type: z.literal("word"),
  start: z.number(),
  end: z.number(),
  speaker_id: z.string(),
  logprob: z.number().optional(),
});

export const transcriptSpacingEntrySchema = z.object({
  text: z.string(),
  type: z.literal("spacing"),
  start: z.number(),
  end: z.number(),
});

// Scribe v2 with tag_audio_events=true emits bracketed labels for non-speech
// sounds (`[cough]`, `[breath]`, `[laughter]`, `[mouth_noise]`,
// `[throat_clear]`). They share the spacing-row shape — no speaker_id, no
// logprob — but carry the original label in `text`.
export const transcriptAudioEventEntrySchema = z.object({
  text: z.string(),
  type: z.literal("audio_event"),
  start: z.number(),
  end: z.number(),
});

export const transcriptEntrySchema = z.discriminatedUnion("type", [
  transcriptWordEntrySchema,
  transcriptSpacingEntrySchema,
  transcriptAudioEventEntrySchema,
]);

export const transcriptSchema = z.object({
  audio_duration_secs: z.number().optional(),
  language_code: z.string(),
  language_probability: z.number(),
  text: z.string(),
  words: z.array(transcriptEntrySchema),
});

export const cutSchema = z.object({
  id: z.string().min(1),
  start: z.number().nonnegative(),
  end: z.number().nonnegative(),
  reason: z.string().optional(),
});

export const cutsFileSchema = z.object({
  version: z.literal(1),
  cuts: z
    .array(cutSchema)
    .refine((arr) => arr.every((c) => c.end > c.start), {
      message: "every cut must have end > start",
    }),
});

export type Transcript = z.infer<typeof transcriptSchema>;
export type CutsFile = z.infer<typeof cutsFileSchema>;
export type Cut = z.infer<typeof cutSchema>;
