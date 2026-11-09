# GOOGLE MERCHANT CENTER — FREE REMEDIATION OPTIONS & ARCHITECTURAL PLAYBOOK

**Target Domain:** `aitoolgems.tech`  
**Merchant Center ID:** `5877049045`  
**Repository:** `m-rehman55/ai-tool-gems`  
**Date:** November 10, 2026  
**Status:** Pre-Deployment Implementation Guide (Strict Zero-Cost Prioritization)  

---

## 1. Executive Summary

This guide outlines **100% free and zero-cost solutions** to resolve every technical and policy blocker identified in the Google Merchant Center (GMC) audit. 

No commercial SaaS subscriptions, paid email plans, or paid e-commerce platforms are required to establish compliance. Paid alternatives are documented strictly for comparison.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ZERO-COST REMEDIATION PATHWAY                   │
├────────────────────────────────┬───────────────────────────────────────┤
│ 1. Business Support Mailbox    │ Name.com Free Inbound Forwarding OR   │
│                                │ Zoho Mail Forever Free Plan ($0/mo)   │
├────────────────────────────────┼───────────────────────────────────────┤
│ 2. Checkout Incompatibility    │ Dual-Channel Strategy: Search Text    │
│    (Article 12756116)          │ Ads for WhatsApp + Crated Feed ($0)   │
├────────────────────────────────┼───────────────────────────────────────┤
│ 3. Catalog Feed Curation       │ `merchant_agent` Python Feed Filters  │
│                                │ (Exclude Turnitin / Shared / <12m)    │
├────────────────────────────────┼───────────────────────────────────────┤
│ 4. Country Targeting Cleanup   │ Manual GMC Portal Reconfiguration:    │
│                                │ Delete South Korea (KR), Set PK ($0)  │
├────────────────────────────────┼───────────────────────────────────────┤
│ 5. Physical Operating Address  │ Add Genuine Registered Pakistani      │
│                                │ Street Address to HTML + GMC ($0)     │
└────────────────────────────────┴───────────────────────────────────────┘
```

---

## 2. Business Email Remediation: Free vs. Paid Options

Google Merchant Center requires an active, responsive customer support email matching the website domain (`support@aitoolgems.tech`). The current repository references this email, but DNS MX records are absent and connections time out.

### FREE OPTION 1: Name.com Free Email Forwarding (Recommended for Fastest Setup)
The domain `aitoolgems.tech` is registered at **Name.com** and uses Name.com authoritative nameservers (`ns1.name.com` - `ns4.name.com`). Name.com provides free domain email forwarding on all active domains.

- **How it works:**
  1. In the Name.com DNS Management Console, add the standard Name.com Mail Exchange (MX) records:
     - `Priority 10`: `mx1.name.com`
     - `Priority 20`: `mx2.name.com`
  2. In the **Email Forwarding** tab of Name.com, create a forwarding rule:
     - Forward from: `support@aitoolgems.tech`
     - Forward to: `[owner_personal_inbox]@gmail.com`
  3. Add SPF TXT Record to DNS to authorize Name.com:
     - Host: `@` (or leave blank)
     - Type: `TXT`
     - Value: `v=spf1 include:_spf.name.com ~all`
- **Inbound Delivery:** 100% functional. Any verification email sent by Google or customers immediately arrives in the owner's Gmail inbox.
- **Outbound Email (Sending from support@aitoolgems.tech for Free):**
  - Name.com forwarding is inbound-only.
  - To send outbound replies from `support@aitoolgems.tech` without paying, connect the email address in Gmail (*Settings > Accounts and Import > Send mail as*) using a **Free SMTP Relay Service**:
    - **Brevo (formerly Sendinblue):** Free tier provides 300 free emails per day with custom domain DKIM/SPF.
    - **Resend:** Free tier provides 3,000 free emails per month (100/day).
- **Cost:** **$0.00 / month forever**.

---

### FREE OPTION 2: Zoho Mail "Forever Free Plan"
Zoho Mail offers a dedicated custom-domain business email hosting tier with zero monthly fee.

- **Plan Details:**
  - Up to 5 custom domain user accounts.
  - 5 GB email storage per user.
  - Custom webmail interface and native mobile apps (iOS & Android).
- **Setup Steps:**
  1. Register at `https://www.zoho.com/mail/zohomail-pricing.html` and select the **Forever Free Plan**.
  2. Verify domain ownership by adding a TXT/CNAME record at Name.com.
  3. Configure Zoho MX records at Name.com:
     - Priority 10: `mx.zoho.com`
     - Priority 20: `mx2.zoho.com`
     - Priority 50: `mx3.zoho.com`
  4. Configure SPF record:
     - `v=spf1 include:zoho.com ~all`
  5. Configure DKIM record:
     - Generate DKIM key in Zoho Mail Admin Console and add the TXT record (`zoho._domainkey.aitoolgems.tech`) at Name.com.
  6. Configure DMARC record:
     - Host: `_dmarc.aitoolgems.tech`
     - Type: `TXT`
     - Value: `v=DMARC1; p=none; rua=mailto:support@aitoolgems.tech`
