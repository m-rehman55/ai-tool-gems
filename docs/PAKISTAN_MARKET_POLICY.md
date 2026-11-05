# PAKISTAN MARKET POLICY & BUSINESS STANDARDS
**Authority**: HERMES Autonomous SEO & Growth Governance  
**Scope**: 100% of Commercial Operations, Landing Pages, Tools, Metadata, Schemas & Messaging  

---

## 1. Core Market Mandate

AI Tool Gems (`https://aitoolgems.tech/`) operates exclusively with **PAKISTAN as its primary and active commercial fortress**.

All commercial claims, product listings, pricing displays, payment instructions, transactional search optimization, and marketing communication must be 100% aligned with Pakistani business realities and consumer expectations.

---

## 2. Currency & Pricing Integrity

1. **Currency**: All commercial product listings and public offers must state prices in **Pakistani Rupees (PKR / Rs.)**.
2. **Flat & Transparent Rates**: Prices must be clearly displayed as flat numbers (e.g., `Rs. 2,300/mo` or `PKR 2,300`).
3. **No Foreign Commercial Dominance**: No page may present foreign currencies (such as USD or JPY) as primary local consumer pricing. Historical USD references for international inquiries must remain strictly secondary and transparent without misleading local users.
4. **No Currency Fabrication**: Prices listed in schema, OpenGraph tags, and UI modals must match the exact price verified on WhatsApp.

---

## 3. Domestic Payment Rails (Pakistan)

Orders are confirmed and provisioned via verified domestic Pakistani financial rails:
- **EasyPaisa** (Telenor Microfinance Bank)
- **JazzCash** (Mobilink Microfinance Bank)
- **SadaPay** (EMI / Commercial Banking)
- **NayaPay** (EMI)
- **Raast** (State Bank of Pakistan Instant Payment System)
- **Bank IBFT** (Interbank Funds Transfer across all scheduled Pakistani commercial banks)

No foreign checkout gateway (such as Stripe, PayPal, or foreign merchant portals) may be claimed as an active local domestic payment option.

---

## 4. Product Provisioning, Licensing & Transparency

1. **Truthful Access Types**: Every tool listing must explicitly define its delivery format:
   - **Private Account**: Dedicated user access with personal credentials.
   - **Shared Account**: Multi-profile access subject to fair-usage guidelines.
   - **Invitation**: Direct workspace/team email invitation.
   - **License Key**: Official digital product key/code.
2. **Third-Party Terms Verification**: No tool listing may claim official direct reseller status unless authorized by the software provider. Disclose marketplace independence clearly.
3. **Delivery Timelines**: State realistic delivery estimates (assisted WhatsApp fulfillment within confirmed support hours). Never claim instant automated delivery unless an automated webhook or API actually provisions the license.
4. **Warranty & Replacement**: Clearly state replacement policies (e.g., 7-day or duration of subscription replacement for account lockouts). Digital software replacement must never claim "Return by Mail" in structured data or copy.

---

## 5. Review & Social Proof Truthfulness

1. **No Fabricated Reviews**: Never inject fake customer names, simulated testimonials, or artificial 5-star review markup.
2. **Structured Data Alignment**: Schema `Product` markup must ONLY include `Review` or `AggregateRating` if genuine, verifiable customer reviews are visible on the page.
3. **No Artificial Urgency**: Do not deploy fake countdown timers, fake stock counters, or simulated purchase notification toasts.

---

## 6. International & Historical Safeguards

1. **Japan Market Exclusion**: Permanent prohibition of Japanese commercial targeting, yen (`¥`, `JPY`), Japanese cities, and Japanese language meta tags.
2. **Preservation of Historical Safeguards**: Existing Japan unit tests (`tests/test_japan_safeguards.py`, `seo-agent/tests/test_scope_guard.py`) are immutable and must continue to pass 100%.
3. **No Unrelated Homepage Redirects**: Historical URLs must be evaluated individually for search traffic and canonical mapping before any redirect is applied.

