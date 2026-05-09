import { chromium } from 'playwright';
import { existsSync, readFileSync } from 'node:fs';

/**
 * Render an SVG file to a square PNG at the given pixel size.
 *
 * The SVG is inlined into a minimal HTML wrapper so the browser scales it
 * to fill a `size`×`size` viewport; the screenshot is then taken with
 * transparent background so corners outside any disk in the SVG stay clear.
 *
 * @param {string} svgPath - absolute or relative path to the source SVG
 * @param {string} outPngPath - absolute or relative path for the output PNG
 * @param {number} size - target square size in pixels (positive integer)
 * @returns {Promise<void>}
 */
export async function renderSvgToPng(svgPath, outPngPath, size) {
  if (!existsSync(svgPath)) {
    throw new Error(`Input SVG not found: ${svgPath} (ENOENT)`);
  }
  if (!Number.isInteger(size) || size <= 0) {
    throw new Error(`size must be a positive integer (got ${size})`);
  }

  const svgContent = readFileSync(svgPath, 'utf8');
  const html = `<!doctype html><html><head><meta charset="utf-8"><style>
    html, body { margin: 0; padding: 0; background: transparent; }
    body > svg { display: block; width: 100vw; height: 100vh; }
  </style></head><body>${svgContent}</body></html>`;

  const browser = await chromium.launch();
  try {
    const context = await browser.newContext({
      viewport: { width: size, height: size },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    await page.setContent(html, { waitUntil: 'load' });
    await page.screenshot({
      path: outPngPath,
      type: 'png',
      omitBackground: true,
      clip: { x: 0, y: 0, width: size, height: size },
    });
  } finally {
    await browser.close();
  }
}
