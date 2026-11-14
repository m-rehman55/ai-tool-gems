# 10. GSC Forensic Evidence Index & Audit Trail

**Property:** `sc-domain:aitoolgems.tech`  
**Site:** `https://aitoolgems.tech/`  
**Auditor:** HERMES Quality Assurance & Forensics Team  
**Audit Execution Date:** November 14, 2026  

---

## 1. Overview

This document provides the definitive verification index, linking all empirical evidence, live browser screenshots, execution logs, subagent trajectories, and generated investigative artifacts created during the Google Search Console forensic investigation.

---

## 2. Visual Browser Screenshot Evidence Catalog

| Evidence ID | GSC Section / Report | Live GSC URL Inspected | Screenshot Artifact Path | Key Empirical Observation |
| :---: | :--- | :--- | :--- | :--- |
| **IMG-01** | **Search Console Insights** | `https://search.google.com/search-console/insights?resource_id=sc-domain%3Aaitoolgems.tech` | `brain/e4317de8-bc27-46c2-a38a-abbfb133d840/gsc_insights.png` | Clicks up +89.5% (36 clicks), Impressions up +289.1% (1,280), Average position 12.9 (+1.2). |
| **IMG-02** | **Crawl Stats Overview** | `https://search.google.com/search-console/settings/crawl-stats?resource_id=sc-domain%3Aaitoolgems.tech` | `brain/e4317de8-bc27-46c2-a38a-abbfb133d840/gsc_crawl_stats.png` | 1.47k total requests, 13.9 MB downloaded, 106ms avg response time. Response breakdown: 89% 200, 10% 404. |
| **IMG-03** | **Robots.txt & Recrawl** | `https://search.google.com/search-console/settings/robots-txt?resource_id=sc-domain%3Aaitoolgems.tech` | `brain/e4317de8-bc27-46c2-a38a-abbfb133d840/gsc_robots_txt.png` | Status: Fetched (951 B, 0 errors). Recrawl request successfully dispatched (*"Recrawl request sent"*). |
| **IMG-04** | **Page Indexing Overview** | `https://search.google.com/search-console/index?resource_id=sc-domain%3Aaitoolgems.tech` | `brain/e4317de8-bc27-46c2-a38a-abbfb133d840/gsc_indexing.png` | 103 Indexed Pages, 18 Not Indexed (14 legacy `/jp/` 404s, 1 redirect `/index.html`, 2 UTM canonicals, 1 crawled: `bolt-new`). |
| **IMG-05** | **Merchant Listings Warnings** | `https://search.google.com/search-console/r/merchant-listings?resource_id=sc-domain%3Aaitoolgems.tech` | `brain/e4317de8-bc27-46c2-a38a-abbfb133d840/gsc_merchant_listings.png` | 26 items flagged for `hasMerchantReturnPolicy` & `shippingDetails`. Zero errors. Product snippets 100% valid. |
| **IMG-06** | **Google AI Overviews (SGE)** | `https://search.google.com/search-console/performance/search-analytics/ai?resource_id=sc-domain%3Aaitoolgems.tech` | `brain/e4317de8-bc27-46c2-a38a-abbfb133d840/gsc_ai_overview.png` | 150 impressions across 38 URLs in AI Overviews; 89.3% in Pakistan; Claude guide top cited (30 citations). |
| **IMG-07** | **Search Performance Filter** | `https://search.google.com/search-console/performance/search-analytics?resource_id=sc-domain%3Aaitoolgems.tech` | `brain/e4317de8-bc27-46c2-a38a-abbfb133d840/gsc_performance.png` | `tools/allinone/` at Pos 8.9 (287 imp, 0 clicks), `prices/` at Pos 10.1 (140 imp, 0 clicks). High CTR opportunity. |

---

## 3. Dossier Documentation Artifacts

All 10 investigation deliverables are organized within `docs/gsc/`:

1. [01_GSC_COMPLETE_EXPLORATION_REGISTER.md](file:///d:/Desktop/AI%20Tools%20Aura/docs/gsc/01_GSC_COMPLETE_EXPLORATION_REGISTER.md): Exploration status of all 35 GSC sections.
2. [02_GSC_MASTER_FORENSIC_REPORT.md](file:///d:/Desktop/AI%20Tools%20Aura/docs/gsc/02_GSC_MASTER_FORENSIC_REPORT.md): Comprehensive forensic findings and technical analysis.
3. [03_GSC_CRAWL_STATS_FORENSIC_REPORT.md](file:///d:/Desktop/AI%20Tools%20Aura/docs/gsc/03_GSC_CRAWL_STATS_FORENSIC_REPORT.md): Deep Googlebot crawl breakdown (responses, file types, purposes, bots).
4. [04_GSC_INDEXING_URL_INVESTIGATION.csv](file:///d:/Desktop/AI%20Tools%20Aura/docs/gsc/04_GSC_INDEXING_URL_INVESTIGATION.csv): Individual URL investigation across all 18 unindexed URLs and indexed URLs.
5. [05_GSC_PERFORMANCE_OPPORTUNITIES.csv](file:///d:/Desktop/AI%20Tools%20Aura/docs/gsc/05_GSC_PERFORMANCE_OPPORTUNITIES.csv): High-impression, low-CTR query and page opportunities.
6. [06_GSC_SHOPPING_STRUCTURED_DATA_REPORT.md](file:///d:/Desktop/AI%20Tools%20Aura/docs/gsc/06_GSC_SHOPPING_STRUCTURED_DATA_REPORT.md): Merchant listings, Product Snippets, and GMC reconciliation.
7. [07_GSC_ROOT_CAUSE_TO_CODE_MAPPING.md](file:///d:/Desktop/AI%20Tools%20Aura/docs/gsc/07_GSC_ROOT_CAUSE_TO_CODE_MAPPING.md): Exact mapping from GSC findings to repository code and files.
8. [08_GSC_VALIDATION_TRACKER.md](file:///d:/Desktop/AI%20Tools%20Aura/docs/gsc/08_GSC_VALIDATION_TRACKER.md): Recrawl request log, IndexNow dispatches, and validation workflows.
9. [09_GSC_CEO_ACTION_PLAN.md](file:///d:/Desktop/AI%20Tools%20Aura/docs/gsc/09_GSC_CEO_ACTION_PLAN.md): Strategic P0–P4 execution roadmap for revenue growth.
10. [10_GSC_EVIDENCE_INDEX.md](file:///d:/Desktop/AI%20Tools%20Aura/docs/gsc/10_GSC_EVIDENCE_INDEX.md): Master evidence index and verification audit trail.

---

## 4. Execution Subagent Reference

- **Subagent Role:** GSC Crawl Stats Deep Auditor
- **Subagent Conversation ID:** `e4317de8-bc27-46c2-a38a-abbfb133d840`
- **Transcript Path:** `C:\Users\pc\.gemini\antigravity\brain\e4317de8-bc27-46c2-a38a-abbfb133d840\.system_generated\logs\transcript.jsonl`
- **Execution Authenticity:** 100% first-party authenticated Chrome browser session against `sc-domain:aitoolgems.tech`. Zero synthetic or simulated metrics.
