# WP08 Operations Runbook & Triage SOP

**Generated:** 2026-11-15  
**Service:** AI Tool Gems 24/7 Autonomous Backlink Agent Worker  
**Runtime:** Cloudflare Workers Python + D1 + Queues  
**Audience:** Site Owner, Autonomous Orchestrator (HERMES-PRIME)

---

## 1. Routine Operations & Cadence

The worker operates autonomously on predefined schedules:

| Cadence | Cron Expression | Scheduled Action | Failure Behavior |
| :--- | :--- | :--- | :--- |
| **4x Daily** | `0 1,7,13,19 * * *` | Backlink verification batch of up to 25 prospects | Unreachable targets retry up to 3 times before routing to DLQ |
| **Weekly** | `0 3 * * 0` (Sunday 08:00 PKT) | Executive draft generation cycle (up to 5 drafts) | Logged to D1 `drafts` table; awaiting owner `/approve` command |
| **Heartbeat** | `*/30 * * * *` | Audit event record confirming cron vitality | Emits warning if heartbeat missed for $>2$ consecutive cycles |

---

## 2. Emergency Controls: Immediate Kill Switch

If unexpected behavior occurs, the worker can be instantly frozen via D1 without redeploying code.

### Activation: Immediate Freeze
```powershell
# From local terminal:
npx wrangler d1 execute aitoolgems-backlink-agent --command="UPDATE agent_control SET enabled = 0, updated_at = CURRENT_TIMESTAMP WHERE id = 'global';"

# For staging:
npx wrangler d1 execute aitoolgems-backlink-agent-staging --env staging --command="UPDATE agent_control SET enabled = 0, updated_at = CURRENT_TIMESTAMP WHERE id = 'global';"
```
**Effect:** All subsequent cron jobs and queue workers fail closed immediately without executing HTTP fetches or modifying data.

### Deactivation: Resume Normal Operations
```powershell
npx wrangler d1 execute aitoolgems-backlink-agent --command="UPDATE agent_control SET enabled = 1, updated_at = CURRENT_TIMESTAMP WHERE id = 'global';"
```

---

## 3. Real-Time Telemetry & Log Streaming

To view live runtime events and errors in real time:

```powershell
# Production Worker logs
npx wrangler tail ai-tool-gems-backlink-agent

# Staging Worker logs
npx wrangler tail ai-tool-gems-backlink-agent-staging --env staging
```

Filter specifically for errors or webhook events:
```powershell
npx wrangler tail ai-tool-gems-backlink-agent --format=pretty --status=error
```

---

## 4. Dead-Letter Queue (DLQ) Triage

When a prospect cannot be verified after 3 retries (due to persistent DNS failure, 5xx gateway errors, or SSL issues), the job is routed to `aitoolgems-backlink-dlq`.

### Inspection:
```powershell
# Query audit trail for failed job runs
npx wrangler d1 execute aitoolgems-backlink-agent --command="SELECT id, job_type, error_message, created_at FROM job_runs WHERE status = 'failed' ORDER BY id DESC LIMIT 10;"
```

### Resolution:
1. If the target domain is permanently dead, update prospect in D1:
   ```sql
   UPDATE prospects SET action_status = 'permanently_unreachable' WHERE prospect_domain = 'target-domain.com';
   ```
2. If temporary, requeue job using Wrangler or await next scheduled run.

---

## 5. Owner Telegram Interactive Commands

All Telegram operations must originate from `TELEGRAM_OWNER_CHAT_ID` via private 1-on-1 chat:

- `/backlinks`: Displays summary of tracked links, live count, verified count, and top 5 pending prospects.
- `/backlink <domain>`: Inspects detailed verification history and anchor text for a specific domain.
- `/approve <domain>`: Marks draft as approved for manual outreach (`owner_approved_for_manual_submission`). Records SHA-256 hash in D1 audit trail.
- `/reject <domain> <reason>`: Marks draft as rejected with owner justification.
- `/defer <domain>`: Defers review to next weekly cycle.
- `/backlink_report`: Triggers on-demand executive status report.
