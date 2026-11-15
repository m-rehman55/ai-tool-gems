# WP16.2 Schema & Lifecycle Compatibility Verification Report

**Date:** 2026-11-15  
**Branch:** `feat/backlink-agent-critical-fixes`  
**Target Domain:** `https://aitoolgems.tech/`  
**Modules Inspected:** `backlink_agent/lifecycle/models.py`, `backlink_agent/lifecycle/store.py`, `backlink-worker/migrations/0001_initial.sql`, `backlink_agent/reporting/acquisition_reporter.py`  
**Verification Scope:** 18-State Lifecycle Compatibility, D1 & SQLite Schema Constraints, Audit Triggers, Serialization, Reporting, and TTL Expiration  

---

## 1. Executive Summary

This report verifies the database and application-level compatibility of the 18-state acquisition lifecycle, with specific focus on the 18th state (`expired`).

We confirm that:
1. Neither Cloudflare D1 nor local SQLite contains SQL `CHECK` constraints restricting state names.
2. The database trigger on `audit_events` allows transitions to `expired` while enforcing append-only immutability.
3. Application models, serializers, deserializers, and reporting engines handle all 18 states without error.
4. TTL expiration preserves complete historical audit trails.

---

## 2. Database Schema & Constraint Inspection

### A. Local SQLite Schema (`backlink_agent/lifecycle/store.py`)
```sql
CREATE TABLE IF NOT EXISTS prospect_lifecycle (
    prospect_id TEXT PRIMARY KEY,
    prospect_domain TEXT NOT NULL,
    source_page_url TEXT NOT NULL,
    target_asset_url TEXT NOT NULL,
    prospect_type TEXT NOT NULL,
    current_state TEXT NOT NULL,  -- Unconstrained TEXT: accepts all 18 states
    score INTEGER NOT NULL DEFAULT 0,
    ...
);
CREATE TABLE IF NOT EXISTS lifecycle_transitions (
    transition_id TEXT PRIMARY KEY,
    prospect_id TEXT NOT NULL,
    from_state TEXT NOT NULL,     -- Unconstrained TEXT: records transitions to 'expired'
    to_state TEXT NOT NULL,
    ...
);
```

### B. Cloudflare D1 Staging Schema (`backlink-worker/migrations/0001_initial.sql`)
```sql
CREATE TABLE IF NOT EXISTS prospects (
    id TEXT PRIMARY KEY,
    prospect_domain TEXT NOT NULL,
    action_status TEXT NOT NULL DEFAULT 'active', -- Unconstrained TEXT
    link_status TEXT NOT NULL DEFAULT 'not_live',   -- Unconstrained TEXT
    ...
);
CREATE TABLE IF NOT EXISTS audit_events (
    id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    prospect_id TEXT,
    details TEXT,
    created_at TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS block_audit_events_mutation
BEFORE UPDATE ON audit_events
BEGIN
    SELECT RAISE(FAIL, 'audit_events is append-only and immutable');
END;
```

**Constraint & Trigger Findings:**
- **Zero SQL CHECK Constraints:** No table enforces a hardcoded enumeration constraint like `CHECK(current_state IN ('discovered', ...))`.
- **Trigger Compatibility:** The trigger `block_audit_events_mutation` applies only to `UPDATE` operations on `audit_events`. Inserting new audit rows during a transition to `expired` succeeds normally.
- **Zero Schema Migrations Required:** The staging D1 instance (`aitoolgems-backlink-agent-staging`) accepts `expired` immediately without DDL modifications.

---

## 3. Application-Level Compatibility & Reporting

### A. Transition Graph Integrity
All 18 states are defined in `VALID_TRANSITION_GRAPH`:
- Forward Happy Path: `discovered` -> `evidence_verified` -> `scored` -> `draft_ready` -> `owner_approved` -> `manually_submitted` -> `published` -> `backlink_verified` -> `retained`.
- Exception & Terminal States: `quarantined`, `rejected`, `submission_failed`, `publication_pending`, `verification_failed`, `verification_inconclusive`, `link_changed`, `link_removed`, and `expired`.
- Terminal State Invariant: `VALID_TRANSITION_GRAPH[LifecycleState.EXPIRED] == set()` (zero outgoing transitions).

### B. Reporting Engine Aggregation
In `AcquisitionReporter` (`backlink_agent/reporting/acquisition_reporter.py`):
```python
"funnel_metrics": {
    "discovered": total_discovered,
    ...
    "link_removed": funnel.get(LifecycleState.LINK_REMOVED, 0),
    "expired": funnel.get(LifecycleState.EXPIRED, 0),
}
```
State counts are queried dynamically via `SELECT current_state, count(*) ... GROUP BY current_state`, preventing unhandled state exceptions or division-by-zero errors.

### C. TTL Expiration & Audit History
When a prospect exceeds its 90-day time-to-live (TTL) window without resolution:
1. `current_state` is updated to `'expired'`.
2. A transition record (`to_state = 'expired'`, `actor = 'ttl_sweeper'`) is appended to `lifecycle_transitions`.
3. Historical discovery dates, scores, pitch drafts, and submission records remain permanently intact for audit and anti-spam suppression.

---

## 4. Unit Test Verification Evidence

Verified in `backlink_agent/tests/test_wp16_2_verification.py`:
- `test_all_18_states_defined_in_lifecycle_and_accepted_by_sqlite`: PASS
  - Verifies all 18 states defined and counted.
  - Verifies SQLite store registers and transitions prospect to `LifecycleState.EXPIRED`.
  - Verifies transition history retrieved via `get_prospect_transitions()`.
  - Verifies `AcquisitionReporter` includes `expired` count in report data.

All 18 states are compatible across schemas, code, and reporting layers.
