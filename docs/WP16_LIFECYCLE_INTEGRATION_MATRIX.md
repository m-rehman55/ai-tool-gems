# WP16: Comprehensive Lifecycle State Transition Matrix

**Document Version:** 1.0.0  
**Phase:** Phase 1 (Lifecycle Integration Matrix)  
**Verification Date:** 2026-11-15  
**Governing Code:** `backlink_agent.lifecycle.models.VALID_TRANSITION_GRAPH`  

---

## 1. Complete 18-State Catalog

| State ID | State Constant | Type | Purpose & Lifecycle Context |
| :--- | :--- | :--- | :--- |
| **S01** | `discovered` | Active | Candidate prospect identified via automated discovery channels. |
| **S02** | `evidence_verified` | Active | Source domain, route, and basic reachability validated. |
| **S03** | `scored` | Active | Scored by 100-point 5-dimension qualification engine. |
| **S04** | `draft_ready` | Active | High priority (>=75) candidate with generated truth-grounded pitch. |
| **S05** | `owner_approved` | Active | Explicitly reviewed and authorized by site owner for manual submission. |
| **S06** | `manually_submitted`| Active | Owner executed manual web form or outreach and supplied proof. |
| **S07** | `publication_pending`| Staging | Submission acknowledged by external publisher; awaiting appearance. |
| **S08** | `published` | Active | Publisher reported placement live; awaiting independent DOM crawl. |
| **S09** | `backlink_verified` | **Earned** | **Live indexable anchor independently confirmed via strict DOM audit.** |
| **S10** | `retained` | **Earned** | **Earned link verified healthy at Day 7, 30, or 90 retention checks.** |
| **S11** | `quarantined` | Terminal | Rejected during scoring (<55, toxic PBN, reciprocal demand, paywall). |
| **S12** | `rejected` | Terminal | Explicitly rejected by owner during draft review. |
| **S13** | `submission_failed` | Failure | Owner reported form broken, captcha impassable, or email bounced. |
| **S14** | `verification_failed`| Failure | Deep DOM crawl confirmed anchor absent, wrong target, or noindex. |
| **S15** | `verification_inconclusive` | Transient | Audit encountered temporary HTTP 5xx, timeout, or network glitch. |
| **S16** | `link_changed` | Degraded | Earned link still present but anchor text, target, or rel tokens drifted. |
| **S17** | `link_removed` | Degraded | Previously earned link confirmed vanished or page returned 404/410. |
| **S18** | `expired` | Terminal | Prospect or opportunity aged out without action (>90 days inactive). |

---

## 2. Permitted State Transitions Matrix

| From State | Allowed Target States | Trigger / Condition | Required Evidence Data | Failure Mode if Violated |
| :--- | :--- | :--- | :--- | :--- |
| `discovered` | `evidence_verified` | Reachability check passes | DNS and HTTP pre-flight OK | Fails closed; remains `discovered` |
| | `quarantined` | Spam signals or blacklisted | Risk factor documented | Blocked from further processing |
| | `expired` | Inactive > 90 days | Ingestion timestamp > 90d | Retired to archive |
| `evidence_verified` | `scored` | Scoring engine completed | 5-dimension score breakdown | Fails closed; remains un-scored |
| | `quarantined` | Score < 55 or toxic flag | Score < 55 | Quarantined permanently |
| | `expired` | Stale prospect | Ingestion timestamp > 90d | Retired to archive |
| `scored` | `draft_ready` | Score >= 75 (High Priority) | Draft generated + hash | Remains in `scored` |
| | `quarantined` | Score < 55 | Score < 55 | Quarantined permanently |
| | `expired` | Score 55-74 without review | Age > 90d | Retired to archive |
| `draft_ready` | `owner_approved` | Owner review in UI/Telegram | Inbound `draft_hash` matches stored | **Hash mismatch rejected** |
| | `rejected` | Owner declines opportunity | Rejection reason recorded | Discarded |
| | `expired` | Draft unreviewed > 30 days | Age > 30d | Retired |
| `owner_approved` | `manually_submitted` | Owner completes external form | `ManualSubmissionEvidence` | **Missing evidence or secrets rejected** |
| | `submission_failed` | External form error/captcha | Failure reason recorded | Moves to `submission_failed` for retry |
| | `rejected` | Owner revokes approval | Revocation reason | Moved to `rejected` |
| `manually_submitted`| `publication_pending` | Confirmation email received | Confirmation reference | Staged for crawl |
| | `published` | Direct placement confirmed | `publication_url` required | **Missing publication URL rejected** |
| | `submission_failed` | Editorial bounce / rejection | Rejection notice | Moves to `submission_failed` |
| `publication_pending`| `published` | Publisher notifies live | `publication_url` required | **Missing publication URL rejected** |
| | `verification_inconclusive`| Crawl attempt timed out | Inconclusive error | Staged for automatic re-probe |
| | `expired` | 60 days without appearance | Timeout reached | Retired |
| `published` | `backlink_verified` | Deep DOM crawl succeeds | `anchor_verified=True` + `target_url_matched=True` | **Missing DOM proof rejected** |
| | `verification_failed`| Anchor missing or noindexed | Crawl outcome details | Flagged for operator review |
| | `verification_inconclusive`| 5xx error or socket timeout | Server error / timeout code | **Preserves state; scheduled for retry** |
| `backlink_verified` | `retained` | Day 7/30/90 milestone hit | Milestone crawl passes | Milestone recorded in retention log |
| | `link_changed` | Anchor, rel, or target drifted| Drift diff documented | Operator notification dispatched |
| | `link_removed` | Anchor deleted (HTTP 200) | Missing anchor crawl proof | Marked `link_removed` |
| | `verification_inconclusive`| 5xx error or socket timeout | Server error / timeout code | **Preserves verified state; retry queued** |
| `retained` | `retained` | Subsequent milestone passed | Milestone crawl passes | Milestone incremented |
| | `link_changed` | Anchor, rel, or target drifted| Drift diff documented | Operator notification dispatched |
| | `link_removed` | Anchor vanished / 404 / 410 | Crawl proof of removal | Marked `link_removed` |
| | `verification_inconclusive`| 5xx error or socket timeout | Server error / timeout code | **Preserves retained state; retry queued** |
| `verification_inconclusive`| `backlink_verified` | Retry crawl succeeds | DOM anchor evidence | Promoted to verified |
| | `verification_failed`| Retry returns 404 or missing | Permanent failure proof | Marked verification failed |
| | `link_removed` | 3 consecutive failures | Failure history | Marked link removed |
| `link_changed` | `backlink_verified` | Publisher restored anchor | DOM anchor evidence | Re-instated as verified |
| | `link_removed` | Unsatisfactory drift rejected | Owner decision | Marked link removed |
| `submission_failed` | `manually_submitted` | Owner retries submission | New `ManualSubmissionEvidence` | Re-queued for verification |
| | `rejected` | Owner gives up on form | Rejection reason | Discarded |
| `verification_failed`| `link_removed` | Absence confirmed | Crawl proof | Retired |
| | `expired` | Inactive > 60 days | Age > 60d | Retired |
| `link_removed` | `expired` | Removed link archived | Age > 90d | Retired |
| `quarantined` | *(None)* | **TERMINAL** | N/A | Fails closed (immutable) |
| `rejected` | *(None)* | **TERMINAL** | N/A | Fails closed (immutable) |
| `expired` | *(None)* | **TERMINAL** | N/A | Fails closed (immutable) |
