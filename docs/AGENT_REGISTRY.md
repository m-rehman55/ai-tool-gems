# HERMES AGENT REGISTRY & SUBSYSTEM AUDIT
**Date**: 2026-11-05  
**Audit Standard**: Empirical Verification (Code Inspection & Live Run)  

---

## 1. Executive Agent Matrix

| Agent | Current Code Location | Entry Point | Test Suite | Current Health |
| :--- | :--- | :--- | :--- | :--- |
| **HERMES-CEO** | `seo-agent/agent/orchestrator.py` | `python -m seo-agent.agent.main` | `seo-agent/tests/test_workflows.py` | ⚠️ DEFECTIVE: Live crawl checks only homepage; firewall not invoked; passes empty list to safety check. |
| **GSC Intelligence** | `keyword_agent/gsc_data.py`, `marketing_agent/search_apis.py` | `python -m keyword_agent audit` | `keyword_agent/tests/test_keyword_agent.py` | ⚠️ DEFECTIVE: `marketing_agent/search_apis.py` limits to 20 rows, lacks pagination loop, and lacks country: 'pak' filter. |
| **Technical SEO** | `seo-agent/agent/crawler.py`, `scripts/link_graph_checker.py` | `python scripts/link_graph_checker.py --strict` | `tests/test_link_graph.py` | ⚠️ DEFECTIVE: Live crawler only requests homepage URL; ignores entire link tree when live_crawl=True. |
| **Keyword & Intent** | `keyword_agent/discovery.py`, `keyword_agent/page_mapper.py` | `python -m keyword_agent competitor-gap` | `keyword_agent/tests/test_competitor_gap.py` | ✅ FUNCTIONAL: 25 unit tests passing; RE2 regex library active. |
| **Bing & IndexNow** | `ping_agent/dispatcher.py`, `scripts/submit_indexnow.py` | `python -m ping_agent ping --all` | `ping_agent/tests/test_ping_agent.py` | ⚠️ DEFECTIVE: `ping_agent/cli.py` sends all URLs from sitemap rather than diffing changed URLs. |
| **GA4 Conversion** | `attribution.js`, `marketing_agent/search_apis.py` | Client-side tracking / GA4 API | `tests/test_integrity_and_regressions.py` | ⚠️ DEFECTIVE: Broad CSS class selectors trigger `view_guide`, `view_comparison`, and `view_item` simultaneously on homepage. |
| **PostHog Behavioral**| NONE (Missing from codebase) | Missing | None | 🔴 CRITICAL DEFECT: PostHog library is not integrated or ingested in any template or script. |
| **PageSpeed & CWV** | Local benchmark JSONs only | Static files (`baseline-current-desktop.json`) | None | 🔴 CRITICAL DEFECT: No live PageSpeed Insights API or CrUX API client exists in the repository. |
| **GEO / AEO** | `aio_agent/extractability.py`, `aio_agent/grounding_scorer.py` | `python -m aio_agent audit` | `aio_agent/tests/test_aio_agent.py` | ⚠️ DEFECTIVE: GitHub workflow pushes directly to main without PR review. |
| **Editorial & Guide** | `scripts/auto_blog_publisher.py` | `python scripts/auto_blog_publisher.py` | `tests/test_auto_blog_publisher.py` | 🔴 CRITICAL DEFECT: Self-approves dynamic candidates (`approved_for_publishing: True`), publishes boilerplate on Gemini failure, pushes to main. |
| **Backlink Intelligence**| `scripts/diagnose_ahrefs.py` | Script only | None | ⚠️ DEFECTIVE: No automated backlink monitor; pending authorized Ahrefs/Semrush API keys. |
| **Competitor Intel** | `keyword_agent/competitor_gap.py` | `python -m keyword_agent competitor-gap` | `keyword_agent/tests/test_competitor_gap.py` | ✅ FUNCTIONAL: Monitors Top 10 Pakistan & regional competitors. |
| **Social Marketing** | `marketing_agent/cli.py` | `python -m marketing_agent daily-run` | `marketing_agent/tests/test_agent.py` | ⚠️ DEFECTIVE: Buffer token missing from `.env`; workflow lacks exponential backoff retry. |
| **Merchant Center** | NONE (Missing from codebase) | Missing | None | 🔴 CRITICAL DEFECT: No Google Merchant Center feed generator or API integration exists. |
| **Conversion Journey**| `app.js`, `policies.html`, `how-we-price.html` | Client-side modal / WhatsApp link generator | `tests/test_ui_interactions.py` | ⚠️ DEFECTIVE: Header still displays `WORLDWIDE & PK` instead of strictly localized Pakistan fortress positioning. |
| **Security & Firewall**| `seo-agent/agent/scope_guard.py`, `seo-agent/agent/safety_firewall.py` | `seo-agent/agent/safety_firewall.py` | `seo-agent/tests/test_scope_guard.py` | ⚠️ DEFECTIVE: Safety firewall is bypassed in orchestrator Step 7; empty list passed to immutability verifier. |

