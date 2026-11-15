# WP14 Telegram Delivery & Approval Acceptance Specification
**Document Version:** 1.0.0  
**Date:** 2026-11-15  
**Branch:** `feat/backlink-agent-critical-fixes`  
**Status:** Approved & Enforced  

---

## 1. Scope & Objective

This document defines the strict acceptance criteria, security gates, and validation semantics for Telegram notifications, operator callbacks, and approval workflows in the HERMES Autonomous Backlink Operating System.

---

## 2. Notification Security Constraints

1. **Authentication Gate:**
   - Inbound webhook calls to Cloudflare Edge require `X-Telegram-Bot-Api-Secret-Token` matching secret `TELEGRAM_WEBHOOK_SECRET` via constant-time comparison.
   - Missing or non-matching tokens immediately return `401 Unauthorized`.

2. **Sender Authorization:**
   - Only private chat messages (`chat.type == "private"`) from the exact authorized owner user ID (`from.id == TELEGRAM_OWNER_USER_ID`) are accepted.
   - Group chats, supergroups, channels, and messages from unauthorized user IDs (even if forwarding into owner chat) are rejected with `403 Forbidden`.

3. **Replay & Concurrency Protection:**
   - Atomic update ID claim table (`telegram_processed_updates`) prevents double-processing of duplicate webhooks.
   - Race conditions between concurrent workers are handled via SQLite `BEGIN IMMEDIATE` / D1 batch assertion gates.

4. **Sensitive Data Sanitization:**
   - All outgoing logs and error notifications redact bot tokens using `redact_bot_token()`, replacing `bot<token>` with `bot[REDACTED_TOKEN]`.

---

## 3. Approval Levels & Operational Boundaries

To prevent unauthorized automated actions, HERMES defines three distinct approval levels:

| Approval Level | Command / Callback | Allowed in WP14? | Operational Side Effect |
|---|---|---|---|
| **Level 1: Draft Approval** | `/approve <domain> <draft_hash>` | **YES** | Validates draft hash against prospect record, transitions status to `owner_approved_draft`. Generates copy-ready submission package for owner. |
| **Level 2: Manual Submission Approval** | `/submit_manual <domain>` | **YES** | Transitions prospect status to `owner_approved_for_manual_submission`. Emits checklist for manual browser submission by owner. |
| **Level 3: Autonomous External Submission** | N/A (Automated API/form POST) | **STRICTLY PROHIBITED** | **Disabled by Architecture & Safety Policy.** The agent never automatically submits web forms, emails external editors, or performs automated link placements. |

---

## 4. Callback Validation Protocol

When an operator taps an inline button or sends an approval command, the system validates the following before state mutation:

```
┌─────────────────────────────────────────────────────────────────┐
│                    INBOUND APPROVAL VALIDATION                  │
│                                                                 │
│  1. Check sender user ID == TELEGRAM_OWNER_USER_ID              │
│     ↳ FAIL: 403 Forbidden                                       │
│                                                                 │
│  2. Check chat.type == 'private'                                │
│     ↳ FAIL: 403 Group chats rejected                            │
│                                                                 │
│  3. Lookup prospect record by domain                            │
│     ↳ FAIL: 404 Prospect not found                              │
│                                                                 │
│  4. Revalidate SHA-256 Draft Hash                               │
│     ↳ Match stored draft_hash against inbound token             │
│     ↳ FAIL: 409 Conflict (Stale or modified draft rejected)     │
│                                                                 │
│  5. Check prospect current status eligible for approval         │
│     ↳ Must be 'active', 'pending_owner_review', or 'submitted'  │
│     ↳ FAIL: 409 Conflict (Already approved / quarantined)       │
│                                                                 │
│  6. Execute atomic state transition in D1 / SQLite              │
│     ↳ Enforce rowcount assertion table                          │
│     ↳ Record immutable audit event with millisecond timestamp   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Live Acceptance Verification Protocol

When configuring live Telegram notifications in production or staging, the operator must execute the following acceptance checklist:

- [x] **LAT-T01:** Verify invalid secret header yields `401 Unauthorized`.
- [x] **LAT-T02:** Verify non-owner user ID yields `403 Forbidden`.
- [x] **LAT-T03:** Verify valid owner command yields Markdown response summary.
- [x] **LAT-T04:** Verify re-posted update ID is idempotently skipped without mutation.
- [x] **LAT-T05:** Verify `/approve` command enforces deterministic draft hash revalidation.
- [x] **LAT-T06:** Verify dry-run mode writes to outbox without invoking external Telegram HTTP APIs.
- [x] **LAT-T07:** Verify network timeouts during dispatch transition message to `delivery_unknown` without crash.
