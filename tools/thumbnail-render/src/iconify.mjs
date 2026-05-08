import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_CACHE_PATH = path.resolve(__dirname, '..', 'icons', 'iconify-cache.json');
const NAME_PATTERN = /^[a-z0-9-]+:[a-z0-9-]+$/;
const DEFAULT_VIEWBOX = '0 0 24 24';

/**
 * Resolve an Iconify icon — body and viewBox — fetching from the API and
 * caching on miss.
 *
 * @param {string} qualifiedName - "<set>:<icon>", e.g. "ph:cursor-click"
 * @param {object} [opts]
 * @param {string} [opts.cachePath] - path to iconify-cache.json
 * @param {function} [opts.fetcher] - fetch implementation (for testing)
 * @returns {Promise<{body: string, viewBox: string}>}
 */
export async function getIconifyIcon(qualifiedName, opts = {}) {
  if (!NAME_PATTERN.test(qualifiedName)) {
    throw new Error(`invalid Iconify name: "${qualifiedName}" (expected <set>:<icon>)`);
  }

  const cachePath = opts.cachePath ?? DEFAULT_CACHE_PATH;
  const fetcher = opts.fetcher ?? globalThis.fetch;

  const cache = existsSync(cachePath)
    ? JSON.parse(readFileSync(cachePath, 'utf8'))
    : {};

  const cached = cache[qualifiedName];
  if (cached) return normalizeEntry(cached);

  const [set, icon] = qualifiedName.split(':');
  const url = `https://api.iconify.design/${set}/${icon}.svg`;
  const res = await fetcher(url);
  if (!res.ok) {
    throw new Error(`Iconify fetch failed for "${qualifiedName}": HTTP ${res.status}`);
  }
  const svg = (await res.text()).replace(/^﻿/, '');
  const entry = extractIcon(svg);

  cache[qualifiedName] = entry;
  const sorted = Object.fromEntries(Object.keys(cache).sort().map(k => [k, cache[k]]));
  writeFileSync(cachePath, JSON.stringify(sorted, null, 2) + '\n');

  return entry;
}

/**
 * Backward-compat wrapper. Returns just the body string.
 * Prefer getIconifyIcon for new code.
 *
 * @param {string} qualifiedName
 * @param {object} [opts]
 * @returns {Promise<string>}
 */
export async function getIconifyBody(qualifiedName, opts = {}) {
  const { body } = await getIconifyIcon(qualifiedName, opts);
  return body;
}

/**
 * Promote a legacy string cache entry to the {body, viewBox} shape.
 * Pre-schema entries are assumed to be 24x24 (the only schema that worked
 * before this change).
 */
function normalizeEntry(entry) {
  if (typeof entry === 'string') {
    return { body: entry, viewBox: DEFAULT_VIEWBOX };
  }
  return { body: entry.body, viewBox: entry.viewBox ?? DEFAULT_VIEWBOX };
}

function extractIcon(svg) {
  const open = svg.indexOf('<svg');
  const gt = svg.indexOf('>', open);
  const close = svg.lastIndexOf('</svg>');
  if (open < 0 || gt < 0 || close < 0) {
    throw new Error('cannot parse SVG response — no <svg>...</svg>');
  }
  const openTag = svg.slice(open, gt + 1);
  const body = svg.slice(gt + 1, close).trim();
  const vbMatch = openTag.match(/\bviewBox\s*=\s*["']([^"']+)["']/);
  const viewBox = vbMatch ? vbMatch[1].trim() : DEFAULT_VIEWBOX;
  return { body, viewBox };
}
