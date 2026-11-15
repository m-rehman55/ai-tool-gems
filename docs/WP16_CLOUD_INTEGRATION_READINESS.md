# WP16: Cloud Integration Architectural Readiness Assessment

**Document Version:** 1.0.0  
**Phase:** Phase 8 (Cloud Integration Readiness)  
**Verification Date:** 2026-11-15  
**Governing Standard:** HERMES Autonomous SEO Operating System  

---

## 1. Executive Status & Absolute Boundaries

> **CRITICAL POSTURE:**
> The Cloudflare staging worker (`https://ai-tool-gems-backlink-agent-staging.mrehmanfarooq6.workers.dev`) and D1 database (`aitoolgems-backlink-agent-staging`) remain in their mandatory **48-Hour Burn-In Observation Window** (`2026-11-15T05:50:00Z` to `2026-11-17T05:50:00Z`).
> **Zero modifications, redeployments, restarts, or migrations may touch the staging worker during this window.**

This document provides the technical readiness audit for connecting WP15/WP16 modules to Cloudflare Edge infrastructure *only after* the 48-hour burn-in observation concludes with zero errors.

---

## 2. Cloudflare D1 Target Schema Migration Specification

Once the 48-hour staging observation completes, the following tables will be provisioned in D1 via `npx wrangler d1 execute aitoolgems-backlink-agent-staging --file=migrations/0002_wp16_lifecycle.sql`:

```sql
-- Migration 0002: Acquisition Lifecycle & Retention
CREATE TABLE IF NOT EXISTS prospect_lifecycle (
    prospect_id TEXT PRIMARY KEY,
    prospect_domain TEXT NOT NULL,
    source_page_url TEXT NOT NULL,
    target_asset_url TEXT NOT NULL,
    prospect_type TEXT NOT NULL,
    current_state TEXT NOT NULL DEFAULT 'discovered',
    score INTEGER NOT NULL DEFAULT 0,
    priority_tier TEXT,
    draft_id TEXT,
    draft_hash TEXT,
    submission_ref TEXT,
    publication_url TEXT,
    first_verified_at TEXT,
    last_verified_at TEXT,
    retention_days INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS lifecycle_transitions (
    transition_id TEXT PRIMARY KEY,
    prospect_id TEXT NOT NULL,
    from_state TEXT NOT NULL,
    to_state TEXT NOT NULL,
    actor TEXT NOT NULL,
    reason TEXT NOT NULL,
    evidence_json TEXT,
    idempotency_key TEXT UNIQUE,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (prospect_id) REFERENCES prospect_lifecycle(prospect_id)
);

CREATE TABLE IF NOT EXISTS manual_submission_evidence (
    submission_id TEXT PRIMARY KEY,
    prospect_id TEXT NOT NULL,
    draft_id TEXT NOT NULL,
    draft_hash TEXT NOT NULL,
    destination TEXT NOT NULL,
    method TEXT NOT NULL,
    evidence_ref TEXT NOT NULL,
    publication_url TEXT,
    notes TEXT,
    submission_date TEXT NOT NULL,
    FOREIGN KEY (prospect_id) REFERENCES prospect_lifecycle(prospect_id)
);
```

---

## 3. Worker Runtime Compatibility & Subrequest Budget

The Cloudflare Python Worker runtime (Pyodide) imposes specific constraints that must be accounted for:
1. **Subrequest Limit:** Cloudflare Workers allow up to 50 subrequests per invocation on Workers Paid plans (or 50 on standard requests). The verifier's `max_redirects = 5` and single-hop checks fit comfortably within this budget.
2. **CPU Execution Time:** Worker CPU time is capped at 50ms (or 30s on Unbound/Cron). Deep DOM parsing of 2MB HTML must use lightweight streaming regex or chunked parsing to prevent CPU limits.
3. **Pyodide External SDK Flag:** The `compatibility_flags = ["python_workers", "disable_python_external_sdk"]` setting validated in WP12 must be preserved.

---

## 4. Controlled Staging Integration Roadmap (Post-WP12 Observation)

1. **Step 1 (Nov 17 05:50 UTC):** Conclude 48-hour observation window. Extract Cloudflare Worker metrics, tail logs, and D1 assertion records.
2. **Step 2 (Local Dry-Run):** Apply `0002_wp16_lifecycle.sql` locally against SQLite test fixtures to verify migration reversibility.
3. **Step 3 (Staging D1 Migration):** Apply D1 migration on `aitoolgems-backlink-agent-staging`.
4. **Step 4 (Staging Acceptance Testing):** Re-run Live Cloud Acceptance Tests (LAT-01 through LAT-08) and verify lifecycle transition endpoints.
5. **Step 5 (Production Review):** Submit complete staging report to site owner and ChatGPT for final production authorization.
