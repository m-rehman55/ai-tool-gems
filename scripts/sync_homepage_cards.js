const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const appJsPath = path.join(root, 'app.js');
const indexHtmlPath = path.join(root, 'index.html');

// Read app.js
const appJs = fs.readFileSync(appJsPath, 'utf8');

// Extract products array using VM or eval with minimal mocked environment
const vm = require('vm');
const sandbox = {
  localStorage: { getItem: () => null, setItem: () => {}, removeItem: () => {} },
  window: { dataLayer: [], matchMedia: () => ({ matches: false }), addEventListener: () => {} },
  document: { querySelector: () => null, querySelectorAll: () => [], addEventListener: () => {} }
};

// We can extract just products and helper functions from app.js
const codeToRun = `
${appJs.slice(0, appJs.indexOf('function renderProducts() {'))}
;
this.exportedProducts = products;
this.exportedCard = card;
this.exportedState = state;
`;

vm.runInNewContext(codeToRun, sandbox);

const products = sandbox.exportedProducts;
const card = sandbox.exportedCard;

console.log('Loaded products:', products.length);

const generatedCards = products.map(p => card(p)).join('\n');

// Read index.html
let indexHtml = fs.readFileSync(indexHtmlPath, 'utf8');

// Replace contents of productGrid
const gridStartMarker = '<div class="product-grid" id="productGrid">';
const navMarker = '<nav class="catalog-directory"';

const startIndex = indexHtml.indexOf(gridStartMarker);
const navIndex = indexHtml.indexOf(navMarker, startIndex);

if (startIndex === -1 || navIndex === -1) {
  console.error('Could not find productGrid boundaries in index.html!');
  process.exit(1);
}

// Find the last </div> before navMarker
const endIndex = indexHtml.lastIndexOf('</div>', navIndex);

const before = indexHtml.slice(0, startIndex + gridStartMarker.length);
const after = indexHtml.slice(endIndex);

const updatedHtml = before + '\n' + generatedCards + '\n      ' + after;

fs.writeFileSync(indexHtmlPath, updatedHtml, 'utf8');
console.log('Successfully updated productGrid in index.html with all', products.length, 'cards.');
