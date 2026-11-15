# WP12 — 48-Hour Staging Observation & Telemetry Log

**Document Version:** 1.1.0  
**Start Date:** Pending Live Staging Deployment  
**Target Duration:** 48 Consecutive Clock Hours (Zero Error Threshold)  
**Environment:** Staging Worker (`ai-tool-gems-backlink-agent-staging`)  
**Status:** Observation Controls Formulated per ChatGPT Engineering Guidance

---

## 1. 10 Core Observation Telemetry Channels

During the mandatory 48-hour staging observation period, the worker operates continuously in `report_only` mode (`BACKLINK_AGENT_ENABLED="false"`, `BACKLINK_AGENT_MODE="report_only"`).
The following 10 telemetry categories are reconciled continuously:

| Telemetry Channel | What to Capture | Passing Condition |
| :--- | :--- | :--- |
| **1. Cron Reliability** | Scheduled UTC time, actual start UTC, completion UTC, duration | 8 verification cycles + 96 sweep runs accounted for |
| **2. Heartbeat Intervals** | Expected vs. received intervals | 96 expected 30-minute intervals reconciled |
| **3. Verification Integrity** | Prospects checked, passed, failed, skipped, rel classifications | Every result has a deterministic DOM evidence record |
| **4. Queue Health** | Jobs produced, consumed, retried, acknowledged | $Produced = Consumed + DLQ$ reconciles cleanly |
| **5. Dead-Letter Queue** | Message ID, failure reason, retry history | $0$ unexplained DLQ entries; all investigated |
| **6. Telegram Security** | Authorized, rejected, replayed, delivered, dropped notifications | Zero unauthorized command execution |
| **7. Database & D1 State** | D1 errors, assertion check constraint triggers, migration integrity | Zero partial commits or corrupted rows |
| **8. Lease Recovery** | Stale claims, lease takeovers, fenced workers | Zero stale workers perform mutations |
| **9. SSRF & Security** | SSRF blocks, redirect hop limits, webhook secret 401s | Zero security or sandbox bypasses |
| **10. Cost & Limits** | Worker invocations, D1 reads/writes, queue operations | Stays strictly within Cloudflare free-tier quotas |

---

## 2. Five Mandatory Observation Safeguards

1. **Strict UTC Timestamps:** Record scheduled and actual execution timestamps in ISO-8601 UTC across all log entries.
2. **Reconcile Produced vs. Consumed Work:** Never treat an empty DLQ as proof of success. Reconcile total enqueued jobs with acknowledged consumer batches.
3. **Controlled Staging Failure Tests:** Execute 4 controlled failure tests during staging (worker crash, stale lease recovery, D1 assertion constraint abort, and Telegram delivery ambiguity).
4. **Absolute Staging Isolation:** Use a separate Telegram staging bot and webhook. Never overwrite the production bot's active webhook.
5. **Preserve Redacted Evidence:** Keep raw logs, LAT request/response headers, D1 query results, and deployment identifiers with all tokens redacted.

---

## 3. Four Observation Acceptance Gates

- **Gate A — Deployment Evidence:**
  - Wrangler authentication verified (`npx wrangler whoami`).
  - Staging account (`4f7a087d9199c825cced4aa7b66ee81d`) and resources verified.
  - Initial migrations (`migrations/0001_initial.sql`) applied successfully.
  - Staging deployment identifier recorded.
  - Production resources untouched.

- **Gate B — Live Acceptance Tests:**
  - LAT-01 through LAT-08 executed against live staging worker.
  - Each test backed by verifiable HTTP status, JSON payload, and D1 rowcount evidence.
  - Kill switch (`BACKLINK_AGENT_ENABLED="false"`) and `report_only` verified active.

- **Gate C — 48-Hour Observation:**
  - 8 verification cycles (01:00, 07:00, 13:00, 19:00 UTC) reconciled.
  - 96 heartbeat intervals reconciled.
  - Queue and DLQ counts fully reconciled.
  - Zero unexplained security or data-integrity failures.
  - Notification outcomes and recovery behavior documented.

- **Gate D — Production Go/No-Go Decision:**
  - All 12 G-01 through G-12 criteria independently evidenced.
  - Remaining operational risks documented.
  - Explicit owner sign-off and approval obtained before any production dispatch.

---

## 4. Telemetry Log Sheet (Sample Template)

| UTC Timestamp | Trigger / Event | Scheduled Job | Enqueued | Consumed | Retried | DLQ Count | Audit Events Recorded | Status / Discrepancy Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `2026-11-15T12:00:00Z` | Cron `0 1,7,13,19` | Verification Batch | 10 | 10 | 0 | 0 | 10 | PASS - 10 prospects verified (DOM checked) |
| `2026-11-15T12:30:00Z` | Cron `*/30 * * * *` | Stale Lease Sweep | 0 | 0 | 0 | 0 | 0 | PASS - 0 stale leases detected |
| `2026-11-15T13:00:00Z` | Cron `*/30 * * * *` | Stale Lease Sweep | 0 | 0 | 0 | 0 | 0 | PASS - 0 stale leases detected |
