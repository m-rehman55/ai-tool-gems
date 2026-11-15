# WP16: Retention Monitoring and Reporting Truth Audit

**Document Version:** 1.0.0  
**Phase:** Phase 5 & 6 (Retention & Reporting Truth Audit)  
**Verification Date:** 2026-11-15  
**Governing Modules:** `backlink_agent.retention.monitor`, `backlink_agent.reporting.acquisition_reporter`  

---

## 1. Retention Horizons & State Degradation Classification

The health of an earned placement is audited over time across three standardized retention horizons: **Day 7, Day 30, and Day 90**.

The retention monitor strictly distinguishes between:
1. **`retained`:** The placement remains live, indexable, with unchanged anchor text, rel attributes, and target destination.
2. **`anchor_changed`:** The hyperlink remains live, but the publisher modified the visible anchor text.
3. **`target_changed`:** The hyperlink was redirected or altered to point to a different destination.
4. **`noindex_added`:** The host page introduced `<meta name="robots" content="noindex">` or an `X-Robots-Tag: noindex` header.
5. **`link_removed`:** The anchor tag was removed from the DOM on an HTTP 200 response, or the page returned permanent HTTP 404 / 410.
6. **`inconclusive_temporary_failure`:** The server returned HTTP 429 (rate limited), HTTP 500-504 (server downtime), or a network socket timeout.

---

## 2. Inconclusive Temporary Failure Protection (Critical Invariant)

> **CRITICAL INVARIANT:** A temporary network glitch or server reboot must NEVER trigger a permanent state downgrade.

If an audit encounters an inconclusive state:
- The existing verified status (`backlink_verified` or `retained`) is preserved in the lifecycle store.
- The link is **NOT** marked as `link_removed`.
- The snapshot records `status_detected = INCONCLUSIVE_TEMPORARY_FAILURE` and notes the temporary status code.
- Only after **3 consecutive permanent failures (HTTP 404/410/missing anchor on HTTP 200)** is the link transitioned to `link_removed`.

---

## 3. Reporting Invariants & Reconciled Metrics

Under the HERMES operating system, every reported number must be traceable to underlying SQLite records. The reporting engine strictly enforces these boundaries:

| Stage | Internal Status | Counted as Backlink? | Funnel Metric Category |
| :--- | :--- | :--- | :--- |
| **Discovered Prospect** | `discovered` | ❌ **NO (0)** | Ingestion Intake |
| **Scored Candidate** | `scored` | ❌ **NO (0)** | Ingestion Intake |
| **Draft Ready** | `draft_ready` | ❌ **NO (0)** | Proposed Opportunity |
| **Owner Approved** | `owner_approved` | ❌ **NO (0)** | Authorization Queue |
| **Manually Submitted** | `manually_submitted` | ❌ **NO (0)** | Outbox / In-Review |
| **Published (Pending Audit)**| `published` | ❌ **NO (0)** | Verification Queue |
| **Verified Live Anchor** | `backlink_verified` | ✅ **YES (1)** | **Actual Earned Backlink** |
| **Day 7 / 30 / 90 Retained** | `retained` | ✅ **YES (1)** | **Actual Earned Backlink** |

### Conversion Rate Formulas:
1. **Owner Approval Rate:** $CR_{approval} = \frac{\text{owner\_approved}}{\text{draft\_ready}} \times 100\%$ (Guarded: returns `0.0%` if denominator is 0).
2. **Submission Execution Rate:** $CR_{execution} = \frac{\text{manually\_submitted}}{\text{owner\_approved}} \times 100\%$ (Guarded: returns `0.0%` if denominator is 0).
3. **Verified Placement Rate:** $CR_{placement} = \frac{\text{actual\_active\_backlinks}}{\text{manually\_submitted}} \times 100\%$ (Guarded: returns `0.0%` if denominator is 0).
