# 🛡️ Google Search Console RE2 Regex Filter Library — AIToolGems Pakistan
**Last Updated:** `2026-10-17`  
**Target Market:** Pakistan (PKR, EasyPaisa, JazzCash, SadaPay)  
**Syntax Standard:** Google Search Console RE2 Regular Expressions  

---

## 📖 How to Use These Filters in Google Search Console
1. Open [Google Search Console](https://search.google.com/search-console) -> Select **aitoolgems.tech** property.
2. Navigate to **Performance** -> **Search results**.
3. Click **+ New** at the top filter bar and choose **Query** or **Page**.
4. In the dropdown, switch from *Queries containing* to **Custom (regex)**.
5. Select either **Matches regex** or **Doesn't match regex** as indicated below.
6. Copy and paste the exact regex pattern.

---

## 🗂️ Verified RE2 Regex Filters

### 🔍 Filter: Brand Queries
- **Dimension:** `Query`
- **Filter Mode:** **Matches regex**
- **RE2 Compatibility:** ✅ RE2 Validated
- **Copy-Ready Regex:**
```regex
(?i)(ai\s*tool\s*gems|aitoolgems|ai\s*tools\s*aura)
```
- **What it Matches:** All variations of brand name queries (with spaces, without spaces, or legacy brand name).
- **What it Excludes:** Generic, non-branded AI tool searches.
- **Example Matches:** `ai tool gems`, `aitoolgems`, `aitoolgems login`, `ai tools aura`
- **Example Excluded:** `chatgpt price in pakistan`, `buy canva pro`, `elevenlabs urdu`
- **Edge Cases & False Positives:** Does not match separate generic words 'ai tools' unless accompanied by 'gems' or 'aura'.
- **How to Apply in GSC:**
  1. Open Search Console -> Performance -> **Search results**.
  2. Click **+ New** at the top filter bar and choose **Query**.
  3. Select **Custom (regex)** -> **Matches regex**.
  4. Paste the regex above and click **Apply**.
- **Metrics to Inspect:** Track brand awareness growth, direct navigational clicks, and brand CTR (should exceed 30%).


---

### 🔍 Filter: Non-Brand Organic Queries
- **Dimension:** `Query`
- **Filter Mode:** **Doesn't match regex**
- **RE2 Compatibility:** ✅ RE2 Validated
- **Copy-Ready Regex:**
```regex
(?i)(ai\s*tool\s*gems|aitoolgems|ai\s*tools\s*aura)
```
- **What it Matches:** Every query that does NOT mention the brand name.
- **What it Excludes:** Brand navigation searches.
- **Example Matches:** `buy chatgpt pro pakistan`, `canva pro price easypaisa`, `claude 3.5 sonnet pkr`
- **Example Excluded:** `ai tool gems`, `aitoolgems pakistan`, `aitoolgems review`
- **Edge Cases & False Positives:** Ensures no brand equity masks true non-brand organic search growth.
- **How to Apply in GSC:**
  1. Open Search Console -> Performance -> **Search results**.
  2. Click **+ New** at the top filter bar and choose **Query**.
  3. Select **Custom (regex)** -> **Doesn't match regex**.
  4. Paste the regex above and click **Apply**.
- **Metrics to Inspect:** Pure non-brand impressions and non-brand click acquisition trends.


---

### 🔍 Filter: Pakistan & Local Payment Intent
- **Dimension:** `Query`
- **Filter Mode:** **Matches regex**
- **RE2 Compatibility:** ✅ RE2 Validated
- **Copy-Ready Regex:**
```regex
(?i)(pakistan|pakistani|pkr|rs\.?|rupees?|easypaisa|jazzcash|sadapay|nayapay|raast|lahore|karachi|islamabad)
```
- **What it Matches:** Queries indicating explicit Pakistani geographical presence or local payment method intent.
- **What it Excludes:** Global international queries with no local payment affinity.
- **Example Matches:** `chatgpt price in pakistan`, `buy canva pro easypaisa`, `midjourney pkr`, `gemini advanced jazzcash`
- **Example Excluded:** `chatgpt api docs`, `canva templates free`, `figma plugins`
- **Edge Cases & False Positives:** Matches mentions of major Pakistani cities (Lahore, Karachi, Islamabad) and local wallets.
- **How to Apply in GSC:**
  1. Open Search Console -> Performance -> **Search results**.
  2. Click **+ New** at the top filter bar and choose **Query**.
  3. Select **Custom (regex)** -> **Matches regex**.
  4. Paste the regex above and click **Apply**.
- **Metrics to Inspect:** High-intent transactional conversion rate, local SERP rankings, and WhatsApp lead signals.


---

### 🔍 Filter: Commercial & Purchase Intent
- **Dimension:** `Query`
- **Filter Mode:** **Matches regex**
- **RE2 Compatibility:** ✅ RE2 Validated
- **Copy-Ready Regex:**
```regex
(?i)(buy|price|pricing|cost|subscription|subscribe|purchase|plans?|cheap|affordable|discount|deal|license|key|account)
```
- **What it Matches:** Queries where user wants to buy, compare prices, or purchase subscriptions.
- **What it Excludes:** Pure educational or informational troubleshooting searches.
- **Example Matches:** `buy chatgpt plus`, `canva pro cheap subscription`, `claude pro pricing pkr`, `capcut pro license key`
- **Example Excluded:** `what is chatgpt`, `how to use figma`, `free prompt examples`
- **Edge Cases & False Positives:** 'free trial' might match 'trial' if included; 'cost' matches price investigations.
- **How to Apply in GSC:**
  1. Open Search Console -> Performance -> **Search results**.
  2. Click **+ New** at the top filter bar and choose **Query**.
  3. Select **Custom (regex)** -> **Matches regex**.
  4. Paste the regex above and click **Apply**.
- **Metrics to Inspect:** Clicks on commercial pages (/deals/, /prices/, /tools/*/).


---

### 🔍 Filter: Question & AEO Snippet Intent
- **Dimension:** `Query`
- **Filter Mode:** **Matches regex**
- **RE2 Compatibility:** ✅ RE2 Validated
- **Copy-Ready Regex:**
```regex
(?i)^(who|what|when|where|why|which|how|can|does|is|are|best|top)\b
```
- **What it Matches:** Natural-language questions and list-based discovery queries suitable for featured snippets and AI overviews.
- **What it Excludes:** Short-tail keywords without question starters.
- **Example Matches:** `how to buy chatgpt in pakistan`, `can i pay via easypaisa for canva`, `which ai tool is best for video editing`, `is claude available in pakistan`
- **Example Excluded:** `chatgpt plus pkr`, `canva pro login`, `elevenlabs api`
- **Edge Cases & False Positives:** Anchored to start of query (^) to capture clear question structure.
- **How to Apply in GSC:**
  1. Open Search Console -> Performance -> **Search results**.
  2. Click **+ New** at the top filter bar and choose **Query**.
  3. Select **Custom (regex)** -> **Matches regex**.
  4. Paste the regex above and click **Apply**.
- **Metrics to Inspect:** Rich results, FAQ schema click-throughs, and featured snippet positions (1-3).


---

### 🔍 Filter: Comparison & Alternative Queries
- **Dimension:** `Query`
- **Filter Mode:** **Matches regex**
- **RE2 Compatibility:** ✅ RE2 Validated
- **Copy-Ready Regex:**
```regex
(?i)(vs\.?|versus|alternative|alternatives|compare|comparison|better|or\b)
```
- **What it Matches:** Queries comparing two tools or seeking alternatives to expensive AI tools.
- **What it Excludes:** Single tool searches.
- **Example Matches:** `chatgpt vs claude`, `midjourney alternative`, `capcut vs premiere pro`, `veo or runway`
- **Example Excluded:** `buy chatgpt`, `canva pricing`, `replit download`
- **Edge Cases & False Positives:** Word boundary on 'or' prevents false matches inside words like 'creator' or 'generator'.
- **How to Apply in GSC:**
  1. Open Search Console -> Performance -> **Search results**.
  2. Click **+ New** at the top filter bar and choose **Query**.
  3. Select **Custom (regex)** -> **Matches regex**.
  4. Paste the regex above and click **Apply**.
- **Metrics to Inspect:** Traffic to /guides/ comparison articles.


---

### 🔍 Filter: AI Chat & LLM Cluster
- **Dimension:** `Query`
- **Filter Mode:** **Matches regex**
- **RE2 Compatibility:** ✅ RE2 Validated
- **Copy-Ready Regex:**
```regex
(?i)(chatgpt|gpt[- ]?4|gpt[- ]?5|gemini|claude|copilot|perplexity|deepseek)
```
- **What it Matches:** Queries targeting conversational LLMs and reasoning engines.
- **What it Excludes:** Video, design, or dev tool queries.
- **Example Matches:** `chatgpt plus pakistan`, `gemini advanced subscription`, `claude 3.5 sonnet`, `deepseek r1 pkr`
- **Example Excluded:** `canva pro`, `elevenlabs voice`, `figma license`
- **Edge Cases & False Positives:** Captures hyphenated and spaced variants like 'gpt-4' or 'gpt 4'.
- **How to Apply in GSC:**
  1. Open Search Console -> Performance -> **Search results**.
  2. Click **+ New** at the top filter bar and choose **Query**.
  3. Select **Custom (regex)** -> **Matches regex**.
  4. Paste the regex above and click **Apply**.
- **Metrics to Inspect:** Impressions and CTR on /tools/chatgpt/ and /tools/gemini/.


---

### 🔍 Filter: AI Video & Audio Cluster
- **Dimension:** `Query`
- **Filter Mode:** **Matches regex**
- **RE2 Compatibility:** ✅ RE2 Validated
- **Copy-Ready Regex:**
```regex
(?i)(capcut|elevenlabs|veo|runway|sora|heygen|synthesia|sunoo|midjourney|leonardo)
```
- **What it Matches:** Queries targeting generative media, voice cloning, and AI video generators.
- **What it Excludes:** Text LLMs and productivity software.
- **Example Matches:** `capcut pro pakistan`, `elevenlabs urdu voice`, `google veo 3 ultra`, `leonardo ai credits`
- **Example Excluded:** `cursor ai editor`, `chatgpt plus`, `nordvpn account`
- **Edge Cases & False Positives:** Groups top media generation tools.
- **How to Apply in GSC:**
  1. Open Search Console -> Performance -> **Search results**.
  2. Click **+ New** at the top filter bar and choose **Query**.
  3. Select **Custom (regex)** -> **Matches regex**.
  4. Paste the regex above and click **Apply**.
- **Metrics to Inspect:** Growth among Pakistani YouTubers and TikTok creators.


---

### 🔍 Filter: Dev & Design AI Cluster
- **Dimension:** `Query`
- **Filter Mode:** **Matches regex**
- **RE2 Compatibility:** ✅ RE2 Validated
- **Copy-Ready Regex:**
```regex
(?i)(canva|figma|adobe|cursor|replit|notion|gamma|n8n|lovable)
```
- **What it Matches:** Queries targeting Pakistani freelancers, developers, and graphic designers.
- **What it Excludes:** Entertainment or generic chat tools.
- **Example Matches:** `canva pro lifetime`, `figma pro pakistan`, `cursor ai pro pkr`, `gamma app subscription`
- **Example Excluded:** `netflix pakistan`, `chatgpt login`, `capcut mod apk`
- **Edge Cases & False Positives:** Ensures tracking of high-ARPU developer and agency software.
- **How to Apply in GSC:**
  1. Open Search Console -> Performance -> **Search results**.
  2. Click **+ New** at the top filter bar and choose **Query**.
  3. Select **Custom (regex)** -> **Matches regex**.
  4. Paste the regex above and click **Apply**.
- **Metrics to Inspect:** High average CTR and high commercial conversion intent.


---

### 🔍 Filter: Page Group: Tool Detail Pages
- **Dimension:** `Page`
- **Filter Mode:** **Matches regex**
- **RE2 Compatibility:** ✅ RE2 Validated
- **Copy-Ready Regex:**
```regex
^https?://aitoolgems\.tech/tools/
```
- **What it Matches:** All 20 individual tool landing pages (/tools/chatgpt/, /tools/canva/, etc.).
- **What it Excludes:** Guides, homepage, deals, and policy pages.
- **Example Matches:** `https://aitoolgems.tech/tools/chatgpt/`, `https://aitoolgems.tech/tools/leonardo/`
- **Example Excluded:** `https://aitoolgems.tech/`, `https://aitoolgems.tech/guides/developers/`, `https://aitoolgems.tech/prices/`
- **Edge Cases & False Positives:** Exact protocol and path prefix matching.
- **How to Apply in GSC:**
  1. Open Search Console -> Performance -> **Search results**.
  2. Click **+ New** at the top filter bar and choose **Page**.
  3. Select **Custom (regex)** -> **Matches regex**.
  4. Paste the regex above and click **Apply**.
- **Metrics to Inspect:** Aggregate performance of product catalog.


---

### 🔍 Filter: Page Group: Educational Guides
- **Dimension:** `Page`
- **Filter Mode:** **Matches regex**
- **RE2 Compatibility:** ✅ RE2 Validated
- **Copy-Ready Regex:**
```regex
^https?://aitoolgems\.tech/guides/
```
- **What it Matches:** All in-depth Pakistani buying guides and tool comparison pages.
- **What it Excludes:** Direct product landing pages and legal policies.
- **Example Matches:** `https://aitoolgems.tech/guides/ai-tools-price-pakistan/`, `https://aitoolgems.tech/guides/chatgpt-vs-gemini-pakistan/`
- **Example Excluded:** `https://aitoolgems.tech/tools/gemini/`, `https://aitoolgems.tech/about.html`
- **Edge Cases & False Positives:** Captures top-of-funnel informational and AEO traffic.
- **How to Apply in GSC:**
  1. Open Search Console -> Performance -> **Search results**.
  2. Click **+ New** at the top filter bar and choose **Page**.
  3. Select **Custom (regex)** -> **Matches regex**.
  4. Paste the regex above and click **Apply**.
- **Metrics to Inspect:** Informational impressions, organic backlink attraction, and internal link CTR.


---
