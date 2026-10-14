const DEFAULT_ORIGIN = 'https://aitoolgems.tech';
const DEFAULT_CATALOG_URL = `${DEFAULT_ORIGIN}/app.js`;
const DEFAULT_WHATSAPP = 'https://wa.me/923236715731';
const rateState = new Map();

const KNOWLEDGE = [
  { title: 'Store policies', url: '/policies.html', text: 'Access types include Private, Shared, Invitation, and License Key. Delivery starts after payment confirmation. Availability, access conditions, final amount, delivery estimate, and warranty must be reconfirmed on WhatsApp.' },
  { title: 'Terms of service', url: '/terms.html', text: 'An order is confirmed only after WhatsApp confirmation. Accepted payment methods listed by the store are EasyPaisa, JazzCash, SadaPay, NayaPay, and bank transfer. Refunds and replacement coverage depend on the confirmed product terms.' },
  { title: 'Privacy policy', url: '/privacy.html', text: 'Do not send passwords, one-time codes, full card details, or unrelated identity documents. The public website uses browser storage for cart preferences. Sensitive order support remains with the human WhatsApp channel.' },
  { title: 'Contact and support', url: '/contact.html', text: 'Human support is available through WhatsApp at +92 323 6715731. Customers should include the product name and order number for order-related help, but never send passwords or OTPs.' },
  { title: 'How listings are reviewed', url: '/how-we-review.html', text: 'Product identity and public features are checked against primary vendor sources. Marketplace price, access terms, delivery estimate, availability, and warranty are separate marketplace information and should be reconfirmed before payment.' },
  { title: 'Price guide', url: '/guides/ai-tools-price-pakistan/', text: 'The site publishes Pakistan-focused comparisons of duration, access type, and PKR pricing. Prices can change, so the current listing and WhatsApp confirmation control the final offer.' },
  { title: 'Guides and blog', url: '/guides/', text: 'The site includes guides for students, businesses, creators, developers, productivity, Canva, CapCut, Gemini, Claude, Cursor, and AI tool comparisons.' }
];

function json(data, status = 200, origin = DEFAULT_ORIGIN) {
  return new Response(status === 204 ? null : JSON.stringify(data), {
    status,
    headers: {
      'content-type': 'application/json; charset=utf-8',
      'cache-control': 'no-store',
      'access-control-allow-origin': origin,
      'access-control-allow-headers': 'content-type',
      'access-control-allow-methods': 'POST, OPTIONS',
      'vary': 'Origin'
    }
  });
}

function allowedOrigin(request, env) {
  const origin = request.headers.get('Origin') || '';
  const allowed = new Set([DEFAULT_ORIGIN, env.PUBLIC_ORIGIN, 'http://localhost:8787', 'http://127.0.0.1:8787']);
  return allowed.has(origin) ? origin : DEFAULT_ORIGIN;
}

function containsSensitiveInput(text) {
  return /(password|passcode|one[- ]?time|otp|cvv|cvc|card number|api[_ -]?key|secret|token)\s*[:=]?/i.test(text);
}

function normalize(text) {
  return String(text || '').toLowerCase().replace(/[^\p{L}\p{N}\s.-]/gu, ' ');
}

