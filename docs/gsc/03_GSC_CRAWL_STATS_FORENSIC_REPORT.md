# 🔬 Google Search Console Crawl Stats Forensic Audit Report

**Property:** `https://aitoolgems.tech/`  
**Report Window:** 90 Days Rolling (Ending 12/11/2026)  
**Host Status:** Acceptable fail rate (Normalized to 0% failure)  
**Auditor:** HERMES-PRIME Crawl Engineering & Server Forensics Directorate  

---

## 1. Quantitative Core Metrics Overview

* **Total Crawl Requests (90-Day Volume):** **1,470 requests (1.47k)**
* **Total Download Size:** **13.9 MB**
* **Average Response Time:** **106 milliseconds** (Top-tier edge CDN performance)
* **Host Status Health History:**
  * **Robots.txt Fetch:** 0% Failure rate (100% successful)
  * **DNS Resolution:** 0% Failure rate (100% successful)
  * **Server Connectivity:** 0% Failure rate currently; 1 historic timeout incident on 31/10/2026 at 12:38 (`notion.png` timed out at 13s, since resolved to 356ms).

---

## 2. Crawl Request Breakdown by Response Code

| HTTP Status Code | Share (%) | Est. Request Count | Description & Impact |
| :--- | :---: | :---: | :--- |
| **200 (OK)** | **89%** | ~1,308 requests | Healthy content crawling across canonical tools and guides. |
| **404 (Not Found)** | **10%** | **139 requests** | Crawl waste on 29 distinct legacy or deleted URLs. |
| **301 (Moved Permanently)** | **< 1%** | 6 requests | Standard permalink redirection (e.g. `/index.html` -> `/`). |
| **Timeout / Unreachable** | **< 1%** | 1 request | Single 13s latency spike on 31/10/2026. |
| **5xx (Server Error)** | **0%** | 0 requests | Zero server crashes or gateway drops. |
| **Blocked by robots.txt** | **0%** | 0 requests | Zero accidental crawler blocks. |

---

## 3. Crawl Breakdown by File Type

| File Type | Share (%) | Analysis |
| :--- | :---: | :--- |
| **HTML** | **70%** | Primary crawling of tool listings, guides, categories, and policy pages. |
| **Unknown (Failed Requests)** | **10%** | Direct 1:1 match with the 10% 404 HTTP errors. |
| **Image** | **8%** | Googlebot Image discovering product logos and visual diagrams. |
| **CSS** | **7%** | Style rendering resources (`style.css`, `tool-page.css`, `guide.css`). |
| **JavaScript** | **5%** | Script assets (`app.js`, `attribution.js`). |
| **Other / Fonts** | **< 1%** | Web fonts (`woff2`, `ttf`) and manifest files. |

---

## 4. Crawl Breakdown by Purpose

* **Refresh (90% of Total Requests):**  
  Googlebot primarily re-visits URLs it already knows about to check for price modifications, content updates, or header changes. Because 90% of crawl activity is Refresh, legacy deleted URLs remain in the crawl queue until Googlebot verifies repeated 404s over several cycles.
* **Discovery (10% of Total Requests):**  
  Dedicated to discovering newly published content. As legacy 404s decline, Googlebot's discovery budget will expand to index new tool additions and weekly blog guides rapidly.

---

## 5. Crawl Breakdown by Googlebot Type

* **Googlebot Smartphone:** **45%** (Mobile-first indexing flagship user-agent).
* **Googlebot Desktop:** **24%** (Desktop parity checking).
* **Page Resource Load:** **12%** (Headless Chromium rendering engine evaluating CSS/JS layout and visual contrast).
* **Googlebot Image:** **11%** (Asset indexing for Google Images).
* **Other Agent Types / AdsBot:** **8%** (Ad landing page verification and auxiliary crawlers).

---

## 6. The 29 404 URLs: Comprehensive Grouping & Root Causes

The 139 crawl attempts across 29 distinct URLs break down into four distinct structural sources:

### Category 1: Missing Chatbot Assets (Now 100% Fixed Live)
* `https://aitoolgems.tech/chatbot/widget.css?v=2` (2 requests — 12/11/2026)
* `https://aitoolgems.tech/chatbot/widget.js?v=2` (2 requests — 12/11/2026)
* **Root Cause:** `attribution.js` dynamically appended these tags, but the GitHub Pages deploy build script (`scripts/build_public_site.py`) previously excluded `chatbot/`.
* **Fix Status:** Fixed in PR #57 and PR #59. Live verified: Both return **HTTP 200 OK**.

### Category 2: Root & Platform Probes
* `https://aitoolgems.tech/favicon.ico` (18 requests) — Root favicon exists; live verified **HTTP 200 OK**.
* `https://aitoolgems.tech/apple-app-site-association` (3 requests) — Automatic iOS universal links probe. Returning 404 is standard web behavior for non-app domains.
* `https://aitoolgems.tech/.well-known/apple-app-site-association` (2 requests) — Same as above.

### Category 3: Abandoned Japanese (`/jp/`) Stubs (65%+ of Crawl Waste)
* 19 distinct URLs (`/jp/tools/leonardo/`, `/jp/tools/veo/`, `/jp/tools/gemini/`, `/jp/tool-page.css`, `/jp/tools/netflix/`, etc.).
* **Root Cause:** In late October, experimental Japanese URLs were deleted. Because Googlebot had indexed some and users had clicked on them (e.g. 1 click on `/jp/tools/gemini/`), Googlebot's 90% Refresh loop kept checking them.
* **Fix Status:** 404 is the official RFC status code signaling permanent removal. Crawl attempts on `/jp/` have decreased by 80% between October and November and will drop completely off the queue.

### Category 4: Subdirectory Relative Asset Traps & Old Typos
* `/guides/assets/brand-logo-light.webp` (4 requests — Last: 07/11/2026)
* `/prices/assets/brand-logo-light.png` (1 request — Last: 17/10/2026)
* `/tools/resemble ai/` (1 request — 05/10/2026)
* `/terms.html` & `/policies/` (1 request each)
* **Root Cause:** Relative `src="assets/..."` paths in older guide templates resolved relative to `/guides/` instead of apex root `/assets/`.
* **Fix Status:** All active templates in the current repository use strict normalized paths (`../../assets/...` or `/assets/...`). Live link graph checker confirms **0 broken links**.
