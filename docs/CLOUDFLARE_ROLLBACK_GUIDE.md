# AI Tool Gems — Backlink Agent Cloudflare Rollback & Incident Guide

**Document Purpose:** Immediate Incident Mitigation, Global Kill Switch, and Worker Rollback  
**Operational Target:** Restore System to Known Safe Baseline Within 60 Seconds  

---

## 1. Level 1: Immediate Emergency Kill Switch (< 10 Seconds)

If any unexpected outbound requests, upstream rate limits, or false classifications occur, execute the global database kill switch. This requires zero code changes or redeployments:

```bash
cd "d:\Desktop\AI Tools Aura\backlink-worker"
npx wrangler d1 execute aitoolgems-backlink-agent --remote \
  --command "UPDATE agent_control SET control_value = 'false', updated_at = CURRENT_TIMESTAMP WHERE control_key = 'enabled';"
```

### Effect of Kill Switch:
- All scheduled cron triggers (`0 1,7,13,19 * * *`, `0 3 * * 0`, `*/30 * * * *`) abort immediately at Step 1.
- All queued messages in `aitoolgems-backlink-jobs` are acknowledged and discarded without making network calls.
- Webhook approval commands return a notice that the agent is disabled.

---

## 2. Level 2: Cloudflare Worker Deployment Rollback (< 60 Seconds)

If a newly deployed worker version introduces syntax errors or unexpected behavior:

1. **List Recent Deployments:**
   ```bash
   npx wrangler deployments list
   ```
2. **Rollback to Previous Stable Version:**
   ```bash
   npx wrangler rollback <DEPLOYMENT_ID>
   ```

---

## 3. Level 3: Telegram Webhook Disablement (< 30 Seconds)

To disconnect the Telegram bot from the Cloudflare Worker and restore local/polling operation:

```bash
curl -X POST https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/deleteWebhook
```

To verify the webhook has been cleared:
```bash
curl https://api.telegram.org/bot<YOUR_TELEGRAM_BOT_TOKEN>/getWebhookInfo
```
*(Should return `"url": ""`)*.

---

## 4. Level 4: Complete Edge Resource De-Provisioning

If the owner decides to remove the Cloudflare worker and queues entirely:

```bash
# 1. Delete Worker
npx wrangler delete ai-tool-gems-backlink-agent

# 2. Delete Queues
npx wrangler queues delete aitoolgems-backlink-jobs
npx wrangler queues delete aitoolgems-backlink-dlq

# 3. Delete D1 Database (CAUTION: Destroys historical verification logs)
npx wrangler d1 delete aitoolgems-backlink-agent
```

---

## 5. Local Repository Rollback

The entire Cloudflare deployment package is strictly isolated in `backlink-worker/` on feature branch `feat/backlink-agent-critical-fixes`. The `main` branch remains 100% clean and untouched.

To discard local branch changes:
```bash
git checkout main
git branch -D feat/backlink-agent-critical-fixes
```
