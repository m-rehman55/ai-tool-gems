import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import worker from './index.js';

const catalogSource = await readFile(new URL('../app.js', import.meta.url), 'utf8');
const originalFetch = globalThis.fetch;

function mockFetch() {
  globalThis.fetch = async (input) => {
    if (String(input).endsWith('/app.js')) return new Response(catalogSource, { status: 200 });
    throw new Error(`unexpected fetch: ${input}`);
  };
}

function request(message, language = 'en') {
  return new Request('https://aitoolgems.tech/api/chat', {
    method: 'POST',
    headers: { origin: 'https://aitoolgems.tech', 'cf-connecting-ip': '127.0.0.1', 'content-type': 'application/json' },
    body: JSON.stringify({ message, language })
  });
}

test.beforeEach(mockFetch);
test.after(() => { globalThis.fetch = originalFetch; });

test('returns source-linked current catalog matches without an AI key', async () => {
  const response = await worker.fetch(request('Canva under Rs 1000'), { PUBLIC_ORIGIN: 'https://aitoolgems.tech', CATALOG_URL: 'https://aitoolgems.tech/app.js' });
  const body = await response.json();
  assert.equal(response.status, 200);
  assert.match(body.answer, /Canva Pro Edu/);
  assert.match(body.answer, /Rs\. 900/);
  assert.ok(body.sources.some(source => source.url.includes('/tools/canva/')));
});

test('supports Roman Urdu requests without inventing order status', async () => {
  const response = await worker.fetch(request('Mera budget Rs 1000 hai, design ke liye tool batao', 'roman-ur'), { PUBLIC_ORIGIN: 'https://aitoolgems.tech', CATALOG_URL: 'https://aitoolgems.tech/app.js' });
  const body = await response.json();
  assert.equal(response.status, 200);
  assert.match(body.answer, /Rs\./);
  assert.match(body.answer, /WhatsApp|confirm|budget/i);
});

test('recommends affordable products for a budget-only question', async () => {
  const response = await worker.fetch(request('Mera budget Rs. 1,000 hai. Best AI tools batao.', 'roman-ur'), { PUBLIC_ORIGIN: 'https://aitoolgems.tech', CATALOG_URL: 'https://aitoolgems.tech/app.js' });
  const body = await response.json();
  assert.equal(response.status, 200);
  assert.match(body.answer, /Netflix Premium 4K|QuillBot Premium|Gemini Pro/);
  assert.doesNotMatch(body.answer, /Rs\. 1,100|Rs\. 2,300/);
});

test('returns a comparison for named products', async () => {
  const response = await worker.fetch(request('ChatGPT aur Gemini compare karo', 'roman-ur'), { PUBLIC_ORIGIN: 'https://aitoolgems.tech', CATALOG_URL: 'https://aitoolgems.tech/app.js' });
  const body = await response.json();
  assert.match(body.answer, /comparison|compare/i);
  assert.match(body.answer, /ChatGPT Plus/);
  assert.match(body.answer, /Gemini Pro/);
});

test('routes order status requests to human support', async () => {
  const response = await worker.fetch(request('Meri payment aur order status check karo.', 'en'), { PUBLIC_ORIGIN: 'https://aitoolgems.tech', CATALOG_URL: 'https://aitoolgems.tech/app.js' });
  const body = await response.json();
  assert.match(body.answer, /WhatsApp|human|order status/i);
  assert.ok(body.sources.some(source => source.url.includes('wa.me')));
});

test('answers general help without accidental product matches', async () => {
  const response = await worker.fetch(request('What can you help me with?', 'en'), { PUBLIC_ORIGIN: 'https://aitoolgems.tech', CATALOG_URL: 'https://aitoolgems.tech/app.js' });
  const body = await response.json();
  assert.match(body.answer, /compare|recommend|budget/i);
  assert.doesNotMatch(body.answer, /Netflix|YouTube/);
});

test('handles CORS preflight with a valid empty 204 response', async () => {
  const response = await worker.fetch(new Request('https://aitoolgems.tech/api/chat', { method: 'OPTIONS', headers: { origin: 'https://aitoolgems.tech' } }), {});
  assert.equal(response.status, 204);
  assert.equal(response.headers.get('access-control-allow-origin'), 'https://aitoolgems.tech');
  assert.equal(await response.text(), '');
});

test('supports Urdu fallback answers without an AI key', async () => {
  const response = await worker.fetch(request('وارنٹی اور ادائیگی کی پالیسی کیا ہے؟', 'ur'), { PUBLIC_ORIGIN: 'https://aitoolgems.tech', CATALOG_URL: 'https://aitoolgems.tech/app.js' });
  const body = await response.json();
  assert.equal(response.status, 200);
  assert.match(body.answer, /WhatsApp|وارنٹی|ادائیگی/);
});

test('rejects sensitive data requests safely', async () => {
  const response = await worker.fetch(request('My password is secret123, check my order'), { PUBLIC_ORIGIN: 'https://aitoolgems.tech', CATALOG_URL: 'https://aitoolgems.tech/app.js' });
  const body = await response.json();
  assert.equal(response.status, 200);
  assert.match(body.answer, /do not send passwords/i);
  assert.ok(body.sources.some(source => source.url.includes('wa.me')));
});

test('rejects invalid methods and oversized input', async () => {
  const get = await worker.fetch(new Request('https://aitoolgems.tech/api/chat', { method: 'GET', headers: { origin: 'https://aitoolgems.tech' } }), {});
  assert.equal(get.status, 405);
  const oversized = await worker.fetch(request('x'.repeat(801)), { PUBLIC_ORIGIN: 'https://aitoolgems.tech', CATALOG_URL: 'https://aitoolgems.tech/app.js' });
  assert.equal(oversized.status, 400);
});
