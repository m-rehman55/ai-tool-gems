# WP14 Failure and Recovery Runbook
**Document Version:** 1.0.0  
**Date:** 2026-11-15  
**Audience:** HERMES System Operators & SRE  
**Status:** Approved & Enforced  

---

## 1. Quick Emergency Triage

```
🚨 EMERGENCY ACTIONS:
1. To disable pipeline immediately:
   set BACKLINK_AGENT_ENABLED="false"
2. To force local dry-run only:
   set BACKLINK_AGENT_DRY_RUN="true"
3. To flush stale worker leases:
   python -m backlink_agent recover-leases
```

---

## 2. Failure Scenarios & Standard Operating Procedures

### Scenario A: Worker Crash During Telegram Dispatch (Stale Leases)
- **Symptom:** Messages stuck in `'sending'` state; subsequent runs do not reprocess them immediately.
- **Root Cause:** A worker crashed or timed out after acquiring a row lease without updating the status to `'delivered'` or `'failed'`.
- **Automatic Recovery:**
  - `LocalSQLiteOutboxStore.recover_stale_leases()` runs automatically at the start of every `flush_outbox()` call.
  - Any message in `'sending'` state with `locked_at < (now - 300 seconds)` is automatically reset to `'retry_pending'`, its `retry_count` is incremented, and an error note is recorded.
- **Manual Remediation Command:**
  ```bash
  python -c "from backlink_agent.telegram_delivery.outbox_store import LocalSQLiteOutboxStore; print('Recovered:', LocalSQLiteOutboxStore().recover_stale_leases(0))"
  ```

---

### Scenario B: Telegram Socket Timeout (`delivery_unknown`)
- **Symptom:** Outbox telemetry reports `delivery_unknown > 0`.
- **Root Cause:** The HTTPS request was sent to `api.telegram.org`, but the socket timed out before receiving the HTTP response. The message may or may not have reached Telegram.
- **Protocol:**
  - The message is NOT immediately retried to avoid duplicate message spam in the operator chat.
  - The message status transitions to `'delivery_unknown'`.
  - Operator inspects Telegram chat. If the message was received, operator can ignore or mark resolved. If missing, operator can manually requeue.

---

### Scenario C: Fact Validator Rejection on Proposed Outreach Copy
- **Symptom:** Pipeline reports `fact_validator_rejected > 0`, draft generation aborted with `ValueError: Draft validation failed against verified facts`.
- **Root Cause:** The drafting engine generated text referencing unverified claims (e.g. Stripe/PayPal instant checkout, USD-only pricing, or unauthorized brand partnerships).
- **Remediation:**
  1. Inspect rejected text:
     ```bash
     python -m backlink_agent facts --check-copy "<text>"
     ```
  2. Ensure copy strictly adheres to `verified_facts.yml` (authentic PKR pricing, EasyPaisa, JazzCash, SadaPay, Raast, IBFT).
  3. Never bypass or disable `DraftFactValidator`.

---

### Scenario D: SQLite `busy_timeout` / Database Lock Concurrency
- **Symptom:** `sqlite3.OperationalError: database is locked`.
- **Remediation:**
  - HERMES SQLite database operates in WAL mode (`PRAGMA journal_mode = WAL;`) with `busy_timeout = 5000` ms, allowing concurrent readers and serialized writers.
  - If a dangling process holds a lock, identify and terminate the process:
    ```powershell
    Get-Process python | Where-Object { $_.StartTime -lt (Get-Date).AddMinutes(-30) }
    ```
