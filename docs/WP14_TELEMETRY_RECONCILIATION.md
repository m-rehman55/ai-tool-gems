# WP14 Cross-System Telemetry Reconciliation Specification
**Document Version:** 1.0.0  
**Date:** 2026-11-15  
**Status:** Approved & Enforced  

---

## 1. Multi-Tier Telemetry Architecture

HERMES operates across three discrete execution environments with explicit boundaries:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        HERMES TELEMETRY MAPPING                        │
│                                                                        │
│   [ Tier 1: Local / GitHub Runner ]      [ Tier 2: Cloudflare Staging ]│
│   • SQLite Outbox (backlink_outbox.db)   • D1 Database (HKG)           │
│   • Intelligence Reports (JSON/MD)       • Cloudflare Queues           │
│   • Verified Facts (verified_facts.yml)  • Edge Cron Triggers          │
│   • Discovery Engine Cache               • Health Probe (/health)      │
│                     │                                   │              │
│                     └─────────────────┬─────────────────┘              │
│                                       ▼                                │
│                          [ Tier 3: Remote Search ]                     │
│                          • Google Search Console API                   │
│                          • IndexNow Endpoint (api.indexnow.org)        │
│                          • Telegram Bot API (api.telegram.org)         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Telemetry Invariant Alignment

| Telemetry Field | Source of Truth | Permitted Values | Synchronization Cadence |
|---|---|---|---|
| `prospect_status` | D1 `prospects` / CSV `backlinks_tracker.csv` | `active`, `submitted`, `verified_live`, `owner_approved_for_manual_submission`, `quarantined` | Daily at 07:23 PKT |
| `outbox_status` | SQLite `outbox_messages` | `pending`, `sending`, `dry_run_simulated`, `accepted_by_telegram`, `delivery_unknown`, `retry_pending`, `failed` | Real-time during flush |
| `confirmed_live_backlinks` | Verifier HTML DOM parser | Non-negative integer (verified `<a>` tags with `200 OK`) | Weekly Sunday 08:00 PKT |
| `kill_switch_state` | Cloudflare D1 `system_settings` / ENV | `ENABLED` (active) / `DISABLED` (safe mode) | Continuous probe |

---

## 3. Discrepancy Reconciliation Rules

1. **Local vs Edge Prospect Count:**
   - Seed prospects in D1 (15 items) represent baseline tracking targets.
   - Newly discovered prospects in SQLite outbox represent *candidate leads*.
   - Lead records only sync to D1 after passing 100-point scoring ($\ge 75$) AND receiving explicit owner approval.
2. **Staging Burn-In Protection:**
   - During the active 48-hour staging burn-in (`2026-11-15T05:50:00Z` to `2026-11-17T05:50:00Z`), zero telemetry sync mutations may target the staging D1 database.
   - All WP14 telemetry is generated, verified, and persisted locally and via GitHub Actions workflow artifacts.
