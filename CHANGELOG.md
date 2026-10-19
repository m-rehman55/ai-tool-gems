# AI Tool Gems — Changelog

All notable changes to the AI Tool Gems platform are documented in this file in reverse chronological order.
Governing Specification: Prompt 0 — Shared Operating Rules.

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
