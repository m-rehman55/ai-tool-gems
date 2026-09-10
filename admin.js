const DEFAULT_WHATSAPP = '923476242709';
const productSeed = [
  ['chatgpt','ChatGPT Plus','AI Assistants',2300,'chatgpt.com'],
  ['gemini','Gemini Pro','AI Assistants',800,'gemini.google.com'],
  ['veo','Veo 3 Ultra','AI Video',2100,'deepmind.google'],
  ['leonardo','Leonardo AI Essential','Design',1900,'leonardo.ai'],
  ['elevenlabs','ElevenLabs','AI Voice',3300,'elevenlabs.io'],
  ['canva','Canva Pro Edu','Design',900,'canva.com'],
  ['figma','Figma Pro Private','Design',3000,'figma.com'],
  ['capcut','CapCut Pro','AI Video',900,'capcut.com'],
  ['adobe','Adobe Creative Cloud','Design',1700,'adobe.com'],
  ['lovable','Lovable Pro','Development',1600,'lovable.dev'],
  ['gamma','Gamma Pro','Productivity',23000,'gamma.app'],
  ['replit','Replit Core','Development',3200,'replit.com'],
  ['n8n','n8n Starter','Development',7000,'n8n.io'],
  ['notion','Notion Business','Productivity',2200,'notion.so'],
  ['nordvpn','NordVPN','VPN & Security',1800,'nordvpn.com'],
  ['surfshark','Surfshark VPN','VPN & Security',800,'surfshark.com'],
  ['youtube','YouTube Premium','Entertainment',1200,'youtube.com'],
  ['netflix','Netflix Premium 4K','Entertainment',400,'netflix.com'],
  ['linkedin','LinkedIn Premium','Business',1500,'linkedin.com'],
  ['windows','Windows 11 Pro Key','Software',1900,'microsoft.com']
].map(([id,name,category,price,domain]) => ({
  id, name, category, price, domain,
  description: '',
  logo: `https://www.google.com/s2/favicons?domain=${domain}&sz=128`
}));

function readCatalog() {
  try {
    const saved = JSON.parse(localStorage.getItem('atg-admin-products') || '[]');
    return Array.isArray(saved) && saved.length ? saved : productSeed;
  } catch {
    localStorage.removeItem('atg-admin-products');
    return productSeed;
  }
}

let adminProducts = readCatalog();
let editingId = null;
const $ = selector => document.querySelector(selector);
const $$ = selector => [...document.querySelectorAll(selector)];
const money = value => `Rs. ${Number(value).toLocaleString('en-PK')}`;
const escapeHTML = value => String(value || '').replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[char]);

function renderAdminProducts() {
  $('#adminProducts').innerHTML = adminProducts.map(product => `
    <tr>
      <td><div class="product-cell"><img src="${product.logo || 'assets/brand-logo-light.png'}" alt="${escapeHTML(product.name)} logo"><span><b>${escapeHTML(product.name)}</b><small>Saved in this browser</small></span></div></td>
      <td>${escapeHTML(product.category)}</td>
      <td><b>${money(product.price)}</b></td>
      <td><span class="status">In stock</span></td>
      <td><button class="edit" data-edit-product="${escapeHTML(product.id)}" aria-label="Edit ${escapeHTML(product.name)}">Edit</button></td>
    </tr>
  `).join('');
  $('#adminProductCount').textContent = adminProducts.length;
}

function saveCatalog() {
  localStorage.setItem('atg-admin-products', JSON.stringify(adminProducts));
  renderAdminProducts();
}

const dialog = $('#productDialog');
const form = $('#productForm');

function openProductEditor(product = null) {
  editingId = product?.id || null;
  form.reset();
  dialog.querySelector('h2').textContent = product ? 'Edit product' : 'Add a new subscription';
  $('#productName').value = product?.name || '';
  $('#productCategory').value = product?.category || 'AI Assistants';
  $('#productPrice').value = product?.price || '';
  $('#productDescription').value = product?.description || '';
  dialog.showModal();
  requestAnimationFrame(() => $('#productName').focus());
}

