const DEFAULT_WA_NUMBER = '817095128428';
const LEGACY_WA_NUMBER = '923236715731';

const products = [
  {id:'gemini',name:'Gemini Pro',category:'AI Assistants',description:'Gemini Proを日本向けに比較。18か月、¥849。利用条件と提供状況は注文前に確認します。',price:849,old価格:1019,duration:'18か月',access:'招待形式',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'chatgpt',name:'ChatGPT Plus',category:'AI Assistants',description:'ChatGPT Plusを日本向けに比較。1か月、¥1,697。利用条件と提供状況は注文前に確認します。',price:1697,old価格:2036,duration:'1か月',access:'個人アクセス',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'veo',name:'Veo 3 Ultra',category:'AI Video',description:'Veo 3 Ultraの日本向け掲載。¥1,415。動画生成プランと利用条件は注文前に確認します。',price:1415,old価格:1698,duration:'無制限',access:'共有アクセス',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'leonardo',name:'Leonardo AI Essential',category:'Design',description:'Leonardo AI Essentialを日本向けに比較。8,500クレジット、¥1,358。',price:1358,old価格:1630,duration:'8,500 クレジット',access:'個人アクセス',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'elevenlabs',name:'ElevenLabs',category:'AI Voice',description:'ElevenLabsの日本向け掲載。130Kクレジット、1か月、¥2,150。',price:2150,old価格:2580,duration:'1か月',access:'個人アクセス',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'canva',name:'Canva Pro Edu',category:'Design',description:'Canva Pro Eduを日本向けに比較。1年、¥679。利用条件は注文前に確認します。',price:679,old価格:815,duration:'1年間',access:'招待形式',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'figma',name:'Figma Pro Private',category:'Design',description:'Figma Pro Privateを日本向けに比較。2年、¥2,207。',price:2207,old価格:2648,duration:'2年間',access:'個人アクセス',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'capcut',name:'CapCut Pro',category:'AI Video',description:'CapCut Proを日本向けに比較。1か月、¥679。',price:679,old価格:815,duration:'1か月',access:'個人アクセス',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'adobe',name:'Adobe Creative',category:'Design',description:'Adobe Creativeの日本向け掲載。2か月¥1,075、1年¥15,277。プランは注文前に確認します。',price:1075,old価格:1290,duration:'2か月 / 1年間',access:'個人アクセス',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'lovable',name:'Lovable Pro',category:'Development',description:'Lovable Proを日本向けに比較。1か月、¥1,075。',price:1075,old価格:1290,duration:'1か月',access:'個人アクセス',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'gamma',name:'Gamma Pro',category:'Productivity',description:'Gamma Proを日本向けに比較。1年、¥14,711。',price:14711,old価格:17653,duration:'1年間',access:'個人アクセス',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'replit',name:'Replit Core',category:'Development',description:'Replit Coreの日本向け掲載。$40クレジット¥2,150、1年¥7,921。プランは注文前に確認します。',price:2150,old価格:2580,duration:'$40 クレジット / 1年間',access:'個人アクセス',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'n8n',name:'n8n Starter',category:'Development',description:'n8n Starterを日本向けに比較。1年、¥4,526。',price:4526,old価格:5431,duration:'1年間',access:'個人アクセス',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'manus',name:'Manus AI Pro',category:'AI Assistants',description:'Manus AI Proの日本向け掲載。1年、¥8,487。利用条件は注文前に確認します。',price:8487,old価格:10184,duration:'1年間',access:'個人アクセス',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'notion',name:'Notion Business',category:'Productivity',description:'Notion Businessを日本向けに比較。3か月、¥1,415。',price:1415,old価格:1698,duration:'3か月',access:'招待形式',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'nordvpn',name:'NordVPN',category:'VPN & Security',description:'NordVPNを日本向けに比較。3か月、¥6,846。',price:6846,old価格:8215,duration:'3か月',access:'個人アクセス',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'surfshark',name:'Surfshark VPN',category:'VPN & Security',description:'Surfshark VPNを日本向けに比較。2か月、¥679。',price:679,old価格:815,duration:'2か月',access:'共有アクセス',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'youtube',name:'YouTube Premium',category:'Entertainment',description:'YouTube Premiumを日本向けに比較。3か月、¥1,018。',price:1018,old価格:1222,duration:'3か月',access:'招待形式',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'netflix',name:'Netflix Premium 4K',category:'Entertainment',description:'Netflix Premium 4Kを日本向けに比較。1か月、¥453。',price:453,old価格:544,duration:'1か月',access:'共有アクセス',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'linkedin',name:'LinkedIn Premium',category:'Business',description:'LinkedIn Premiumを日本向けに比較。2か月、¥1,075。',price:1075,old価格:1290,duration:'2か月',access:'招待形式',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']},
  {id:'windows',name:'Windows 11 Pro License Key',category:'Software',description:'Windows 11 Pro License Keyを日本向けに比較。¥1,245。ライセンス条件は注文前に確認します。',price:1245,old価格:1494,duration:'永久ライセンス',access:'ライセンスキー',delivery:'15–60 min',warranty:'7 Days',rating:4.8,badge:'Japan',bestFor:['AI','Work'],logo:'../assets/brand-logo-light.webp',features:['Plan details confirmed before payment','Japanese and English WhatsApp support'],intent:['ai','work','study','creator']}
];

const categoryData = [
  ['AI Assistants','AI','2 tools'],
  ['AI Video','▶','2 tools'],
  ['Design','✦','4 tools'],
  ['Development','</>','3 tools'],
  ['Productivity','P','2 tools'],
  ['AI Voice','∿','1 tool'],
  ['VPN & Security','S','2 tools'],
  ['Entertainment','E','2 tools'],
  ['Business','B','1 tool'],
  ['Software','W','1 tool']
];

const officialLogos = {
  chatgpt: 'https://www.google.com/s2/favicons?domain=chatgpt.com&sz=128',
  gemini: 'https://www.google.com/s2/favicons?domain=gemini.google.com&sz=128',
  veo: 'https://www.google.com/s2/favicons?domain=deepmind.google&sz=128',
  leonardo: 'https://www.google.com/s2/favicons?domain=leonardo.ai&sz=128',
  elevenlabs: 'https://www.google.com/s2/favicons?domain=elevenlabs.io&sz=128',
  canva: 'https://www.google.com/s2/favicons?domain=canva.com&sz=128',
  figma: 'https://www.google.com/s2/favicons?domain=figma.com&sz=128',
  capcut: 'https://www.google.com/s2/favicons?domain=capcut.com&sz=128',
  adobe: 'https://www.google.com/s2/favicons?domain=adobe.com&sz=128',
  lovable: 'https://www.google.com/s2/favicons?domain=lovable.dev&sz=128',
  gamma: 'https://www.google.com/s2/favicons?domain=gamma.app&sz=128',
  replit: 'https://www.google.com/s2/favicons?domain=replit.com&sz=128',
  n8n: 'https://www.google.com/s2/favicons?domain=n8n.io&sz=128',
  notion: 'https://www.google.com/s2/favicons?domain=notion.so&sz=128',
  nordvpn: 'https://www.google.com/s2/favicons?domain=nordvpn.com&sz=128',
  surfshark: 'https://www.google.com/s2/favicons?domain=surfshark.com&sz=128',
  youtube: 'https://www.google.com/s2/favicons?domain=youtube.com&sz=128',
  netflix: 'https://www.google.com/s2/favicons?domain=netflix.com&sz=128',
  linkedin: 'https://www.google.com/s2/favicons?domain=linkedin.com&sz=128',
  windows: 'https://www.google.com/s2/favicons?domain=microsoft.com&sz=128'
};

products.forEach(p => {
  if (officialLogos[p.id]) {
    p.logo = officialLogos[p.id];
  }
});

const safeCatalogText = value => String(value || '').replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[char]);

