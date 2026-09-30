# SEO TECHNICAL SPEC

## Technical SEO Baseline

### Crawlability
- robots.txt: ✅ Present
- Sitemaps: ✅ sitemap.xml + sitemap-jp.xml
- Crawl directives: ✅

### Indexability
- Noindex pages: Check needed
- Canonical: ⚠️ 3 pages missing
- Status codes: Check needed

### Canonicals
- Missing canonicals: 3 pages
- Cross-locale errors: 9 broken hreflang targets

### HTTP/Redirects
- 404s: Check needed
- Redirect chains: Check needed

### Rendering
- Static HTML: ✅
- JS rendering: Minimal

### Core Web Vitals
- Average page weight: 12.0 KB ✅
- Largest page: 57.9 KB (jp/index.html)
- No pages over 100KB ✅
- Viewport: 100% ✅
- Preload: Present on image pages ✅
- Lazy loading: 18% (24/133) ⚠️
- Responsive images (srcset): 0% ❌

### GA4 Status
- G- IDs in schema: YES (G-CHATGPT, G-JP-CHATGPT)
- Actual gtag tracking code: NO ❌
- GA4 measurement ID in <head>: YES (but no gtag script)
- Status: GA4 NOT FUNCTIONAL — IDs in schema only, no tracking code

### Mobile
- Viewport: 100% ✅
- Responsive: ✅
- Content parity: ✅

### Accessibility
- H1 coverage: 100% ✅
- Semantic HTML: 96% ✅
- Form labels: 97% ⚠️

### JavaScript
- Total scripts: 141
- Async: 0 ❌
- Defer: 5 ⚠️
- Third-party: 0 ✅
"""
