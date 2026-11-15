# WP13 — Autonomous Backlink Intelligence Engine Architecture Specification

**Document Version:** 1.0.0  
**Date:** 2026-11-15  
**Author:** HERMES Autonomous Operations & ChatGPT Engineering  
**Branch:** `feat/backlink-agent-critical-fixes`  
**Current Staging Posture:** `report_only` (48-hour Cloudflare burn-in running)  
**Production Posture:** STRICT HOLD  
**Scope:** Local Python Backlink Intelligence Pipeline (`backlink_agent/`)

---

## 1. Executive Summary & Strategic Directive

While the WP12 Cloudflare Workers staging deployment operates undisturbed in its mandatory 48-hour observation window (`2026-11-15T05:50:00Z` to `2026-11-17T05:50:00Z`), the site owner has given explicit orders to advance the long-term system objective without stopping:
> *"hmara goal hy yeah agent banana jo backlinks lagay daily hamri web py, ur koi next move krna hy to chatgpt ky pass chly jana okay but rukna ni hy"*

Per ChatGPT's official architectural review, WP13 establishes the **end-to-end autonomous backlink engine** that finds genuinely relevant, high-authority, white-hat backlink prospects daily, verifies their live evidence, scores their opportunity potential, synthesizes verified submission packages, and delivers actionable, hash-bound Telegram notifications to the owner.

```
Daily Backlink Intelligence Pipeline:
1. Discovery (Competitor gaps · AI Directories · GitHub Awesome Lists · Tech Publications)
   ↓
2. Evidence Verification (Live page · Outbound link · Anchor text · Rel tokens · SSRF guard)
   ↓
3. Opportunity Scoring (100-point framework: Relevance, Editorial, Fit, Risk, Indexability)
   ↓
4. Draft Generation (Directory packages · GitHub PRs · Developer publication pitches)
   ↓
5. Telegram Owner Delivery (Daily batch summary + Hash-bound approval callbacks)
   ↓
6. Controlled Execution & Monitoring (Owner-operated manual submission + Local audit tracking)
```

---

## 2. Non-Negotiable Implementation Boundaries

1. **Staging Isolation:** The deployed WP12 Cloudflare Worker (`ai-tool-gems-backlink-agent-staging`), its D1 database (`aitoolgems-backlink-agent-staging`), queues, cron triggers, and environment variables remain **100% untouched and unmodified**.
2. **Local Python Execution:** All WP13 discovery, scoring, drafting, and notification logic executes strictly in the local Python environment (`backlink_agent/`).
3. **Zero Automated Outreach:** Zero automated public form submission, zero automated GitHub PR creation, zero automated email sending. All approvals strictly authorize manual owner submission (`action_status = 'owner_approved_for_manual_submission'`).
4. **Zero Paid Links / PBNs:** Zero link buying, sponsored placements, PBNs, or reciprocal badge link networks.
5. **Grounded Fact Enforcement:** All generated pitch copy and submission drafts are strictly constrained by `verified_facts.yml` (authentic PKR flat pricing, verified Pakistani payment rails, no fabricated checkout gateways).
6. **Isolated Development Storage:** Local intelligence operations use an isolated SQLite database (`seo-agent/data/backlink_intelligence.db`) and CSV records.

---

## 3. Modular Architecture Overview (`backlink_agent/`)

### A. `prospect_discovery/`
- `discovery_orchestrator.py`: Coordinates daily discovery runs across all enabled sources, dispatches deduplication, and schedules jobs.
- `competitor_gap_discovery.py`: Ingests competitor backlinks (Ahrefs/Semrush exports + existing intelligence in `AI_TOOL_GEMS_COMPETITOR_INTELLIGENCE_2026-11-15/`) and identifies referring domains linking to competitors but missing on AI Tool Gems.
- `directory_discovery.py`: Crawls and classifies directories across Class 1 (AI Aggregators), Class 2 (Tool Showcases), and Class 3 (Technology Directories).
- `github_awesome_discovery.py`: Scans curated GitHub Awesome lists, parses `CONTRIBUTING.md`, verifies category fit, and detects existing entries.
- `technical_publication_discovery.py`: Discovers technical publications, case studies, and blogs where citation of `/prices/` datasets and `llms.txt` is genuinely relevant.
- `deduplication.py`: Enforces canonical composite identity (`normalized_source_page_url + target_asset_url + prospect_type`) to prevent duplicate prospect churn.