try {
  const managedCatalog = JSON.parse(localStorage.getItem('atg-admin-products') || '[]');
  if (Array.isArray(managedCatalog)) {
    managedCatalog.forEach(saved => {
      const existing = products.find(product => product.id === saved.id);
      if (existing) {
        if (saved.name) existing.name = safeCatalogText(saved.name);
        if (saved.category) existing.category = safeCatalogText(saved.category);
        if (Number(saved.price) > 0) existing.price = Number(saved.price);
        if (saved.description) existing.description = safeCatalogText(saved.description);
        if (saved.logo && /^(https:\/\/|assets\/)/.test(saved.logo)) existing.logo = saved.logo;
      } else if (saved.id && saved.name && saved.category && Number(saved.price) > 0) {
        products.push({
          id: saved.id,
          name: safeCatalogText(saved.name),
          category: safeCatalogText(saved.category),
          description: saved.description ? safeCatalogText(saved.description) : 'A newly added subscription. Contact our team for complete plan details.',
          price: Number(saved.price),
          old価格: Math.ceil(Number(saved.price) * 1.2),
          duration: '1 Month',
          access: 'Private',
          delivery: '30–60 min',
          warranty: '7 Days',
          rating: 4.5,
          badge: 'New',
          bestFor: [safeCatalogText(saved.category)],
          logo: saved.logo && /^(https:\/\/|assets\/)/.test(saved.logo) ? saved.logo : '../assets/brand-logo-light.webp',
          features: ['Plan details confirmed before payment', 'Direct WhatsApp activation'],
          intent: [String(saved.category).toLowerCase(), String(saved.name).toLowerCase()]
        });
      }
    });
  }
} catch {
  localStorage.removeItem('atg-admin-products');
}

function loadStoredカート() {
  try {
    const saved = JSON.parse(localStorage.getItem('atg-cart') || '[]');
    return Array.isArray(saved) ? saved.filter(id => products.some(p => p.id === id)) : [];
  } catch {
    localStorage.removeItem('atg-cart');
    return [];
  }
}

let state = {
  category: 'All',
  query: '',
  limit: 20,
  cart: loadStoredカート(),
  compare: [],
  finder: { intent: '', minBudget: 0, maxBudget: Infinity }
};

const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const money = n => '¥' + n.toLocaleString('ja-JP');
const discount = p => Math.round((1 - p.price / p.old価格) * 100);
const svg = id => `<svg><use href="#${id}"></use></svg>`;
const escapeHTML = value => String(value).replace(/[&<>'"]/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' })[char]);

window.dataLayer = window.dataLayer || [];
function trackEvent(event, details = {}) {
  window.dataLayer.push({ event, ...details });
}

function clear検索Field() {
  const input = $('#hero検索');
  if (input) input.value = '';
}

/* --------------------------------------------------------------------------
   RENDERING FUNCTIONS
   -------------------------------------------------------------------------- */
function renderカテゴリー() {
  const container = $('#categoryGrid');
  if (!container) return;
  container.innerHTML = categoryData.map((c, index) => {
    const count = products.filter(product => product.category === c[0]).length;
    return `
    <button class="category-card" data-category="${c[0]}" aria-label="Explore ${c[0]}">
      <span class="category-visual" style="--category-x:${(index % 5) * 25}%;--category-y:${index < 5 ? 0 : 100}%">
        <span class="category-count">${count} ${count === 1 ? 'tool' : 'tools'}</span>
      </span>
      <span class="category-content">
        <span>
          <small>Explore Collection</small>
          <b>${c[0]}</b>
        </span>
        <i aria-hidden="true">${svg('i-arrow')}</i>
      </span>
    </button>`;
  }).join('');
}

