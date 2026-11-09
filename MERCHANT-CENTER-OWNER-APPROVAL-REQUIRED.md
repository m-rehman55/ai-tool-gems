# Google Merchant Center — Business Owner Approval & Decision Gate

**Document:** `MERCHANT-CENTER-OWNER-APPROVAL-REQUIRED.md`  
**Merchant Center Account:** AI Tool Gems Pakistan (`5877049045`)  
**Target Domain:** `https://aitoolgems.tech/`  
**Date:** 2026-11-10  
**Status:** `ACTION REQUIRED BY BUSINESS OWNER`  
**Rule:** No changes to live Google account settings, no production deployment, and no Merchant Center review request will be submitted without explicit business owner sign-off.  

---

## 1. Executive Notice to Business Owner

All automated technical audits, code improvements, image upscaling, schema parity repairs, and test suites have been completed on the dedicated branch `feat/merchant-center-compliance`.

To achieve genuine compliance, eliminate the 6 observed Merchant Center diagnostics, and prepare for account re-review, the following **7 strategic business decisions** require your explicit instruction and approval.

---

## 2. Decision Gate Register

### Decision 1: Restrict Google Merchant Center Targeting Strictly to Pakistan
- **Context:**
  South Korea was inadvertently selected as a target country in Google Merchant Center, triggering three diagnostics:
  1. *Missing Korean business registration number* (20 products)
  2. *Missing shipping information in some countries* (20 products)
  3. *Unsupported currency — South Korea listings* (20 products)
- **Recommendation:**
  In the Google Merchant Center web portal (`merchants.google.com`), delete South Korea from Target Countries and primary feed settings. Lock Country of Sale strictly to **Pakistan (`PK`)** with currency **`PKR`**.
- **Consequences of Approval:**
  - Diagnostics #2, #3, and #4 will clear immediately.
  - Merchant Center feeds will evaluate shipping and currency strictly for Pakistani consumers.
  - Website international traffic and USD reference pricing for international SEO remain 100% intact.
- **Owner Action Required:**  
  [ ] **APPROVED:** Authorize restricting Merchant Center targeting exclusively to Pakistan (`PK`).  
  [ ] **REJECTED:** Provide alternate country instructions.

---

### Decision 2: Physical Business Address for Contact Page & Merchant Center
- **Context:**
  Google’s Misrepresentation policy mandates that e-commerce websites display a verifiable physical operating street address where the business conducts operations. The absence of a physical address on `contact.html` is a primary reason for the account-level Misrepresentation disapproval.
- **Recommendation:**
  Select and provide an authentic business operating address in Pakistan (e.g., commercial or shared office address in Karachi, Lahore, or Islamabad) to display on `contact.html`, `about.html`, and in Merchant Center **Settings > Business information**.
- **Owner Action Required:**  
  Please provide the exact address string to be published:  
  *Address Line 1:* __________________________________________________  
  *City & Postal Code:* _______________________________________________  
  *Province / Region:* ________________________________________________  
  *Country:* Pakistan  
  [ ] **APPROVED:** Authorize publication of the above physical address on `contact.html` and in Merchant Center settings.

---

### Decision 3: Feed Catalog Scope vs Software Subscriptions 12-Month Rule
- **Context:**
  Google Merchant Center’s official *Software Subscriptions Policy* explicitly states:
  > *"Subscriptions for computer software can only be submitted to Google Shopping if they are prepaid for a minimum term of at least 1 year (12 months). Monthly software subscriptions are strictly prohibited."*
  26 out of 40 assisted subscriptions in our catalog are 1-month or short-term access passes. Submitting monthly software subscriptions triggers automatic disapproval for Misrepresentation.
- **Options for Business Owner:**
  - **Option A (Recommended):** Maintain all monthly software subscriptions on hold in the feed generator (`eligible_only=True`). Promote monthly subscriptions through organic SEO and Google Search Text Ads (which allows monthly terms with transparent third-party reseller disclosures). Reserve Shopping feeds for eligible annual packages.
  - **Option B:** Introduce genuine 12-month prepaid packages for core tools (e.g., ChatGPT Plus 1-Year, Claude Pro 1-Year, Canva Pro 1-Year) with verified procurement, allowing them to be compliantly submitted to Google Shopping feeds.
- **Owner Action Required:**  
  [ ] **APPROVED (Option A):** Restrict Shopping feeds to eligible items only; maintain monthly subscriptions on policy hold for Shopping feeds.  
  [ ] **APPROVED (Option B):** Plan introduction of 12-month prepaid subscription tiers.

---

### Decision 4: Permanent Exclusion of Shared Accounts & Academic Cheating Aids
- **Context:**
  - 7 tools in the catalog utilize shared accounts (`netflix`, `semrush`, `surfshark`, `veo`, `quillbot-shared`, `grammarly-shared`). Selling shared account access violates Google’s *Enabling Dishonest Behavior* policy.
  - 1 tool (`turnitin`) provides student accounts for plagiarism check bypass, which strictly violates Google’s *Academic Dishonesty Policy*.
- **Recommendation:**
  Permanently block shared accounts and Turnitin from all Google Merchant Center and Google Ads feeds. They will remain documented as `HOLD_POLICY_VIOLATION` in `data/merchant/merchant_hold_register.json`.
- **Owner Action Required:**  
  [ ] **APPROVED:** Confirm permanent exclusion of shared accounts and `turnitin` from all Google feeds.

---

### Decision 5: Microsoft Software Licenses Policy (`windows` & `office365`)
- **Context:**
  The catalog lists Microsoft Windows 11 Pro Retail Keys and Office 365 accounts. Microsoft actively files intellectual property and brand complaints on Google Shopping unless the seller is a certified Microsoft Authorized Partner.
- **Recommendation:**
  Keep Windows and Office 365 on `HOLD_UNVERIFIED_AUTHORIZATION` and exclude them from Google Shopping feeds unless you hold documented Microsoft Partner Network (MPN) reseller certification.
- **Owner Action Required:**  
  [ ] **APPROVED:** Exclude Microsoft keys from Shopping feeds until partner credentials are confirmed.  
  [ ] **HAVE CREDENTIALS:** Business holds official Microsoft Partner Network certificate (provide MPN ID).

---

### Decision 6: Timing & Protocol for Google Merchant Center Review Request
- **Context:**
  Google Merchant Center limits the frequency of account review requests. Requesting a review before all portal settings and website address updates are in place will result in a failed review and an extended account cooldown penalty.
- **Protocol:**
  1. Complete portal updates (remove South Korea, add Pakistan physical address).
  2. Deploy website changes from branch `feat/merchant-center-compliance` to production.
  3. Verify that live website displays updated contact details.
  4. Submit the formal Review Request in Google Merchant Center under **Account Issues > Misrepresentation**.
- **Owner Action Required:**  
  [ ] **APPROVED:** Authorize review submission only after Steps 1–3 are fully verified.

---

### Decision 7: Production Deployment Authorization
- **Context:**
  All technical remediations (upscaled logos, schema `merchantReturnLink` fixes, contact email disclosures, and hardened feed validators) are currently isolated on branch `feat/merchant-center-compliance`.
- **Recommendation:**
  Authorize merging branch `feat/merchant-center-compliance` into `main` and deploying to production via GitHub Pages.
- **Owner Action Required:**  
  [ ] **APPROVED:** Authorize PR creation and merge to `main`.  
  [ ] **HOLD:** Hold deployment pending address finalization.
