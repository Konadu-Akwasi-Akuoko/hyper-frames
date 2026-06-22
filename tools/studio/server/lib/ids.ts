import { createHash } from "node:crypto";

/** Unit separator (0x1f) — keeps source/externalId boundaries unambiguous. */
const US = String.fromCharCode(0x1f);

/**
 * Stable id for a raw_signal row. MUST stay byte-for-byte identical to the
 * Python `studio_discovery.ids.raw_signal_id` so the two writers dedup against
 * the same keyspace: sha1(source + 0x1f + externalId), first 16 hex chars.
 */
export function rawSignalId(source: string, externalId: string): string {
  return createHash("sha1")
    .update(source + US + externalId)
    .digest("hex")
    .slice(0, 16);
}
