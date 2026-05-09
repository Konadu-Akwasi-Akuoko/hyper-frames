import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, existsSync, statSync, rmSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { renderSvgToPng } from '../src/render.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const fixture = path.join(__dirname, 'fixtures', 'square.svg');

function readPngDims(pngPath) {
  const buf = readFileSync(pngPath);
  return { width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}

test('renderSvgToPng writes a PNG of the requested size', async () => {
  const dir = mkdtempSync(path.join(tmpdir(), 'br-'));
  const out = path.join(dir, 'out.png');
  try {
    await renderSvgToPng(fixture, out, 96);
    assert.ok(existsSync(out), 'output PNG should exist');
    assert.ok(statSync(out).size > 100, 'output PNG should be non-empty');
    const dims = readPngDims(out);
    assert.equal(dims.width, 96);
    assert.equal(dims.height, 96);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test('renderSvgToPng rejects a missing input', async () => {
  await assert.rejects(
    () => renderSvgToPng('/no/such/file.svg', '/tmp/x.png', 96),
    /not found/i,
  );
});

test('renderSvgToPng rejects a non-positive size', async () => {
  await assert.rejects(
    () => renderSvgToPng(fixture, '/tmp/x.png', 0),
    /positive integer/i,
  );
});
