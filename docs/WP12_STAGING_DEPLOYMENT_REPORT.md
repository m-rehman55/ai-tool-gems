# WP12 — Staging Deployment & Execution Report

**Document Version:** 1.0.0  
**Date:** 2026-11-15  
**Author:** HERMES Autonomous Operations & ChatGPT Engineering  
**Branch:** `feat/backlink-agent-critical-fixes`  
**Git HEAD:** `398a1d8`  
**Environment:** STAGING (`ai-tool-gems-backlink-agent-staging`)

---

## 1. Environment & Runtime Specifications

- **Worker Name:** `ai-tool-gems-backlink-agent-staging`
- **Main Entrypoint:** `src/entry.py`
- **Compatibility Date:** `2026-11-15`
- **Compatibility Flags:** `["python_workers"]`
- **D1 Database Binding:** `DB` (`aitoolgems-backlink-agent-staging`)
- **Queue Binding:** `BACKLINK_QUEUE` (`aitoolgems-backlink-jobs-staging`)
- **Dead Letter Queue:** `aitoolgems-backlink-dlq-staging`
- **Max Batch Size / Timeout:** 2 messages / 10 seconds
- **Max Retries:** 2
- **Cron Triggers:** `0 1,7,13,19 * * *`, `0 3 * * 0`, `*/30 * * * *`
- **Kill Switch Default:** `BACKLINK_AGENT_ENABLED="false"`
- **Operating Mode:** `BACKLINK_AGENT_MODE="report_only"`

---

## 2. Migration Execution Audit

Migrations to be applied to the provisioned staging D1 database from `migrations/0001_initial.sql`:

1. `prospects` table: 13 columns, index on `link_status`, `action_status`, `prospect_domain`. Seeded with 15 initial target prospects across GitHub, Dev.to, Medium, Reddit, etc.
2. `drafts` table: 8 columns, foreign key to `prospects.id`, index on `prospect_id` and `status`.
3. `verification_runs` table: 18 columns, capturing DOM parsing, rel tokens, HTTP status, redirect chain, canonical URL, and error message.
4. `job_runs` table: 6 columns, unique index on `idempotency_key` ensuring zero duplicate queue job processing.
5. `audit_events` table: 6 columns, with append-only triggers (`prevent_audit_update`, `prevent_audit_delete`) blocking any `UPDATE` or `DELETE` statements.
6. `telegram_processed_updates` table: 10 columns, atomic `update_id` primary key, `lease_recoveries` counter, `lease_token`, and `response_text`.
7. `_d1_transaction_assertions` table: ephemeral assertion table enforcing `CHECK (is_valid = 1)` to trigger D1 batch rollback on conditional mismatch.
8. `agent_control` table: dynamic database-backed kill switch controls.

---

## 3. Deployment Safety Gates

- [x] Staging resource naming completely isolated from production.
- [x] Production webhook configuration remains untouched on owner bot.
- [x] Fail-closed environment variables enforced in `wrangler.jsonc`.
- [x] Strict SSRF firewall blocks all RFC private, loopback, link-local, carrier, and IPv4-mapped IPv6 ranges.
- [x] All 42 worker unit tests passing locally before deployment dispatch.
- [ ] Live Cloud Acceptance Tests (LAT-01 to LAT-08) pending owner interactive authentication.
