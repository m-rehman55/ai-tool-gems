const DEFAULT_WA_NUMBER = '923476242709';

const products = [
  {id:'chatgpt',name:'ChatGPT Plus',category:'AI Assistants',description:'Advanced writing, research, coding and creative assistance with GPT-4o & reasoning.',price:2300,oldPrice:3000,duration:'1 Month',access:'Private',delivery:'15–30 min',warranty:'7 Days',rating:4.9,badge:'Best Seller',bestFor:['Writing','Coding','Study'],logo:'https://cdn.simpleicons.org/openai/FFFFFF',features:['Advanced AI models','Image generation','File analysis','Voice conversations'],intent:['writing','research','study','code','coding','content']},
  {id:'gemini',name:'Gemini Pro',category:'AI Assistants',description:'Google’s multimodal AI for deep research, documents, code and everyday workflow.',price:800,oldPrice:1500,duration:'18 Months',access:'Invitation',delivery:'30–60 min',warranty:'30 Days',rating:4.8,badge:'Best Value',bestFor:['Research','Study','Google'],logo:'https://cdn.simpleicons.org/googlegemini/FFFFFF',features:['2M token context window','Google Workspace integration','Multimodal reasoning','Deep research mode'],intent:['writing','research','study','content']},
  {id:'veo',name:'Veo 3 Ultra',category:'AI Video',description:'Generate cinematic AI video with photorealistic motion, physics, and native audio.',price:2100,oldPrice:3000,duration:'Unlimited',access:'Shared',delivery:'15–30 min',warranty:'7 Days',rating:4.9,badge:'Trending',bestFor:['Video','Ads','Creators'],logo:'https://cdn.simpleicons.org/google/FFFFFF',features:['Text to 1080p video','Native synchronized audio','Consistent motion','Unlimited generations'],intent:['video','videos','creator']},
  {id:'leonardo',name:'Leonardo AI Essential',category:'Design',description:'Create production-ready digital art, marketing visuals, assets and concepts.',price:1900,oldPrice:2600,duration:'8,500 Credits',access:'Private',delivery:'30–60 min',warranty:'7 Days',rating:4.7,badge:'For Creators',bestFor:['Images','Assets','Concepts'],logo:'https://cdn.simpleicons.org/leonardoai/FFFFFF',features:['PhotoReal & Alchemy pipeline','Realtime canvas','Prompt enhancer','Commercial license'],intent:['image','images','design','creator']},
  {id:'elevenlabs',name:'ElevenLabs',category:'AI Voice',description:'Hyper-realistic AI voice synthesis & voice cloning for reels, ads, and podcasts.',price:3300,oldPrice:4200,duration:'1 Month',access:'Private',delivery:'30–60 min',warranty:'7 Days',rating:4.8,badge:'Premium',bestFor:['Voice','Dubbing','Audio'],logo:'https://cdn.simpleicons.org/elevenlabs/FFFFFF',features:['130,000 credits/mo','Voice cloning library','Multilingual speech','Low latency API'],intent:['voice','audio','video','creator']},
  {id:'canva',name:'Canva Pro Edu',category:'Design',description:'Design social media posts, pitch decks, presentations and branded assets.',price:900,oldPrice:1800,duration:'1 Year',access:'Invitation',delivery:'15–30 min',warranty:'30 Days',rating:4.9,badge:'Best Seller',bestFor:['Design','Social','Students'],logo:'https://cdn.simpleicons.org/canva/FFFFFF',features:['100M+ premium assets','1-click background remover','Magic Studio AI tools','Cloud brand kit'],intent:['image','images','design','presentation','study','creator','social']},
  {id:'figma',name:'Figma Pro Private',category:'Design',description:'Professional interface design, prototyping and design system workspace.',price:3000,oldPrice:4800,duration:'2 Years',access:'Private',delivery:'1–2 hours',warranty:'30 Days',rating:4.8,badge:'Long Term',bestFor:['UI/UX','Teams','Web'],logo:'https://cdn.simpleicons.org/figma/FFFFFF',features:['Unlimited files & version history','Dev Mode inspection','Shared design libraries','Full prototype viewer'],intent:['design','code','coding','business']},
  {id:'capcut',name:'CapCut Pro',category:'AI Video',description:'Fast, intuitive editing suite for viral TikToks, Instagram Reels, and YouTube Shorts.',price:900,oldPrice:1400,duration:'1 Month',access:'Private',delivery:'15–30 min',warranty:'7 Days',rating:4.7,badge:'Popular',bestFor:['Reels','Shorts','Editing'],logo:'https://cdn.simpleicons.org/capcut/FFFFFF',features:['Pro video transitions & filters','Auto captions generator','AI background remover','Cloud draft sync'],intent:['video','videos','creator','social']},
  {id:'adobe',name:'Adobe Creative Cloud',category:'Design',description:'Complete suite of Photoshop, Illustrator, Premiere Pro, After Effects and Firefly.',price:1700,oldPrice:2600,duration:'2 Months',access:'Private',delivery:'1–2 hours',warranty:'7 Days',rating:4.8,badge:'Pro Choice',bestFor:['Creative','Photo','Video'],logo:'https://cdn.simpleicons.org/adobecreativecloud/FFFFFF',features:['20+ desktop & web apps','Firefly generative credits','100GB Adobe Cloud storage','Adobe Fonts access'],intent:['image','images','design','video','creator']},
  {id:'lovable',name:'Lovable Pro',category:'Development',description:'Build, design and ship full-stack web applications and MVPs with natural language.',price:1600,oldPrice:2200,duration:'1 Month',access:'Private',delivery:'30–60 min',warranty:'7 Days',rating:4.6,badge:'For Builders',bestFor:['Apps','Web','MVPs'],logo:'https://cdn.simpleicons.org/lovable/FFFFFF',features:['AI full-stack code generator','Direct GitHub integration','Custom domains & deploy','Fast iterative edits'],intent:['code','coding','business','automation']},
  {id:'gamma',name:'Gamma Pro',category:'Productivity',description:'Turn raw ideas, briefs and outlines into interactive presentations, decks and docs.',price:23000,oldPrice:28000,duration:'1 Year',access:'Private',delivery:'1–2 hours',warranty:'30 Days',rating:4.6,badge:'Annual',bestFor:['Slides','Pitching','Docs'],logo:'https://cdn.simpleicons.org/gamma/FFFFFF',features:['Unlimited AI generation','Custom fonts & themes','Analytics & tracking','Export to PDF/PowerPoint'],intent:['presentation','content','business','study']},
  {id:'replit',name:'Replit Core',category:'Development',description:'Code, collaborate, host and scale web applications with autonomous AI agents.',price:3200,oldPrice:4200,duration:'$40 Credits',access:'Private',delivery:'30–60 min',warranty:'7 Days',rating:4.7,badge:'Developer Pick',bestFor:['Coding','Apps','Deploy'],logo:'https://cdn.simpleicons.org/replit/FFFFFF',features:['Autonomous AI code agent','Instant cloud environments','Serverless hosting','$40 included usage credits'],intent:['code','coding','automation']},
  {id:'n8n',name:'n8n Starter',category:'Development',description:'Self-hosted or cloud visual workflow automation for AI agents, APIs and business logic.',price:7000,oldPrice:9000,duration:'1 Year',access:'Private',delivery:'1–2 hours',warranty:'30 Days',rating:4.7,badge:'Automation',bestFor:['Workflow','Agents','Teams'],logo:'https://cdn.simpleicons.org/n8n/FFFFFF',features:['Visual drag-and-drop builder','400+ native app integrations','LangChain AI nodes','Custom JavaScript execution'],intent:['code','coding','automation','business']},
  {id:'notion',name:'Notion Business',category:'Productivity',description:'All-in-one connected workspace for team knowledge, project boards, and AI summaries.',price:2200,oldPrice:3000,duration:'3 Months',access:'Invitation',delivery:'30–60 min',warranty:'30 Days',rating:4.8,badge:'Team Pick',bestFor:['Docs','Projects','Teams'],logo:'https://cdn.simpleicons.org/notion/FFFFFF',features:['Unlimited team blocks','Integrated Notion AI assistant','Advanced team permissions','Custom database views'],intent:['writing','content','business','study']},
  {id:'nordvpn',name:'NordVPN',category:'VPN & Security',description:'Military-grade encrypted browsing, high-speed servers, and threat protection.',price:1800,oldPrice:2400,duration:'3 Months',access:'Private',delivery:'15–30 min',warranty:'7 Days',rating:4.7,badge:'Secure',bestFor:['Privacy','Travel','Streaming'],logo:'https://cdn.simpleicons.org/nordvpn/FFFFFF',features:['Ultra-fast 10Gbps servers','Threat protection & ad blocker','6 simultaneous connections','Strict zero-logs policy'],intent:['vpn','security','privacy']},
  {id:'surfshark',name:'Surfshark VPN',category:'VPN & Security',description:'Reliable everyday privacy, geo-unblocking, and unlimited device connections.',price:800,oldPrice:1200,duration:'2 Months',access:'Shared',delivery:'15–30 min',warranty:'7 Days',rating:4.6,badge:'Best Value',bestFor:['Privacy','Devices','Travel'],logo:'https://cdn.simpleicons.org/surfshark/FFFFFF',features:['Unlimited device support','CleanWeb ad & tracker blocker','Global server locations','Bypasser split tunneling'],intent:['vpn','security','privacy']},
  {id:'youtube',name:'YouTube Premium',category:'Entertainment',description:'Ad-free videos, background play on mobile, offline downloads, and YouTube Music.',price:1200,oldPrice:1700,duration:'3 Months',access:'Invitation',delivery:'15–30 min',warranty:'30 Days',rating:4.8,badge:'Popular',bestFor:['Music','Video','Mobile'],logo:'https://cdn.simpleicons.org/youtube/FFFFFF',features:['Zero video ads','Background & picture-in-picture','Offline smart downloads','Full YouTube Music access'],intent:['entertainment','video','music']},
  {id:'netflix',name:'Netflix Premium 4K',category:'Entertainment',description:'Stream global movies and series in crisp 4K Ultra HD with spatial audio.',price:400,oldPrice:650,duration:'1 Month',access:'Shared',delivery:'15–30 min',warranty:'7 Days',rating:4.5,badge:'Quick Delivery',bestFor:['Movies','Series','4K'],logo:'https://cdn.simpleicons.org/netflix/FFFFFF',features:['4K Ultra HD & HDR resolution','Spatial audio support','Smart TV & laptop compatibility','Dedicated profile access'],intent:['entertainment','video','movies']},
  {id:'linkedin',name:'LinkedIn Premium',category:'Business',description:'Career growth insights, competitive applicant analysis, and LinkedIn Learning.',price:1500,oldPrice:2400,duration:'2 Months',access:'Invitation',delivery:'30–60 min',warranty:'7 Days',rating:4.6,badge:'Career',bestFor:['Jobs','Learning','Sales'],logo:'https://cdn.simpleicons.org/linkedin/FFFFFF',features:['5 InMail credits per month','See who viewed your profile','Competitive job applicant insights','16,000+ LinkedIn Learning courses'],intent:['business','jobs','study']},
  {id:'windows',name:'Windows 11 Pro Key',category:'Software',description:'Official retail digital license key for permanent Windows 11 Pro activation.',price:1900,oldPrice:2800,duration:'Lifetime',access:'License Key',delivery:'15–30 min',warranty:'7 Days',rating:4.7,badge:'License Key',bestFor:['PC','Work','Security'],logo:'https://cdn.simpleicons.org/windows11/FFFFFF',features:['100% genuine retail key','BitLocker drive encryption','Remote Desktop Host','Direct Microsoft online activation'],intent:['software','windows','business']}
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

let state = {
  category: 'All',
  query: '',
  limit: 20,
  cart: JSON.parse(localStorage.getItem('atg-cart') || '[]'),
  compare: [],
  finder: { intent: '', budget: Infinity }
};

const $ = s => document.querySelector(s);
const $$ = s => [...document.querySelectorAll(s)];
const money = n => 'Rs. ' + n.toLocaleString('en-PK');
const discount = p => Math.round((1 - p.price / p.oldPrice) * 100);
const svg = id => `<svg><use href="#${id}"></use></svg>`;

/* --------------------------------------------------------------------------
   RENDERING FUNCTIONS
   -------------------------------------------------------------------------- */
function renderCategories() {
  const container = $('#categoryGrid');
  if (!container) return;
  container.innerHTML = categoryData.map((c, index) => `
    <button class="category-card" data-category="${c[0]}" aria-label="Explore ${c[0]}">
      <span class="category-visual" style="--category-x:${(index % 5) * 25}%;--category-y:${index < 5 ? 18 : 82}%">
        <span class="category-count">${c[2]}</span>
      </span>
      <span class="category-content">
        <span>
          <small>Explore Collection</small>
          <b>${c[0]}</b>
        </span>
        <i aria-hidden="true">${svg('i-arrow')}</i>
      </span>
    </button>
  `).join('');
}

function renderFilters() {
  const cats = ['All','AI Assistants','AI Video','Design','Development','Productivity','VPN & Security','Entertainment'];
  const row = $('#filterRow');
  if (!row) return;
  row.innerHTML = cats.map(c => `
    <button class="filter-chip ${state.category === c ? 'active' : ''}" data-filter="${c}">${c}</button>
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
  const inCart = state.cart.includes(p.id);
  const comparing = state.compare.includes(p.id);
  return `
  <article class="product-card" data-id="${p.id}">
    <div class="product-media">
      <span class="product-badge">${p.badge}</span>
      <button class="compare-toggle ${comparing ? 'active' : ''}" data-compare="${p.id}" aria-label="Compare ${p.name}">
        ${svg(comparing ? 'i-check' : 'i-plus')}
      </button>
      <img class="brand-logo" src="${p.logo}" alt="Official ${p.name} logo" loading="lazy">
    </div>
    <div class="product-body">
      <div class="product-meta">
        <span>${p.category}</span>
        <span class="rating">★ ${p.rating}</span>
      </div>
      <h3>${p.name}</h3>
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
          <small>${money(p.oldPrice)}</small>
          <strong>${money(p.price)}</strong>
        </div>
        <span class="saving">Save ${discount(p)}%</span>
      </div>
      <div class="card-actions">
        <button class="buy-now-card" data-order="${p.id}">${svg('i-whatsapp')} Buy now</button>
        <button class="detail-button" data-detail="${p.id}">View details</button>
        <button class="add-button ${inCart ? 'added' : ''}" data-add="${p.id}" aria-label="Add ${p.name} to cart">
          ${svg(inCart ? 'i-check' : 'i-plus')}
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
  
  const showAllBtn = $('#showAll');
  if (showAllBtn) showAllBtn.style.display = 'none';
  
  const aq = $('#activeQuery');
  if (aq) {
    aq.classList.toggle('show', !!state.query);
    aq.innerHTML = state.query ? `Showing verified results for “${state.query}” · <button id="clearQuery">Clear search</button>` : '';
  }
  
  renderFilters();
}

/* --------------------------------------------------------------------------
   CART & COMPARE LOGIC
   -------------------------------------------------------------------------- */
function updateCart() {
  localStorage.setItem('atg-cart', JSON.stringify(state.cart));
  const cCount = $('#cartCount');
  const mCount = $('#mobileCartCount');
  if (cCount) cCount.textContent = state.cart.length;
  if (mCount) mCount.textContent = state.cart.length;

  const selected = state.cart.map(id => products.find(p => p.id === id)).filter(Boolean);
  const cartItems = $('#cartItems');
  if (cartItems) {
    cartItems.innerHTML = selected.length ? selected.map(p => `
      <div class="cart-item">
        <img src="${p.logo}" alt="${p.name}">
        <span>
          <b>${p.name}</b>
          <small>${p.duration} · ${p.access} Plan</small>
          <strong>${money(p.price)}</strong>
        </span>
        <button class="remove-cart" data-remove="${p.id}" aria-label="Remove ${p.name}">×</button>
      </div>
    `).join('') : `
      <div class="cart-empty">
        <img src="assets/logo-transparent.png" class="empty-state-logo" alt="Aura Diamond">
        <h3>Your cart is empty</h3>
        <p>Explore the 3D marketplace and add tools here.</p>
      </div>
    `;
  }

  const totalEl = $('#cartTotal');
  if (totalEl) totalEl.textContent = money(selected.reduce((s, p) => s + p.price, 0));
  
  const footer = $('#cartFooter');
  if (footer) footer.style.display = selected.length ? 'block' : 'none';
}

function toggleCart(id) {
  state.cart = state.cart.includes(id) ? state.cart.filter(x => x !== id) : [...state.cart, id];
  updateCart();
  renderProducts();
  toast(state.cart.includes(id) ? 'Added to your cart' : 'Removed from cart');
}

function updateCompare() {
  const compCount = $('#compareCount');
  const compBar = $('#compareBar');
  const compMini = $('#compareMini');
  if (compCount) compCount.textContent = state.compare.length;
  if (compBar) compBar.classList.toggle('show', state.compare.length > 0);
  if (compMini) {
    compMini.innerHTML = state.compare.map(id => {
      const p = products.find(x => x.id === id);
      return `<img src="${p.logo}" alt="${p.name}">`;
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

function openLayer(el) {
  if (!el) return;
  const backdrop = $('#backdrop');
  if (backdrop) backdrop.classList.add('show');
  el.classList.add('open');
  el.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
}

function closeLayers() {
  $$('.drawer, .modal').forEach(x => {
    x.classList.remove('open');
    x.setAttribute('aria-hidden', 'true');
  });
  const backdrop = $('#backdrop');
  if (backdrop) backdrop.classList.remove('show');
  document.body.style.overflow = '';
}

function openProduct(id) {
  const p = products.find(x => x.id === id);
  if (!p) return;
  const detail = $('#productDetail');
  if (detail) {
    detail.innerHTML = `
      <div class="product-detail">
        <div class="detail-media">
          <img class="brand-logo" src="${p.logo}" alt="Official ${p.name} logo">
        </div>
        <div class="detail-copy">
          <span class="detail-category">${p.category} · ${p.badge}</span>
          <h2>${p.name}</h2>
          <div class="detail-rating">★★★★★ &nbsp; ${p.rating}/5 Verified Rating</div>
          <p>${p.description} Guaranteed authentic subscription activated quickly via WhatsApp.</p>
          <div class="detail-price">${money(p.price)} <del>${money(p.oldPrice)}</del></div>
          <div class="detail-grid">
            <div class="detail-spec"><small>Plan duration</small><b>${p.duration}</b></div>
            <div class="detail-spec"><small>Access type</small><b>${p.access} Plan</b></div>
            <div class="detail-spec"><small>Delivery speed</small><b>${p.delivery}</b></div>
            <div class="detail-spec"><small>Warranty</small><b>${p.warranty}</b></div>
          </div>
          <div class="feature-list">
            ${p.features.map(f => `<span>${svg('i-check')}${f}</span>`).join('')}
          </div>
          <div class="detail-actions">
            <button class="add-detail" data-add="${p.id}">${state.cart.includes(p.id) ? 'Added to cart' : 'Add to cart'}</button>
            <button class="order-now" data-order="${p.id}">${svg('i-whatsapp')} Order on WhatsApp</button>
          </div>
        </div>
      </div>
    `;
  }
  openLayer($('#productModal'));
}

function waLink(message) {
  const saved = localStorage.getItem('atg-whatsapp');
  const number = (!saved || saved === '923001234567') ? DEFAULT_WA_NUMBER : saved;
  return `https://wa.me/${number}?text=${encodeURIComponent(message)}`;
}

function orderProduct(id) {
  const p = products.find(x => x.id === id);
  if (!p) return;
  window.open(waLink(`Hello AI Tools Aura 👋\n\nI would like to order:\n\n💎 Product: ${p.name}\n⏱️ Duration: ${p.duration}\n🔑 Access: ${p.access}\n💰 Price: ${money(p.price)}\n\nPlease confirm payment details and delivery time.`), '_blank');
}

function checkout() {
  const selected = state.cart.map(id => products.find(p => p.id === id)).filter(Boolean);
  if (!selected.length) return;
  const total = selected.reduce((s, p) => s + p.price, 0);
  const lines = selected.map((p, i) => `${i + 1}. ${p.name} (${p.duration}, ${p.access}) — ${money(p.price)}`).join('\n');
  window.open(waLink(`Hello AI Tools Aura 👋\n\nI want to place an order for my cart:\n\n${lines}\n\n💎 Total: ${money(total)}\n\nPlease confirm availability and payment methods (JazzCash/EasyPaisa/Bank).`), '_blank');
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
    <div class="suggestion" data-suggest="${p.id}">
      <img src="${p.logo}" alt="${p.name}">
      <span>${p.name}</span>
      <small>${money(p.price)}</small>
    </div>
  `).join('') : `
    <div class="suggestion"><span>No matching tools found</span></div>
  `;
  box.classList.add('show');
}

function applySearch(q) {
  state.query = q;
  state.limit = 20;
  const sInput = $('#heroSearch');
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
      <img src="assets/logo-transparent.png" class="empty-state-logo" alt="">
      <h3>Select one more tool</h3>
      <p>Select 2 or 3 products to compare features and prices side by side.</p>
    </div>
  ` : `
    <table class="compare-table">
      <thead>
        <tr>
          <th></th>
          ${ps.map(p => `<th><img src="${p.logo}" alt="">${p.name}</th>`).join('')}
        </tr>
      </thead>
      <tbody>
        ${[
          ['Price', p => money(p.price)],
          ['Duration', p => p.duration],
          ['Access Type', p => p.access],
          ['Delivery', p => p.delivery],
          ['Warranty', p => p.warranty],
          ['User Rating', p => '★ ' + p.rating + ' / 5'],
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
        <div class="eyebrow dark"><span></span> Step 1 of 2</div>
        <h2>What outcome are you pursuing?</h2>
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
        <div class="eyebrow dark"><span></span> Step 2 of 2</div>
        <h2>What is your budget target?</h2>
        <p>We’ll prioritize tools with the highest verified ROI in your range.</p>
        <div class="finder-choices">
          <button class="finder-choice" data-budget="1000">Under Rs. 1,000<small>Budget friendly</small></button>
          <button class="finder-choice" data-budget="2500">Rs. 1,000 – 2,500<small>Most popular tier</small></button>
          <button class="finder-choice" data-budget="5000">Rs. 2,500 – 5,000<small>Power creator</small></button>
          <button class="finder-choice" data-budget="999999">Rs. 5,000+<small>Annual & teams</small></button>
        </div>
      </div>
    `;
  }
  if (step === 3) {
    let matches = products.filter(p => p.intent.includes(state.finder.intent) && p.price <= state.finder.budget).sort((a, b) => b.rating - a.rating).slice(0, 3);
    if (!matches.length) {
      matches = products.filter(p => p.intent.includes(state.finder.intent)).sort((a, b) => a.price - b.price).slice(0, 3);
    }
    root.innerHTML = `
      <div class="finder-step">
        <div class="progress"><span style="width:100%"></span></div>
        <div class="eyebrow dark"><span></span> Recommendation Ready</div>
        <h2>Your Best 3D Tool Matches</h2>
        <p>Matched for your objective, budget tier, and user satisfaction rating.</p>
        <div class="finder-results">
          ${matches.map((p, i) => `
            <button class="finder-result" data-detail="${p.id}">
              <img src="${p.logo}" alt="${p.name}">
              <div>
                <small>${i === 0 ? '★ TOP VERIFIED MATCH' : 'EXCELLENT COMPANION'}</small>
                <b>${p.name}</b>
                <span>${p.bestFor.join(' · ')} · ${p.duration}</span>
              </div>
              <strong>${money(p.price)}</strong>
            </button>
          `).join('')}
        </div>
      </div>
    `;
  }
}

function openFinder() {
  state.finder = { intent: '', budget: Infinity };
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

  function onMouseMove(e) {
    const rect = stage.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width - 0.5;
    const y = (e.clientY - rect.top) / rect.height - 0.5;
    targetX = x * 24; // tilt degrees
    targetY = -y * 24;
  }

  function onMouseLeave() {
    targetX = 0;
    targetY = 0;
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

    requestAnimationFrame(renderHero3d);
  }

  stage.addEventListener('mousemove', onMouseMove);
  stage.addEventListener('mouseleave', onMouseLeave);
  renderHero3d();
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
    toggleCart(add.dataset.add);
    if ($('#productModal').classList.contains('open')) openProduct(add.dataset.add);
    return;
  }
  const remove = e.target.closest('[data-remove]');
  if (remove) {
    toggleCart(remove.dataset.remove);
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
    state.limit = 20;
    renderProducts();
    $('#products').scrollIntoView({ behavior: 'smooth' });
    return;
  }
  const catLink = e.target.closest('[data-category-link]');
  if (catLink) {
    state.category = catLink.dataset.categoryLink;
    state.query = '';
    renderProducts();
    return;
  }
  const query = e.target.closest('[data-query]');
  if (query) {
    applySearch(query.dataset.query);
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
  const budget = e.target.closest('[data-budget]');
  if (budget) {
    state.finder.budget = Number(budget.dataset.budget);
    finderStep(3);
    return;
  }
  const order = e.target.closest('[data-order]');
  if (order) {
    orderProduct(order.dataset.order);
    return;
  }
  const wa = e.target.closest('[data-whatsapp]');
  if (wa) {
    e.preventDefault();
    window.open(waLink('Hello AI Tools Aura, I need assistance choosing a premium AI tool.'), '_blank');
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
    if ($('#heroSearch')) $('#heroSearch').value = '';
    renderProducts();
  }
});

/* Search listeners */
const heroSearch = $('#heroSearch');
if (heroSearch) {
  heroSearch.addEventListener('input', e => showSuggestions(e.target.value));
  heroSearch.addEventListener('keydown', e => {
    if (e.key === 'Enter') applySearch(e.target.value);
    if (e.key === 'Escape') $('#suggestions').classList.remove('show');
  });
}

const openSearch = $('#openSearch');
if (openSearch && heroSearch) {
  openSearch.onclick = () => {
    heroSearch.focus();
    heroSearch.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };
}

document.addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault();
    if (heroSearch) {
      heroSearch.focus();
      heroSearch.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }
  if (e.key === 'Escape') closeLayers();
});

const openCart = $('#openCart');
const mobileCart = $('#mobileCart');
if (openCart) openCart.onclick = () => openLayer($('#cartDrawer'));
if (mobileCart) mobileCart.onclick = () => openLayer($('#cartDrawer'));

const checkoutWA = $('#checkoutWhatsApp');
if (checkoutWA) checkoutWA.onclick = checkout;

const openComp = $('#openCompare');
if (openComp) openComp.onclick = renderCompare;

const sortSel = $('#sortSelect');
if (sortSel) sortSel.onchange = renderProducts;

const showAllBtn = $('#showAll');
if (showAllBtn) {
  showAllBtn.onclick = () => {
    state.limit = 20;
    renderProducts();
  };
}

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
    renderProducts();
  };
}

const menuBtn = $('#menuButton');
if (menuBtn) {
  menuBtn.onclick = () => {
    const mobNav = $('#mobileNav');
    if (mobNav) mobNav.classList.toggle('show');
  };
}

const addBundleBtn = $('#addBundle');
if (addBundleBtn) {
  addBundleBtn.onclick = () => {
    ['chatgpt', 'canva', 'capcut', 'elevenlabs'].forEach(id => {
      if (!state.cart.includes(id)) state.cart.push(id);
    });
    updateCart();
    renderProducts();
    toast('Creator stack added to your cart');
  };
}

/* --------------------------------------------------------------------------
   INITIALIZATION
   -------------------------------------------------------------------------- */
renderCategories();
renderProducts();
updateCart();
updateCompare();
init3dHero();
init3dCards();
