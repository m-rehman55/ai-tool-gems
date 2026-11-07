# Phase 2.1 Release Candidate Changelog

**Repository:** `m-rehman55/ai-tool-gems`  
**Release Target:** Phase 2.1 Remediation  
**Branch:** `release/security-pages-hardening` (PR #16) & `content/wave1-category-hubs-staged` (PR #17)  
**Date:** 2026-11-07  

---

## 1. Security & Repository Boundary Hardening

### Added:
- `tests/test_public_repository_boundary.py`:
  - 4 automated regression tests enforcing boundaries between public Git tracking and private operational files.
  - Verifies that credentials, secrets, databases, logs, wholesale inventories, and sensitive incident reports are never tracked in Git.
- `docs/PUBLIC_REPOSITORY_SECURITY_POLICY.md`:
  - Architectural policy delineating the 3-tier boundary: Public Git Repo, Public GitHub Pages, and Local Quarantined Data.
- `docs/PUBLIC_DEPLOYMENT_ALLOWLIST_SPEC.md`:
  - Technical specification of the affirmative allowlist build engine.

### Modified:
- `.gitignore`:
  - Added explicit quarantine pattern `reports/` to prevent diagnostic logs and test reports from leaking into Git tracking.

### Deleted (Untracked from Public Git):
- `reports/GA4_Regression_Report.md` (internal diagnostic report)
- `reports/GitHub_Support_Ticket_and_Refs_Report.md` (internal security ticket draft referencing purged commit SHAs)
- `reports/Git_History_Purge_Verification_Report.md` (internal git history verification report)
- `reports/Pages_Artifact_Inspection_Report.md` (internal build artifact inspection report)
- `reports/Public_Private_Data_Classification.csv` (internal data classification register)
- `reports/Public_Private_Tracked_Data_Audit.md` (internal audit log)
- `reports/Updated_Release_Readiness_Report.md` (internal release readiness draft)
- `marketing_agent/data/repair-last.log` (internal runtime log file)

---

## 2. Public Deployment Isolation & Build Engine

### Modified:
- `scripts/build_public_site.py`:
  - Completely rewritten with fail-closed architecture.
  - Replaced negative denylist with strict affirmative allowlists (`APPROVED_ROOT_FILES`, `APPROVED_VERIFICATION_FILES`, `APPROVED_PUBLIC_DIRS`).
  - Added directory-specific file extension whitelists (`assets/` allows media/css/fonts; root and content directories strictly allow `.html`).
  - Implemented affirmative CNAME validation (`aitoolgems.tech`).
  - Implemented directory symbolic link detection and rejection (`PublicSiteSecurityError`).
  - Implemented destination path traversal checks (`dest_resolved.relative_to(output_dir)`).
  - Implemented deterministic SHA-256 build manifest generation (`manifest-public-build.json`).
- `tests/test_public_deployment_allowlist.py`:
  - Re-implemented with 4 comprehensive test cases including adversarial injections (`.env`, `.pem`, `.csv`, `.sqlite`, `.zip`, `.log`), CNAME tampering, directory symlink escaping, and legitimate build verification.

---

## 3. GitHub Pages Deployment Safety

### Modified:
- `.github/workflows/deploy-pages.yml`:
  - Decoupled `build` job from `deploy` job.
  - `build` job runs on push, PR, and manual dispatch with minimal permissions (`contents: read`).
  - `deploy` job gated with strict conditional `if: github.ref == 'refs/heads/main'`.
  - Manual workflow dispatches on feature branches strictly cannot trigger production deployment.

### Added:
- `docs/GITHUB_PAGES_DEPLOYMENT_GUARDRAILS.md`:
  - Operational guardrails document detailing GitHub Pages permissions, environment protections, and release procedures.

---

## 4. GA4 Privacy & Conversion Integrity

### Modified:
- `attribution.js`:
  - Updated Consent Mode v2 default to privacy-first denial: `'analytics_storage': 'denied'`.
  - Sanitized `proof_image_open` event telemetry: passes categorical `{ proof_type: 'payment_verification_proof' }` instead of raw image source.
  - Retained Measurement ID `G-NQJCMDCLLP` across all web tracking.
- `ga4_agent/models.py`:
  - Implemented `validate_client_id(client_id, customer_phone_hash)` to validate GA4 format (`^[0-9a-zA-Z._-]{10,64}$`) and reject phone hash derivations, emails, and PII markers.
  - Added `client_id_provenance` tracking to `OfflineVerifiedOrder`.
  - Enforced validation inside `OfflineVerifiedOrder.create`.
- `ga4_agent/conversion_importer.py`:
  - Updated `record_verified_payment` to gracefully catch and return descriptive errors for invalid client IDs.
  - Updated `build_measurement_protocol_payload` and `build_refund_payload` to validate client ID provenance before payload generation.
  - Updated `record_verified_refund` to enforce parent transaction existence and refund amount bounding.
- `ga4_agent/tests/test_ga4_agent.py`:
  - Expanded unit test suite from 20 to 30 tests covering client ID validation, PII rejection, Consent Mode v2 defaults, telemetry sanitization, and refund parent validation.

### Added:
- `docs/GA4_PRIVACY_AND_CONVERSION_VALIDATION.md`:
  - Comprehensive architectural specification and test verification report for GA4 privacy and conversion tracking.

---

## 5. Release Governance & Gate Matrix

### Added:
- `docs/RELEASE_GATE_MATRIX.md`:
  - Complete 12-gate release matrix providing truthful verification statuses across security, deployment, privacy, conversion, SEO, and legal governance.
- `docs/PHASE_2_1_REMEDIATION_REPORT.md`:
  - Comprehensive Phase 2.1 executive report covering all remediation actions and verification results.

