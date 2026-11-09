# Google Merchant Center — Independent Verification & Claim Challenge Report

**Audit Target:** Feat branch `feat/merchant-center-compliance`, Commit `2133f0f`  
**Role:** Independent Google Merchant Center Compliance Reviewer & External Auditor  
**Mandate:** Challenge prior audit conclusions, verify business facts against objective evidence, test policy claims against verbatim Google documentation, and evaluate production readiness.  
**Mode:** Strictly Read-Only (Zero file mutations, zero deployments, zero API calls).  
**Date:** 2026-11-10  
**Overall Verdict:** **`NEEDS CORRECTION & NOT READY FOR DEPLOYMENT`**  

---

## 1. Executive Summary & Verification Verdict

An independent, critical review was performed to audit every claim made in `MERCHANT-CENTER-MISREPRESENTATION-ROOT-CAUSE.md`, inspect modified repository files against baseline git history, verify DNS infrastructure, and evaluate structured data and image assets against verbatim Google Merchant Center policies.

### Core Discoveries of the Independent Challenge
1. **Critical Email Failure (`support@aitoolgems.tech` is Non-Functional):** DNS query inspection proves `aitoolgems.tech` has **zero active MX records**. The published support email is currently non-functional text. Any verification email sent by Google reviewers or customers will bounce, guaranteeing immediate Misrepresentation rejection.
2. **Logo vs. Product Image Policy Conflict:** While upscaling 9 logos to $256 \times 256$ px satisfied the raw dimension requirement ($> 100 \times 100$ px), **Google Merchant Center Help Article 6324350 explicitly prohibits using standalone brand logos or placeholder icons as product images**. Technical resolution does not equate to policy approval.
3. **South Korea Target Origin is Inferred, Not Proven in Code:** There is zero mention of South Korea in repository files. The presence of South Korea in Merchant Center was inferred entirely from diagnostic text, not directly observed via API. Furthermore, deleting South Korea will clear the 3 Korean sub-errors, but will **not** restore the account, as all products remain blocked by Misrepresentation.
4. **Policy Overstatements Corrected:** The prior audit generalized several policies. Specifically:
   - Google Merchant Center does not explicitly mandate a physical street address on the website if other verified contact methods are present, though it is mandatory in Merchant Center Account Settings.
   - The 12-month software subscription rule applies to the `price` attribute in Merchant Center feeds (Shopping Ads and Free Listings), but does not apply to Google Ads Search Text Ads or non-subscription perpetual licenses.
   - "Enabling Dishonest Behavior" is a Google Ads policy heading, enforced under "Misrepresentation / Unacceptable Business Practices" in Merchant Center.
   - Turnitin is not explicitly named in Google policies; it is banned under academic cheating aids if framed as a plagiarism filter bypass.

---

## 2. Recheck of Major Policy Conclusions (Challenging Claims A through F)

