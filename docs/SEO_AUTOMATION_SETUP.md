# Autonomous SEO & Daily Blog Automation Setup Guide

**Repository:** `m-rehman55/ai-tool-gems`  
**Production Site:** [https://aitoolgems.tech/](https://aitoolgems.tech/)  
**Primary Target Market:** Pakistan (`en-PK`, PKR prices, EasyPaisa, JazzCash, WhatsApp delivery)  
**Author:** AI Tool Gems Autonomous Engineering Team  
**Last Verified:** 2026-10-11

---

## 1. System Architecture

The AI Tool Gems Autonomous SEO Content Automation System is a production-grade, zero-maintenance pipeline designed specifically for our custom-coded static site deployed on GitHub Pages. It discovers, drafts, optimizes, validates, and deploys high-converting, Pakistan-focused AI guides and blogs.

```text
[ data/seo/content-queue.json ] (Approved Topics)
               │
               ▼
[ scripts/auto_blog_publisher.py ] ◄── [ Google Gemini API ] (Dynamic insights, optional)
               │
               ├─► [ scripts/validate_content.py ]
               │     ├── Anti-Cannibalization Check (data/seo/keyword-map.json)
               │     ├── Internal Links Check (data/seo/internal-link-map.json)
               │     ├── Density & Anti-Stuffing (0.5%–2.0%)
               │     ├── Single H1, Meta Title & Desc Bounds (20–65 / 70–170 chars)
               │     └── JSON-LD Schema (Article, BreadcrumbList, FAQPage)
               │
               ▼
[ Production Artifacts ]
   ├── /guides/<slug>/index.html
   ├── sitemap.xml (52+ canonical URLs)
   ├── sitemap.txt
   ├── llms.txt (AI bot context)
   ├── guides/index.html (Card grid showcase)
   └── index.html (#blog-guides showcase)
               │
               ▼
[ GitHub Actions Validation Gate ]
   ├── python scripts/build_url_inventory.py
   ├── python audit_all.py (0 errors / 0 warnings)
   ├── python schema_audit.py (100% complete)
   └── python scripts/growth_seo_engine.py --live (Instant IndexNow Ping)
```

---

## 2. Sequence of Execution

1. **Topic Selection & Deduplication:** The engine checks `data/seo/content-queue.json` for approved topics not yet published in `guides/*/index.html`.
2. **Anti-Cannibalization Gate:** The engine verifies that the candidate's primary keyword and secondary entities do not collide with any existing entry in `data/seo/keyword-map.json`.
3. **Draft Generation & Local Enrichment:** Content is generated with in-depth technical analysis, PKR pricing tables, Pakistani banking payment instructions (EasyPaisa, JazzCash, SadaPay), and official vendor citations.
4. **Contextual Internal Linking:** 2+ related tool links and 2+ contextual guide links are injected using verified targets from `data/seo/internal-link-map.json`.
5. **Technical Pre-Publish Validation:** The validator (`scripts/validate_content.py`) enforces:
   - Word count $\ge 1,200$ words.
   - Exact title length (20–65 chars) and meta description length (70–170 chars).
   - Exactly one H1 tag.
   - Self-referential `<link rel="canonical">`.
   - Valid JSON-LD schemas (`Article`, `BreadcrumbList`, `FAQPage`).
   - All internal links resolve to physical files on disk.
   - Zero foreign currency contamination (no Japan/JPY tokens).
6. **Controlled Publication:** When running in `--publish` mode, the engine updates `sitemap.xml`, `llms.txt`, `guides/index.html`, and `data/seo/keyword-map.json`.
7. **Instant Search Engine Indexing:** `scripts/growth_seo_engine.py --live` submits the fresh URLs directly to Bing and IndexNow-compatible search engines.

---

## 3. GitHub Secrets Configuration

To operate the automated daily publisher, configure the following repository secrets under **Settings → Secrets and variables → Actions**:

| Secret Name | Required? | Purpose |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Optional | Free Google AI Studio API key used for dynamic Gemini 1.5 Flash expansion. If absent, the engine uses our high-converting structured template fallback. |
| `TELEGRAM_BOT_TOKEN` | Optional | Telegram bot token used for Hermes shift alerts and publication notifications. |
| `TELEGRAM_OWNER_CHAT_ID` | Optional | Owner Telegram Chat ID to receive instant alerts. |

> [!CAUTION]
> **Never commit secret values into source code, documentation, reports, or PR logs.**

---

## 4. Local CLI Commands

All components can be tested and executed locally in PowerShell or Bash:

```powershell
# 1. Rebuild and verify the machine-readable 52-page URL inventory
python scripts/build_url_inventory.py

# 2. Run dry-run preview of the next daily blog article
python scripts/auto_blog_publisher.py

# 3. Test validation on any specific guide HTML file
python scripts/validate_content.py guides/cursor-ai-pakistan/index.html cursor-ai-pakistan

# 4. Run the complete 56-page technical HTML SEO audit
python audit_all.py

# 5. Run the JSON-LD schema completeness audit (Target: 100%)
python schema_audit.py

# 6. Run the Autonomous SEO Growth Engine with IndexNow ping
python scripts/growth_seo_engine.py --live

# 7. Run 41 regression unit tests
python -m unittest discover -s marketing_agent/tests -v
```

---

## 5. Enabling or Disabling Automated Publishing

- **Safe Approval Mode (Default):**  
  In `.github/workflows/daily-blog-publisher.yml`, the scheduled cron (`00 00 * * *` UTC / 05:00 AM PKT) creates a clean, tested Pull Request (`automated-daily-blog`) for human review. Once you approve and merge the PR, GitHub Pages automatically deploys the article and IndexNow pings search engines.
- **Direct Auto-Publish Mode:**  
  You can manually trigger the workflow via **GitHub Actions → Autonomous Daily SEO Blog Publisher → Run workflow** and select `auto` from the `publish_mode` dropdown to commit and deploy directly to `main`.
- **Pausing the System:**  
  To temporarily suspend automated publishing, disable the workflow in the GitHub Actions tab or set `"approved_for_publishing": false` in `data/seo/content-queue.json`.

---

## 6. How to Add or Reject Topics

### Adding a New Topic:
Append a new entry to `data/seo/content-queue.json`:
```json
{
  "slug": "new-ai-tool-pakistan",
  "title": "New AI Tool in Pakistan: Pricing & Guide (2026)",
  "meta_description": "Complete guide to New AI Tool in Pakistan with PKR pricing...",
  "primary_keyword": "New AI Tool Pakistan",
  "secondary_keywords": ["buy New AI Tool PKR", "New AI Tool EasyPaisa"],
  "target_audience": "Pakistani software developers and freelancers",
  "primary_tool": "chatgpt",
  "related_tools": [{"slug": "chatgpt", "name": "ChatGPT Plus"}],
  "official_sources": ["https://vendor.com"],
  "pakistani_payment_support": ["EasyPaisa", "JazzCash"],
  "approved_for_publishing": true,
  "priority": 1
}
```

### Rejecting or Skipping a Topic:
Set `"approved_for_publishing": false` in `data/seo/content-queue.json`.

---

## 7. Verifying a Published Page

After deployment to GitHub Pages (`aitoolgems.tech`):
1. **HTTP Status & Canonical:** Confirm `https://aitoolgems.tech/guides/<slug>/` returns HTTP 200 with matching canonical tag.
2. **Schema Test:** Paste the URL into the [Google Rich Results Test](https://search.google.com/test/rich-results) — it should detect `Article`, `BreadcrumbList`, and `FAQPage`.
3. **IndexNow Ping:** Verify that `scripts/growth_seo_engine.py` reported `IndexNow Status: success`.
4. **Navigation:** Verify that the article card appears on [aitoolgems.tech/guides/](https://aitoolgems.tech/guides/) and on the homepage showcase.

---

## 8. Known Safeguards & Limitations

1. **Daily Cadence:** Capped at 1 article per scheduled run to maintain maximum quality and avoid flooding search engines.
2. **Price Integrity:** Prices are strictly cross-referenced against the verified first-party PKR catalog; zero simulated or unverified claims are permitted.
3. **No Foreign Currency Contamination:** Any article mentioning foreign currency tokens (such as Japanese Yen) is automatically rejected by the pre-publish validator.
