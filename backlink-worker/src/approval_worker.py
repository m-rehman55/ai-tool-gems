"""Telegram Webhook & Approval Handler for Cloudflare Backlink Agent Worker.

Processes incoming Telegram updates at POST /telegram/webhook.
Strictly validates owner identity against TELEGRAM_OWNER_CHAT_ID.
Draft-only execution: approvals update D1 state for owner manual outreach only.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import hmac
import json
from typing import Any, Dict, Optional, Tuple

from .d1_adapter import D1Adapter


def secure_compare(a: str, b: str) -> bool:
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


class WorkerApprovalEngine:
    """Processes webhook commands and maintains state in Cloudflare D1."""

    def __init__(self, d1: D1Adapter, owner_chat_id: str, owner_user_id: Optional[str] = None):
        self.d1 = d1
        self.owner_chat_id = owner_chat_id.strip() if owner_chat_id else ""
        self.owner_user_id = owner_user_id.strip() if owner_user_id else ""

    def is_authorized(self, chat_id: str, chat_type: str, user_id: Optional[str] = None) -> Tuple[bool, str]:
        if chat_type != "private":
            return False, f"Unauthorized chat type '{chat_type}'. Commands allowed in private chat only."
        if not self.owner_chat_id:
            return False, "TELEGRAM_OWNER_CHAT_ID is not configured in worker environment."
        if not secure_compare(str(chat_id), str(self.owner_chat_id)):
            return False, f"Unauthorized chat_id '{chat_id}'"
        if self.owner_user_id and user_id:
            if not secure_compare(str(user_id), str(self.owner_user_id)):
                return False, f"Unauthorized user_id '{user_id}'"
        return True, "Authorized"

    async def handle_update(self, update: Dict[str, Any]) -> str:
        message = update.get("message") or {}
        chat = message.get("chat") or {}
        from_user = message.get("from") or {}
        chat_id = str(chat.get("id", ""))
        chat_type = str(chat.get("type", ""))
        user_id = str(from_user.get("id")) if from_user else None
        text = str(message.get("text") or "").strip()
        update_id = int(update.get("update_id", 0))

        authorized, reason = self.is_authorized(chat_id, chat_type, user_id)
        if not authorized:
            return f"⛔ Access Denied: {reason}"

        parts = text.split()
        cmd = parts[0].lower() if parts else ""

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
            await self.d1.execute_mutation(
                "UPDATE prospects SET action_status = 'owner_approved_for_manual_submission', updated_at = ? WHERE id = ?",
                (now_utc, p.get("id")),
            )
            await self.d1.record_audit_event(
                event_type="prospect_approved",
                actor=f"telegram:{chat_id}",
                entity_id=p.get("id"),
                payload={"action": "approve", "update_id": update_id, "timestamp": now_utc},
            )
            return (
                f"✅ Approved for Manual Submission: {p.get('prospect_domain')}\n"
                f"• Target URL: {p.get('target_url')}\n"
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
