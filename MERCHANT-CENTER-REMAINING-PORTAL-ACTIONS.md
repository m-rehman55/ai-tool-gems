# GOOGLE MERCHANT CENTER — REMAINING PORTAL ACTIONS

**Target Account:** AI Tool Gems Pakistan (`Merchant ID: 5877049045`)  
**Store URL:** `https://aitoolgems.tech/`  
**Execution Date:** November 10, 2026  
**Auditor / Engineer:** Autonomous SRE & Merchant Center Compliance Engineer  

---

## 1. Overview & Human Authorization Boundary

The repository codebase, feed generator, and structured data schemas have been completely remediated and verified. However, **certain account-level configurations exist solely within the Google Merchant Center web console** (`merchants.google.com`) and can only be altered by the account owner logging into Google.

This document provides exact, click-by-click instructions for each remaining administrative action.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                         MANUAL PORTAL ACTION CHECKLIST                                 │
├────┬─────────────────────────────┬─────────────────────────────────────────────────────┤
│ #  │ Portal Action               │ Impact / Diagnostic Cleared                         │
├────┼─────────────────────────────┼─────────────────────────────────────────────────────┤
│ 1  │ Remove South Korea (KR)     │ Clears:                                             │
│    │ from Target Countries       │ • Missing Korean business registration number (x20) │
│    │                             │ • Missing shipping information in KR (x20)          │
│    │                             │ • Unsupported currency (PKR) in KR (x20)            │
├────┼─────────────────────────────┼─────────────────────────────────────────────────────┤
│ 2  │ Verify Phone Number         │ Clears:                                             │
│    │ (+92 323 6715731)           │ • Misrepresentation phone verification check        │
├────┼─────────────────────────────┼─────────────────────────────────────────────────────┤
│ 3  │ Update Customer Support     │ Clears:                                             │
│    │ Email Field in GMC          │ • Misrepresentation non-functional email bounce     │
├────┼─────────────────────────────┼─────────────────────────────────────────────────────┤
│ 4  │ Add 0 PKR Digital Shipping  │ Clears:                                             │
│    │ Service for Pakistan        │ • Missing shipping information for domestic offers  │
├────┼─────────────────────────────┼─────────────────────────────────────────────────────┤
│ 5  │ Hold Review Request         │ Prevents premature appeal rejection while Google    │
│    │ Until Cured                 │ re-crawls updated website code and schemas.         │
└────┴─────────────────────────────┴─────────────────────────────────────────────────────┘
```

---

## 2. Action 1: Remove South Korea (`KR`) from Target Countries & Shipping

### Why This Is Mandatory:
The repository has zero references to South Korea, KRW currency, or Korean shipping. The live diagnostic errors (`Missing Korean business registration number`, `Missing shipping information in South Korea`, and `Unsupported currency`) were triggered because South Korea was erroneously selected as a destination market in the Merchant Center portal settings.

### Step-by-Step Portal Execution:
1. Open a browser and log in to [Google Merchant Center](https://merchants.google.com/).
2. Select account: **AI Tool Gems Pakistan** (`Merchant ID: 5877049045`).
3. **Delete South Korea Shipping Service:**
   - In the left-hand navigation menu, click the **Gear Icon (Settings) > Shipping and returns**.
   - Under **Shipping services**, look for any service targeting `South Korea`.
   - Click the three-dot menu icon on that service and select **Delete**.
4. **Remove South Korea from Primary Feed Targeting:**
   - In the left menu, click **Products > Feeds**.
   - Click on your Primary Feed (e.g., `products_feed.xml`, `AI Tool Gems Feed`, or `Content API`).
   - In the top tab bar, click **Settings**.
   - Under **Target countries**, click the pencil (Edit) icon.
   - **Uncheck South Korea**.
   - Ensure that **Pakistan** is the **only** selected target country.
   - Click **Save**.

*Outcome: All 3 Korean diagnostic errors will disappear from the Diagnostics tab upon the next automated account refresh.*

---

## 3. Action 2: Verify Phone Number in Business Information

### Why This Is Mandatory:
Google's automated Misrepresentation crawler tests the operational responsiveness of published phone numbers. Verifying the number via SMS/voice in GMC establishes authenticated ownership.

### Step-by-Step Portal Execution:
1. In the left menu, click **Settings (Gear Icon) > Business information**.
2. Under the **Contact** or **Business identity** section, locate the **Phone number** field.
3. Enter the verified operational WhatsApp phone number:
   ```
   +92 323 6715731
   ```
4. Click **Verify phone number**.
5. Choose **Text message (SMS)** or **Voice call**.
6. Enter the 6-digit verification code received on the device and click **Finish**.

---

## 4. Action 3: Update Customer Support Email in GMC Settings

### Why This Is Mandatory:
Because `support@aitoolgems.tech` has been removed from the website (as no mailbox exists), keeping `support@aitoolgems.tech` in GMC's account profile will trigger a data mismatch and bounce when Google's crawler tests it.

### Step-by-Step Portal Execution:
1. In **Settings > Business information**, scroll to **Customer service contact**.
2. In the **Email** field:
   - If an operational personal Gmail exists (e.g. `mrehmanfarooq6@gmail.com`), enter it here so Google's automated policy notifications reach you.
   - If you prefer not to display an email, leave the customer support email field blank and select **Phone / Messaging** as the primary contact channel.
3. Click **Save**.

---

## 5. Action 4: Configure Free Digital Shipping for Pakistan

### Why This Is Mandatory:
For digital goods and software in Google Merchant Center, merchants must configure a domestic shipping rate. Setting a free 0 PKR rate prevents "Missing shipping information" errors for Pakistani listings.

### Step-by-Step Portal Execution:
1. Navigate to **Settings > Shipping and returns**.
2. Click **Add shipping service** (the blue `+` button).
3. **Service name:** `Instant Digital Delivery (Pakistan)`.
4. **Target country:** Select `Pakistan`.
5. **Currency:** Select `PKR`.
6. **Delivery times:**
   - Order cutoff time: `11:59 PM` (Time zone: Pakistan Standard Time / Karachi).
   - Handling time: `0` to `0` days (Monday – Sunday).
   - Transit time: `0` to `0` days (Monday – Sunday).
7. **Shipping rates:**
   - Select **Single rate for all orders**.
   - Enter `0.00 PKR` (Free Shipping).
8. Click **Save**.

---

## 6. Action 5: Hold Account Re-Review / Appeal Submission

### Policy Safety Warning:
> **DO NOT** click "Request review" or submit a policy appeal immediately after completing these steps.

### Why:
1. Google's web crawlers require 24 to 72 hours to re-fetch `aitoolgems.tech/contact.html`, `policies.html`, and the updated JSON-LD structured data.
2. If you request a review before Google's cache updates, the automated review bot will inspect the stale cached snapshot and instantly reject the appeal, incurring a mandatory cooldown penalty (often 7 to 14 days).

### Sequence to Follow:
1. Complete Actions 1 through 4 above.
2. Wait 48 hours for Google Merchant Center diagnostics to update naturally.
3. Check **Products > Diagnostics**: verify that the 3 South Korean errors have cleared to 0.
4. Only when the Diagnostics tab shows that old errors have cleared should you initiate an official review or re-submit the updated feed.

