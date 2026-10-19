# AI Tool Gems — Master Implementation Plan (Phases 1–7)

**Governing Specification:** Prompt 0 — Shared Operating Rules  
**Repository:** [m-rehman55/ai-tool-gems](https://github.com/m-rehman55/ai-tool-gems)  
**Constraint:** Strict PKR 0 additional spend, zero fake claims, no unverified third-party dependencies.

---

## Phased Execution Roadmap

### Phase 1: Core Navigation, Clickability, Breadcrumbs, Orbit & Contrast
- **Dependencies:** Phase 0 audit approval.
- **File & Component Areas:**
  - `tools/*/index.html` (all 20 tool detail pages)
  - `tool-page.css`
  - `light-theme.css`, `styles.css`
  - `index.html` (hero section lines 2120–2155, payment strip lines 2160–2200)
  - `app.js` (tag click handlers)
- **Scoped Tasks:**
  1. Breadcrumb repair across all 20 detail pages: wrap `Home` in `<a href="../../">Home</a>` with focus/contrast styling.
  2. Contrast remediation: add explicit high-contrast overrides in `light-theme.css` for `.float-card span`, `.stack-item span`, `.finder-preview > p`, and `.price-block strong`.
  3. Hero orbit accessibility: add accessible labels and navigation targets to `.float-card` and `.orbit-node`.
  4. Card feature tags: make `.tags span` clickable to filter products by query/intent.
- **Intended Tests:**
  - `python -m unittest discover -s tests -v`
  - Browser computed contrast check for WCAG AA compliance (>4.5:1).
- **Rollback Approach:** Revert single Phase 1 Git commit (`git revert HEAD`).
- **Acceptance Checks:**
  - [ ] Every breadcrumb has a clickable `Home` anchor.
  - [ ] Zero white-on-white text in light mode.
  - [ ] All 96 baseline tests remain green.

---

### Phase 2: Product Catalog Reconciliation & Detail Routes
- **Dependencies:** Phase 1 complete; Owner confirmation on missing 12 tools in `OWNER_DECISIONS.md`.
- **File & Component Areas:**
  - `tools/` (create 12 missing directories and `index.html` pages)
  - `index.html` (`#productGrid` pre-rendered cards)
  - `app.js` (`STATIC_TOOL_PAGES` set and card links)
  - `sitemap.xml`, `sitemap.txt`
  - `tests/test_integrity_and_regressions.py`
- **Scoped Tasks:**
  1. Generate 12 missing static pages under `tools/<slug>/index.html` with accurate PKR prices, WhatsApp ordering, replacement warranties, and complete JSON-LD `Product` & `BreadcrumbList` schema.
  2. Pre-render all 32 cards directly inside `index.html` at `#productGrid`.
  3. Synchronize `sitemap.xml` and update route integrity tests.
- **Intended Tests:**
  - New test in `tests/test_integrity_and_regressions.py` validating that every tool in `app.js` has an existing `tools/<slug>/index.html` file.
  - `python schema_audit.py` to verify JSON-LD schema validity.
- **Rollback Approach:** Revert Phase 2 commit and remove newly generated static tool folders.
- **Acceptance Checks:**
  - [ ] Exactly 32 tool pages exist and return HTTP 200.
  - [ ] `#productGrid` has zero blank renders with JS disabled.
  - [ ] Schema audit scores 100%.

---

### Phase 3: "Tools for Every Ambition" & Guided Finder
- **Dependencies:** Phase 2 complete.
- **File & Component Areas:**
  - `index.html` (lines 3094–3130)
  - `app.js` (finder functions & preview handlers)
  - `light-theme.css`
- **Scoped Tasks:**
  1. Pre-render all 11 category cards statically in `<div id="categoryGrid">` with accessible links.
  2. Connect `#finderMatchCard` to direct URLs (`tools/<slug>/`) instead of modal-only triggers.
  3. Ensure modal keyboard traps, Escape-key listeners, and focus management work reliably.
- **Intended Tests:**
  - Playwright/DOM test checking that `#categoryGrid` is non-empty before JS executes.
  - Keydown event testing for Escape key on modals.
- **Rollback Approach:** Revert Phase 3 commit.
- **Acceptance Checks:**
  - [ ] Category grid is populated in raw HTML.
  - [ ] Finder match card links directly to valid tool route.

---

### Phase 4: Truthful Local & International Payment Experience
- **Dependencies:** Phase 1 & 3 complete; Owner confirmation on international payment handling in `OWNER_DECISIONS.md`.
- **File & Component Areas:**
  - `index.html` (lines 2158–2200)
  - `tools/*/index.html`
  - `policies.html`, `how-we-price.html`
- **Scoped Tasks:**
  1. Update payment trust strip with interactive info triggers explaining local Pakistani methods (EasyPaisa, JazzCash, SadaPay, NayaPay, Raast, Bank IBFT).
  2. Add honest international customer guidance (Bank Wire Transfer, Wise, direct WhatsApp support assistance) without fake automated gateway promises.
- **Intended Tests:**
  - `test_scope_guard.py` updated to permit approved international explanation copy while enforcing PKR/local payment integrity on Pakistani transactional pages.
- **Rollback Approach:** Revert Phase 4 commit.
- **Acceptance Checks:**
  - [ ] No fake payment buttons or unverified claims.
  - [ ] Clear customer instructions for both Pakistani and international visitors.

---

### Phase 5: Technical SEO, International SEO, AEO/GEO Readiness
- **Dependencies:** Phases 1–4 complete.
- **File & Component Areas:**
  - `robots.txt`, `llms.txt`, `llms-full.txt`
  - `AGENTS.md` (policy updates)
  - All static HTML pages (meta tags, hreflang/locale tags, canonicals)
- **Scoped Tasks:**
  1. Add AEO/GEO direct-answer structured snippets to all new tool pages.
  2. Verify robots allowlist, sitemap references, and LLM text exports.
  3. Harmonize `AGENTS.md` to reflect realistic local-and-international business model.
- **Intended Tests:**
  - `python -m keyword_agent audit`
  - `python -m seo-agent.agent.main --mode audit --report`
- **Rollback Approach:** Revert Phase 5 commit.
- **Acceptance Checks:**
  - [ ] SEO audit technical score: 100/100.
  - [ ] 0 canonical, robots, or sitemap collisions.

---

## Phase 6: Link Graph Validation & Automated Regression Suite
- **Dependencies:** Phases 1–5 complete.
- **File & Component Areas:**
  - `guides/*.html` (fix 30 broken TOC fragments)
  - `index.html` (fix 3 empty hrefs)
  - `tests/test_integrity_and_regressions.py`
- **Scoped Tasks:**
  1. Fix 30 mismatched heading IDs in `guides/` articles so Table of Contents jump links work smoothly.
  2. Eliminate all `href="#"` instances.
  3. Add automated link-graph crawler to the CI test suite.
- **Intended Tests:**
  - `python -m unittest discover -s tests -v`
  - Link graph verification script checking for 0 broken internal links and 0 broken fragments.
- **Rollback Approach:** Revert Phase 6 commit.
- **Acceptance Checks:**
  - [ ] Broken fragments count = 0.
  - [ ] Empty href count = 0.

---

## Phase 7: Cross-Device QA, Diff Review & Release
- **Dependencies:** All previous phases complete.
- **File & Component Areas:**
  - End-to-end repository review, `CHANGELOG.md`, git commit.
- **Scoped Tasks:**
  1. Full cross-viewport visual check (Mobile 375px, Tablet 768px, Desktop 1440px).
  2. Final check of `git diff` to ensure zero secrets, zero regressions, and zero unrelated changes.
  3. Deploy to production via GitHub Actions and verify live URL `https://aitoolgems.tech/`.
- **Intended Tests:**
  - Run all 4 test suites: 100+ tests passing.
  - Live HTTP status code and response payload verification.
- **Rollback Approach:** Fast revert of production commit via Git.
- **Acceptance Checks:**
  - [ ] 100% of acceptance criteria across Phases 1–7 verified.
  - [ ] Live site operational with verified cards, breadcrumbs, contrast, and routes.
