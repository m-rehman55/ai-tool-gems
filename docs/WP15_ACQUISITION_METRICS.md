# WP15: Backlink Acquisition Funnel Metrics & Conversion Velocity

**Document Version:** 1.0.0  
**Status:** Approved & Implemented  
**Package:** `backlink_agent.reporting.acquisition_reporter`  
**Governing Standard:** HERMES Autonomous SEO Operating System  

---

## 1. Cardinal Standard & Anti-Hallucination Gate

> **THE CARDINAL RULE:**
> Under no circumstances may candidate prospects discovered, opportunities scored, drafts generated, or owner approvals granted be tallied or reported as backlinks.
> **Only an independently verified, crawlable, indexable DOM anchor pointing to `aitoolgems.tech` counts as an earned backlink.**

Reports violating this standard create false confidence and compromise operational integrity.

---

## 2. Acquisition Funnel Metrics Schema

The funnel is divided into 5 strictly defined stages:

```
[ DISCOVERED ]   --> Candidate websites identified via crawlers / competitor gap
       |
[   SCORED   ]   --> 100-point 5-dimension qualification filter
       |
[ DRAFT_READY ]  --> High priority opportunities (>=75) with truth-grounded pitches
       |
[OWNER_APPROVED] --> Human operator explicitly authorizes manual submission
       |
[  SUBMITTED ]   --> Human operator executes submission and records evidence
       |
[  VERIFIED  ]   --> Independent DOM anchor crawl passes (HTTP 200, anchor found, indexable)
       |
[  RETAINED  ]   --> Link survives Day 7, Day 30, and Day 90 retention checks
```

---

## 3. Conversion Rate Formulations

The reporting engine calculates 3 primary conversion ratios to measure pipeline efficiency:

### 3.1 Draft-to-Approval Rate ($CR_{approval}$)
Measures the relevance and quality of the autonomous drafting engine.
$$CR_{approval} = \frac{\text{Total Owner Approved}}{\text{Total Drafts Ready}} \times 100\%$$

### 3.2 Approval-to-Submission Execution Rate ($CR_{execution}$)
Measures operator execution velocity and submission throughput.
$$CR_{execution} = \frac{\text{Total Manually Submitted}}{\text{Total Owner Approved}} \times 100\%$$

### 3.3 Submission-to-Verified Placement Rate ($CR_{placement}$)
Measures external editorial acceptance and domain outreach success.
$$CR_{placement} = \frac{\text{Actual Verified Earned Backlinks}}{\text{Total Manually Submitted}} \times 100\%$$

---

## 4. Daily Report Schema (JSON & Markdown)

Reports are exported daily to `reports/acquisition/` with standardized naming:
- `acquisition_performance_YYYY-MM-DD.md`
- `acquisition_performance_YYYY-MM-DD.json`

### JSON Schema:
```json
{
  "generated_at": "2026-11-15 06:51:01 UTC",
  "funnel_metrics": {
    "discovered": 28,
    "scored": 28,
    "draft_ready": 8,
    "owner_approved": 6,
    "manually_submitted": 5,
    "published_pending_audit": 1,
    "backlink_verified": 4,
    "retained_clean": 4,
    "quarantined": 12,
    "rejected_by_owner": 2,
    "link_removed": 0
  },
  "conversion_rates": {
    "owner_approval_rate_pct": 75.0,
    "submission_execution_rate_pct": 83.3,
    "placement_verification_rate_pct": 80.0
  },
  "actual_earned_backlinks_count": 4,
  "retention_milestones": {
    "7_day_confirmed": 4,
    "30_day_confirmed": 3,
    "90_day_confirmed": 2
  }
}
```
