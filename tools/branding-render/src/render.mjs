import { chromium } from 'playwright';
import { existsSync, readFileSync } from 'node:fs';

/**
 * Render an SVG file to a PNG at the given pixel dimensions.
 *
 * The SVG is inlined into a minimal HTML wrapper that loads JetBrains Mono
 * ExtraBold via Google Fonts so any text in the SVG renders in the channel
 * font. The browser scales the SVG to fill the viewport, the renderer waits
 * for fonts to load, and the screenshot is taken with transparent background
 * so anything outside an SVG-drawn shape stays clear.
 *
 * @param {string} svgPath - absolute or relative path to the source SVG
 * @param {string} outPngPath - absolute or relative path for the output PNG
 * @param {number | { width: number, height: number }} dims
 *   - A positive integer is treated as a square size.
 *   - `{ width, height }` produces a rectangular output.
 * @returns {Promise<void>}
 */
export async function renderSvgToPng(svgPath, outPngPath, dims) {
  if (!existsSync(svgPath)) {
    throw new Error(`Input SVG not found: ${svgPath} (ENOENT)`);
  }

  let width, height;
  if (typeof dims === 'number') {
    if (!Number.isInteger(dims) || dims <= 0) {
      throw new Error(`size must be a positive integer (got ${dims})`);
    }
    width = height = dims;
  } else if (dims && typeof dims === 'object' && 'width' in dims && 'height' in dims) {
    ({ width, height } = dims);
    if (!Number.isInteger(width) || width <= 0 || !Number.isInteger(height) || height <= 0) {
      throw new Error(`width and height must be positive integers (got width=${width}, height=${height})`);
    }
  } else {
    throw new Error(`dims must be a positive integer or {width, height} object (got ${typeof dims})`);
  }

  const svgContent = readFileSync(svgPath, 'utf8');
  const html = `<!doctype html><html><head><meta charset="utf-8">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@800&display=block" rel="stylesheet">
    <style>
      html, body { margin: 0; padding: 0; background: transparent; }
      body > svg { display: block; width: 100vw; height: 100vh; }
    </style></head><body>${svgContent}</body></html>`;

  const browser = await chromium.launch();
  try {
    const context = await browser.newContext({
      viewport: { width, height },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    await page.setContent(html, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({
      path: outPngPath,
      type: 'png',
      omitBackground: true,
      clip: { x: 0, y: 0, width, height },
    });
  } finally {
    await browser.close();
  }
}
