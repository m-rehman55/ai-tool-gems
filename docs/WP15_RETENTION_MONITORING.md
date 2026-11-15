# WP15: Long-Term Backlink Retention & Change Detection Monitoring

**Document Version:** 1.0.0  
**Status:** Approved & Implemented  
**Package:** `backlink_agent.retention`  
**Governing Standard:** HERMES Autonomous SEO Operating System  

---

## 1. Objective & Challenge

Acquiring a backlink is only half the battle. Industry data indicates that 18% to 32% of earned backlinks decay, disappear, or are de-indexed within 90 days due to website redesigns, editorial purges, CMS migration errors, or intentional publisher removal.

The Retention Monitoring Engine (`RetentionMonitor`) provides automated, non-destructive auditing of previously earned backlinks across standard retention horizons: **Day 7, Day 30, and Day 90**.

---

## 2. Retention Milestones & Cadence

| Horizon | Primary Risk Assessed | Action on Failure |
| :--- | :--- | :--- |
| **Day 7** | Immediate editorial rollback, automated moderation purge, or URL restructure. | Immediate owner Telegram notification; editorial contact lookup. |
| **Day 30** | CMS template changes, author link swaps, or relocation to archive/paged archives. | Flag as `link_modified` or `link_removed`; update acquisition report. |
| **Day 90** | Domain expiration, wholesale de-indexing, sitewide noindex, or permanent link purge. | Mark as `archived` (if retained) or terminal loss; update lifetime retention curve. |

---

## 3. Change Detection Engine

The retention monitor compares the live crawl result (`DetailedVerificationResult`) against the baseline snapshot recorded at initial verification.

### Detected Change Categories:
1. **`retained` (Healthy):** Anchor text, target URL, indexability, and qualification remain consistent.
2. **`anchor_changed`:** The link is present, but the anchor text was changed (e.g. from brand "AI Tool Gems" to generic "source" or keyword text).
3. **`target_changed`:** The hyperlink points to a different target or subpage than originally approved.
4. **`rel_changed`:** The rel attribute changed (e.g., from `dofollow` to `nofollow` or `ugc`).
5. **`noindex_added`:** The host page introduced `<meta name="robots" content="noindex">` or `X-Robots-Tag: noindex`.
6. **`link_removed`:** The anchor tag was deleted from the page body, or the source page returned a permanent HTTP `404 Not Found` or `410 Gone`.

---

## 4. Temporary 5xx / Timeout Inconclusive Protection

> **CRITICAL INVARIANT:** A temporary network glitch must NEVER trigger a permanent state downgrade.

If an external publisher's server encounters high load, downtime, or DDoS protection resulting in HTTP 500, 502, 503, 504, or socket timeout:
- The monitor classifies the audit as **`inconclusive_temporary_failure`**.
- The existing verified status is preserved.
- The link is NOT marked as `link_removed`.
- A retry is scheduled for the next audit cycle.
- Only after **3 consecutive permanent failures (404/410/missing anchor on HTTP 200)** is the link transitioned to `link_removed`.

---

## 5. Retention Snapshot Schema

Each audit produces an immutable `RetentionSnapshot`:
```json
{
  "prospect_id": "dir_001_aitoolpak",
  "audit_timestamp": "2026-11-15T06:45:00Z",
  "days_since_first_verified": 30,
  "milestone_reached": "30_day",
  "retention_status": "retained",
  "http_status": 200,
  "is_indexable": true,
  "current_anchor_text": "AI Tool Gems",
  "current_rel_tokens": [],
  "current_content_hash": "a8f5c9e2b1049382...",
  "change_detected": false,
  "change_summary": "All attributes identical to baseline."
}
```
