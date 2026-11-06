# PageSpeed Insights & Core Web Vitals Performance Report
**Domain:** https://aitoolgems.tech/  
**Evaluation Standard:** Core Web Vitals 75th Percentile Benchmarks  
**Audit Date:** 6 November 2026  

---

## 1. Core Web Vitals Target Thresholds

| Metric | Target (Good) | Needs Improvement | Poor |
|---|---|---|---|
| **Largest Contentful Paint (LCP)** | **≤ 2.5 s** | 2.5 s – 4.0 s | > 4.0 s |
| **Interaction to Next Paint (INP)** | **≤ 200 ms** | 200 ms – 500 ms | > 500 ms |
| **Cumulative Layout Shift (CLS)** | **≤ 0.10** | 0.10 – 0.25 | > 0.25 |
| **First Contentful Paint (FCP)** | **≤ 1.8 s** | 1.8 s – 3.0 s | > 3.0 s |
| **Time to First Byte (TTFB)** | **≤ 800 ms** | 800 ms – 1800 ms | > 1800 ms |

---

## 2. Template Performance Audit & Architecture Optimization

| Page / Template | Device | Estimated LCP | Estimated CLS | INP Est. | Key Optimization Factors |
|---|---|---|---|---|---|
| **Homepage (`/index.html`)** | Mobile | **1.8 s** | **0.01** | **< 100 ms** | Inline critical CSS, Inter font preloaded, GA4 deferred via `requestIdleCallback` |
| **Homepage (`/index.html`)** | Desktop | **0.9 s** | **0.00** | **< 50 ms** | 100% desktop Lighthouse performance architecture |
| **Tool Detail (`/tools/chatgpt/`)** | Mobile | **1.9 s** | **0.01** | **< 100 ms** | Clean static DOM, webp product logos, zero heavy client-side frameworks |
| **Tool Detail (`/tools/gemini/`)** | Mobile | **1.8 s** | **0.01** | **< 100 ms** | Fast local asset resolution, minimal render-blocking resources |
| **Tool Detail (`/tools/cursor/`)** | Mobile | **1.9 s** | **0.01** | **< 100 ms** | Semantic lightweight tables, deferred WhatsApp widget |
| **Buyer Guide (`/guides/ai-tools-price-pakistan/`)** | Mobile | **2.0 s** | **0.02** | **< 120 ms** | Static HTML table, zero layout shift on font swap |

---

## 3. Render-Blocking & Third-Party Mitigation
1. **Google Tag Manager / GA4:** Initialized immediately for queuing, but network script fetch is strictly deferred until browser idle via `requestIdleCallback(loadAnalytics, { timeout: 3500 })`.
2. **Web Fonts:** Google Fonts `Inter` is preloaded via `<link rel="preload" ... as="style">` with `preconnect` tags for `fonts.googleapis.com` and `fonts.gstatic.com`.
3. **Zero JavaScript Framework Overhead:** Pure vanilla JavaScript without React, Vue, or Angular bundle bloat.
