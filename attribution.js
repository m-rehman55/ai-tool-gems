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

  function detectReferrer() {
    try {
      const ref = document.referrer;
      if (!ref) return null;
      const refHost = new URL(ref).hostname.toLowerCase();
      if (refHost.includes('chatgpt.com') || refHost.includes('openai.com')) {
        return { utm_source: 'chatgpt', utm_medium: 'ai_referral', utm_campaign: 'ai_citation' };
      }
      if (refHost.includes('perplexity.ai')) {
        return { utm_source: 'perplexity', utm_medium: 'ai_referral', utm_campaign: 'ai_citation' };
      }
      if (refHost.includes('claude.ai') || refHost.includes('anthropic.com')) {
        return { utm_source: 'claude', utm_medium: 'ai_referral', utm_campaign: 'ai_citation' };
      }
      if (refHost.includes('gemini.google.com')) {
        return { utm_source: 'gemini', utm_medium: 'ai_referral', utm_campaign: 'ai_citation' };
      }
      if (refHost.includes('copilot.microsoft.com')) {
        return { utm_source: 'copilot', utm_medium: 'ai_referral', utm_campaign: 'ai_citation' };
      }
    } catch (_) {}
    return null;
  }

  function current() {
    const incoming = readFromUrl();
    if (Object.keys(incoming).length) {
      incoming.recorded_at = new Date().toISOString();
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(incoming)); } catch (_) {}
      return incoming;
    }
    const existing = stored();
    if (Object.keys(existing).length) return existing;
    const aiRef = detectReferrer();
    if (aiRef) {
      aiRef.recorded_at = new Date().toISOString();
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(aiRef)); } catch (_) {}
      return aiRef;
    }
    return {};
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
    'analytics_storage': 'denied',
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

  function updateConsent(settings) {
    if (typeof window.gtag === 'function') window.gtag('consent', 'update', settings);
    if (settings && settings.analytics_storage === 'granted') {
      initPostHog();
    }
  }

  // ── PostHog Privacy-First Integration (EU Cloud / Conservative Replay) ────
  function initPostHog(apiKey) {
    if (window.posthog && window.posthog.__loaded) return;
    var key = apiKey || (window.ATG_CONFIG && window.ATG_CONFIG.POSTHOG_KEY) || window.POSTHOG_API_KEY || 'phc_aitoolgems_public_token';
    var host = 'https://eu.i.posthog.com';

    (function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){function g(t,e){var o=e.split(".");2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement("script")).type="text/javascript",p.async=!0,p.src=s.api_host.replace(".i.posthog.com","-assets.i.posthog.com")+"/static/array.js",(r=t.getElementsByTagName("script")[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a="posthog",u.people=u.people||[],u.toString=function(t){var e="posthog";return"posthog"!==a&&(e+="."+a),t||(e+=" (stub)"),e},u.people.toString=function(){return u.toString(1)+".people (stub)"},o="init capture register register_once register_for_session unregister unregister_for_session getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys renderSurvey canRenderSurvey getNextSurveyStep identify setPersonProperties group resetGroups setPersonPropertiesForFlags resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing debug".split(" "),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)})(document,window.posthog||[]);

    window.posthog.init(key, {
      api_host: host,
      ui_host: 'https://eu.posthog.com',
      autocapture: false, // Strict: Disable auto-capturing arbitrary clicks/keystrokes
      capture_pageview: false, // Handled explicitly via taxonomy
      disable_session_recording: false,
      session_recording: {
        mask_all_element_attributes: true, // Masks IDs, data attributes, and form fields
        mask_all_text: true, // Masks all user-entered text during session replays
        mask_input_options: {
          password: true,
          color: true,
          date: true,
          'datetime-local': true,
          email: true,
          month: true,
          number: true,
          range: true,
          search: true,
          tel: true,
          text: true,
          time: true,
          url: true,
          week: true
        }
      },
      sanitize_properties: function(properties, eventName) {
        if (properties && properties['$current_url']) {
          properties['$current_url'] = properties['$current_url'].split('?')[0];
        }
        return properties;
      }
    });
    window.posthog.__loaded = true;
  }

  window.ATGAttribution = { current, label, appendToMessage, updateConsent, initPostHog, trackEvent };
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
    if (path.indexOf('/category/') !== -1 || path.indexOf('/categories/') !== -1) {
      var catParts = (path.indexOf('/category/') !== -1 ? path.split('/category/')[1] : path.split('/categories/')[1]).split('/').filter(Boolean);
      var catSlug = catParts[0] || 'category';
      return { type: 'category', slug: catSlug, path: path };
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

    // 1. Product page view (view_item & view_tool) - Only fired on actual /tools/ routes
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
      trackEvent('view_tool', {
        tool_slug: meta.slug || name.toLowerCase().replace(/[^a-z0-9]/g, '-'),
        tool_name: name,
        currency: 'PKR',
        value: priceVal
      });
      return;
    }

    // 2. Category page view (view_category & view_item_list) - Only fired on actual /category/ routes
    if (meta.type === 'category') {
      var catH1 = document.querySelector('h1');
      var catName = catH1 ? catH1.textContent.trim() : (meta.slug || 'AI Category');
      trackEvent('view_category', {
        category_slug: meta.slug,
        category_name: catName,
        page_path: meta.path
      });
      trackEvent('view_item_list', {
        item_list_name: catName,
        item_list_id: 'category-' + (meta.slug || 'all')
      });
      return;
    }

    // 3. Comparison page view (view_comparison) - Only fired on actual /guides/*-vs-* routes
    if (meta.type === 'comparison') {
      trackEvent('view_comparison', {
        page_type: 'comparison',
        page_path: meta.path
      });
      return;
    }

    // 4. Editorial Guide page view (view_guide) - Only fired on actual /guides/ routes
    if (meta.type === 'guide') {
      trackEvent('view_guide', {
        page_type: 'guide',
        page_path: meta.path
      });
      return;
    }

    // 5. Prices directory view
    if (meta.type === 'prices') {
      trackEvent('view_item_list', {
        item_list_name: 'Pakistan AI Tools Pricing Directory',
        item_list_id: 'prices-directory'
      });
      return;
    }

    // 6. Deals catalog view
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
        // Order Initiation (begin_checkout, generate_lead, click_whatsapp_order_inquiry)
        var h1 = document.querySelector('h1');
        var itemName = h1 ? h1.textContent.trim() : 'AI Tool Subscription';
        trackEvent('whatsapp_order_click', { destination: 'whatsapp_order', item_name: itemName });
        trackEvent('click_whatsapp_order_inquiry', { destination: 'whatsapp_order', item_name: itemName });
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
        trackEvent('click_whatsapp_support', { destination: 'whatsapp_support' });
      }
      return;
    }

    // C) Official Website Reference Clicks (click_official_website)
    var officialLink = e.target.closest('a[data-official], a[rel*="noopener"], .official-link, .updated a');
    if (officialLink && !officialLink.closest('.brand, .floating-whatsapp, nav, footer, .policy-note')) {
      var linkText = (officialLink.textContent || '').toLowerCase();
      var linkHref = (officialLink.href || '').toLowerCase();
      if (officialLink.hasAttribute('data-official') || linkText.indexOf('official') !== -1 || officialLink.closest('.updated')) {
        if (linkHref.indexOf('wa.me') === -1 && linkHref.indexOf('whatsapp.com') === -1) {
          var h1El = document.querySelector('h1');
          trackEvent('click_official_website', {
            tool_name: h1El ? h1El.textContent.trim() : 'AI Tool',
            destination_url: officialLink.href,
            page_path: window.location.pathname
          });
        }
      }
    }

    // D) Payment Guidance Clicks (click_payment_guidance)
    var paymentElem = e.target.closest('#paymentMethodsDisclosure, a[href*="policies.html#payments"], a[href*="policies.html#warranty"], a[href*="policies.html#refunds"], [data-guidance="payment"], .paymentMethodsSummary');
    if (paymentElem) {
      var hrefAttr = paymentElem.getAttribute('href') || '';
      var topic = hrefAttr.indexOf('#') !== -1 ? hrefAttr.split('#')[1] : 'disclosure_toggle';
      trackEvent('click_payment_guidance', {
        guidance_topic: topic,
        page_path: window.location.pathname
      });
    }

    // E) Filter Tools Clicks (filter_tools)
    var filterElem = e.target.closest('[data-filter], .tag-chip, button[data-category], #filterToggle');
    if (filterElem) {
      var fType = filterElem.dataset.tag ? 'tag' : (filterElem.dataset.filter ? 'category' : (filterElem.dataset.category ? 'category_pill' : 'filter_toggle'));
      var fVal = filterElem.dataset.tag || filterElem.dataset.filter || filterElem.dataset.category || 'toggle';
      trackEvent('filter_tools', {
        filter_type: fType,
        filter_value: fVal,
        page_path: window.location.pathname
      });
    }

    // F) Proof Image opens
    var proofElem = e.target.closest('img.proof-image, [data-proof], .payment-proof, .proof-screenshot');
    if (proofElem) {
      trackEvent('proof_image_open', {
        proof_type: 'payment_verification_proof'
      });
      return;
    }

    // G) Affiliate Link Clicks
    var affLink = e.target.closest('a[href*="affiliate"], a[href*="ref="], a[href*="click="]');
    if (affLink) {
      trackEvent('click_affiliate', { link_url: affLink.href });
      return;
    }

    // H) Market & Language switches
    var marketLink = e.target.closest('a[href*="/pk/"], a[href*="market="], a[href*="country="]');
    if (marketLink) {
      trackEvent('market_switch', { link_url: marketLink.href });
      return;
    }
  });

  // ── Search Action Listener (search) ────────────────────────────────────────
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && e.target) {
      var target = e.target;
      if (target.id === 'heroSearch' || target.name === 'q' || target.type === 'search' || (target.className && String(target.className).indexOf('search') !== -1)) {
        var query = (target.value || '').trim();
        if (query.length >= 2) {
          trackEvent('search', {
            search_term: query,
            page_path: window.location.pathname
          });
        }
      }
    }
  }, { passive: true });

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
