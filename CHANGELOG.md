# AI Tool Gems — Changelog

All notable changes to the AI Tool Gems platform are documented in this file in reverse chronological order.
Governing Specification: Prompt 0 — Shared Operating Rules.

## [Phase 5] - 2026-10-19 — Global Positioning, Guardrails Modernization & Technical SEO / AEO / GEO
### Fixed & Generated
- **Speed Claim Remediation & Activation Transparency (`a0df742`):**
  - Replaced "immediate activation" in `index.html` line 3749 with truthful wording: "activation after payment and availability confirmation via WhatsApp".
  - Eliminated specific unsubstantiated minute speed claims from all customer proof captions:
    - Replaced `in 2 minutes` with `upon receipt verification` and `upon confirmation`.
    - Replaced `in 3–5 minutes` with `after payment confirmation`.
    - Replaced `in 5 minutes` with `after receipt confirmation via WhatsApp`.
  - Added strict regression coverage in `tests/test_integrity_and_regressions.py` testing for negative absence of `immediate activation`, `in 2 minutes`, `in 3–5 minutes`, and `in 5 minutes`, and asserting presence of the confirmation wording.
- **Global Positioning & Agent Guardrails Harmonization:**
  - Modernized `AGENTS.md` to remove obsolete "100% Pakistan-exclusive" phrasing while preserving authentic domestic focus:
    - Established Pakistan as the Primary Core Market (authoritative PKR pricing, verified local wallets EasyPaisa/JazzCash/SadaPay/Raast/IBFT).
    - Established International as Inquiry & Content Access (manual WhatsApp routing, custom Wise/IBFT quotes, no fake automated gateways or currency switchers).
    - Updated Safety section to prohibit fabricating foreign local payment rails or fake country offices.
  - Recorded Decisions 8 & 9 in `OWNER_DECISIONS.md` establishing policies on currency display (no fake switchers) and language versioning (canonical `en-PK` without fake `hreflang` alternate links).
- **Technical SEO, Schema & AEO/GEO Verification:**
  - Confirmed 71 canonical indexable URLs in `sitemap.xml` with zero admin or private URLs.
  - Verified `robots.txt` disallows private paths while explicitly granting access to beneficial AI crawlers (`GPTBot`, `ClaudeBot`, `PerplexityBot`, `Google-Extended`).
  - Ran `schema_audit.py`: 74/74 pages pass with 100.0% schema completeness.
  - Ran `audit_all.py`: 74/74 HTML files clean with 0 errors and 0 warnings.
  - Ran `marketing_agent seo-monitor`: scored 100/100 across 70 verified URLs with 8 AEO answer blocks and 0 issues.
  - Ran `keyword_agent audit`: compiled 11 RE2-compliant GSC filters, mapped 42 keywords with 0 route collisions.

### Verification
- 99/99 tests passed across all 4 suites:
  - `tests`: 8/8 passed
  - `keyword_agent`: 15/15 passed
  - `seo-agent`: 43/43 passed
  - `marketing_agent`: 33/33 passed
- `schema_audit.py`: 74/74 pages passed (100% score)
- `audit_all.py`: 74/74 HTML files clean (0 errors, 0 warnings)
- `seo-monitor`: 100/100 score (0 issues)

---

## [Phase 4] - 2026-10-19 — Payment Transparency, Policy Section & Contact Protection
### Fixed & Generated
- **Dedicated Payments Section in `policies.html` (`#payments`):**
  - Added `<section class="page-section" id="payments">` providing complete transparency on manual WhatsApp payment verification, order confirmation, and delivery processes.
  - Formatted a responsive comparison table classifying payment rails into 3 truthful tiers:
    - *Verified & Configured (Local Pakistan):* EasyPaisa, JazzCash, SadaPay, NayaPay, Raast, and Local Bank IBFT (Meezan, HBL, Bank Alfalah, etc.).
    - *Contact Owner / Inquiry-Only (International):* Wise, Bank Wire (SWIFT). Handled manually on inquiry with quotes per request.
    - *Unsupported / Unavailable:* PayPal (does not operate for direct receiving in Pakistan) and automated credit/debit card gateway checkout.
  - Added anti-fraud and security disclosure: no stored cards, no automated debits, and a clear warning that AI Tool Gems will never ask for ATM PINs, CVVs, or OTP codes.
  - Linked all 32 canonical product detail pages directly to `policies.html#payments`.
