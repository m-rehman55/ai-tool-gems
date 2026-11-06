# GA4 Conversion & Event Tracking Quality Assurance Report
**Measurement ID:** `G-NQJCMDCLLP`  
**Implementation File:** `attribution.js`  
**QA Date:** 6 November 2026  

---

## 1. Verified Event Model Taxonomy

| Standard GA4 Event | Actual Trigger Condition | Parameters Delivered | Verification Status |
|---|---|---|---|
| `view_item` | Product page (`/tools/<slug>/`) loaded | `currency: 'PKR'`, `items: [{ item_name, currency: 'PKR' }]` | **VERIFIED** |
| `select_item` | Product card clicked on directory / hub | `item_name`, `link_url` | **VERIFIED** |
| `begin_checkout` | Customer clicks WhatsApp Order CTA button | `currency: 'PKR'`, `items: [{ item_name, currency: 'PKR' }]` | **VERIFIED** |
| `generate_lead` | Customer initiates qualified order inquiry via WhatsApp | `currency: 'PKR'`, `lead_type: 'whatsapp_order_inquiry'`, `item_name` | **VERIFIED & WIRED** |
| `purchase` | Offline confirmed domestic payment received | `transaction_id`, `value`, `currency: 'PKR'`, `items: [...]` | **OFFLINE DISPATCH ONLY** |
| `page_view` | Initial load & SPA route change | `page_path` | **VERIFIED** |
| `rage_click` | 3 rapid clicks on same element within 1s | `target_selector`, `click_count`, `time_window_ms` | **VERIFIED** |
| `dead_click` | Click on un-clickable element with pointer cursor | `target_selector`, `text_content` | **VERIFIED** |

---

## 2. Inviolable Conversion Guardrails

1. **WhatsApp Click != Purchase:**
   - Under no circumstances does clicking a WhatsApp button fire a `purchase` event in the browser.
   - A WhatsApp click is strictly tracked as `begin_checkout` and `generate_lead`.
2. **Purchase Event Integrity:**
   - Verified purchases are recorded offline by `ga4_agent` via Google Analytics Measurement Protocol (`/mp/collect`) only after proof of payment (EasyPaisa / JazzCash / Bank IBFT transaction ID) is confirmed.
3. **Zero PII Transmitted:**
   - No names, telephone numbers, emails, passwords, or WhatsApp conversation text are transmitted to Google Analytics or PostHog.
4. **Deferred Performance Loading:**
   - GA4 script injection is scheduled via `requestIdleCallback` (with a fallback timeout of 2,000ms), ensuring analytics scripts never block Core Web Vitals (LCP/FCP).
