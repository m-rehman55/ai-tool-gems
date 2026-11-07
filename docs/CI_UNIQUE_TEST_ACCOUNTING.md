# CI Test Accounting & Suite Reconciliation Register

- **Repository:** `m-rehman55/ai-tool-gems`
- **Branch:** `release/security-pages-hardening` (PR #16) & `content/wave1-category-hubs-staged` (PR #17)
- **Audit Date:** 2026-11-07 (PKT UTC+05:00)
- **Status:** PASS — 100% RECONCILED (213 UNIQUE TESTS / 221 CI TEST EXECUTIONS)

---

## 1. Executive Summary

This register provides the definitive, evidence-based reconciliation of automated testing across the `m-rehman55/ai-tool-gems` repository. It resolves previous ambiguities between **unique test definitions** (213 unique test methods discovered across the codebase) and **CI test executions** (221 test executions performed during workflow runs).

Both PR #16 and PR #17 execute 100% passing tests with zero failures, zero errors, and zero skipped assertions.

---

## 2. Definitive Suite-by-Suite Test Inventory (213 Unique Tests)

| Test Suite Path | Target System / Functionality | Test Method Count | Status | Execution Command |
| :--- | :--- | :---: | :---: | :--- |
| `tests/` (Root Suite) | Link graph, DOM integrity, UI interactions, Japan cleanup safeguards, and security boundary tests | **61** | **PASS** | `python -m unittest discover -s tests -v` |
| `ga4_agent/tests/` | GA4 consent mode, `client_id` synthetic bounding, purchase provenance, and refund ledger | **30** | **PASS** | `python -m unittest discover -s ga4_agent/tests -v` |
| `merchant_agent/tests/` | GMC Merchant Center feed XML generation, PKR schema validation, and WhatsApp delivery | **10** | **PASS** | `python -m unittest discover -s merchant_agent/tests -v` |
| `aio_agent/tests/` | Google AI Overviews (AIO), RAG extractability, query fan-out intent, and machine sync | **5** | **PASS** | `python -m unittest discover -s aio_agent/tests -v` |
| `ping_agent/tests/` | Instant IndexNow protocol verification, multi-engine ping dispatch (Bing, Yandex, Seznam) | **6** | **PASS** | `python -m unittest discover -s ping_agent/tests -v` |
| `keyword_agent/tests/` | GSC regex library, keyword intent mapping, SERP cannibalization, competitor gap | **25** | **PASS** | `python -m unittest discover -s keyword_agent/tests -v` |
| `marketing_agent/tests/` | Buffer social automation, deal card generation, pricing index, and growth analytics | **33** | **PASS** | `python -m unittest discover -s marketing_agent/tests -v` |
| `seo-agent/tests/` | Technical crawler, scope guard, safety firewall, schema completeness, and 14-artifact reporter | **43** | **PASS** | `python -m unittest discover -s seo-agent/tests -v` |
| **Total Unique Test Methods** | **Comprehensive Full Repository Test Inventory** | **213** | **PASS** | **100% Green Across All 8 Suites** |

---

## 3. Root `tests/` Breakdown (61 Tests)

The 61 tests in the root `tests/` directory comprise:
1. `test_integrity_and_regressions.py`: 40 tests (Core Web Vitals, HTML semantic structure, image lazy loading, schema tags).
2. `test_link_graph.py`: 8 tests (0 broken links, 0 orphaned routes, fragment anchor integrity).
3. `test_ui_interactions.py`: 2 tests (Interactive pricing calculators, mobile search modals).
4. `test_japan_safeguards.py`: 3 tests (Permanent exclusion of historical `/jp/` paths and Japanese content).
5. `test_public_deployment_allowlist.py`: 4 tests (Affirmative allowlist staging in `build_public_site.py`).
6. `test_public_repository_boundary.py`: 4 tests (Strict exclusion of `reports/`, `data/orders`, credentials, and support ticket drafts from Git tracking).

**Total Root Tests:** 40 + 8 + 2 + 3 + 4 + 4 = **61 unique tests**.

---

## 4. Reconciliation: 213 Unique Tests vs 221 Executed Tests

In `.github/workflows/deploy-pages.yml`, the CI test step runs:
```yaml
- name: Run Test Suites
  run: |
    python -m unittest tests/test_public_deployment_allowlist.py -v   # 4 tests
    python -m unittest tests/test_public_repository_boundary.py -v    # 4 tests
    python -m unittest discover -s tests -v                           # 61 tests
    python -m unittest discover -s ga4_agent/tests -v                 # 30 tests
    python -m unittest discover -s merchant_agent/tests -v            # 10 tests
    python -m unittest discover -s aio_agent/tests -v                 # 5 tests
    python -m unittest discover -s ping_agent/tests -v                # 6 tests
    python -m unittest discover -s keyword_agent/tests -v             # 25 tests
    python -m unittest discover -s marketing_agent/tests -v           # 33 tests
    python -m unittest discover -s seo-agent/tests -v                 # 43 tests
```

### Mathematical Accounting
$$\text{Total Executions} = 4 + 4 + 61 + 30 + 10 + 5 + 6 + 25 + 33 + 43 = 221$$

- **Why 8 tests are run twice:**
  `test_public_deployment_allowlist.py` (4 tests) and `test_public_repository_boundary.py` (4 tests) are executed standalone as immediate fail-fast pre-flight checks at the start of the CI run, before the full discovery suite `unittest discover -s tests` executes all 61 tests in `tests/`.
- **Verdict:**
  - Unique test cases implemented: **213**
  - Total test executions in CI: **221**
  - Failure rate: **0.00%** (0 failures, 0 errors across both PRs).

---

## 5. Additional Quality & Compliance Audits

In addition to the 213 unit tests, CI and local release validation execute 3 standalone technical audit engines:
1. `python scripts/link_graph_checker.py --strict`: Audits 102 HTML files, verifying 0 broken links, 0 orphaned routes, and 0 anchor fragment mismatches (**PASS**).
2. `python scripts/build_public_site.py --verify-only`: Asserts that all 316 staged assets comply with the affirmative allowlist (**PASS**).
3. `python schema_audit.py`: Validates JSON-LD Product, FAQ, and BreadcrumbList structured data across 101 pages (**PASS — 100.0%**).