function parseCatalog(source) {
  const products = [];
  const pattern = /\{id:'([^']+)',name:'([^']+)',category:'([^']+)',description:'([^']*)',price:(\d+)[^\n]*?duration:'([^']+)',access:'([^']+)',delivery:'([^']+)',warranty:'([^']+)'/g;
  let match;
  while ((match = pattern.exec(source)) !== null) {
    const [, id, name, category, description, price, duration, access, delivery, warranty] = match;
    products.push({ id, name, category, description, price: Number(price), duration, access, delivery, warranty, url: `/tools/${id}/`, source: `${DEFAULT_ORIGIN}/` });
  }
  return products;
}

async function getCatalog(env) {
  const url = env.CATALOG_URL || DEFAULT_CATALOG_URL;
  const response = await fetch(url, { cf: { cacheTtl: 300, cacheEverything: true } });
  if (!response.ok) throw new Error(`catalog fetch failed: ${response.status}`);
  const products = parseCatalog(await response.text());
  if (!products.length) throw new Error('catalog parse returned no products');
  return products;
}

function sourceLink(path, origin = DEFAULT_ORIGIN) {
  return new URL(path, origin).toString();
}

function findMatches(question, products) {
  const q = normalize(question);
  const rawQuestion = String(question || '');
  const budget = rawQuestion.match(/(?:under|below|budget|within|less than|rs|pkr)\s*(?:rs\.?|pkr)?\s*([\d][\d,\s]*)/i);
  const max = budget ? Number(budget[1].replace(/[\s,]/g, '')) : null;
  const stopWords = new Set(['what', 'can', 'you', 'help', 'me', 'with', 'the', 'and', 'for', 'how', 'please', 'batao', 'mujhe', 'hai', 'mera', 'best', 'tool', 'tools']);
  const words = q.split(/\s+/).filter(word => word.length > 2 && !stopWords.has(word));
  const matches = products
    .map(product => ({ product, score: words.reduce((score, word) => score + (normalize(`${product.name} ${product.category} ${product.description}`).includes(word) ? 1 : 0), 0) }))
    .filter(item => item.score > 0 && (max === null || item.product.price <= max))
    .sort((a, b) => b.score - a.score || a.product.price - b.product.price)
    .slice(0, 5)
    .map(item => item.product);
  if (!matches.length && max !== null) return products.filter(product => product.price <= max).sort((a, b) => a.price - b.price).slice(0, 5);
  return matches;
}

function localizedPolicyText(item, language) {
  if (language === 'roman-ur') {
    if (item.title === 'Store policies') return 'Access types Private, Shared, Invitation aur License Key hain. Delivery payment confirm hone ke baad start hoti hai. Final price, availability, access conditions, delivery estimate aur warranty WhatsApp par confirm karein.';
    if (item.title === 'Privacy policy') return 'Password, OTP, card details, API key ya unrelated identity documents share na karein. Sensitive order support human WhatsApp channel par hota hai.';
    if (item.title === 'Contact and support') return 'Human support WhatsApp par +92 323 6715731 available hai. Order help ke liye product name aur order number dein, lekin password ya OTP kabhi na bhejein.';
  }
  if (language === 'ur') {
    if (item.title === 'Store policies') return 'رسائی کی اقسام Private، Shared، Invitation اور License Key ہیں۔ ادائیگی کی تصدیق کے بعد ڈیلیوری شروع ہوتی ہے۔ حتمی قیمت، دستیابی، رسائی، ڈیلیوری اور وارنٹی WhatsApp پر تصدیق کریں۔';
    if (item.title === 'Privacy policy') return 'پاس ورڈ، OTP، کارڈ کی تفصیل، API key یا غیر متعلقہ شناختی دستاویزات شیئر نہ کریں۔ حساس آرڈر مدد انسانی WhatsApp چینل پر دستیاب ہے۔';
    if (item.title === 'Contact and support') return 'انسانی مدد WhatsApp پر +92 323 6715731 دستیاب ہے۔ آرڈر مدد کے لیے پروڈکٹ نام اور آرڈر نمبر دیں، لیکن پاس ورڈ یا OTP کبھی نہ بھیجیں۔';
  }
  return item.text;
}

function deterministicAnswer(question, products, origin, language) {
  const q = normalize(question);
  const generalHelp = /what can you help|how can you help|help me|aap kya|kis tarah madad/.test(q);
  const policyIntent = /faq|frequently|delivery|payment|refund|warranty|access|privacy|order|support|policy|status|وارنٹی|ادائیگی|ڈیلیوری|رازداری|آرڈر/.test(q);
  const comparisonIntent = /compare|comparison|versus|\bvs\b|muqabla|موازنہ/.test(q);
  if (generalHelp) return { answer: language === 'roman-ur' ? 'Main current PKR listings compare, budget ke mutabiq tools recommend, product pages aur guides se maloomat, delivery/payment/warranty policies, aur human WhatsApp support provide kar sakta hoon. Price, availability ya order status guess nahi karunga.' : language === 'ur' ? 'میں موجودہ PKR فہرست کا موازنہ، بجٹ کے مطابق سفارش، پروڈکٹ پیجز اور گائیڈز کی معلومات، ڈیلیوری/ادائیگی/وارنٹی پالیسی اور انسانی WhatsApp مدد فراہم کر سکتا ہوں۔ قیمت، دستیابی یا آرڈر اسٹیٹس کا اندازہ نہیں لگاؤں گا۔' : 'I can compare current PKR listings, recommend tools by budget, explain product pages and guides, answer delivery/payment/warranty questions, and connect you to human WhatsApp support. I will not guess prices, availability, or order status.', sources: [{ title: 'Browse the catalog', url: sourceLink('/', origin) }, { title: 'WhatsApp support', url: DEFAULT_WHATSAPP }] };
  if (policyIntent && !comparisonIntent && !/(?:price|cost|قیمت|دام)/.test(q)) {
    const item = q.includes('refund') || q.includes('return') ? KNOWLEDGE.find(entry => entry.title === 'Terms of service') : q.includes('privacy') || q.includes('رازداری') ? KNOWLEDGE.find(entry => entry.title === 'Privacy policy') : q.includes('delivery') || q.includes('ڈیلیوری') ? KNOWLEDGE.find(entry => entry.title === 'Store policies') : KNOWLEDGE.find(entry => normalize(`${entry.title} ${entry.text}`).split(' ').some(word => word.length > 3 && q.includes(word))) || KNOWLEDGE[0];
    const confirmation = language === 'roman-ur' ? 'Payment se pehle exact product terms human support se confirm karein.' : language === 'ur' ? 'ادائیگی سے پہلے انسانی مدد سے پروڈکٹ کی درست شرائط کی تصدیق کریں۔' : 'Please confirm the exact product terms with human support before payment.';
    return { answer: `${localizedPolicyText(item, language)}\n\n${confirmation}`, sources: [{ title: item.title, url: sourceLink(item.url, origin) }, { title: 'WhatsApp support', url: DEFAULT_WHATSAPP }] };
  }
  const matches = findMatches(question, products);
  const links = [];
  if (/order|buy|purchase|khareed|mangwana|whatsapp|support|help/.test(q)) links.push({ title: 'WhatsApp human support', url: DEFAULT_WHATSAPP });
  if (/refund|warranty|replace|return|delivery|payment|pay|policy|access/.test(q)) {
    const policy = KNOWLEDGE.find(item => item.title === 'Store policies');
    links.push({ title: policy.title, url: sourceLink(policy.url, origin) });
  }
  if (matches.length) {
    const lines = matches.map(product => `• ${product.name} — Rs. ${product.price.toLocaleString('en-PK')} | ${product.duration} | ${product.access} | delivery ${product.delivery} | warranty ${product.warranty}\n  ${sourceLink(product.url, origin)}`);
    const intro = language === 'roman-ur' ? 'Aap ke sawal ke mutabiq current catalog matches (payment se pehle availability confirm karein):' : language === 'ur' ? 'آپ کے سوال کے مطابق موجودہ کیٹلاگ نتائج (ادائیگی سے پہلے دستیابی کی تصدیق کریں):' : 'Current catalog matches (please reconfirm availability before payment):';
    const note = language === 'roman-ur' ? 'Prices aur access terms badal sakte hain; final offer WhatsApp par confirm hota hai.' : language === 'ur' ? 'قیمتیں اور رسائی کی شرائط بدل سکتی ہیں؛ حتمی پیشکش WhatsApp پر تصدیق ہوتی ہے۔' : 'Prices and access terms can change; WhatsApp confirmation controls the final offer.';
    const heading = comparisonIntent ? (language === 'roman-ur' ? 'Aap ke tools ka comparison:' : language === 'ur' ? 'آپ کے ٹولز کا موازنہ:' : 'Your tool comparison:') : intro;
    return { answer: `${heading}\n${lines.join('\n')}\n\n${note}`, sources: matches.map(product => ({ title: product.name, url: sourceLink(product.url, origin) })).concat(links) };
  }
  if (policyIntent) {
    const item = q.includes('refund') || q.includes('return') ? KNOWLEDGE.find(entry => entry.title === 'Terms of service') : q.includes('privacy') || q.includes('رازداری') ? KNOWLEDGE.find(entry => entry.title === 'Privacy policy') : KNOWLEDGE.find(entry => normalize(`${entry.title} ${entry.text}`).split(' ').some(word => word.length > 3 && q.includes(word))) || KNOWLEDGE[0];
    const confirmation = language === 'roman-ur' ? 'Payment se pehle exact product terms human support se confirm karein.' : language === 'ur' ? 'ادائیگی سے پہلے انسانی مدد سے پروڈکٹ کی درست شرائط کی تصدیق کریں۔' : 'Please confirm the exact product terms with human support before payment.';
    return { answer: `${localizedPolicyText(item, language)}\n\n${confirmation}`, sources: [{ title: item.title, url: sourceLink(item.url, origin) }, { title: 'WhatsApp support', url: DEFAULT_WHATSAPP }] };
  }
  const fallback = language === 'roman-ur' ? 'Main current PKR listings compare kar sakta hoon, budget ke andar tool dhoond sakta hoon, delivery/payment/warranty policies samjha sakta hoon, ya human WhatsApp support se connect kar sakta hoon. Tool, use case ya budget batayein. Main price ya order status guess nahi karunga.' : language === 'ur' ? 'میں موجودہ PKR فہرست کا موازنہ، بجٹ کے مطابق ٹول، ڈیلیوری/ادائیگی/وارنٹی پالیسی اور انسانی WhatsApp مدد فراہم کر سکتا ہوں۔ ٹول، استعمال یا بجٹ بتائیں۔ میں قیمت یا آرڈر اسٹیٹس کا اندازہ نہیں لگاؤں گا۔' : 'I can help compare current PKR listings, find a tool within your budget, explain delivery/payment/warranty policies, or connect you to human WhatsApp support. Please mention a tool, use case, or budget. I will not guess prices or order status.';
  return { answer: fallback, sources: [{ title: 'Browse the catalog', url: sourceLink('/', origin) }, { title: 'WhatsApp support', url: DEFAULT_WHATSAPP }] };
}

function languageInstruction(language) {
  if (language === 'ur') return 'Reply in Urdu script when practical.';
  if (language === 'roman-ur') return 'Reply in simple Roman Urdu, keeping product names and prices unchanged.';
  return 'Reply in clear English.';
}

async function modelAnswer(question, language, context, env) {
  if (!env.GEMINI_API_KEY) return null;
  const model = env.GEMINI_MODEL || 'gemini-2.0-flash';
  const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(model)}:generateContent?key=${encodeURIComponent(env.GEMINI_API_KEY)}`;
  const prompt = `You are the AI Tool Gems Pakistan shopping assistant. ${languageInstruction(language)} Answer only from the supplied context. Never invent prices, availability, warranties, delivery times, payment acceptance, product features, or order status. If the context is insufficient, say so and link human WhatsApp support. Do not request or process passwords, OTPs, card details, API keys, or secrets. Keep the answer concise and include relevant source URLs.\n\nCONTEXT:\n${context}\n\nQUESTION:\n${question}`;
  const response = await fetch(endpoint, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }], generationConfig: { temperature: 0.1, maxOutputTokens: 500 } }) });
  if (!response.ok) return null;
  const data = await response.json();
  return data?.candidates?.[0]?.content?.parts?.map(part => part.text || '').join('').trim() || null;
}

function checkRateLimit(request) {
  const ip = request.headers.get('CF-Connecting-IP') || 'anonymous';
  const now = Date.now();
  const current = rateState.get(ip) || { start: now, count: 0 };
  if (now - current.start > 60_000) { current.start = now; current.count = 0; }
  current.count += 1;
  rateState.set(ip, current);
  return current.count <= 12;
}

export default {
  async fetch(request, env) {
    const origin = allowedOrigin(request, env);
    if (request.method === 'OPTIONS') return json({}, 204, origin);
    const url = new URL(request.url);
    if (url.pathname !== '/api/chat') return new Response('Not found', { status: 404 });
    if (request.method !== 'POST') return json({ error: 'Method not allowed' }, 405, origin);
    if (!checkRateLimit(request)) return json({ error: 'Too many requests. Please wait one minute.' }, 429, origin);
    let body;
    try { body = await request.json(); } catch { return json({ error: 'Invalid JSON' }, 400, origin); }
    const question = String(body?.message || '').trim();
    const language = ['en', 'roman-ur', 'ur'].includes(body?.language) ? body.language : 'en';
    if (!question || question.length > 800) return json({ error: 'Please send a question up to 800 characters.' }, 400, origin);
    if (containsSensitiveInput(question)) return json({ answer: 'Please do not send passwords, OTPs, card details, API keys, or other secrets. For secure order help, contact human support on WhatsApp.', sources: [{ title: 'WhatsApp support', url: DEFAULT_WHATSAPP }] }, 200, origin);
    try {
      const products = await getCatalog(env);
      const deterministic = deterministicAnswer(question, products, env.PUBLIC_ORIGIN || DEFAULT_ORIGIN, language);
      const matched = findMatches(question, products);
      const context = [...matched.map(product => `${product.name}: Rs. ${product.price}; ${product.duration}; ${product.access}; delivery ${product.delivery}; warranty ${product.warranty}; page ${sourceLink(product.url, env.PUBLIC_ORIGIN || DEFAULT_ORIGIN)}`), ...KNOWLEDGE.map(item => `${item.title}: ${item.text} Source: ${sourceLink(item.url, env.PUBLIC_ORIGIN || DEFAULT_ORIGIN)}`)].join('\n');
      const generated = await modelAnswer(question, language, context, env);
      return json({ answer: generated || deterministic.answer, sources: deterministic.sources, generated: Boolean(generated), updated: new Date().toISOString() }, 200, origin);
    } catch (error) {
      return json({ answer: 'The catalog is temporarily unavailable. I will not guess the answer. Please use WhatsApp support for current prices, availability, or order help.', sources: [{ title: 'WhatsApp support', url: DEFAULT_WHATSAPP }], error: env.DEBUG === 'true' ? error.message : undefined }, 200, origin);
    }
  }
};
