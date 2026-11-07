# HERMES Unique Test Accounting & Reproducibility Matrix

**Document ID:** ATG-QA-ACCOUNTING-001  
**Audit Phase:** Phase 2.2 Final Independent Release Verification  
**Repository:** `m-rehman55/ai-tool-gems`  
**Execution Environment:** Python 3.10+ / Windows / Ubuntu CI  
**Audit Date:** 2026-11-07  

---

## 1. Executive Summary & Test Accounting Resolution

In Phase 2.1 documentation, a grand total of **221 test executions** was reported across 10 test execution steps. An independent audit was conducted in Phase 2.2 to determine:
1. Whether the 4 public boundary tests (`tests/test_public_repository_boundary.py`) and 4 deployment allowlist tests (`tests/test_public_deployment_allowlist.py`) are already included in the 61 root regression tests (`tests/`).
2. The exact, deduped count of unique test cases discovered by `unittest`.

### Audit Findings:
- **Unique Test Cases Discovered:** **213 unique test cases** exist across the entire codebase.
- **Root Regression Discovery:** The 61 tests discovered under `tests/` **already include** the 4 tests from `test_public_deployment_allowlist.py` and the 4 tests from `test_public_repository_boundary.py`.
- **Explanation of 221 Figure:** Running the 2 security test files as standalone commands (4 + 4) and subsequently running `discover -s tests` (61) resulted in 8 test cases being executed twice (4 + 4 + 61 = 69 executions for 61 unique tests). Adding the 152 tests from the 7 agent suites yielded 221 total test executions.
- **Truthful Status:** There are **213 unique, fully reproducible test cases**, all passing with 100% green exit codes.

---

## 2. Test Discovery Breakdown by Module

### 2.1 Root Regression Suite (`tests/` — 61 Unique Tests)

Discovery Command: `python -m unittest discover -s tests -v`

| Module | Test Class | Unique Tests | Focus / Coverage | Included in 61? |
| :--- | :--- | :---: | :--- | :---: |
| `test_auto_blog_publisher` | `TestAutoBlogPublisherSafeguards`, `TestSitemapAutomationSafeguards` | 10 | Content queue, slug regex, title/meta bounds, payment rails | YES |
| `test_integrity_and_regressions` | `TestIntegrityAndRegressions` | 14 | AdSense, catalog routing, no exposed API secrets, no fake toast, pricing | YES |
| `test_japan_safeguards` | `TestJapanSafeguards` | 3 | Scope guard, foreign currency/domain exclusion | YES |
| `test_link_graph` | `TestLinkGraph` | 10 | Internal links, fragment anchors, sitemap routes, 0 broken links | YES |
| `test_public_deployment_allowlist` | `TestPublicDeploymentAllowlist` | 4 | Fail-closed allowlist, symlink escape, CNAME tampering, adversarial files | **YES** |
| `test_public_repository_boundary` | `TestPublicRepositoryBoundary` | 4 | No tracked orders, no secrets, no commit-hash reports, .gitignore | **YES** |
| `test_ui_interactions` | `TestUIInteractions` | 16 | Category filters, modals, focus traps, reduced motion, search input | YES |
| **Subtotal `tests/`** | **7 Modules** | **61** | **Complete Core & Regression Coverage** | — |

---

### 2.2 Specialized Agent Test Suites (152 Unique Tests)

| Agent Suite | Test Path / Discovery Target | Unique Tests | Key Verification Responsibilities |
| :--- | :--- | :---: | :--- |
| **GA4 Agent** | `ga4_agent/tests` | 30 | Consent Mode v2 default, client_id format/regex, phone hash PII rejection, email rejection, provenance tracking, refund lifecycle symmetry, missing-secret safety |
| **Merchant Center Agent** | `merchant_agent/tests` | 10 | Feed generation, SLA alignment (15–60 min), prohibited tool hold, Google Ads status `PRELIMINARY_POLICY_REVIEW` |
| **AIO Agent** | `aio_agent/tests` | 5 | RAG grounding scorer, 5-branch query fan-out coverage, `llms.txt` / `llms-full.txt` sync engine |
| **Instant Ping Agent** | `ping_agent/tests` | 6 | IndexNow key verification, multi-engine dispatch (Bing, Yandex, Seznam), dispatch history logger |
| **Keyword Intelligence Agent** | `keyword_agent/tests` | 25 | RE2 regex library, intent mapping (transactional vs comparison), Top 10 competitor gap analysis, cannibalization |
| **Marketing Agent** | `marketing_agent/tests` | 33 | Buffer social cadence, channel separation, duplicate protection, live metrics refresh without rescheduling |
| **SEO Safety & Firewall Agent**| `seo-agent/tests` | 43 | Safety firewall, commercial price freeze, scope guard (PKR/EasyPaisa), technical audit, crawler policy, 14-artifact suite |
| **Subtotal Agent Suites** | **7 Specialized Suites** | **152** | **Full Systemic & Autonomous Agent Integrity** |

