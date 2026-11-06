const DEFAULT_WHATSAPP = '923236715731';
const LEGACY_WHATSAPP = ['923', '476', '242709'].join('');
const productSeed = [
  ['chatgpt','ChatGPT Plus','AI Assistants',2300,'chatgpt.com',28868,0.08,'Fat bunny hub'],
  ['gemini','Gemini Pro','AI Assistants',800,'gemini.google.com',9902,0.75,'OxygenPremium Store'],
  ['veo','Veo 3 Ultra','AI Video',2100,'deepmind.google',18051,2.5,'Ai tools premium'],
  ['leonardo','Leonardo AI Essential','Design',1900,'leonardo.com',4,0.77,'Fat bunny hub'],
  ['elevenlabs','ElevenLabs Voice AI','AI Voice',3300,'elevenlabs.io',5372,1.2,'GET digital tools'],
  ['canva','Canva Pro Edu','Design',900,'canva.com',8263,0.04,'Fat bunny hub'],
  ['figma','Figma Pro Private','Design',3000,'figma.com',271,2.5,'MediaHubMarketplace_bot'],
  ['capcut','CapCut Pro VIP','AI Video',900,'capcut.com',1293,0.04,'Fat bunny hub'],
  ['adobe','Adobe Creative Cloud','Design',1700,'adobe.com',1521,0.63,'AI Toolify Studio'],
  ['lovable','Lovable Pro','Development',1600,'lovable.dev',1717,0.98,'GET digital tools'],
  ['gamma','Gamma Pro','Productivity',23000,'gamma.app',9558,4.22,'Fat bunny hub'],
  ['replit','Replit Core','Development',3200,'replit.com',82,6.0,'Premium tools'],
  ['n8n','n8n Starter','Development',7000,'n8n.io',76,15.0,'Premium tools'],
  ['notion','Notion Business','Productivity',2200,'notion.so',10925,0.99,'AI Toolify Studio'],
  ['nordvpn','NordVPN','VPN & Security',1800,'nordvpn.com',1198,0.58,'Fat bunny hub'],
  ['surfshark','Surfshark VPN','VPN & Security',800,'surfshark.com',418,0.47,'Fat bunny hub'],
  ['youtube','YouTube Premium','Entertainment',1200,'youtube.com',4688,0.58,'Fat bunny hub'],
  ['netflix','Netflix Premium 4K','Entertainment',400,'netflix.com',3109,2.0,'GET digital tools'],
  ['linkedin','LinkedIn Premium','Business',1500,'linkedin.com',8185,0.5,'Premium tools'],
  ['windows','Windows 11 Pro Key','Software',1900,'microsoft.com',77,2.98,'GET digital tools'],
  ['claude','Claude Pro (3.5 Sonnet)','AI Assistants',2200,'claude.com',9112,0.97,'Hitmeow shop'],
  ['midjourney','Midjourney v6.1 Pro','Design',2400,'midjourney.com',16,11.99,'GET digital tools'],
  ['cursor','Cursor AI Pro','Development',2800,'cursor.com',2114,7.77,'Fat bunny hub'],
  ['perplexity','Perplexity Pro','AI Assistants',1400,'perplexity.com',121,3.39,'Fat bunny hub'],
  ['deepseek','DeepSeek Unlimited','AI Assistants',1100,'deepseek.com',918,1.12,'Hitmeow shop'],
  ['grok','SuperGrok / Grok 2','AI Assistants',1800,'grok.com',2774,1.12,'Hitmeow shop'],
  ['runway','Runway ML Gen-3 Pro','AI Video',3500,'runway.com',74,1.9,'GET digital tools'],
  ['heygen','HeyGen AI Avatar Pro','AI Video',4200,'heygen.com',1026,15.24,'Fat bunny hub'],
  ['grammarly','Grammarly Premium','Writing & SEO',750,'grammarly.com',36,0.39,'Fat bunny hub'],
  ['quillbot','QuillBot Premium','Writing & SEO',450,'quillbot.com',1998,3.05,'Fat bunny hub'],
  ['semrush','SEMrush Pro','Writing & SEO',1500,'semrush.com',20,3.5,'MediaHubMarketplace_bot'],
  ['allinone','All-in-One Mega AI Portal','AI Assistants',1999,'allinone.com',40,4.2,'AIToolGems Direct Domestic'],
  ['tradingview','TradingView Pro','Business',3500,'tradingview.com',999,1.91,'Fat bunny hub'],
  ['kling','Kling AI','AI Video',4800,'kling.com',840,0.08,'Fat bunny hub'],
  ['freepik','Freepik Premium','Design',2400,'freepik.com',210,2.67,'Fat bunny hub'],
  ['spotify','Spotify Premium','Entertainment',1200,'spotify.com',733,0.3,'AI Toolify Studio'],
  ['copilot','GitHub Copilot','Development',2500,'github.com',54,2.48,'Fat bunny hub'],
  ['suno','Suno AI','AI Voice',3200,'suno.com',10,3.81,'Hitmeow shop'],
  ['turnitin','Turnitin Student Account','Writing & SEO',3600,'turnitin.com',32,2.2,'GET digital tools'],
  ['office365','Microsoft Office 365 (1TB)','Productivity',2200,'microsoft.com',2077,0.96,'Fat bunny hub']
].map(([id,name,category,price,domain,stock,wholesaleCost,supplier]) => ({
  id, name, category, price, domain, stock: stock || 15, wholesaleCost: wholesaleCost || 0, supplier: supplier || 'AIToolGems Direct',
  description: '',
  logo: `assets/product-logos/${id}.png`
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
      <td><div class="product-cell"><img src="${product.logo || 'assets/brand-logo-light.webp'}" width="128" height="128" loading="lazy" alt="${escapeHTML(product.name)} logo"><span><b>${escapeHTML(product.name)}</b><small>Saved in this browser</small></span></div></td>
      <td>${escapeHTML(product.category)}</td>
      <td><b>${money(product.price)}</b></td>
      <td><span class="status" style="font-size:12px;padding:3px 8px;border-radius:6px;background:${product.stock > 5 ? "rgba(16,185,129,0.15)" : "rgba(245,158,11,0.15)"};color:${product.stock > 5 ? "#10b981" : "#f59e0b"};font-weight:600;">${product.stock || 15} in stock</span><br><small style="opacity:0.65;font-size:11px;">Cost: $${product.wholesaleCost || 0} (${escapeHTML(product.supplier || "Supplier")})</small></td>
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
    logo: current?.logo || 'assets/brand-logo-light.webp'
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
if (savedWhatsApp === LEGACY_WHATSAPP) localStorage.setItem('atg-whatsapp', DEFAULT_WHATSAPP);
wa.value = /^\d{10,15}$/.test(savedWhatsApp)
  && savedWhatsApp !== '923001234567'
  && savedWhatsApp !== LEGACY_WHATSAPP
  ? savedWhatsApp
  : DEFAULT_WHATSAPP;
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
