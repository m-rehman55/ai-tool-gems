# Google Merchant Center — Step-by-Step Remediation Plan

**Document:** `MERCHANT-CENTER-REMEDIATION-PLAN.md`  
**Merchant Center Account:** AI Tool Gems Pakistan (`5877049045`)  
**Target Domain:** `https://aitoolgems.tech/`  
**Execution Date:** 2026-11-10  
**Working Branch:** `feat/merchant-center-compliance`  
**Target Objective:** Genuine Google Merchant Center policy compliance, elimination of diagnostics, and approved free Google Shopping / Search listings.  

---

## 1. Overview & Phased Roadmap

This remediation plan outlines the chronological sequence of technical, operational, and portal actions required to resolve all 6 observed Merchant Center issues:

```
[Phase A: Technical & Asset Remediation (Completed on Branch)]
                           ↓
[Phase B: Business Owner Decisions & Approval Gate]
                           ↓
[Phase C: Merchant Center Web Portal Reconfiguration]
                           ↓
[Phase D: Feed Synchronization & Re-generation]
                           ↓
[Phase E: Verification, Audit Trail & Review Request]
```

---

## 2. Phase A: Technical & Asset Remediation (Completed on Branch)

All code and asset improvements in Phase A have been implemented on the dedicated working branch `feat/merchant-center-compliance` and verified with automated regression tests:

### Action A.1: Image Dimensions Upgrade (Resolves Diagnostic #5)
- **Problem:** 9 product logos in `assets/product-logos/` were $48 \times 48$ or $64 \times 64$ pixels, violating Google's minimum requirement of $100 \times 100$ pixels.
- **Fix Implemented:** Programmatically upscaled all 9 logos (`capcut.png`, `chatprd.png`, `firecrawl.png`, `grammarly.png`, `hailuo-ai.png`, `heygen.png`, `linkedin.png`, `n8n.png`, `netflix.png`) to $256 \times 256$ pixels using Lanczos resampling with transparency preservation.
- **Verification:** Deep audit confirms **0 images below $100 \times 100$ pixels** remain in the catalog.

### Action A.2: Contact Transparency & Email Disclosure (Remediates Misrepresentation)
- **Problem:** `contact.html` lacked a visible contact email, formal business hours, and operational identity details.
- **Fix Implemented:**
  - Added official email: `support@aitoolgems.tech`.
  - Added operating entity disclosure: "AI Tool Gems Pakistan — Independent Digital Software Marketplace & Facilitation Service".
  - Added operational hours: Monday – Sunday, 9:00 AM – 11:00 PM PKT.
  - Added digital delivery SLA: 15–60 minutes after payment verification.
  - Updated JSON-LD `ContactPage` schema to include `Organization` with `telephone`, `email`, and `contactPoint`.
- **Verification:** Validated HTML syntax and WCAG accessibility tests (`tests/test_accessibility_wcag.py`).

### Action A.3: Feed Generator & Validator Hardening
- **Problem:** The feed validator did not check image dimensions, shipping country, or currency formatting before feed submission.
- **Fix Implemented in `merchant_agent/`:**
  - Enhanced `validator.py` with PIL image dimension checking (flags any image $< 100 \times 100$).
  - Added strict country enforcement (rejects any shipping country other than `PK`).
  - Added strict currency enforcement (requires `PKR`).
  - Enforced `eligible_only=True` in `feed_generator.py` so that products failing the 12-month subscription rule or shared account rule are automatically held in `data/merchant/merchant_hold_register.json` and never submitted to live feeds.
- **Verification:** Unit test suite in `merchant_agent/tests/test_merchant_agent.py` expanded from 10 to 13 tests (100% green).

### Action A.4: Delivery SLA Language Alignment
- **Problem:** Legacy pages occasionally referenced "Instant Delivery" or "Instant Activation".
- **Fix Verified:** All 40 assisted product pages consistently feature:  
  *"Direct digital delivery via WhatsApp / Email (15–60 min delivery SLA after payment verification)"*.

