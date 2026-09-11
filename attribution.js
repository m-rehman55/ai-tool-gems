(function () {
  'use strict';

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
    document.querySelectorAll('a[href*="wa.me/923476242709"]').forEach(link => {
      try {
        const url = new URL(link.href);
        const message = url.searchParams.get('text') || '';
        url.searchParams.set('text', appendToMessage(message));
        link.href = url.toString();
      } catch (_) {}
    });
  }

  window.ATGAttribution = { current, label, appendToMessage };
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', decorateWhatsAppLinks, { once: true });
  } else {
    decorateWhatsAppLinks();
  }
})();
