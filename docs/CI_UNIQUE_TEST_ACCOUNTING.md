# CI Test Accounting & Suite Reconciliation Register

- **Repository:** `m-rehman55/ai-tool-gems`
- **Branch:** `release/security-pages-hardening` (PR #16) & `content/wave1-category-hubs-staged` (PR #17)
- **Audit Date:** 2026-11-07 (PKT UTC+05:00)
- **Status:** PASS (LOCAL VERIFICATION: 213 TESTS PASSING) / PENDING (REMOTE CI RUN ON UPDATED PR HEAD)

---

## 1. Executive Summary & Verification Distinction

This register provides the definitive, evidence-based reconciliation of automated testing across the `m-rehman55/ai-tool-gems` repository. Following the Phase 2.3.1 CI coverage repair in `.github/workflows/seo-agent-validation.yml`, all eight test suites are explicitly configured in the workflow to run once via standard discovery.

### Exact Verification Distinction:
- **Local Verification:** Exactly **213 unique tests passed** across all eight test suites in 67.55s with zero failures, zero errors, and zero skipped assertions.
- **CI Configuration:** All **eight suites are explicitly configured** in `.github/workflows/seo-agent-validation.yml`, with both `ga4_agent/**` and `merchant_agent/**` added to path filters and test execution steps.
- **Remote CI Verification:** **Pending** until GitHub Actions completes successfully on the exact updated PR head commit.

---

## 2. Definitive Suite-by-Suite Test Inventory (213 Unique Tests)

| Test Suite Path | Target System / Functionality | Test Method Count | Local Verification | CI Configuration Status | Execution Source |
| :--- | :--- | :---: | :---: | :---: | :--- |
| `tests/` (Root Suite) | Link graph, DOM integrity, UI interactions, Japan cleanup safeguards, and security boundary tests | **61** | **PASS** (24.76s) | Configured | `.github/workflows/seo-agent-validation.yml` (`validate` job) |
| `ga4_agent/tests/` | GA4 consent mode, `client_id` synthetic bounding, purchase provenance, and refund ledger | **30** | **PASS** (3.62s) | Configured (NEW) | `.github/workflows/seo-agent-validation.yml` (`validate` job) |
| `merchant_agent/tests/` | GMC Merchant Center feed XML generation, PKR schema validation, and WhatsApp delivery | **10** | **PASS** (0.07s) | Configured (NEW) | `.github/workflows/seo-agent-validation.yml` (`validate` job) |
| `aio_agent/tests/` | Google AI Overviews (AIO), RAG extractability, query fan-out intent, and machine sync | **5** | **PASS** (0.35s) | Configured | `.github/workflows/seo-agent-validation.yml` (`validate` job) |
| `ping_agent/tests/` | Instant IndexNow protocol verification, multi-engine ping dispatch (Bing, Yandex, Seznam) | **6** | **PASS** (0.04s) | Configured | `.github/workflows/seo-agent-validation.yml` (`validate` job) |
| `keyword_agent/tests/` | GSC regex library, keyword intent mapping, SERP cannibalization, competitor gap | **25** | **PASS** (0.27s) | Configured | `.github/workflows/seo-agent-validation.yml` (`validate` job) |
| `marketing_agent/tests/` | Buffer social automation, deal card generation, pricing index, and growth analytics | **33** | **PASS** (3.74s) | Configured | `.github/workflows/seo-agent-validation.yml` (`validate` job) |
| `seo-agent/tests/` | Technical crawler, scope guard, safety firewall, schema completeness, and 14-artifact reporter | **43** | **PASS** (34.70s) | Configured | `.github/workflows/seo-agent-validation.yml` (`validate` job) |
| **Total Test Accounting** | **Comprehensive Full Repository Test Inventory** | **213** | **PASS (213 / 213)** | **8 / 8 Suites Configured** | **Single-Pass CI Execution Target** |

---

## 3. Root `tests/` Directory Breakdown (61 Tests)

The 61 tests discovered within the root `tests/` directory comprise:
1. `test_integrity_and_regressions.py`: 40 tests (Core Web Vitals, HTML semantic structure, image lazy loading, schema tags).
2. `test_link_graph.py`: 8 tests (0 broken links, 0 orphaned routes, fragment anchor integrity).
3. `test_ui_interactions.py`: 2 tests (Interactive pricing calculators, mobile search modals).
4. `test_japan_safeguards.py`: 3 tests (Permanent exclusion of historical `/jp/` paths and Japanese content).
5. `test_public_deployment_allowlist.py`: 4 tests (Affirmative allowlist staging in `build_public_site.py`).
6. `test_public_repository_boundary.py`: 4 tests (Strict exclusion of `reports/`, `data/orders`, credentials, and support ticket drafts from Git tracking).

**Total Root Tests:** 40 + 8 + 2 + 3 + 4 + 4 = **61 unique tests**.

---

## 4. Reconciliation: 213 Unique Tests & CI Configuration

### Historical Context (Phase 2.1 - Phase 2.3)
In earlier phase documentation, an execution count of 221 was calculated by adding standalone pre-flight commands (`test_public_deployment_allowlist.py` [4 tests] and `test_public_repository_boundary.py` [4 tests]) to the 61 root tests and 152 agent tests ($4 + 4 + 61 + 152 = 221$).

### Phase 2.3.1 Clean CI Architecture
To ensure complete transparency and prevent confusing test metrics:
1. `.github/workflows/seo-agent-validation.yml` was repaired to explicitly include `ga4_agent/tests` (30 tests) and `merchant_agent/tests` (10 tests) alongside the other 6 suites.
2. Each test suite is configured to run exactly once via standard `unittest discover`.
3. Standalone duplicate pre-flight runs are avoided in the validation workflow.
4. Total unique test definitions: **213**.
5. Total test executions configured per CI validation run: **213**.

$$\text{Total Discovered Tests} = 61 + 30 + 10 + 5 + 6 + 25 + 33 + 43 = 213$$
$$\text{Total Configured CI Executions} = 61 + 30 + 10 + 5 + 6 + 25 + 33 + 43 = 213$$

---

## 5. Additional Quality & Compliance Audits (Non-Unit Checks)

In addition to the 213 unit tests, the validation workflow and release gates execute 3 standalone technical audit engines:
1. `python scripts/link_graph_checker.py --strict`: Audits 102 HTML files, verifying 0 broken links, 0 orphaned routes, and 0 anchor fragment mismatches (**PASS**).
2. `python scripts/build_public_site.py --verify-only`: Asserts that all 316 staged assets comply with the affirmative allowlist (**PASS**).
3. `python schema_audit.py`: Validates JSON-LD Product, FAQ, and BreadcrumbList structured data across 101 pages (**PASS — 100.0%**).
