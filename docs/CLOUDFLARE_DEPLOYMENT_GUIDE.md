# AI Tool Gems — Backlink Agent Cloudflare 24/7 Deployment Guide

**Target Environment:** Cloudflare Workers (Python) + D1 + Queues  
**Worker Directory:** `backlink-worker/`  
**Configuration File:** `backlink-worker/wrangler.jsonc`  
**Migration Directory:** `backlink-worker/migrations/`  

---

## 1. Prerequisites & Account Verification

Ensure the following tools are installed on the local system:
- **Node.js & npm:** Verified working.
- **Wrangler CLI:** Verified (`wrangler 4.162.0` available via `npx wrangler`).
- **Cloudflare Account ID:** `4f7a087d9199c825cced4aa7b66ee81d` (configured in `wrangler.jsonc`).

To confirm Cloudflare authentication:
```bash
npx wrangler whoami
```

---

## 2. Step-by-Step Cloud Resource Provisioning

Navigate to the worker directory before executing wrangler commands:
```bash
cd "d:\Desktop\AI Tools Aura\backlink-worker"
```

### Step 2.1 — Create Cloudflare Queues
Create the primary asynchronous job queue and its associated dead-letter queue:
```bash
npx wrangler queues create aitoolgems-backlink-jobs
npx wrangler queues create aitoolgems-backlink-dlq
```

### Step 2.2 — Create Cloudflare D1 Database
Create the dedicated relational database:
```bash
npx wrangler d1 create aitoolgems-backlink-agent
```
*Note: Wrangler will output the generated `database_id` (e.g., `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`). Copy this ID and paste it into `backlink-worker/wrangler.jsonc` under `d1_databases[0].database_id`.*

### Step 2.3 — Apply Database Migrations (Remote)
Apply `migrations/0001_initial.sql` to instantiate the schema and seed the 15 baseline prospects:
```bash
npx wrangler d1 migrations apply aitoolgems-backlink-agent --remote
```
To verify the migration remotely:
```bash
npx wrangler d1 execute aitoolgems-backlink-agent --remote --command "SELECT count(*) FROM prospects;"
```
*(Expected output: 15)*

---

## 3. Configure Encrypted Secrets

Never store sensitive credentials in `wrangler.jsonc` or commit them to Git. Set them securely via the Wrangler secret manager:

```bash
# 1. Telegram Bot Token
npx wrangler secret put TELEGRAM_BOT_TOKEN

# 2. Telegram Owner Chat ID (Numeric Chat ID)
npx wrangler secret put TELEGRAM_OWNER_CHAT_ID

# 3. Telegram Owner User ID (Optional 2FA User Check)
npx wrangler secret put TELEGRAM_OWNER_USER_ID
```

---

## 4. Local Testing & Preflight Simulation

Before deploying to production, run the local emulation server:
```bash
npx wrangler dev
```
In a secondary terminal, verify the health endpoint:
```bash
curl http://localhost:8787/health
```
Expected response:
```json
{
  "status": "healthy",
  "service": "ai-tool-gems-backlink-agent",
  "runtime": "cloudflare-workers",
  "gates": {
    "kill_switch_enabled": false,
    "mode": "report_only",
    "owner_approval_required": true,
    "automated_outreach": false
  }
}
```

---

## 5. Production Deployment

Deploy the worker to Cloudflare's global edge:
```bash
npx wrangler deploy
```
Wrangler will output the live URL:
`https://ai-tool-gems-backlink-agent.<your-subdomain>.workers.dev`

---

## 6. Configure Telegram Webhook

To enable real-time owner approvals over Telegram (eliminating the need for 30-minute cron polling), set the Telegram webhook to your worker's live URL:

```bash
curl -F "url=https://ai-tool-gems-backlink-agent.<your-subdomain>.workers.dev/telegram/webhook" \
  https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/setWebhook
```

To verify webhook status:
```bash
curl https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/getWebhookInfo
```

---

## 7. Enabling / Disabling the Agent Kill Switch

The worker is **fail-closed** by default (`enabled = 'false'`). To dynamically enable or disable the agent without redeploying code:

### Enable Agent (Report-Only Mode):
```bash
npx wrangler d1 execute aitoolgems-backlink-agent --remote \
  --command "UPDATE agent_control SET control_value = 'true', updated_at = CURRENT_TIMESTAMP WHERE control_key = 'enabled';"
```

### Emergency Kill Switch (Instant Shutoff):
```bash
npx wrangler d1 execute aitoolgems-backlink-agent --remote \
  --command "UPDATE agent_control SET control_value = 'false', updated_at = CURRENT_TIMESTAMP WHERE control_key = 'enabled';"
```
*(All queued and cron jobs immediately terminate without network calls when `enabled != 'true'`)*.
