# AIToolGems Autonomous Worldwide SEO & AI Search Growth Agent

Production-conscious, autonomous SEO and AI Search Growth Agent exclusively built for **AI Tool Gems Pakistan** ([https://aitoolgems.tech/](https://aitoolgems.tech/)).

---

## 1. Mission & Exclusive Scope

- **Primary Market:** Pakistan (Exclusive commercial scope: PKR pricing, EasyPaisa, JazzCash, Pakistani developer context).
- **Secondary Scope:** Relevant worldwide search visibility and AI answer engine discoverability (Google AI Overviews, Perplexity, ChatGPT Search, Claude).
- **Prohibited Content:** 100% prohibited from introducing Japan/JP content, JPY currency, or foreign payment methods.
- **Evidence-Based Policy:** Never invent metrics, rankings, citations, or prices. Work strictly from measured crawl data, GSC metrics, and validated repository content.

---

## 2. Evidence-Based Scope Inventory (JP Purge Baseline)

An audit of the repository confirmed:
- Zero `/jp/` directories or routes exist.
- Zero JPY / Japanese Yen currency symbols exist in the catalog or HTML pages.
- All 57 static pages enforce `lang="en-PK"`, PKR pricing signals, and local payment methods (`EasyPaisa`, `JazzCash`).
- Automated tests (`test_scope_guard.py`) continuously enforce this barrier.

---

## 3. Architecture & Directory Scaffolding

```text
seo-agent/
├── README.md
├── requirements.txt
├── config/
│   ├── settings.example.yml
│   └── keyword-map.example.csv
├── agent/
│   ├── __init__.py
│   ├── scope_guard.py         # Enforces Pakistan-exclusive scope, blocks foreign contamination
│   ├── safety_firewall.py     # Production gate: blocks secret leaks, destructive ops, price changes
│   ├── decision_engine.py     # Evaluates tasks by Impact, Confidence, Risk, Cost -> Action Tier
│   ├── crawler.py             # Polite, bounded website & local repository crawler
│   ├── technical_audit.py     # Audits indexing, canonicals, titles, robots, sitemaps, Core Web signals
│   ├── schema_validator.py    # Audits Schema.org JSON-LD (Product, FAQ, Breadcrumb, Organization)
│   ├── internal_links.py      # Audits graph connectivity, orphans, broken links, click depth
│   ├── keyword_research.py    # Manages keyword clusters, search intent, gap detection
│   ├── content_quality.py     # Audits anti-cannibalization, depth, anti-stuffing, readability
│   ├── content_planner.py     # Produces evidence-backed briefs & drafts for missing clusters
│   ├── monitoring.py          # Interfaces with GSC and local trend baselines
│   ├── reporting.py           # Generates structured daily markdown & JSON audit reports
│   ├── github_integration.py  # Prepares reviewable Git branches, patches, and pull requests
│   ├── orchestrator.py        # 10-step autonomous execution loop coordinator
│   └── main.py                # CLI entry point supporting AUDIT, PROPOSE, and PR modes
├── reports/                   # Daily evidence-backed audit reports
├── logs/                      # Redacted runtime logs
└── tests/
    ├── test_scope_guard.py
    ├── test_safety_firewall.py
    ├── test_technical_audit.py
    ├── test_content_quality.py
    └── test_workflows.py
```

---

## 4. Operational Modes & Safety Firewall

1. **AUDIT Mode (Default / Zero-Risk):**
   Runs preflight, crawls site, performs technical/schema/content audit, checks GSC metrics, and writes an evidence-backed report to `reports/`. No git branch or code modifications are made.
2. **PROPOSE Mode:**
   Prepares minimal, targeted patches on a dedicated branch (e.g. `seo-growth/YYYY-MM-DD`). Does not push or publish.
3. **PR Mode:**
   Opens a GitHub Pull Request with full test results, diffs, and rollback instructions for human review.
4. **Production Publish:**
   Strictly requires human approval and merges through GitHub branch protection. Direct writes to `main` are blocked.

---

## 5. Verification Commands

```bash
# Run test suite
python -m unittest discover -s seo-agent/tests -v

# Run local offline audit
python -m seo-agent.agent.main --mode audit

# Run local audit with report generation
python -m seo-agent.agent.main --mode audit --report
```
