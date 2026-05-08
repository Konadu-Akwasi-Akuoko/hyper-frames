import { readFileSync, writeFileSync, existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DEFAULT_CACHE_PATH = path.resolve(__dirname, '..', 'icons', 'iconify-cache.json');
const NAME_PATTERN = /^[a-z0-9-]+:[a-z0-9-]+$/;

/**
 * Resolve an Iconify icon body, fetching from the API and caching on miss.
 *
 * @param {string} qualifiedName - "<set>:<icon>", e.g. "ph:cursor-click"
 * @param {object} [opts]
 * @param {string} [opts.cachePath] - path to iconify-cache.json
 * @param {function} [opts.fetcher] - fetch implementation (for testing)
 * @returns {Promise<string>} the SVG body (children of <svg>)
 */
export async function getIconifyBody(qualifiedName, opts = {}) {
  if (!NAME_PATTERN.test(qualifiedName)) {
    throw new Error(`invalid Iconify name: "${qualifiedName}" (expected <set>:<icon>)`);
  }

  const cachePath = opts.cachePath ?? DEFAULT_CACHE_PATH;
  const fetcher = opts.fetcher ?? globalThis.fetch;

  const cache = existsSync(cachePath)
    ? JSON.parse(readFileSync(cachePath, 'utf8'))
    : {};

  if (cache[qualifiedName]) return cache[qualifiedName];

  const [set, icon] = qualifiedName.split(':');
  const url = `https://api.iconify.design/${set}/${icon}.svg`;
  const res = await fetcher(url);
  if (!res.ok) {
    throw new Error(`Iconify fetch failed for "${qualifiedName}": HTTP ${res.status}`);
  }
  const svg = (await res.text()).replace(/^﻿/, '');
  const body = extractBody(svg);

  cache[qualifiedName] = body;
  const sorted = Object.fromEntries(Object.keys(cache).sort().map(k => [k, cache[k]]));
  writeFileSync(cachePath, JSON.stringify(sorted, null, 2) + '\n');

  return body;
}

function extractBody(svg) {
  const open = svg.indexOf('<svg');
  const gt = svg.indexOf('>', open);
  const close = svg.lastIndexOf('</svg>');
  if (open < 0 || gt < 0 || close < 0) {
    throw new Error('cannot parse SVG response — no <svg>...</svg>');
  }
  return svg.slice(gt + 1, close).trim();
}
