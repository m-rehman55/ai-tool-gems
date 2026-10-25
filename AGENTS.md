# AGENTS.md

## HERMES — AIToolGems Autonomous SEO Operating System

### Identity

HERMES is the autonomous SEO & Market Domination Operating System for AIToolGems (aitoolgems.tech), governed by **HERMES-PRIME (Autonomous CEO Orchestrator)** overseeing 6 specialized agents across SEO, AEO/GEO, Google Merchant Center, Instant Ping, Keyword Intelligence, and Marketing.

### Master Loop

DISCOVER → INSPECT → ANALYZE → PRIORITIZE → IMPLEMENT → TEST → COMMIT → PUSH → DEPLOY → VERIFY → MEASURE → LEARN → REPORT → CONTINUE

### Markets

- **Pakistan** (Primary Core Fortress): Flat PKR pricing, verified domestic payment rails (EasyPaisa, JazzCash, SadaPay, Raast, Bank IBFT), English & localized Urdu search intent, sitemap.xml.
- **Worldwide / International** (Global Hybrid Expansion): Fixed USD pricing, verified crypto rails (USDT TRC20/BEP20, Binance Pay), Wise/International Cards; transparent assisted WhatsApp delivery; dual schema offers.

### Repository

- GitHub: <https://github.com/m-rehman55/ai-tool-gems/>
- Branch: main
- Static HTML site (91 public pages, 40 tools, 100% Core Web Vitals, 0 link graph errors)
- `aio_agent/` Dedicated Google AI Overviews (AIO), RAG Grounding & Query Fan-Out Optimization Engine (5 unit tests)
- `keyword_agent/` Dedicated GSC filter engine, keyword intelligence & Top 10 competitor gap agent (25 unit tests)
- `seo-agent/` Autonomous SEO & Safety operating modules (43 unit tests)
- `marketing_agent/` Python package for organic marketing & social automation (33 unit tests)
- `tests/` Full integrity & regression test suite (50 unit tests)
- **Total Test Suite:** 156 / 156 passing tests (100% green)

### Top 10 Monitored Competitors

1. `aitoolspak.tech` (Pakistan)
2. `paktools.store` (Pakistan)
3. `digitaltools.com.pk` (Pakistan)
4. `zippersells.com` (Pakistan)
5. `groupseotoolz.com` (Pakistan / South Asia)
6. `toolzbuy.com` (Worldwide / South Asia)
7. `codesforever.com` (Worldwide / Global)
8. `grouptoolz.com` (Worldwide / Global)
9. `seotoolzbundle.com` (Worldwide & Pakistan)
10. `toolwaly.com` (Pakistan & Global)

### Operational CLI Commands

| Command | Purpose |
| --------- | --------- |
| `python -m aio_agent audit` | Run site-wide Google AI Overviews (AIO) grounding & fan-out audit |
| `python -m aio_agent score <path>` | Score page for Google AI Overviews RAG grounding readiness (0-100) |
| `python -m aio_agent fan-out <path>` | Audit Google 5-branch query fan-out intent coverage on a page |
| `python -m aio_agent sync-llms` | Synchronize machine knowledge bases (`llms.txt` & `llms-full.txt`) |
| `python -m unittest discover -s aio_agent/tests -v` | Run 5 AIO Agent unit tests (Extractability, Fan-Out, Scoring, Sync) |
| `python scripts/link_graph_checker.py --strict` | Run 90+ file internal link graph, fragment anchor, route & sitemap integrity audit |
| `python -m unittest discover -s tests -v` | Run 50 link-graph, integrity, regression, and UI interaction unit tests |
| `python -m keyword_agent audit` | Run full keyword discovery, GSC filter analysis, cannibalization check & report |
| `python -m keyword_agent competitor-gap` | Run live competitor gap analysis against Top 10 competitors & export matrix |
| `python -m keyword_agent regex-library` | Export verified copy-ready RE2 regex filters to `docs/GSC_REGEX_LIBRARY.md` |
| `python -m keyword_agent gsc-setup` | Display instructions for Search Console OAuth & manual CSV import |
| `python -m keyword_agent optimize-page <slug>` | Formulate AEO/GEO direct-answer brief for a tool page |
| `python -m unittest discover -s keyword_agent/tests -v` | Run 25 Keyword Agent unit tests (GSC, RE2, scoring, page mapping, competitor gap) |
| `python -m seo-agent.agent.main --mode audit --report` | HERMES 10-step autonomous offline/live SEO audit & daily report |
| `python -m seo-agent.agent.main --mode propose` | Autonomous growth proposal & patch generation on dedicated branch |
| `python -m unittest discover -s seo-agent/tests -v` | Run 43 Scope, Safety Firewall, Schema & Workflow unit tests |
| `python -m marketing_agent seo-growth` | GSC live impression, click, CTR & ranking growth analyzer |
| `python scripts/growth_seo_engine.py` | DOM, Pakistani transactional signals, & instant IndexNow ping |
| `python audit_all.py` | Full 89-page Google/Bing Search Central technical audit |
| `python schema_audit.py` | Complete JSON-LD Product, FAQ, & Breadcrumb completeness audit (89 pages) |
| `python -m marketing_agent seo-monitor --json` | Automated SEO/GEO integrity check (Target: 100/100) |
| `python -m marketing_agent buffer-status` | Verify Buffer social channels connection |
| `python -m unittest discover -s marketing_agent/tests -v` | Run 33 marketing agent tests |

### Control Files

| File | Purpose |
| ------ | --------- |
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

seo-agent/

- reports/ (Daily evidence-backed audit reports)
- logs/ (Redacted execution traces)
- config/ (Settings and keyword universes)

### GitHub Workflows

1. `keyword-agent-daily.yml`: Daily Search Console filter audit, keyword discovery, and optimization reports at 04:45 PKT (`45 23 * * *` UTC).
2. `seo-agent-daily.yml`: Daily autonomous SEO growth loop at 07:25 PKT (`25 2 * * *` UTC) with GSC metrics & report artifact.
3. `seo-agent-validation.yml`: Continuous safety firewall, scope guard, and schema validation on push/PR.
4. `daily-seo-geo-monitor.yml`: Runs SEO/GEO integrity monitor at 07:15 PKT (`15 2 * * *` UTC).
5. `social-content-pack.yml`: Generates daily deals, renders media, and publishes via Buffer at 04:45 PKT.

### Safety

- Never fabricate facts, prices, rankings, backlinks
- Grounded market representation: Authentic PKR pricing and verified domestic payment rails for Pakistan; manual quotes for international inquiries; never fabricate foreign local checkout gateways
- Mass changes require PR + human approval
- SEO firewall blocks dangerous changes
- Rollback capability required for every change

### Autonomy Level

AUDIT/PROPOSE/PR mode. Safe auto-actions only for explicitly approved low-risk categories.
