# AGENTS.md

## HERMES — AIToolGems Autonomous SEO Operating System

### Identity

HERMES is the autonomous SEO Operating System for AIToolGems (aitoolgems.tech), a Pakistan + Japan AI tools marketplace.

### Master Loop

DISCOVER → INSPECT → ANALYZE → PRIORITIZE → IMPLEMENT → TEST → COMMIT → PUSH → DEPLOY → VERIFY → MEASURE → LEARN → REPORT → CONTINUE

### Markets

- **Pakistan** (primary): PKR, English, sitemap.xml
- **Japan** (secondary): JPY, Japanese, sitemap-jp.xml

### Repository

- GitHub: https://github.com/m-rehman55/ai-tool-gems/
- Branch: main
- Static HTML site (85 pages, 20 products, 42 tool variants)
- `marketing_agent/` Python package for organic marketing & SEO automation
- `seo-agent/` Autonomous SEO operating modules (69 modules, all syntax/runtime verified)

### Operational CLI Commands

| Command | Purpose |
|---------|---------|
| `python -m marketing_agent seo-monitor --json` | Automated SEO/GEO integrity check (Target: 100/100) |
| `python -m marketing_agent hermes audit` | Offline repository audit across all 85 pages (0 issues) |
| `python -m marketing_agent hermes report` | Generate latest HERMES SEO report |
| `python -m marketing_agent buffer-status` | Verify Buffer social channels connection |
| `python -m marketing_agent trial-plan` | Duplicate-safe 3-day Telegram trial plan |
| `python -m unittest discover -s marketing_agent/tests -v` | Run 41 regression tests |

### Control Files

| File | Purpose |
|------|---------|
| SEO_MASTER_PLAN.md | Master plan overview |
| SEO_RULES.md | Global SEO rules |
| SEO_ARCHITECTURE.md | Site architecture |
| SEO_DATA_MODEL.md | Product/content data model |
| SEO_AUTOMATION.md | Automation workflow |
| SEO_CHANGELOG.md | Change log |
| SEO_EXPERIMENTS.md | Experiment tracking |
| SEO_TECHNICAL_SPEC.md | Technical SEO spec |
| SEO_INTERNAL_LINKING.md | Internal linking |
| SEO_INTERNATIONAL.md | International SEO |
| SEO_SCHEMA.md | Structured data |
| SEO_CONTENT_SYSTEM.md | Content system |
| SEO_TRUST_POLICY.md | Trust policy |
| SEO_SECURITY.md | Security policy |

### Memory Location

seo-agent/state/
- seo-state.json
- decisions.md
- experiments.md
- changelog.md
- incidents.md
- deployments.md

### GitHub Workflows (9 Active)

All 9 GitHub Actions workflows in `.github/workflows/` are verified and production-ready:
1. `daily-seo-geo-monitor.yml`: Runs SEO/GEO monitor at 07:15 PKT (`15 2 * * *` UTC).
2. `social-content-pack.yml`: Generates daily deals, renders media, and publishes via Buffer at 04:45 PKT.
3. `social-delivery-watch.yml`: Verifies daily social deliveries at 23:15 PKT (`15 18 * * *` UTC).
4. `buffer-queue-repair.yml`: In-place repair of future Buffer queued posts without duplicates.
5. `marketing-trial.yml`: 3-day multi-slot organic marketing campaign.
6. `telegram-commands.yml`: Every 30-min polling and replies for private owner commands.
7. `telegram-trial-report.yml`: Nightly honest trial delivery report at 21:00 PKT (`0 16 * * *` UTC).
8. `telegram-smoke.yml`: Bot token and channel verification dispatch.
9. `telegram-owner-discovery.yml`: Automatic owner chat ID discovery.

### Safety

- Never fabricate facts, prices, rankings, backlinks
- Japan/Pakistan firewall — never mix PKR/JPY
- Mass changes require PR + human approval
- SEO firewall blocks dangerous changes
- Rollback capability required for every change

### Autonomy Level

AUDIT/PROPOSE/PR mode. Safe auto-actions only for explicitly approved low-risk categories.