- **Limitations of Free Tier:**
  - **No IMAP/POP support:** You cannot sync this free account into third-party desktop email clients like Microsoft Outlook or Apple Mail. You must access emails via `mail.zoho.com` in a browser or through the official Zoho Mail mobile app.
- **Cost:** **$0.00 / month forever**.

---

### FREE OPTION 3: Cloudflare Email Routing
If DNS management is shifted from Name.com to Cloudflare (free tier):
- Cloudflare provides free, unlimited inbound email routing from `support@aitoolgems.tech` to any destination mailbox.
- Includes automatic SPF and DKIM generation.
- **Cost:** **$0.00 / month**.

---

### Paid Email Comparison (For Future Scaling)
| Provider | Monthly Cost per User | Features | Trade-Off |
| :--- | :--- | :--- | :--- |
| **Namecheap Private Email** | ~$1.25 / mo ($14.88/yr) | IMAP/POP, 5GB storage, webmail | Low cost, basic web UI |
| **Google Workspace Business Starter** | $6.00 / mo | Gmail UI, Google Drive, Meet, Calendar | Higher monthly overhead |
| **Microsoft 365 Business Basic** | $6.00 / mo | Outlook Web, 50GB mailbox, Teams, OneDrive | Higher monthly overhead |

**Recommendation:** Proceed with **FREE OPTION 1 (Name.com Forwarding)** or **FREE OPTION 2 (Zoho Mail Free Tier)**. Both eliminate BLK-01 at zero expense.

---

## 3. Checkout Compliance & Channel Strategy Playbook

### The Root Conflict (Google Policy Article 12756116)
Google Merchant Center Shopping Feeds (Free Listings & Shopping Ads) require:
> *"Users must be able to add the item to a cart and complete checkout directly on your online store without leaving to an unassociated third-party messaging app."*

Because `aitoolgems.tech` uses conversational WhatsApp checkout for manual Pakistani payment rails (EasyPaisa, JazzCash, Bank IBFT), Google's automated shopping crawler will flag the site for non-compliant checkout.

### Zero-Cost Strategic Options

