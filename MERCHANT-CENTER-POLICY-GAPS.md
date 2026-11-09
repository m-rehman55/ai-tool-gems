# Google Merchant Center — Comprehensive Policy Gaps & Remediation Matrix

**Document:** `MERCHANT-CENTER-POLICY-GAPS.md`  
**Merchant Center Account:** AI Tool Gems Pakistan (`5877049045`)  
**Target Domain:** `https://aitoolgems.tech/`  
**Audit Date:** 2026-11-10  
**Scope:** Complete Codebase, Website, Feed, Schema, and Policy Gap Analysis  

---

## 1. Overview

This document provides a systematic, itemized register of all policy gaps identified across the AI Tool Gems platform, comparing current repository and live website implementations against official Google Merchant Center, Google Shopping, and Google Ads guidelines.

Each finding is documented with:
- **Evidence & File/Page Location:** Exact repository paths and code snippets.
- **Observed Problem:** Description of the defect or non-compliant practice.
- **Google Policy Involved:** Specific policy citation from Google Merchant Center Help.
- **Severity Classification:** `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW`.
- **Recommended Fix:** Exact technical or operational remediation.
- **Automation Feasibility:** Whether the fix can safely be automated via code.
- **Owner Confirmation Required:** Whether business owner approval is mandatory.

---

## 2. Policy Gap Register

