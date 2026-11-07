# Fail-Closed Public Deployment Allowlist Specification

**Script:** [`scripts/build_public_site.py`](file:///d:/Desktop/AI%20Tools%20Aura/scripts/build_public_site.py)  
**Test Suite:** [`tests/test_public_deployment_allowlist.py`](file:///d:/Desktop/AI%20Tools%20Aura/tests/test_public_deployment_allowlist.py)  
**Deployment Target:** GitHub Pages (`aitoolgems.tech`)  
**Standard:** Phase 2.1 Fail-Closed Public Isolation Policy  
**Effective Date:** 2026-11-07  

---

## 1. Security Architecture & Threat Model

Traditional static deployments copy all files recursively, which risks leaking accidental `.env` files, internal diagnostic reports, wholesale supplier databases, or credentials into the public web root.

`scripts/build_public_site.py` addresses this threat through a **fail-closed, affirmative allowlist** architecture:

```
Source Directory (D:\Desktop\AI Tool Gems)
  ├── index.html, about.html, ...  ──► [Affirmative Whitelist Filter] ──► Staged in public-site/
  ├── tools/*/index.html          ──► [Extension & Path Verifier]     ──► Staged in public-site/tools/
  ├── assets/*.webp, *.css, ...   ──► [Extension & Path Verifier]     ──► Staged in public-site/assets/
  ├── data/orders/*               ──► [BLOCKED & EXCLUDED]
  ├── config/*.json               ──► [BLOCKED & EXCLUDED]
  ├── reports/*.md                ──► [BLOCKED & EXCLUDED]
  ├── admin.html, admin.js        ──► [BLOCKED & EXCLUDED]
  └── adversarial *.csv, *.env    ──► [FAILS BUILD WITH PublicSiteSecurityError]
```

---

## 2. Technical Enforcement Rules

### A. Strict Extension Whitelist per Directory
Every file candidate inside an approved public directory must match an explicit extension whitelist:
- **`assets/`:** `.webp`, `.png`, `.jpg`, `.jpeg`, `.svg`, `.ico`, `.css`, `.mp4`, `.woff`, `.woff2`, `.ttf` (Zero `.json`, `.csv`, `.zip`, `.sqlite`, or `.log` allowed).
- **`tools/`, `category/`, `guides/`, `blog/`, `prices/`, `deals/`, `privacy-policy/`, `terms-of-service/`:** `.html` only.

### B. Universal Prohibited Extensions & Filenames (Defense-in-Depth)
Regardless of location, files with the following extensions immediately trigger `PublicSiteSecurityError`:
- `.env`, `.pem`, `.key`, `.pfx`, `.pkcs12`, `.crt`, `.cer`
- `.csv`, `.tsv`, `.sqlite`, `.sqlite3`, `.db`
- `.zip`, `.tar`, `.gz`, `.tgz`, `.rar`, `.7z`
- `.log`, `.trace`, `.bak`, `.tmp`, `.old`, `.swp`
- `.py`, `.pyc`, `.pyd`, `.sh`, `.bash`, `.ps1`, `.cmd`, `.bat`
- `.yml`, `.yaml`, `.toml`, `.ini`, `.cfg`, `.conf`
- `.md`, `.jsonl`

### C. Explicit Search Engine Verification Whitelist
Verification files must be explicitly enumerated. Wildcard patterns (such as `*.txt` or `google*.html`) are prohibited. Only verified tokens are copied:
- `googleb36d12ee905644d9.html`
- `BingSiteAuth.xml`
- `e1a8c47f9d2b4f30a6c8116de5b97042.txt`
- `tiktokH6tjBYp7wfiuUxSHoxcdjeAaS7xub1s6.txt`

### D. Path Traversal & Symlink Rejection
- All symbolic links are detected via `islink()` and abort the build.
- Every destination path is checked for strict containment within `output_dir` via `dest_resolved.relative_to(output_dir)`.

### E. Deterministic Public Build Manifest (`manifest-public-build.json`)
Every build produces a cryptographically verifiable JSON manifest in the deployment root containing:
- Canonical relative path (sorted alphabetically)
- Size in bytes
- SHA-256 digest

---

## 3. Adversarial Test Evidence

The automated test suite in [`tests/test_public_deployment_allowlist.py`](file:///d:/Desktop/AI%20Tools%20Aura/tests/test_public_deployment_allowlist.py) tests the following adversarial injection attacks:

| Injected Adversarial File | Attack Vector | Expected Result | Actual Test Result |
| :--- | :--- | :--- | :--- |
| `assets/private.csv` | Supplier margins or cost table | `PublicSiteSecurityError` raised | **PASSED** (Aborted) |
| `assets/supplier-export.json` | Supplier procurement handles | `PublicSiteSecurityError` raised | **PASSED** (Aborted) |
| `tools/test/.env` | Leaked API key or secret | `PublicSiteSecurityError` raised | **PASSED** (Aborted) |
| `guides/internal-audit.md` | Unapproved internal markdown doc | `PublicSiteSecurityError` raised | **PASSED** (Aborted) |
| `blog/customer-data.sqlite` | SQLite transaction database | `PublicSiteSecurityError` raised | **PASSED** (Aborted) |
| `category/private.pem` | SSH/TLS private key | `PublicSiteSecurityError` raised | **PASSED** (Aborted) |
| `assets/backup.zip` | Archive containing raw code/data | `PublicSiteSecurityError` raised | **PASSED** (Aborted) |
| `assets/secrets.log` | Error log with token trace | `PublicSiteSecurityError` raised | **PASSED** (Aborted) |
| Symlink escape | Directory traversal outside root | `PublicSiteSecurityError` raised | **PASSED** (Aborted) |
| Invalid CNAME | Domain hijacking | `PublicSiteSecurityError` raised | **PASSED** (Aborted) |

