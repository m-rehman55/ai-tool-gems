# WP16: Outbox Reliability, Distributed Systems & Crash Recovery Report

**Document Version:** 1.0.0  
**Phase:** Phase 3 (Outbox & Distributed Systems Review)  
**Verification Date:** 2026-11-15  
**Governing Modules:** `backlink_agent.telegram_delivery.outbox_store`, `backlink-worker.d1_adapter`  

---

## 1. Executive Summary

Autonomous distributed background agents face distinct reliability failure modes: worker process crashes midway through sending, network timeouts during Telegram dispatches, and lease races where two workers attempt to claim the same queue item simultaneously.

This report documents the architectural safeguards, concurrency models, and crash-recovery procedures implemented in HERMES across local SQLite (`LocalSQLiteOutboxStore`) and Cloudflare D1 edge workers (`D1Adapter`).

---

## 2. Distributed Lease Locking & Worker Fencing

### 2.1 The Stale Worker Split-Brain Hazard
In distributed queues, if Worker A claims a message with a 300-second lease, encounters an unexpected thread pause or network delay, and Worker B claims the task after the lease expires, Worker A might wake up and overwrite Worker B's newer status.

```mermaid
sequenceDiagram
    participant DB as SQLite / Cloudflare D1
    participant WA as Worker A (Slow / Crash)
    participant WB as Worker B (Healthy)

    WA->>DB: 1. Claim message (lease_token = tok_AAA)
    Note over WA: 2. Stalls or encounters network pause > 300s
    Note over DB: 3. Lease expires (locked_at > 300s old)
    WB->>DB: 4. Recovery sweep: reclaim message (lease_token = tok_BBB)
    WB->>DB: 5. Execute action and mark completed (WHERE lease_token = tok_BBB)
    Note over DB: Updated to 'delivered'
    WA->>DB: 6. Stale Worker A wakes up and attempts update (WHERE lease_token = tok_AAA)
    DB-->>WA: 7. REJECTED (0 rows updated; token mismatch)
```

### 2.2 Proof of Enforcement
In `backlink_agent/telegram_delivery/outbox_store.py`:
- Every call to `claim_pending_messages()` generates `lease_token = f"tok_{uuid.uuid4().hex[:12]}"`.
- Every call to `update_delivery_status()` enforces:
  ```sql
  UPDATE outbox_messages
  SET status = ?, delivered_at = ?, error_message = ?
  WHERE message_id = ? AND (lease_token = ? OR lease_token IS NULL)
  ```
- If the token was changed by a newer worker, the query matches 0 rows and returns `False`.
- Validated via `test_lease_token_fencing_blocks_stale_worker_update` (PASS).

---

## 3. Storage Durability & SQLite WAL Journaling

### 3.1 Pragma Configurations
All SQLite connections enforce:
- `PRAGMA journal_mode = WAL;`: Write-Ahead Logging allows simultaneous reads and writes without thread deadlocks.
- `PRAGMA busy_timeout = 5000;`: Automatic exponential backoff up to 5000ms prevents `database is locked` exceptions during high-frequency concurrent operations.
- `PRAGMA synchronous = NORMAL;`: Ensures durability across process crashes while avoiding disk I/O bottlenecks.

### 3.2 WAL Checkpointing
`LocalSQLiteOutboxStore` and `LocalSQLiteLifecycleStore` implement explicit WAL truncation (`checkpoint_wal()`):
```sql
PRAGMA wal_checkpoint(TRUNCATE);
```
This flushes the `-wal` journal back into the master `.db` file before archival, snapshotting, or CI artifact upload.

---

## 4. Ephemeral Runner Limitations & Cloud Persistence

> **CRITICAL REALITY:** GitHub Actions runners are ephemeral containers.
> The runner's local filesystem (including `data/backlink_outbox.db` and `data/backlink_lifecycle.db`) is destroyed when the job terminates.

### Operational Mitigations:
1. **Runner-Scoped Isolation:** Inside a single workflow run, SQLite provides safe atomic locks between parallel sub-processes and steps.
2. **Artifact Persistence:** Every daily workflow run exports:
   - `reports/acquisition/acquisition_performance_*.md`
   - `reports/acquisition/acquisition_performance_*.json`
   - `data/backlink_lifecycle.db` (as a compressed workflow artifact)
3. **Target Edge Database (Cloudflare D1):** True multi-region persistence across daily runs is anchored in Cloudflare D1 (`aitoolgems-backlink-agent-staging`), which operates as the persistent cloud database once the 48-hour staging observation window concludes.

---

## 5. Crash Recovery & Disaster Runbook

| Scenario | Symptom | Automated Recovery Behavior | Operator Recovery Command |
| :--- | :--- | :--- | :--- |
| **Worker SIGKILL / Crash** | Message stuck in `sending` state. | After 300s, `recover_stale_leases()` transitions message to `retry_pending` and clears lock. | `python -m backlink_agent recover-leases --timeout 300` |
| **Telegram Network Timeout** | Dispatch request hangs > 15s. | Message transitioned to `delivery_unknown`; logged in audit trail; retry scheduled. | Evaluated in next outbox flush cycle |
| **Max Retries Exceeded** | `retry_count >= 3`. | Message transitioned to `failed`; alert formatted for operator console. | `python -m backlink_agent report` |
| **Database Corruption** | SQLite checksum failure. | Restore from previous day's GitHub Actions artifact backup. | `cp backup/backlink_lifecycle.db data/` |
