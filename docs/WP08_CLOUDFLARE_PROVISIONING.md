# WP08 Cloudflare Infrastructure Provisioning & Deployment Specification

**Generated:** 2026-11-15  
**Cloudflare Account ID:** `4f7a087d9199c825cced4aa7b66ee81d`  
**Account Name:** Mrehmanfarooq6@gmail.com's Account  
**Status:** **INFRASTRUCTURE CONFIG READY / AUTH TOKEN RENEWAL REQUIRED**

---

## 1. Authentication Status & Resolution

During pre-deployment verification, executing `npx wrangler whoami` produced:
```
[ERROR] Not logged in. Your auth token has expired and could not be refreshed, and the environment is non-interactive. Run wrangler login in an interactive terminal or set a CLOUDFLARE_API_TOKEN.
```

### Required One-Line Owner Action

To authenticate Wrangler and allow automated provisioning, execute either of the following from the project root (`d:\Desktop\AI Tools Aura\backlink-worker`):

**Option A (Interactive Web Login):**
```powershell
npx wrangler login
```

**Option B (CI/CD API Token):**
Set environment variable with permissions for Workers Scripts, D1, Queues, and Cron:
```powershell
$env:CLOUDFLARE_API_TOKEN = "<YOUR_CLOUDFLARE_API_TOKEN>"
```

---

## 2. Staging Infrastructure Creation Commands

Once authenticated, execute the following commands sequentially to provision isolated staging resources:

### Step 1: Create Staging D1 Database
```powershell
npx wrangler d1 create aitoolgems-backlink-agent-staging
```
*Note output `database_id` and replace `"STAGING_D1_ID_PENDING_PROVISION"` in `backlink-worker/wrangler.jsonc` under `env.staging.d1_databases[0].database_id`.*

### Step 2: Apply Database Schema & Baseline Prospects
```powershell
npx wrangler d1 execute aitoolgems-backlink-agent-staging --env staging --file=migrations/0001_initial.sql
```

### Step 3: Create Staging Queues
```powershell
# Create primary job queue
npx wrangler queues create aitoolgems-backlink-jobs-staging

# Create dead-letter queue
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

---

## 3. Webhook Registration (Staging)

After deploying to staging, register the Telegram webhook with secret token enforcement:

```powershell
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook" `
  -H "Content-Type: application/json" `
  -d '{
    "url": "https://ai-tool-gems-backlink-agent-staging.<workers_subdomain>.workers.dev/telegram/webhook",
    "secret_token": "<TELEGRAM_WEBHOOK_SECRET>",
    "allowed_updates": ["message"]
  }'
```

---

## 4. Production Promotion Checklist

Production deployment follows identical commands targeting the root environment (`wrangler deploy` without `--env staging`). Promotion requires:
1. Full 48-hour error-free staging burn-in.
2. Verified receipt of 4x daily verification cron triggers in staging logs.
3. Verification of `/backlinks` and `/approve` commands via Telegram in staging.
4. Formal Go/No-Go signoff as defined in `docs/WP08_PRODUCTION_GO_NO_GO.md`.
