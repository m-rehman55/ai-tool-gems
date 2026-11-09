# Google Merchant Center — Country Targeting & Currency Audit

**Document:** `MERCHANT-CENTER-COUNTRY-CURRENCY-AUDIT.md`  
**Merchant Center Account:** AI Tool Gems Pakistan (`5877049045`)  
**Target Domain:** `https://aitoolgems.tech/`  
**Investigation Date:** 2026-11-10  
**Scope:** South Korea Diagnostics (#2, #3, #4) & International Targeting Strategy  
**Primary Commercial Market:** Pakistan (`PK`, `PKR`)  

---

## 1. Executive Summary & Diagnostic Overview

Three of the six observed Merchant Center diagnostics relate directly to **South Korea (`KR`)**:

| Diagnostic Issue | Products Flagged | Severity | Root Cause Mechanism |
| :--- | :--- | :--- | :--- |
| **Missing Korean business registration number** | 20 products | `HIGH` | South Korea was enabled as a target country in Google Merchant Center, triggering mandatory Korean corporate registration checks. |
| **Missing shipping information in some countries** | 20 products | `HIGH` | The feed specified shipping rules only for Pakistan (`PK`). Google flagged South Korea listings for missing shipping costs. |
| **Unsupported currency — South Korea listings** | 20 products | `HIGH` | Product feed prices are in Pakistani Rupees (`PKR`). Google Shopping requires South Korean Won (`KRW`) for Korean listings unless Google Currency Conversion is configured. |

### Key Audit Finding
**South Korea was enabled by mistake during the Google Merchant Center account creation or feed destination setup.**

AI Tool Gems is a Pakistani digital marketplace with domestic payment rails (EasyPaisa, JazzCash, SadaPay, Bank IBFT) and PKR pricing. It has no presence in South Korea, no Korean language support, no Korean business entity, and no domestic Korean payment methods. Targeting South Korea in Google Merchant Center was completely unintentional and has caused three separate disapprovals across all 20 submitted products.

---

## 2. Technical Investigation of the South Korea Mismatch

### 2.1. The 20-Product Correlation
Historical git forensics reveal the exact origin of the "20 products" number:
- In commit `ffd5442f10ecb959c9de5c2f31a33bdaa7d97532` (*"feat(merchant): implement Agent 13 Google Merchant Center"*), the initial `data/merchant/products_feed.xml` was created with **exactly 20 items**:
  `atg-chatgpt`, `atg-veo`, `atg-elevenlabs`, `atg-figma`, `atg-adobe`, `atg-gamma`, `atg-n8n`, `atg-nordvpn`, `atg-youtube`, `atg-linkedin`, `atg-claude`, `atg-cursor`, `atg-deepseek`, `atg-runway`, `atg-grammarly`, `atg-semrush`, `atg-tradingview`, `atg-freepik`, `atg-copilot`, `atg-turnitin`.
- When this 20-product XML feed was uploaded to Merchant Center account `5877049045`, the account settings or feed configuration included South Korea (`KR`) as a target destination.
- Consequently, all 20 products in the feed were evaluated against South Korean merchant standards, resulting in the 3 diagnostics simultaneously across all 20 items.

### 2.2. South Korea Business Registration Number Requirement
- **Legal Context:** South Korea’s *Act on the Consumer Protection in Electronic Commerce* and the *Telecommunications Business Act* mandate that any e-commerce merchant targeting Korean residents must:
  1. Hold a valid Korean Business Registration Number (사업자등록번호) issued by the National Tax Service.
  2. Hold a Mail-Order Sales Registration Certificate (통신판매업신고) issued by the local Korean municipal authority.
  3. Display both registration numbers in the website footer and register them in Google Merchant Center under **Business Information > About your business > South Korea Registration**.
- **Impact on AI Tool Gems:** Because AI Tool Gems is an independent Pakistani sole proprietorship / digital service without a South Korean corporate entity, it is legally and practically impossible to provide a Korean Business Registration Number. Attempting to target South Korea guarantees disapproval.

### 2.3. Shipping Rate Configuration Mismatch
- **Feed Evidence:** The feed items contain:
  ```xml
  <g:shipping>
    <g:country>PK</g:country>
    <g:price>0.00 PKR</g:price>
  </g:shipping>
  ```
- **Error Trigger:** Google Shopping enforces the rule that every country selected as a target destination must have explicit shipping costs defined—either in the feed item via `<g:shipping>` or at the account level under **Shipping & Returns**.
- Because `<g:shipping>` contained rules only for `PK`, and no account-level shipping table was defined for South Korea, Google automatically flagged: *"Missing shipping information in some countries (South Korea) — 20 products"*.

### 2.4. Unsupported Currency (PKR vs KRW)
- **Feed Evidence:** The feed prices are submitted in Pakistani Rupees (e.g., `<g:price>2300.00 PKR</g:price>`).
- **Policy Rule:** Google Shopping requires feed prices to match the official currency of the target country. To list products in South Korea, the merchant must either:
  1. Submit prices directly in South Korean Won (`KRW`), with landing pages displaying KRW; OR
  2. Enable Google Currency Conversion (which automatically translates the feed price into KRW based on live exchange rates).
- Submitting raw PKR prices into a South Korea target profile without currency conversion triggered the *"Unsupported currency — South Korea listings"* error.

---

## 3. Commercial Reality: Can AI Tool Gems Serve South Korea?

An objective e-commerce capability assessment demonstrates that AI Tool Gems cannot compliantly serve the South Korean market:

| Operational Dimension | Reality for AI Tool Gems | Google Shopping Requirement in KR | Verdict |
| :--- | :--- | :--- | :--- |
| **Legal Registration** | Registered / Operating in Pakistan | National Tax Service Business Registration Number | **NON-COMPLIANT** |
| **Payment Gateways** | EasyPaisa, JazzCash, SadaPay, Bank IBFT | Domestic Korean cards, KakaoPay, Toss, Naver Pay | **NON-COMPLIANT** |
| **Language** | English & Urdu | Korean (Hangul) | **NON-COMPLIANT** |
| **Currency** | Pakistani Rupee (PKR) | South Korean Won (KRW) | **NON-COMPLIANT** |
| **Fulfillment** | WhatsApp chat in PKT timezone | Korean localized customer service | **NON-COMPLIANT** |

**Conclusion:** South Korea must be completely removed from Google Merchant Center target destinations.

---

## 4. International SEO vs Merchant Center Targeting

It is critical to distinguish between **organic international SEO** and **Google Merchant Center product feed targeting**:

### 4.1. Organic Website International Presence (Keep Intact)
- The website `aitoolgems.tech` receives international traffic and ranks for global search queries.
- Pages like `prices/index.html` and `deals/index.html` display reference pricing in USD alongside PKR.
- International visitors who contact support via WhatsApp can receive manual consultation and quotes.
- **Rule:** This organic international presence must be preserved. It does not violate Google search policies and drives qualified global traffic.

### 4.2. Merchant Center Shopping Feed Targeting (Restrict to Pakistan)
- Google Shopping / Free Listings feeds require strict adherence to local consumer laws, domestic currencies, and return policies of each target country.
- Attempting to submit products to foreign countries (like South Korea, the United States, or Japan) where domestic payment processing, local business registration, and localized checkouts are absent results in immediate account suspension.
- **Rule:** Google Merchant Center targeting must be strictly locked to **Pakistan (`PK`)** with currency **`PKR`**.

---

## 5. Step-by-Step Merchant Center Reconfiguration Instructions

To resolve Diagnostics #2, #3, and #4 permanently, the business owner must perform the following actions in the Google Merchant Center web portal:

### Step 1: Remove South Korea from Account Target Countries
1. Log in to [Google Merchant Center](https://merchants.google.com/) using the administrator Google account.
2. Ensure Account ID **`5877049045`** (AI Tool Gems Pakistan) is selected.
3. In the left navigation, click on **Settings** (gear icon) > **Account settings** > **Countries of sale**.
4. Check the list of target countries:
   - If **South Korea** (Republic of Korea / KR) is listed, click the trash/remove icon to **delete South Korea**.
   - If any other unintended countries (e.g., Japan, United States, United Kingdom) are listed, **remove them as well**.
   - Ensure **Pakistan (`PK`)** is selected as the **sole Country of Sale**.
5. Click **Save**.

### Step 2: Remove South Korea from Primary Feed Settings
1. In the left navigation, navigate to **Products** > **Feeds**.
2. Click on the primary feed (e.g., `AI Tool Gems Pakistan Product Feed` or `products_feed.xml`).
3. Click on the **Settings** tab.
4. Under **Target countries / Default countries**:
   - Deselect / remove **South Korea**.
   - Set Target Country strictly to **Pakistan**.
   - Set Language to **English**.
5. Under **Destinations**, ensure **Free Listings** is enabled for Pakistan.
6. Click **Save**.

### Step 3: Verify Account Shipping Settings
1. Navigate to **Settings** > **Shipping and returns** > **Shipping**.
2. If any shipping service exists for South Korea, delete it.
3. Ensure a single domestic shipping service exists for **Pakistan**:
   - Service name: `Standard Digital Delivery (Pakistan)`
   - Country: `Pakistan`
   - Currency: `PKR`
   - Delivery time: `Same day / Digital delivery (15–60 minutes)`
   - Shipping rate: `Free shipping (Rs. 0)`
4. Click **Save**.

### Step 4: Confirm Elimination of South Korea Diagnostics
Once South Korea is removed:
- Diagnostic #2 (*Missing Korean business registration number*) will clear immediately.
- Diagnostic #3 (*Missing shipping information in South Korea*) will clear immediately.
- Diagnostic #4 (*Unsupported currency — South Korea listings*) will clear immediately.

This will reduce active Merchant Center diagnostics from 6 down to the core Misrepresentation issue, allowing focused remediation.
