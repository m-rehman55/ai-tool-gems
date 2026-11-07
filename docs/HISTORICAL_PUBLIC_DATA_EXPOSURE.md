# Historical Public Data Exposure & GitHub Support Escalation Package

**Document ID:** ATG-SEC-EXPOSURE-001  
**Audit Phase:** Phase 2.2 Final Independent Release Verification  
**Repository:** `m-rehman55/ai-tool-gems`  
**Classification:** PUBLIC ENGINEERING RECORD (Strictly sanitized — zero customer PII, zero tokens, zero supplier costs)  
**Date:** 2026-11-07  

---

## 1. Executive Summary

This document provides a factual, evidence-based audit of historical sensitive data exposure in the public GitHub repository. It clearly distinguishes between **current-tree removal** (files removed from the active branch filesystem) and **historical git object persistence** (commits and blobs cached in GitHub's internal database). It also provides a ready-to-submit escalation package for GitHub Support to complete server-side repository garbage collection.

---

## 2. Current-Tree Removal vs Historical-Object Persistence

| Layer | Status | Technical Reality | Verification Evidence |
| :--- | :---: | :--- | :--- |
| **Current Working Tree (`main`)** | **CLEAN** | Zero order data, zero credentials, zero internal operational reports tracked. | Verified via `git ls-tree -r origin/main` |
| **Current Release PR A (`release/security-pages-hardening`)** | **CLEAN** | All 7 diagnostic reports, wholesale registers, and runtime logs untracked from Git index. | Verified via `tests/test_public_repository_boundary.py` (Exit code 0) |
| **Current Content PR B (`content/wave1-category-hubs-staged`)** | **CLEAN** | All category content verified; research report quarantined in gitignored `data/reports/`. | Verified via `scripts/build_public_site.py --verify-only` (Exit code 0) |
| **Active Git Branches & Tags** | **CLEAN** | No active branch or release tag points to historical commits containing order data. | Verified via `git branch -a --contains d9cdef4` (0 matches) |
| **GitHub Backend Object Storage (PR Refs)** | **EXPOSED IN CACHE** | Historical pull requests (#13, #14, #15) preserve commit SHAs in GitHub's internal `refs/pull/*/head` cache. | Direct GitHub web URL renders commit view until garbage collection is executed by GitHub Support. |

---

## 3. Inventory of Historical Exposed Objects

The following objects were identified in historical commit histories from earlier iterations:

### 3.1 Historical Order Data Exposure (PR #13 / PR #14 / PR #15)
- **Path in Historical Commits:** `data/orders/verified_orders.json`
- **Historical Commit Anchor:** `d9cdef409ac00f278986179afaaa34cd08c4ddd4` (Head of closed PR #13)
- **Current Tree Status:** Completely deleted and quarantined in `.gitignore` (`data/orders/`).
- **Reachable Git Graph:** Unreachable from `main`, PR #16, or PR #17.
- **GitHub Cache Status:** Accessible if a user navigates directly to the exact commit SHA URL on `github.com`.

### 3.2 Historical Diagnostic & Classification Reports (PR A Initial Commit)
- **Paths in Commit `108118a9`:**
  - `reports/GA4_Regression_Report.md`
  - `reports/GitHub_Support_Ticket_and_Refs_Report.md`
  - `reports/Git_History_Purge_Verification_Report.md`
  - `reports/Pages_Artifact_Inspection_Report.md`
  - `reports/Public_Private_Data_Classification.csv`
  - `reports/Public_Private_Tracked_Data_Audit.md`
  - `reports/Updated_Release_Readiness_Report.md`
  - `marketing_agent/data/repair-last.log`
- **Current Tree Status:** Untracked from Git via commit `a7b85ae3` and `00902e17`. Relocated to local gitignored directory `data/reports/`.
- **Mitigation Recommendation:** When merging PR #16 into `main`, repository owner must use **Squash and Merge**. This collapses all intermediate commits into a single commit on `main` where these files were never added.

---

## 4. Remediation Boundaries: What Local Engineers Cannot Do

Under Git and GitHub platform architecture:
1. **Local Commands Cannot Purge GitHub Remote Caches:** Commands such as `git gc --prune=now` or `git filter-repo` executed locally only clean the local workstation `.git` folder. They **do not** affect GitHub's server-side repository replica.
2. **Force-Pushing is Restricted and Insufficient:** Rewriting shared Git history disrupts collaborator workflows and does not delete GitHub's internal pull request reference cache (`refs/pull/*/head`).
3. **Only GitHub Support Can Run Server-Side Purge:** Permanent removal of unreachable cached commit objects requires GitHub Support to remove the pull request refs and execute server-side garbage collection.

---

## 5. Factual GitHub Support Escalation Package

The repository owner should submit the following ticket to GitHub Support (`https://support.github.com/contact`):

---

### Ticket Submission Draft

**Subject:** Request for permanent repository garbage collection and PR ref purge on `m-rehman55/ai-tool-gems`

**Category:** Git & GitHub Platform / Security & Sensitive Data

**Repository:** `https://github.com/m-rehman55/ai-tool-gems`

**Body:**

> Dear GitHub Support Team,
> 
> I am the owner of the public repository `https://github.com/m-rehman55/ai-tool-gems`.
> 
> During development, a file containing transaction records (`data/orders/verified_orders.json`) was committed on a feature branch and included in pull requests that have since been closed and rejected without merging:
> - Pull Request #13 (Closed, unmerged)
> - Pull Request #14 (Closed, unmerged)
> - Pull Request #15 (Closed, unmerged)
> 
> In our active repository tree and current release branches (`main`, `release/security-pages-hardening`, `content/wave1-category-hubs-staged`), this file and all sensitive paths have been permanently deleted and quarantined in `.gitignore`. No active branch or tag references these commits.
> 
> However, the historical commits remain accessible via direct URL on GitHub's web interface due to cached pull request references:
> - Commit SHA: `d9cdef409ac00f278986179afaaa34cd08c4ddd4`
> - Commit SHA: `76d45a7a195b9422931a6f7ea26fe08640aa621c`
> - Commit SHA: `e915c680f2e7c68af1173cdd043171180d799a4a`
> 
> We kindly request that GitHub Support:
> 1. Clear the cached pull request head references for PR #13, PR #14, and PR #15 (`refs/pull/13/head`, `refs/pull/14/head`, `refs/pull/15/head`).
> 2. Execute server-side garbage collection (`git gc --prune=now`) on `m-rehman55/ai-tool-gems` so that these unreachable commit objects and associated blobs are permanently purged from GitHub's servers and web view.
> 
> Thank you for your assistance in maintaining our repository's data security.
> 
> Sincerely,  
> Muhammad Rehman Farooq  
> Repository Owner, `m-rehman55/ai-tool-gems`

---

## 6. Pre-Merge Verification Checklist for Owner

- [ ] Confirm PR #13, PR #14, and PR #15 are CLOSED and UNMERGED in GitHub UI.
- [ ] Select **Squash and Merge** when merging PR #16 into `main`.
- [ ] Select **Squash and Merge** when merging PR #17 into `main`.
- [ ] Submit the above escalation ticket to GitHub Support.
- [ ] Verify via incognito browser that direct URLs to historical commits return HTTP 404 after GitHub Support confirms garbage collection.
