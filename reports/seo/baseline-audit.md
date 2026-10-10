# AI Tool Gems Pakistan — Baseline Technical SEO & Architecture Audit

**Audit Date:** 2026-10-11  
**Website:** [https://aitoolgems.tech/](https://aitoolgems.tech/)  
**Deployment Platform:** GitHub Pages (`m-rehman55/ai-tool-gems`, branch: `main`)  
**Target Market:** Pakistan (`en-PK`, PKR pricing, EasyPaisa, JazzCash, SadaPay, WhatsApp)  
**Auditor:** Autonomous SEO Operating System (HERMES Engine)

---

## 1. Executive Summary

| Category | Metric / Finding | Status |
| :--- | :--- | :--- |
| **Indexable URLs** | 52 canonical URLs in `sitemap.xml` | ✅ Verified 100% |
| **Local HTML Pages** | 56 HTML pages (including root utilities) | ✅ Checked (0 errors, 0 warnings) |
| **SEO Integrity Score** | 100 / 100 on live SEO/GEO Monitor | ✅ Complete (52/52 URLs 200 OK) |
| **JSON-LD Schema Points** | 2,820 / 2,820 points (100.0%) | ✅ Complete across all pages |
| **Search Engine Discovery** | Bing IndexNow live ping active | ✅ Instant submission pipeline |
| **AI Crawler Access** | GPTBot, ClaudeBot, PerplexityBot allowed | ✅ Clean in `robots.txt` & `llms.txt` |
| **Pakistani Signals** | PKR rates, EasyPaisa, JazzCash on all 20 tools | ✅ Zero Japan/JPY contamination |

---

## 2. Site Architecture & Directory Layout

```text
ai-tool-gems/
├── index.html                 (Homepage, Hero, 3D Canvas, Tool Finder, Blog Showcase)
├── deals/index.html           (20-product PKR deal directory & bundle savings)
├── prices/index.html          (Verified 2026 pricing index & warranty breakdown)
├── guides/                    (Topical Guides & Blog Hub — 17 published clusters)
│   ├── index.html             (Guides & Blog master index)
│   ├── cursor-ai-pakistan/    (Developer Guide: Cursor AI in Pakistan)
│   ├── claude-ai-pakistan/    (Model Spotlight: Claude 3.5 Sonnet Pakistan)
│   ├── ai-tools-price-pakistan/ (Price Guide: 20 listed tools in PKR)
│   ├── chatgpt-alternatives/  (Editorial Guide: Top ChatGPT Alternatives)
│   ├── chatgpt-vs-gemini-pakistan/ (Head-to-head comparison)
│   └── canva-vs-figma-pakistan/ (Design workflow comparison)
├── blog/index.html            (Fast canonical entry hub for /blog/ visitors)
├── tools/                     (20 Individual Tool Transactional Landing Pages)
│   ├── chatgpt/index.html     (ChatGPT Plus, DALL-E, GPT-4o)
│   ├── gemini/index.html      (Google Gemini Pro, 2M context)
│   ├── leonardo/index.html    (Leonardo AI Essential)
│   └── ...                    (17 more tool pages)
├── data/seo/                  (Machine-readable inventories & link graphs)
│   ├── url-inventory.json     (52 verified URLs with title, desc, H1, intent)
│   ├── keyword-map.json       (Master keyword & anti-cannibalization database)
│   ├── internal-link-map.json (Verified internal link targets & contextual anchors)
│   └── content-queue.json     (Researched content queue for autonomous publishing)
├── sitemap.xml                (52 canonical URLs)
├── sitemap.txt                (Plaintext sitemap)
├── llms.txt                   (Structured context for LLM search engines & bots)
└── robots.txt                 (Explicit allowance for major AI bots)
```

---

## 3. URL Inventory Breakdown

| Page Type | Count | Search Intent | Example URL |
| :--- | :--- | :--- | :--- |
| **Homepage** | 1 | Commercial / Transactional | `https://aitoolgems.tech/` |
| **Deal Directory** | 1 | Commercial | `https://aitoolgems.tech/deals/` |
| **Price Index** | 1 | Commercial / Research | `https://aitoolgems.tech/prices/` |
| **Editorial & Blog Hubs** | 2 | Informational / Navigational | `https://aitoolgems.tech/guides/`, `https://aitoolgems.tech/blog/` |
| **Topical Guides & Blog** | 17 | Informational / Commercial | `https://aitoolgems.tech/guides/cursor-ai-pakistan/` |
| **Product Landing Pages** | 20 | Transactional | `https://aitoolgems.tech/tools/chatgpt/` |
| **Trust, Policies & Sourcing** | 11 | Navigational / E-E-A-T | `https://aitoolgems.tech/how-we-review.html` |
| **Total Canonical URLs** | **52** | — | — |

---

## 4. Technical SEO Compliance

1. **Title & Heading Hierarchy:**
   - Every page features exactly **one primary `<h1>`** tag.
   - Title tag lengths adhere to strict 20–65 character constraints.
   - Meta descriptions adhere to 70–170 character constraints.
2. **Canonical & URL Integrity:**
   - Every indexable page declares a self-referential `<link rel="canonical">` matching its exact trailing-slash convention.
   - No redirect chains or duplicate URL loops detected.
3. **Structured Data Completeness:**
   - Product pages include `Product`, `Offer`, `MerchantReturnPolicy`, `ShippingDetails`, and `AggregateRating` schemas.
   - Guide pages include `Article`, `BreadcrumbList`, and `FAQPage` schemas.
   - Zero syntax errors or missing fields detected (Score: 2,820 / 2,820 points).
4. **Internal Linking & Crawlability:**
   - Navigation links across desktop header, mobile menu, and footer point to `Guides & Blog`.
   - Homepage contains a dedicated 6-card showcase (`#blog-guides`) with direct links to high-intent guides.
   - Cross-linking between related tools and parent guides is operational.

---

## 5. Automation & GitHub Workflows

1. **Autonomous SEO Growth Pipeline (`seo-growth-pipeline.yml`):**
   - Triggers on every push to `main`.
   - Runs unit tests, DOM integrity checks, schema audit, and pings IndexNow API live.
2. **Daily SEO/GEO Integrity Monitor (`daily-seo-geo-monitor.yml`):**
   - Runs daily at 07:15 PKT (`15 02 * * *` UTC).
   - Validates live HTTP response status for all 52 URLs, verifies AEO answer blocks, and checks AI bot crawlability.
3. **Social Content Automation (`social-content-pack.yml`):**
   - Renders daily deal media and schedules updates via Buffer at 04:45 PKT.
4. **Hermes 3-Shift Monitor (`hermes-agent-shifts.yml`):**
   - Dispatches autonomous morning, afternoon, and night shift health reports to Telegram.
5. **Daily Blog & Guide Publisher (`daily-blog-publisher.yml`):**
   - Scheduled daily content engine running safe pre-publish validation gates.

---

## 6. Gaps & Opportunities Identified

1. **Anti-Cannibalization Control:** Standardize a central `data/seo/keyword-map.json` so every proposed topic is vetted against existing slugs and primary keywords prior to generation.
2. **Contextual Internal Linking Engine:** Introduce `data/seo/internal-link-map.json` to systematically suggest 2+ product links and 2+ contextual guide links per article with non-repetitive anchors.
3. **Automated Content Validation Gate:** Implement `scripts/validate_content.py` to enforce strict anti-stuffing bounds (0.5%–2.0%), schema presence, word count sanity, and zero broken links before commits reach `main`.
