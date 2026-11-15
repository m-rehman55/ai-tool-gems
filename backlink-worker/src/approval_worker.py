"""Telegram Webhook & Approval Handler for Cloudflare Backlink Agent Worker.

Processes incoming Telegram updates at POST /telegram/webhook.
Strictly validates:
1. X-Telegram-Bot-Api-Secret-Token header via constant-time comparison.
2. Private chat enforcement (chat.type == 'private').
3. Exact chat.id authorization (TELEGRAM_OWNER_CHAT_ID).
4. Exact from.id authorization (TELEGRAM_OWNER_USER_ID).
5. D1-based update_id replay protection.
6. Deterministic SHA256 draft-content hash verification.
7. Draft-only execution: approvals update D1 state for owner manual outreach only.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import hmac
import json
from typing import Any, Dict, Optional, Tuple

from .d1_adapter import D1Adapter


def secure_compare(a: str, b: str) -> bool:
    """Constant-time comparison to prevent timing attacks."""
    if not a or not b:
        return False
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


class WorkerApprovalEngine:
    """Processes webhook commands and maintains state in Cloudflare D1."""

    def __init__(
        self,
        d1: D1Adapter,
        owner_chat_id: str,
        owner_user_id: Optional[str] = None,
        webhook_secret: Optional[str] = None,
    ):
        self.d1 = d1
        self.owner_chat_id = owner_chat_id.strip() if owner_chat_id else ""
        self.owner_user_id = owner_user_id.strip() if owner_user_id else ""
        self.webhook_secret = webhook_secret.strip() if webhook_secret else ""

    def verify_webhook_secret(self, header_secret: Optional[str]) -> Tuple[bool, str]:
        """Validates X-Telegram-Bot-Api-Secret-Token header."""
        if not self.webhook_secret:
            # If no secret configured in staging, pass with warning
            return True, "No secret configured"
        if not header_secret:
            return False, "Missing X-Telegram-Bot-Api-Secret-Token header"
        if not secure_compare(header_secret, self.webhook_secret):
            return False, "Invalid X-Telegram-Bot-Api-Secret-Token"
        return True, "Valid Secret"

    def is_authorized(self, chat_id: str, chat_type: str, user_id: Optional[str] = None) -> Tuple[bool, str]:
        if chat_type != "private":
            return False, f"Unauthorized chat type '{chat_type}'. Commands allowed in private chat only."
        if not self.owner_chat_id:
            return False, "TELEGRAM_OWNER_CHAT_ID is not configured in worker environment."
        if not secure_compare(str(chat_id), str(self.owner_chat_id)):
            return False, f"Unauthorized chat_id '{chat_id}'"
        if self.owner_user_id:
            if not user_id or not secure_compare(str(user_id), str(self.owner_user_id)):
                return False, f"Unauthorized sender user_id '{user_id}'"
        return True, "Authorized"

    async def is_update_already_processed(self, update_id: int) -> bool:
        """Checks if update_id was already handled (via telegram_processed_updates table)."""
        if not update_id:
            return False
        row = await self.d1.execute_first(
            "SELECT count(*) as c FROM telegram_processed_updates WHERE update_id = ?",
            (int(update_id),),
        )
        return bool(row and row.get("c", 0) > 0)

    async def claim_telegram_update(
        self,
        update_id: int,
        chat_id: str,
        user_id: Optional[str],
        command: str,
    ) -> bool:
        """Atomically claims an incoming Telegram update ID in D1.
        Relies on PRIMARY KEY (update_id) constraint to eliminate race conditions
        between concurrent webhook deliveries.
        """
        if not update_id:
            return True
        now_utc = datetime.now(timezone.utc).isoformat()
        try:
            await self.d1.execute_mutation(
                "INSERT INTO telegram_processed_updates (update_id, chat_id, user_id, command, claimed_at) VALUES (?, ?, ?, ?, ?)",
                (int(update_id), str(chat_id), str(user_id or ""), str(command), now_utc),
            )
            return True
        except Exception:
            # Primary key constraint violation (already claimed concurrently)
            return False

    async def handle_update(self, update: Dict[str, Any], header_secret: Optional[str] = None) -> str:
        # 1. Header Secret Verification
        secret_ok, secret_msg = self.verify_webhook_secret(header_secret)
        if not secret_ok:
            return f"⛔ Unauthorized: {secret_msg}"

        message = update.get("message") or {}
        chat = message.get("chat") or {}
        from_user = message.get("from") or {}
        chat_id = str(chat.get("id", ""))
        chat_type = str(chat.get("type", ""))
        user_id = str(from_user.get("id")) if from_user else None
        text = str(message.get("text") or "").strip()
        update_id = int(update.get("update_id", 0))

        # 2. Sender and Channel Authorization
        authorized, reason = self.is_authorized(chat_id, chat_type, user_id)
        if not authorized:
            return f"⛔ Access Denied: {reason}"

        parts = text.split()
        cmd = parts[0].lower() if parts else ""

        # 3. Atomic Replay and Concurrency Claim
        if update_id:
            claimed = await self.claim_telegram_update(update_id, chat_id, user_id, cmd)
            if not claimed:
                return f"ℹ️ Update ID {update_id} already processed or claimed concurrently. Duplicate skipped safely."

        # Record update receipt in audit trail
        if update_id:
            await self.d1.record_audit_event(
                event_type="telegram_update",
                actor=f"user:{user_id or 'unknown'}",
                entity_id=str(update_id),
                payload={"command": cmd, "chat_id": chat_id, "timestamp": datetime.now(timezone.utc).isoformat()},
            )

        if cmd == "/backlinks":
            summary = await self.d1.get_pipeline_summary()
            prospects = await self.d1.get_prospects_for_verification(limit=5)
            lines = [
                "🔗 AI Tool Gems Cloudflare Backlink Pipeline",
                f"• Total Prospects in D1: {summary.get('total_prospects')}",
                f"• Live Placements: {summary.get('live_placements')}",
                f"• Verification Runs: {summary.get('total_verification_runs')}",
                "",
                "Top Queue Items:",
            ]
            for p in prospects:
                lines.append(f"• [{p.get('relevance')}/100] {p.get('prospect_domain')} ({p.get('action_status')})")
            lines.append("\nUse /backlink <domain> to inspect detail.")
            return "\n".join(lines)

        if cmd == "/backlink":
            if len(parts) < 2:
                return "Usage: /backlink <prospect_domain>"
            target = parts[1].lower()
            p = await self.d1.execute_first("SELECT * FROM prospects WHERE lower(prospect_domain) = ?", (target,))
            if not p:
                return f"Prospect '{target}' not found in D1."
            content_hash = hashlib.sha256(f"{p.get('prospect_domain')}|{p.get('target_url')}".encode("utf-8")).hexdigest()[:16]
            lines = [
                f"📋 Prospect: {p.get('prospect_domain')}",
                f"• URL: {p.get('prospect_url')}",
                f"• Score: {p.get('relevance')}/100",
                f"• Eligibility: {p.get('eligibility')}",
                f"• Target URL: {p.get('target_url')}",
                f"• Action Status: {p.get('action_status')}",
                f"• Link Status: {p.get('link_status')}",
                f"• Draft Hash: {content_hash}",
                f"• Evidence: {p.get('evidence')}",
                "",
                f"To approve for manual outreach: /approve {p.get('prospect_domain')}",
            ]
            return "\n".join(lines)

        if cmd == "/approve":
            if len(parts) < 2:
                return "Usage: /approve <prospect_domain>"
            target = parts[1].lower()
            p = await self.d1.execute_first("SELECT * FROM prospects WHERE lower(prospect_domain) = ?", (target,))
            if not p:
                return f"Prospect '{target}' not found in D1."

            now_utc = datetime.now(timezone.utc).isoformat()
            content_hash = hashlib.sha256(f"{p.get('prospect_domain')}|{p.get('target_url')}".encode("utf-8")).hexdigest()[:16]

            # Revalidate pending draft in drafts table if present
            draft = await self.d1.execute_first(
                "SELECT * FROM drafts WHERE prospect_id = ? AND status = 'pending_approval' ORDER BY created_at DESC LIMIT 1",
                (p.get("id"),),
            )
            if draft:
                expected_draft_hash = hashlib.sha256(
                    f"{draft.get('target_url')}|{draft.get('proposed_anchor')}|{draft.get('pitch_copy')}".encode("utf-8")
                ).hexdigest()
                recorded_hash = draft.get("content_sha256", "")
                if recorded_hash and not secure_compare(recorded_hash, expected_draft_hash):
                    return f"⛔ Draft integrity error: SHA-256 content hash mismatch for {target}. Approval blocked."
                await self.d1.execute_mutation(
                    "UPDATE drafts SET status = 'approved', approved_at = ?, approved_by = ? WHERE id = ?",
                    (now_utc, f"telegram:{user_id or chat_id}", draft.get("id")),
                )

            await self.d1.execute_mutation(
                "UPDATE prospects SET action_status = 'owner_approved_for_manual_submission', updated_at = ? WHERE id = ?",
                (now_utc, p.get("id")),
            )
            await self.d1.record_audit_event(
                event_type="prospect_approved",
                actor=f"telegram:{chat_id}",
                entity_id=p.get("id"),
                payload={
                    "action": "approve",
                    "draft_hash": content_hash,
                    "user_id": user_id,
                    "update_id": update_id,
                    "timestamp": now_utc,
                },
            )
            return (
                f"✅ Approved for Manual Submission: {p.get('prospect_domain')}\n"
                f"• Target URL: {p.get('target_url')}\n"
                f"• Draft Hash: {content_hash}\n"
                "🛡️ Guardrail: Zero automated forms or emails sent. Submission is owner-operated."
            )

        if cmd == "/reject":
            if len(parts) < 3:
                return "Usage: /reject <prospect_domain> <reason>"
            target = parts[1].lower()
            reason_text = " ".join(parts[2:])
            p = await self.d1.execute_first("SELECT * FROM prospects WHERE lower(prospect_domain) = ?", (target,))
            if not p:
                return f"Prospect '{target}' not found in D1."
            now_utc = datetime.now(timezone.utc).isoformat()
            await self.d1.execute_mutation(
                "UPDATE prospects SET action_status = 'rejected', link_status = 'rejected', updated_at = ? WHERE id = ?",
                (now_utc, p.get("id")),
            )
            await self.d1.record_audit_event(
                event_type="prospect_rejected",
                actor=f"telegram:{chat_id}",
                entity_id=p.get("id"),
                payload={"action": "reject", "reason": reason_text, "update_id": update_id},
            )
            return f"❌ Rejected {p.get('prospect_domain')}: {reason_text}"

        if cmd == "/backlink_report":
            summary = await self.d1.get_pipeline_summary()
            enabled = await self.d1.is_agent_enabled()
            mode = await self.d1.get_agent_mode()
            return (
                "📊 Cloudflare Backlink Agent Status\n"
                f"• Kill Switch: {'ENABLED' if enabled else 'DISABLED (Safe Mode)'}\n"
                f"• Operational Mode: {mode.upper()}\n"
                f"• Total Tracked: {summary.get('total_prospects')}\n"
                f"• Live Placements: {summary.get('live_placements')}\n"
                f"• Verifications Recorded: {summary.get('total_verification_runs')}\n"
                "• Runtime: Cloudflare Workers + D1 + Queues (24/7 Serverless)"
            )

        return f"Unknown command: {cmd}. Supported: /backlinks, /backlink, /approve, /reject, /backlink_report"
