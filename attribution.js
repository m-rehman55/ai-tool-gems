(function () {
  'use strict';

  const MEASUREMENT_ID = 'G-NQJCMDCLLP';
  const STORAGE_KEY = 'atg-attribution';
  const ALLOWED_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'src'];

  function clean(value) {
    return String(value || '').replace(/[^a-zA-Z0-9_.:-]/g, '').slice(0, 80);
  }

  function readFromUrl() {
    const params = new URLSearchParams(window.location.search);
    const data = {};
    ALLOWED_KEYS.forEach(key => {
      const value = clean(params.get(key));
      if (value) data[key] = value;
    });
    return data;
  }

  function stored() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
    } catch (_) {
      return {};
    }
  }

  function current() {
    const incoming = readFromUrl();
    if (Object.keys(incoming).length) {
      incoming.recorded_at = new Date().toISOString();
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(incoming)); } catch (_) {}
      return incoming;
    }
    return stored();
  }

  function label() {
    const data = current();
    const parts = ALLOWED_KEYS.filter(key => data[key]).map(key => `${key}=${data[key]}`);
    return parts.length ? parts.join('; ') : '';
  }

  function appendToMessage(message) {
    const source = label();
    return source && !String(message).includes('Campaign source:')
      ? `${message}\n\nCampaign source: ${source}`
      : message;
  }

  function decorateWhatsAppLinks() {
    const source = label();
    if (!source) return;
    document.querySelectorAll('a[href*="wa.me/923236715731"]').forEach(link => {
      try {
        const url = new URL(link.href);
        const message = url.searchParams.get('text') || '';
        url.searchParams.set('text', appendToMessage(message));
        link.href = url.toString();
      } catch (_) {}
    });
  }

  // GA4 initialization: keep the queue available immediately, but defer the
  // third-party download until the browser is idle so it cannot compete with LCP.
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };

  // Google Consent Mode v2: privacy-first defaults before tag evaluation
  window.gtag('consent', 'default', {
    'analytics_storage': 'granted',
    'ad_storage': 'denied',
    'ad_user_data': 'denied',
    'ad_personalization': 'denied',
    'wait_for_update': 500
  });

  window.gtag('js', new Date());
  window.gtag('config', MEASUREMENT_ID, { 
    send_page_view: true,
    anonymize_ip: true
  });
  function loadAnalytics() {
    if (document.querySelector(`script[src*="googletagmanager.com/gtag/js?id=${MEASUREMENT_ID}"]`)) return;
    const analyticsScript = document.createElement('script');
    analyticsScript.async = true;
    analyticsScript.src = `https://www.googletagmanager.com/gtag/js?id=${MEASUREMENT_ID}`;
    document.head.appendChild(analyticsScript);
  }
  if ('requestIdleCallback' in window) requestIdleCallback(loadAnalytics, { timeout: 3500 });
  else setTimeout(loadAnalytics, 2000);

  const originalPush = window.dataLayer.push.bind(window.dataLayer);
  window.dataLayer.push = function (entry) {
    if (entry && typeof entry === 'object' && entry.event && typeof window.gtag === 'function') {
      const { event, ...parameters } = entry;
      window.gtag('event', event, parameters);
    }
    return originalPush(entry);
  };

  function updateConsent(settings) { if (typeof window.gtag === 'function') window.gtag('consent', 'update', settings); }
  window.ATGAttribution = { current, label, appendToMessage, updateConsent };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', decorateWhatsAppLinks, { once: true });
  } else {
    decorateWhatsAppLinks();
  }

  // ── Explicit Page Type Detection & Clean Ecommerce Event Taxonomy ────────
  function getPageMetadata() {
    var path = window.location.pathname.toLowerCase();
    var metaType = (document.querySelector('meta[name="page-type"]') || {}).content;

    if (metaType) {
      return { type: metaType, path: path };
    }

    if (path === '/' || path === '/index.html' || path === '') {
      return { type: 'homepage', path: path };
    }
    if (path.indexOf('/tools/') !== -1) {
      var parts = path.split('/tools/')[1].split('/').filter(Boolean);
      var slug = parts[0] || 'tool';
      return { type: 'product', slug: slug, path: path };
    }
    if (path.indexOf('/guides/') !== -1) {
      var isComparison = path.indexOf('-vs-') !== -1 || path.indexOf('compare') !== -1;
      return { type: isComparison ? 'comparison' : 'guide', path: path };
    }
    if (path.indexOf('/prices/') !== -1) {
      return { type: 'prices', path: path };
    }
    if (path.indexOf('/deals/') !== -1) {
      return { type: 'deals', path: path };
    }
    return { type: 'content', path: path };
  }

  // Event tracking wrapper (GA4 & PostHog dual-dispatch)
  function trackEvent(eventName, params) {
    params = params || {};
    if (typeof window.gtag === 'function') {
      window.gtag('event', eventName, params);
    }
    if (window.posthog && typeof window.posthog.capture === 'function') {
      window.posthog.capture(eventName, params);
    }
  }

  // Track initial page load according to clean taxonomy
  function trackPageLoad() {
    var meta = getPageMetadata();

    // 1. Product page view (view_item) - Only fired on actual /tools/ routes
    if (meta.type === 'product') {
      var h1 = document.querySelector('h1');
      var name = h1 ? h1.textContent.trim() : (meta.slug || 'AI Tool');
      var priceElem = document.querySelector('.price-pkr, [data-price-pkr], .price, .product-price');
      var priceMatch = priceElem ? String(priceElem.textContent).replace(/[^0-9]/g, '') : '';
      var priceVal = priceMatch ? parseInt(priceMatch, 10) : undefined;

      trackEvent('view_item', {
        currency: 'PKR',
        value: priceVal,
        items: [{
          item_id: meta.slug || name.toLowerCase().replace(/[^a-z0-9]/g, '-'),
          item_name: name,
          item_category: 'AI Tool',
          price: priceVal,
          currency: 'PKR'
        }]
      });
      return;
    }

    // 2. Comparison page view (view_comparison) - Only fired on actual /guides/*-vs-* routes
    if (meta.type === 'comparison') {
      trackEvent('view_comparison', {
        page_type: 'comparison',
        page_path: meta.path
      });
      return;
    }

    // 3. Editorial Guide page view (view_guide) - Only fired on actual /guides/ routes
    if (meta.type === 'guide') {
      trackEvent('view_guide', {
        page_type: 'guide',
        page_path: meta.path
      });
      return;
    }

    // 4. Prices directory view
    if (meta.type === 'prices') {
      trackEvent('view_item_list', {
        item_list_name: 'Pakistan AI Tools Pricing Directory',
        item_list_id: 'prices-directory'
      });
      return;
    }

    // 5. Deals catalog view
    if (meta.type === 'deals') {
      trackEvent('view_item_list', {
        item_list_name: 'AIToolGems Deals Catalog',
        item_list_id: 'deals-catalog'
      });
      return;
    }

    // Homepage and standard pages DO NOT trigger view_item or view_guide!
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', trackPageLoad, { once: true });
  } else {
    trackPageLoad();
  }

  // ── Interactions & Clicks ──────────────────────────────────────────────────
  document.addEventListener('click', function(e) {
    // A) Product selection / Navigation to tool page
    var toolLink = e.target.closest('a[href*="/tools/"]');
    if (toolLink && !toolLink.closest('.floating-whatsapp')) {
      var slug = toolLink.href.split('/tools/')[1] ? toolLink.href.split('/tools/')[1].split('/')[0] : 'unknown';
      trackEvent('select_item', {
        items: [{
          item_id: slug,
          item_name: (toolLink.textContent || slug).trim(),
          item_category: 'AI Tool'
        }]
      });
    }

    // B) WhatsApp Interactions: Distinguish Order vs Support vs Channel
    var waLink = e.target.closest('a[href*="wa.me"], a[href*="whatsapp.com"], [data-whatsapp]');
    if (waLink) {
      var href = waLink.href || '';
      var text = (waLink.textContent || '').toLowerCase();
      var isChannel = href.indexOf('whatsapp.com/channel') !== -1;
      var isOrder = waLink.closest('button[data-order], .buy-now-card, .order-now, [data-step-action="whatsapp"]') ||
                    text.indexOf('buy') !== -1 || text.indexOf('order') !== -1 || text.indexOf('get access') !== -1 ||
                    href.indexOf('interested in') !== -1;

      if (isChannel) {
        trackEvent('whatsapp_channel_click', { destination: 'whatsapp_channel' });
      } else if (isOrder) {
        // Order Initiation (begin_checkout & qualified lead generation)
        var h1 = document.querySelector('h1');
        var itemName = h1 ? h1.textContent.trim() : 'AI Tool Subscription';
        trackEvent('whatsapp_order_click', { destination: 'whatsapp_order', item_name: itemName });
        trackEvent('begin_checkout', {
          currency: 'PKR',
          items: [{ item_name: itemName, currency: 'PKR', quantity: 1 }]
        });
        trackEvent('generate_lead', {
          currency: 'PKR',
          lead_type: 'whatsapp_order_inquiry',
          item_name: itemName
        });
      } else {
        // Support Inquiry
        trackEvent('whatsapp_support_click', { destination: 'whatsapp_support' });
      }
      return;
    }

    // C) Proof Image opens
    var proofElem = e.target.closest('img.proof-image, [data-proof], .payment-proof, .proof-screenshot');
    if (proofElem) {
      trackEvent('proof_image_open', {
        proof_src: proofElem.src || proofElem.dataset.proof || 'proof'
      });
      return;
    }

    // D) Affiliate Link Clicks
    var affLink = e.target.closest('a[href*="affiliate"], a[href*="ref="], a[href*="click="]');
    if (affLink) {
      trackEvent('click_affiliate', { link_url: affLink.href });
      return;
    }

    // E) Market & Language switches
    var marketLink = e.target.closest('a[href*="/pk/"], a[href*="market="], a[href*="country="]');
    if (marketLink) {
      trackEvent('market_switch', { link_url: marketLink.href });
      return;
    }
  });

  // ── Behavioural Intelligence: Rage Click & Dead Click Detection ──────────
  var recentClicks = [];
  document.addEventListener('click', function (e) {
    if (!e.target) return;
    var now = Date.now();
    recentClicks.push({ target: e.target, time: now });
    recentClicks = recentClicks.filter(function (c) { return now - c.time <= 1000; });
    var sameClicks = recentClicks.filter(function (c) { return c.target === e.target; });
    if (sameClicks.length === 3) {
      var tag = (e.target.tagName || 'ELEMENT').toLowerCase();
      var cls = e.target.className && typeof e.target.className === 'string' ? '.' + e.target.className.trim().split(/\s+/)[0] : '';
      trackEvent('rage_click', {
        target_selector: (tag + cls).slice(0, 60),
        click_count: sameClicks.length,
        time_window_ms: 1000,
        page_url: window.location.pathname
      });
    }

    if (!e.target.closest('a, button, input, select, textarea, [role="button"], [tabindex]')) {
      var style = window.getComputedStyle ? window.getComputedStyle(e.target) : null;
      if (style && style.cursor === 'pointer') {
        trackEvent('dead_click', {
          target_selector: (e.target.tagName || 'ELEMENT').toLowerCase(),
          text_content: (e.target.textContent || '').trim().slice(0, 40),
          page_url: window.location.pathname
        });
      }
    }
  }, { passive: true });

  // Track page view for SPA-like navigation
  if (window.history && window.history.pushState) {
    var originalPushState = window.history.pushState;
    window.history.pushState = function() {
      originalPushState.apply(this, arguments);
      trackEvent('page_view', { page_path: window.location.pathname });
    };
  }

