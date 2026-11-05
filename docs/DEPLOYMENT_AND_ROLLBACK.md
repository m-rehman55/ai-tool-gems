# DEPLOYMENT AND ROLLBACK PROCEDURES
**Target Environment**: GitHub Pages (`https://aitoolgems.tech/`)  
**Production Branch**: `main`  
**Development Branch**: Feature branches (`feature/*`, `fix/*`, `content/*`)  

---

## 1. Controlled Deployment Lifecycle

```
[Local Feature Branch]
         │
         ▼
[Local Quality Gates] (Unit Tests, Link Graph Checker, Schema Audit)
         │
         ▼
[Push to Origin Feature Branch]
         │
         ▼
[Open Pull Request against main]
         │
         ▼
[CI Validation Workflow] (Tests + Security + Scope Guard)
         │
         ▼
[Human Review & Merge to main]
         │
         ▼
[GitHub Pages Build & Deploy]
         │
         ▼
[Live Production Verification] (HTTP 200, Canonical, Schema, CWV)
         │
         ▼
[IndexNow Selective Ping for Modified URLs]
```

---

## 2. Mandatory Pre-Merge Test Gates

Before any pull request can be merged into `main`, the following automated commands must pass 100%:

```bash
# 1. Full integrity and unit test suite
python -m unittest discover -s tests -v

# 2. Specialized agent unit tests
python -m unittest discover -s keyword_agent/tests -v
python -m unittest discover -s aio_agent/tests -v
python -m unittest discover -s ping_agent/tests -v
python -m unittest discover -s seo-agent/tests -v
python -m unittest discover -s marketing_agent/tests -v

# 3. Strict internal link graph and route validation
python scripts/link_graph_checker.py --strict

# 4. Technical and Schema audits
python audit_all.py
python schema_audit.py
```

---

## 3. Post-Deployment Production Verification

After deployment, run `scripts/verify_live_deployment.py` to confirm that:
1. Production returns HTTP 200 for newly published routes.
2. Canonical tags match the live production URL (`https://aitoolgems.tech/...`).
3. Title, H1, and Meta Description match the approved release.
4. JSON-LD schema parses cleanly with 0 errors.

---

## 4. Emergency Rollback Protocol

If a production defect or regression is detected on `https://aitoolgems.tech/`:

1. **Revert Commit**:
   ```bash
   git checkout main
   git pull origin main
   git revert <DEFECTIVE_COMMIT_SHA> -m 1
   git push origin main
   ```
2. **Await GitHub Pages Deployment**: Monitor `gh api repos/:owner/:repo/pages/builds/latest` until status is `built`.
3. **Verify Reversion Live**: Confirm live endpoint returns the previous stable state or clean 404/redirect.
4. **IndexNow Purge / Update**: If a defective URL was removed, dispatch an IndexNow ping with the deleted/updated URL to ensure search engines purge the defective state immediately.