| Claim Challenged | Prior Audit Claim | Verbatim Google Policy Finding & Exact Citation | Scope (Shopping vs. Free vs. Ads) | Finding Classification & Confidence |
| :--- | :--- | :--- | :--- | :--- |
| **Claim A: Physical Street Address** | "Physical street address is mandatory on the website to clear Misrepresentation." | **[Article 6363310 (Website Requirements)](https://support.google.com/merchants/answer/6363310):** *"Ensure users can find accurate contact information on your website. Examples include a telephone number, email address, physical address, and social media accounts."* The policy requires accessible contact methods (at least phone, email, contact form, or address). However, in Merchant Center account settings under **Business Information**, an address is mandatory. During manual reviews, human auditors routinely look for address parity. | Both Shopping & Free Listings. | **CORRECTED**  <br>*(Confidence: HIGH)*  <br>An address is mandatory in GMC account settings, and strongly expected in manual reviews, but Google's website guideline accepts combinations of phone + email + form. Stating it is a hard website requirement is an operational reality, not verbatim policy text. |
| **Claim B: WhatsApp Assisted Checkout** | "WhatsApp-assisted checkout without an automated cart automatically violates Google policy." | **[Article 6363310 (Checkout Requirements)](https://support.google.com/merchants/answer/6363310):** *"Allow everyone to check out... Keep account creation barrier-free: registration must not force extra barriers like downloading an app or changing devices."* Forcing users to download or open WhatsApp to complete a transaction violates Google Shopping's self-service online checkout mandate. | Applies strictly to **Google Shopping Feeds** (Free Listings & Shopping Ads). Does **NOT** apply to **Google Ads Search Text Ads**. | **CONFIRMED FOR SHOPPING; CORRECTED FOR ADS**  <br>*(Confidence: HIGH)*  <br>Conversational checkout is prohibited for Merchant Center feeds, but fully permissible for Google Search Text campaigns with transparent third-party disclosures. |
| **Claim C: Shared Software Accounts** | "Shared software accounts automatically violate Enabling Dishonest Behavior." | **[Google Ads Enabling Dishonest Behavior Policy](https://support.google.com/adspolicy/answer/6023648):** Bans *"Products or services that enable unauthorized access to systems, devices, or accounts."* In Merchant Center, this is enforced under **[Misrepresentation (Unacceptable Business Practices)](https://support.google.com/merchants/answer/6150127)**. Selling credentials that circumvent third-party vendor single-user license limits is prohibited. | Both Shopping & Free Listings, plus Google Ads. | **CONFIRMED SUBSTANTIVELY; CORRECTED CLASSIFICATION**  <br>*(Confidence: HIGH)*  <br>Selling shared credentials violates Google rules, but the governing Merchant Center policy is *Misrepresentation / Unacceptable Business Practices*, not the standalone Google Ads policy heading. |
| **Claim D: Subscriptions Under 12 Months** | "All subscriptions shorter than 12 months are prohibited in every Merchant Center marketing method." | **[Article 6324371 (Price Attribute Specification)](https://support.google.com/merchants/answer/6324371):** *"Software subscriptions: Submit the price for the full length of the software subscription, with a minimum of 1 year (12 months)."* This applies to computer software submitted via the `price` attribute. It does not apply to physical goods (which use `subscription_cost`) or perpetual non-subscription licenses. | Applies to **Merchant Center Software Feeds** (Shopping Ads & Free Listings). Does **NOT** apply to Google Ads Search Text Ads. | **CORRECTED**  <br>*(Confidence: HIGH)*  <br>The 12-month rule is verified for software subscription feeds in Merchant Center, but the claim that it applies to "every marketing method" is false; Google Search Text Ads can advertise monthly SaaS subscriptions. |
| **Claim E: Microsoft License Keys** | "Microsoft license keys require Microsoft Authorized Partner proof in every case." | **[Google Merchant Center Copyrights Policy](https://support.google.com/merchants/answer/6150127):** Prohibits unauthorized distribution of copyrighted software. While Microsoft aggressively files trademark/counterfeit complaints against unauthorized OEM product key resellers, Google's policy does not state "Microsoft Authorized Partner proof is required in every case." Rather, unverified supply chains trigger Counterfeit/Copyright disapprovals. | Both Shopping & Free Listings. | **UNSUPPORTED AS A VERBATIM RULE; CONFIRMED AS PRACTICAL ENFORCEMENT**  <br>*(Confidence: MEDIUM)*  <br>Partner status is not a codified prerequisite in Google documentation, but practically necessary to survive Microsoft IP takedowns and Google supply-chain audits. |
| **Claim F: Turnitin Prohibition** | "Turnitin is automatically prohibited under a specific Google Shopping policy." | **[Products that Enable Dishonest Behavior](https://support.google.com/merchants/answer/6150127):** Bans *"Products that enable academic dishonesty, like custom or pre-written essays."* Turnitin itself is an enterprise academic integrity tool. However, third-party reselling of individual "Student Accounts" to allow students to pre-check essays and bypass institutional detection is interpreted as enabling academic dishonesty. | Both Shopping & Free Listings. | **CORRECTED**  <br>*(Confidence: HIGH)*  <br>Google has no policy naming "Turnitin." The prohibition is context-dependent: reselling student accounts to evade plagiarism filters violates the academic dishonesty clause. |

---

## 3. Verification of Actual Business Facts

### 3.1. Business Support Email (`support@aitoolgems.tech`) — CRITICAL DEFECT
- **Audit Assertion:** Prior audit added `support@aitoolgems.tech` to `contact.html` and structured data.
- **Independent Verification Check:**
  - Ran DNS MX record lookup via authoritative nameservers (`ns1.name.com`):
    ```
    Resolve-DnsName -Name aitoolgems.tech -Type MX
    Query result: Section: Authority (SOA record only, NO MX RECORDS RETURNED)
    ```
  - Ran port 25 connectivity tests: IP resolves to GitHub Pages CDN (`185.199.108.153`), which does not provide mail exchange services.
- **Finding:** **`support@aitoolgems.tech` is currently non-functional text.** Emails sent to this address will bounce immediately. Submitting this email to Google Merchant Center will trigger an instant Misrepresentation rejection upon automated or human email ping.
- **Required Action:** The business owner must configure DNS MX records (via Google Workspace, Zoho, or Name.com mail forwarding) OR publish an existing operational contact email before deployment.
- **Confidence:** `HIGH`

### 3.2. Delivery SLA (15–60 Minute Window)
- **Audit Assertion:** Published SLA is "15–60 minutes after payment verification."
- **Independent Verification Check:**
  - Git history shows earlier versions claimed "Instant Delivery" (commit `14fcc70`) or "within 1–2 hours" (commit `67d6e2a`).
  - Commit `114203e` purged delivery minute claims from SEO pages.
  - On `policies.html`, the business explicitly states: *"Delivery starts after payment is confirmed. The estimate on each listing is not a guaranteed deadline because product availability and third-party activation systems can change."*
  - Operations occur between 9:00 AM and 11:00 PM PKT. Orders placed outside these hours cannot be delivered within 60 minutes.
- **Finding:** The 15–60 minute window is an **operational target during business hours**, not an absolute SLA. Wording should clarify: *"Typically delivered within 15–60 minutes during operating hours (9 AM – 11 PM PKT) following payment verification."*
- **Confidence:** `HIGH`

### 3.3. Physical Business Address
- **Audit Assertion:** Address was not invented; remains undisclosed pending owner instruction.
- **Independent Verification Check:** Programmatic scan across all 112 repository files confirmed **zero occurrences of invented street addresses, fake office suites, or phantom postal codes**.
- **Finding:** Factually confirmed. The repository truthfully avoids fabricating an address.
- **Confidence:** `HIGH`

### 3.4. Reseller Disclosures & Brand Affiliation
- **Audit Assertion:** Independent marketplace status is clearly disclosed; no official affiliation is claimed.
- **Independent Verification Check:**
  - Inspected `about.html`, `policies.html`, `terms-of-service/index.html`, and `tools/<slug>/index.html`.
  - Every page features prominent non-affiliation disclaimers:  
    *"AI Tool Gems is an independent digital service facilitator. We are not an official reseller, authorized distributor, partner, or sponsor of OpenAI, Google, Anthropic, Midjourney, Canva, Adobe, Cursor, Perplexity, ElevenLabs, GitHub, or any other third-party software manufacturer unless explicitly stated."*
  - Secondary buttons on tool pages link directly to the official vendor websites (`openai.com`, `anthropic.com`, etc.).
- **Finding:** Factually confirmed. The site makes no false claims of authorization.
- **Confidence:** `HIGH`

---

## 4. Verification of Image Changes & Image Policy Challenge

### 4.1. Technical Image Verification (9 Modified Logos)
Programmatic analysis of the upscaled files in `assets/product-logos/` revealed:

| File Name | Original Size | Upscaled Size | Mode | Alpha Channel | Transparency % | Visual Inspection Result |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `capcut.png` | $64 \times 64$ | $256 \times 256$ | RGBA | Present | 2.30% | Edges slightly softened; visually recognizable. |
| `chatprd.png` | $48 \times 48$ | $256 \times 256$ | RGBA | Present | 0.00% | Slight interpolation blur; SVG exists in repo. |
| `firecrawl.png` | $48 \times 48$ | $256 \times 256$ | RGBA | Present | 0.00% | Softened raster; SVG exists in repo. |
| `grammarly.png` | $48 \times 48$ | $256 \times 256$ | RGBA | Present | 9.94% | Clean icon outline; recognizable. |
| `hailuo-ai.png` | $64 \times 64$ | $256 \times 256$ | RGBA | Present | 3.06% | Softened corners; SVG exists in repo. |
| `heygen.png` | $48 \times 48$ | $256 \times 256$ | RGBA | Present | 30.28% | Clean circular icon. |
| `linkedin.png` | $64 \times 64$ | $256 \times 256$ | RGBA | Present | 16.89% | Sharp high-contrast 'in' mark. |
| `n8n.png` | $48 \times 48$ | $256 \times 256$ | RGBA | Present | 76.07% | High transparency; visible node diagram. |
| `netflix.png` | $64 \times 64$ | $256 \times 256$ | RGBA | Present | 43.61% | Clean red 'N' ribbon mark. |

### 4.2. Policy Challenge: The "Brand Logo as Product Image" Trap
- **The Prior Assumption:** Upscaling images to $\ge 100 \times 100$ px satisfies Google Merchant Center requirements and resolves Diagnostic #5.
- **The Independent Challenge:** **[Google Merchant Center Help Article 6324350](https://support.google.com/merchants/answer/6324350)** explicitly states:
  > *"Do not submit placeholder images or images that do not show your product. Generic images, illustrations, or graphics that aren't the actual product aren't allowed. **You cannot use a brand logo or a generic placeholder image as a substitute for an actual photo of the product.**"*
- **Critical Risk:** Even at $256 \times 256$ px, Google’s automated computer vision crawler (ImageBot) detects that these files are **standalone corporate logos**, not product packaging or user-interface screenshots.
- **Verdict:** Technical compliance ($256 \times 256$ px) is achieved, but **Google policy compliance is NOT guaranteed**. For Shopping feeds, Google expects software packaging mockups (e.g., a digital access card graphic) rather than raw brand logos.
- **Confidence:** `HIGH`

---

## 5. Verification of Structured Data Changes

### 5.1. JSON-LD Syntax & Structure
- Programmatically parsed all 65 tool detail pages.
- **Result:** **65 / 65 JSON-LD blocks parsed with 0 syntax errors.**
- Verified graph structure: `BreadcrumbList`, `WebPage`, `Product`, `Offer`, `MerchantReturnPolicy`, `FAQPage`, `Organization`, `WebSite`.

### 5.2. `merchantReturnLink` Schema Validity
- Checked Schema.org vocabulary: `merchantReturnLink` is an official property of `MerchantReturnPolicy` (superseding `productReturnLink`).
- Google Search Central officially documents `merchantReturnLink` as a recognized attribute for return policy URL mapping.
- In all 40 assisted tools, the schema now specifies:
  ```json
  "hasMerchantReturnPolicy": {
    "@type": "MerchantReturnPolicy",
    "applicableCountry": "PK",
    "returnPolicyCategory": "https://schema.org/MerchantReturnFiniteReturnWindow",
    "merchantReturnDays": 7,
    "merchantReturnLink": "https://aitoolgems.tech/policies.html#refunds",
    "returnFees": "https://schema.org/FreeReturn"
  }
  ```
- **Finding:** Replacing `ReturnByMail` with `merchantReturnLink` is **100% syntactically and semantically correct**. It eliminates the physical mail return defect without creating schema errors.
- **Confidence:** `HIGH`

---

## 6. Verification of Country & Currency Assumptions

### 6.1. South Korea Configuration Evidence
- **Audit Assertion:** South Korea was configured as a target country in Google Merchant Center.
- **Independent Verification:**
  - Inspected entire codebase: Zero references to South Korea, KR, or KRW in `tools/`, `merchant_agent/`, or `data/`.
  - The feed specifies `<g:shipping><g:country>PK</g:country><g:price>0.00 PKR</g:price></g:shipping>`.
- **Finding:** The conclusion that South Korea was targeted is an **inference based exclusively on user-reported diagnostic messages**, not empirical repository code. The misconfiguration exists solely within Google's cloud portal settings (`merchants.google.com`), likely selected during onboarding or feed destination expansion.
- **Consequence:** Removing South Korea in the Merchant Center portal will eliminate the 3 South Korea diagnostics, but **will NOT approve the products**, because all 38 products remain disapproved for Misrepresentation.
- **Confidence:** `HIGH`

### 6.2. Currency Requirements
- **[Article 160637 (Currency Requirements)](https://support.google.com/merchants/answer/160637):** Feed currency must match the target country currency unless Currency Conversion is active.
- For Pakistan (`PK`), the currency must be `PKR`.
- Submitting `PKR` into a South Korea target profile without currency conversion is a verified policy violation.
- **Finding:** Confirmed. Locking targeting strictly to Pakistan aligns feed currency with country currency.
- **Confidence:** `HIGH`

---

## 7. Independent 65-Product Eligibility Audit & Correction

We re-evaluated the entire 65-product catalog, enforcing strict distinctions between **Google Merchant Center (Shopping Feeds / Free Listings)** and **Google Ads (Search Text Ads)**:

```
[Entire Catalog: 65 Tools]
 ├── 25 Directory Knowledge Profiles ──> Strictly Ineligible for Shopping Feeds (No On-Site Checkout)
 └── 40 Assisted Commercial Tools
      ├── 1 Academic Cheating Aid (turnitin) ──> Prohibited on ALL Google Platforms
      ├── 7 Shared Account Access ─────────────> Ineligible for Shopping Feeds (Enabling Dishonest Behavior)
      ├── 2 Unverified Microsoft Keys ─────────> Hold / Ineligible (Trademark/Counterfeit IP Risk)
      ├── 2 Workspace Invites (canva, gemini) ─> Hold / Ineligible (Unauthorized Distribution)
      ├── 23 Subscriptions < 12 Months ────────> Ineligible for Shopping Feeds (Article 6324371)
      │                                         └── BUT: Eligible for Google Ads Search Text Campaigns
      └── 5 Annual / Multi-Month Subscriptions ─> Potentially Eligible for Shopping Feeds (Pending Supply Chain Docs)
```

### Corrected Eligibility Classification Table

| Product Category / Slugs | Shopping Feeds (Free Listings & Shopping Ads) | Google Ads Search Text Ads | Policy Basis | Action Required |
| :--- | :--- | :--- | :--- | :--- |
| **Directory Profiles (25 tools)** <br>`ahrefs`, `v0`, `make`, `supabase`, `windsurf`, etc. | **INELIGIBLE** | **N/A (Informational)** | Article 6363310: Requires transactional cart/checkout. | Exclude from all commercial feeds. Retain for organic SEO. |
| **Academic Tool (1 tool)** <br>`turnitin` | **STRICTLY PROHIBITED** | **PROHIBITED** | Enabling Dishonest Behavior / Academic Dishonesty. | Permanently blacklist across all Google platforms. |
| **Shared Accounts (7 tools)** <br>`netflix`, `semrush`, `surfshark`, `veo`, `quillbot-shared`, `grammarly-shared`, `spotify-shared` | **INELIGIBLE** | **HIGH RISK / HOLD** | Misrepresentation / Circumventing account access limits. | Exclude from Shopping feeds. Do not run Search ads without explicit legal review. |
| **Microsoft Keys (2 tools)** <br>`windows`, `office365` | **HOLD / INELIGIBLE** | **TRADEMARK HOLD** | Copyrighted software / Trademark restrictions. | Hold until authentic supply chain invoices or MPN credentials are confirmed. |
| **Workspace Invites (2 tools)** <br>`canva`, `gemini` | **HOLD / INELIGIBLE** | **PRELIMINARY REVIEW** | Unauthorized distribution of team workspace seats. | Exclude from Shopping feeds. Permitted in Search ads with reseller disclosures. |
| **Monthly Subscriptions (23 tools)** <br>`chatgpt`, `claude`, `midjourney`, `cursor`, `runway`, `elevenlabs`, `adobe`, etc. | **INELIGIBLE FOR SHOPPING** | **ELIGIBLE WITH DISCLOSURES** | Article 6324371 mandates minimum 12-month prepaid term for Shopping feeds. Google Ads allows monthly services with reseller disclosures. | **Exclude from Merchant Center Shopping feeds.** Promote via SEO and Google Search Text Ads. |
| **Annual Private Tiers (5 tools)** <br>`gamma` (Annual), `n8n` (Annual), `figma` (Annual), `notion` (Annual), `replit` (Annual) | **POTENTIALLY ELIGIBLE** | **ELIGIBLE WITH DISCLOSURES** | Satisfies 12-month duration requirement. Subject to landing page checkout review. | Hold until owner provides supplier invoices and chooses checkout path. |

---

## 8. Synthesis of Findings & Confidence Ratings

### 8.1. Claims Confirmed
- **ReturnByMail elimination improves schema parity (HIGH):** Valid Schema.org syntax; resolves Defect 19.
- **WhatsApp checkout is prohibited on Google Shopping feeds (HIGH):** Article 6363310 requires self-service online checkout.
- **Software subscriptions $< 12$ months are ineligible for Merchant Center feeds (HIGH):** Article 6324371 explicitly mandates 1-year minimum prepaid terms.
- **Shared accounts violate Google policies (HIGH):** Breaches Misrepresentation and account manipulation rules.
- **Turnitin student accounts violate academic dishonesty policies (HIGH):** Circumventing institutional plagiarism detection is prohibited.

### 8.2. Claims Corrected
- **Physical address requirement (HIGH):** Mandatory in Merchant Center account settings; strongly expected by manual reviewers; but website guidelines technically allow phone + email combinations.
- **Scope of 12-month rule (HIGH):** Restricts Merchant Center product feeds only; does not prohibit monthly SaaS in Google Ads Search Text campaigns.
- **South Korea configuration source (HIGH):** Inferred from user diagnostics, not found in repository code.
- **Turnitin policy naming (HIGH):** No standalone "Turnitin" policy exists; violation falls under "Products that enable dishonest behavior."

### 8.3. Claims Unsupported / Critical Blockers
- **`support@aitoolgems.tech` is functional (CRITICAL BLOCKER — HIGH CONFIDENCE):** DNS lookup proves zero MX records. Email will bounce.
- **Upscaled logos guarantee image compliance (HIGH CONFIDENCE):** Article 6324350 bans standalone brand logos as product images on Google Shopping.

---

## 9. Business Facts Requiring Owner Confirmation

1. **Email Routing:** Business owner must configure MX records for `aitoolgems.tech` OR approve using a working operational email address.
2. **Physical Address:** Business owner must provide an authentic physical street address in Pakistan to publish and match with Merchant Center.
3. **South Korea Target Removal:** Business owner must manually log in to `merchants.google.com` to verify and delete South Korea from Target Countries and Feeds.
4. **Acquisition Channel Selection:** Business owner must confirm whether to:
   - **Strategy A (Recommended):** Use Google Merchant Center feeds solely for genuinely eligible annual/digital items, and use **Google Ads Search Text Campaigns** for assisted monthly subscriptions.
   - **Strategy B:** Build a full on-site credit card / web checkout and offer 12-month prepaid subscriptions to satisfy Google Shopping feeds.

---

## 10. Technical Changes Requiring Rollback or Correction

1. **`contact.html` Email Blocker:** Do **NOT** deploy commit `2133f0f` to production until MX records are verified live. If deployed now, the public contact email will bounce, causing immediate review failure.
2. **Product Images in Feeds:** For any product submitted to Google Shopping feeds, replace standalone brand logos with styled software product cards (e.g., displaying the plan duration, tool name, and brand badge on a clean background) to comply with Article 6324350.

---

## 11. Final Verdict

# `NOT READY FOR DEPLOYMENT`

### Reasons:
1. **Critical DNS Blocker:** `support@aitoolgems.tech` has no active MX records and bounces.
2. **Incomplete Contact Data:** Physical operating address is not yet supplied by the owner.
3. **Checkout Model Mismatch:** WhatsApp assisted ordering cannot be submitted to Google Shopping feeds without triggering Misrepresentation.
4. **Portal Dependencies:** South Korea settings must be verified and cleared inside the live Merchant Center portal by the account administrator.

**Safe Next-Step:** Keep commit `2133f0f` isolated on branch `feat/merchant-center-compliance`. Present this independent verification report to the business owner to resolve the 4 operational decisions before merging or requesting review.

