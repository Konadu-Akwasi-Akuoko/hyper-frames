import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, writeFileSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { getIconifyBody } from '../src/iconify.mjs';

const SVG_RESPONSE = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path d="M2 2h20v20H2z" /></svg>';
const EXPECTED_BODY = '<path d="M2 2h20v20H2z" />';

function makeCache() {
  const dir = mkdtempSync(path.join(tmpdir(), 'iconify-test-'));
  const file = path.join(dir, 'iconify-cache.json');
  writeFileSync(file, '{}\n');
  return { dir, file };
}

test('getIconifyBody returns cached body without network', async () => {
  const { dir, file } = makeCache();
  try {
    writeFileSync(file, JSON.stringify({ 'ph:test-icon': '<rect />' }) + '\n');
    let fetchCalled = false;
    const fetcher = async () => { fetchCalled = true; throw new Error('should not fetch'); };
    const body = await getIconifyBody('ph:test-icon', { cachePath: file, fetcher });
    assert.equal(body, '<rect />');
    assert.equal(fetchCalled, false);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('getIconifyBody fetches and caches on miss', async () => {
  const { dir, file } = makeCache();
  try {
    let fetchCount = 0;
    const fetcher = async (url) => {
      fetchCount++;
      assert.match(url, /\/ph\/cursor-click\.svg$/);
      return { ok: true, status: 200, text: async () => SVG_RESPONSE };
    };
    const body1 = await getIconifyBody('ph:cursor-click', { cachePath: file, fetcher });
    assert.equal(body1, EXPECTED_BODY);
    assert.equal(fetchCount, 1);

    const cached = JSON.parse(readFileSync(file, 'utf8'));
    assert.equal(cached['ph:cursor-click'], EXPECTED_BODY);

    const body2 = await getIconifyBody('ph:cursor-click', { cachePath: file, fetcher });
    assert.equal(body2, EXPECTED_BODY);
    assert.equal(fetchCount, 1, 'second call should hit cache');
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('getIconifyBody throws on invalid name', async () => {
  const { dir, file } = makeCache();
  try {
    const fetcher = async () => { throw new Error('should not fetch'); };
    await assert.rejects(
      () => getIconifyBody('not a name', { cachePath: file, fetcher }),
      /invalid Iconify name/i
    );
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('getIconifyBody throws on HTTP failure and leaves cache unchanged', async () => {
  const { dir, file } = makeCache();
  try {
    const fetcher = async () => ({ ok: false, status: 404, text: async () => 'Not Found' });
    await assert.rejects(
      () => getIconifyBody('ph:does-not-exist', { cachePath: file, fetcher }),
      /Iconify fetch failed.*404/i
    );
    const cached = JSON.parse(readFileSync(file, 'utf8'));
    assert.deepEqual(cached, {});
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
