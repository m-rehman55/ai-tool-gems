# WP12 — Isolated Cloudflare Staging Preflight & Authentication Guide

**Document Version:** 1.0.0  
**Date:** 2026-11-15  
**Author:** HERMES Autonomous Operations & ChatGPT Engineering  
**Branch:** `feat/backlink-agent-critical-fixes`  
**Commit:** `398a1d8`  
**Status:** READY FOR LIVE CLOUDFLARE RUNTIME PROVISIONING

---

## 1. Executive Preflight Summary

Work Packages 01 through 11 have established the complete codebase for the AI Tool Gems 24/7 Serverless Backlink Agent. Every component has been designed with zero-trust architectural boundaries:
- **Repository Health:** 316 / 316 Passing Unit Tests (100% green across all 8 project suites).
- **Git HEAD:** `398a1d8ed972eeaabedde8bce8e3a8286cb0c913` on `feat/backlink-agent-critical-fixes`.
- **Target Cloudflare Account:** `4f7a087d9199c825cced4aa7b66ee81d` ("Mrehmanfarooq6@gmail.com's Account").
- **Staging Isolation Principle:** Zero shared state, zero production webhook mutation, zero public website modifications. Production remains on **STRICT HOLD**.

---

## 2. Mandatory Authentication Step

Wrangler OAuth token in the non-interactive environment has expired. To provision the isolated staging environment, the owner must run interactive authentication:

```powershell
cd "d:\Desktop\AI Tools Aura\backlink-worker"
npx wrangler login
```
*Alternatively, the owner can set an API token:*
```powershell
$env:CLOUDFLARE_API_TOKEN = "<YOUR_CLOUDFLARE_API_TOKEN>"
```

### Identity Verification Command
```powershell
npx wrangler whoami
```
Expected output:
```text
Getting User settings...
👋 You are logged in with an OAuth Token, associated with the email 'mrehmanfarooq6@gmail.com'!
Account Name: Mrehmanfarooq6@gmail.com's Account
Account ID:   4f7a087d9199c825cced4aa7b66ee81d
```

---

## 3. Resource Discovery & Conflict Audit

Before creating any new resources, execute discovery to inspect existing Workers, D1 databases, and Queues:

```powershell
# 1. Discover existing D1 databases
npx wrangler d1 list

# 2. Discover existing Queues
npx wrangler queues list

# 3. Discover existing Workers
npx wrangler deployments list --name ai-tool-gems-backlink-agent-staging
```

---

## 4. Staging Isolation Architecture

| Resource Layer | Production Configuration (STRICT HOLD) | Isolated Staging Target (WP12) | Isolation Guarantee |
| :--- | :--- | :--- | :--- |
| **Worker Name** | `ai-tool-gems-backlink-agent` | `ai-tool-gems-backlink-agent-staging` | Distinct worker script, distinct domain/route |
| **D1 Database** | `aitoolgems-backlink-agent` | `aitoolgems-backlink-agent-staging` | Physically separated database partition |
| **Queue Producer** | `aitoolgems-backlink-jobs` | `aitoolgems-backlink-jobs-staging` | Independent message broker |
| **Dead Letter Queue** | `aitoolgems-backlink-dlq` | `aitoolgems-backlink-dlq-staging` | Independent failure capture |
| **Telegram Bot** | Owner Production Bot | Dedicated Staging Bot | Dedicated webhook URL & secret; production bot untouched |
| **Agent State** | `BACKLINK_AGENT_ENABLED="false"` | `BACKLINK_AGENT_ENABLED="false"` | Fail-closed kill switch default |
| **Agent Mode** | `BACKLINK_AGENT_MODE="report_only"` | `BACKLINK_AGENT_MODE="report_only"` | Draft & verify only; zero automated outreach |

---

## 5. One-Line Zero-Touch Provisioning Script

Once authenticated, run the following automated PowerShell script from `backlink-worker/`:

```powershell
# 1. Create Staging D1 Database
$d1_output = npx wrangler d1 create aitoolgems-backlink-agent-staging --json | ConvertFrom-Json
$staging_d1_id = $d1_output.uuid
Write-Host "Provisioned Staging D1 Database ID: $staging_d1_id"

# 2. Create Staging Queues
npx wrangler queues create aitoolgems-backlink-jobs-staging
npx wrangler queues create aitoolgems-backlink-dlq-staging

# 3. Apply Schema & Seed Migrations to Staging D1
npx wrangler d1 execute aitoolgems-backlink-agent-staging --file=migrations/0001_initial.sql

# 4. Set Staging Secrets
npx wrangler secret put TELEGRAM_BOT_TOKEN --env staging
npx wrangler secret put TELEGRAM_WEBHOOK_SECRET --env staging
npx wrangler secret put TELEGRAM_OWNER_CHAT_ID --env staging
npx wrangler secret put TELEGRAM_OWNER_USER_ID --env staging

# 5. Deploy Staging Worker
npx wrangler deploy --env staging
```
