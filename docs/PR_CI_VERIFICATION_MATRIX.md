# Machine-Readable PR & CI Verification Matrix

**Document ID:** ATG-CI-MATRIX-001  
**Audit Phase:** Phase 2.2 Final Independent Release Verification  
**Repository:** `m-rehman55/ai-tool-gems`  
**Generated At:** 2026-11-07T06:48:00+05:00  

---

## 1. Pull Request Core Metadata Matrix

| Property | Pull Request A (PR #16) | Pull Request B (PR #17) |
| :--- | :--- | :--- |
| **Pull Request URL** | `https://github.com/m-rehman55/ai-tool-gems/pull/16` | `https://github.com/m-rehman55/ai-tool-gems/pull/17` |
| **Title** | `feat(release): PR A - Public Data Security, GitHub Pages Deployment Allowlist & Analytics Hardening` | `feat(content): PR B - Wave 1 Category Hubs (AI Chatbots, AI Video, AI Design) [Staged noindex]` |
| **State** | `OPEN` | `OPEN` |
| **Base Branch (`base.ref`)** | `main` | `release/security-pages-hardening` |
| **Base Commit SHA (`base.sha`)** | `418fc477084c4ebb393b3c5cb6abb40b27e1fc36` | `00902e17a3a82df31c79fb4b18c50ecb79f649f9` |
| **Head Branch (`head.ref`)** | `release/security-pages-hardening` | `content/wave1-category-hubs-staged` |
| **Head Commit SHA (`head.sha`)** | `00902e17a3a82df31c79fb4b18c50ecb79f649f9` | `9d2aac9e2ea4eeec5f5df6d45903b6009ae84c98` |
| **Mergeability (`mergeable`)** | `true` | `true` |
| **Mergeable State** | `clean` | `clean` |
| **Changed Files Count** | `40` | `5` |
| **Auto-Merge Policy** | `disabled` | `disabled` |

---

## 2. Check Runs Matrix for PR #16 Head (`00902e17`)

Commit: [`00902e17a3a82df31c79fb4b18c50ecb79f649f9`](https://github.com/m-rehman55/ai-tool-gems/commit/00902e17a3a82df31c79fb4b18c50ecb79f649f9)

| Check Run Name | Status | Conclusion | Run Duration | Check Run URL |
| :--- | :---: | :---: | :---: | :--- |
| **CodeQL** | `completed` | **`success`** | 3s | `https://github.com/m-rehman55/ai-tool-gems/runs/128260918294` |
| **Build & Validate Public Artifact** | `completed` | **`success`** | 13s | `https://github.com/m-rehman55/ai-tool-gems/actions/runs/42325809822/job/128260739749` |
| **Deploy to GitHub Pages** | `completed` | **`skipped`** | 0s | `https://github.com/m-rehman55/ai-tool-gems/actions/runs/42325809822/job/128260811771` |
| **Analyze Code Security (JS/TS)** | `completed` | **`success`** | 53s | `https://github.com/m-rehman55/ai-tool-gems/actions/runs/42325809823/job/128260708335` |
| **Analyze Code Security (Python)** | `completed` | **`success`** | 54s | `https://github.com/m-rehman55/ai-tool-gems/actions/runs/42325809823/job/128260707996` |
| **test** (Root Regression Suite) | `completed` | **`success`** | 9s | `https://github.com/m-rehman55/ai-tool-gems/actions/runs/42325809789/job/128260707475` |
| **validate** (HERMES Engine) | `completed` | **`success`** | 25s | `https://github.com/m-rehman55/ai-tool-gems/actions/runs/42325809839/job/128260708187` |

**PR #16 CI Outcome:** 6 Successes, 1 Intentionally Skipped (Deploy to Pages), 0 Failures. **100% GREEN.**

---

## 3. Check Runs Matrix for PR #17 Head (`9d2aac9e`)

Commit: [`9d2aac9e2ea4eeec5f5df6d45903b6009ae84c98`](https://github.com/m-rehman55/ai-tool-gems/commit/9d2aac9e2ea4eeec5f5df6d45903b6009ae84c98)

| Check Run Name | Status | Conclusion | Run Duration | Check Run URL |
| :--- | :---: | :---: | :---: | :--- |
| **CodeQL** | `completed` | **`success`** | 2s | `https://github.com/m-rehman55/ai-tool-gems/runs/128261009214` |
| **Build & Validate Public Artifact** | `completed` | **`success`** | 9s | `https://github.com/m-rehman55/ai-tool-gems/actions/runs/42325835466/job/128260812213` |
| **Deploy to GitHub Pages** | `completed` | **`skipped`** | 0s | `https://github.com/m-rehman55/ai-tool-gems/actions/runs/42325835466/job/128260863666` |
| **Analyze Code Security (JS/TS)** | `completed` | **`success`** | 56s | `https://github.com/m-rehman55/ai-tool-gems/actions/runs/42325835411/job/128260791197` |
| **Analyze Code Security (Python)** | `completed` | **`success`** | 55s | `https://github.com/m-rehman55/ai-tool-gems/actions/runs/42325835411/job/128260791410` |
| **validate** (HERMES Engine) | `completed` | **`success`** | 15s | `https://github.com/m-rehman55/ai-tool-gems/actions/runs/42325835465/job/128260791541` |

**PR #17 CI Outcome:** 5 Successes, 1 Intentionally Skipped (Deploy to Pages), 0 Failures. **100% GREEN.**

---

## 4. Pages Deployment Guardrail Verification

### Architectural Guardrail:
In `.github/workflows/deploy-pages.yml`:
```yaml
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
```

### Empirical Proof of Guardrail:
1. When PR #16 ran, `github.ref` was `refs/pull/16/merge`.
   - Result: `Build & Validate Public Artifact` ran and succeeded in 13 seconds.
   - Result: `Deploy to GitHub Pages` was evaluated as false and **skipped** (`conclusion: skipped`).
2. When PR #17 ran, `github.ref` was `refs/pull/17/merge`.
   - Result: `Build & Validate Public Artifact` ran and succeeded in 9 seconds.
   - Result: `Deploy to GitHub Pages` was evaluated as false and **skipped** (`conclusion: skipped`).
3. GitHub Environment Protection:
   - Query to `repos/m-rehman55/ai-tool-gems/environments/github-pages/deployment-branch-policies` confirms that deployment is restricted to branches matching `main` or `gh-pages`. Any other branch is blocked at the GitHub infrastructure level.

---

## 5. Distinction: Mergeability vs CI Verification

- **Mergeability (`mergeable: true`, `mergeable_state: clean`):**
  - Confirms solely that Git's three-way merge algorithm (`git merge-base`) can integrate the pull request into its target branch without encountering conflicting changes in identical file lines.
  - Does NOT assess code security, runtime exceptions, syntax errors, or data leakage risks.
- **CI Verification (`check_runs: all success/skipped`):**
  - Evaluates actual execution: CodeQL vulnerability scans, AST syntax compilation, affirmative allowlist enforcement, custom domain assertions, and regression test suites.
  - **Verdict:** Both PR #16 and PR #17 satisfy **BOTH** criteria independently.
