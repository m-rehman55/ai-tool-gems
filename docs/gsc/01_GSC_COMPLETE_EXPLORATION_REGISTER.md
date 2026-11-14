# 🧭 Google Search Console Complete Exploration & Navigation Register

**Property:** `https://aitoolgems.tech/` (`sc-domain:aitoolgems.tech`)  
**Audit Date:** 14 November 2026  
**Auditor:** HERMES-PRIME Senior Search Forensics & Technical Architecture Team  
**Verification Method:** Live Authenticated Chrome DevTools Session (`mrehmanfarooq6@gmail.com`)  

---

## 1. Master Exploration & Navigation Register

| Section | Subsection | URL / Path | Opened | Filters Explored | Data Extracted | Root Cause Investigated | Status | Evidence Reference |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Overview** | Main Dashboard | `/overview` | YES | Default 3M | Top metrics, widgets, cards | N/A | **COMPLETED** | Screenshot `media_0.png` |
| **Overview** | Search Console Insights | `/insights` | YES | 28D vs 7D | 36 clicks (+89%), 1.28k imp (+289%), top 18 pages | `og:image` logo fallback | **COMPLETED** | Step 369/393 |
| **Overview** | Recommendations | `/overview` | YES | All | Evaluated merchant suggestions | Misrepresentation defense | **COMPLETED** | Step 345 |
| **Performance** | Core KPIs & Chart | `/performance/search-analytics` | YES | 24H, 7D, 28D, 3M, Compare | 56 clicks, 1.63k imp, 3.4% CTR, Pos 13.1 | Historical rolling window | **COMPLETED** | Step 426 `media_0.png` |
| **Performance** | Queries Tab | `/performance/search-analytics` | YES | Regex, Contains, Top clicks | 215 queries, 54 anonymized clicks | Intent clustering | **COMPLETED** | `05_GSC_PERFORMANCE_OPPORTUNITIES.csv` |
| **Performance** | Pages Tab | `/performance/search-analytics` | YES | High-imp, zero-click | 108 pages, Allinone (287 imp), Prices (140 imp) | Snippet CTR hooks | **COMPLETED** | Step 426 |
| **Performance** | Countries Tab | `/performance/search-analytics` | YES | Country breakdown | 47 countries, Pakistan 82.1% clicks (46 clicks) | Domestic payment intent | **COMPLETED** | Full Country Matrix |
| **Performance** | Devices Tab | `/performance/search-analytics` | YES | Mobile, Desktop, Tablet | Mobile 53.6% clicks (5.8% CTR), Desktop 46.4% | Mobile-first indexing | **COMPLETED** | Device Breakdown |
| **Performance** | Search Appearance | `/performance/search-analytics` | YES | Rich snippets, Product | Product snippets: 9 clicks, 316 imp; Review: 60 imp | Structured data health | **COMPLETED** | Search Appearance Tab |
| **Performance** | Generative AI Features | `/performance/search-analytics/ai` | YES | AI Overviews (SGE) | 150 impressions across 38 pages, Pakistan 89.3% | RAG chunking readiness | **COMPLETED** | Step 393 `media_0.png` |
| **Performance** | Filter: `"pakistan"` | `/performance/search-analytics` | YES | Query contains | 37 queries, 87 imp, 2 clicks, Avg pos 48.6 | High commercial intent | **COMPLETED** | Query Filter Matrix |
| **Performance** | Filter: `"price"` | `/performance/search-analytics` | YES | Query contains | 26 queries, 59 imp, Avg pos 51.7 | Transactional pricing | **COMPLETED** | Query Filter Matrix |
| **Performance** | Filter: `"buy"` | `/performance/search-analytics` | YES | Query contains | 3 queries, 3 imp, Pos 24-91 | Direct checkout intent | **COMPLETED** | Query Filter Matrix |
| **Indexing** | Page Indexing Summary | `/index` | YES | Default | 103 Indexed, 18 Not Indexed | 100% accounted for | **COMPLETED** | Step 249 |
| **Indexing** | Not Found (404) | `/index` | YES | 14 pages drilldown | 14 URLs (All legacy `/jp/` paths) | Decommissioned language | **COMPLETED** | `04_GSC_INDEXING_URL_INVESTIGATION.csv` |
| **Indexing** | Page with redirect | `/index` | YES | 1 page drilldown | `https://aitoolgems.tech/index.html` (301 to `/`) | Root permalink redirect | **COMPLETED** | Step 249 |
| **Indexing** | Crawled - not indexed | `/index` | YES | 1 page drilldown | `https://aitoolgems.tech/tools/bolt-new/` | Newly crawled queue | **COMPLETED** | `04_GSC_INDEXING_URL_INVESTIGATION.csv` |
| **Indexing** | Alternate with canonical | `/index` | YES | 2 pages drilldown | Social UTM tracking tags (`src=ti-...`, `in-...`) | Clean canonicalization | **COMPLETED** | Step 249 `media_0.png` |
| **Indexing** | Sitemaps | `/sitemaps` | YES | Submitted files | `/sitemap.xml` Success (111 discovered URLs) | Clean generator sync | **COMPLETED** | Step 261 `media_0.png` |
| **Indexing** | Removals | `/removals` | YES | Temp, Outdated, SafeSearch | 5 active temp removals for `/jp/` from 5 Nov | Clean Japanese removal | **COMPLETED** | Step 276 `media_0.png` |
| **Experience** | Core Web Vitals | `/core-web-vitals` | YES | Mobile & Desktop | Insufficient CrUX field volume, 0 Poor, 0 Need imp | Static fast HTML | **COMPLETED** | Step 249 |
| **Experience** | HTTPS | `/https` | YES | Security | 81 HTTPS URLs, 0 Non-HTTPS, No issues | Full HTTPS cert | **COMPLETED** | Step 249 |
| **Shopping** | Product Snippets | `/r/product` | YES | Valid vs Invalid | 55 Valid, 0 Invalid, AggregateRating recs | Compliant JSON-LD | **COMPLETED** | `06_GSC_SHOPPING_STRUCTURED_DATA_REPORT.md` |
| **Shopping** | Merchant Listings | `/r/merchant-listings` | YES | Valid vs Invalid | 55 Valid, 0 Invalid, 26 items flagged | Return & Shipping schema | **COMPLETED** | `06_GSC_SHOPPING_STRUCTURED_DATA_REPORT.md` |
| **Shopping** | Warning: Return Policy | `/r/merchant-listings` | YES | 26 items drilldown | 21 homepage offers + 5 tool pages | Digital good policy lock | **COMPLETED** | Step 345 `media_0.png` |
| **Shopping** | Warning: Shipping Details | `/r/merchant-listings` | YES | 26 items drilldown | 21 homepage offers + 5 tool pages | Digital delivery model | **COMPLETED** | Step 357 `media_0.png` |
| **Enhancements** | Breadcrumbs | `/r/breadcrumbs` | YES | Valid vs Invalid | 55 Valid, 0 Invalid | BreadcrumbList schema | **COMPLETED** | Step 249 |
| **Enhancements** | Review Snippets | `/r/review-snippet` | YES | Valid vs Invalid | 43 Valid, 0 Invalid | Grounded reviews | **COMPLETED** | Step 249 |
| **Enhancements** | Datasets | `/r/datasets` | YES | Valid vs Invalid | 1 Valid (`prices/`), 0 Invalid | CSV/JSON pricing index | **COMPLETED** | Step 249 |
| **Security** | Manual Actions | `/manual-actions` | YES | Penalties check | 🟢 "No issues detected" | 100% Clean standing | **COMPLETED** | Step 276 |
| **Security** | Security Issues | `/security-issues` | YES | Malware check | 🟢 "No issues detected" | 100% Clean standing | **COMPLETED** | Step 276 |
| **Settings** | Ownership Verification | `/settings` | YES | Methods | HTML file (`googleb36d...`) & DNS TXT verified | Dual verified owners | **COMPLETED** | Step 318 `media_0.png` |
| **Settings** | Users & Permissions | `/settings/users` | YES | Roster | `hermes-agent@...` & `mrehmanfarooq6@gmail.com` | Full Owner permissions | **COMPLETED** | Step 318 `media_0.png` |
| **Settings** | Robots.txt Report | `/settings/robots-txt` | YES | Open Report | Status: Fetched, 951 B, 0 errors, Recrawl requested | Full AI bot access | **COMPLETED** | Step 369 `media_0.png` |
| **Settings** | Crawl Stats | `/settings/crawl-stats` | YES | Full breakdown | 1.47k req, 13.9 MB, 106ms avg, Host normalized | Grouped 404 analysis | **COMPLETED** | `03_GSC_CRAWL_STATS_FORENSIC_REPORT.md` |

---

## 2. Exploration Coverage Metric
* **Total Sections & Subsections Evaluated:** **35 / 35 (100% Full UI Coverage)**
* **Unexplored Sections:** **0**
* **Blocked Sections:** **0**
* **Data Sources Verified:** Live Chrome Browser Session + GSC Search Analytics API + Local Repository Source Verification.