function renderFilters() {
  const cats = ['All','AI Assistants','AI Video','Design','Development','Productivity','VPN & Security','Entertainment'];
  const row = $('#filterRow');
  if (!row) return;
  row.innerHTML = cats.map(c => `
    <button class="filter-chip ${state.category === c ? 'active' : ''}" data-filter="${c}" aria-pressed="${state.category === c}">${c}</button>
  `).join('');
}

function filteredProducts() {
  let out = products.filter(p => state.category === 'All' || p.category === state.category);
  const q = state.query.toLowerCase().trim();
  if (q === 'under 1000') {
    out = out.filter(p => p.price < 1000);
  } else if (q) {
    out = out.filter(p => [p.name, p.category, p.description, ...p.bestFor, ...p.intent].join(' ').toLowerCase().includes(q));
  }
  const sort = $('#sortSelect') ? $('#sortSelect').value : 'featured';
  if (sort === 'price-low') out.sort((a, b) => a.price - b.price);
  if (sort === 'rating') out.sort((a, b) => b.rating - a.rating);
  if (sort === 'discount') out.sort((a, b) => discount(b) - discount(a));
  return out;
}

function card(p) {
  const inカート = state.cart.includes(p.id);
  const comparing = state.compare.includes(p.id);
  return `
  <article class="product-card" data-id="${p.id}">
    <div class="product-media">
      <span class="product-badge">${p.badge}</span>
      <button class="compare-toggle ${comparing ? 'active' : ''}" data-compare="${p.id}" aria-label="Compare ${p.name}">
        ${svg(comparing ? 'i-check' : 'i-plus')}
      </button>
      <img class="brand-logo" src="${p.logo}" width="128" height="128" loading="lazy" alt="Official ${p.name} logo" decoding="async" referrerpolicy="no-referrer">
    </div>
    <div class="product-body">
      <div class="product-meta">
        <span>${p.category}</span>
        <span class="rating">JPY pricing</span>
      </div>
      <h3><a class="product-page-link" href="tools/${p.id}/">${p.name}</a></h3>
      <p class="product-desc">${p.description}</p>
      <div class="tags">
        ${p.bestFor.map(t => `<span>${t}</span>`).join('')}
      </div>
      <div class="product-specs">
        <span><i></i>${p.duration}</span>
        <span>${p.access} Plan</span>
      </div>
      <div class="product-price">
        <div class="price-block">
          <small>${money(p.old価格)}</small>
          <strong>${money(p.price)}</strong>
        </div>
        <span class="saving">Save ${discount(p)}%</span>
      </div>
      <div class="card-actions">
        <button class="buy-now-card" data-order="${p.id}">${svg('i-whatsapp')} 今すぐ注文</button>
        <button class="detail-button" data-detail="${p.id}">View details</button>
        <button class="add-button ${inカート ? 'added' : ''}" data-add="${p.id}" aria-label="${inカート ? 'Remove' : 'Add'} ${p.name} ${inカート ? 'from' : 'to'} cart" aria-pressed="${inカート}">
          ${svg(inカート ? 'i-check' : 'i-plus')}
        </button>
      </div>
    </div>
  </article>`;
}

function renderProducts() {
  const all = filteredProducts();
  const shown = all.slice(0, state.limit);
  const grid = $('#productGrid');
  if (grid) grid.innerHTML = shown.map(card).join('');
  
  const empty = $('#emptyState');
  if (empty) empty.classList.toggle('show', !all.length);
  
  const aq = $('#activeQuery');
  if (aq) {
    aq.classList.toggle('show', !!state.query);
    aq.innerHTML = state.query ? `Showing verified results for “${escapeHTML(state.query)}” · <button id="clearQuery">Clear search</button>` : '';
  }
  
  renderFilters();
}

/* --------------------------------------------------------------------------
   CART & COMPARE LOGIC
   -------------------------------------------------------------------------- */
function updateカート() {
  localStorage.setItem('atg-cart', JSON.stringify(state.cart));
  const cCount = $('#cartCount');
  const mCount = $('#mobileカートCount');
  if (cCount) cCount.textContent = state.cart.length;
  if (mCount) mCount.textContent = state.cart.length;

  const selected = state.cart.map(id => products.find(p => p.id === id)).filter(Boolean);
  const cartItems = $('#cartItems');
  if (cartItems) {
    cartItems.innerHTML = selected.length ? selected.map(p => `
      <div class="cart-item">
        <img src="${p.logo}" width="128" height="128" loading="lazy" alt="${p.name}">
        <span>
          <b>${p.name}</b>
          <small>${p.duration} · ${p.access} Plan</small>
          <strong>${money(p.price)}</strong>
        </span>
        <button class="remove-cart" data-remove="${p.id}" aria-label="Remove ${p.name}">×</button>
      </div>
    `).join('') : `
      <div class="cart-empty">
        <img src="../assets/logo-transparent.webp" width="1024" height="1024" loading="lazy" class="empty-state-logo" alt="AI Tool Gems Diamond">
        <h3>Your cart is empty</h3>
        <p>Explore the 3D marketplace and add tools here.</p>
      </div>
    `;
  }

  const totalEl = $('#cartTotal');
  if (totalEl) totalEl.textContent = money(selected.reduce((s, p) => s + p.price, 0));
  
  const footer = $('#cartFooter');
  if (footer) footer.style.display = selected.length ? 'block' : 'none';
  updateBundleButton();
}

