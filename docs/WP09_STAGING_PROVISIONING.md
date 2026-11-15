# WP09 Staging Provisioning Plan & Execution Blueprint

**Generated:** 2026-11-15  
**Target Environment:** Staging (`--env staging`)  
**Parent Service:** AI Tool Gems (`https://aitoolgems.tech`)  
**Status:** **READY FOR EXECUTION IMMEDIATELY AFTER TOKEN RENEWAL**

---

## 1. Automated Provisioning Sequence

Once `npx wrangler whoami` confirms active authentication, the following sequence provisions all staging infrastructure:

### Step 1: Create Staging D1 Database
```powershell
cd "d:\Desktop\AI Tools Aura\backlink-worker"
npx wrangler d1 create aitoolgems-backlink-agent-staging
```
*Action: Copy the generated `database_id` and update `backlink-worker/wrangler.jsonc` under `env.staging.d1_databases[0].database_id`.*

### Step 2: Apply Migrations & Seed Baseline Data
```powershell
npx wrangler d1 execute aitoolgems-backlink-agent-staging --env staging --file=migrations/0001_initial.sql
```
*Verification Check:*
```powershell
npx wrangler d1 execute aitoolgems-backlink-agent-staging --env staging --command="SELECT count(*) as total_prospects FROM prospects;"
```
Expected output: `total_prospects: 15`.

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

### Step 5: Deploy Worker to Staging
```powershell
npx wrangler deploy --env staging
```
Output will provide the public staging URL:
`https://ai-tool-gems-backlink-agent-staging.<subdomain>.workers.dev`

---

## 2. Baseline Prospects Integrity Verification

The initial schema seeds exactly 15 verified prospects:
1. `github.com` (Repo About - 95 relevance)
2. `github.com` (Profile - 90 relevance)
3. `agentwebmap.com` (llms.txt Directory - 92 relevance)
4. `eudk/awesome-ai-tools` (Awesome List - 88 relevance)
5. `saashub.com` (SaaS Directory - 84 relevance)
6. `startupnetwork.pk` (Pakistan Startup Directory - 82 relevance)
7. `startups.pasha.org.pk` (PASHA Startup Hub - 78 relevance)
8. `altftool.com` (AI Directory - 68 relevance)
9. `hooshware.net` (AI Directory - 66 relevance)
10. `dev.to` (Technical Article - 85 relevance)
11. `hashnode.com` (Developer Publication - 83 relevance)
12. `futuretools.io` (Ineligible - 35 relevance)
13. `toolpilot.ai` (Ineligible Reciprocal - 25 relevance)
14. `aitooldiscovery.com` (Ineligible Reciprocal Badge - 25 relevance)
15. `OuterSpacee/awesome-ai-tools` (Ineligible Mismatch - 45 relevance)

Re-executing `0001_initial.sql` uses `INSERT OR IGNORE`, preventing duplicates.
