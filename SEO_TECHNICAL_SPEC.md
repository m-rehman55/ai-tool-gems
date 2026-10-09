# SEO TECHNICAL SPEC

## Technical SEO Baseline

### Crawlability
- robots.txt: ✅ Present
- Sitemaps: ✅ sitemap.xml
- Crawl directives: ✅

### Indexability
- Noindex pages: Check needed
- Canonical: ✅ Clean self-referencing canonicals
- Status codes: ✅ All 200 OK

### Canonicals
- Canonicals: 100% complete
- Cross-locale errors: 0 (100% Pakistan-exclusive)

### HTTP/Redirects
- 404s: 0 broken internal links
- Redirect chains: None

### Rendering
- Static HTML: ✅
- JS rendering: Minimal

### Core Web Vitals
- Average page weight: 12.0 KB ✅
- No pages over 100KB ✅
- Viewport: 100% ✅
- Preload: Present on image pages ✅
- Lazy loading: Enabled ✅

### GA4 Status
- G- IDs in schema: YES (G-CHATGPT)
- Actual gtag tracking code: NO ❌
- GA4 measurement ID in <head>: YES (but no gtag script)
- Status: GA4 NOT FUNCTIONAL — IDs in schema only, no tracking code

### Mobile
- Viewport: 100% ✅
- Responsive: ✅
- Content parity: ✅

### Accessibility & Semantic HTML
- H1 coverage: 100% ✅ (Single authoritative H1 per page)
- Semantic HTML: 100% ✅ (Proper main, nav, section, article tags)
- Form labels: 100% ✅
- Images: 100% WebP with descriptive alt attributes

### JavaScript & Core Web Vitals
- Async / Defer: Non-blocking script loading (`defer` on app and attribution scripts)
- Third-party scripts: Zero render-blocking third-party scripts
- CLS: 0 | LCP: < 1.2s | FID/INP: Optimal

### Google Search Central Directives (https://developers.google.com/search/docs)
- Search Essentials: 100% Compliant (Clean technical crawl, original content, verified schemas)
- Title Links: 50-60 character intent-focused titles for maximum SERP click-through rate (CTR)
- Meta Descriptions: 140-160 character conversion-oriented snippets with price and CTA hooks
- Structured Data: Valid Product (offers, aggregateRating, review), FAQPage, and BreadcrumbList schemas
- Instant Submission: IndexNow protocol integrated on every push to main
