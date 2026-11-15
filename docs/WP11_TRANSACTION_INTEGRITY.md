# WP11 — D1 Batch Transaction Integrity & Lease Fencing Architecture

**Document Version:** 1.0.0  
**Date:** 2026-11-15  
**Author:** HERMES Autonomous Operations & ChatGPT Engineering  
**Branch:** `feat/backlink-agent-critical-fixes`  
**Status:** IMPLEMENTED & VERIFIED (311 / 311 Unit Tests Passing)

---

## 1. Executive Summary

During WP10 review, an operational vulnerability was identified in distributed Cloudflare D1 batch execution:
- Cloudflare D1's `DB.batch()` treats zero rows modified by an `UPDATE` statement as a successful statement execution.
- If an approval precondition (such as a prospect being already approved, a draft not in `pending_approval`, or a worker holding a stale or expired lease) was evaluated via a `WHERE` clause in the `UPDATE`, D1 would not abort the batch. Subsequent statements in the batch would proceed unconditionally.
- Furthermore, under network latency or process stalls, an old worker that was paused could resume and write changes even after its lease had expired and another worker had taken over.

To eliminate both risks with zero trust, WP11 introduces:
1. **D1 Constraint Assertion Table (`_d1_transaction_assertions`)**: Prepending a strict condition check that attempts to insert an invalid row (`is_valid = 0`) violating a `CHECK (is_valid = 1)` constraint when any condition fails. This causes D1's SQL engine to abort and roll back the entire batch atomically.
2. **Deterministic Lease Fencing (`lease_token`)**: Every claimed update is assigned a unique cryptographic token (`tok_<uuid>`). Every mutation and completion requires matching both `update_id`, `lease_token`, and `status = 'processing'`. Old workers attempting to complete or approve are rejected instantly.
3. **Optimistic Crash Recovery with Atomic SQL Counters**: Stale claims exceeding `lease_timeout_seconds` (default 300s) are recovered atomically using `UPDATE ... SET claimed_at = ?, lease_recoveries = lease_recoveries + 1, lease_token = ? WHERE update_id = ? AND status = 'processing' AND claimed_at = ?`.
4. **Scheduled Recovery Sweeper (`recover_stale_claims_sweep`)**: Proactively scans and reclaims abandoned claims.
5. **Exact Prospect Status Enforcement**: Approvals are strictly restricted to `action_status IN ('active', 'submitted_pending_review', 'draft_ready')`. Rejected or ineligible prospects trigger immediate constraint failures.

---

## 2. D1 Constraint Assertion Mechanism

### Schema Definition
```sql
CREATE TABLE IF NOT EXISTS _d1_transaction_assertions (
    id TEXT PRIMARY KEY,
    is_valid INTEGER NOT NULL CHECK (is_valid = 1)
);
```

### Batch Construction
When executing `execute_atomic_approval(prospect_id, draft_id, timestamp, actor, update_id, lease_token)`:
```sql
-- Step 1: Precondition Assertion Statement
INSERT INTO _d1_transaction_assertions (id, is_valid)
VALUES (?, CASE WHEN 
    (SELECT count(*) FROM prospects WHERE id = ? AND action_status IN ('active', 'submitted_pending_review', 'draft_ready')) = 1
    AND (? IS NULL OR (SELECT count(*) FROM drafts WHERE id = ? AND status = 'pending_approval') = 1)
    AND (? IS NULL OR (SELECT count(*) FROM telegram_processed_updates WHERE update_id = ? AND lease_token = ? AND status = 'processing') = 1)
THEN 1 ELSE 0 END);

-- Step 2: Prospect Status Mutation
UPDATE prospects SET action_status = 'owner_approved_for_manual_submission', updated_at = ? WHERE id = ?;

-- Step 3 (Optional): Draft Status Mutation
UPDATE drafts SET status = 'approved', approved_at = ?, approved_by = ? WHERE id = ?;

-- Step 4: Ephemeral Assertion Cleanup
DELETE FROM _d1_transaction_assertions WHERE id = ?;
```

If **any** subquery condition fails:
- `CASE WHEN ... THEN 1 ELSE 0 END` evaluates to `0`.
- SQLite/D1 attempts `INSERT INTO _d1_transaction_assertions (id, is_valid) VALUES (..., 0)`.
- The `CHECK (is_valid = 1)` constraint fires an immediate `CHECK constraint failed` exception.
- The entire batch rolls back, guaranteeing zero partial writes and zero false approvals.

---

## 3. Worker Lease Fencing & Completion Safety

### Lifecycle State Machine
```
[Telegram Webhook]
       │
       ▼
claim_telegram_update() ──(INSERT / tok_uuid)──► status = 'processing'
       │                                               │
       │                                        (Lease Timeout > 300s)
       │                                               │
       │                                               ▼
       │                                     recover_stale_claims_sweep()
       │                                               │
       │                                 (Optimistic UPDATE / tok_new)
       │                                               │
       ▼                                               ▼
execute_atomic_approval()                     status = 'processing' (new lease)
       │ (requires tok == current_tok)                 │
       ▼                                               ▼
complete_telegram_update() ◄───────────────────────────┘
       │ (requires tok == current_tok)
       ▼
status = 'completed'
```

### Stale Worker Rejection Proof
If Worker A experiences a 301-second GC pause:
1. Worker B executes `recover_stale_claims_sweep` and claims update `77001` with `token_b`.
2. Worker A resumes with `token_a` and calls `execute_atomic_approval(..., lease_token=token_a)`.
3. The assertion query checks:
   `SELECT count(*) FROM telegram_processed_updates WHERE update_id = 77001 AND lease_token = 'token_a' AND status = 'processing'`
4. The count is `0`. The assertion fails with `CHECK constraint failed`.
5. Worker A's transaction rolls back completely.
6. Worker A calls `complete_telegram_update(77001, token_a)`. The update returns `rows = 0` and returns `False`.

---

## 4. Verification & Test Evidence

All 37 unit tests in `backlink-worker/tests/` passed cleanly:

| Test Case | Coverage / Invariant Tested | Result |
| :--- | :--- | :--- |
| `test_execute_atomic_approval_rollback_on_conflict` | Verifies double-approval attempts trigger constraint rollback | ✅ PASS |
| `test_d1_assertion_forces_rollback_when_draft_not_pending` | Verifies non-pending draft aborts prospect approval | ✅ PASS |
| `test_approval_rejected_if_prospect_in_rejected_or_ineligible_state` | Verifies rejected prospect status rejects approval | ✅ PASS |
| `test_stale_worker_fenced_out_when_lease_token_changes` | Verifies stale worker fenced out on token mismatch | ✅ PASS |
| `test_stale_worker_cannot_complete_update_after_lease_loss` | Verifies completion requires matching active lease token | ✅ PASS |
| `test_two_workers_racing_to_recover_same_expired_claim` | Verifies optimistic lock allows only one recovery winner | ✅ PASS |
| `test_recover_stale_claims_sweep` | Verifies background sweep recovers expired claims | ✅ PASS |
| `test_stale_claim_recovery_after_timeout` | Verifies crash recovery logs `lease_recoveries` in audit trail | ✅ PASS |

Overall test suite status: **311 / 311 passing across all 8 project test suites**.