function updateBundleButton() {
  const button = $('#addBundle');
  if (!button) return;
  const bundleIds = ['chatgpt', 'canva', 'capcut', 'elevenlabs'];
  const isComplete = bundleIds.every(id => state.cart.includes(id));
  button.classList.toggle('added', isComplete);
  button.setAttribute('aria-pressed', String(isComplete));
  button.innerHTML = isComplete ? `Stack in cart ${svg('i-check')}` : `Add creator stack ${svg('i-plus')}`;
}

function toggleカート(id) {
  const wasInカート = state.cart.includes(id);
  state.cart = state.cart.includes(id) ? state.cart.filter(x => x !== id) : [...state.cart, id];
  const product = products.find(p => p.id === id);
  if (product) trackEvent(wasInカート ? 'remove_from_cart' : 'add_to_cart', { item_id: product.id, item_name: product.name, value: product.price, currency: 'JPY' });
  updateカート();
  renderProducts();
  toast(state.cart.includes(id) ? 'Added to your cart' : 'Removed from cart');
}

function updateCompare() {
  const compCount = $('#compareCount');
  const compBar = $('#compareBar');
  const compMini = $('#compareMini');
  if (compCount) compCount.textContent = state.compare.length;
  if (compBar) compBar.classList.toggle('show', state.compare.length > 0);
  document.body.classList.toggle('compare-mode', state.compare.length > 0);
  if (compMini) {
    compMini.innerHTML = state.compare.map(id => {
      const p = products.find(x => x.id === id);
      return `<img src="${p.logo}" width="128" height="128" alt="${p.name}">`;
    }).join('');
  }
}

function toggleCompare(id) {
  if (state.compare.includes(id)) {
    state.compare = state.compare.filter(x => x !== id);
  } else if (state.compare.length < 3) {
    state.compare.push(id);
  } else {
    return toast('You can compare up to 3 tools at once');
  }
  updateCompare();
  renderProducts();
}

let focusBeforeLayer = null;

function openLayer(el) {
  if (!el) return;
  focusBeforeLayer = document.activeElement;
  const backdrop = $('#backdrop');
  if (backdrop) backdrop.classList.add('show');
  el.classList.add('open');
  el.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
  requestAnimationFrame(() => {
    const first = el.querySelector('[data-close], button, a, input, select, [tabindex="0"]');
    if (first) first.focus();
  });
}

function closeLayers() {
  $$('.drawer, .modal').forEach(x => {
    x.classList.remove('open');
    x.setAttribute('aria-hidden', 'true');
  });
  const backdrop = $('#backdrop');
  if (backdrop) backdrop.classList.remove('show');
  document.body.style.overflow = '';
  if (focusBeforeLayer && document.contains(focusBeforeLayer)) focusBeforeLayer.focus();
  focusBeforeLayer = null;
}

function openProduct(id) {
  const p = products.find(x => x.id === id);
  if (!p) return;
  trackEvent('view_item', { item_id: p.id, item_name: p.name, item_category: p.category, value: p.price, currency: 'JPY' });
  const detail = $('#productDetail');
  if (detail) {
    detail.innerHTML = `
      <div class="product-detail">
        <div class="detail-media">
          <img class="brand-logo" src="${p.logo}" width="128" height="128" alt="Official ${p.name} logo">
        </div>
        <div class="detail-copy">
          <span class="detail-category">${p.category} · ${p.badge}</span>
          <h2 id="productDetailTitle">${p.name}</h2>
          <div class="detail-rating">Plan details confirmed before payment</div>
          <p>${p.description} Availability, access type, and delivery timing are confirmed directly on WhatsApp before payment.</p>
          <div class="detail-price">${money(p.price)} <del>${money(p.old価格)}</del></div>
          <div class="detail-grid">
            <div class="detail-spec"><small>Plan duration</small><b>${p.duration}</b></div>
            <div class="detail-spec"><small>アクセス type</small><b>${p.access} Plan</b></div>
            <div class="detail-spec"><small>Delivery speed</small><b>${p.delivery}</b></div>
            <div class="detail-spec"><small>Warranty</small><b>${p.warranty}</b></div>
          </div>
          <div class="feature-list">
            ${p.features.map(f => `<span>${svg('i-check')}${f}</span>`).join('')}
          </div>
          <div class="detail-actions">
            <button class="add-detail" data-add="${p.id}">${state.cart.includes(p.id) ? 'Added to cart' : 'Add to cart'}</button>
            <button class="order-now" data-order="${p.id}">${svg('i-whatsapp')} WhatsAppで注文</button>
          </div>
          <a class="full-details-link" href="tools/${p.id}/">Open full product page ${svg('i-arrow')}</a>
        </div>
      </div>
    `;
  }
  openLayer($('#productModal'));
}

function waLink(message) {
  const saved = localStorage.getItem('atg-whatsapp');
  const cleanSaved = (saved || '').replace(/\D/g, '');
  if (cleanSaved === LEGACY_WA_NUMBER) localStorage.setItem('atg-whatsapp', DEFAULT_WA_NUMBER);
  const number = /^\d{10,15}$/.test(cleanSaved)
    && cleanSaved !== '923001234567'
    && cleanSaved !== LEGACY_WA_NUMBER
    ? cleanSaved
    : DEFAULT_WA_NUMBER;
  const attributedMessage = window.ATGAttribution ? window.ATGAttribution.appendToMessage(message) : message;
  return `https://wa.me/${number}?text=${encodeURIComponent(attributedMessage)}`;
}

function orderProduct(id) {
  const p = products.find(x => x.id === id);
  if (!p) return;
  trackEvent('whatsapp_checkout', { item_id: p.id, item_name: p.name, value: p.price, currency: 'JPY' });
  window.open(waLink(`Hello AI Tool Gems 👋\n\nI would like to order:\n\n💎 Product: ${p.name}\n⏱️ 期間: ${p.duration}\n🔑 アクセス: ${p.access}\n💰 価格: ${money(p.price)}\n\nPlease confirm payment details and delivery time.`), '_blank');
}