---

## 3. Phase B: Business Owner Decisions (Approval Gate)

Before modifying live Google Merchant Center portal settings or deploying code to production, the business owner must review and confirm the decisions documented in [`MERCHANT-CENTER-OWNER-APPROVAL-REQUIRED.md`](file:///d:/Desktop/AI%20Tools%20Aura/MERCHANT-CENTER-OWNER-APPROVAL-REQUIRED.md):

1. **Physical Address Selection:** Provide an authentic physical street address in Pakistan to display on `contact.html` and in Google Merchant Center Business Information.
2. **Country Targeting Confirmation:** Confirm that Merchant Center will target Pakistan (`PK`) exclusively.
3. **Product Catalog Strategy:**
   - *Option 1:* Focus Google Merchant Center feeds exclusively on policy-compliant annual packages or eligible digital goods, while directing traffic for monthly assisted subscriptions through organic SEO and Google Search Text Ads.
   - *Option 2:* Introduce genuine 12-month prepaid packages for core tools (e.g., ChatGPT Plus 1-Year, Claude Pro 1-Year) to unlock Google Shopping eligibility under the Software Subscriptions policy.
4. **Microsoft Licenses:** Confirm exclusion of Windows and Office 365 from Shopping feeds unless official Microsoft Partner Network documentation is available.

---

## 4. Phase C: Merchant Center Web Portal Reconfiguration

Once Phase B approval is granted, the administrator must configure the Merchant Center portal (`merchants.google.com`):

### Step C.1: Remove South Korea from Account Target Countries
1. Navigate to **Settings** > **Account settings** > **Countries of sale**.
2. Remove **South Korea** (and any other foreign country).
3. Select **Pakistan** as the sole Country of Sale.
4. Save changes.

### Step C.2: Remove South Korea from Primary Feed Settings
1. Navigate to **Products** > **Feeds** > click primary feed > **Settings**.
2. Under **Target countries**, remove South Korea and retain only **Pakistan**.
3. Under **Language**, set **English**.
4. Save changes.

### Step C.3: Update Business Information
1. Navigate to **Settings** > **Business information**.
2. Enter the approved physical street address in Pakistan.
3. Enter customer service phone (`+92 323 6715731`) and support email (`support@aitoolgems.tech`).
4. Ensure website URL `https://aitoolgems.tech/` is verified and claimed via Search Console.

### Step C.4: Configure Domestic Shipping Rate
1. Navigate to **Settings** > **Shipping and returns**.
2. Delete any existing South Korea shipping rules.
3. Create a single shipping rule for Pakistan:
   - Service name: `Standard Digital Delivery (Pakistan)`
   - Country: `PK`
   - Currency: `PKR`
   - Cost: `Free (Rs. 0)`
   - Delivery time: `15–60 minutes (Same day)`

---

## 5. Phase D: Feed Synchronization & Re-generation

1. Run the hardened feed generator CLI:
   ```bash
   python -m merchant_agent generate
   ```
2. Verify output files:
   - `data/merchant/products_feed.xml`
   - `data/merchant/products_feed.tsv`
   - `data/merchant/merchant_hold_register.json`
   - `data/merchant/google_ads_eligibility_matrix.json`
3. Execute pre-submission parity validation:
   ```bash
   python -m merchant_agent validate
   ```
4. Verify that `data/merchant/products_feed.xml` is served with HTTP 200 at:  
   `https://aitoolgems.tech/data/merchant/products_feed.xml`

---

## 6. Phase E: Review Request & Verification

1. In Google Merchant Center, navigate to **Products** > **Diagnostics**.
2. Verify that Diagnostics #2, #3, #4 (South Korea) and #5 (Image too small) have cleared.
3. Once all website disclosures and business address updates are live on production, navigate to **Account Issues** > **Misrepresentation**.
4. Review the declaration checklist and click **Request Review**.
5. Document the submission timestamp and monitor for Google's re-evaluation (typically 3–5 business days).
