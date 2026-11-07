# PR #17 Post-PR #16 Rebase & Sequential Merge Protocol

- **Repository:** `m-rehman55/ai-tool-gems`
- **Stacked Dependency:** `main` → `release/security-pages-hardening` (PR #16) → `content/wave1-category-hubs-staged` (PR #17)
- **Base PR:** PR #16 (`release/security-pages-hardening`)
- **Dependent PR:** PR #17 (`content/wave1-category-hubs-staged`)
- **Audit Date:** 2026-11-07 (PKT UTC+05:00)
- **Status:** READY FOR SEQUENCED EXECUTION

---

## 1. Executive Summary

Pull Request #17 contains the Wave 1 Category Hubs for AIToolGems (`category/ai-chatbots/`, `category/ai-video/`, `category/ai-design/`). It is architecturally stacked directly upon PR #16 (`release/security-pages-hardening`).

Because PR #17 branches off PR #16, **merging PR #17 before PR #16 is strictly prohibited**. This document outlines the exact, conflict-free procedure for rebasing and merging PR #17 once PR #16 has been approved and merged into `main` by the repository owner.

---

## 2. Content Safeguards & Indexing Policy Active in PR #17

All category hub content in PR #17 has been audited against SEO safety gates:

| Safeguard | Enforcement Mechanism | Verification Status |
| :--- | :--- | :---: |
| **Robots Directive** | `<meta name="robots" content="noindex, follow">` present on all 3 pages | **PASS (HOLD_SAFE)** |
| **Self-Referential Canonical** | Explicit canonical URLs pointing to `https://aitoolgems.tech/category/*/` | **PASS** |
| **Sitemap Exclusion** | Category URLs are strictly omitted from `sitemap.xml` | **PASS** |
| **Internal Linking** | Contextual footer links and header navigation integrate seamlessly | **PASS** |
| **Allowlist Staging** | `scripts/build_public_site.py` includes `"category"` in `APPROVED_PUBLIC_DIRS` | **PASS** |

> [!IMPORTANT]
> The `noindex, follow` directive must **NOT** be removed during this release. The category pages will be deployed in a staged, non-indexed state to allow the owner to review live mobile styling and conversion layouts on production before indexing.

---

## 3. Step-by-Step Post-PR #16 Rebase & Merge Procedure

Follow this sequential workflow after the owner merges PR #16:

### Step 1: Update Local Repository State
Ensure all remote changes from `origin` are fetched locally:
```bash
git fetch origin
git checkout main
git pull origin main
```

### Step 2: Switch PR #17 Base Branch in GitHub UI
1. Navigate to: **`https://github.com/m-rehman55/ai-tool-gems/pull/17`**
2. Click **"Edit"** next to the PR title.
3. Change the **base branch** dropdown from:
   - `release/security-pages-hardening`
   to:
   - **`main`**
4. Save the base change.

### Step 3: Rebase PR #17 Onto Updated `main`
Execute the git rebase using the explicit upstream boundary:
```bash
git checkout content/wave1-category-hubs-staged
git rebase origin/main
```
*(If any minor metadata conflict occurs, keep the incoming commit from PR #17, run `git rebase --continue`).*

### Step 4: Push Rebased Branch to GitHub
Push the clean, linearized history with safety lease:
```bash
git push --force-with-lease origin content/wave1-category-hubs-staged
```

### Step 5: Verify CI Check Runs on PR #17
Wait for GitHub Actions to complete on PR #17:
- Verify `CodeQL` passes (0 alerts).
- Verify `Build & Validate Public Artifact` passes.
- Verify `test` runs all 213 unique unit tests with 100% green exit code.
- Verify `validate` passes SEO scope checks.

### Step 6: Owner Merges PR #17
Once all checks are green and the owner approves the content:
- Select **Squash and Merge** to merge PR #17 into `main`.
- Production deployment workflow will automatically publish the 3 staged category hubs to `https://aitoolgems.tech/category/*/`.

---

## 4. Post-Merge Live Production Verification

After PR #17 merges and deploys:
1. Curl the 3 category URLs and assert HTTP 200:
   - `curl -I https://aitoolgems.tech/category/ai-chatbots/`
   - `curl -I https://aitoolgems.tech/category/ai-video/`
   - `curl -I https://aitoolgems.tech/category/ai-design/`
2. Inspect the HTTP response / DOM:
   - Assert `<meta name="robots" content="noindex, follow">` is physically present.
   - Assert canonical link equals target URL.
3. Fetch `https://aitoolgems.tech/sitemap.xml` and confirm category URLs do **NOT** appear in the sitemap.

