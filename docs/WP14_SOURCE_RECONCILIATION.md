# WP14 Source Reconciliation & Architecture Review
**Document Version:** 1.0.0  
**Date:** 2026-11-15  
**Branch:** `feat/backlink-agent-critical-fixes`  
**Base Commit:** `1a61de1`  
**Status:** Approved & Implemented  

---

## 1. Executive Summary

This document reconciles all source modules introduced in WP13, addresses feedback from the architectural review, documents defect corrections, and establishes the production-grade reliability architecture for WP14.

---

## 2. File & Module Inventory

| Module / Path | Responsibilities & Functions | Test Coverage |
|---|---|---|
| `backlink_agent/prospect_discovery/` | Multi-channel prospect discovery across curated directories, GitHub Awesome lists, competitor gap profiles, and technical publications. | 9 unit tests in `test_prospect_discovery.py` |
| `backlink_agent/prospect_discovery/competitor_gap_discovery.py` | Ingests referring domain records, filters toxic PBN patterns, matches candidate gaps. | Tested in `test_toxic_pbn_filter_blocks_spam_farms` |
| `backlink_agent/evidence_scoring/` | 100-point 5-dimension opportunity scoring engine (Relevance, Editorial, Brand/Dataset Fit, Non-Spam, Indexability). | 6 unit tests in `test_evidence_scoring.py` |
| `backlink_agent/submission_drafter/` | Structured draft package generation for directories, GitHub PRs, and technical publication pitches citing `/prices/`. | 5 unit tests in `test_submission_drafter.py` |
| `backlink_agent/submission_drafter/drafting_engine.py` | Coordinates draft generators and enforces strict draft eligibility gates. | Tested in `test_submission_drafting_engine_routing_and_batch` |
| `backlink_agent/telegram_delivery/outbox_store.py` | Durable `OutboxStore` abstraction and `LocalSQLiteOutboxStore` implementation with WAL mode and atomic lease locking. | 8 unit tests in `test_outbox_store.py` |
| `backlink_agent/telegram_delivery/outbox_manager.py` | Outbox lifecycle manager handling chunking, token redaction, atomic claiming, and delivery status transitions. | 5 unit tests in `test_telegram_delivery.py` |
| `backlink_agent/pipeline.py` | End-to-end autonomous pipeline runner orchestrating Discovery -> Scoring -> Drafting -> Outbox -> Reports. | Unit tests in `test_pipeline.py` |
| `.github/workflows/backlink-intelligence-daily.yml` | GitHub Actions workflow for daily intelligence runs with `workflow_dispatch` validation. | Syntax & schema verified |

---

## 3. WP13 Defect Corrections & Hardening Actions

### 3.1 Domain Risk Classification: Blanket TLD Rejection Eliminated
- **Previous Behavior:** Regex `r"\.shop$"` and `r"\.site$"` blanket-rejected all candidate domains ending in `.shop` or `.site`.
- **Finding:** A `.shop` or `.site` TLD is not proof of a PBN. Legitimate e-commerce or technical resources on these TLDs were falsely quarantined.
- **WP14 Remediation:** Blanket TLD rejection was removed. Specific verified PBN keywords (`searchwins`, `solidlinkpro`, `serpvilo`, `backlinkblast`, `pbnfarm`, `cheapbacklinks`, `spammy-directory`) and keyword-TLD combinations (`(seo|pbn|blast|backlink)[a-z0-9-]*\.(shop|site|online|xyz)`) are used instead. Legitimate domains (`creativetools.shop`, `ai-portfolio.site`) pass cleanly.

### 3.2 Draft Eligibility Gate Hardening
- **Previous Behavior:** Drafting engine checked only `opp.action_recommendation == "draft_ready"`.
- **Finding:** Risk of silent draft generation for non-qualified prospects if action was incorrectly set.
- **WP14 Remediation:** Triple-check gate enforced:
  ```python
  if (
      opp.action_recommendation != "draft_ready"
      or opp.score.priority_tier != "high_priority"
      or opp.score.total_score < 75
  ):
      return None
  ```
  Prospects in Investigate ($55\text{--}74$) and Quarantine ($< 55$) tiers produce zero submission drafts.

### 3.3 Dry-Run vs. Live Telegram Delivery Semantics
- **Previous Behavior:** Dry-run marked messages as `"delivered"`, which could be conflated with external Telegram delivery.
- **WP14 Remediation:** Explicit distinct lifecycle statuses introduced:
  - `pending`: Newly enqueued.
  - `sending`: Worker lease claimed.
  - `dry_run_simulated`: Processed in dry-run mode (zero external HTTP calls).
  - `accepted_by_telegram`: Telegram API returned HTTP 200 with `message_id`.
  - `delivery_unknown`: Socket timeout during dispatch.
  - `retry_pending`: Recoverable failure scheduled for retry.
  - `failed`: Terminal failure exceeding `max_retries`.

### 3.4 Outbox Durability Across Ephemeral Environments
- **Previous Behavior:** Individual JSON files in `seo-agent/data/outbox/` were prone to concurrency race conditions and loss across cloud runner lifecycles.
- **WP14 Remediation:** Implemented `LocalSQLiteOutboxStore` with WAL mode, row-level lease locking (`locked_by`, `locked_at`), atomic claim transactions (`BEGIN IMMEDIATE`), and crash recovery sweeps.

---

## 4. Verification Evidence

- Total Unit Tests: **77 / 77 passing** in `backlink_agent/tests/`.
- Workspace Total: **350 / 350 passing** across all suites.
- Zero regressions in existing verifier, SSRF guard, tracker, or approval handlers.
