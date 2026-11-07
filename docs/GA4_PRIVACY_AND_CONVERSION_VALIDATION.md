# GA4 Privacy and Conversion Integrity Specification & Validation

**Document ID:** ATG-SEC-GA4-001  
**Status:** VALIDATED & OPERATIONAL  
**Target Release:** Phase 2.1 Release Candidate  
**Scope:** Client-side telemetry (`attribution.js`), Server-side Measurement Protocol (`ga4_agent`), Privacy & Provenance Architecture  
**Primary Market:** Pakistan  

---

## 1. Executive Summary

This document specifies the privacy architecture, consent governance, and server-side conversion ingestion mechanisms for AIToolGems (`aitoolgems.tech`). It documents the technical remediation completed in Phase 2.1, addressing client ID provenance tracking, Consent Mode v2 default denials, Measurement ID reconciliation, symmetrical refund accounting, and telemetry PII elimination.

---

## 2. Measurement ID Reconciliation & Verification

### 2.1 Authentic Production Property
- **Active Measurement ID:** `G-NQJCMDCLLP`
- **Verification Trail:**
  - Installed and active in `attribution.js` across production pages since commit `b8b06350` (October 2026).
  - Configured in `ga4_agent/conversion_importer.py` (`MEASUREMENT_ID = "G-NQJCMDCLLP"`).
  - Documented in `marketing_agent/data/analytics.json`.
  - Stored in GitHub Secrets as `GA4_MEASUREMENT_SECRET` for secure server-side `/mp/collect` authentication.
- **Erroneous Legacy Reference:**
  - `G-F85W59KG5F` was an accidental documentation error in an earlier markdown draft. It has been audited across all codebase files (`git grep "G-F85W59KG5F"` returns 0 matches) and is formally superseded.

---

## 3. Google Consent Mode v2 Architecture

AIToolGems enforces privacy-by-default before tag evaluation. No tracking cookies or personal data are collected until affirmative consent is provided by the user.

### 3.1 Initial Consent State (`attribution.js`)
```javascript
window.gtag('consent', 'default', {
  'analytics_storage': 'denied',
  'ad_storage': 'denied',
  'ad_user_data': 'denied',
  'ad_personalization': 'denied',
  'wait_for_update': 500
});
```

### 3.2 Dynamic Consent State Transitions
Consent state updates are routed through `ATGAttribution.updateConsent(settings)`:
- When a user explicitly accepts analytics cookies:
  ```javascript
  ATGAttribution.updateConsent({ 'analytics_storage': 'granted' });
  ```
- Advertising storage (`ad_storage`, `ad_user_data`, `ad_personalization`) remains strictly `denied` as AIToolGems does not operate third-party tracking or display ad networks.

---

## 4. Client ID Provenance & PII Sanitization

### 4.1 Strict Provenance Rules
The GA4 Measurement Protocol requires a `client_id` parameter to associate server-side conversion events with web sessions.
Under HERMES Privacy Principles:
1. **Derivation from PII is Strictly Prohibited:**
   - Generating a pseudo-client-id from customer phone numbers, phone hashes, names, emails, or order metadata is illegal.
   - Any attempt to pass phone hash substrings or email addresses as `client_id` is automatically intercepted and rejected.
2. **Provenance Tracking:**
   - Every recorded order tracks its `client_id_provenance`:
     - `"browser_cookie"`: Legitimately captured from the client-side `_ga` cookie with valid random format (`^[0-9a-zA-Z._-]{10,64}$`).
     - `"none"`: Order completed without client-side cookie capture (e.g. direct manual WhatsApp inquiry).
     - `"rejected"`: Disallowed pattern intercepted by validation engine.

### 4.2 Validation Logic (`ga4_agent.models.validate_client_id`)
```python
def validate_client_id(
    client_id: Optional[str],
    customer_phone_hash: Optional[str] = None
) -> Tuple[bool, Optional[str], str]:
    if client_id is None:
        return True, None, "missing"
    c_id = str(client_id).strip()
    if not c_id:
        return True, None, "missing"

    lower = c_id.lower()
    if "@" in c_id:
        return False, None, "rejected_email_pii"
    if customer_phone_hash and (c_id in customer_phone_hash or customer_phone_hash in c_id):
        return False, None, "rejected_phone_hash_derivation"
    for marker in ("phone", "hash", "email", "customer", "user", "mobile", "contact"):
        if marker in lower:
            return False, None, f"rejected_pii_marker_{marker}"
    if not re.match(r"^[0-9a-zA-Z._-]{10,64}$", c_id):
        return False, None, "invalid_format_regex"

    return True, c_id, "browser_cookie"
```

