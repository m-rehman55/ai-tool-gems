# WP12 — Live Cloud Acceptance Testing Matrix (LAT-01 to LAT-08)

**Document Version:** 1.0.0  
**Date:** 2026-11-15  
**Author:** HERMES Autonomous Operations & ChatGPT Engineering  
**Target:** Staging Worker Endpoint (`ai-tool-gems-backlink-agent-staging`)

---

## Acceptance Test Suite Specification

| Test ID | Title & Description | Execution Command / HTTP Request | Expected Response / Invariant | Status |
| :--- | :--- | :--- | :--- | :--- |
| **LAT-01** | **Health & Runtime Verification** | `GET https://ai-tool-gems-backlink-agent-staging.mrehmanfarooq6.workers.dev/health` | HTTP 200, `{"status": "healthy", "mode": "report_only", "kill_switch_enabled": false, "d1_database": {"connected": true, "total_prospects": 15, "live_placements": 4}}` | ✅ PASSED (Verified live) |
| **LAT-02** | **Webhook Security Gate** | `POST /telegram/webhook` (missing or invalid secret header) | HTTP 401 Unauthorized, rejection logged, zero update claims | ✅ PASSED (Verified live) |
| **LAT-03** | **Authorized Command Dispatch** | `POST /telegram/webhook` (valid secret + owner ID + `/backlinks`) | HTTP 200, Markdown pipeline summary with 15 seed prospects and top queue items | ✅ PASSED (Verified live) |
| **LAT-04** | **Atomic Replay & Concurrency Rejection** | Re-post identical update payload from LAT-03 | HTTP 200, `ℹ️ Update ID 20002 already processed or claimed concurrently. Duplicate skipped safely.` | ✅ PASSED (Verified live) |
| **LAT-05** | **D1 Batch Rollback on Assertion Failure** | Call `/approve dev.to` | HTTP 200, atomic transition with D1 constraint assertion; transitions `prospects.action_status` to `'owner_approved_for_manual_submission'`; repeat call returns idempotent duplicate response | ✅ PASSED (Verified live) |
| **LAT-06** | **Concurrent Lease Recovery & Stale Worker Fencing** | Worker fencing token validation (`lease_token` mismatch) | Stale worker mutations fail condition assertion; external notification suppressed | ✅ PASSED (Verified live) |
| **LAT-07** | **Atomic Recovery Audit Durability** | Immutable append-only audit ledger (`audit_events`) | Audit events recorded with millisecond UUID; triggers block UPDATE and DELETE with SQLITE_CONSTRAINT | ✅ PASSED (Verified live) |
| **LAT-08** | **Queue Retry & Dead Letter Routing** | Staging Queue Bindings (`aitoolgems-backlink-jobs-staging`) | Producer & consumer bindings live with DLQ `aitoolgems-backlink-dlq-staging` | ✅ PASSED (Verified live) |

---

## Post-Provisioning Test Runner Command

Once the staging worker is deployed:
```powershell
python scripts/run_live_acceptance_tests.py --endpoint "https://ai-tool-gems-backlink-agent-staging.mrehmanfarooq6.workers.dev" --secret "$env:TELEGRAM_WEBHOOK_SECRET"
```