---

## 3. Discovered vs Executed Reconciliation

```
  61 unique tests in tests/ (including 4 boundary + 4 allowlist tests)
+ 30 unique tests in ga4_agent/tests
+ 10 unique tests in merchant_agent/tests
+  5 unique tests in aio_agent/tests
+  6 unique tests in ping_agent/tests
+ 25 unique tests in keyword_agent/tests
+ 33 unique tests in marketing_agent/tests
+ 43 unique tests in seo-agent/tests
------------------------------------------------------------------------
= 213 UNIQUE TEST CASES (Zero duplication, zero overlaps)

When executed as 10 discrete workflow commands:
   4 (python -m unittest tests/test_public_repository_boundary.py)
+  4 (python -m unittest tests/test_public_deployment_allowlist.py)
+ 61 (python -m unittest discover -s tests)  <-- Re-executes the 8 above
+ 30 (python -m unittest discover -s ga4_agent/tests)
+ 10 (python -m unittest discover -s merchant_agent/tests)
+  5 (python -m unittest discover -s aio_agent/tests)
+  6 (python -m unittest discover -s ping_agent/tests)
+ 25 (python -m unittest discover -s keyword_agent/tests)
+ 33 (python -m unittest discover -s marketing_agent/tests)
+ 43 (python -m unittest discover -s seo-agent/tests)
------------------------------------------------------------------------
= 221 TEST EXECUTIONS (8 tests executed twice across discrete commands)
```

---

## 4. Independent Reproducibility Log

Every test command was executed independently from a clean shell session:

| Execution Command | Commit Head Evaluated | Exit Code | Tests Reported | Wall Clock Time | Reproducibility Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `python -m unittest tests/test_public_repository_boundary.py -v` | `9d2aac9e` | `0` | 4 | 0.23s | **VERIFIED CLEAN** |
| `python -m unittest tests/test_public_deployment_allowlist.py -v` | `9d2aac9e` | `0` | 4 | 9.49s | **VERIFIED CLEAN** |
| `python -m unittest discover -s tests -v` | `9d2aac9e` | `0` | 61 | 33.88s | **VERIFIED CLEAN** |
| `python -m unittest discover -s ga4_agent/tests -v` | `9d2aac9e` | `0` | 30 | 3.56s | **VERIFIED CLEAN** |
| `python -m unittest discover -s merchant_agent/tests -v` | `9d2aac9e` | `0` | 10 | 0.12s | **VERIFIED CLEAN** |
| `python -m unittest discover -s aio_agent/tests -v` | `9d2aac9e` | `0` | 5 | 0.41s | **VERIFIED CLEAN** |
| `python -m unittest discover -s ping_agent/tests -v` | `9d2aac9e` | `0` | 6 | 0.06s | **VERIFIED CLEAN** |
| `python -m unittest discover -s keyword_agent/tests -v` | `9d2aac9e` | `0` | 25 | 0.36s | **VERIFIED CLEAN** |
| `python -m unittest discover -s marketing_agent/tests -v` | `9d2aac9e` | `0` | 33 | 4.73s | **VERIFIED CLEAN** |
| `python -m unittest discover -s seo-agent/tests -v` | `9d2aac9e` | `0` | 43 | 35.49s | **VERIFIED CLEAN** |
| `python scripts/link_graph_checker.py --strict` | `9d2aac9e` | `0` | 102 HTML files | 2.11s | **VERIFIED CLEAN (0 errors)** |
| `python scripts/build_public_site.py --verify-only` | `9d2aac9e` | `0` | 316 public assets | 0.85s | **VERIFIED CLEAN (0 violations)** |
| `python schema_audit.py` | `9d2aac9e` | `0` | 101 pages | 1.15s | **VERIFIED CLEAN (100.0%)** |
