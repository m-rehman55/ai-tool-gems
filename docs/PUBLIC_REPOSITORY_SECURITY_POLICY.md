# Public Repository Security, Quarantine Boundary & Disclosure Policy

**Repository:** `https://github.com/m-rehman55/ai-tool-gems`  
**Deployment Surface:** `https://aitoolgems.tech/` (GitHub Pages)  
**Standard:** Phase 2.1 Public Repository & Deployment Boundary Specification  
**Classification:** Public Information Architecture & Governance Specification  
**Effective Date:** 2026-11-07  

---

## 1. Architectural Distinction: Public Git Repository vs. Public GitHub Pages

A critical security principle governs the architecture of AI Tool Gems:
- **Public GitHub Repository (`github.com/m-rehman55/ai-tool-gems`):** Any file committed and pushed to any branch in this repository is immediately viewable, downloadable, and indexed by anyone with internet access.
- **Public GitHub Pages Deployment (`aitoolgems.tech`):** The static customer-facing storefront served from GitHub Pages.

> [!CRITICAL]
> Excluding an operational or diagnostic file from the GitHub Pages deployment artifact (`public-site/`) **does NOT** make that file private if it remains tracked in the public Git repository. 
> To achieve genuine confidentiality, operational data, wholesale costs, customer records, supplier bots, service credentials, and internal incident drafts must be **strictly excluded from Git tracking** via `.gitignore` and kept local or in an external private datastore.

---

## 2. Comprehensive File Inventory & 3-Tier Classification

