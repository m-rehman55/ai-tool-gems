# AIToolGems — Global Tools Expansion Master Blueprint & Workspace Handover

## 1. Project Overview & Current Architecture
* **Website:** AIToolGems (`https://aitoolgems.tech/`)
* **Repository:** `https://github.com/m-rehman55/ai-tool-gems/` (Branch: `main`)
* **Current Catalog:** 32 verified tools live (79 HTML pages, 100% schema completeness, 0 link graph errors).
* **Strategic Pivot:** Evolving from a Pakistan-only domestic marketplace (`PKR`) into a **Global / Worldwide Multi-Currency Platform (`USD $` + `PKR Rs`)** accepting Crypto (USDT TRC20/BEP20), Cards/Wise, alongside domestic rails (EasyPaisa, JazzCash, SadaPay).
* **Source Raw Data:** `D:\Desktop\reseller_products_2026-10-22.csv` (2,902 raw supplier listings from 10 Telegram reseller bots).
  * Filtered: 1,133 duplicate bot rows of existing 32 tools removed.
  * Filtered: 170 farmed emails/throwaway spam accounts blacklisted.
  * Result: **~48 genuine new global tools discovered**.

---

## 2. Phase 1: Top 8 Priority Tools to Launch First

| Tool Name | Category | CSV Wholesale (USDT) | Retail Price (USD) | Retail Price (PKR) | Net Profit Margin | Target Slug |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **TradingView Pro** | Finance / Trading | $3.50 | **$14.99** | **Rs. 3,500** | ~330% | `tools/tradingview/` |
| **Kling AI** | AI Video Creation | $6.00 | **$19.99** | **Rs. 4,800** | ~230% | `tools/kling/` |
| **Freepik Premium** | Graphic Design | $3.00 | **$9.99** | **Rs. 2,400** | ~230% | `tools/freepik/` |
| **Spotify Premium** | Audio & Streaming | $1.50 | **$5.99** | **Rs. 1,200** | ~300% | `tools/spotify/` |
| **GitHub Copilot** | Developer & AI Code | $2.50 | **$9.99** | **Rs. 2,500** | ~300% | `tools/copilot/` |
| **Suno AI** | AI Music Creation | $4.00 | **$12.99** | **Rs. 3,200** | ~225% | `tools/suno/` |
| **Turnitin (Student/Instructor)** | Academic Research | $3.50 | **$14.99** | **Rs. 3,600** | ~330% | `tools/turnitin/` |
| **Microsoft Office 365 (1TB)** | Productivity & Cloud | $2.00 | **$8.99** | **Rs. 2,200** | ~350% | `tools/office365/` |

---

## 3. Phase 2: Next 8 Follow-up Tools (Queued)
1. **Discord Nitro** (Gamer & Web3 Community)
2. **Telegram Premium** (File Sharing & Voice Transcription)
3. **Hailuo AI / MiniMax** (Ultra-Realistic Motion AI Video)
4. **Duolingo Super** (Global #1 Language Learning)
5. **Coursera Plus / Udemy** (Professional Global Certifications)
6. **Envato Elements & Motion Array** (Video & Design Templates)
7. **ExpressVPN** (Global Tier-1 Privacy & VPN)
8. **Krea AI** (Real-Time Upscaling & AI Canvas)

---

## 4. Strict Technical & Google Compliance Rules (Do Not Violate)

1. **Zero Scaled Duplicate Spam:**
   * Never create multiple separate URLs for duration variants (e.g. do NOT create `chatgpt-1-day.html` and `chatgpt-1-month.html`).
   * Exactly **1 Canonical Landing Page per Tool** (`tools/{slug}/index.html`).
   * Different durations (1 Month, 3 Months, 1 Year) are handled as options/variants inside the same page via structured tables and schema `offers`.
2. **100% Local Asset Hosting (Googlebot Compliant):**
   * Never link to external `google.com/s2/favicons` (causes Googlebot robots.txt 403/blocked resource errors).
   * All logos must reside locally in `assets/product-logos/{slug}.png` (HTTP 200).
3. **Character Limits (Bing & Google SERP Optimization):**
   * `<title>` tag: Strictly between **50 and 65 characters**.
   * `<meta name="description">`: Strictly between **140 and 155 characters**.
   * Exactly **1 `<h1>` tag** per page.
   * Exactly **1 `<link rel="canonical">`** per page.
4. **Structured Data (JSON-LD Schemas):**
   * Every product page must include valid schemas: `Product`, `Offer` (with both USD and PKR pricing options), `AggregateRating`, `Review`, `BreadcrumbList`, and `FAQPage`.
5. **GEO / AEO Direct Answer Block:**
   * Every tool page must include a quick-answer summary answering: What is the tool, exact price, delivery time, and warranty, optimized for Perplexity, ChatGPT Search, and Gemini citations.

---

## 5. Site Integration Checklist For Each New Tool
When a new tool is built:
- [ ] Create `tools/{slug}/index.html` (800-1,200 words, responsive layout, full schemas).
- [ ] Add logo to `assets/product-logos/{slug}.png`.
- [ ] Add product card to `index.html` (Product grid & Category tabs).
- [ ] Add entry to `tools/index.html` (Master catalog directory).
- [ ] Add data entry into `app.js` (Catalog registry).
- [ ] Append URL to `sitemap.xml`.
- [ ] Update `llms.txt` and `llms-full.txt`.
- [ ] Run verification: `python scripts/link_graph_checker.py --strict`, `python audit_all.py`, `python schema_audit.py`.
- [ ] Commit, push to `main`, and dispatch IndexNow ping (`python scripts/submit_indexnow.py --all`).
