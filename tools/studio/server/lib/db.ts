import { Database } from "bun:sqlite";
import path from "node:path";

const DEFAULT_DB_PATH = path.resolve(import.meta.dir, "../../studio.db");

/**
 * Schema — spec §6. Four small tables; the server owns all UI-driven writes,
 * the discovery CLI writes only `raw_signal`. NO score column on `ideas`, by
 * design (aggregator, never a judge).
 */
export const SCHEMA = `
CREATE TABLE IF NOT EXISTS channels (
  handle      TEXT PRIMARY KEY,
  url         TEXT NOT NULL,
  note        TEXT,
  active      INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS raw_signal (
  id             TEXT PRIMARY KEY,
  source         TEXT NOT NULL,
  external_id    TEXT NOT NULL,
  title          TEXT,
  url            TEXT,
  payload_json   TEXT NOT NULL,
  fetched_at     TEXT NOT NULL,
  judged_at      TEXT,
  judged_verdict TEXT
);
CREATE INDEX IF NOT EXISTS idx_raw_unjudged ON raw_signal(judged_at) WHERE judged_at IS NULL;

CREATE TABLE IF NOT EXISTS ideas (
  id            TEXT PRIMARY KEY,
  type          TEXT NOT NULL,
  kind          TEXT NOT NULL DEFAULT 'unset',
  status        TEXT NOT NULL DEFAULT 'new',
  title         TEXT NOT NULL,
  rationale     TEXT,
  source        TEXT,
  source_url    TEXT,
  source_title  TEXT,
  evidence_json TEXT,
  raw_signal_id TEXT,
  first_seen    TEXT NOT NULL,
  notes         TEXT,
  promoted_slug TEXT
);
CREATE INDEX IF NOT EXISTS idx_ideas_status ON ideas(status);

CREATE TABLE IF NOT EXISTS board_overlay (
  slug              TEXT PRIMARY KEY,
  title             TEXT,
  stage             TEXT,
  notes             TEXT,
  created_from_idea TEXT,
  updated_at        TEXT NOT NULL
);
`;

export function migrate(db: Database): void {
  db.exec(SCHEMA);
}

/** Open a fresh (non-singleton) database — used by tests and tools. */
export function openDb(dbPath: string): Database {
  const db = new Database(dbPath, { create: true });
  if (dbPath !== ":memory:") db.exec("PRAGMA journal_mode = WAL;");
  migrate(db);
  return db;
}

let _db: Database | null = null;

/** Process-wide singleton over the local `studio.db` file. */
export function getDb(): Database {
  if (_db) return _db;
  const dbPath = process.env.STUDIO_DB ?? DEFAULT_DB_PATH;
  _db = openDb(dbPath);
  return _db;
}
