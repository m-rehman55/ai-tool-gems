# Public vs Private Repository Data Boundary & Audit Report

**Repository:** `https://github.com/m-rehman55/ai-tool-gems`  
**Audit Target:** Public GitHub Repository Index & Deployment Artifacts  
**Date:** 2026-11-07  
**Standard:** Phase 2 Public Data Security & Least-Privilege Deployment Policy  

---

## 1. Boundary Architecture & Objectives

Because `m-rehman55/ai-tool-gems` is a public GitHub repository, any file tracked in Git is publicly accessible to any web visitor or search engine crawler via `github.com/m-rehman55/ai-tool-gems/blob/main/...`. Furthermore, standard GitHub Pages deployments that serve the repository root or docs/ folder risk exposing internal files.

To permanently secure sensitive operational assets while maintaining a high-performance, verifiable storefront, this audit defines and implements a strict 3-tier classification system:

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
├─────────────────────────┼──────────────────────┼───────────────────────┤
│ ACTION:                 │ ACTION:              │ ACTION:               │
│ Gitignored locally &    │ Tracked in Git;      │ Tracked in Git;       │
│ strictly excluded from  │ Deployed to GitHub   │ Excluded from public  │
│ public deployment       │ Pages via allowlist  │ Pages deployment      │
└─────────────────────────┴──────────────────────┴───────────────────────┘
```

---

## 2. File-by-File Classification & Policy Matrix

A machine-readable classification is maintained in [`reports/Public_Private_Data_Classification.csv`](file:///d:/Desktop/AI%20Tools%20Aura/reports/Public_Private_Data_Classification.csv). Below is the operational summary:

| Path / Pattern | Classification | Sensitivity | Git Status | Deployment Action | Justification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `data/orders/*` | Group A | HIGH (Confidential) | **Gitignored** | STRICTLY EXCLUDED | Real customer transaction records; offline WhatsApp proofs. |
| `data/wholesale_inventory.json` | Group A | HIGH (Confidential) | **Gitignored** | STRICTLY EXCLUDED | Proprietary wholesale costs, supplier Telegram handles, and margin equations. |
| `data/wholesale_cost_reference.json` | Group A | HIGH (Confidential) | **Gitignored** | STRICTLY EXCLUDED | Internal wholesale baseline pricing floor calculations. |
| `data/suppliers/*` | Group A | HIGH (Confidential) | **Gitignored** | STRICTLY EXCLUDED | Raw reseller catalog feeds and procurement endpoints. |
| `config/*.json` | Group A | HIGH (Confidential) | **Gitignored** | STRICTLY EXCLUDED | Service account credentials, OAuth tokens, and secrets. |
| `data/snapshots/*` | Group A | LOW (Operational) | **Gitignored** | STRICTLY EXCLUDED | Automated system recovery points and state backups. |
| `data/gsc_history/raw_responses/` | Group A | MEDIUM (Telemetry) | **Gitignored** | STRICTLY EXCLUDED | Raw Search Console response payloads. |
| `data/analytics/*` | Group A | MEDIUM (Internal) | **Gitignored** | STRICTLY EXCLUDED | Raw GA4 telemetry snapshots and local queues. |
| `admin.html`, `admin.js` | Group A | MEDIUM (Sandbox) | Tracked Clean | STRICTLY EXCLUDED | Developer prototype sandbox; labeled with explicit banner. |
| `reports/*` | Group A | MEDIUM (Audit) | Tracked Clean | STRICTLY EXCLUDED | Technical strategy reports, audit logs, and release evaluations. |
| `index.html`, `about.html`, `contact.html` | Group B | PUBLIC | Tracked Clean | **APPROVED** | Core customer-facing marketing and information pages. |
| `tools/*/index.html` (40 tools) | Group B | PUBLIC | Tracked Clean | **APPROVED** | Verified parent tool subscription pages with PKR prices. |
| `guides/*/`, `blog/*/` | Group B | PUBLIC | Tracked Clean | **APPROVED** | Editorial articles and informational comparisons. |
| `assets/*` | Group B | PUBLIC | Tracked Clean | **APPROVED** | Verified product logos, site brand marks, and styles. |
| `CNAME` | Group B | PUBLIC | Tracked Clean | **APPROVED** | Custom apex domain pointer (`aitoolgems.tech`). |
| `sitemap.xml`, `robots.txt` | Group B | PUBLIC | Tracked Clean | **APPROVED** | Search engine discovery directives and canonical index. |
| `llms.txt`, `llms-full.txt` | Group B | PUBLIC | Tracked Clean | **APPROVED** | Machine knowledge bases for AI search crawlers. |
| `tests/fixtures/*` | Group C | SYNTHETIC | Tracked Clean | STRICTLY EXCLUDED | Synthetic mock orders (e.g. `SYNTH-DRYRUN-001`) for QA. |
| `*_agent/tests/*` | Group C | SYNTHETIC | Tracked Clean | STRICTLY EXCLUDED | Unit tests asserting system integrity. |

---

## 3. Enforcement Mechanisms

### A. Git Index Guard (`.gitignore`)
The repository's root `.gitignore` has been updated with explicit quarantine blocks:
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

### B. Deployment Artifact Builder (`scripts/build_public_site.py`)
Rather than deploying the raw repository root to GitHub Pages, the automated deployment workflow invokes `scripts/build_public_site.py`. This script:
1. Enforces an affirmative allowlist of public files (`PUBLIC_ALLOWLIST_PATTERNS` and `PUBLIC_ALLOWLIST_DIRS`).
2. Scans the generated output directory (`public-site/`) against strict exclusion sets (`STRICT_EXCLUDE_FILES` and `STRICT_EXCLUDE_PREFIXES`).
3. Guarantees `public-site/CNAME` is populated with `aitoolgems.tech`.
4. Raises a hard exception if any private file or directory is detected in the artifact.

### C. CI/CD Pre-Deployment Test Suite (`tests/test_public_deployment_allowlist.py`)
Automated unit tests execute during CI/CD to verify that:
- Over 50 customer-facing pages are successfully staged.
- `public-site/data/` and `public-site/reports/` do not exist.
- `admin.html` is never copied to the deployment directory.
- `CNAME` exists and strictly matches `aitoolgems.tech`.

---

## 4. Audit Conclusion

The public/private repository boundary is fully established and programmatically enforced. No private operational files or supplier records are exposed on the public GitHub storefront.