The repository files are strictly divided into three distinct operational groups:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        AI TOOL GEMS ARCHITECTURE                       │
├─────────────────────────┬──────────────────────┬───────────────────────┤
│         GROUP A         │       GROUP B        │        GROUP C        │
│    Private Internal     │   Sanitized Public   │  Synthetic Test / QA  │
│       Operational       │   Customer-Facing    │       Fixtures        │
├─────────────────────────┼──────────────────────┼───────────────────────┤
│ • Customer orders       │ • Homepage / Tools   │ • Synthetic JSONs     │
│ • Wholesale supplier    │ • Guides & Blog      │ • Mock client_ids     │
│   costs & margins       │ • Assets / CSS / JS  │ • Regression suites   │
│ • Telegram bot handles  │ • CNAME / Sitemap    │ • Unit test mocks     │
│ • API secrets & keys    │ • Robots / LLMs.txt  │                       │
│ • Internal audit logs   │ • Public Docs        │                       │
├─────────────────────────┼──────────────────────┼───────────────────────┤
│ ACTION:                 │ ACTION:              │ ACTION:               │
│ Gitignored locally &    │ Tracked in Git;      │ Tracked in Git;       │
│ strictly excluded from  │ Deployed to GitHub   │ Excluded from public  │
│ public deployment       │ Pages via allowlist  │ Pages deployment      │
└─────────────────────────┴──────────────────────┴───────────────────────┘
```

### Detailed Inventory & Classification Matrix:

| File / Pattern | Group | Sensitivity | Git Status | Pages Deployment | Justification & Policy |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `data/orders/*` | Group A | **HIGH** | **Gitignored** | Strictly Excluded | Offline customer transaction records and WhatsApp payment confirmations. Never tracked in Git. |
| `data/wholesale_inventory.json` | Group A | **HIGH** | **Gitignored** | Strictly Excluded | Proprietary supplier pricing, Telegram procurement bot IDs, margin formulas. |
| `data/wholesale_cost_reference.json`| Group A | **HIGH** | **Gitignored** | Strictly Excluded | Internal wholesale floor cost modeling. |
| `data/suppliers/*` | Group A | **HIGH** | **Gitignored** | Strictly Excluded | Raw third-party procurement catalogs. |
| `config/*.json` | Group A | **HIGH** | **Gitignored** | Strictly Excluded | Service account private keys, OAuth tokens, API secrets. |
| `data/analytics/*` | Group A | **MEDIUM** | **Gitignored** | Strictly Excluded | Raw local analytics dumps and telemetry caches. |
| `data/snapshots/*` | Group A | **LOW** | **Gitignored** | Strictly Excluded | Local pre-audit rollback snapshots. |
| `reports/GitHub_Support_Ticket_*.md`| Group A | **MEDIUM** | **Gitignored** | Strictly Excluded | Incident drafts referencing historical commit hashes. Must be filed directly with GitHub Support, not committed publicly. |
| `reports/Git_History_Purge_*.md` | Group A | **MEDIUM** | **Gitignored** | Strictly Excluded | Internal diagnostic reports analyzing purge status. |
| `reports/*.csv`, `reports/*.json` | Group A | **MEDIUM** | **Gitignored** | Strictly Excluded | Raw data exports and crawl databases. |
| `admin.html`, `admin.js`, `admin.css` | Group A | **MEDIUM** | Tracked Clean | Strictly Excluded | Developer prototype sandbox. Kept in Git for development, excluded from Pages deployment. |
| `docs/*.md` | Group B | **PUBLIC** | Tracked Clean | Excluded from Pages | Sanitized engineering documentation, architecture specs, and release governance reports. |
| `index.html`, `about.html`, etc. | Group B | **PUBLIC** | Tracked Clean | **Deployed** | Public customer-facing storefront pages with flat PKR pricing. |
| `tools/*/index.html` (40 tools) | Group B | **PUBLIC** | Tracked Clean | **Deployed** | Canonical parent tool pages with PKR pricing and domestic payment rails. |
| `category/*/index.html` (3 hubs) | Group B | **PUBLIC** | Tracked Clean | **Deployed (noindex)** | Staged category taxonomy hubs. |
| `guides/*/`, `blog/*/` | Group B | **PUBLIC** | Tracked Clean | **Deployed** | Long-form informational and comparative guides. |
| `assets/*` | Group B | **PUBLIC** | Tracked Clean | **Deployed** | Public brand marks, product logos, icons, and stylesheets. |
| `CNAME`, `robots.txt`, `sitemap.xml` | Group B | **PUBLIC** | Tracked Clean | **Deployed** | Search engine discovery directives and domain mapping. |
| `tests/*` | Group C | **SYNTHETIC**| Tracked Clean | Strictly Excluded | Automated regression test suites using synthetic mock data. |

---

## 3. Incident Analysis & Historical Git Availability

### Critical Git Principle:
> Deleting a file from the latest commit (`HEAD`) **does not** erase that file from historical Git commits. Any user who clones the repository or accesses the commit-addressed GitHub API can retrieve historical commits unless they are purged and garbage-collected upstream.

### Historical Purge Status:
1. **Purged File:** `data/orders/verified_orders.json` (accidentally committed in historical commit `8d521de0f3eee707722dd7abcb5d82c7d90989b4`).
2. **Current Branches (100% Clean):**  
   - `origin/main` (`418fc477084c4ebb393b3c5cb6abb40b27e1fc36`): 0 order commits.
   - `release/security-pages-hardening` (`108118a935`): 0 order commits.
   - `content/wave1-category-hubs-staged` (`1cbdb22b20`): 0 order commits.
3. **Upstream GitHub Object Cache:**
   - Commit `8d521de0f3` remains reachable via commit-addressed API (`/commits/8d521de0...`) solely because GitHub retains hidden pull request head references: `refs/pull/13/head` and `refs/pull/14/head`.
   - Because `refs/pull/*` are hidden and immutable to Git clients (`deny updating a hidden ref`), repository administrators cannot delete them via `git push origin :refs/pull/...`.
   - A dedicated GitHub Support request must be filed by the repository owner to delete `refs/pull/13/head` and `refs/pull/14/head` and trigger backend garbage collection.
4. **Current PR A Cleanliness:**
   - All operational diagnostic reports and draft support tickets containing commit hashes have been untracked from Git.
   - Future releases are guarded by automated regression test `tests/test_public_repository_boundary.py`.

---

## 4. Automated Regression Enforcement

The boundary between public repository assets and quarantined operational files is continuously enforced by:
1. **Quarantine Rule in `.gitignore`:**
   ```gitignore
   # Credentials and Service Accounts
   config/
   *.service_account.json
   credentials*.json
   client_secrets*.json

   # Public Build Artifacts
   public-site/
   dist/

   # Private Operational & Supplier Data Quarantine
   data/orders/
   data/wholesale_inventory.json
   data/wholesale_cost_reference.json
   data/suppliers/
   data/snapshots/
   data/gsc_history/raw_responses/
   data/reports/
   data/analytics/
   data/tasks/
   data/posthog/
   data/backlinks/
   data/aio/
   data/bing/
   data/merchant/
   ```
2. **Automated Unit Test (`tests/test_public_repository_boundary.py`):**
   - Automatically executed in CI on every push and PR.
   - Asserts zero tracked files in quarantined operational directories.
   - Asserts zero secrets, certificates, or `.log` files in Git index.
   - Asserts zero incident tickets detailing historical commit hashes in public tree.

