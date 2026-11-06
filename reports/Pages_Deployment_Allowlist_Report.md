# GitHub Pages Public Deployment Allowlist & Data Boundary Report

**Website:** [aitoolgems.tech](https://aitoolgems.tech/)  
**Document ID:** SEC-PAGES-ALLOWLIST-20261107  
**Status:** IMPLEMENTED & VERIFIED (Automated Regression Guard Active)  
**Security Level:** STRICT PUBLIC/PRIVATE ENFORCEMENT  
**Associated Tool:** [`scripts/build_public_site.py`](file:///d:/Desktop/AI%20Tools%20Aura/scripts/build_public_site.py)  
**Associated Test Guard:** [`tests/test_public_deployment_allowlist.py`](file:///d:/Desktop/AI%20Tools%20Aura/tests/test_public_deployment_allowlist.py)  

---

## 1. Executive Summary

AIToolGems operates a high-performance static web presence deployed to GitHub Pages. Under legacy configuration (`gh api repos/m-rehman55/ai-tool-gems/pages`: `source: {branch: "main", path: "/"}`), serving directly from repository root creates an inherent risk of public exposure for internal files, operational directories, and developer sandboxes.

To guarantee that internal supplier data, customer records, audit logs, and developer prototypes are never publicly reachable over HTTP, a strict **Public Deployment Allowlist Architecture** has been established.

```
+-------------------------------------------------------------------------+
|                  AI TOOL GEMS WORKSPACE REPOSITORY                      |
|                                                                         |
|  [Group B: Public Customer-Facing Assets]      [Group A & C: Internal]   |
|   - Root HTML (index, about, policies, ...)     - data/ (Wholesale,...) |
|   - assets/ (Logos, WebP, Icons)                - reports/ (Audits,...) |
|   - tools/ (40 Canonical Product Pages)         - admin.html / admin.js |
|   - guides/ & blog/ (Search Content)            - *_agent/ (CLI Agents) |
|   - sitemap.xml, robots.txt, llms.txt           - tests/ & scripts/     |
+----------------------------------------------------+--------------------+
                                                     |
                                   scripts/build_public_site.py
                                   (Enforces Strict Allowlist)
                                                     |
                                                     v
                                  +---------------------------------------+
                                  |   public-site/ DEPLOYMENT ARTIFACT    |
                                  |   (285 Verified Clean Public Files)   |
                                  |   Zero Internal Data Leaks            |
                                  +---------------------------------------+
```

---

## 2. Public Asset Allowlist Specification

Only the following customer-facing components are designated for public deployment:

| Category | Permitted Patterns / Paths | File Count | Purpose |
|---|---|---|---|
| **Root Public Pages** | `index.html`, `about.html`, `contact.html`, `policies.html`, `correction-policy.html`, `how-we-price.html`, `how-we-review.html`, `how-we-source.html`, `product-verification.html`, `404.html` | 10 | Primary customer navigation, storefront, and legal policies |
| **Storefront Logic** | `app.js`, `attribution.js`, `style.css`, `manifest.json`, `favicon.ico` | 5 | Frontend rendering, cyber-crystal styling, GA4 measurement |
| **Search Engine Directives** | `robots.txt`, `sitemap.xml`, `llms.txt`, `llms-full.txt`, `google*.html`, `bing_*.xml` | 6 | Crawl control, XML indexing, LLM grounding, site ownership |
| **Product Landing Pages** | `tools/*/index.html` | 40 | Verified individual AI tool product landing pages |
| **Content & Editorial** | `guides/*/`, `blog/*/` | 45 | Informational guides, software comparisons, editorial updates |
| **Public Visual Assets** | `assets/product-logos/`, `assets/*.webp`, `assets/*.png` | 179 | High-efficiency WebP logos, icons, and brand graphics |
| **Total Staged Public Artifact** | **All Allowlisted Customer Assets** | **285** | **100% Customer Facing; Zero Internal Data** |

---

## 3. Strict Exclusion & Quarantine Matrix

The following components are strictly excluded from public builds and prohibited from production web exposure:

| Component | Path | Reason for Exclusion | Enforcement Mechanism |
|---|---|---|---|
| **Customer Order Records** | `data/orders/` | Confidential customer transaction data | Purged from Git history; Gitignored; Excluded from build |
| **Wholesale Supplier Data** | `data/wholesale_inventory.json`, `data/wholesale_cost_reference.json`, `data/suppliers/` | Proprietary wholesale USDT costs, supplier bot names, margin calculations | Gitignored; Excluded by prefix check in builder |
| **Internal Audit Reports** | `reports/` (all subdirectories) | Internal technical SEO audits, CWV logs, security diagnostics | Excluded by prefix check in builder |
| **Developer Admin Sandbox** | `admin.html`, `admin.js`, `admin.css`, `admin-light.css` | Unrouted developer prototype; local storage sandbox fixture | Explicitly barred in `STRICT_EXCLUDE_FILES` |
| **Autonomous CLI Agents** | `*_agent/`, `hermes_core/` | Internal automated SEO orchestration Python engines | Excluded by prefix check in builder |
| **Automated Test Suites** | `tests/`, `*_agent/tests/` | Internal QA regression tests, synthetic fixtures | Excluded by prefix check in builder |
| **Automation Scripts** | `scripts/` | Internal build, maintenance, and deployment utilities | Excluded by prefix check in builder |

---

## 4. Automated Builder & Regression Guard

### 4.1 Deployment Builder (`scripts/build_public_site.py`)
The standalone utility `scripts/build_public_site.py` provides:
1. **Deterministic Staging**: Copies only allowlisted root files, verification tokens, and approved public directories (`assets/`, `tools/`, `guides/`, `blog/`).
2. **Post-Build Security Scanner**: Traverses the staged output directory. If any file matches `STRICT_EXCLUDE_FILES` or begins with a path in `STRICT_EXCLUDE_PREFIXES`, the build halts immediately with a `RuntimeError`.
3. **Execution Verification**:
   ```bash
   python scripts/build_public_site.py --verify-only
   # Output: VERIFICATION SUCCESS: 285 public files staged with 0 security policy violations.
   ```

### 4.2 Unit Test Guard (`tests/test_public_deployment_allowlist.py`)
To prevent configuration drift, [`test_build_public_site_creates_clean_artifact_without_leaks`](file:///d:/Desktop/AI%20Tools%20Aura/tests/test_public_deployment_allowlist.py) executes as part of the core test suite:
- Asserts that all essential public pages (`index.html`, `about.html`, `policies.html`, `sitemap.xml`, `robots.txt`) are present.
- Asserts that `data/`, `reports/`, and `admin.html` are strictly absent.
- Asserts that zero excluded prefixes are present in the output tree.

---

## 5. Deployment Recommendations for Production Release

1. **GitHub Pages Source Migration**: Transition GitHub Pages from root deployment (`source: branch: main, path: /`) to dedicated artifact dispatch using GitHub Actions (`actions/deploy-pages@v4`) triggered by `scripts/build_public_site.py`.
2. **Continuous Security Inspection**: Maintain the pre-commit and CI check to verify that `data/` and `reports/` never appear in web-served paths.
3. **Release Approval Gate**: Maintain production deployment in HOLD status until repository owner explicitly reviews and approves the release candidate.