---

## 2. In-Depth Defect Breakdown

### Defect 1 & 2: Homepage Metadata & Pakistan Commercial Focus
- **File**: `index.html` (lines 5-15, 75-80)
- **Problem**: Title `Buy Cheap AI Tools & Subscriptions Worldwide (PKR/USD)` and H1 `Affordable AI Tools Worldwide. Subscriptions in USD & PKR.` violate Section 1 (exclusive active commercial market: Pakistan).
- **Required Fix**: Change Title, Meta Description, H1, and hero text to reflect Pakistan AI subscription marketplace, flat PKR pricing, and domestic rails (EasyPaisa/JazzCash).

### Defect 3: Scope Guard Missing Enforcement on Transactional Pages
- **File**: `seo-agent/agent/scope_guard.py`, `seo-agent/agent/orchestrator.py`
- **Problem**: Orchestrator only calls `scope_guard.check_text()`, completely omitting `check_transactional_page()`.
- **Required Fix**: Enforce `check_transactional_page()` on all commercial and tool routes in both orchestrator and CI validation.

### Defect 4 & 5: Live Crawl & Audit Scope
- **File**: `seo-agent/agent/orchestrator.py` (lines 133-137)
- **Problem**: `if self.live_crawl: crawled_pages = [self.crawler.fetch_live_page(self.crawler.base_url + "/")]` crawls only 1 single page!
- **Required Fix**: Implement recursive multi-page sitemap-driven live crawl with rate limits, connection pools, and error handling.

### Defect 6, 7 & 8: Safety Firewall & Quality Gates
- **File**: `seo-agent/agent/orchestrator.py` (lines 128, 224-234)
- **Problem**: Line 128 passes `[]` into `verify_safety_immutability()`. Step 7 prints "Validating Scope Guard & Safety Firewall" but never calls `self.firewall`. Schema and Content Quality are not mandatory gates.
- **Required Fix**: Pass critical system files to immutability checks; execute `self.firewall.validate()`; fail closed if schema or content quality fails.

### Defect 9, 10 & 11: Auto Blog Publisher Governance
- **File**: `scripts/auto_blog_publisher.py` (lines 205-254, 273-300), `.github/workflows/auto-blog-publisher.yml`
- **Problem**: Dynamically creates catalog topics and sets `"approved_for_publishing": True` (self-approval). If Gemini API fails, it sets `ai_extra_html = ""` and publishes thin template boilerplate. Pushes directly to `main` via `git push origin main`.
- **Required Fix**: Prohibit dynamic self-approval (fail closed on `NO_ELIGIBLE_TOPIC`), reject publication if AI generation fails, and output to a pull request rather than pushing to `main`.

### Defect 12: AIO Daily Loop Direct Push
- **File**: `.github/workflows/aio-agent-daily.yml` (line 54)
- **Problem**: Directly pushes to `main`.
- **Required Fix**: Create a dedicated branch and PR if changes are detected.

### Defect 14 & 15: GSC Pagination & Pakistan Filtering
- **File**: `marketing_agent/search_apis.py` (lines 150-179)
- **Problem**: Hardcoded `rowLimit: 20` and `startRow: 0` without pagination. No country filter applied.
- **Required Fix**: Implement full pagination loop up to API row limits; add `dimensionFilterGroups` filtering by country `pak`.

### Defect 16: Attribution Event Classification Misfires
- **File**: `attribution.js` (lines 162-170, 197-199)
- **Problem**: Generic querySelector checks trigger `view_comparison`, `view_guide`, and `view_item` on every homepage load.
- **Required Fix**: Use exact URL route matching and explicit page metadata attributes (`data-page-type="homepage|product|guide|comparison"`).

### Defect 17: PostHog Missing
- **File**: Missing from `index.html` and codebase.
- **Required Fix**: Implement privacy-safe PostHog client with PII masking, tracking user journey up to verified WhatsApp conversion.

### Defect 18 & 19: Product Schema Reviews & Return Policy
- **File**: `tools/*/index.html` (e.g. `tools/chatgpt/index.html`)
- **Problem**: Injects fake `Review` ("Verified Pakistani Buyer") and `AggregateRating` ("4.9", 38 reviews) that do not exist in visible HTML. Specifies `ReturnByMail` for digital subscriptions.
- **Required Fix**: Remove unverified reviews; align schema strictly with visible on-page content; update return policy to digital replacement policy.

### Defect 21: Live PageSpeed Insights API
- **File**: Missing client.
- **Required Fix**: Implement automated PSI client querying `https://www.googleapis.com/pagespeedonline/v5/runPagespeed` for mobile and desktop metrics.

### Defect 24: IndexNow Changed URLs Only
- **File**: `ping_agent/cli.py`, `ping_agent/dispatcher.py`
- **Problem**: `cmd_ping --all` dispatches all 96 URLs every run.
- **Required Fix**: Maintain persistent state cache of URL hashes; dispatch only modified, new, or deleted URLs.

