export type SpeakerPalette = {
  bg: string;
  fg: string;
  ring: string;
  initial: string;
};

const cache = new Map<string, SpeakerPalette>();

// Avoid colliding with the accent (~210° blue) and cut (~350° red) brand hues —
// keep speaker colors visually distinct from the editor's signal colors.
function safeHue(rawHue: number): number {
  const h = ((rawHue % 360) + 360) % 360;
  if (h >= 190 && h <= 230) return (h + 60) % 360;  // bump blue band → cyan/teal
  if (h >= 340 || h <= 10) return 30;               // bump red band → orange
  if (h >= 330 && h < 340) return 30;
  return h;
}

function deriveInitial(id: string): string {
  // ElevenLabs Scribe gives ids like "speaker_0" / "speaker_1". Prefer trailing
  // digits; fall back to the first non-symbol char uppercased.
  const trailingDigits = id.match(/(\d+)\s*$/);
  if (trailingDigits) return trailingDigits[1].slice(-1);
  const firstAlpha = id.match(/[A-Za-z]/);
  return (firstAlpha ? firstAlpha[0] : "?").toUpperCase();
}

export function speakerColor(id: string): SpeakerPalette {
  const key = id || "unknown";
  const cached = cache.get(key);
  if (cached) return cached;

  let h = 0;
  for (let i = 0; i < key.length; i++) h = (h * 31 + key.charCodeAt(i)) | 0;
  const hue = safeHue(Math.abs(h));

  const palette: SpeakerPalette = {
    bg: `hsl(${hue} 55% 38% / 0.22)`,
    fg: `hsl(${hue} 70% 72%)`,
    ring: `hsl(${hue} 70% 60%)`,
    initial: deriveInitial(key),
  };
  cache.set(key, palette);
  return palette;
}
