# 07. GSC Forensic Root Cause to Code Mapping Matrix

**Property:** `sc-domain:aitoolgems.tech`  
**Site:** `https://aitoolgems.tech/`  
**Date of Audit:** November 14, 2026  
**Auditor:** HERMES Technical SEO & Systems Architecture Team  

---

## 1. Overview

This document maps every single forensic finding, anomaly, crawl observation, indexing state, and CTR performance opportunity discovered during the live Google Search Console inspection directly to the repository codebase, configuration files, and GitHub automation workflows.

---

## 2. Root Cause to Code Mapping Table

| # | GSC Observation / Issue | GSC Report Location | Root Cause Analysis | Repository Code Location | Fix Status & Action Taken |
| :-: | :--- | :--- | :--- | :--- | :--- |
| **1** | **Chatbot 404 Errors**<br>`/chatbot/widget.css?v=2`<br>`/chatbot/widget.js?v=2` | Crawl Stats (`/settings/crawl-stats`)<br>Page Indexing: Not Found (404) | In older builds, `scripts/build_public_site.py` did not include the `chatbot/` directory in `APPROVED_PUBLIC_DIRS`. When Googlebot requested the asset on 12/11/2026, GitHub Pages returned HTTP 404. | `scripts/build_public_site.py:34`<br>`chatbot/widget.js`<br>`chatbot/widget.css` | **FIXED & VERIFIED**<br>Added `chatbot` to `APPROVED_PUBLIC_DIRS` in PR #57 / #59. Live curl check returns **HTTP 200 OK**. |
| **2** | **Legacy `/jp/` 404 Errors**<br>(14 URLs, e.g. `/jp/tools/gemini/`) | Page Indexing: Not Found (404)<br>Crawl Stats: By Response (404) | A previous experimental localized Japanese directory (`/jp/`) was deleted from the repository. Because `/jp/tools/gemini/` received an organic click in October, Googlebot kept re-crawling it to check for updates. | Directory deleted from git history.<br>`sitemap.xml` (does not list `/jp/`)<br>`robots.txt` | **PERFECT BY DESIGN**<br>Google Search Central guidelines state deleted pages should return HTTP 404 or 410. Disallowing in robots.txt would trap them in index; returning 404 allows Googlebot to drop them naturally. |
| **3** | **Search Console Insights:**<br>Pages show brand logo instead of product graphic | Search Console Insights (`/insights`)<br>"Your most popular content" | Tool pages defaulted their `<meta property="og:image">` to `assets/images/brand-logo-light.webp` rather than tool-specific high-resolution artwork or UI graphics. | `tools/allinone/index.html:15`<br>`tools/claude/index.html:15`<br>`tools/chatgpt/index.html:15`<br>`tools/gemini/index.html:15` | **IMPLEMENTED**<br>Updated `og:image` tags to point to dedicated high-resolution tool logos in `assets/product-logos/`. |
| **4** | **`tools/allinone/` CTR Goldmine**<br>(287 imp, Pos 8.9, 0 clicks) | Search Performance: Pages (`/performance/search-analytics`) | Generic title and meta description failed to communicate clear pricing, trust signals, and domestic payment options in Pakistan SERP snippets. | `tools/allinone/index.html:7-14` | **OPTIMIZED**<br>Upgraded title to include commercial keywords, PKR pricing, and domestic payment options. |
| **5** | **`prices/` CTR Goldmine**<br>(140 imp, Pos 10.1, 0 clicks) | Search Performance: Pages (`/performance/search-analytics`) | High commercial intent query group ("ai tools price in pakistan") with snippet lacking direct price ranges and immediate contact CTAs. | `prices/index.html:7-14` | **OPTIMIZED**<br>Upgraded title and meta description to highlight updated 2026 rates and payment rails. |
| **6** | **`tools/bolt-new/` Status:**<br>"Crawled - currently not indexed" | Page Indexing (`/index`)<br>Status: Discovered/Crawled | Fresh tool page crawled on November 10, 2026. Page is undergoing standard secondary index processing; internal link graph was sparse. | `tools/bolt-new/index.html`<br>`tools/index.html`<br>`sitemap.xml` | **INDEX BOOSTED**<br>Reinforced internal links from coding tool sections and sitemap priority `0.8`. Recrawl requested. |
| **7** | **Merchant Listings Warnings**<br>`hasMerchantReturnPolicy`<br>`shippingDetails` | Merchant Listings (`/r/merchant-listings`)<br>(26 Items) | Non-physical digital SaaS services lack traditional postal courier shipping. Injecting fake postal shipping violates Google Merchant Center misrepresentation rules. | `index.html:JSON-LD`<br>`tools/*/index.html:JSON-LD`<br>`tests/test_integrity_and_regressions.py` | **ANALYZED & PROTECTED**<br>GSC flags these as optional recommendations. Repository safety tests enforce authentic digital delivery declaration without fake courier claims. |
| **8** | **Robots.txt Recrawl Cadence**<br>(951 Bytes, Fetched) | Settings: Robots.txt (`/settings/robots-txt`) | Googlebot cached previous robots.txt version. Fast verification needed after recent deployment changes. | `robots.txt` | **RECRAWL TRIGGERED**<br>Live browser subagent clicked "Request recrawl" on 14/11/2026. Status confirmed: *"Recrawl request sent"*. |
| **9** | **Google AI Overviews Grounding**<br>(150 impressions across 38 URLs) | Search Performance: AI (`/performance/search-analytics/ai`) | High citation frequency for `guides/claude-ai-pakistan/` (30 citations) and `tools/gemini/` (21 citations) demonstrates strong RAG extractability. | `guides/claude-ai-pakistan/index.html`<br>`tools/gemini/index.html`<br>`llms.txt`<br>`llms-full.txt` | **MAINTAINED & EXPANDED**<br>Synchronized direct-answer definitions and `llms.txt` machine knowledge bases via `aio_agent`. |

---

## 3. Architecture & Automation Integration

All fixes are permanently protected by our automated test harness:
- **`tests/test_integrity_and_regressions.py`**: Ensures 0 broken links, valid canonicals, and correct metadata.
- **`scripts/link_graph_checker.py --strict`**: Validates 4,480+ links across all 91 pages.
- **`aio_agent/`**: Verifies Google AI Overviews query fan-out and RAG extractability.
- **`ping_agent/`**: Dispatches instant IndexNow updates upon any deployment.