#### STRATEGY A (Recommended): Dual Marketing Architecture
Separate the commercial marketing channels to align perfectly with Google policy:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        DUAL MARKETING ARCHITECTURE                     │
├────────────────────────────────────┬───────────────────────────────────┤
│ 1. GOOGLE SEARCH ADS & ORGANIC SEO │ 2. GOOGLE MERCHANT CENTER FEED    │
│    (Text Campaigns & Ranking)      │    (Shopping Free Listings)       │
├────────────────────────────────────┼───────────────────────────────────┤
│ • Targets: High-intent keywords    │ • Restricted strictly to eligible │
│ • Destination: Tool landing pages  │   annual/prepaid digital tools    │
│ • Purchase Flow: WhatsApp assisted │ • Target Country: Pakistan (PK)   │
│ • 100% Compliant under Google Ads  │ • Requires on-site self-service   │
│   Landing Page Editorial Policy    │   checkout or form submission     │
│ • Zero code changes to core UX     │ • Zero-cost feed filtering        │
└────────────────────────────────────┴───────────────────────────────────┘
```

- **Why this works:** Google Ads Search (Text Ads) does **NOT** enforce Article 12756116. On Google Search campaigns, having a clear "Order via WhatsApp" button on a landing page with upfront pricing is 100% compliant under Google Ads policies.
- **Cost:** **$0.00 infrastructure cost**.

#### STRATEGY B: Zero-Cost Serverless On-Site Checkout Integration
If the owner desires active Google Shopping product carousels:
- **Architecture:** Deploy a client-side digital ordering form that allows users to submit customer name, email, and select payment rail (EasyPaisa / JazzCash / Bank Transfer), generating an immediate on-site order confirmation receipt (`/order-success.html`).
- **Payment Verification:** Customer completes payment via their banking app and uploads the transaction reference number (TRX ID) directly on the website form.
- **Backend:** Hosted for free on Cloudflare Pages Functions, Netlify Functions, or GitHub Pages + Formspree/Formspark free tier.
- **Compliance Status:** Satisfies the requirement that the order is initiated and confirmed on the domain without an involuntary redirect.
- **Cost:** **$0.00 / month**.

---

## 4. Zero-Cost Catalog Curation (`merchant_agent`)

The automated feed generator in `merchant_agent/feed_generator.py` can be configured to filter out non-compliant items automatically, ensuring only 100% policy-compliant items are submitted to Google.

### Feed Exclusion Rules (Implemented in Code at Zero Cost):
1. **Exclude Prohibited Academic Cheating Tools:** Automatically filter out `turnitin`.
2. **Exclude Shared Multi-User Accounts:** Automatically filter out tools with `access_type == "shared"` (`ahrefs`, `semrush`, `moz`, `envato`, `coursera`, `helium10`, `ubersuggest`).
3. **Exclude Monthly Subscriptions (< 12 Months):** Automatically filter out products without an annual or lifetime duration.
4. **Exclude Unverified OEM Keys:** Suppress `windows` and `office365` until official distributor documentation is available.

### Eligible Shopping Product Roster:
By applying these zero-cost filters, the generated Shopping XML feed retains clean, high-margin, compliant digital products:
- `gamma` (Annual Personal License)
- `n8n` (Self-Hosted Community / Annual Setup)
- `figma` (Annual Professional License)
- `notion` (Annual Personal Plus)
- `replit` (Annual Hacker / Core Plan)

---

## 5. Free Merchant Center Portal Configuration Guide

Follow these manual steps inside the Google Merchant Center web interface (`merchants.google.com`) at zero cost:

### Step 1: Remove South Korea (`KR`) Targeting
1. Log in to [Google Merchant Center](https://merchants.google.com/) using account ID `5877049045`.
2. In the left navigation menu, click **Settings (Gear Icon) > Shipping and returns**.
3. Under **Shipping services**, delete any service targeting South Korea.
4. Navigate to **Products > Feeds**.
5. Click on your Primary Feed and open **Settings**.
6. Under **Target countries**, remove `South Korea` and ensure only **Pakistan** is selected.
7. Save changes. *(This instantly clears the 3 South Korea diagnostic errors).*

### Step 2: Configure Free Digital Shipping for Pakistan
1. Under **Shipping and returns**, click **Add shipping service**.
2. Service name: `Digital Instant Delivery (Pakistan)`.
3. Target country: `Pakistan`.
4. Currency: `PKR`.
5. Delivery time:
   - Order cutoff: `11:59 PM`.
   - Handling time: `0 - 0 days`.
   - Transit time: `0 - 0 days`.
6. Shipping rates: Select **Free shipping over PKR 0** (Flat Rate PKR 0).
7. Save service.

### Step 3: Complete Business Information
1. Navigate to **Settings > Business information**.
2. **Business Name:** `AI Tool Gems Pakistan`.
3. **Physical Address:** Enter the verified, street-level operating address in Lahore, Pakistan (matching the address to be published on `contact.html`).
4. **Phone Number:** Verify `+92 324 9826265` via SMS or automated voice call.
5. **Customer Service Email:** Enter `support@aitoolgems.tech` (once the free forwarding or Zoho MX records are active).
6. Save changes.

---

## 6. Action Checklist for Business Owner

| Phase | Action Item | Platform | Cost | Estimated Time |
| :--- | :--- | :--- | :--- | :--- |
| **1. Email** | Add Name.com MX records and set up forwarding from `support@aitoolgems.tech` to Gmail. | Name.com DNS | **$0** | 10 minutes |
| **2. Email** | Send a test email from an outside account to `support@aitoolgems.tech` and confirm receipt. | Outside Email | **$0** | 2 minutes |
| **3. Address** | Provide official street-level operating address for Lahore, Pakistan. | Owner Decision | **$0** | Immediate |
| **4. GMC Settings** | Delete South Korea from GMC feeds and shipping settings. | `merchants.google.com` | **$0** | 5 minutes |
| **5. GMC Settings** | Add 0 PKR Digital Shipping service for Pakistan. | `merchants.google.com` | **$0** | 5 minutes |
| **6. Strategy** | Confirm channel strategy: Search Text Ads for WhatsApp sales vs. Serverless On-Site Checkout for Shopping feeds. | Owner Decision | **$0** | Strategic |

---

## 7. Conclusion

By executing the zero-cost steps above:
- All 3 South Korean errors are eliminated.
- The critical contact verification blocker (dead email) is permanently resolved.
- Misrepresentation risks related to business identity are cleared.
- Zero financial expenditure is incurred.

