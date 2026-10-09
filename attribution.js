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

  // GA4 initialization
  window.dataLayer = window.dataLayer || [];
  window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', MEASUREMENT_ID, { send_page_view: true });
  const analyticsScript = document.createElement('script');
  analyticsScript.async = true;
  analyticsScript.src = `https://www.googletagmanager.com/gtag/js?id=${MEASUREMENT_ID}`;
  document.head.appendChild(analyticsScript);

  const originalPush = window.dataLayer.push.bind(window.dataLayer);
  window.dataLayer.push = function (entry) {
    if (entry && typeof entry === 'object' && entry.event && typeof window.gtag === 'function') {
      const { event, ...parameters } = entry;
      window.gtag('event', event, parameters);
    }
    return originalPush(entry);
  };

  window.ATGAttribution = { current, label, appendToMessage };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', decorateWhatsAppLinks, { once: true });
  } else {
    decorateWhatsAppLinks();
  }

  // Event tracking for SEO analytics
  function trackEvent(eventName, params) {
    params = params || {};
    if (typeof window.gtag === 'function') {
      window.gtag('event', eventName, params);
    }
  }

  // view_item - product page views
  function trackViewItem() {
    var productName = document.querySelector('h1');
    if (productName) {
      var name = productName.textContent.trim();
      if (name) {
        trackEvent('view_item', {
          items: [{
            item_id: name.toLowerCase().replace(/[^a-z0-9]/g, '-'),
            item_name: name,
            item_category: 'AI Tool'
          }]
        });
      }
    }
  }

  // select_item - product selection
  document.addEventListener('click', function(e) {
    var link = e.target.closest('a[href*="/tools/"], a[href*="/product/"]');
    if (link) {
      trackEvent('select_item', {
        items: [{
          item_id: link.href.split('/').filter(Boolean).pop() || 'unknown',
          item_name: (link.textContent || '').trim() || 'unknown',
          item_category: 'AI Tool'
        }]
      });
    }
  });

  // click_whatsapp - WhatsApp links
  document.addEventListener('click', function(e) {
    var waLink = e.target.closest('a[href*="wa.me"], a[href*="whatsapp"]');
    if (waLink) {
      trackEvent('click_whatsapp', { link_url: waLink.href });
    }
  });

  // click_order - order intent
  document.addEventListener('click', function(e) {
    var orderLink = e.target.closest('a[href*="buy"], a[href*="order"], a[href*="subscription"], a[href*="purchase"]');
    if (orderLink) {
      trackEvent('click_order', { link_url: orderLink.href });
    }
  });

  // click_affiliate - affiliate links
  document.addEventListener('click', function(e) {
    var affLink = e.target.closest('a[href*="affiliate"], a[href*="ref="], a[href*="click="]');
    if (affLink) {
      trackEvent('click_affiliate', { link_url: affLink.href });
    }
  });

  // view_comparison - comparison pages
  if (document.querySelector('[class*="comparison"], [id*="comparison"], .comparison, #comparison')) {
    trackEvent('view_comparison', { page_type: 'comparison' });
  }

  // view_guide - guide pages
  if (document.querySelector('[class*="guide"], [id*="guide"], .guide, #guide, [class*="article"], [id*="article"]')) {
    trackEvent('view_guide', { page_type: 'guide' });
  }

  // language_switch - language switching
  document.addEventListener('click', function(e) {
    var langLink = e.target.closest('a[href*="/en/"], a[href*="lang="], a[href*="language="]');
    if (langLink) {
      trackEvent('language_switch', { link_url: langLink.href });
    }
  });

  // market_switch - market switching
  document.addEventListener('click', function(e) {
    var marketLink = e.target.closest('a[href*="/pk/"], a[href*="market="], a[href*="country="]');
    if (marketLink) {
      trackEvent('market_switch', { link_url: marketLink.href });
    }
  });

  // Track page view for SPA-like navigation
  if (window.history && window.history.pushState) {
    var originalPushState = window.history.pushState;
    window.history.pushState = function() {
      originalPushState.apply(this, arguments);
      trackEvent('page_view', { page_path: window.location.pathname });
    };
  }

  // Track view_item on product pages
  if (document.querySelector('[class*="product"], [id*="product"], .product, #product')) {
    trackViewItem();
  }

})();
