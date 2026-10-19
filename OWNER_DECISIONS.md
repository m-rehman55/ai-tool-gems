# AI Tool Gems — Owner Decision Log (Phase 0)

**Governing Standard:** Prompt 0 — Shared Operating Rules  
**Date:** 2026-10-19  
**Status:** Open for Store Owner Confirmation  
**Note:** For each decision below, a **Safe Default Behavior** is defined and active so progress is never blocked while awaiting owner choices.

---

### Decision 1: Catalog Scope & Missing 12 Tool Detail Pages
- **Context:** The catalog in `app.js` advertises 32 products, but only 20 have standalone static pages under `tools/<slug>/index.html`. The 12 missing tools are:
  `claude`, `midjourney`, `cursor`, `perplexity`, `deepseek`, `grok`, `runway`, `heygen`, `grammarly`, `quillbot`, `semrush`, and `allinone`.
- **Options:**
  - **Option A (Recommended):** Build full static detail pages for all 12 tools following the established standard (`tools/<slug>/index.html`), complete with truthful PKR prices, replacement warranties, WhatsApp order links, and JSON-LD structured data.
  - **Option B:** Keep them modal-only on the homepage and exclude from the sitemap.
- **Safe Default While Pending:** Build full static pages for all 12 tools in Phase 2 so that no advertised product results in a dead route or un-indexable experience.

---

### Decision 2: Supported Payment Methods (Local & International)
- **Context:** The site currently highlights Pakistani local wallets (EasyPaisa, JazzCash, SadaPay, NayaPay, Raast, Bank IBFT). For international customers, automated checkout does not exist.
- **Rule:** Never fabricate automated payment gateways (e.g. fake Stripe/PayPal checkout) without verified merchant credentials.
- **Options:**
  - **Option A (Recommended):** Display verified local Pakistani payment badges, plus an explicit notice: *"International orders welcomed via Bank Wire Transfer (IBFT/SWIFT), Wise, or WhatsApp support."*
  - **Option B:** Restrict sales exclusively to Pakistan and add a notice explaining that international transactions are not currently supported.
- **Safe Default While Pending:** Maintain all verified Pakistani local badges and add contact-based international guidance via WhatsApp support.

---

### Decision 3: Use of WhatsApp Number `03476242709` (`LEGACY_WA_NUMBER`)
- **Context:** Two WhatsApp numbers exist in `app.js`:
  1. Primary: `923236715731` (`DEFAULT_WA_NUMBER` / `+92 323 6715731`)
  2. Legacy: `923476242709` (`LEGACY_WA_NUMBER` / `0347 6242709`)
- **Options:**
  - **Option A (Recommended):** Use `+92 323 6715731` as the primary operational WhatsApp number across all "Buy now", "Order", and "Support" buttons, and retain `0347 6242709` as a secondary backup or emergency support line on the `/contact.html` page.
  - **Option B:** Swap and use `0347 6242709` as the primary number.
  - **Option C:** Remove `0347 6242709` entirely if no longer active.
- **Safe Default While Pending:** Use `923236715731` on all order links; list `0347 6242709` as secondary customer care on `contact.html`.

---

### Decision 4: Supported Language Versions & Locales
- **Context:** The website is currently written in English (`en-PK`) with Roman Urdu search intent keywords and localized product descriptions in certain guide sections.
- **Options:**
  - **Option A (Recommended):** Keep primary site in English with Roman Urdu search terms, and retain `lang="en-PK"` as primary canonical locale.
  - **Option B:** Add a dedicated Urdu script section (`ur-PK`) or toggle.
- **Safe Default While Pending:** Maintain `en-PK` as primary language with natural bilingual search terminology.

---

### Decision 5: Official Currencies
- **Context:** All catalog prices are currently listed in Pakistani Rupees (`PKR` / `Rs.`).
- **Options:**
  - **Option A (Recommended):** Keep PKR as the primary base currency on all product pages, and display an approximate USD estimate (e.g. `~$8 USD`) for international visitors.
  - **Option B:** Keep 100% pure PKR pricing only without currency conversion.
- **Safe Default While Pending:** Display authoritative PKR pricing everywhere; convert dynamically on WhatsApp for international buyers upon request.

---


### Decision 6: AI Crawlers & Search Engine Access (`robots.txt`)
- **Context:** AI crawlers (`GPTBot`, `PerplexityBot`, `ClaudeBot`, `Google-Extended`, etc.) frequently crawl the site for LLM search indexing and Answer Engine Optimization (AEO/GEO).
- **Options:**
  - **Option A (Recommended):** Allow verified AI search crawlers (`GPTBot`, `PerplexityBot`, `ClaudeBot`, `GoogleOther`) to index public product pages to maximize GEO/AEO visibility.
  - **Option B:** Disallow all non-Google AI crawlers in `robots.txt`.
- **Safe Default While Pending:** Allow all standard AI search crawlers on public catalog pages while strictly blocking administrative, test, and private paths.

---

### Decision 7: Functional Internal Linking Across All Tool Detail Pages
- **Owner Directive (Confirmed):** "just leonardo ai nahi balky sb tools ky pages ky 7 yahi kro okay."
- **Scope:** Across all current and new tool detail pages (`tools/*/index.html`), ensure that:
  1. Breadcrumbs have a clickable `Home` link and valid `AI tools` link.
  2. The "Key Features" section includes contextual links to relevant use-case guides or related categories.
  3. The "Who Should Use This Tool" section includes links to target workflows (e.g. students, designers, coders).
  4. The "Frequently Asked Questions" section provides clear, actionable answers with links to policies, warranties, or WhatsApp support.
  5. The "Alternatives" and "Compare related tools" sections link directly to active static pages in the catalog (e.g. `../midjourney/`, `../canva/`, `../veo/`) rather than dead plain text.
- **Status:** **CONFIRMED BY OWNER** (Targeted for implementation across Phase 1 and Phase 2).


