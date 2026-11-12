# AI Tool Gems (`aitoolgems.tech`)

Official repository for **[AI Tool Gems](https://aitoolgems.tech/)** -- a curated AI tools directory, buyer guidance hub, and **Pakistan AI Tools Pricing Tracker** in Pakistani Rupees (PKR) and US Dollars (USD).

## Core Resources
- **Canonical Website:** [https://aitoolgems.tech/](https://aitoolgems.tech/)
- **Pakistan AI Tools Pricing Index (Research Hub):** [https://aitoolgems.tech/prices/](https://aitoolgems.tech/prices/)
  - Downloadable CSV dataset: [`prices/ai-tools-pricing-pakistan.csv`](prices/ai-tools-pricing-pakistan.csv)
  - Downloadable JSON dataset: [`prices/ai-tools-pricing-pakistan.json`](prices/ai-tools-pricing-pakistan.json)
- **Machine-Readable Site Index:** [`llms.txt`](llms.txt) & [`sitemap.xml`](sitemap.xml)
- **Verified Social Profiles:** See `Organization.sameAs` in [`index.html`](index.html)

## Repository Architecture & Automation
- `tools/`, `guides/`, `category/`, `prices/`, `deals/`: Static HTML pages built for GitHub Pages via [`scripts/build_public_site.py`](scripts/build_public_site.py).
- `seo-agent/` & `scripts/offpage_authority_tracker.py`: SEO audit, metadata integrity, and closed-loop off-page authority tracker (`seo-agent/data/offpage_authority_tracker.csv`).
- `marketing_agent/` & `.agents/skills/`: Bounded SOP skills (`geo-aeo-optimizer`, `off-page-authority-builder`) and launch kits.
- `tests/`: Regression, schema, allowlist, link-graph, and off-page integrity tests.

## Verification
```bash
python3 -m unittest discover -s tests
python3 scripts/offpage_authority_tracker.py --validate
python3 scripts/link_graph_checker.py --strict
python3 audit_all.py
```
