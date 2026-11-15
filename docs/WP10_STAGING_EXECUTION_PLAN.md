# WP10 Staging Deployment & Live Cloud Acceptance Plan

**Generated:** 2026-11-15  
**Milestone:** Work Package 10 (WP10)  
**Parent Service:** AI Tool Gems (`https://aitoolgems.tech`)  
**Target Environment:** Cloudflare Workers Staging (`--env staging`)  
**Account ID:** `4f7a087d9199c825cced4aa7b66ee81d` (Mrehmanfarooq6@gmail.com)  
**Git Branch:** `feat/backlink-agent-critical-fixes`  
**Status:** **READY FOR EXECUTION IMMEDIATELY UPON WRANGLER LOGIN**

---

## 1. Objective & Boundaries

WP10 transitions the AI Tool Gems 24/7 Autonomous Backlink Agent from local simulated verification to **live Cloudflare staging infrastructure**.

### Strict Operational Boundaries:
- **Zero Production Mutations:** No production Workers, production D1 databases, or production Queues will be created or altered.
- **Zero Public Website Modifications:** Public HTML pages and production sitemaps remain untouched.
- **Zero Autonomous Outreach:** The agent has no automated email dispatch or form-filling logic; approvals only flag records for owner manual submission.
- **Fail-Closed Mode:** Defaults remain `BACKLINK_AGENT_ENABLED="false"` and `BACKLINK_AGENT_MODE="report_only"`.

---

## 2. Immediate Pre-Flight Checklist for the Owner

When you wake up, run the following command in PowerShell or Terminal:

```powershell
cd "d:\Desktop\AI Tools Aura\backlink-worker"
npx wrangler login
```

Once authenticated in your browser, verify:
```powershell
npx wrangler whoami
```
Expected output:
```
Account Name: Mrehmanfarooq6@gmail.com's Account
Account ID:   4f7a087d9199c825cced4aa7b66ee81d
```

---

## 3. Sequential Staging Execution Protocol

### Step 1: Discover & Create Staging D1 Database
```powershell
# Create staging database
npx wrangler d1 create aitoolgems-backlink-agent-staging
```
*Note output `database_id` and replace `"STAGING_D1_ID_PENDING_PROVISION"` in `wrangler.jsonc` under `env.staging.d1_databases[0].database_id`.*

### Step 2: Apply Migrations & Verify Seed Data
```powershell
# Apply D1 schema (6 tables, triggers, replay table, 15 baseline prospects)
npx wrangler d1 execute aitoolgems-backlink-agent-staging --env staging --file=migrations/0001_initial.sql

# Verify seed count
npx wrangler d1 execute aitoolgems-backlink-agent-staging --env staging --command="SELECT count(*) as total FROM prospects;"
```
Expected: `total: 15`.

### Step 3: Create Staging Cloudflare Queues
```powershell
npx wrangler queues create aitoolgems-backlink-jobs-staging
npx wrangler queues create aitoolgems-backlink-dlq-staging
```

### Step 4: Configure Staging Secrets
```powershell
npx wrangler secret put TELEGRAM_BOT_TOKEN --env staging
npx wrangler secret put TELEGRAM_WEBHOOK_SECRET --env staging
npx wrangler secret put TELEGRAM_OWNER_CHAT_ID --env staging
npx wrangler secret put TELEGRAM_OWNER_USER_ID --env staging
```

### Step 5: Deploy Worker to Staging Environment
```powershell
npx wrangler deploy --env staging
```
Output URL: `https://ai-tool-gems-backlink-agent-staging.<subdomain>.workers.dev`

---

## 4. Live Cloud Acceptance Test (LAT) Matrix

Once deployed, the following live tests are executed against the staging endpoint:

