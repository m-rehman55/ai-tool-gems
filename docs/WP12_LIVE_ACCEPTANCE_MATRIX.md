# WP12 — Live Cloud Acceptance Testing Matrix (LAT-01 to LAT-08)

**Document Version:** 1.0.0  
**Date:** 2026-11-15  
**Author:** HERMES Autonomous Operations & ChatGPT Engineering  
**Target:** Staging Worker Endpoint (`ai-tool-gems-backlink-agent-staging`)

---

## Acceptance Test Suite Specification

| Test ID | Title & Description | Execution Command / HTTP Request | Expected Response / Invariant | Status |
| :--- | :--- | :--- | :--- | :--- |
| **LAT-01** | **Health & Runtime Verification** | `GET https://<worker-staging>/health` | HTTP 200, `{"status": "ok", "mode": "report_only", "enabled": false}` | PENDING_PROVISION |
| **LAT-02** | **Webhook Security Gate** | `POST https://<worker-staging>/telegram/webhook` (no secret header) | HTTP 401 Unauthorized, rejection logged | PENDING_PROVISION |
| **LAT-03** | **Authorized Command Dispatch** | `POST https://<worker-staging>/telegram/webhook` (valid secret + owner ID + `/backlinks`) | HTTP 200, Markdown pipeline summary with 15 seed prospects | PENDING_PROVISION |
| **LAT-04** | **Atomic Replay & Concurrency Rejection** | Re-post identical update payload from LAT-03 | HTTP 200, `ℹ️ Update ID ... already processed. Duplicate skipped safely.` | PENDING_PROVISION |
| **LAT-05** | **D1 Batch Rollback on Assertion Failure** | Call `/approve <prospect>` on a non-pending or tampered draft | HTTP 200, `CHECK constraint failed`, batch rolls back, zero prospect mutation | PENDING_PROVISION |
| **LAT-06** | **Concurrent Lease Recovery & Stale Worker Fencing** | Worker A paused; Worker B recovers lease after timeout; Worker A resumes and attempts completion | Worker A fenced out (`rows = 0`), notification dropped, Worker B holds lease | PENDING_PROVISION |
| **LAT-07** | **Atomic Recovery Audit Durability** | Force crash/abort during audit event insertion of recovery | Recovery update rolls back with audit failure; zero orphan takeovers | PENDING_PROVISION |
| **LAT-08** | **Queue Retry & Dead Letter Routing** | Enqueue a poison message payload into `aitoolgems-backlink-jobs-staging` | Retries 2 times, transitions cleanly to `aitoolgems-backlink-dlq-staging` | PENDING_PROVISION |

---

## Post-Provisioning Test Runner Command

Once the staging worker is deployed:
```powershell
python scripts/run_live_acceptance_tests.py --endpoint "https://ai-tool-gems-backlink-agent-staging.mrehmanfarooq6.workers.dev" --secret "$env:TELEGRAM_WEBHOOK_SECRET"
```