### 4.3 Telemetry Sanitization in `attribution.js`
In previous iterations, the `proof_image_open` event passed the raw DOM image source (`proofElem.src`), which risked exposing query parameters or local image paths.
- **Remediated Implementation:**
  ```javascript
  // Sanitized proof interaction telemetry
  trackEvent('proof_image_open', {
    proof_type: 'payment_verification_proof'
  });
  ```

---

## 5. Offline Conversion & Refund Lifecycle Symmetry

### 5.1 Purchase Verification Gate
- WhatsApp link clicks represent high-intent leads (`begin_checkout`, `whatsapp_order_click`, `generate_lead`), **never** `purchase`.
- A `purchase` event is recorded **only** after domestic payment has been received, verified by human operations, and logged in persistent storage with an immutable transaction ID (`ATG-YYYYMMDD-XXX`).

### 5.2 Symmetrical Refund Lifecycle
To maintain statistical and financial ledger integrity:
1. **Parent Transaction Requirement:**
   - A refund cannot be created without a valid, verified parent purchase order (`transaction_id`). Orphan refunds are strictly rejected.
2. **Amount Bounding:**
   - The refund amount cannot exceed the parent purchase amount.
   - Cumulative refunds for a transaction cannot exceed the original verified order value.
3. **Legitimate Identifier Inheritance:**
   - Refunds inherit the parent order's verified `client_id` for Measurement Protocol dispatch.
   - If the parent order lacked a legitimate `client_id`, the refund dispatch is safely skipped (`status: "skipped_missing_legitimate_client_id"`). Identifiers are never synthesized.

---

## 6. Verification and Regression Test Suite

All GA4 privacy and conversion behaviors are verified by automated tests in `ga4_agent/tests/test_ga4_agent.py`:

| Test Case | Description | Result |
| :--- | :--- | :--- |
| `test_attribution_js_consent_mode_v2_defaults_to_denied` | Verifies default `analytics_storage: 'denied'` before consent | PASS |
| `test_attribution_js_proof_image_telemetry_sanitized` | Verifies proof image opens emit sanitized categorical metadata | PASS |
| `test_attribution_js_excludes_homepage_from_product_and_guide_events` | Verifies homepage does not emit false product/guide events | PASS |
| `test_attribution_js_separates_whatsapp_actions` | Verifies orders are separated from channel and support inquiries | PASS |
| `test_client_id_validation_rejects_email_pii` | Verifies email strings are rejected as client IDs | PASS |
| `test_client_id_validation_rejects_phone_hash_derivation` | Verifies client IDs matching phone hash are rejected | PASS |
| `test_client_id_validation_rejects_pii_markers` | Verifies strings with PII markers (`user`, `customer`) are rejected | PASS |
| `test_client_id_validation_accepts_valid_cookie_format` | Verifies standard pseudo-random GA4 cookie format is accepted | PASS |
| `test_record_verified_payment_rejects_invalid_client_id` | Verifies invalid client IDs fail gracefully with descriptive error | PASS |
| `test_refund_without_parent_order_is_rejected` | Verifies refunds without recorded parent orders are rejected | PASS |
| `test_refund_exceeding_parent_order_amount_is_rejected` | Verifies refund exceeding original price is rejected | PASS |
| `test_cumulative_refunds_exceeding_parent_order_amount_are_rejected` | Verifies partial refunds cannot sum beyond original purchase | PASS |
| `test_dry_run_strictly_never_mutates_order_or_refund_state` | Verifies dry runs never mutate persisted order/refund records | PASS |
| `test_missing_secret_returns_blocked_and_preserves_orders_and_refunds` | Verifies missing secrets leave records pending without loss | PASS |

**Total Suite Result:** 30 / 30 tests passing (100% green).

