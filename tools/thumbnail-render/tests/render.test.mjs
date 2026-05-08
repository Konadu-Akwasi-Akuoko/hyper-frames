import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, existsSync, statSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderHtmlToPng } from '../src/render.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const fixture = path.join(__dirname, 'fixtures', 'basic.html');

test('renderHtmlToPng writes a PNG at the requested path', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'tnr-'));
  const out = path.join(dir, 'out.png');
  try {
    await renderHtmlToPng(fixture, out);
    assert.ok(existsSync(out), 'output PNG should exist');
    assert.ok(statSync(out).size > 1000, 'output PNG should be non-trivially sized (>1KB)');
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('renderHtmlToPng throws a useful error when the input file is missing', async () => {
  await assert.rejects(
    () => renderHtmlToPng('/nonexistent/file.html', '/tmp/nowhere.png'),
    /not found|ENOENT/i
  );
});