// Global floating WhatsApp button (ensures WhatsApp +923236715731 is accessible site-wide)
  function ensureFloatingWhatsApp() {
    if (document.querySelector('.floating-whatsapp, .floating-wa-btn')) return;
    if (/\/admin\.html$/i.test(window.location.pathname)) return;

    var waBtn = document.createElement('a');
    waBtn.className = 'floating-whatsapp';
    waBtn.target = '_blank';
    waBtn.rel = 'noopener nofollow';
    waBtn.setAttribute('aria-label', 'Chat with us on WhatsApp (+92 323 6715731)');

    var msg = 'Hello AI Tool Gems 👋, I need assistance choosing a premium AI tool.';
    var h1 = document.querySelector('h1');
    if (h1 && h1.textContent.trim()) {
      var title = h1.textContent.trim().replace(/\s+/g, ' ').slice(0, 70);
      msg = 'Hello AI Tool Gems 👋\n\nI am interested in:\n' + title + '\n\nPlease confirm availability and details.';
    }
    waBtn.href = 'https://wa.me/923236715731?text=' + encodeURIComponent(msg);
    waBtn.innerHTML = '<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.711 2.598 2.664-.698c.969.587 1.771.879 2.796.88h.001c3.181 0 5.767-2.586 5.768-5.766 0-3.18-2.587-5.767-5.769-5.767zm7.536 5.765c-.002 4.148-3.375 7.52-7.525 7.52-1.309 0-2.548-.344-3.642-.947l-4.04 1.059 1.079-3.94c-.663-1.144-1.026-2.454-1.026-3.692.002-4.149 3.375-7.52 7.525-7.52 4.15 0 7.525 3.371 7.529 7.52z"/></svg><span>WhatsApp</span>';

    document.body.appendChild(waBtn);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', ensureFloatingWhatsApp, { once: true });
  } else {
    ensureFloatingWhatsApp();
  }

  // Shared source-based assistant. Keep the private admin portal out of the public widget.
  if (!/\/admin\.html$/i.test(window.location.pathname) && !document.querySelector('script[data-aitg-chatbot]')) {
    const chatbotStyles = document.createElement('link');
    chatbotStyles.rel = 'stylesheet';
    chatbotStyles.href = '/chatbot/widget.css?v=2';
    chatbotStyles.dataset.aitgChatbot = 'true';
    document.head.appendChild(chatbotStyles);
    const chatbotScript = document.createElement('script');
    chatbotScript.src = '/chatbot/widget.js?v=2';
    chatbotScript.defer = true;
    chatbotScript.dataset.aitgChatbot = 'true';
    document.head.appendChild(chatbotScript);
  }

})();
