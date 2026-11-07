# GitHub Pages Deployment Guardrails & CI/CD Safety Specification

**Workflow:** [`.github/workflows/deploy-pages.yml`](file:///d:/Desktop/AI%20Tools%20Aura/.github/workflows/deploy-pages.yml)  
**Deployment Target:** GitHub Pages (`aitoolgems.tech`)  
**Environment:** `github-pages`  
**Standard:** Phase 2.1 Least-Privilege & Production Protection Guardrails  
**Effective Date:** 2026-11-07  

---

## 1. Deployment Security Objectives

To ensure zero risk of accidental or unauthorized deployment of development code, experimental branches, or non-main pull requests to the live storefront:
1. **Branch-Restricted Deployment:** Production deployment (`deploy` job) is strictly restricted to `refs/heads/main`.
2. **Safe Pull Request Validation:** Pull requests targeting `main` automatically execute the `build` job to validate asset staging, verify CNAME, and check for leaks, but **never deploy**.
3. **Manual Trigger Safety:** Even if a user manually triggers `workflow_dispatch` from a feature branch (e.g. `release/*` or `feature/*`), the `deploy` job evaluates `if: github.ref == 'refs/heads/main'` and skips deployment.
4. **Least-Privilege Job Permissions:** Each job requests only the precise permissions it requires.

---

## 2. Permissions & Job Architecture Matrix

```
┌────────────────────────────────────────────────────────────────────────┐
│                   DEPLOY-PAGES.YML PIPELINE ARCHITECTURE               │
├───────────────────────────────────┬────────────────────────────────────┤
│             JOB: BUILD            │            JOB: DEPLOY             │
├───────────────────────────────────┼────────────────────────────────────┤
│ Trigger: push to main,            │ Trigger: push to main only         │
│          pull_request to main,    │ Condition:                         │
│          workflow_dispatch        │   github.ref == 'refs/heads/main'  │
│ Permissions:                      │ Permissions:                       │
│   contents: read                  │   pages: write                     │
│                                   │   id-token: write                  │
├───────────────────────────────────┼────────────────────────────────────┤
│ Actions:                          │ Actions:                           │
│ • Checkout repo (depth: 0)        │ • actions/deploy-pages@v4          │
│ • Build public-site/ allowlist    │ • Publishes artifact to Pages      │
│ • Run post-build assertions       │ • Reports live page URL            │
│ • Upload artifact (main only)     │                                    │
└───────────────────────────────────┴────────────────────────────────────┘
```

---

## 3. Mandatory GitHub Repository Settings (Owner Action)

To complete the defense-in-depth posture on GitHub, the repository owner should verify the following settings in the GitHub web interface:

### A. Environment Protection (`Settings -> Environments -> github-pages`)
1. **Deployment branches:** Select **Selected branches** and add rule `main`.  
   *Result:* GitHub's infrastructure will reject any deployment attempt targeted at the `github-pages` environment from non-main branches.
2. **Required reviewers (Optional/Recommended):** Enable required reviewers to mandate explicit owner sign-off before Pages deployment executes.

### B. Pages Publishing Source (`Settings -> Pages`)
1. **Source:** Select **GitHub Actions** (not "Deploy from a branch").  
   *Result:* Pages is populated exclusively by the cryptographically signed `actions/deploy-pages` artifact.
2. **Custom domain:** Ensure custom domain is configured as `aitoolgems.tech`.
3. **Enforce HTTPS:** Ensure **Enforce HTTPS** is checked.

---

## 4. Verification & Testing

1. **Local Build & Validation:**
   ```powershell
   python scripts/build_public_site.py --verify-only
   # Output: VERIFICATION SUCCESS: 313 public files staged with 0 security policy violations.
   ```
2. **Workflow YAML Linting:**
   ```powershell
   python -c "import yaml; yaml.safe_load(open('.github/workflows/deploy-pages.yml', encoding='utf-8')); print('Valid')"
   # Output: Valid
   ```
3. **PR Simulation:**
   On pull requests targeting `main`, the workflow executes `build` only. `actions/upload-pages-artifact` and `deploy` are skipped, preventing artifact creation or production updates.

