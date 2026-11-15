# WP12 — 48-Hour Staging Observation & Telemetry Log

**Document Version:** 1.0.0  
**Start Date:** Pending Live Staging Deployment  
**Target Duration:** 48 Consecutive Clock Hours (Zero Error Threshold)  
**Environment:** Staging Worker (`ai-tool-gems-backlink-agent-staging`)

---

## 1. Observation Objectives & Metrics

During the mandatory 48-hour staging observation period, the worker operates continuously in `report_only` mode (`BACKLINK_AGENT_ENABLED="false"`, `BACKLINK_AGENT_MODE="report_only"`).
The following telemetry channels must be reconciled:
- **Verification Cron Cycles:** 8 cycles (scheduled every 6 hours at 01:00, 07:00, 13:00, 19:00 UTC).
- **Heartbeat & Sweeper Runs:** 96 runs (scheduled every 30 minutes).
- **Queue Reconciliation:** Enqueued jobs vs. successfully consumed jobs vs. retries vs. DLQ entries.
- **D1 Audit Log Growth:** Verification run entries, lease recoveries, update claims.

---

## 2. Telemetry Log Sheet (Sample Template)

| UTC Timestamp | Trigger / Event | Scheduled Job | Enqueued | Consumed | Retried | DLQ Count | Audit Events Recorded | Status / Discrepancy Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `2026-11-15T12:00:00Z` | Cron `0 1,7,13,19` | Verification Batch | 10 | 10 | 0 | 0 | 10 | PASS - 10 prospects verified (DOM checked) |
| `2026-11-15T12:30:00Z` | Cron `*/30 * * * *` | Stale Lease Sweep | 0 | 0 | 0 | 0 | 0 | PASS - 0 stale leases detected |
| `2026-11-15T13:00:00Z` | Cron `*/30 * * * *` | Stale Lease Sweep | 0 | 0 | 0 | 0 | 0 | PASS - 0 stale leases detected |

---

## 3. Discrepancy & Anomaly Thresholds

A discrepancy requires an immediate investigation and resets the 48-hour observation timer if:
1. Any job enters `aitoolgems-backlink-dlq-staging` unexpectedly.
2. A verification run records an unhandled exception or malformed HTML parser crash.
3. A lease takeover occurs without an associated `telegram_claim_recovered` audit event.
4. Any SSRF firewall check fails to block a private, link-local, or metadata address.
5. A double-state transition occurs on any prospect or draft record.
