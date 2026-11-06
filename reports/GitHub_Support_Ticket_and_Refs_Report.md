# GitHub Support Ticket & Pull Request References Report

**Repository:** `https://github.com/m-rehman55/ai-tool-gems`  
**Account:** `m-rehman55` (Muhammad Rehman Farooq)  
**Date:** 2026-11-07  
**Urgency:** High (Sensitive Operational Data Retention in Cached PR Refs)  

---

## 1. Background & Technical Context

We recently conducted a security history purge to remove an accidentally committed file containing internal offline customer transaction records:
- **Purged File:** `data/orders/verified_orders.json`
- **Initial Commit:** `8d521de0f3eee707722dd7abcb5d82c7d90989b4`
- **First Changed Commit in PRs:** `8d521de0f3eee707722dd7abcb5d82c7d90989b4`

We ran `git-filter-repo` locally and force-pushed clean rewritten histories to our branches. However, commit `8d521de0f3` remains reachable over the GitHub REST API and commit view because GitHub retains hidden pull request head references (`refs/pull/*/head`) for closed pull requests.

Because `refs/pull/*` are immutable to Git clients (`! [remote rejected] (deny updating a hidden ref)`), repository administrators cannot delete them via `git push origin :refs/pull/...`. We request that GitHub Support prune the tainted pull request refs and execute repository garbage collection.

---

## 2. Copy-Ready GitHub Support Ticket

**Submission Channel:** https://support.github.com/contact (Select: **Account or repository data removal / Git cache**)

```markdown
Subject: Request to prune cached pull request refs and run repository GC (Purge sensitive data)

Dear GitHub Support Team,

I am the owner of the public repository:
https://github.com/m-rehman55/ai-tool-gems

We have completed a repository rewrite using git-filter-repo to remove an internal operational file (`data/orders/verified_orders.json`) that was inadvertently committed to feature branches.

All our active branches (including `main`) have been cleaned and verified. However, the sensitive commit remains accessible via the GitHub commit view and commit-addressed API:
https://github.com/m-rehman55/ai-tool-gems/commit/8d521de0f3eee707722dd7abcb5d82c7d90989b4

Our `git ls-remote` audit confirms this commit is kept alive solely by cached pull request head references on two closed pull requests:
- PR #13 (Closed): `refs/pull/13/head` -> `76d45a7a195b9422931a6f7ea26fe08640aa621c`
- PR #14 (Closed): `refs/pull/14/head` -> `76d45a7a195b9422931a6f7ea26fe08640aa621c`

Both PR #13 and PR #14 are closed and will never be merged. Client-side attempts to delete these hidden refs (`git push origin :refs/pull/13/head`) are rejected with `deny updating a hidden ref`.

We respectfully request GitHub Support to:
1. Delete or prune `refs/pull/13/head` and `refs/pull/14/head` (and any associated merge cache refs for PR #13 and PR #14).
2. Run backend garbage collection and reflog expiration (`git gc --prune=now`) on `m-rehman55/ai-tool-gems` to permanently remove unreferenced commit `8d521de0f3eee707722dd7abcb5d82c7d90989b4` and its descendants.

Thank you very much for your prompt assistance in protecting sensitive data.

Sincerely,
Muhammad Rehman Farooq
Repository Owner: m-rehman55
Email: m-rehman55@users.noreply.github.com
```

---

## 3. Pre-Submission vs Post-Submission Verification

The repository owner can test the state of the purge at any time using the following CLI commands:

### A. Pre-Ticket Verification (Current Behavior - Confirms Reachability)
```powershell
# Check if commit 8d521de0f3 is still returned by the API (HTTP 200)
gh api repos/m-rehman55/ai-tool-gems/commits/8d521de0f3eee707722dd7abcb5d82c7d90989b4 --jq "{sha: .sha, status: 'STILL REACHABLE'}"
```
*Current output:*
`{"sha": "8d521de0f3eee707722dd7abcb5d82c7d90989b4", "status": "STILL REACHABLE"}`

### B. Post-Ticket Verification (Expected Behavior after GitHub Acts)
```powershell
# Once GitHub Support prunes refs and runs GC, this command MUST return HTTP 404 (Not Found)
gh api repos/m-rehman55/ai-tool-gems/commits/8d521de0f3eee707722dd7abcb5d82c7d90989b4
```
*Expected output:*
`gh: Not Found (HTTP 404)`

### C. Verify Remote Refs
```powershell
# Confirm that refs/pull/13/head and refs/pull/14/head are no longer listed
git ls-remote origin "refs/pull/*" | Select-String "refs/pull/13|refs/pull/14"
```
*Expected output:*
*(No output - references successfully removed)*
