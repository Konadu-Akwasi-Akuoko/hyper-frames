import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { getIconifyBody, getIconifyIcon } from '../src/iconify.mjs';

const SVG_24 = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M2 2h20v20H2z" /></svg>';
const SVG_LOGO = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 417"><path fill="#d33833" d="M0 0h256v417H0z" /></svg>';
const EXPECTED_BODY_24 = '<path d="M2 2h20v20H2z" />';
const EXPECTED_BODY_LOGO = '<path fill="#d33833" d="M0 0h256v417H0z" />';

function makeCache() {
  const dir = mkdtempSync(path.join(tmpdir(), 'iconify-test-'));
  const file = path.join(dir, 'iconify-cache.json');
  writeFileSync(file, '{}\n');
  return { dir, file };
}

test('getIconifyIcon returns cached entry without network', async () => {
  const { dir, file } = makeCache();
  try {
    writeFileSync(file, JSON.stringify({
      'ph:test-icon': { body: '<rect />', viewBox: '0 0 24 24' },
    }) + '\n');
    let fetchCalled = false;
    const fetcher = async () => { fetchCalled = true; throw new Error('should not fetch'); };
    const entry = await getIconifyIcon('ph:test-icon', { cachePath: file, fetcher });
    assert.deepEqual(entry, { body: '<rect />', viewBox: '0 0 24 24' });
    assert.equal(fetchCalled, false);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('getIconifyIcon promotes legacy string cache entries to {body, viewBox}', async () => {
  const { dir, file } = makeCache();
  try {
    writeFileSync(file, JSON.stringify({
      'ph:legacy-icon': '<rect />',
    }) + '\n');
    const fetcher = async () => { throw new Error('should not fetch'); };
    const entry = await getIconifyIcon('ph:legacy-icon', { cachePath: file, fetcher });
    assert.deepEqual(entry, { body: '<rect />', viewBox: '0 0 24 24' });
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('getIconifyIcon fetches, parses viewBox, and caches on miss', async () => {
  const { dir, file } = makeCache();
  try {
    let fetchCount = 0;
    const fetcher = async (url) => {
      fetchCount++;
      assert.match(url, /\/ph\/cursor-click\.svg$/);
      return { ok: true, status: 200, text: async () => SVG_24 };
    };
    const e1 = await getIconifyIcon('ph:cursor-click', { cachePath: file, fetcher });
    assert.deepEqual(e1, { body: EXPECTED_BODY_24, viewBox: '0 0 24 24' });
    assert.equal(fetchCount, 1);

    const cached = JSON.parse(readFileSync(file, 'utf8'));
    assert.deepEqual(cached['ph:cursor-click'], { body: EXPECTED_BODY_24, viewBox: '0 0 24 24' });

    const e2 = await getIconifyIcon('ph:cursor-click', { cachePath: file, fetcher });
    assert.deepEqual(e2, e1);
    assert.equal(fetchCount, 1, 'second call should hit cache');
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('getIconifyIcon preserves non-24x24 viewBox from upstream SVG', async () => {
  const { dir, file } = makeCache();
  try {
    const fetcher = async () => ({ ok: true, status: 200, text: async () => SVG_LOGO });
    const entry = await getIconifyIcon('logos:fake-brand', { cachePath: file, fetcher });
    assert.deepEqual(entry, { body: EXPECTED_BODY_LOGO, viewBox: '0 0 256 417' });

    const cached = JSON.parse(readFileSync(file, 'utf8'));
    assert.equal(cached['logos:fake-brand'].viewBox, '0 0 256 417');
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('getIconifyBody (compat wrapper) returns just the body string', async () => {
  const { dir, file } = makeCache();
  try {
    const fetcher = async () => ({ ok: true, status: 200, text: async () => SVG_24 });
    const body = await getIconifyBody('ph:cursor-click', { cachePath: file, fetcher });
    assert.equal(body, EXPECTED_BODY_24);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('getIconifyIcon throws on invalid name', async () => {
  const { dir, file } = makeCache();
  try {
    const fetcher = async () => { throw new Error('should not fetch'); };
    await assert.rejects(
      () => getIconifyIcon('not a name', { cachePath: file, fetcher }),
      /invalid Iconify name/i
    );
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('getIconifyIcon throws on HTTP failure and leaves cache unchanged', async () => {
  const { dir, file } = makeCache();
  try {
    const fetcher = async () => ({ ok: false, status: 404, text: async () => 'Not Found' });
    await assert.rejects(
      () => getIconifyIcon('ph:does-not-exist', { cachePath: file, fetcher }),
      /Iconify fetch failed.*404/i
    );
    const cached = JSON.parse(readFileSync(file, 'utf8'));
    assert.deepEqual(cached, {});
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