- **Accessible Responsive Payment Disclosure in `index.html`:**
  - Replaced the static payment trust strip with an accessible `<details class="payment-disclosure" id="paymentMethodsDisclosure" open>` component.
  - Replaced unsupported claims ("100% Verified Local Payments" and "Instant Guaranteed Activation") with honest, transparent copy: "Local Payments (Pakistan) & International Inquiries" and "Manual WhatsApp Verification".
  - Structured 3 card categories with distinct status badges (`verified`, `inquiry`, `unsupported`).
  - Added direct link to `policies.html#payments`.
  - Added responsive light-theme styling in `light-theme.css` and toggle handler in `app.js`.
- **Contact Number Protection:**
  - Redacted unconfirmed private account number `03476242709` from public proof card in `index.html` (line 3853), protecting owner contact details and preventing impersonation.
  - Preserved verified operational business number `923236715731` across all order buttons.
- **Regression Testing:**
  - Added `test_phase4_payment_transparency_and_policy_integrity` in `tests/test_integrity_and_regressions.py` verifying `#payments` fragment resolution, classification wording, absence of fake checkout scripts, and contact protection.

- **Production Verification Remediation & Secondary Copy Clean-up (`fa978a5`):**
  - Thoroughly audited all visible homepage sections and eliminated remaining instances of unsupported claims:
    - Replaced `100% Real Customer`, `100% Genuine Pakistani Buyer`, `Instant Dispatch`, `Instant Account Delivery`, `2–15 Minute WhatsApp Activation` with truthful terminology: `Verified Customer`, `Genuine Pakistani Buyer`, `Verified Dispatch`, `Verified Account Delivery`, and `Estimated 15–30 Minute Fulfillment`.
    - In the comparison table, replaced `Feature / Guarantee`, `100% Flat PKR Pricing`, `100% Private Workspaces`, `Fast 2 to 15 Minutes WhatsApp Activation` with `Marketplace Standards & Terms`, `Transparent Flat PKR Pricing`, `Private Workspaces`, and `Prompt WhatsApp Verification & Delivery`.
    - Removed `100% PAKISTAN MARKET` and `instant WhatsApp activation` from `tools/index.html`.
    - Replaced `guaranteed delivery within 15 to 30 minutes` with `estimated delivery within 15 to 30 minutes` across all 5 affected guide articles (`best-ai-video-generators-pakistan`, `elevenlabs-voice-ai-pakistan`, `lovable-vs-replit-pakistan`, `midjourney-alternatives-pakistan`, `n8n-automation-pakistan`).
    - Verified complete redaction of legacy number `03476242709` across all HTML files in the repository.
    - Updated `tests/test_integrity_and_regressions.py` with comprehensive assertions covering all remaining claims and recursive scan for `03476242709`.
    - Monitored GitHub Pages deployment (`39277105966`) and independently validated live production site (`https://aitoolgems.tech/`) confirming `paymentMethodsDisclosure` is live, legacy claims/number are gone, and `policies.html#payments` resolves cleanly.

### Verification
- 99/99 tests passed across all 4 suites:
  - `tests`: 8/8 passed
  - `keyword_agent`: 15/15 passed
  - `seo-agent`: 43/43 passed
  - `marketing_agent`: 33/33 passed
- `schema_audit.py`: 74/74 pages passed (100% score)
- `audit_all.py`: 74/74 HTML files clean (0 errors, 0 warnings)
- Live production check: HTTP 200, ETag verified, 100% passing checks.

---

## [Phase 3] - 2026-10-19 — Categories Pre-Rendering, Guided Finder & Anchor Resolution
### Fixed & Generated
- **Pre-rendered 11 Verified Categories in `index.html`:**
  - Injected all 11 ambition categories into `<div class="category-grid" id="categoryGrid">` as semantic `<a href="#products" class="category-card" data-category="...">` elements with accurate tool counts and visuals.
  - Enabled native non-JavaScript navigation to `#products` while preserving interactive JavaScript category filtering.
  - Added anchor text-decoration reset and accessible `:focus-visible` styles in `light-theme.css`.
