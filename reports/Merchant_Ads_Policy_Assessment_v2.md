# Google Merchant Center & Google Ads Policy Assessment (Version 2)

**Website:** [aitoolgems.tech](https://aitoolgems.tech/)  
**Document ID:** GADS-MC-POLICY-V2-20261107  
**Status:** REVISED & GOVERNANCE ENFORCED  
**Release Readiness Gate:** HARD BLOCK (Feeds & Campaigns Held Pending Human Owner Approval)  
**Agent Responsible:** AGENT-13-MERCHANT ([`merchant_agent`](file:///d:/Desktop/AI%20Tools%20Aura/merchant_agent))  

---

## 1. Executive Summary & Critical Governance Updates

In accordance with Phase 8 of the remediation master plan:
1. **Label Renaming**: The previous automated status label `ELIGIBLE_WITH_DISCLOSURES` has been permanently renamed to **`PRELIMINARY_POLICY_REVIEW`**. This eliminates the false perception that automated systems have approved ads for live deployment without human legal/policy review.
2. **Mandatory Campaign Hold**: All Google Ads search campaigns and Google Merchant Center product feed submissions remain **STRICTLY BLOCKED** (`HOLD`). No feeds are submitted to Google Merchant Center, and no ads accounts are active.
3. **No Fabricated Defaults**: If duration or access model is missing from an offer record, systems record `UNVERIFIED` and classify the item as `HOLD_UNVERIFIED_TERMS`, rather than assuming default 1-month or private terms.

---

## 2. Google Merchant Center (Shopping & Free Listings) Evaluation

Under Google Merchant Center policies for digital software and subscriptions, 100% of the active catalogue (40 tools) is currently on **HOLD** in [`data/merchant/merchant_hold_register.json`](file:///d:/Desktop/AI%20Tools%20Aura/data/merchant/merchant_hold_register.json).

```
TOTAL CATALOG TOOLS EVALUATED: 40
├── HOLD_TERM_INSUFFICIENT: 34 tools (85.0%)
│   └── GMC Software Subscriptions Policy requires minimum 12-month prepaid terms;
│       storefront offers are currently 1-month subscriptions.
├── HOLD_POLICY_VIOLATION: 2 tools (5.0%)
│   ├── Netflix Premium (Shared account access violates Misrepresentation policy).
│   └── Turnitin (Violates Academic Dishonesty & Plagiarism bypass policy).
├── HOLD_UNVERIFIED_AUTHORIZATION: 2 tools (5.0%)
│   └── Windows 11 & Office 365 (Require verified Microsoft Partner Network certificates).
└── HOLD_RESELLER_AUTHORIZATION_PENDING: 2 tools (5.0%)
    └── Gamma & n8n (Annual plans exist, but official OEM distributor proof is pending).
```

### Key Policy Disqualifiers:
- **12-Month Minimum Term Rule**: Google Shopping software subscriptions policy explicitly requires digital software subscriptions to be prepaid for a minimum of 1 year. The core AIToolGems commercial value proposition in Pakistan is affordable, flexible monthly access (e.g., Rs. 2,300/mo for ChatGPT Plus). Submitting these to Google Shopping would result in immediate account-level feed disapproval.
- **Shared Access Ban**: Google Merchant Center policy against Enabling Dishonest Behavior prohibits reselling shared logins or credentials.
- **Academic Dishonesty Ban**: Turnitin and student accounts are permanently barred under Google's academic cheating policy.

---

## 3. Google Ads (Search Text Ads) Evaluation

Unlike Google Merchant Center, Google Ads Search Text Ads permit third-party resellers and independent software support providers under the **Google Ads Third-Party Reseller Policy**, subject to strict compliance rules.

### 3.1 Status Classification Breakdown
- **`PRELIMINARY_POLICY_REVIEW` (36 tools):** Qualify for preliminary consideration under Third-Party Reseller guidelines, but remain on **HOLD** until explicit human owner review.
- **`HOLD_PROHIBITED` (1 tool — Turnitin):** Strictly prohibited under Academic Dishonesty Policy. No search ads permitted under any circumstances.
- **`HOLD_HIGH_RISK` (1 tool — Netflix Shared):** High probability of advertiser account suspension due to account-sharing restrictions.
- **`HOLD_TRADEMARK_RISK` (2 tools — Windows 11, Office 365):** Microsoft actively enforces trademark restrictions on brand keywords in ad copy.

### 3.2 Mandatory Conditions for Future Ads Activation (When Approved by Owner)
If the repository owner decides to initiate Google Ads Search campaigns in the future:
1. **Prominent Non-Affiliation Disclaimers**: Ad copy and landing pages must clearly state "Independent Provider / Setup Assistance" with zero imitation of official brand identity.
2. **Exact Upfront Pricing**: Ads must reflect exact PKR pricing without hidden recurring billing.
3. **Negative Keyword Lists**: Add negative keywords for brand claims, e.g., "official openai store", "microsoft authorized distributor", "free crack", "keygen".

---

## 4. Technical File & Feed Verification

- [`merchant_agent/feed_generator.py`](file:///d:/Desktop/AI%20Tools%20Aura/merchant_agent/feed_generator.py): Enforces policy checks, sets `PRELIMINARY_POLICY_REVIEW`, and outputs sanitized feeds.
- [`data/merchant/products_feed.xml`](file:///d:/Desktop/AI%20Tools%20Aura/data/merchant/products_feed.xml): Cleaned of all "instant domestic activation" claims; strictly contains 0 items in live automated mode because all items are on policy hold.
- [`data/merchant/merchant_hold_register.json`](file:///d:/Desktop/AI%20Tools%20Aura/data/merchant/merchant_hold_register.json): Complete durable audit log documenting the specific policy rationale for all 40 held tools.
- [`merchant_agent/tests/test_merchant_agent.py`](file:///d:/Desktop/AI%20Tools%20Aura/merchant_agent/tests/test_merchant_agent.py): 10 unit tests passing (100% green).
