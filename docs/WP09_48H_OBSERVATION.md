# WP09 48-Hour Staging Observation Protocol

**Generated:** 2026-11-15  
**Service:** AI Tool Gems Cloudflare Backlink Agent Staging  
**Status:** **PROTOCOL DEFINED / PENDING STAGING DEPLOYMENT START**

---

## 1. Ground Rules & Timing Enforcement

> [!IMPORTANT]
> Per autonomous safety guidelines and ChatGPT instructions:
> **The 48-hour observation period cannot be claimed complete until 48 actual clock hours have elapsed following live staging deployment.**
> Simulated or accelerated time does not satisfy this operational requirement.

---

## 2. Observation Metrics & Checklist

During the 48-hour burn-in period, the following metrics will be observed:

| Observation Dimension | Target Standard | Failure Threshold | Action on Failure |
| :--- | :--- | :--- | :--- |
| **Verification Cron Cadence** | Minimum 8 scheduled runs observed (`0 1,7,13,19 * * *`) | $<7$ successful cron executions | Investigate Cloudflare Cron Triggers in Dashboard |
| **Heartbeat Vital Signs** | 96 heartbeat records in `audit_events` (`*/30 * * * *`) | $>2$ consecutive heartbeats missed | Check worker CPU time or edge unhandled exceptions |
| **Queue Backlog** | Zero stuck queue messages; all processed $\le 30\text{s}$ | $>10$ messages backlog for $>5$ minutes | Check queue consumer concurrency and batch size |
| **Dead-Letter Queue (DLQ)** | 0 messages routed to DLQ under normal operation | $\ge 1$ DLQ message | Inspect D1 `job_runs.error` for target site failures |
| **Replay & Concurrency** | 100% duplicate updates rejected cleanly | Duplicate entries in `audit_events` | Activate kill switch, investigate transaction isolation |
| **Zero External Mutation** | 0 outbound emails or automated forms dispatched | Any external automated mutation | Immediate freeze of worker via D1 `agent_control` |

---

## 3. Log Querying During Observation

To inspect runtime metrics during the 48-hour period:

```powershell
# Real-time tailing of staging logs:
npx wrangler tail ai-tool-gems-backlink-agent-staging --env staging

# Querying D1 audit trail for heartbeat vitality:
npx wrangler d1 execute aitoolgems-backlink-agent-staging --env staging --command="SELECT event_type, count(*) as count, max(created_at) as last_seen FROM audit_events GROUP BY event_type;"

# Querying verification runs recorded in D1:
npx wrangler d1 execute aitoolgems-backlink-agent-staging --env staging --command="SELECT classification, count(*) FROM verification_runs GROUP BY classification;"
```