function checkout() {
  const selected = state.cart.map(id => products.find(p => p.id === id)).filter(Boolean);
  if (!selected.length) return;
  const total = selected.reduce((s, p) => s + p.price, 0);
  trackEvent('begin_checkout', { item_ids: selected.map(p => p.id), item_count: selected.length, value: total, currency: 'JPY', destination: 'whatsapp' });
  const lines = selected.map((p, i) => `${i + 1}. ${p.name} (${p.duration}, ${p.access}) — ${money(p.price)}`).join('\n');
  window.open(waLink(`Hello AI Tool Gems 👋\n\nI want to place an order for my cart:\n\n${lines}\n\n💎 Total: ${money(total)}\n\nPlease confirm availability, the accepted payment route, and delivery time.`), '_blank');
}

function showSuggestions(q) {
  const box = $('#suggestions');
  if (!box) return;
  if (!q.trim()) {
    box.classList.remove('show');
    return;
  }
  const hits = products.filter(p => [p.name, p.category, ...p.intent].join(' ').toLowerCase().includes(q.toLowerCase())).slice(0, 5);
  box.innerHTML = hits.length ? hits.map(p => `
    <button type="button" class="suggestion" data-suggest="${p.id}">
      <img src="${p.logo}" width="128" height="128" loading="lazy" alt="${p.name}">
      <span>${p.name}</span>
      <small>${money(p.price)}</small>
    </button>
  `).join('') : `
    <div class="suggestion"><span>No matching tools found</span></div>
  `;
  box.classList.add('show');
}

function apply検索(q) {
  state.query = q;
  state.limit = 20;
  const sInput = $('#hero検索');
  if (sInput) sInput.value = q;
  const box = $('#suggestions');
  if (box) box.classList.remove('show');
  renderProducts();
  const prodSec = $('#products');
  if (prodSec) prodSec.scrollIntoView({ behavior: 'smooth' });
}

function renderCompare() {
  const ps = state.compare.map(id => products.find(p => p.id === id));
  const content = $('#compareContent');
  if (!content) return;
  content.innerHTML = ps.length < 2 ? `
    <div class="cart-empty">
      <img src="../assets/logo-transparent.webp" width="1024" height="1024" loading="lazy" class="empty-state-logo" alt="">
      <h3>Select one more tool</h3>
      <p>2〜3個の商品を選択 to compare features and prices side by side.</p>
    </div>
  ` : `
    <table class="compare-table">
      <thead>
        <tr>
          <th></th>
          ${ps.map(p => `<th><img src="${p.logo}" width="128" height="128" alt="">${p.name}</th>`).join('')}
        </tr>
      </thead>
      <tbody>
        ${[
          ['価格', p => money(p.price)],
          ['期間', p => p.duration],
          ['アクセス Type', p => p.access],
          ['Delivery', p => p.delivery],
          ['Warranty', p => p.warranty],
          ['Best For', p => p.bestFor.join(', ')]
        ].map(r => `
          <tr>
            <td>${r[0]}</td>
            ${ps.map(p => `<td>${r[1](p)}</td>`).join('')}
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
  openLayer($('#compareDrawer'));
}

/* --------------------------------------------------------------------------
   GUIDED FINDER MODAL STEPS
   -------------------------------------------------------------------------- */
function finderStep(step = 1) {
  const root = $('#finderSteps');
  if (!root) return;
  if (step === 1) {
    root.innerHTML = `
      <div class="finder-step">
        <div class="progress"><span style="width:33%"></span></div>
        <div class="eyebrow dark"><span></span> Step 1 of 3</div>
        <h2 id="finderTitle">What outcome are you pursuing?</h2>
        <p>Choose your primary ambition to get tailored tool matches.</p>
        <div class="finder-choices">
          ${[
            ['video','Create AI Videos'],
            ['image','Generate Visuals & Art'],
            ['writing','Write Copy & Research'],
            ['code','Build Software & Code'],
            ['presentation','Design Presentations'],
            ['voice','Generate Voice & Audio'],
            ['automation','Automate Workflows'],
            ['study','University & Research'],
            ['design','UI/UX & Graphics']
          ].map(x => `
            <button class="finder-choice" data-intent="${x[0]}">
              ${x[1]}
              <small>View top gems</small>
            </button>
          `).join('')}
        </div>
      </div>
    `;
  }
  if (step === 2) {
    root.innerHTML = `
      <div class="finder-step">
        <div class="progress"><span style="width:66%"></span></div>
        <div class="eyebrow dark"><span></span> Step 2 of 3</div>
        <h2 id="finderTitle">What is your budget target?</h2>
        <p>We’ll prioritize tools with the highest verified ROI in your range.</p>
        <div class="finder-choices">
          <button class="finder-choice" data-budget-min="0" data-budget-max="999">Under Rs. 1,000<small>Budget friendly</small></button>
          <button class="finder-choice" data-budget-min="1000" data-budget-max="2500">Rs. 1,000 – 2,500<small>Most popular tier</small></button>
          <button class="finder-choice" data-budget-min="2501" data-budget-max="5000">Rs. 2,500 – 5,000<small>Power creator</small></button>
          <button class="finder-choice" data-budget-min="5001" data-budget-max="999999">Rs. 5,000+<small>Annual &amp; teams</small></button>
        </div>
        <button class="finder-back" type="button" data-finder-back="1">← Change your goal</button>
      </div>
    `;
  }
  if (step === 3) {
    let matches = products.filter(p => p.intent.includes(state.finder.intent) && p.price >= state.finder.minBudget && p.price <= state.finder.maxBudget).sort((a, b) => a.price - b.price).slice(0, 3);
    let outsideBudget = false;
    if (!matches.length) {
      matches = products.filter(p => p.intent.includes(state.finder.intent)).sort((a, b) => a.price - b.price).slice(0, 3);
      outsideBudget = true;
    }
    root.innerHTML = `
      <div class="finder-step">
        <div class="progress"><span style="width:100%"></span></div>
        <div class="eyebrow dark"><span></span> Step 3 of 3 · Recommendation ready</div>
        <h2 id="finderTitle">${outsideBudget ? 'Closest available matches' : 'Your best tool matches'}</h2>
        <p>${outsideBudget ? 'No exact tool is available in that budget. These are the lowest-priced relevant options, shown transparently.' : 'Matched for your objective and exact budget range using the catalog details shown.'}</p>
        <div class="finder-results">
          ${matches.map((p, i) => `
            <button class="finder-result" data-detail="${p.id}">
              <img src="${p.logo}" width="128" height="128" loading="lazy" alt="${p.name}">
              <div>
                <small>${outsideBudget ? 'CLOSEST OPTION · ABOVE BUDGET' : (i === 0 ? 'TOP BUDGET MATCH' : 'RECOMMENDED OPTION')}</small>
                <b>${p.name}</b>
                <span>${p.bestFor.join(' · ')} · ${p.duration}</span>
              </div>
              <strong>${money(p.price)}</strong>
            </button>
          `).join('')}
        </div>
        <button class="finder-back" type="button" data-finder-back="2">← Change your budget</button>
      </div>
    `;
  }
}

