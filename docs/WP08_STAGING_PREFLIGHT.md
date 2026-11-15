# WP08 Staging Preflight & Code Inventory

**Generated:** 2026-11-15  
**Target Environment:** Cloudflare Workers Python (`ai-tool-gems-backlink-agent-staging`)  
**Account ID:** `4f7a087d9199c825cced4aa7b66ee81d` (Mrehmanfarooq6@gmail.com)  
**Parent Service:** AI Tool Gems (`https://aitoolgems.tech`)  
**Git Branch:** `feat/backlink-agent-critical-fixes`

---

## 1. Executive Summary

This preflight document inventories all components, configuration schemas, runtime constraints, and dependencies for deploying the **AI Tool Gems 24/7 Autonomous Backlink Agent Worker** to Cloudflare Workers staging environment.

The architecture eliminates laptop dependency, executing scheduled verification runs (4x daily) and weekly draft cycles (Sunday 08:00 PKT) in serverless edge isolation with zero automated external mutations.

---

## 2. File & Module Inventory

| File Path | Role & Purpose | Runtime Environment | External Dependencies |
| :--- | :--- | :--- | :--- |
| `backlink-worker/wrangler.jsonc` | Multi-environment configuration (root + staging), D1 binding, queue triggers, cron schedule | Wrangler CLI / Cloudflare Edge | `@cloudflare/workers-types` |
| `backlink-worker/migrations/0001_initial.sql` | 6 D1 relational tables (`prospects`, `verification_runs`, `drafts`, `job_runs`, `audit_events`, `agent_control`) + 15 seed prospects | Cloudflare D1 (SQLite) | None (Pure SQL) |
| `backlink-worker/src/entry.py` | Python `WorkerEntrypoint` implementation routing HTTP `fetch()`, Cron `scheduled()`, and Queue `queue()` | Cloudflare Python / Pyodide | Python stdlib (`json`, `urllib`) |
| `backlink-worker/src/d1_adapter.py` | Abstracted database adapter supporting both Cloudflare D1 prepared statements and local SQLite | Dual-mode (Worker & Local) | Python stdlib (`sqlite3`, `json`) |
| `backlink-worker/src/verifier_worker.py` | DOM anchor parser (`HTMLParser`), multi-hop redirect validator, Content-Type guard, and SSRF firewall | Worker & Local | Python stdlib (`html.parser`, `ipaddress`, `urllib`) |
| `backlink-worker/src/approval_worker.py` | Hardened Telegram webhook handler with `X-Telegram-Bot-Api-Secret-Token`, exact `from.id` checks, replay guard | Worker & Local | Python stdlib (`hmac`, `hashlib`, `json`) |
| `backlink-worker/src/queue_handlers.py` | Asynchronous queue batch processor with idempotency lock, kill switch verification, and DLQ retries | Worker & Local | Python stdlib (`datetime`, `uuid`) |
| `backlink-worker/src/health.py` | Diagnostic `/health` endpoint reporting D1 connectivity, kill switch state, and pending queues | Worker & Local | Python stdlib (`json`, `datetime`) |

---

## 3. Dependency Compatibility & Zero-C-Extension Audit

Cloudflare Python workers execute in a WebAssembly sandbox via **Pyodide**. Native C-extensions requiring precompiled shared objects (`.so`/`.pyd`) are prohibited unless bundled with Pyodide.

- **Zero Third-Party Binary Dependencies:** The entire `backlink-worker` is written using **100% Python Standard Library** modules:
  - `html.parser` for DOM traversal and anchor resolution (replaces BeautifulSoup/lxml).
  - `urllib.parse` for strict URL normalization and query preservation.
  - `ipaddress` for CIDR subnet containment and loopback/private IP blocking.
  - `hmac` and `hashlib` for constant-time secret comparison and SHA-256 draft hashing.
  - `json`, `datetime`, `uuid` for structured serialization and audit logging.
- **Local Testability:** Every module executes identically under CPython 3.10+ during CI/CD (`unittest`) and under Pyodide at the edge.

---

## 4. Staging Resource Names

| Resource Type | Resource Identifier | Purpose |
| :--- | :--- | :--- |
| **Worker Script** | `ai-tool-gems-backlink-agent-staging` | Isolated staging worker instance |
| **D1 Database** | `aitoolgems-backlink-agent-staging` | Separate SQLite database for staging verification |
| **Primary Queue** | `aitoolgems-backlink-jobs-staging` | Asynchronous job pipeline (verifications & drafts) |
| **Dead-Letter Queue** | `aitoolgems-backlink-dlq-staging` | Quarantined failed jobs for root cause analysis |
| **D1 Database Binding** | `DB` | Cloudflare D1 environment binding |
| **Queue Producer Binding** | `BACKLINK_QUEUE` | Cloudflare Queue publisher binding |

---

## 5. Security & Isolation Controls

1. **Staging Database Isolation:** Staging runs against `aitoolgems-backlink-agent-staging`. Production databases are never shared or touched.
2. **Safe Defaults:** `BACKLINK_AGENT_ENABLED="false"`, `BACKLINK_AGENT_MODE="report_only"`.
3. **Owner Approval Boundary:** Telegram commands only change D1 `action_status` to `owner_approved_for_manual_submission`. The worker possesses zero outbound email, webhook mutation, or automated form-filling capabilities.
4. **Secrets Redaction:** `/health` endpoint exposes zero Telegram bot tokens, secret tokens, or D1 keys.
