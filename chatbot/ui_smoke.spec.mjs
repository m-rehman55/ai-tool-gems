import { test, expect } from '@playwright/test';

const site = process.env.AITG_TEST_URL || 'https://aitoolgems.tech/';
test.use({ launchOptions: { executablePath: process.env.CHROMIUM_PATH || undefined } });

test('chatbot controls, request recovery, and mobile reachability', async ({ browser }) => {
  const errors = [];
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(site, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await expect(page.locator('.aitg-chatbot')).toHaveCount(1);
  const launch = page.locator('.aitg-chatbot-launch');
  const panel = page.locator('.aitg-chatbot-panel');
  await launch.click();
  await expect(panel).toBeVisible();
  await page.locator('.aitg-chatbot-minimize').click();
  await expect(panel).toBeHidden();
  await launch.click();
  await expect(panel).toBeVisible();
  await expect(page.locator('.aitg-chatbot-message')).toHaveCount(1);
  await page.locator('.aitg-chatbot-form textarea').fill('Canva Pro ki current price kya hai?');
  await page.locator('.aitg-chatbot-send').click();
  await expect(page.locator('.aitg-chatbot-message.bot').filter({ hasText: 'Canva Pro Edu' })).toBeVisible({ timeout: 30000 });
  await expect(page.locator('.aitg-chatbot-send')).toBeEnabled();
  await page.locator('.aitg-chatbot-close').click();
  await launch.click();
  await expect(page.locator('.aitg-chatbot')).toHaveCount(1);
  await expect(page.locator('.aitg-chatbot-message')).toHaveCount(3);

  await page.route('**/api/chat', route => route.abort());
  await page.locator('.aitg-chatbot-form textarea').fill('This request should recover after a network failure');
  await page.locator('.aitg-chatbot-send').click();
  await expect(page.locator('.aitg-chatbot-message.error')).toBeVisible({ timeout: 10000 });
  await expect(page.locator('.aitg-chatbot-send')).toBeEnabled();
  await expect(page.locator('.aitg-chatbot-retry')).toHaveCount(1);
  await page.unroute('**/api/chat');

  const mobile = await browser.newPage({ viewport: { width: 375, height: 667 } });
  await mobile.goto(site, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await expect(mobile.locator('.aitg-chatbot')).toHaveCount(1);
  await mobile.locator('.aitg-chatbot-launch').click();
  for (const selector of ['.aitg-chatbot-form textarea', '.aitg-chatbot-send', '.aitg-chatbot-minimize', '.aitg-chatbot-close']) {
    const box = await mobile.locator(selector).boundingBox();
    expect(box && box.x >= 0 && box.y >= 0 && box.x + box.width <= 375 && box.y + box.height <= 667).toBeTruthy();
  }
  expect(errors).toEqual([]);
  await mobile.close();
  await page.close();
});