const finderPreviewPresets = {
  video: {
    counter: '01 / 04',
    badge: 'Top match · 96% fit',
    id: 'veo',
    name: 'Veo 3 Ultra',
    desc: 'Unlimited cinematic video generation with photorealistic physics',
    price: 2100,
    logo: 'https://www.google.com/s2/favicons?domain=deepmind.google&sz=128'
  },
  image: {
    counter: '02 / 04',
    badge: 'Top match · 98% fit',
    id: 'leonardo',
    name: 'Leonardo AI Essential',
    desc: 'Production-ready digital art, photorealistic assets & visuals',
    price: 1900,
    logo: 'https://www.google.com/s2/favicons?domain=leonardo.ai&sz=128'
  },
  writing: {
    counter: '03 / 04',
    badge: 'Top match · 99% fit',
    id: 'chatgpt',
    name: 'ChatGPT Plus',
    desc: 'Advanced research, coding, writing and creative assistance',
    price: 2300,
    logo: 'https://www.google.com/s2/favicons?domain=chatgpt.com&sz=128'
  },
  code: {
    counter: '04 / 04',
    badge: 'Top match · 95% fit',
    id: 'lovable',
    name: 'Lovable Pro',
    desc: 'Build, design and ship full-stack web applications and MVPs',
    price: 1600,
    logo: 'https://www.google.com/s2/favicons?domain=lovable.dev&sz=128'
  }
};

function updateFinderPreview(intent) {
  const data = finderPreviewPresets[intent] || finderPreviewPresets.video;
  $$('.preview-option').forEach(btn => {
    const selected = btn.dataset.previewIntent === intent;
    btn.classList.toggle('selected', selected);
    btn.setAttribute('aria-pressed', String(selected));
  });
  const counter = $('#previewCounter');
  if (counter) counter.textContent = data.counter;
  const badge = $('#finderMatchBadge');
  if (badge) badge.textContent = data.badge;
  const name = $('#finderMatchName');
  if (name) name.textContent = data.name;
  const desc = $('#finderMatchDesc');
  if (desc) desc.textContent = data.desc;
  const price = $('#finderMatch価格');
  if (price) price.textContent = money(data.price);
  const logo = $('#finderMatchLogo');
  if (logo) {
    logo.src = data.logo;
    logo.alt = data.name;
  }
  const card = $('#finderMatchCard');
  if (card) {
    card.dataset.detail = data.id;
    card.setAttribute('aria-label', `View recommended ${data.name} details`);
    card.classList.remove('pulse-update');
    void card.offsetWidth;
    card.classList.add('pulse-update');
  }
}

function openFinder() {
  state.finder = { intent: '', minBudget: 0, maxBudget: Infinity };
  trackEvent('finder_start');
  finderStep(1);
  openLayer($('#finderModal'));
}

