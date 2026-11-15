# WP16.1 Lifecycle State Machine Topology & Database Compatibility

**Date:** 2026-11-15  
**Branch:** `feat/backlink-agent-critical-fixes`  
**Target:** AI Tool Gems (`https://aitoolgems.tech/`)  
**Adjudication Scope:** 18-State Lifecycle Topology, Rationale for `expired`, and Cloudflare D1 / SQLite Schema Compatibility  

---

## 1. Executive Summary

In WP15, the core lifecycle was designed around 17 primary operational states. During WP16 release candidate hardening, an 18th state—`expired`—was formally introduced into `backlink_agent/lifecycle/models.py` (`LifecycleState.EXPIRED = "expired"`).

This document explains:
1. The architectural role of `expired` as a durable aging and garbage-collection boundary.
2. The complete 18-state transition matrix.
3. Database backward and forward schema compatibility across Cloudflare D1 and local SQLite stores.

---

## 2. The 18-State Canonical Classification

The 18 states are categorized into two distinct operational groups:

### A. Canonical Acquisition Progression (9 States)
These represent the forward-moving happy path:
1. `discovered`: Unscored prospect identified by multi-channel discovery engine.
2. `evidence_verified`: Seed metadata, submission endpoints, and ownership verified.
3. `scored`: 100-point 5-dimension algorithmic assessment completed (quality tier assigned).
4. `draft_ready`: Contextual pitch and non-spam anchor text generated from `verified_facts.yml`.
5. `owner_approved`: Cryptographically verified owner approval received via Telegram `/approve`.
6. `manually_submitted`: Owner completed external submission and logged non-secret proof.
7. `published`: External site published listing or guest post containing AI Tool Gems mention.
8. `backlink_verified`: Advanced DOM verifier confirmed live `<a>` tag, target URL, and canonical indexability.
9. `retained`: Retention monitor verified ongoing presence across Day 7, Day 30, and Day 90 milestones.

### B. Terminal, Side, and Remediation States (9 States)
These represent exception handling, security quarantines, failures, and end-of-life:
10. `quarantined`: Low quality (<55/100), toxic signals, or reciprocal link demands detected (isolated).
11. `rejected`: Explicitly rejected by owner via Telegram `/reject` or policy violation.
12. `submission_failed`: Manual submission could not be completed or form rejected.
13. `publication_pending`: Submission logged, awaiting editorial publication.
14. `verification_failed`: External publication page verified, but AI Tool Gems backlink was not present.
15. `verification_inconclusive`: Transient network error, rate limit, or CDN block during verification.
16. `link_changed`: Link modified (e.g. anchor text changed, rel attribute shifted to nofollow/sponsored).
17. `link_removed`: Multi-stage verification confirmed backlink permanently removed (HTTP 410 or repeat 404).
18. `expired`: Stale prospect or abandoned pipeline entry safely retired after retention limit (>90 days).

---

## 3. Rationale & Behavioral Semantics of the 18th State (`expired`)

### Problem
Without `expired`, prospects that were:
- Discovered but never evaluated or acted upon within 90 days,
- Left in `draft_ready` without owner approval for months,
- Left in `publication_pending` where the external site never approved or published the submission, or
- Confirmed as `link_removed` and observed for 90 days with no recovery,
would remain permanently in active tables or clutter operator dashboards, creating memory and query latency overhead.

### Architectural Solution
`expired` acts as a durable, auditable archive state:
- **Zero Outgoing Transitions:** Once marked `expired`, the prospect is terminal (`VALID_TRANSITION_GRAPH[LifecycleState.EXPIRED] == set()`).
- **Audit Preservation:** All historical draft hashes, audit events, and scores remain permanently preserved in SQLite/D1 for compliance and anti-spam suppression.
- **Deduplication Suppression:** Discovered domains that are `expired` are prevented from re-entering discovery queues unless explicitly cleared by owner configuration.

### Allowed Ingoing Transitions to `expired`:
- `discovered` -> `expired` (discovery TTL exceeded)
- `evidence_verified` -> `expired` (verification TTL exceeded)
- `scored` -> `expired` (scoring TTL exceeded)
- `draft_ready` -> `expired` (approval TTL exceeded)
- `publication_pending` -> `expired` (editorial timeout exceeded)
- `verification_failed` -> `expired` (failed link retention timeout)
- `link_removed` -> `expired` (post-removal observation completed)

---

## 4. Cloudflare D1 and SQLite Schema Compatibility

### SQLite / D1 Column Definitions
In both Cloudflare D1 (`backlink-worker/migrations/0001_initial.sql`) and Local SQLite (`backlink_agent/lifecycle/store.py`):
```sql
CREATE TABLE IF NOT EXISTS prospects (
    id TEXT PRIMARY KEY,
    prospect_domain TEXT NOT NULL,
    action_status TEXT NOT NULL DEFAULT 'active',
    link_status TEXT NOT NULL DEFAULT 'not_live',
    ...
);
```

### Zero Breaking Schema Changes
1. **Unconstrained Text Columns:** `action_status` and `link_status` are defined as `TEXT NOT NULL` without restrictive `CHECK(status IN (...))` constraints that would block new state tokens.
2. **Deterministic State Machine Enforcement:** State validity is strictly enforced in the application layer via `VALID_TRANSITION_GRAPH`.
3. **No Migration Required for Staging D1:** The live Cloudflare D1 staging database (`aitoolgems-backlink-agent-staging`) accepts `action_status = 'expired'` without schema alteration or table recreation.
4. **Idempotent Lease Token Protection:** All lifecycle transitions continue to require atomic lease token validation and record immutable audit logs.
