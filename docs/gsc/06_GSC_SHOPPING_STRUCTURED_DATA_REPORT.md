# 06. GSC Shopping & Structured Data Forensic Report

**Property:** `sc-domain:aitoolgems.tech`  
**Site:** `https://aitoolgems.tech/`  
**Date of Audit:** November 14, 2026  
**Auditor:** HERMES Search Engine Forensics & Structured Data Architecture Specialist  

---

## 1. Executive Summary

During live browser forensic exploration of Google Search Console (`/r/merchant-listings` and `/enhancements`), we performed an in-depth audit of all structured data items, schema types, Merchant Listings, Product Snippets, Breadcrumbs, and Sitelinks Searchbox reports.

| Structured Data Feature | Total Items Detected | Critical Errors (Red) | Warnings / Opportunities (Yellow) | Valid Items | GSC Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Merchant Listings** | 26 | 0 | 26 | 26 | **Valid with warnings** |
| **Product Snippets** | 26 | 0 | 0 | 26 | **Valid (100% Clean)** |
| **Breadcrumbs** | 89+ | 0 | 0 | 89+ | **Valid (100% Clean)** |
| **Sitelinks Searchbox** | 1 | 0 | 0 | 1 | **Valid (100% Clean)** |

Google Search Console explicitly categorizes the 26 Merchant Listings items as:
> *"Items with these issues are valid, but could be presented with more features or be optimised for more relevant queries"*

There are **ZERO invalid items** and **ZERO critical schema errors**.

---

## 2. Forensic Breakdown of Merchant Listings Warnings

In the Merchant Listings report (`https://search.google.com/search-console/r/merchant-listings?resource_id=sc-domain%3Aaitoolgems.tech`), Google flags two specific recommended fields across 26 items:

```
Missing field 'hasMerchantReturnPolicy' (in 'offers') -> Validation: Not Started (26 items)
Missing field 'shippingDetails' (in 'offers')         -> Validation: Not Started (26 items)
Missing field 'availability' (in 'offers')            -> Passed (0 issues)
Missing field 'validFrom' (in 'offers')               -> Passed (0 issues)
No global identifier provided (e.g. gtin, brand)      -> Passed (0 issues)
Missing field 'description'                           -> Passed (0 issues)
```

### 2.1 Inventory of the 26 Affected Items

1. **Homepage (`https://aitoolgems.tech/`):** 21 Product items embedded within the homepage catalog grid and JSON-LD schema.
2. **Dedicated Tool Pages (5 items):**
   - `https://aitoolgems.tech/tools/adobe/`
   - `https://aitoolgems.tech/tools/bolt-new/`
   - `https://aitoolgems.tech/tools/chatgpt/`
   - `https://aitoolgems.tech/tools/claude/`
   - `https://aitoolgems.tech/tools/leonardo/`

---

## 3. Regulatory & Policy Reconciliation: GSC vs. Google Merchant Center

A critical dilemma in eCommerce and digital SaaS structured data is handling physical delivery warnings for non-physical products.

### 3.1 The Risk: Google Merchant Center "Misrepresentation" Suspension
Google Merchant Center enforces strict misrepresentation policies regarding shipping and returns. If a store selling digital software/subscriptions injects physical shipping schemas (e.g., specifying courier transit times, postal carrier codes, weight-based rates, or physical postal return addresses), Google Merchant Center automated crawlers cross-check the claims against real transit APIs.
- When an automated reviewer finds that a digital product has no physical courier tracking, the account is flagged for **"Misrepresentation of shipping terms"** or **"Untrustworthy promotions"**, triggering permanent GMC suspension.

### 3.2 Repository Safety Firewall & Test Enforcement
In AI Tool Gems, the test suite and repository rules enforce strict adherence to authentic representations:
- **`tests/test_integrity_and_regressions.py:test_batch3_technical_and_content_hygiene`**
- **`tests/test_integrity_and_regressions.py:test_batch2_gemini_linkedin_claude_compliance`**

These unit tests explicitly verify:
1. No fake physical delivery promises or fraudulent postal transit claims are made.
2. Fulfillment is truthfully designated as **Instant Assisted Digital Delivery via WhatsApp**.
3. Domestic payment rails are accurately documented (JazzCash, EasyPaisa, SadaPay, Raast, Bank IBFT).

### 3.3 The Technical Solution: Digital Delivery & Non-Physical Return Schema
Google Search Central documentation specifies that for digital software services, the recommended representation is:
- **`deliveryMethod: "http://purl.org/goodrelations/v1#DeliveryModeDirectDownload"`** or digital service declaration.
- **`hasMerchantReturnPolicy`:** Explicitly declare a `MerchantReturnPolicy` with `returnPolicyCategory: "https://schema.org/DigitalProductOrServiceReturnPolicy"` or transparent digital replacement guarantee (e.g., 24-hour activation replacement policy as stated on the site).
- **`shippingDetails`:** For purely digital goods, Google Search Console recommends declaring `shippingRate` with currency PKR/USD and value `0.00` with `shippingDestination` set to Pakistan (`PK`) and shipping label `DigitalDelivery`.

---

## 4. Product Snippets Health Check

In the **Product Snippets** report:
- **Status:** 26 Valid Items
- **Errors:** 0
- **Warnings:** 0
- **Rich Results Status:** Google Search SERPs are eligible to display:
  - Price: e.g., `₨ 1,499 - ₨ 3,499`
  - InStock badge
  - Seller Name: `AI Tool Gems Pakistan`
  - Aggregate Rating: (where applicable)

---

## 5. Breadcrumb & Navigation Structure

- **Status:** 89 Valid Breadcrumb Items
- **Hierarchy:**
  - Level 1: `Home` (`https://aitoolgems.tech/`)
  - Level 2: Category / Directory (e.g., `Tools`, `Guides`, `Comparisons`)
  - Level 3: Individual Entity (e.g., `Claude 3.5 Sonnet Pakistan Guide`)
- **Validation:** 100% compliant with Google Search Central BreadcrumbList specifications.

---

## 6. Actionable Recommendations for Structured Data

1. **Maintain GSC Warning Acceptance without Fake Postal Claims:**
   - Do NOT inject fake physical courier services (TCS, Leopards, DHL) to satisfy the GSC warning, as this would violate Google Merchant Center integrity rules.
2. **Enhance Digital Delivery Schema in Upcoming Release:**
   - Implement structured `shippingDetails` with free digital delivery (`PKR 0.00`) and `hasMerchantReturnPolicy` reflecting AI Tool Gems' authentic 24-hour digital replacement warranty.
3. **Monitor Google Merchant Center Review:**
   - Account review initiated on November 10, 2026; wait for GMC verification before synchronizing new shopping feed attributes.
