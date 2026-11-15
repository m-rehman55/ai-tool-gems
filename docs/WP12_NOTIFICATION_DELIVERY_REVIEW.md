# WP12 — Telegram Notification Delivery & Outbox Architecture Review

**Document Version:** 1.0.0  
**Date:** 2026-11-15  
**Author:** HERMES Autonomous Operations & ChatGPT Engineering  
**Subsystem:** Telegram Approval & Notification Dispatcher

---

## 1. Architectural Distinction: Lease Fencing vs. Exactly-Once External Delivery

As highlighted in ChatGPT's WP11 review, while a database lease token (`lease_token`) strictly fences database mutations and prevents stale workers from executing approvals or updating records, it cannot mathematically guarantee exactly-once external delivery to third-party APIs (such as Telegram).

### Two Inherent External Failure Windows:
1. **Failure Window 1 (Commit Succeeded, Notification Undelivered):**
   - The D1 approval transaction commits, and the update is marked `completed`.
   - The worker crashes, network drops, or isolate restarts *before* the HTTP response reaches Telegram.
   - *Impact:* The approval succeeded in the database, but the owner never sees the confirmation message in chat.
2. **Failure Window 2 (Telegram Accepted, Completion Unrecorded):**
   - The worker dispatches the message to Telegram, and Telegram receives it.
   - The worker crashes before recording the successful delivery or marking the update `completed`.
   - On retry, the worker might send the message a second time.
   - *Impact:* The owner receives a duplicate notification in chat.

---

## 2. Implemented Safeguards in Commit `398a1d8`

To handle these windows reliably without risk to database integrity:

1. **Suppression on Lease Loss:**
   - In `handle_update`:
     ```python
     completed_ok = await self.complete_telegram_update(update_id, lease_token, response_text=reply_text)
     if not completed_ok:
         return f"⛔ Execution dropped: Worker was fenced out..."
     ```
   - If a worker lost its lease, it is barred from reporting success.
2. **Durable In-Database Response Caching:**
   - When an update completes, `response_text` is stored directly in `telegram_processed_updates`.
   - If Telegram retries a completed update ID, the worker safely returns `Duplicate skipped safely` with zero mutations.
3. **Idempotent Crash Recovery:**
   - If a crash occurs after `execute_atomic_approval` commits, retrying the command does not attempt a second approval.
   - It discovers the prior `prospect_approved` audit record, reconstructs the valid confirmation text, and completes the update.

---

## 3. Production Hardening: Transactional Outbox Pattern

For production promotion after the 48-hour staging burn-in, we recommend implementing a dedicated `notification_outbox` table:

```sql
CREATE TABLE IF NOT EXISTS notification_outbox (
    id TEXT PRIMARY KEY,
    recipient_chat_id TEXT NOT NULL,
    message_text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending', -- pending, sent, failed
    attempts INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sent_at TEXT
);
```

### Outbox Invariants:
1. When an approval transaction executes, the notification record is inserted inside the **same D1 batch transaction**.
2. A lightweight background queue consumer or scheduled alarm reads `pending` outbox items and dispatches them with retry backoff.
3. The underlying prospect approval is **never re-executed** merely to retry a notification.
