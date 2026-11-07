# HERMES Final Owner Decision & Release Register

**Document ID:** ATG-GOV-DECISIONS-001  
**Audit Phase:** Phase 2.2 Final Independent Release Verification  
**Repository:** `m-rehman55/ai-tool-gems`  
**Date:** 2026-11-07  

---

## 1. Executive Summary

This register presents all remaining governance, security, deployment, and editorial decisions required from the repository owner before merging pull requests, initiating production deployment, or altering search engine indexing.

In accordance with HERMES Safety Principles:
- Autonomous agents operate strictly in **AUDIT / PROPOSE / PR** mode.
- No code has been auto-merged.
- No production deployment has been initiated.
- No category page indexing has been unblocked without owner authorization.

---

## 2. Master Decision Register

| Decision ID | Area | Current Status | Required Owner Decision | Evidence Requirement / Action |
| :--- | :--- | :---: | :--- | :--- |
| **DEC-01** | **PR #16 Production Merge** | **READY FOR REVIEW** | Approve and merge PR #16 (`release/security-pages-hardening`) into `main`. | **CRITICAL:** Use **Squash and Merge** in GitHub UI to collapse intermediate commits into a single clean commit on `main`. |
| **DEC-02** | **GitHub Branch Protection on `main`** | **NOT ACTIVE (HTTP 404)** | Enable Branch Protection on `main` branch in GitHub Repository Settings. | API audit confirms `main` currently has 0 protection rules. Set: 1 required PR review, required passing status checks (`Build & Validate Public Artifact`, `validate`). |
| **DEC-03** | **GitHub Support Cache Purge** | **BLOCKED (OWNER ESCALATION)** | Submit the prepared ticket draft to GitHub Support (`support.github.com`). | Submit the sanitized escalation package from `docs/HISTORICAL_PUBLIC_DATA_EXPOSURE.md` requesting deletion of cached PR refs #13, #14, #15. |
| **DEC-04** | **Commercial Supplier Authorization** | **BLOCKED (LEGAL/COMMERCIAL)** | Review and verify commercial resale / assisted account delivery terms with suppliers. | Confirm that assisting Pakistani buyers with domestic payment rails complies with platform terms of service for each of the 16 catalog tools. |
| **DEC-05** | **Wave 1 Category Hub Indexing** | **HOLD (SAFE NOINDEX)** | Decide whether to publish Wave 1 category hubs to Google index or keep staged. | Review `docs/CATEGORY_HUB_EVIDENCE_AUDIT.md`. To index: change `<meta name="robots" content="noindex, follow">` to `index, follow` and add URLs to `sitemap.xml`. |
| **DEC-06** | **GitHub Pages Deployment Source** | **VERIFIED LEGACY** | Decide whether to maintain classic branch-based Pages (`main /`) or switch to GitHub Actions. | API confirms `build_type: legacy` (served from `main`). To switch to Actions-based Pages, change Source in Settings -> Pages -> Source to "GitHub Actions". |
| **DEC-07** | **PR #17 Content Merge** | **READY FOR REVIEW** | Merge PR #17 (`content/wave1-category-hubs-staged`) into `main` after PR #16 is merged. | Rebase or Squash and Merge PR #17 into `main` after editorial approval of category hubs. |

---

## 3. Step-by-Step Owner Execution Guide

Follow these sequential steps to safely release the remediated platform:

### Step 1: Review Pull Request A (PR #16)
- **URL:** [https://github.com/m-rehman55/ai-tool-gems/pull/16](https://github.com/m-rehman55/ai-tool-gems/pull/16)
- Inspect the PR verification matrix in [`docs/PR_CI_VERIFICATION_MATRIX.md`](file:///d:/Desktop/AI%20Tools%20Aura/docs/PR_CI_VERIFICATION_MATRIX.md).
- Confirm all 6 CI checks are green.
- Click the merge dropdown and select **"Squash and merge"**.

### Step 2: Configure Branch Protection on `main`
- Navigate to: `https://github.com/m-rehman55/ai-tool-gems/settings/branches`
- Click **"Add branch protection rule"** with pattern `main`.
- Check:
  - [x] Require a pull request before merging (1 approval).
  - [x] Require status checks to pass before merging:
    - `Build & Validate Public Artifact`
    - `validate`
    - `test`
    - `CodeQL`
  - [x] Require conversation resolution before merging.
- Click **"Create"**.

### Step 3: Submit Support Ticket for Historical Cache Purge
- Navigate to: `https://support.github.com/contact`
- Copy the sanitized ticket text from Section 5 of [`docs/HISTORICAL_PUBLIC_DATA_EXPOSURE.md`](file:///d:/Desktop/AI%20Tools%20Aura/docs/HISTORICAL_PUBLIC_DATA_EXPOSURE.md).
- Submit ticket to permanently clear historical cached PR refs.

### Step 4: Review Pull Request B (PR #17)
- **URL:** [https://github.com/m-rehman55/ai-tool-gems/pull/17](https://github.com/m-rehman55/ai-tool-gems/pull/17)
- Review the claim-by-claim verification table in [`docs/CATEGORY_HUB_EVIDENCE_AUDIT.md`](file:///d:/Desktop/AI%20Tools%20Aura/docs/CATEGORY_HUB_EVIDENCE_AUDIT.md).
- Verify the three category hubs remain `<meta name="robots" content="noindex, follow">`.
- Click **"Squash and merge"** to integrate the staged category content into `main`.

### Step 5: (Optional) Activate Public Indexing for Category Hubs
- When ready to launch the 3 category hubs on Google Search:
  1. Update `category/ai-chatbots/index.html`, `category/ai-video/index.html`, `category/ai-design/index.html` to `<meta name="robots" content="index, follow">`.
  2. Add the 3 URLs to `sitemap.xml`.
  3. Create a small PR targeting `main` and merge.