- **Guided Finder Routing & Intent Matching:**
  - Updated Guided Finder Step 3 recommendation cards to direct anchor links `<a class="finder-result" href="tools/${p.id}/">` pointing directly to canonical first-party tool pages.
  - Normalized singular/plural intent matching in `app.js` so goals like "Generate Visuals & Art" (`image`) accurately include tools with plural tags (`images`, e.g. Midjourney).
  - Updated homepage `#finderMatchCard` to link directly to canonical tool routes (`tools/veo/`) with dynamic href updates.
  - Added honest, transparent no-results state without fabricating products.
  - Added URL parameter deep-linking support (`?category=...`, `?q=...`, `?find=...`, `#finderModal`).
- **33 Broken & Placeholder Anchor Links Cleaned:**
  - Replaced 3 placeholder `href="#"` links on WhatsApp buttons in `index.html` with verified business URL (`https://wa.me/923236715731?text=...`).
  - Fixed 30 broken Table-of-Contents jump links across 3 guide articles (`guides/ai-tools-price-pakistan/`, `guides/canva-vs-figma-pakistan/`, `guides/chatgpt-vs-gemini-pakistan/`) by mapping verbose slug fragments to actual heading IDs.
- **Regression Testing:**
  - Added `test_phase3_category_prerendering_and_anchor_integrity` in `tests/test_integrity_and_regressions.py` covering category rendering, zero `href="#"`, finder links, and TOC anchor resolution.

### Verification
- 98/98 tests passed across all 4 suites:
  - `tests`: 7/7 passed
  - `keyword_agent`: 15/15 passed
  - `seo-agent`: 43/43 passed
  - `marketing_agent`: 33/33 passed
- `schema_audit.py`: 74/74 pages passed (100% score)
- `audit_all.py`: 74/74 HTML files clean (0 errors, 0 warnings)

---

## [Phase 2] - 2026-10-19 — Product Catalog Reconciliation (12 Missing Pages & Static Grid)
### Fixed & Generated
- **12 Missing Product Detail Pages Created:**
  - Generated standalone canonical detail pages under `tools/<slug>/index.html` for all 12 missing catalog items:
    - `claude` (Anthropic Claude Pro - Rs. 1,400)
    - `midjourney` (Midjourney Standard - Rs. 2,800)
    - `cursor` (Cursor Pro - Rs. 2,200)
    - `perplexity` (Perplexity Pro - Rs. 1,600)
    - `deepseek` (DeepSeek V3 / R1 - Rs. 1,200)
    - `grok` (Grok 2 / X Premium - Rs. 1,800)
    - `runway` (Runway Gen-3 Alpha - Rs. 2,600)
    - `heygen` (HeyGen Creator - Rs. 3,500)
    - `grammarly` (Grammarly Premium - Rs. 650)
    - `quillbot` (QuillBot Premium - Rs. 550)
    - `semrush` (Semrush Guru - Rs. 1,450)
    - `allinone` (All-in-One Mega Suite - Rs. 3,800)
  - All 12 pages include complete schema markup (`Product`, `BreadcrumbList`, `FAQPage`, `WebPage`), OpenGraph/Twitter cards, Pakistani payment methods, 7-day replacement warranty badges, verified WhatsApp direct-order CTAs, and internal links.
- **Pre-rendered 32 Product Cards in Homepage `#productGrid`:**
  - Injected all 32 products into `index.html` as static semantic HTML, completely preventing white-space rendering bugs caused by client-side script delays or lazy observers.
  - Updated price table rows in `index.html` to link directly to verified canonical routes (`tools/<id>/`).
  - Updated catalog directory list in `index.html` footer to list and link all 32 tools.
  - Updated `STATIC_TOOL_PAGES` Set in `app.js` with all 32 IDs.
- **Sitemap & SEO Synchronization:**
  - Synchronized `sitemap.xml` to include all 32 verified canonical detail routes (`https://aitoolgems.tech/tools/<slug>/`), bringing verified sitemap entries to 70 URLs.
  - Synchronized `sitemap.txt` to include all 32 tool URLs (46 URLs total).
- **Schema Audit Remediation:**
  - Repaired JSON-LD quotation syntax error in `tools/chatgpt/index.html`.
  - Achieved 100% (3,675 / 3,675) schema pass score across all 74 HTML files in repository.
