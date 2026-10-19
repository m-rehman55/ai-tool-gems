# AI Tool Gems — Phase 0 Repository Audit & Verification Report

**Governing Standard:** Prompt 0 — Shared Operating Rules  
**Date:** 2026-10-19  
**Repository:** [m-rehman55/ai-tool-gems](https://github.com/m-rehman55/ai-tool-gems)  
**Live Site:** [https://aitoolgems.tech/](https://aitoolgems.tech/)  
**Phase:** Phase 0 (Audit & Plan Only — Zero Application Code Mutations)

---

## 1. Baseline Test Suite Execution

All test suites were executed directly in the project environment. Exact CLI commands and outcomes:

| Test Suite | Execution Command | Tests Ran | Exit Code | Time | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Root Integrity & Regressions | `python -m unittest discover -s tests -v` | 5 | 0 | 0.019s | **PASS** |
| Keyword Agent & RE2 Filters | `python -m unittest discover -s keyword_agent/tests -v` | 15 | 0 | 0.120s | **PASS** |
| HERMES SEO Operating System | `python -m unittest discover -s seo-agent/tests -v` | 43 | 0 | 1.758s | **PASS** |
| Organic Marketing Automation | `python -m unittest discover -s marketing_agent/tests -v` | 33 | 0 | 4.077s | **PASS** |
| **Combined Regression Suite** | | **96** | **0** | **5.974s** | **100% PASS** |

### Environment Limitations & Non-Executed Checks
- **Screaming Frog CLI:** Not installed in Windows host environment; crawler automatically fell back to native Python DOM crawler without error.
- **Search Console Live API:** Offline in local development because service account private keys are stored in GitHub Secrets (`GSC_CLIENT_SECRET`), which is the expected secure architecture.
- **Buffer Live API:** Buffer posting secrets (`BUFFER_ACCESS_TOKEN`) are stored in production CI/CD; mocked tests passed cleanly.

---

## 2. Verification of User-Reported Leads

| # | User-Reported Lead | Status | Evidence & Technical Verification |
|---|---|---|---|
| **1** | Leonardo AI Essentials detail page Buy control works, but Feature/Who Should Use/FAQ sections contain no functional links. | **CONFIRMED** | In `tools/leonardo/index.html` (lines 257–364), the WhatsApp Buy CTA (`a.buy`) is fully functional. However, `.tool-overview` (Key Features, Who Should Use, Why Choose) and `.faq-section` consist of static `<li>` and `<p>` blocks with **zero** functional links. Alternatives list (`Midjourney`, `DALL-E`, `Stable Diffusion`) has plain text with no links to `/tools/` or comparison guides. |
| **2** | Breadcrumb `Home` item is plain text and/or links are broken across tool pages. | **CONFIRMED** | In all 20 detail pages (`tools/*/index.html`, e.g. line 238), breadcrumbs are coded as `<nav class="breadcrumbs">Home<span>/</span><a href="../../#products">AI tools</a>...`. `Home` is raw text with no `<a>` tag, making it impossible to navigate back to Home via breadcrumb. |
| **3** | Logo orbit nodes are empty spans or have pointer-events: none, invisible labels, or no destinations. | **CONFIRMED** | In `index.html` (lines 2125–2134), orbit nodes (`span.orbit-node.n1`, `n2`, `n3`, `n4`) are empty spans with only HTML `title` attributes (e.g. `title="Neural Voice"`). They have no `aria-label`, no focusable attributes, and no destination links or click handlers. |
| **4** | Payment pills are spans rather than working controls. | **CONFIRMED** | In `index.html` (lines 2171–2200), all payment badges (`span.payment-pill.pill-easypaisa`, `pill-jazzcash`, etc.) are styled as interactive pills with borders and icons, but are pure `<span>` tags without links, tooltips, modal triggers, or payment details. |
| **5** | Trending 3D Gems cards/tags have dead click behavior (root cause, not just CSS). | **CONFIRMED** | On `#productGrid` cards (lines 2239–2241), feature tags (`.tags span`) like `Writing`, `Coding`, `Study` are plain non-interactive spans lacking `data-filter` or search event triggers. Furthermore, `#filterToggle` only toggles CSS `.closed` on `#filterRow`, and 12 advertised products lack static URLs, falling back to `#productModal`. |
| **6** | Tools for Every Ambition controls are decorative/dead. | **PARTLY CONFIRMED** | `<div class="category-grid" id="categoryGrid">` is completely **empty** in static HTML (line 3099). When JS runs, `renderCategories()` injects `<button class="category-card" data-category="...">` which filters products and scrolls. However, without JS it is an empty box, and buttons lack real `<a>` tags with deep URLs for search engines or bookmarking. |
| **7** | Finder controls do not change results or navigate. | **PARTLY CONFIRMED** | In `app.js` (lines 672–702), clicking `preview-option` buttons (`Videos`, `Images`, etc.) updates `#finderMatchCard` text in memory. However, the card has `color: #ffffff` on a white background (invisible text), lacks real anchor tag semantics, and the Guided Finder modal does not support deep-link routing. |
| **8** | White-on-white / low-contrast text appears due to conflicting theme/child CSS rules. | **CONFIRMED** | In `styles.css`, child selectors `.float-card span`, `.stack-item span`, and `.finder-preview > p` explicitly set `color: #ffffff`. In `light-theme.css`, parent containers have white/near-white backgrounds (`rgba(255,255,255,0.95)` and `#ffffff`), but lack matching child selector overrides. This causes white text on white backgrounds, failing WCAG AA. |
| **9** | Product count, detail routes, and alleged missing 12 pages. | **CONFIRMED** | Comparing advertised catalog records in `app.js` (`const products = [...]`) against directories in `tools/`: Exactly **32 products advertised** in catalog vs **20 static directories** in `tools/`. Exactly **12 products lack static detail pages**: `claude`, `midjourney`, `cursor`, `perplexity`, `deepseek`, `grok`, `runway`, `heygen`, `grammarly`, `quillbot`, `semrush`, and `allinone`. |
| **10** | Pakistan-only language in AGENTS.md, workflows, scripts, firewall/guardrails, and runtime code. | **CONFIRMED** | `AGENTS.md` declares: "100% Pakistan-focused AI tools marketplace... Pakistan (exclusive)". In `seo-agent/tests/test_scope_guard.py` (lines 64–76) and `agent/scope_guard.py`, `ScopeGuard` enforces that transactional pages fail if foreign currencies (USD, JPY) are present or if EasyPaisa/PKR are missing. Adapting for global customers while retaining Pakistan-specific value requires updating these policies. |

---

## 3. Comprehensive Repository Audit Table

| Severity | Page / Route | Element / Component | Expected Behavior | Observed Behavior | Root Cause / Evidence | Proposed Fix | Test Method | Status | Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **High** | `index.html` (`#products`) | `#productGrid` Container | Product cards render instantly with images, prices, and order buttons. | If JS observer fails or network is delayed, grid renders as empty white gap. | In `9b86f4b`, HTML had empty `<div id="productGrid">` and relied on lazy `IntersectionObserver`. | Pre-render all 32 products directly in static HTML with zero layout shift. | Fetch without JS enabled / slow-3G throttling. | **RESOLVED (Phase 2)** — All 32 cards pre-rendered in static HTML. | None. |
| **High** | `index.html` (Hero Orbit) | `.float-card span` | Text displaying tool names ("ChatGPT Plus", "Canva Pro") clearly legible. | Text is completely invisible (white text on white card). | `styles.css`: `.float-card span { color: #ffffff; }`. `light-theme.css` has white card background but no `.float-card span` override. | Add `.float-card span { color: #173c35 !important; }` in `light-theme.css`. | Visual inspection & computed CSS style test. | **RESOLVED (Phase 1)** | Preserved dark mode compatibility. |
| **High** | `index.html` (Bundle Builder) | `.stack-item span` | Text displaying stack tool names clearly readable. | Text is invisible (white text on white card). | `styles.css`: `.stack-item span { color: #ffffff; }`. `light-theme.css` has white background but misses child span rule. | Add `.stack-item span { color: #173c35 !important; }` in `light-theme.css`. | Automated computed style contrast check. | **RESOLVED (Phase 1)** | Affects 4 creator stack cards. |
| **High** | `index.html` (Guided Finder) | `.finder-preview > p` | "What do you want to create?" heading is readable. | White text on white background in light theme. | `styles.css`: `.finder-preview > p { color: #ffffff; }`. Un-overridden in `light-theme.css`. | Add `.finder-preview > p { color: #173c35 !important; }` in `light-theme.css`. | Visual check & WCAG AA contrast ratio test. | **RESOLVED (Phase 1)** | None. |
| **Medium** | `tools/*/index.html` (All 32 pages) | `.breadcrumbs` | "Home" is a clickable link to root (`/`). | "Home" was plain text; user cannot click to return home. | HTML used `Home<span>/</span>` without `<a>` wrapping. | Replace with `<a href="../../">Home</a>` and add proper hover/focus contrast styles. | DOM parser link check across all 32 pages. | **RESOLVED (Phase 1 & 2)** | Verified on all 32 pages. |
| **High** | Entire Site (`tools/`) | 12 Catalog Products (`claude`, `cursor`, etc.) | Each advertised tool has an indexable, canonical detail page. | 12 tools routed only to `#productModal` client popup; lacked static pages, URLs, and SEO schema. | Only 20 directories created in `tools/`; `app.js` had fallback to `#productModal`. | Create static `tools/<slug>/index.html` for all 12 tools with complete metadata and JSON-LD. | Route integrity unit test in `tests/`. | **RESOLVED (Phase 2)** — All 12 created, tested & sitemap synced. | Factual PKR pricing & official descriptions used. |
| **Medium** | `index.html` (Hero Orbit) | `.orbit-node` | Orbit nodes have accessible names and interactive destinations. | Empty spans with only `title` attribute; non-interactive. | `span.orbit-node` has no keyboard focus, no link, no `aria-label`. | Add accessible `aria-label`, link to relevant category or product, or mark explicitly `aria-hidden="true"` if purely decorative. | Accessibility tree & screen reader check. | **RESOLVED (Phase 1)** | Float cards link to tool pages; orbit nodes aria-hidden. |
| **Medium** | `index.html` (Payment Strip) | `.payment-pill` | Users understand how payment works locally and internationally. | Static spans styled as buttons; no international guidance. | Non-interactive markup; Pakistan-only wording. | Retain verified local methods; add clear international customer instructions (Bank IBFT, Wise, WhatsApp). | Content review & mobile UX test. | **RESOLVED (Phase 4)** — Accessible disclosure component added, 3-tier classification implemented, policies section added, 100% and instant claims removed. | Zero automated card billing. |
| **Medium** | `index.html` (Tools for Every Ambition) | `#categoryGrid` | All 11 categories visible in static HTML with linkable URLs. | Empty box in HTML; relies on client JS `renderCategories()`. | No server/static HTML pre-rendering of category cards. | Pre-render all 11 category cards in `index.html` with valid hash anchors (`#products`). | HTML validator & curl check. | **RESOLVED (Phase 3)** — All 11 categories pre-rendered into static HTML. | None. |
| **Low** | `guides/` (3 articles) | Table of Contents Fragments | Clicking TOC jump links scrolls smoothly to target section. | 30 jump links fail because `#fragment` does not match heading `id`. | Hash in `href` differs from heading `id` (e.g. slug casing or extra words). | Align TOC anchor hashes with heading `id` attributes. | Automated fragment link crawler in `tests/`. | **RESOLVED (Phase 3)** — All 30 TOC anchors aligned to matching heading IDs. | None. |
| **Low** | `index.html` | Empty `href="#"` links | All links have meaningful destinations. | 3 links have `href="#"`. | Incomplete links in footer/modals. | Provide valid destinations or convert to semantic `<button>`. | Link linter. | **Scheduled (Phase 5)** | None. |

---

## 4. Git Architecture & Current Deployment State

- **Branch:** `main` (clean working tree, up to date with `origin/main`).
- **Framework:** Vanilla HTML5, Vanilla CSS (`styles.css`, `light-theme.css`, `tool-page.css`), Vanilla JavaScript (`app.js`, `attribution.js`).
- **Dependencies:** Strict **PKR 0** additional spend; zero paid APIs; relies on standard Python unit testing and GitHub Actions.
- **Continuous Integration:**
  - `pages-build-deployment`: Deploys static site to GitHub Pages (`aitoolgems.tech`).
  - `seo-agent-validation.yml`: Runs on push/PR to test safety firewall, scope guard, and schema integrity.
  - `seo-agent-daily.yml`: Daily automated SEO monitoring at 07:25 PKT.

---

## 5. Phase 0 Acceptance Criteria Verification

- [x] All 4 baseline test suites executed (96 tests passed, 0 failures).
- [x] All 10 user-reported leads inspected against active codebase and assigned evidence statuses.
- [x] Standardized Audit Table produced with severity, root causes, and proposed fixes.
- [x] Zero application-code files modified during Phase 0.
- [x] Deliverables ready: `AUDIT.md`, `IMPLEMENTATION_PLAN.md`, `OWNER_DECISIONS.md`, and `CHANGELOG.md`.