### Gap 1: Missing Physical Operating Address on Contact & Trust Pages
- **Evidence & File/Page:** `contact.html`, `about.html`, `index.html` (footer).
- **Observed Problem:** The website does not provide a physical street address, building name, or city/postal code for the business operations. Only a WhatsApp phone number was displayed.
- **Google Policy Involved:** [Google Merchant Center — Seller Contact Information](https://support.google.com/merchants/answer/6150127) requires a verifiable physical operating address in the merchant's country of registration.
- **Severity:** `CRITICAL`
- **Recommended Fix:** Add a dedicated "Business Location" section to `contact.html` and `about.html` specifying the operating office location in Pakistan (e.g., Karachi, Lahore, or Islamabad) and update the JSON-LD `Organization` schema.
- **Can Be Safely Automated:** Partial (placeholders and schema structure can be added; actual street address must be supplied by the owner).
- **Owner Confirmation Required:** **YES (Mandatory)**

---

### Gap 2: Missing Visible Contact Email Address on Contact Page
- **Evidence & File/Page:** `contact.html` (lines 88–109).
- **Observed Problem:** While `support@aitoolgems.tech` was mentioned in `terms-of-service/index.html`, it was completely omitted from the visible body of `contact.html`.
- **Google Policy Involved:** [Google Merchant Center — Contact Information](https://support.google.com/merchants/answer/6150127) requires at least two direct contact methods (email and phone number) prominently visible to customers.
- **Severity:** `HIGH`
- **Recommended Fix:** Add `support@aitoolgems.tech` as a clickable mailto link in the main contact card of `contact.html` and in the JSON-LD `ContactPage` schema.
- **Can Be Safely Automated:** **YES** (Implemented on branch `feat/merchant-center-compliance`).
- **Owner Confirmation Required:** **NO** (Matches already-published Terms of Service).

---

### Gap 3: Conversational WhatsApp Checkout vs Standard Web Shopping Cart
- **Evidence & File/Page:** `app.js`, `tools/<slug>/index.html`.
- **Observed Problem:** Product pages feature "Order on WhatsApp" links redirecting customers to a chat thread. The site lacks an on-site e-commerce payment gateway or self-service shopping cart.
- **Google Policy Involved:** [Google Merchant Center — Online Checkout Requirements](https://support.google.com/merchants/answer/6150127) requires a straightforward checkout process where customers can add items to a cart and complete payment online.
- **Severity:** `CRITICAL` (for Shopping feeds)
- **Recommended Fix:**
  1. Clearly explain the assisted order and domestic payment process on `policies.html` and landing pages.
  2. Acknowledge that conversational WhatsApp-only checkouts cannot be submitted as automated Google Shopping feeds without high risk of Misrepresentation disapproval.
  3. Re-orient paid acquisition strategy for third-party assisted access toward **Google Ads Search Text Campaigns** (which permits assisted models with transparent disclosures) while reserving Merchant Center feeds for eligible products.
- **Can Be Safely Automated:** **NO** (Involves business model choice).
- **Owner Confirmation Required:** **YES (Mandatory)**

---

### Gap 4: Software Subscriptions Duration Under 12 Months
- **Evidence & File/Page:** `data/wholesale_inventory.json`, 26 tool landing pages (e.g., `tools/chatgpt/index.html`, `tools/claude/index.html`).
- **Observed Problem:** 26 out of 40 assisted software subscriptions have durations of 1 Month, 2 Months, or 3 Months.
- **Google Policy Involved:** [Google Merchant Center — Software Subscriptions Policy](https://support.google.com/merchants/answer/6150127) explicitly prohibits computer software subscriptions with prepaid terms of less than 1 year (12 months).
- **Severity:** `CRITICAL`
- **Recommended Fix:** Maintain all subscriptions with durations $< 12$ months on `HOLD_TERM_INSUFFICIENT` in `merchant_agent/feed_generator.py`. Never submit them to Google Shopping feeds. Keep them available on the website for organic search and direct WhatsApp orders.
- **Can Be Safely Automated:** **YES** (Implemented via feed generator filter `eligible_only=True`).
- **Owner Confirmation Required:** **YES** (Owner must confirm whether annual 12-month packages will be introduced).

---

### Gap 5: Reselling Shared Account Credentials
- **Evidence & File/Page:** `data/wholesale_inventory.json` (tools: `netflix`, `veo`, `semrush`, `surfshark`, `quillbot`, `grammarly`).
- **Observed Problem:** 7 tools offer "Shared" access models where multiple users share login credentials.
- **Google Policy Involved:** [Google Merchant Center — Enabling Dishonest Behavior](https://support.google.com/merchants/answer/6150127) and [Misrepresentation](https://support.google.com/merchants/answer/6150127) prohibit selling access to shared accounts, unauthorized credential pools, or circumventing vendor account limits.
- **Severity:** `CRITICAL`
- **Recommended Fix:** Permanently exclude all shared account offers from Google Merchant Center feeds (`HOLD_POLICY_VIOLATION`). Maintain strict non-affiliation and shared-pool disclosures on the website.
- **Can Be Safely Automated:** **YES** (Enforced in `feed_generator.py` and `validator.py`).
- **Owner Confirmation Required:** **NO** (Mandated by safety policy).

---

### Gap 6: Academic Dishonesty Software (`turnitin`)
- **Evidence & File/Page:** `tools/turnitin/index.html`, `data/wholesale_inventory.json`.
- **Observed Problem:** The catalog lists Turnitin Student Accounts for Rs. 3,600.
- **Google Policy Involved:** [Google Merchant Center & Ads Academic Dishonesty Policy](https://support.google.com/adspolicy/answer/6018045) bans services that promote academic cheating, bypassing plagiarism checks, or selling unauthorized student portal access.
- **Severity:** `CRITICAL` (Account-Level Ban Risk)
- **Recommended Fix:** Permanently blacklist `turnitin` from all Google feeds (`HOLD_POLICY_VIOLATION` in Merchant Center, `HOLD_PROHIBITED` in Google Ads).
- **Can Be Safely Automated:** **YES** (Implemented in `feed_generator.py` and `validator.py`).
- **Owner Confirmation Required:** **NO** (Non-negotiable Google safety mandate).

---

### Gap 7: Third-Party Copyright & Trademark Authorization (Microsoft Keys)
- **Evidence & File/Page:** `tools/windows/index.html`, `tools/office365/index.html`.
- **Observed Problem:** Selling Microsoft Windows 11 Pro Retail Keys and Office 365 accounts without documented Microsoft Authorized Partner Network status.
- **Google Policy Involved:** [Google Merchant Center — Copyrighted & Unauthorized Software](https://support.google.com/merchants/answer/6150127). Microsoft actively enforces brand protection on Google Shopping.
- **Severity:** `HIGH`
- **Recommended Fix:** Place Microsoft products on `HOLD_UNVERIFIED_AUTHORIZATION`. Exclude from Google Shopping feeds until official reseller certification is obtained.
- **Can Be Safely Automated:** **YES** (Enforced in `feed_generator.py`).
- **Owner Confirmation Required:** **YES** (Owner must supply reseller accreditation if available).

---

### Gap 8: Product Logo Dimensions Below $100 \times 100$ Pixels
- **Evidence & File/Page:** `assets/product-logos/` (9 images: `capcut.png`, `chatprd.png`, `firecrawl.png`, `grammarly.png`, `hailuo-ai.png`, `heygen.png`, `linkedin.png`, `n8n.png`, `netflix.png`).
- **Observed Problem:** Image dimensions were $48 \times 48$ or $64 \times 64$ pixels, directly triggering Merchant Center diagnostic *"Image too small"*.
- **Google Policy Involved:** [Google Merchant Center — Product Image Specifications](https://support.google.com/merchants/answer/6324350) requires a minimum of $100 \times 100$ pixels for non-apparel products.
- **Severity:** `MEDIUM`
- **Recommended Fix:** Upscale all 9 images to $256 \times 256$ pixels using high-quality Lanczos resampling with transparency preservation.
- **Can Be Safely Automated:** **YES** (Executed and verified on branch `feat/merchant-center-compliance`).
- **Owner Confirmation Required:** **NO** (Technical compliance improvement).

---

### Gap 9: Return Policy Schema Parity (`ReturnByMail`)
- **Evidence & File/Page:** `tools/<slug>/index.html` (JSON-LD Product schemas).
- **Observed Problem:** Residual schema markup on some pages historically declared physical return methods (`ReturnByMail`) for digital software products.
- **Google Policy Involved:** [Google Merchant Center — Return Policy Requirements](https://support.google.com/merchants/answer/6324484) requires that return policies match the actual delivery method. Digital goods cannot have physical mail returns.
- **Severity:** `HIGH`
- **Recommended Fix:** Ensure all 65 product schemas declare `MerchantReturnPolicy` aligned with digital replacement warranties or non-returnable categories. Added automated test in `merchant_agent/tests/test_merchant_agent.py`.
- **Can Be Safely Automated:** **YES** (Verified across all tools).
- **Owner Confirmation Required:** **NO**.

---

### Gap 10: Multi-Country Target Settings & South Korea Misconfiguration
- **Evidence & File/Page:** Google Merchant Center Account `5877049045` Settings & Feed Settings.
- **Observed Problem:** South Korea (`KR`) was inadvertently added to target countries, triggering missing Korean Business Registration Number, missing KR shipping, and unsupported currency errors.
- **Google Policy Involved:** [Google Merchant Center — Target Country Requirements](https://support.google.com/merchants/answer/160637).
- **Severity:** `HIGH`
- **Recommended Fix:** In the Merchant Center web portal, delete South Korea from Account Target Countries and Feed Settings. Lock targeting strictly to Pakistan (`PK`) with currency `PKR`.
- **Can Be Safely Automated:** **NO** (Requires human administrator login to `merchants.google.com`).
- **Owner Confirmation Required:** **YES (Mandatory)**

---

## 3. Summary Gap Analysis Matrix

| Gap # | Policy Area | Files Affected | Severity | Fix Automated? | Owner Approval? |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **1** | Missing physical address | `contact.html`, `about.html` | `CRITICAL` | Partial | **YES** |
| **2** | Missing visible email | `contact.html` | `HIGH` | **YES** | **NO** |
| **3** | Conversational WhatsApp checkout | `app.js`, tool pages | `CRITICAL` | Disclosed | **YES** |
| **4** | Subscriptions $< 12$ months | 26 product pages, feeds | `CRITICAL` | **YES** (Filtered) | **YES** |
| **5** | Shared account access | 7 product pages, feeds | `CRITICAL` | **YES** (Filtered) | **NO** |
| **6** | Academic cheating (`turnitin`) | `tools/turnitin/index.html` | `CRITICAL` | **YES** (Blocked) | **NO** |
| **7** | Microsoft key authorization | `windows`, `office365` | `HIGH` | **YES** (Held) | **YES** |
| **8** | Sub-100px images | 9 logo files in `assets/` | `MEDIUM` | **YES** (Upscaled) | **NO** |
| **9** | ReturnByMail schema | Tool JSON-LD schemas | `HIGH` | **YES** (Verified) | **NO** |
| **10** | South Korea target configuration | GMC Portal Settings | `HIGH` | Instructions | **YES** |
