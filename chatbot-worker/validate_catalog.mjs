import { readFile } from 'node:fs/promises';

const source = await readFile(new URL('../app.js', import.meta.url), 'utf8');
const entries = [...source.matchAll(/\{id:'([^']+)',name:'([^']+)'[^}]*?price:(\d+)/g)];
if (entries.length < 20) throw new Error(`Expected at least 20 catalog products, found ${entries.length}`);
const ids = new Set();
for (const [, id, name, price] of entries) {
  if (ids.has(id)) throw new Error(`Duplicate product id: ${id}`);
  ids.add(id);
  if (!name.trim() || Number(price) <= 0) throw new Error(`Invalid product: ${id}`);
}
console.log(`Catalog validation passed: ${entries.length} products with positive PKR prices.`);