let toastTimer;
function toast(msg) {
  const t = $('#toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 2200);
}

/* --------------------------------------------------------------------------
   3D INTERACTIVE PHYSICS & TILT ENGINE
   -------------------------------------------------------------------------- */
function init3dHero() {
  const stage = $('#heroVisualStage');
  const gem = $('#hero3dGem');
  const orbits = $('#heroOrbitSystem');
  const cards = $$('.hero-visual .float-card');
  if (!stage || !gem) return;

  let targetX = 0, targetY = 0;
  let currentX = 0, currentY = 0;
  let animationFrame = 0;
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function onMouseMove(e) {
    const rect = stage.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    targetX = x * 24; // tilt degrees
    targetY = -y * 24;
    if (!reducedMotion && !animationFrame) animationFrame = requestAnimationFrame(renderHero3d);
  }

  function onMouseLeave() {
    targetX = 0;
    targetY = 0;
    if (!reducedMotion && !animationFrame) animationFrame = requestAnimationFrame(renderHero3d);
  }

  function renderHero3d() {
    currentX += (targetX - currentX) * 0.08;
    currentY += (targetY - currentY) * 0.08;

    if (gem) {
      gem.style.transform = `translateZ(50px) rotateY(${currentX * 0.9}deg) rotateX(${currentY * 0.9}deg)`;
    }
    if (orbits) {
      orbits.style.transform = `translate(-50%, -50%) rotateY(${currentX * 0.4}deg) rotateX(${currentY * 0.4}deg)`;
    }
    cards.forEach(c => {
      const depth = Number(c.dataset.depth || 45);
      c.style.transform = `translate(${currentX * 0.35}px, ${-currentY * 0.35}px) translateZ(${depth}px) rotateY(${currentX * 0.5}deg) rotateX(${currentY * 0.5}deg)`;
    });

    const stillMoving = Math.abs(targetX - currentX) > 0.02 || Math.abs(targetY - currentY) > 0.02;
    animationFrame = stillMoving ? requestAnimationFrame(renderHero3d) : 0;
  }

  stage.addEventListener('mousemove', onMouseMove);
  stage.addEventListener('mouseleave', onMouseLeave);
  if (!reducedMotion && 'IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      const visible = entries[0]?.isIntersecting && !document.hidden;
      if (!visible && animationFrame) {
        cancelAnimationFrame(animationFrame);
        animationFrame = 0;
      }
    }, { threshold: 0.05 });
    observer.observe(stage);
    document.addEventListener('visibilitychange', () => {
      if (document.hidden && animationFrame) {
        cancelAnimationFrame(animationFrame);
        animationFrame = 0;
      }
    });
  }
}

function init3dCards() {
  const grid = $('#productGrid');
  if (!grid) return;

  grid.addEventListener('mousemove', e => {
    const c = e.target.closest('.product-card');
    if (!c) return;
    const rect = c.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    const rotateX = ((y - centerY) / centerY) * -10;
    const rotateY = ((x - centerX) / centerX) * 10;

    c.style.setProperty('--rx', `${rotateX.toFixed(2)}deg`);
    c.style.setProperty('--ry', `${rotateY.toFixed(2)}deg`);
    c.style.setProperty('--mx', `${((x / rect.width) * 100).toFixed(1)}%`);
    c.style.setProperty('--my', `${((y / rect.height) * 100).toFixed(1)}%`);
  });

  grid.addEventListener('mouseleave', e => {
    const c = e.target.closest('.product-card');
    if (c) {
      c.style.setProperty('--rx', '0deg');
      c.style.setProperty('--ry', '0deg');
    }
  }, true);
}

/* --------------------------------------------------------------------------
   GLOBAL EVENT DELEGATION
   -------------------------------------------------------------------------- */
document.addEventListener('click', e => {
  const add = e.target.closest('[data-add]');
  if (add) {
    toggleカート(add.dataset.add);
    if ($('#productModal').classList.contains('open')) openProduct(add.dataset.add);
    return;
  }
  const remove = e.target.closest('[data-remove]');
  if (remove) {
    toggleカート(remove.dataset.remove);
    return;
  }
  const comp = e.target.closest('[data-compare]');
  if (comp) {
    toggleCompare(comp.dataset.compare);
    return;
  }
  const detail = e.target.closest('[data-detail]');
  if (detail) {
    closeLayers();
    setTimeout(() => openProduct(detail.dataset.detail), 50);
    return;
  }
  const filter = e.target.closest('[data-filter]');
  if (filter) {
    state.category = filter.dataset.filter;
    state.limit = 20;
    renderProducts();
    return;
  }
  const cat = e.target.closest('[data-category]');
  if (cat) {
    state.category = cat.dataset.category;
    state.query = '';
    clear検索Field();
    state.limit = 20;
    renderProducts();
    $('#products').scrollIntoView({ behavior: 'smooth' });
    return;
  }
  const catLink = e.target.closest('[data-category-link]');
  if (catLink) {
    state.category = catLink.dataset.categoryLink;
    state.query = '';
    clear検索Field();
    renderProducts();
    return;
  }
  const query = e.target.closest('[data-query]');
  if (query) {
    apply検索(query.dataset.query);
    return;
  }
  const suggestion = e.target.closest('[data-suggest]');
  if (suggestion) {
    openProduct(suggestion.dataset.suggest);
    $('#suggestions').classList.remove('show');
    return;
  }
  const intent = e.target.closest('[data-intent]');
  if (intent) {
    state.finder.intent = intent.dataset.intent;
    finderStep(2);
    return;
  }
  const budget = e.target.closest('[data-budget-min]');
  if (budget) {
    state.finder.minBudget = Number(budget.dataset.budgetMin);
    state.finder.maxBudget = Number(budget.dataset.budgetMax);
    finderStep(3);
    return;
  }
  const finderBack = e.target.closest('[data-finder-back]');
  if (finderBack) {
    finderStep(Number(finderBack.dataset.finderBack));
    return;
  }
  const order = e.target.closest('[data-order]');
  if (order) {
    orderProduct(order.dataset.order);
    return;
  }
  const previewOpt = e.target.closest('[data-preview-intent]');
  if (previewOpt) {
    updateFinderPreview(previewOpt.dataset.previewIntent);
    return;
  }
  const stepAction = e.target.closest('[data-step-action]');
  if (stepAction) {
    const action = stepAction.dataset.stepAction;
    if (action === 'search') {
      const ps = $('#products');
      if (ps) ps.scrollIntoView({ behavior: 'smooth' });
      if (hero検索) hero検索.focus();
    } else if (action === 'cart') {
      openLayer($('#cartDrawer'));
    } else if (action === 'whatsapp') {
      window.open(waLink('Hello AI Tool Gems 👋\n\nI would like to order an AI tool and have a quick question.'), '_blank');
    } else if (action === 'warranty') {
      toast('✓ Exact delivery time and replacement warranty are shown on every tool');
      const faq = $('#faqList');
      if (faq) faq.scrollIntoView({ behavior: 'smooth' });
    }
    return;
  }
  const orderBundle = e.target.closest('#orderBundleWa');
  if (orderBundle) {
    window.open(waLink(`Hello AI Tool Gems 👋\n\nI want to order the Creator Stack Power Bundle (4 Tools):\n1. ChatGPT Plus (1 Month, Private) — Rs. 2,300\n2. Canva Pro Edu (1 Year, Invitation) — Rs. 900\n3. CapCut Pro (1 Month, Private) — Rs. 900\n4. ElevenLabs (1 Month, Private) — Rs. 3,300\n\n💎 Bundle Total: Rs. 7,400\n\nPlease confirm availability, the accepted payment route, and activation time.`), '_blank');
    return;
  }
  const wa = e.target.closest('[data-whatsapp]');
  if (wa) {
    e.preventDefault();
    window.open(waLink('Hello AI Tool Gems, I need assistance choosing a premium AI tool.'), '_blank');
    return;
  }
  if (e.target.closest('[data-open-finder]')) {
    e.preventDefault();
    openFinder();
    return;
  }
  if (e.target.closest('[data-close]') || e.target.id === 'backdrop') {
    closeLayers();
    return;
  }
  if (e.target.id === 'clearQuery') {
    state.query = '';
    clear検索Field();
    renderProducts();
    return;
  }
  if (!e.target.closest('.search-wrap')) {
    const suggestions = $('#suggestions');
    if (suggestions) suggestions.classList.remove('show');
  }
});

