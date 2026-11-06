# Keyword Research and Search Intent Mapping (Phase 4)

**Execution Date:** 6 November 2026  
**Auditor & Specialist:** HERMES Search Intent, GSC Intelligence & Routing Suite  
**Primary Market:** Pakistan (Domestic PKR & verified local payment rails)  
**Growth Market:** International / Global (Tool Comparisons & Cross-Border Inquiry Quotes)  
**Artifact Generated:** [`reports/GSC_Keyword_URL_Map.csv`](file:///d:/Desktop/AI%20Tools%20Aura/reports/GSC_Keyword_URL_Map.csv) (181 mapped queries across 14 dimensions)  

---

## 1. Verified Evidence Sources & Strict Anti-Hallucination Policy

In strict compliance with master instructions (*"Do not make up: Search volume, CPC, Keyword difficulty, Traffic estimates, Conversion rates, Search demand. Mark any unverified keyword values as HYPOTHESIS_ONLY"*):

1. **Google Search Console (Live OAuth API):**
   - Direct empirical data from `https://aitoolgems.tech/` and `sc-domain:aitoolgems.tech`.
   - Verified Impressions, Clicks, CTR, and Average Positions over the trailing 90-day window.
   - Status: **`VERIFIED_GSC`**.
2. **Competitor Gap Intelligence (`aitoolspak.tech`):**
   - High-intent commercial keywords actively targeted by top Pakistani competitor.
   - Zero synthetic search volumes or CPCs assigned; all volume/click fields marked strictly as **`HYPOTHESIS_ONLY`**.
3. **Official Documentation & Technical Knowledge Bases:**
   - Feature definitions, plan tiers, and naming architectures from OpenAI, Google DeepMind, Anthropic, Microsoft, Adobe, and Anysphere.
4. **Customer WhatsApp & On-Site Inquiries:**
   - Real transaction queries targeting Pakistani payment rails (EasyPaisa, JazzCash, SadaPay, NayaPay, Raast).

---

## 2. 8-Way Search Intent Taxonomy & Market Segmentation

Every identified search query is classified through HERMES's multi-dimensional intent engine:

| Search Intent Classification | Description | Sample Queries | Canonical Destination Pattern |
|---|---|---|---|
| **Local Transactional Intent** | Domestic payment rails, currency (PKR), and Pakistani trust queries. | `sadapay`, `easypaisa`, `jazzcash`, `nayapay` | [`/how-we-price.html`](file:///d:/Desktop/AI%20Tools%20Aura/how-we-price.html) & tool checkout modals |
| **Direct Tool Transactional** | High-intent queries seeking to buy or check verified PKR prices. | `chatgpt pro price in pakistan`, `cursor price in pakistan`, `adobe illustrator price in pakistan` | Dedicated tool pages: [`/tools/<slug>/`](file:///d:/Desktop/AI%20Tools%20Aura/tools/) |
| **Tool Comparison Intent** | Evaluating two or more tools before purchasing. | `chatgpt vs gemini price in pakistan`, `canva vs figma comparison pakistan`, `cursor vs copilot` | Dedicated comparison guides: [`/guides/<comparison>-pakistan/`](file:///d:/Desktop/AI%20Tools%20Aura/guides/) |
| **Commercial Investigation** | Broad discovery, alternative searches, and feature research. | `ai tools seller in pakistan`, `ai packages`, `midjourney alternatives` | [`/tools/`](file:///d:/Desktop/AI%20Tools%20Aura/tools/) & [`/deals/`](file:///d:/Desktop/AI%20Tools%20Aura/deals/) |
| **Informational / Question** | Direct questions regarding usage, account types, or setup. | `how to buy chatgpt in pakistan`, `is gemini pro private or shared` | FAQ accordion sections on tool pages & guides |
| **International Growth** | Cross-border inquiries for global workflows and licensing. | `intitle:"leonardo ai" "license key"`, `Canva vs Figma for freelance designers` | Tool pages with international WhatsApp quotes |

---

## 3. Prevention of Keyword Cannibalization & Thin Doorway Pages

> [!IMPORTANT]
> **Anti-Cannibalization Directive:**
> - Never create separate thin URLs for spelling variations, punctuation changes, or closely related queries.
> - Exactly **one canonical destination URL** is assigned to each distinct search-intent cluster.

### Resolved Intent Routing Architecture:

1. **Transactional Tool Intent → Single Canonical Tool Page:**
   - `chatgpt plus subscription price in pakistan`, `buy chatgpt pkr`, `chatgpt easypaisa`, `chatgpt price pakistan`  
     👉 All map exclusively to [`https://aitoolgems.tech/tools/chatgpt/`](file:///d:/Desktop/AI%20Tools%20Aura/tools/chatgpt/).
   - `gemini pro price in pakistan`, `google gemini subscription pakistan`, `buy gemini advanced pkr`  
     👉 All map exclusively to [`https://aitoolgems.tech/tools/gemini/`](file:///d:/Desktop/AI%20Tools%20Aura/tools/gemini/).
   - `cursor price in pakistan`, `cursor ai pro buy pakistan`, `cursor subscription easypaisa`  
     👉 All map exclusively to [`https://aitoolgems.tech/tools/cursor/`](file:///d:/Desktop/AI%20Tools%20Aura/tools/cursor/).

2. **Comparative Intent → Dedicated Comparative Guides (Not Product Pages):**
   - `chatgpt vs gemini price in pakistan`  
     👉 Maps to [`https://aitoolgems.tech/guides/chatgpt-vs-gemini-pakistan/`](file:///d:/Desktop/AI%20Tools%20Aura/guides/chatgpt-vs-gemini-pakistan/) (prevents competing with `/tools/chatgpt/` or `/tools/gemini/`).
   - `canva vs figma feature comparison`  
     👉 Maps to [`https://aitoolgems.tech/guides/canva-vs-figma-pakistan/`](file:///d:/Desktop/AI%20Tools%20Aura/guides/canva-vs-figma-pakistan/) (prevents competing with `/tools/canva/` or `/tools/figma/`).
   - `cursor vs copilot pakistan`  
     👉 Maps to [`https://aitoolgems.tech/guides/cursor-ai-pakistan/`](file:///d:/Desktop/AI%20Tools%20Aura/guides/cursor-ai-pakistan/).

3. **Payment Assurance Intent → Centralized Pricing & Trust Hub:**
   - Queries like `easypaisa`, `jazzcash`, `sadapay`, `nayapay`  
     👉 Map to [`https://aitoolgems.tech/how-we-price.html`](file:///d:/Desktop/AI%20Tools%20Aura/how-we-price.html) and [`/policies.html#payments`](file:///d:/Desktop/AI%20Tools%20Aura/policies.html#payments), preventing diluted tool ranking.

---

## 4. Master Keyword-to-URL Map Summary

The full dataset has been compiled and saved to [`reports/GSC_Keyword_URL_Map.csv`](file:///d:/Desktop/AI%20Tools%20Aura/reports/GSC_Keyword_URL_Map.csv) containing all 14 mandatory columns:
- **Total Mapped Queries:** **181**
- **Canonical Destination URLs:** **27 unique verified routes**
- **Cannibalization Collisions:** **0 collisions**
- **Status Breakdown:**
  * `VERIFIED_GSC`: 173 empirical queries with live GSC performance data.
  * `HYPOTHESIS_ONLY`: 8 high-priority competitor gap targets awaiting empirical verification.

---

## 5. Verification & Ecosystem Test Confirmation

- **Link Graph Integrity:** [`scripts/link_graph_checker.py --strict`](file:///d:/Desktop/AI%20Tools%20Aura/scripts/link_graph_checker.py) confirmed **0 broken links across 99 HTML files**.
- **Automated Regression Suite:** 14 / 14 tests in [`tests/test_integrity_and_regressions.py`](file:///d:/Desktop/AI%20Tools%20Aura/tests/test_integrity_and_regressions.py) passed in 0.257s.
- **Ecosystem Suite:** 284 / 284 tests passed (100% green across all 18 agent systems).
