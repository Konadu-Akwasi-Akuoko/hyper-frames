import { chromium } from 'playwright';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

export const THUMBNAIL_WIDTH = 1280;
export const THUMBNAIL_HEIGHT = 720;

/**
 * Render an HTML file to a PNG at exact thumbnail dimensions.
 *
 * Waits for `document.fonts.ready` before screenshotting — without this,
 * web-font requests resolve after the screenshot fires and the PNG shows
 * the browser's fallback font instead of the intended one.
 *
 * @param {string} htmlPath - absolute path to the input HTML file
 * @param {string} outPngPath - absolute path where the PNG will be written
 * @returns {Promise<void>}
 */
export async function renderHtmlToPng(htmlPath, outPngPath) {
  if (!existsSync(htmlPath)) {
    throw new Error(`Input HTML not found: ${htmlPath} (ENOENT)`);
  }

  const browser = await chromium.launch();
  try {
    const context = await browser.newContext({
      viewport: { width: THUMBNAIL_WIDTH, height: THUMBNAIL_HEIGHT },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    const fileUrl = pathToFileURL(path.resolve(htmlPath)).href;
    await page.goto(fileUrl, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({
      path: outPngPath,
      type: 'png',
      clip: { x: 0, y: 0, width: THUMBNAIL_WIDTH, height: THUMBNAIL_HEIGHT },
    });
  } finally {
    await browser.close();
  }
}
