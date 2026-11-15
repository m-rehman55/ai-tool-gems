# WP15: Cloud Integration Architecture Proposal (Cloudflare Worker & D1 Unification)

**Document Version:** 1.0.0  
**Status:** Architecture Proposal (Strict Hold until 48h Staging Burn-In Concludes)  
**Governing Standard:** HERMES Autonomous SEO Operating System  

---

## 1. Executive Context & Invariant

> **CRITICAL INVARIANT:**
> The active Cloudflare staging deployment (`ai-tool-gems-backlink-agent-staging.mrehmanfarooq6.workers.dev`) and its D1 database (`aitoolgems-backlink-agent-staging`) are currently in an immutable **48-Hour Burn-In Observation Window** (`2026-11-15T05:50:00Z` to `2026-11-17T05:50:00Z`).
> **Zero modifications, redeployments, restarts, or migrations may touch the staging worker during this window.**

This document specifies the target architecture for extending the Cloudflare Worker and D1 database to incorporate WP15 lifecycle tables, outcome webhooks, and verification queues *after* the 48-hour burn-in concludes.

---

## 2. Target D1 Schema Additions (Post-Observation)

The following tables will be migrated to Cloudflare D1 via a dedicated migration script (`migrations/0002_wp15_acquisition_lifecycle.sql`):

```sql
-- 1. Full 17-state lifecycle table
CREATE TABLE IF NOT EXISTS prospect_lifecycle (
    prospect_id TEXT PRIMARY KEY,
    domain TEXT NOT NULL,
    current_state TEXT NOT NULL DEFAULT 'discovered',
    score REAL DEFAULT 0.0,
    priority_tier TEXT DEFAULT 'quarantine',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 2. Append-only lifecycle transition audit log
CREATE TABLE IF NOT EXISTS lifecycle_transitions (
    transition_id TEXT PRIMARY KEY,
    prospect_id TEXT NOT NULL,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    transition_timestamp TEXT NOT NULL,
    actor TEXT NOT NULL,
    reason TEXT NOT NULL,
    evidence_hash TEXT,
    FOREIGN KEY (prospect_id) REFERENCES prospect_lifecycle(prospect_id)
);

-- 3. Manual submission receipts & editorial tracking
CREATE TABLE IF NOT EXISTS manual_submission_evidence (
    submission_id TEXT PRIMARY KEY,
    prospect_id TEXT NOT NULL,
    submission_url TEXT NOT NULL,
    submitted_by TEXT NOT NULL,
    submission_notes TEXT NOT NULL,
    submission_date TEXT NOT NULL,
    FOREIGN KEY (prospect_id) REFERENCES prospect_lifecycle(prospect_id)
);

-- 4. Long-term retention audit snapshots
CREATE TABLE IF NOT EXISTS retention_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    prospect_id TEXT NOT NULL,
    audit_timestamp TEXT NOT NULL,
    days_since_first_verified INTEGER NOT NULL,
    milestone_reached TEXT NOT NULL,
    retention_status TEXT NOT NULL,
    http_status INTEGER NOT NULL,
    is_indexable INTEGER NOT NULL,
    current_anchor_text TEXT,
    current_rel_tokens TEXT,
    current_content_hash TEXT,
    change_detected INTEGER NOT NULL,
    change_summary TEXT,
    FOREIGN KEY (prospect_id) REFERENCES prospect_lifecycle(prospect_id)
);
```

---

## 3. Worker Execution Flow & Scheduled Crons

The target Cloudflare Python Worker runtime will support:
1. **Daily Intelligence Cron (`0 2 * * *` UTC):** Ingests new prospects, runs evidence scoring, and stages drafts in D1 outbox.
2. **Weekly Retention Cron (`0 3 * * SUN` UTC):** Probes earned backlinks at Day 7, 30, and 90 milestones via fetch API with subrequest caps.
3. **Telegram Approval Webhook:** Processes inline button callbacks with `BEGIN IMMEDIATE` batch assertions and lease fencing.
4. **Manual Submission Endpoint (`POST /api/submissions/record`):** Authenticated endpoint allowing the human operator to record submission receipts with secret scrubbing.

---

## 4. Migration Plan & Safety Guardrails

- **Prerequisite:** Staging burn-in completed with 0 errors across 48 continuous hours.
- **Rollback Provision:** All D1 migrations must be reversible via downward migration scripts.
- **Dry-Run Validation:** Local SQLite models mirror D1 schema 1:1, allowing full verification before applying cloud migrations.