### B. `evidence_scoring/`
- `evidence_verifier.py`: Probes candidate pages with SSRF firewall (`validate_worker_url`), extracts HTML DOM anchor elements, rel attributes, canonical tags, and robots meta tags.
- `scoring_engine.py`: Implements the 100-point multi-factor scoring model.

### C. `submission_drafter/`
- `drafting_engine.py`: Orchestrates draft generation, assigns deterministic SHA-256 `draft_hash`, and gates quality.
- `directory_drafter.py`: Pre-fills complete directory submission packages (name, tagline, description, categories, tags, pricing model, logo/favicon, verified facts).
- `github_pr_drafter.py`: Formulates ready-to-submit GitHub PR markdown entries, commit messages, and PR descriptions matching target repo guidelines.
- `publication_pitch_drafter.py`: Prepares technical case study outlines (e.g., *"Building a Transparent AI Tools Pricing Dataset for Pakistan"*).
- `fact_validator.py`: Enforces adversarial checks against `verified_facts.yml`.

### D. `telegram_delivery/`
- `daily_reporter.py`: Compiles the executive daily summary batch.
- `draft_notifier.py`: Formats actionable individual opportunity alerts with hash-bound callback data.
- `outbox.py`: Manages durable, retryable notification delivery.

---

## 4. 100-Point Multi-Factor Scoring Framework

| Criterion | Max Points | Evaluation Basis |
| :--- | :---: | :--- |
| **Relevance** | 25 | Topical match with AI software, subscription services, pricing transparency, or Pakistani tech ecosystem. |
| **Editorial Quality** | 25 | Active editorial curation, human review policy, clear guidelines, low spam footprint. |
| **Brand & Dataset Fit** | 20 | Natural fit for AI Tool Gems catalog, `/prices/` CSV dataset, or `llms.txt`. |
| **Non-Spam & Non-Reciprocal** | 15 | 0% toxic PBN footprint, zero mandatory reciprocal link/badge demands, high trust profile. |
| **Indexability & Authority** | 15 | Google/Bing indexed, clean canonical structure, follow/dofollow or high-trust nofollow context. |
| **TOTAL** | **100** | **Priority: >= 75 High Priority (Draft ready); 55–74 Investigate; < 55 Reject/Quarantine.** |

---

## 5. Development Milestones (WP13-A to WP13-G)

| Milestone | Title | Scope & Deliverables | Status |
| :--- | :--- | :--- | :--- |
| **WP13-A** | Architecture & Repo Audit | Technical specification, module layout, data schema design | ✅ **CURRENT** |
| **WP13-B** | Discovery Engine | Competitor gap ingest, directory discovery, GitHub awesome list discovery, deduplication | ⏳ READY |
| **WP13-C** | Evidence & Scoring Engine | Live evidence probe, SSRF safety, 100-point scoring implementation | ⏳ READY |
| **WP13-D** | Drafting Engine | Directory packages, GitHub PR packages, dev pitch drafter, fact validator | ⏳ READY |
| **WP13-E** | Telegram Executive Pipeline | Daily batch reporter, hash-bound preview cards, durable outbox | ⏳ READY |
| **WP13-F** | Local Acceptance Suite | Comprehensive unit tests, end-to-end dry run verification | ⏳ READY |
| **WP13-G** | Cloud Integration (Future) | Edge sync formulation post-WP12 48-hour burn-in completion | 🔒 GATED |
