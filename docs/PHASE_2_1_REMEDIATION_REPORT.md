# HERMES Phase 2.1 Release Candidate Remediation Report

**Document ID:** ATG-REP-PHASE-2-1  
**Auditor / Roles:** Principal Security Engineer, Senior Python Engineer, GitHub Actions Engineer, Analytics Architect, Technical SEO Lead  
**Audit Date:** 2026-11-07  
**Production Site:** [aitoolgems.tech](https://aitoolgems.tech/)  
**GitHub Repository:** [m-rehman55/ai-tool-gems](https://github.com/m-rehman55/ai-tool-gems)  
**Primary Target Market:** Pakistan (Flat PKR pricing, domestic rails)  
**Release Branches Under Remediation:**  
- PR A (PR #16): `release/security-pages-hardening`  
- PR B (PR #17): `content/wave1-category-hubs-staged`  

---

## 1. Executive Summary

Phase 2.1 was initiated to independently audit, correct, harden, and verify the AIToolGems release candidate following the historical order-data purge. Prior reports asserted that all release-readiness criteria were satisfied; however, an independent architectural inspection revealed several critical gaps:
1. **Public Repository vs Pages Deployment Contradiction:** Internal diagnostic reports detailing security incidents and file classifications were excluded from GitHub Pages deployment, yet were committed to public Git tracking in `reports/`.
2. **Missing Client ID Runtime Provenance:** `ga4_agent/conversion_importer.py` did not enforce strict client ID format validation or runtime provenance checking on orders and refunds.
3. **Consent Mode Discrepancy:** `attribution.js` initialized Consent Mode v2 with `'analytics_storage': 'granted'`, contradicting documentation specifying privacy-first default denial.
4. **Telemetry Data Exposure:** DOM image elements emitted raw image sources (`proofElem.src`) during verification clicks, risking query parameter and local path leakage.
5. **Orphaned & Unbounded Refunds:** Refund records were not validated against verified parent orders or bounded by original order amounts.

Over the course of Phase 2.1, each of these weaknesses has been systematically resolved and validated with automated regression suites.

---

## 2. Repository & Branch State Verification

### 2.1 Branch Dependency Architecture
To prevent conflating infrastructure security with editorial content rollout, the release candidate maintains strict branch separation:
- **Base Anchor (`origin/main`):** Commit `418fc477084c4ebb393b3c5cb6abb40b27e1fc36` (Clean, secure production baseline).
- **PR A (`release/security-pages-hardening` / PR #16):**
  - Targets `main`.
  - Enforces public repository boundaries, the fail-closed build engine, GitHub Actions deployment guardrails, and GA4 privacy/provenance hardening.
  - State: **OPEN, MERGEABLE, ALL CI CHECKS PASSING**.
- **PR B (`content/wave1-category-hubs-staged` / PR #17):**
  - Targets `release/security-pages-hardening`.
  - Delivers Wave 1 topical authority Category Hubs (`category/ai-chatbots/`, `category/ai-video/`, `category/ai-design/`).
  - Staged with `<meta name="robots" content="noindex, follow">` and excluded from `sitemap.xml`.
  - State: **OPEN, MERGEABLE**.

### 2.2 Safety & Recovery Point
Before initiating remediation commits, a persistent recovery tag was established on the pre-remediation state:
- `recovery-phase-2-1-pre-remediation` (`1cbdb22b20e81e9210fe7121395c38f8ebb8cd67`).

---

## 3. Public Repository Boundary Hardening (Phase 1)

### 3.1 Contradiction Resolution
Because the GitHub repository is public, any file committed to Git is readable worldwide via GitHub's web interface or API. Staging files out of GitHub Pages does not prevent public exposure if those files remain in the Git repository tree.

**Remediation Steps:**
1. Untracked all internal diagnostic and operational reports from Git:
   - `reports/GA4_Regression_Report.md`
   - `reports/GitHub_Support_Ticket_and_Refs_Report.md`
   - `reports/Git_History_Purge_Verification_Report.md`
   - `reports/Pages_Artifact_Inspection_Report.md`
   - `reports/Public_Private_Data_Classification.csv`
   - `reports/Public_Private_Tracked_Data_Audit.md`
   - `reports/Updated_Release_Readiness_Report.md`
   - `marketing_agent/data/repair-last.log`
2. Relocated internal diagnostic materials to local gitignored storage: `data/reports/`.
3. Updated `.gitignore` to add `reports/` as an explicit quarantine rule.
4. Published sanitized, public architectural documentation exclusively to `docs/`.
5. Authored `tests/test_public_repository_boundary.py` (4 automated tests verifying zero credentials, zero secret files, zero wholesale pricing sheets, zero customer orders, and comprehensive `.gitignore` rules).

---

## 4. Fail-Closed Public Deployment Builder (Phase 2)

### 4.1 Redesign of `scripts/build_public_site.py`
The staging script was re-engineered from a negative denylist to an affirmative allowlist with strict boundary controls:
- **Affirmative File Allowlists:**
  - `APPROVED_ROOT_FILES`: `index.html`, `prices.html`, `deals.html`, `sitemap.xml`, `robots.txt`, `llms.txt`, `llms-full.txt`, `tool-page.css`, `attribution.js`, `CNAME`.
  - `APPROVED_VERIFICATION_FILES`: Google and Bing site verification HTML files.
- **Affirmative Directory Allowlists:**
  - `APPROVED_PUBLIC_DIRS`: `assets/`, `tools/`, `guides/`, `blog/`, `category/`.
- **Extension Controls:**
  - `assets/`: Strictly `.webp, .png, .jpg, .jpeg, .svg, .ico, .css, .mp4, .woff, .woff2, .ttf`.
  - Root and content directories: Strictly `.html` (plus designated root assets).
  - Universally Prohibited: `.env, .pem, .key, .csv, .sqlite, .db, .zip, .log, .py, .yml, .md, .sh`.
- **Path Traversal & Symlink Defense:**
  - Inspects file attributes for symbolic links; raises `PublicSiteSecurityError` if encountered.
  - Resolves destination paths to ensure no file is written outside the output directory.
- **Deterministic Cryptographic Manifest:**
  - Generates `manifest-public-build.json` containing path, size in bytes, and SHA-256 hash for every staged asset (313 public files verified).

### 4.2 Adversarial Test Suite (`tests/test_public_deployment_allowlist.py`)
Tested with 8 injected attack files (`assets/private.csv`, `assets/supplier-export.json`, `tools/test/.env`, `guides/internal-audit.md`, `blog/customer-data.sqlite`, `category/private.pem`, `assets/backup.zip`, `assets/secrets.log`), CNAME tampering, and symlink injection.
- **Result:** All adversarial cases fail closed with explicit security exceptions.

---

## 5. GitHub Pages Deployment Guardrails (Phase 3)

### 5.1 Workflow Decoupling (`.github/workflows/deploy-pages.yml`)
- **`build` Job:**
  - Executes on push to `main`, pull requests targeting `main`, and manual dispatch.
  - Permissions restricted to `contents: read`.
  - Validates Python syntax, runs `scripts/build_public_site.py`, and uploads the public site artifact for verification.
- **`deploy` Job:**
  - Strictly gated: `if: github.ref == 'refs/heads/main'`.
  - Permissions: `pages: write`, `id-token: write`.
  - Feature branches and PRs **cannot** trigger deployment under any circumstances.

---

## 6. GA4 Privacy and Conversion Integrity (Phase 4)

### 6.1 Authentic Measurement ID Reconciliation
- Confirmed production Measurement ID: `G-NQJCMDCLLP`.
- Erroneous reference `G-F85W59KG5F` in earlier documentation was audited across the codebase (0 occurrences in code) and corrected in all reports.

### 6.2 Google Consent Mode v2
- In `attribution.js`, default consent parameters were updated to privacy-first denial:
  ```javascript
  window.gtag('consent', 'default', {
    'analytics_storage': 'denied',
    'ad_storage': 'denied',
    'ad_user_data': 'denied',
    'ad_personalization': 'denied',
    'wait_for_update': 500
  });
  ```

### 6.3 Client ID Provenance & PII Elimination
- Added `validate_client_id` in `ga4_agent/models.py`.
- Rejects email strings (`@`), phone hash derivations, and explicit PII markers (`user`, `customer`, `phone`).
- Enforces standard GA4 format: `^[0-9a-zA-Z._-]{10,64}$`.
- Tracks `client_id_provenance` (`browser_cookie`, `none`, `rejected`) on `OfflineVerifiedOrder`.
- Sanitized `proof_image_open` event telemetry in `attribution.js` to `{ proof_type: 'payment_verification_proof' }`.

### 6.4 Symmetrical Refund Lifecycle
- Enforced parent transaction lookup in `ga4_agent/conversion_importer.py`. Orphan refunds are rejected.
- Validated that refund amounts do not exceed original order amounts or cumulative prior refunds.
- GA4 Measurement Protocol dispatch safely skips orders/refunds lacking legitimate client IDs without synthesizing identifiers.

---

## 7. Category Hub Staged Safeguards & Editorial Quality (Phase 5)

### 7.1 Staged Topical Authority Hubs
Wave 1 Category Hubs deliver comprehensive comparisons for the Pakistani market:
1. `category/ai-chatbots/index.html` (ChatGPT Plus, Claude Pro, Gemini Advanced, Perplexity Pro, Grok 2, DeepSeek).
2. `category/ai-video/index.html` (Google Veo, Runway Gen-3, Kling AI, HeyGen Avatar Pro).
3. `category/ai-design/index.html` (Midjourney, Leonardo, Canva Pro, Figma Pro, Freepik, Adobe CC).

### 7.2 Safety & Anti-Doorway Controls
- **Word Count:** Over 1,200 words of technical analysis per hub.
- **Pricing Congruence:** 100% match with underlying tool pages (e.g. ChatGPT Plus Rs. 2,300, Claude Pro Rs. 2,200, Canva Pro Rs. 900).
- **Indexing Protection:** Tagged with `<meta name="robots" content="noindex, follow">` and excluded from `sitemap.xml`.
- **Structured Data:** Valid `BreadcrumbList`, `CollectionPage`, and `FAQPage` schemas.

---

## 8. Complete CI & Verification Matrix (Phase 6)

| Verification Suite | Target Script / Command | Exit Code | Outcome |
| :--- | :--- | :---: | :---: |
| **Public Repo Boundary** | `python -m unittest tests/test_public_repository_boundary.py -v` | `0` | 4 / 4 PASSED |
| **Deployment Allowlist** | `python -m unittest tests/test_public_deployment_allowlist.py -v` | `0` | 4 / 4 PASSED |
| **GA4 Privacy & Conversion** | `python -m unittest discover -s ga4_agent/tests -v` | `0` | 30 / 30 PASSED |
| **Link Graph & Route Audit**| `python scripts/link_graph_checker.py --strict` | `0` | 102 / 102 PASSED (0 broken links) |
| **Public Site Builder** | `python scripts/build_public_site.py` | `0` | 313 files staged cleanly |
| **Schema Integrity** | `python schema_audit.py` | `0` | 100% schemas valid |

---

## 9. Release Governance & Next Steps (Phase 7)

- **PR #16 (`release/security-pages-hardening`):** Ready for human owner review and merge into `main`.
- **PR #17 (`content/wave1-category-hubs-staged`):** Ready for human owner editorial review.
- **Production Deployment:** Remains frozen until PR #16 is merged into `main`.
- **GitHub Upstream Purge:** Owner must submit a GitHub Support ticket to execute server-side garbage collection of orphaned commit references containing purged order data.