/* 検索 listeners */
const hero検索 = $('#hero検索');
if (hero検索) {
  hero検索.addEventListener('input', e => showSuggestions(e.target.value));
  hero検索.addEventListener('keydown', e => {
    if (e.key === 'Enter') apply検索(e.target.value);
    if (e.key === 'Escape') $('#suggestions').classList.remove('show');
  });
}

const open検索 = $('#open検索');
if (open検索 && hero検索) {
  open検索.onclick = () => {
    hero検索.focus();
    hero検索.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };
}

document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault();
    if (hero検索) {
      hero検索.focus();
      hero検索.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }
  if (e.key === 'Escape') {
    closeLayers();
    const mobNav = $('#mobileNav');
    if (mobNav) mobNav.classList.remove('show');
    const menuBtn = $('#menuButton');
    if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false');
  }
  if ((e.key === 'Enter' || e.key === ' ') && e.target.matches('[role="button"][tabindex="0"]')) {
    e.preventDefault();
    e.target.click();
  }

  const openLayerEl = $('.drawer.open, .modal.open');
  if (e.key === 'Tab' && openLayerEl) {
    const focusable = [...openLayerEl.querySelectorAll('button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), [tabindex="0"]')];
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }
});

const openカート = $('#openカート');
const mobileカート = $('#mobileカート');
if (openカート) openカート.onclick = () => openLayer($('#cartDrawer'));
if (mobileカート) mobileカート.onclick = () => openLayer($('#cartDrawer'));

const checkoutWA = $('#checkoutWhatsApp');
if (checkoutWA) checkoutWA.onclick = checkout;

const openComp = $('#openCompare');
if (openComp) openComp.onclick = renderCompare;

const sortSel = $('#sortSelect');
if (sortSel) sortSel.onchange = renderProducts;

const filterTog = $('#filterToggle');
if (filterTog) {
  filterTog.onclick = () => {
    const row = $('#filterRow');
    if (row) {
      row.classList.toggle('closed');
      filterTog.setAttribute('aria-expanded', String(!row.classList.contains('closed')));
    }
  };
}

const clearFilt = $('#clearFilters');
if (clearFilt) {
  clearFilt.onclick = () => {
    state.category = 'All';
    state.query = '';
    clear検索Field();
    renderProducts();
  };
}

const menuBtn = $('#menuButton');
if (menuBtn) {
  menuBtn.setAttribute('aria-expanded', 'false');
  menuBtn.setAttribute('aria-controls', 'mobileNav');
  menuBtn.onclick = () => {
    const mobNav = $('#mobileNav');
    if (mobNav) {
      const isOpen = mobNav.classList.toggle('show');
      menuBtn.setAttribute('aria-expanded', String(isOpen));
    }
  };
}

const mobileNav = $('#mobileNav');
if (mobileNav) {
  mobileNav.addEventListener('click', e => {
    if (!e.target.closest('a')) return;
    mobileNav.classList.remove('show');
    if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false');
  });
}

const footerCompare = $('#footerCompare');
if (footerCompare) {
  footerCompare.addEventListener('click', e => {
    e.preventDefault();
    if (state.compare.length >= 2) {
      renderCompare();
    } else {
      $('#products')?.scrollIntoView({ behavior: 'smooth' });
      toast('Select 2 or 3 + buttons on product cards to compare');
    }
  });
}

const addBundleBtn = $('#addBundle');
if (addBundleBtn) {
  addBundleBtn.onclick = () => {
    const bundleIds = ['chatgpt', 'canva', 'capcut', 'elevenlabs'];
    if (bundleIds.every(id => state.cart.includes(id))) {
      openLayer($('#cartDrawer'));
      return;
    }
    bundleIds.forEach(id => {
      if (!state.cart.includes(id)) state.cart.push(id);
    });
    updateカート();
    renderProducts();
    toast('4 Creator stack tools added to your cart');
  };
}

/* --------------------------------------------------------------------------
   INITIALIZATION
   -------------------------------------------------------------------------- */
renderカテゴリー();
renderProducts();
updateカート();
updateCompare();
init3dHero();
init3dCards();
