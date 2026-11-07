# Public Tracked File Classification & Boundary Register

- **Repository:** `m-rehman55/ai-tool-gems`
- **Branch:** `release/security-pages-hardening` (PR #16)
- **Primary Market:** Pakistan (`https://aitoolgems.tech/`)
- **Audit Date:** 2026-11-07 (PKT UTC+05:00)
- **Status:** PASS — ALL TRACKED FILES FORMALLY CLASSIFIED

---

## 1. Executive Summary

This document provides the formal, sanitized classification of all files tracked in Git within the public repository `m-rehman55/ai-tool-gems`. Following the untracking of legacy diagnostic reports (`reports/architecture/`, `reports/keyword-agent/`, `reports/seo/`), every tracked file has been audited against security, privacy, and commercial boundaries.

Zero customer transaction data, zero credentials, zero supplier wholesale price sheets, and zero diagnostic logs are tracked in Git.

---

## 2. Summary Distribution by Category

| Category | Description | Tracked Count | Status |
| :--- | :--- | :---: | :---: |
| **`PUBLIC_APPROVED`** | Live website pages, styles, scripts, product logos, verification records, and public feeds | 316 | **PASS** |
| **`PUBLIC_SANITIZED`** | Public engineering specifications, architectural docs, and governance guides | 27 | **PASS** |
| **`INTERNAL_OPERATIONAL`** | Python agent packages, unit tests, CI/CD workflow configurations, and seed keyword mappings | 243 | **PASS** |
| **`CUSTOMER_OR_TRANSACTION_DATA`** | Private customer identifiers, payment receipts, order logs | **0** | **STRICT ZERO** |
| **`CREDENTIAL_OR_SECRET`** | Private keys, service accounts, bearer tokens, passwords | **0** | **STRICT ZERO** |
| **`UNKNOWN_REQUIRES_OWNER`** | Unclassified or ambiguous files | **0** | **STRICT ZERO** |
| **Total Tracked Inventory** | Audited files across the active release candidate tree | **586** | **100% AUDITED** |

---

## 3. Category Definitions & Audit Criteria

### A. `PUBLIC_APPROVED` (Website Assets & Pages)
Files that are intentionally served to public web users and search engine crawlers:
- **Core Pages:** `index.html`, `prices/index.html`, `deals/index.html`, `privacy-policy/index.html`, `terms-of-service/index.html`.
- **Tool Pages:** 40 tool profile pages under `tools/*/index.html`.
- **Category Hubs (Staged in PR #17):** 3 category hub pages under `category/*/index.html` (retained with `noindex, follow`).
- **Educational Guides & Blog:** 40 educational buying guides in `guides/*/index.html` and `blog/index.html`.
- **Public Assets & Styles:** `assets/`, `styles.css`, `app.js`, `attribution.js`, `script.js`, `search.js`.
- **Crawler & Verification Infrastructure:** `robots.txt`, `sitemap.xml`, `llms.txt`, `llms-full.txt`, `CNAME`, `ads.txt`, `BingSiteAuth.xml`, IndexNow key files.

### B. `PUBLIC_SANITIZED` (Public Engineering Documentation)
Engineering documentation in `docs/` detailing system architecture, release governance, and security controls:
- Contains zero customer identifiers, zero live secrets, and zero raw internal ticket texts.
- All references use repository-relative or GitHub links; zero local workstation filesystem paths.

### C. `INTERNAL_OPERATIONAL` (Autonomous Agents & Pipeline Automation)
Operational source code powering HERMES automation within GitHub Actions:
- **Agents:** `hermes_core/`, `aio_agent/`, `ping_agent/`, `keyword_agent/`, `marketing_agent/`, `seo-agent/`, `ga4_agent/`, `merchant_agent/`.
- **Validation Workflows:** `.github/workflows/deploy-pages.yml`, `seo-agent-validation.yml`, `codeql.yml`, etc.
- **Unit Test Suites:** `tests/`, `aio_agent/tests/`, `keyword_agent/tests/`, etc. (213 unique unit tests).
- **Public Seed Data:** Public keyword mapping examples and public GSC schema snapshots in `data/` (scrubbed of private identifiers).

### D. `CUSTOMER_OR_TRANSACTION_DATA` (Quarantined)
Strictly prohibited from tracking. Enforced via `.gitignore` and `tests/test_public_repository_boundary.py`:
- `data/orders/` — Untracked & ignored.
- `data/wholesale_inventory.json` — Untracked & ignored.
- `data/wholesale_cost_reference.json` — Untracked & ignored.
- `data/suppliers/` — Untracked & ignored.

### E. `CREDENTIAL_OR_SECRET` (Quarantined)
Strictly prohibited from tracking. Zero live credentials present:
- `.env.example` — Public sanitized template (no credentials).
- Production secrets managed exclusively through GitHub Repository Secrets.

---

## 4. Automated Boundary Enforcement

Repository boundaries are continuously asserted via automated unit testing in CI:
- **`tests/test_public_repository_boundary.py`**:
  - `test_no_quarantined_operational_paths_tracked_in_git`: Asserts that `data/orders`, `data/suppliers`, `config`, `reports/`, and wholesale cost paths are never tracked in Git.
  - `test_no_credentials_or_secrets_tracked_in_git`: Asserts that `.pem`, `.key`, `.json` credentials, and `.env` are never tracked in Git.
  - `test_no_incident_reports_with_commit_hashes_in_public_tree`: Asserts that unredacted ticket drafts or sensitive hashes are excluded from tracking.
  - `test_gitignore_contains_comprehensive_quarantine_blocks`: Verifies quarantine rules in `.gitignore`.
- **`tests/test_public_deployment_allowlist.py`**:
  - Asserts that `scripts/build_public_site.py` stages only strictly allowlisted assets into `public-site/`.

