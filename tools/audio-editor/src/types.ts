// Mirror of server/lib/schemas.ts — keep in sync when the Zod schemas change.

export type TranscriptWordEntry = {
  text: string;
  type: "word";
  start: number;
  end: number;
  speaker_id: string;
  logprob?: number;
};

export type TranscriptSpacingEntry = {
  text: string;
  type: "spacing";
  start: number;
  end: number;
};

export type TranscriptEntry = TranscriptWordEntry | TranscriptSpacingEntry;

export type Transcript = {
  audio_duration_secs?: number;
  language_code: string;
  language_probability: number;
  text: string;
  words: TranscriptEntry[];
};

export type Cut = {
  id: string;
  start: number;
  end: number;
  reason?: string;
};

export type CutsFile = {
  version: 1;
  cuts: Cut[];
};

export type Video = {
  slug: string;
  hasAudio: boolean;
  hasTranscript: boolean;
  hasCuts: boolean;
};

export type Session = {
  slug: string;
  transcript: Transcript;
  cuts: CutsFile | null;
  audioUrl: string;
};
