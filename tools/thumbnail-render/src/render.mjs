import { chromium } from 'playwright';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export const ORIENTATION_DIMS = {
  horizontal: { width: 1280, height: 720 },
  vertical:   { width: 1080, height: 1920 },
};

// Backwards-compat exports for any caller that imported the constants
// directly (these always reflect the horizontal mode).
export const THUMBNAIL_WIDTH = ORIENTATION_DIMS.horizontal.width;
export const THUMBNAIL_HEIGHT = ORIENTATION_DIMS.horizontal.height;

/**
 * Render an HTML file to a PNG at the requested orientation's dimensions.
 *
 * Waits for `document.fonts.ready` before screenshotting — without this,
 * web-font requests resolve after the screenshot fires and the PNG shows
 * the browser's fallback font instead of the intended one.
 *
 * @param {string} htmlPath - absolute path to the input HTML file
 * @param {string} outPngPath - absolute path where the PNG will be written
 * @param {'horizontal'|'vertical'} [orientation='horizontal']
 * @returns {Promise<void>}
 */
export async function renderHtmlToPng(htmlPath, outPngPath, orientation = 'horizontal') {
  const dims = ORIENTATION_DIMS[orientation];
  if (!dims) {
    throw new Error(`unknown orientation: ${orientation} (expected one of: ${Object.keys(ORIENTATION_DIMS).join(', ')})`);
  }
  if (!existsSync(htmlPath)) {
    throw new Error(`Input HTML not found: ${htmlPath} (ENOENT)`);
  }

  const { width, height } = dims;
  const browser = await chromium.launch();
  try {
    const context = await browser.newContext({
      viewport: { width, height },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    const fileUrl = pathToFileURL(path.resolve(htmlPath)).href;
    await page.goto(fileUrl, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({
      path: outPngPath,
      type: 'png',
      clip: { x: 0, y: 0, width, height },
    });
  } finally {
    await browser.close();
  }
}