$('#addProduct').addEventListener('click', () => openProductEditor());
$$('[data-dialog-close]').forEach(button => button.addEventListener('click', () => dialog.close()));

form.addEventListener('submit', event => {
  event.preventDefault();
  if (!form.reportValidity()) return;
  const name = $('#productName').value.trim();
  const price = Number($('#productPrice').value);
  const current = adminProducts.find(product => product.id === editingId);
  const next = {
    id: current?.id || `custom-${Date.now()}`,
    name,
    category: $('#productCategory').value,
    price,
    description: $('#productDescription').value.trim(),
    domain: current?.domain || '',
    logo: current?.logo || 'assets/brand-logo-light.png'
  };
  if (current) adminProducts = adminProducts.map(product => product.id === editingId ? next : product);
  else adminProducts.push(next);
  saveCatalog();
  dialog.close();
  $('#saveNote').textContent = `${name} saved. Refresh the storefront in this browser to apply catalog changes.`;
});

$('#adminProducts').addEventListener('click', event => {
  const button = event.target.closest('[data-edit-product]');
  if (!button) return;
  openProductEditor(adminProducts.find(product => product.id === button.dataset.editProduct));
});

const wa = $('#waNumber');
const businessStatus = $('#businessStatus');
const savedWhatsApp = (localStorage.getItem('atg-whatsapp') || '').replace(/\D/g, '');
wa.value = /^\d{10,15}$/.test(savedWhatsApp) && savedWhatsApp !== '923001234567' ? savedWhatsApp : DEFAULT_WHATSAPP;
businessStatus.value = localStorage.getItem('atg-business-status') || businessStatus.value;

$('#saveSettings').addEventListener('click', () => {
  const clean = wa.value.replace(/\D/g, '');
  if (!/^\d{10,15}$/.test(clean)) {
    $('#saveNote').textContent = 'Enter a valid 10–15 digit number with country code.';
    wa.focus();
    return;
  }
  localStorage.setItem('atg-whatsapp', clean);
  localStorage.setItem('atg-business-status', businessStatus.value);
  $('#saveNote').textContent = 'Settings saved. Refresh the storefront in this browser to apply.';
});

const viewContent = {
  orders: ['WhatsApp orders', 'Orders are confirmed directly in WhatsApp. Open your business conversation list to manage payment and delivery.', `https://wa.me/${wa.value}`],
  reviews: ['Customer reviews', 'A public review provider is not connected yet. Collect verified feedback after delivery, then add the approved integration here.', 'index.html#faqList'],
  analytics: ['Store analytics', 'No analytics provider is connected, so this dashboard does not display invented visitor or sales numbers.', 'index.html'],
};

function setAdminView(view) {
  const panel = $('#adminViewPanel');
  const metrics = $('#overviewMetrics');
  const content = $('#adminContent');
  const productsPanel = $('.products-panel');
  const settingsPanel = $('.side-column');
  panel.hidden = true;
  metrics.hidden = view !== 'overview';
  content.hidden = false;
  productsPanel.hidden = view === 'settings';
  settingsPanel.hidden = view === 'products';
  if (view === 'orders' || view === 'reviews' || view === 'analytics') {
    content.hidden = true;
    panel.hidden = false;
    const [title, copy, href] = viewContent[view];
    panel.innerHTML = `<small>LIVE STATUS</small><h2>${title}</h2><p>${copy}</p><a href="${href}">${view === 'orders' ? 'Open WhatsApp' : 'Continue to storefront'} →</a>`;
  }
}

$$('[data-admin-view]').forEach(button => button.addEventListener('click', () => {
  $$('[data-admin-view]').forEach(item => item.classList.remove('active'));
  button.classList.add('active');
  setAdminView(button.dataset.adminView);
}));

renderAdminProducts();
setAdminView('overview');
