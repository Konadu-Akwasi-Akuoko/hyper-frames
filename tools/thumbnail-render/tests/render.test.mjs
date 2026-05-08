import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, existsSync, statSync, rmSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderHtmlToPng } from '../src/render.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const fixture = path.join(__dirname, 'fixtures', 'basic.html');
const verticalFixture = path.join(__dirname, 'fixtures', 'vertical-basic.html');

function readPngDims(pngPath) {
  const buf = readFileSync(pngPath);
  // PNG signature: 8 bytes; IHDR chunk: 4 length + 4 type ('IHDR') + 13 data
  // width = bytes 16-19, height = bytes 20-23 (big-endian uint32)
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}

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

test('renderHtmlToPng with orientation=horizontal produces 1280x720 PNG', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'tnr-'));
  const out = path.join(dir, 'h.png');
  try {
    await renderHtmlToPng(fixture, out, 'horizontal');
    const { width, height } = readPngDims(out);
    assert.equal(width, 1280);
    assert.equal(height, 720);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('renderHtmlToPng with orientation=vertical produces 1080x1920 PNG', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'tnr-'));
  const out = path.join(dir, 'v.png');
  try {
    await renderHtmlToPng(verticalFixture, out, 'vertical');
    const { width, height } = readPngDims(out);
    assert.equal(width, 1080);
    assert.equal(height, 1920);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('renderHtmlToPng defaults to horizontal when orientation omitted', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'tnr-'));
  const out = path.join(dir, 'd.png');
  try {
    await renderHtmlToPng(fixture, out);
    const { width, height } = readPngDims(out);
    assert.equal(width, 1280);
    assert.equal(height, 720);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('renderHtmlToPng throws on unknown orientation', async () => {
  await assert.rejects(
    () => renderHtmlToPng(fixture, '/tmp/nowhere.png', 'square'),
    /unknown orientation|orientation.*square/i
  );
});