- **Regression Tests Added:**
  - Updated `tests/test_integrity_and_regressions.py` to assert all 32 catalog tools exist on disk, have valid static routes, and conform to breadcrumb standards.

### Verification
- 97/97 tests passed across all 4 test suites:
  - `tests`: 6/6 passed
  - `keyword_agent`: 15/15 passed
  - `seo-agent`: 43/43 passed
  - `marketing_agent`: 33/33 passed
- `schema_audit.py`: 74/74 pages passed (100% score)
- `audit_all.py`: 74/74 HTML files clean (0 errors, 0 warnings)

---

## [Phase 1] - 2026-10-19 — Core Navigation, Breadcrumbs, Orbit, Cards & Contrast
### Fixed & Improved
- **Breadcrumb Navigation across all 20 Tool Pages:**
  - Added clickable `<a href="../../">Home</a>` and `<a href="../../tools/">AI tools</a>` breadcrumb links with `aria-current="page"` on current tool across all 20 static detail pages (`tools/*/index.html`).
  - Added rich contrast, focus-visible outline, and hover styles in `tool-page.css`.
- **White-on-White Contrast Remediation:**
  - Added explicit high-contrast overrides in `light-theme.css` for `.float-card span`, `.float-card small`, `.stack-item span`, `.finder-preview > p`, `.match-card span/strong`, and `.price-block strong` (ensuring WCAG AA compliance with dark green `#153f37`).
- **Hero Orbit & Floating Cards:**
  - Converted hero float cards (`float-chatgpt`, `float-canva`, `float-capcut`, `float-figma`) to semantic anchor links (`<a>`) pointing directly to their product pages with clear `aria-label` and `title` tags.
  - Marked decorative orbit floating nodes with `aria-hidden="true"`.
- **Card Feature Tags Clickability:**
  - Converted plain `<span>` tags on `#productGrid` cards into interactive `<button type="button" class="tag-chip">` elements in both `app.js` and pre-rendered `index.html`.
  - Added event delegation in `app.js` enabling instant tag filtering with active filter pills and clear button.
- **Internal Linking Across All 20 Detail Pages (Owner Directive):**
  - Updated "Why Choose AI Tool Gems?" box in all 20 pages with active links to payment policies (`policies.html#payments`), warranty protection (`policies.html#warranty`), access tiers (`policies.html#access`), and contact desk (`contact.html`).
  - Enriched Key Features and FAQs with links to warranty documentation.
  - Converted unlinked plain text in "Alternatives" sections to active links across the catalog.

### Verification
- 96/96 tests passed across all 4 suites (`tests`, `keyword_agent`, `seo-agent`, `marketing_agent`).

---

## [Phase 0] - 2026-10-19 — Baseline Audit & Master Planning

### Added
- Created `AUDIT.md` providing comprehensive evidence-based analysis:
  - 96 baseline tests executed across 4 test suites (5 root + 15 keyword_agent + 43 seo-agent + 33 marketing_agent) with 100% pass rate.
  - Reconciled catalog counts: verified 32 advertised tools in `app.js` vs 20 static detail directories in `tools/` (12 missing detail routes identified).
  - Isolated root cause of missing cards in `#productGrid` between price table and bundle builder (dependency on client-side JS and lazy IntersectionObserver).
  - Identified white-on-white contrast failures: `.float-card span`, `.stack-item span`, `.finder-preview > p`, and `.price-block strong` caused by high-specificity `styles.css` rules not overridden in `light-theme.css`.
  - Identified breadcrumb broken link in `tools/*/index.html`: `Home` plain text without `<a>` link.
  - Scanned full link graph across 62 HTML files: 0 broken relative links, 3 empty hrefs, 30 broken TOC fragments in `guides/`.
- Created `IMPLEMENTATION_PLAN.md` outlining scoped tasks for Phases 1 through 7.
- Created `OWNER_DECISIONS.md` highlighting key business and operational decisions requiring owner confirmation (missing 12 detail pages, international payments, WhatsApp number, grid pagination).

### Verification
- Ran baseline test suite: 96 tests passed in 5.97s.
- Zero application code files modified in Phase 0.