| Test ID | Test Scenario | Execution Command / Action | Expected Result | Pass Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **LAT-01** | Health Endpoint Check | `curl -i https://<staging_url>/health` | HTTP 200, JSON status `"healthy"`, 0 secrets exposed | D1 reachable, kill switch reported |
| **LAT-02** | Webhook Unauth Reject | `curl -i -X POST https://<staging_url>/telegram/webhook -d "{}"` | HTTP 401 Unauthorized | Immediate rejection before body parsing |
| **LAT-03** | Webhook Owner Auth | Send `/backlinks` with valid `X-Telegram-Bot-Api-Secret-Token` | HTTP 200, returns pipeline summary with 15 prospects | D1 queried, owner identity verified |
| **LAT-04** | Atomic Concurrency Replay | Send duplicate update ID concurrently | Exactly 1 command executes; second returns duplicate notice | `telegram_processed_updates` enforces single execution |
| **LAT-05** | Approval Concurrency | Send duplicate `/approve dev.to` | First updates row; second returns `"already approved"` notice | Conditional state transition prevents duplicate approvals |
| **LAT-06** | Audit Immutability | Query D1 attempting `DELETE FROM audit_events` | SQLite abort exception: `"audit_events is an immutable append-only ledger"` | Database trigger aborts operation |
| **LAT-07** | Live SSRF Rejection | Enqueue verification for `https://169.254.169.254/` | Dropped with `ValueError: Prohibited IP address target` | Zero requests sent to link-local/private IPs |
| **LAT-08** | Queue & DLQ Retry | Publish malformed job to staging queue | Retried 2 times then routed to `aitoolgems-backlink-dlq-staging` | Message successfully quarantined in DLQ |

---

## 5. 48-Hour Staging Observation Log Template

| Clock Time (UTC) | Elapsed Hours | Cron Event (`0 1,7,13,19`) | Heartbeat (`*/30`) | Queue Backlog | DLQ Count | Incident / Recovery Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `2026-11-15T08:00Z` | 0h (Start) | Deployment verified | First heartbeat | 0 | 0 | Staging burn-in initiated |
| `2026-11-15T13:00Z` | 5h | Run #1 complete (25 verif) | Vital ok (10/10) | 0 | 0 | Normal operations |
| `2026-11-15T19:00Z` | 11h | Run #2 complete (25 verif) | Vital ok (22/22) | 0 | 0 | Normal operations |
| `2026-11-16T01:00Z` | 17h | Run #3 complete (25 verif) | Vital ok (34/34) | 0 | 0 | Normal operations |
| `2026-11-16T07:00Z` | 23h | Run #4 complete (25 verif) | Vital ok (46/46) | 0 | 0 | Normal operations |
| `2026-11-16T13:00Z` | 29h | Run #5 complete (25 verif) | Vital ok (58/58) | 0 | 0 | Normal operations |
| `2026-11-16T19:00Z` | 35h | Run #6 complete (25 verif) | Vital ok (70/70) | 0 | 0 | Normal operations |
| `2026-11-17T01:00Z` | 41h | Run #7 complete (25 verif) | Vital ok (82/82) | 0 | 0 | Normal operations |
| `2026-11-17T08:00Z` | 48h (End) | Run #8 complete (25 verif) | Vital ok (96/96) | 0 | 0 | 48h Burn-in Complete |

---

## 6. Production Go/No-Go Checklist (12 Gates)

1. [ ] Wrangler authentication confirmed against Account `4f7a087d9199c825cced4aa7b66ee81d`.
2. [ ] Staging resources independently provisioned and verified.
3. [ ] Staging database migrations applied with 15 verified prospects.
4. [ ] Worker deployed to staging; `/health` returns healthy.
5. [ ] Telegram webhook secret and owner sender authentication verified live.
6. [ ] Atomic replay protection and concurrent `/approve` state transition verified live.
7. [ ] Audit triggers successfully block attempted `UPDATE` and `DELETE`.
8. [ ] Live SSRF boundaries reject private/loopback/cloud metadata destinations.
9. [ ] Queue retry and DLQ routing verified with test error job.
10. [ ] Kill switch and report-only mode confirmed active.
11. [ ] 48 actual clock hours of error-free staging operation documented.
12. [ ] Owner reviews live evidence and explicitly authorizes production deployment.
