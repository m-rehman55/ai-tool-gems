# Historical Public Data Exposure & GitHub Support Escalation Architecture

- **Document ID:** ATG-SEC-EXPOSURE-001
- **Repository:** `m-rehman55/ai-tool-gems`
- **Classification:** PUBLIC ENGINEERING RECORD (Strictly sanitized — zero customer PII, zero credentials, zero supplier secrets)
- **Date:** 2026-11-07 (PKT UTC+05:00)
- **Status:** REMEDIATED IN WORKING TREE & TRACKED INDEX; AWAITING OWNER GITHUB SUPPORT PURGE

---

## 1. Executive Summary

This document provides a factual, evidence-based architectural record of historical sensitive data exposure in the public repository `m-rehman55/ai-tool-gems`. It clearly distinguishes between **current-tree removal** (files removed from the active branch filesystem and Git index) and **historical git object persistence** (commits and blobs cached in GitHub's internal database).

The unredacted support ticket draft and sensitive commit inventory are securely maintained in private/local gitignored storage (`data/reports/PRIVATE_GITHUB_SUPPORT_ESCALATION.md` and `data/reports/PRIVATE_HISTORICAL_EXPOSURE_INVENTORY.md`) to prevent exposing incident details in the public Git history.

---

## 2. Multi-Layer Git State Distinctions

| Layer | Status | Technical Reality | Verification Evidence |
| :--- | :---: | :--- | :--- |
| **Current Working Tree (`main`)** | **CLEAN** | Zero customer order data, zero credentials, zero supplier wholesale price lists. | Verified via `git ls-files` |
| **Release PR #16 (`release/security-pages-hardening`)** | **CLEAN** | All legacy diagnostic reports untracked; fail-closed allowlist builder enforced; boundary tests active. | Verified via `tests/test_public_repository_boundary.py` (Exit code 0) |
| **Content PR #17 (`content/wave1-category-hubs-staged`)** | **CLEAN** | Staged category hubs strictly non-indexed; zero private data. | Verified via `scripts/build_public_site.py --verify-only` (Exit code 0) |
| **Active Git Branches & Tags** | **CLEAN** | No active branch or release tag references historical commits containing order data. | Verified via `git branch -a --contains` (0 matches) |
| **GitHub Backend Object Storage (PR Refs)** | **EXPOSED IN CACHE** | Historical pull requests (#13, #14, #15) preserve unreachable commits in GitHub's internal refstore. | Direct HTTP queries return HTTP 200 for commit URLs |

---

## 3. Confirmed Exposure Reality

Direct HTTP verification on 2026-11-07 confirms that while active branches are clean:
1. Historical commits associated with closed pull requests remain cached on GitHub's web servers.
2. Direct raw URL access to historical blob objects returns HTTP 200 until server-side garbage collection is triggered.
3. Squash-merging or deleting local branches controls the commit history introduced into `main`, but does not delete cached objects from GitHub's internal storage.

---

## 4. Remediation Architecture & Governance

To ensure comprehensive, defense-in-depth protection:

1. **Working Tree & Tracking Protection (Completed):**
   - All private paths (`data/orders/`, `data/suppliers/`, `data/wholesale_*.json`, `reports/`) are quarantined in `.gitignore`.
   - Automated unit tests (`tests/test_public_repository_boundary.py`) run in CI to block any re-introduction of prohibited paths.

2. **Public Deployment Artifact Allowlist (Completed):**
   - GitHub Pages deployment utilizes `scripts/build_public_site.py`, which copies only strictly approved public files to `public-site/`.
   - Verified by `tests/test_public_deployment_allowlist.py`.

3. **Server-Side Cache Purge (Awaiting Owner Action):**
   - A complete, unredacted escalation package is provided in the repository owner's private local environment (`data/reports/PRIVATE_GITHUB_SUPPORT_ESCALATION.md`).
   - The repository owner must submit this request to GitHub Support to execute `git gc --prune=now` and permanently purge unreachable dangling commits and closed pull request refs.
