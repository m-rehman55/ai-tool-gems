# Final Repository Owner Release Checklist & Governance Register

- **Target Domain:** `https://aitoolgems.tech/`
- **Repository:** `m-rehman55/ai-tool-gems`
- **Primary Market:** Pakistan
- **Audit Date:** 2026-11-07 (PKT UTC+05:00)
- **Status:** ACTION REQUIRED BY REPOSITORY OWNER BEFORE PRODUCTION MERGE

---

## 1. Executive Summary

This checklist outlines the **8 independent decisions** and manual platform actions required from repository owner **Muhammad Rehman Farooq** before merging Pull Request #16 and Pull Request #17 into `main`.

All automated technical, security, and quality controls have passed (**213 unique unit tests passing**, 0 CodeQL alerts, 0 link graph errors). Production changes remain strictly under the owner's authority.

---

## 2. Owner Decisions & Platform Actions Register

| # | Priority | Decision / Action Description | Portal / Location | Status | Action Required |
| :-: | :---: | :--- | :--- | :---: | :--- |
| **1** | **CRITICAL** | **Migrate GitHub Pages Publishing Source to GitHub Actions** | `Settings -> Pages -> Build and deployment -> Source` | **BLOCKED_OWNER** | Switch dropdown from `Deploy from a branch` to `GitHub Actions`. (Details: `docs/PAGES_PUBLISHING_SOURCE_VERIFICATION.md`) |
| **2** | **HIGH** | **Enable Branch Protection on `main`** | `Settings -> Branches -> Add branch ruleset` | **BLOCKED_OWNER** | Configure ruleset requiring PR, status checks (`build-and-validate`, `test`, `validate`, `Analyze Code Security`), and blocking force pushes. |
| **3** | **HIGH** | **Approve Public Tracked File Classification** | Repository Review | **READY** | Review `docs/PUBLIC_TRACKED_FILE_CLASSIFICATION.md` confirming untracking of legacy diagnostic reports and quarantine of sensitive paths. |
| **4** | **HIGH** | **Submit GitHub Support Escalation Ticket** | `https://support.github.com/contact` | **BLOCKED_OWNER** | Submit the unredacted ticket draft in `data/reports/PRIVATE_GITHUB_SUPPORT_ESCALATION.md` to trigger `git gc` on dangling PR commits. |
| **5** | **HIGH** | **Approve & Merge PR #16** | `https://github.com/m-rehman55/ai-tool-gems/pull/16` | **BLOCKED_OWNER** | Review `docs/PR_16_FINAL_REVIEW.md` and select **Squash and Merge** into `main` after Decisions 1 and 2 are executed. |
| **6** | **MEDIUM** | **Confirm Commercial Resale Terms** | Commercial Policy | **APPROVED** | Confirm Pakistani pricing (Flat PKR), domestic rails (EasyPaisa, JazzCash, SadaPay, Bank IBFT), and WhatsApp delivery. |
| **7** | **MEDIUM** | **Approve & Merge PR #17** | `https://github.com/m-rehman55/ai-tool-gems/pull/17` | **BLOCKED_OWNER** | Follow `docs/PR_17_POST_PR16_REBASE_PLAN.md` to rebase PR #17 onto `main` and squash-merge after PR #16 is live. |
| **8** | **POLICY** | **Retain Category Hub `noindex, follow` Safeguard** | SEO Policy | **HOLD_SAFE** | Retain `<meta name="robots" content="noindex, follow">` on category hubs during initial deployment; decide on indexing in a future PR. |

---

## 3. Recommended Branch Protection Configuration (Decision 2 Details)

In **Settings -> Rules -> Rulesets -> New branch ruleset** for branch `main`:
1. **Ruleset Name:** `Main Production Protection`
2. **Enforcement Status:** `Active`
3. **Target branches:** Include default branch (`main`).
4. **Rules to enable:**
   - [x] **Restrict deletions**
   - [x] **Block force pushes**
   - [x] **Require a pull request before merging:**
     - Allowed merge methods: Squash merge, Rebase merge.
     - *(Single-owner note: Do not require approvals if you are the sole committer, to avoid lockout).*
   - [x] **Require status checks to pass before merging:**
     - Require branches to be up to date before merging.
     - Select checks:
       - `Build & Validate Public Artifact` (`deploy-pages.yml`)
       - `test` (`deploy-pages.yml`)
       - `validate` (`seo-agent-validation.yml`)
       - `Analyze Code Security JS/TS` (`codeql.yml`)
       - `Analyze Code Security Python` (`codeql.yml`)
     - *(Do NOT require `Deploy to GitHub Pages`, as it only runs on push to `main`).*

---

## 4. Post-Merge Production Verification Protocols

### Protocol A: Verification Following PR #16 Merge
After the owner squash-merges PR #16:
1. Navigate to **Actions** tab in GitHub and monitor `.github/workflows/deploy-pages.yml`.
2. Confirm `Build & Validate Public Artifact` generates `public-site/` with 316 assets.
3. Confirm `Deploy to GitHub Pages` completes with exit status **Success**.
4. Verify HTTP 200 and HTTPS on `https://aitoolgems.tech/`.
5. Verify CNAME and SSL certificate remain active.
6. Verify no diagnostic report or internal data file is reachable:
   - `curl -I https://aitoolgems.tech/reports/architecture/audit_summary.md` -> Must return **404**.
   - `curl -I https://aitoolgems.tech/data/wholesale_inventory.json` -> Must return **404**.
   - `curl -I https://aitoolgems.tech/marketing_agent/data/repair-last.log` -> Must return **404**.
7. Perform passive GA4 network inspection (Procedure A in `docs/GA4_PRODUCTION_VERIFICATION_PLAN.md`).

### Protocol B: Verification Following PR #17 Merge
After PR #17 is rebased and merged:
1. Verify the 3 category URLs return HTTP 200:
   - `curl -I https://aitoolgems.tech/category/ai-chatbots/` -> **200**
   - `curl -I https://aitoolgems.tech/category/ai-video/` -> **200**
   - `curl -I https://aitoolgems.tech/category/ai-design/` -> **200**
2. Inspect HTML source and confirm `<meta name="robots" content="noindex, follow">` is physically present.
3. Inspect `https://aitoolgems.tech/sitemap.xml` and assert category URLs are excluded.

---

## 5. Emergency Rollback Reference

If any issue arises during or after production deployment:
- **Pre-Release Rollback Commit:** **`418fc477084c4ebb393b3c5cb6abb40b27e1fc36`** on `main`.
- **Revert Command:**
  ```bash
  git checkout main
  git revert -m 1 <MERGE_COMMIT_SHA>
  git push origin main
  ```

