# WP14 Daily Executive Report & Telemetry Schema
**Document Version:** 1.0.0  
**Date:** 2026-11-15  
**Branch:** `feat/backlink-agent-critical-fixes`  
**Status:** Approved & Enforced  

---

## 1. Schema Philosophy: Earned Authority Over Vanity Quotas

HERMES strictly adheres to Google Search Central quality guidelines:
> **Core Invariant:** Discovered candidate prospects, scored opportunities, and generated drafts are **pipeline inputs only**, NEVER to be reported or counted as acquired backlinks. Only independently verified HTML `<a>` tags with `200 OK` HTTP status and correct canonical destination targets are classified as live backlinks.

---

## 2. Structured JSON Telemetry Schema (`backlink_intelligence_YYYY-MM-DD.json`)

```json
{
  "$schema": "https://aitoolgems.tech/schemas/backlink-telemetry-v1.json",
  "generated_at": "2026-11-15T06:22:57.123456Z",
  "run_id": "run_9a8b7c6d5e",
  "pipeline_version": "2.0.0",
  "environment": "staging",
  "mode": "report_only",
  "dry_run": true,
  "execution_metrics": {
    "duration_seconds": 0.19,
    "memory_peak_mb": 42.5,
    "cpu_percent": 12.0
  },
  "discovery_metrics": {
    "sources_attempted": 4,
    "sources_succeeded": 4,
    "sources_failed": 0,
    "raw_prospects_discovered": 12,
    "duplicates_filtered": 3,
    "unique_prospects": 9,
    "breakdown_by_source": {
      "curated_directory": 4,
      "github_awesome": 2,
      "technical_publication": 3,
      "competitor_gap": 0
    }
  },
  "quality_scoring_metrics": {
    "total_scored": 9,
    "tier_distribution": {
      "high_priority": 9,
      "investigate": 0,
      "quarantine": 0
    },
    "score_statistics": {
      "min_score": 79,
      "max_score": 100,
      "mean_score": 89.8
    },
    "rejection_reasons": {
      "toxic_pbn_pattern": 0,
      "reciprocal_link_demanded": 1,
      "noindex_meta_tag": 0,
      "paid_link_requirement": 0
    }
  },
  "drafting_metrics": {
    "draft_ready_opportunities": 9,
    "drafts_generated": 9,
    "drafts_suppressed_low_score": 0,
    "fact_validator_passed": 9,
    "fact_validator_rejected": 0,
    "packages_by_type": {
      "directory_package": 4,
      "github_pr": 2,
      "publication_pitch": 3
    }
  },
  "outbox_and_telegram_metrics": {
    "total_messages_enqueued": 10,
    "dry_run_simulated": 10,
    "accepted_by_telegram": 0,
    "delivery_unknown": 0,
    "retry_pending": 0,
    "failed": 0,
    "stale_leases_recovered": 0
  },
  "business_and_placement_metrics": {
    "confirmed_live_backlinks": 4,
    "dofollow_backlinks": 4,
    "nofollow_backlinks": 0,
    "ugc_backlinks": 0,
    "owner_approved_pending_submission": 2,
    "submitted_pending_editorial_review": 1,
    "rejected_by_owner": 0,
    "link_retention_30_days_pct": 100.0,
    "link_retention_90_days_pct": 100.0
  }
}
```

---

## 3. Executive Markdown Digest Schema (`backlink_intelligence_YYYY-MM-DD.md`)

```markdown
# 🧠 AI Tool Gems Autonomous Backlink Intelligence Daily Report
**Cycle Run:** `2026-11-15 06:22:57 UTC`  
**Pipeline Mode:** `REPORT_ONLY` | **Kill-Switch:** `SAFE HOLD (Autonomous outreach disabled)`  

## 1. Executive Summary
- **Confirmed Live Backlinks:** `4` (100% verified via HTML DOM parser)
- **Newly Discovered Clean Opportunities:** `9`
- **Publication-Ready Drafts Generated:** `9` (All verified against `verified_facts.yml`)
- **Spam / Quarantined Filtered:** `1`

## 2. High-Priority Draft Packages Ready for Owner Review
| Domain | Type | Score | Draft ID | Draft Hash | Action Status |
|---|---|---|---|---|---|
| `dev.to` | `tech_publication` | **100** | `draft_pub_520bbcf3` | `4159d0effe66fc08` | `pending_owner_review` |
| `hashnode.com` | `tech_publication` | **100** | `draft_pub_c723f7ba` | `69a66089ea1ac1a8` | `pending_owner_review` |
| `saashub.com` | `directory_class1` | **92** | `draft_dir_29593805` | `cb06569adb426665` | `pending_owner_review` |

## 3. Notification Dispatch Telemetry
- Total Outbox Items Processed: `10`
- Telegram Simulation (Dry-Run): `10` (Zero external network calls made)
- Delivery Failures: `0`

## 4. Operational Safety Verification
- Grounded Truth: `verified_facts.yml` enforced; PKR pricing and verified domestic payment rails only.
- External Outreach: Strictly owner-operated; zero autonomous form submissions.
```
