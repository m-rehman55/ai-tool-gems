# WP09 Cloudflare Resource Discovery & Conflict Prevention

**Generated:** 2026-11-15  
**Account:** `4f7a087d9199c825cced4aa7b66ee81d` (Mrehmanfarooq6@gmail.com)  
**Parent Service:** AI Tool Gems (`https://aitoolgems.tech`)

---

## 1. Existing Workspace Discovery

An audit of existing repository files revealed pre-existing Cloudflare configurations:

1. **`chatbot-worker/` Directory:**
   - Account ID: `4f7a087d9199c825cced4aa7b66ee81d`
   - Worker: Customer support / AI assistant worker.
   - Separate scope: Zero overlap with backlink operations.
2. **Current Backlink Agent Scope (`backlink-worker/`):**
   - New autonomous service dedicated entirely to off-page authority verification and Telegram-approved drafting.

---

## 2. Collision-Free Staging Resource Blueprint

To guarantee that staging never collides with production or other workers under the account, all staging resources carry explicit `-staging` naming:

| Resource Type | Resource Name | Purpose | Collision Risk |
| :--- | :--- | :--- | :--- |
| **Worker Script** | `ai-tool-gems-backlink-agent-staging` | Isolated staging Worker | **Zero** (Isolated name) |
| **D1 Database** | `aitoolgems-backlink-agent-staging` | Staging SQLite database | **Zero** (Dedicated DB ID) |
| **Primary Queue** | `aitoolgems-backlink-jobs-staging` | Verification & draft jobs | **Zero** (Separate queue) |
| **Dead-Letter Queue** | `aitoolgems-backlink-dlq-staging` | Quarantined failed tasks | **Zero** (Separate DLQ) |
| **D1 Binding** | `DB` | D1 environment binding | Scoped to worker environment |
| **Queue Producer** | `BACKLINK_QUEUE` | Queue environment binding | Scoped to worker environment |

---

## 3. Production Resource Blueprint (For Future WP11)

When promoted to production after 48-hour staging burn-in, resources will map to:
- Worker Script: `ai-tool-gems-backlink-agent`
- D1 Database: `aitoolgems-backlink-agent`
- Primary Queue: `aitoolgems-backlink-jobs`
- Dead-Letter Queue: `aitoolgems-backlink-dlq`
