"""Owner-Only Telegram Approval and Command Handler for Backlink Agent.

Restricted strictly to configured TELEGRAM_OWNER_CHAT_ID.
Draft-only execution: approvals permit OWNER MANUAL SUBMISSIONS ONLY.
Automated outreach or public form submission is strictly prohibited.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .facts import get_verified_facts
from .models import ApprovalAction, Prospect
from .tracker import load_tracker_rows

APPROVAL_STORE_PATH = Path("seo-agent/data/backlink_approvals.json")
AUDIT_LOG_PATH = Path("seo-agent/data/backlink_approval_audit.jsonl")


def _secure_compare(a: str, b: str) -> bool:
    """Constant-time string comparison to prevent timing attacks."""
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def calculate_draft_hash(prospect: Dict[str, str]) -> str:
    """Calculates deterministic SHA256 hash of prospect draft to prevent stale approvals."""
    facts = get_verified_facts()
    content = (
        f"{prospect.get('prospect_domain', '')}|"
        f"{prospect.get('target_url', '')}|"
        f"{prospect.get('anchor_text', '')}|"
        f"{prospect.get('link_terms', '')}|"
        f"{facts.pricing_model}"
    )
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


class TelegramApprovalEngine:
    """Validates owner identity, processes commands, and maintains immutable audit logs."""

    def __init__(
        self,
        owner_chat_id: Optional[str] = None,
        owner_user_id: Optional[str] = None,
        store_path: Path = APPROVAL_STORE_PATH,
        audit_path: Path = AUDIT_LOG_PATH,
    ):
        self.owner_chat_id = (
            owner_chat_id
            if owner_chat_id is not None
            else os.environ.get("TELEGRAM_OWNER_CHAT_ID", "").strip()
        )
        self.owner_user_id = (
            owner_user_id
            if owner_user_id is not None
            else os.environ.get("TELEGRAM_OWNER_USER_ID", "").strip()
        )
        self.store_path = Path(store_path)
        self.audit_path = Path(audit_path)

    def is_authorized(self, chat_id: str, chat_type: str, user_id: Optional[str] = None) -> Tuple[bool, str]:
        """Strictly verifies if incoming Telegram message originates from the configured owner."""
        if chat_type != "private":
            return False, f"Unauthorized chat type '{chat_type}'. Commands allowed in private chat only."

        if not self.owner_chat_id:
            return False, "TELEGRAM_OWNER_CHAT_ID is not configured in environment."

        if not _secure_compare(str(chat_id), str(self.owner_chat_id)):
            return False, f"Unauthorized chat_id '{chat_id}'"

        if self.owner_user_id and user_id:
            if not _secure_compare(str(user_id), str(self.owner_user_id)):
                return False, f"Unauthorized user_id '{user_id}'"

        return True, "Authorized"

    def load_state(self) -> Dict[str, Any]:
        if not self.store_path.exists():
            return {"last_update_id": 0, "approvals": {}}
        try:
            return json.loads(self.store_path.read_text(encoding="utf-8"))
        except Exception:
            return {"last_update_id": 0, "approvals": {}}

    def save_state(self, state: Dict[str, Any]) -> None:
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        temp_file = self.store_path.with_suffix(".tmp")
        temp_file.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        temp_file.replace(self.store_path)

    def append_audit_event(self, action: ApprovalAction) -> None:
        self.audit_path.parent.mkdir(parents=True, exist_ok=True)
        with self.audit_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(action.to_dict()) + "\n")

    def handle_command(
        self,
        command_text: str,
        chat_id: str,
        chat_type: str,
        user_id: Optional[str] = None,
        update_id: int = 0,
    ) -> str:
        """Processes an administrative backlink command with owner authorization."""
        authorized, reason = self.is_authorized(chat_id, chat_type, user_id)
        if not authorized:
            return f"⛔ Access Denied: {reason}"

        parts = command_text.strip().split()
        cmd = parts[0].lower() if parts else ""

        rows = load_tracker_rows()

        if cmd == "/backlinks":
            return self._cmd_backlinks(rows)

        if cmd == "/backlink":
            if len(parts) < 2:
                return "Usage: /backlink <prospect_domain_or_row_number>"
            return self._cmd_backlink_detail(rows, parts[1])

        if cmd == "/approve":
            if len(parts) < 2:
                return "Usage: /approve <prospect_domain_or_row_number>"
            return self._cmd_approve(rows, parts[1], chat_id, user_id, update_id)

        if cmd == "/reject":
            if len(parts) < 3:
                return "Usage: /reject <prospect_domain_or_row_number> <reason>"
            reason_text = " ".join(parts[2:])
            return self._cmd_reject(rows, parts[1], reason_text, chat_id, user_id, update_id)

        if cmd == "/defer":
            if len(parts) < 3:
                return "Usage: /defer <prospect_domain_or_row_number> <date YYYY-MM-DD>"
            return self._cmd_defer(rows, parts[1], parts[2], chat_id, user_id, update_id)

        if cmd == "/backlink_report":
            return self._cmd_report(rows)

        return f"Unknown backlink command: {cmd}. Supported: /backlinks, /backlink, /approve, /reject, /defer, /backlink_report"

    def _find_prospect(self, rows: List[Dict[str, str]], target: str) -> Optional[Dict[str, str]]:
        target_lower = target.lower()
        if target.isdigit():
            idx = int(target)
            if 1 <= idx <= len(rows):
                return rows[idx - 1]
            return None
        for r in rows:
            if r.get("prospect_domain", "").lower() == target_lower:
                return r
        return None

    def _cmd_backlinks(self, rows: List[Dict[str, str]]) -> str:
        live = [r for r in rows if r.get("link_status") == "live"]
        pending = [r for r in rows if r.get("link_status") == "not_live" and r.get("action_status") != "rejected"]
        lines = [
            "🔗 AI Tool Gems Backlink Pipeline Summary",
            f"• Total Prospects: {len(rows)}",
            f"• Live Placements: {len(live)}",
            f"• Actionable Queue: {len(pending)}",
            "",
            "Top Actionable Prospects (Click link to submit):",
        ]
        for p in pending[:5]:
            url = p.get('prospect_url') or p.get('source_page') or 'https://aitoolgems.tech/'
            lines.append(f"• [{p.get('relevance')}/100] {p.get('prospect_domain')} ({p.get('action_status')})\n  👉 Submit: {url}")
        lines.append("\nUse /backlink <domain> for full review.")
        return "\n".join(lines)

    def _cmd_backlink_detail(self, rows: List[Dict[str, str]], target: str) -> str:
        p = self._find_prospect(rows, target)
        if not p:
            return f"Prospect '{target}' not found in tracker."
        d_hash = calculate_draft_hash(p)
        url = p.get('prospect_url') or p.get('source_page') or 'https://aitoolgems.tech/'
        lines = [
            f"📋 Prospect: {p.get('prospect_domain')}",
            f"👉 Submit Link: {url}",
            f"• Site Type: {p.get('site_type')}",
            f"• Score: {p.get('relevance')}/100",
            f"• Eligibility: {p.get('eligibility')}",
            f"• Link Terms: {p.get('link_terms')}",
            f"• Target URL: {p.get('target_url')}",
            f"• Anchor Text: {p.get('anchor_text')}",
            f"• Action Status: {p.get('action_status')}",
            f"• Link Status: {p.get('link_status')}",
            f"• Draft Hash: {d_hash}",
            f"• Existing Evidence: {p.get('evidence')}",
            "",
            "Actions:",
            f"/approve {p.get('prospect_domain')}",
            f"/reject {p.get('prospect_domain')} <reason>",
        ]
        return "\n".join(lines)

    def _cmd_approve(
        self,
        rows: List[Dict[str, str]],
        target: str,
        chat_id: str,
        user_id: Optional[str],
        update_id: int,
    ) -> str:
        p = self._find_prospect(rows, target)
        if not p:
            return f"Prospect '{target}' not found."
        domain = p.get("prospect_domain", "")
        d_hash = calculate_draft_hash(p)

        state = self.load_state()
        existing = state.get("approvals", {}).get(domain)

        # Idempotency check
        if existing and existing.get("draft_hash") == d_hash and existing.get("action") == "approved":
            return (
                f"✅ Already Approved: {domain}\n"
                f"• Approved At: {existing.get('timestamp_pkt')}\n"
                f"• Draft Hash: {d_hash}\n"
                "⚠️ Note: Automated outreach is disabled. Owner must perform manual submission."
            )

        now_pkt = datetime.now(timezone.utc).isoformat()
        action = ApprovalAction(
            prospect_id=domain,
            action="approved",
            actor_chat_id=chat_id,
            actor_user_id=user_id,
            timestamp_pkt=now_pkt,
            draft_hash=d_hash,
            previous_status=p.get("action_status", ""),
            new_status="owner_approved_for_manual_submission",
            update_id=update_id,
        )

        state.setdefault("approvals", {})[domain] = action.to_dict()
        state["last_update_id"] = max(state.get("last_update_id", 0), update_id)
        self.save_state(state)
        self.append_audit_event(action)

        return (
            f"✅ Approved for Manual Submission: {domain}\n"
            f"• Target URL: {p.get('target_url')}\n"
            f"• Anchor: {p.get('anchor_text')}\n"
            f"• Content Hash: {d_hash}\n"
            "🛡️ Guardrail: No automated forms or outreach sent. Submission is owner-operated."
        )

    def _cmd_reject(
        self,
        rows: List[Dict[str, str]],
        target: str,
        reason: str,
        chat_id: str,
        user_id: Optional[str],
        update_id: int,
    ) -> str:
        p = self._find_prospect(rows, target)
        if not p:
            return f"Prospect '{target}' not found."
        domain = p.get("prospect_domain", "")
        d_hash = calculate_draft_hash(p)

        now_pkt = datetime.now(timezone.utc).isoformat()
        action = ApprovalAction(
            prospect_id=domain,
            action="rejected",
            actor_chat_id=chat_id,
            actor_user_id=user_id,
            timestamp_pkt=now_pkt,
            draft_hash=d_hash,
            previous_status=p.get("action_status", ""),
            new_status="rejected",
            reason=reason,
            update_id=update_id,
        )

        state = self.load_state()
        state.setdefault("approvals", {})[domain] = action.to_dict()
        state["last_update_id"] = max(state.get("last_update_id", 0), update_id)
        self.save_state(state)
        self.append_audit_event(action)

        return f"❌ Rejected {domain}: {reason}"

    def _cmd_defer(
        self,
        rows: List[Dict[str, str]],
        target: str,
        date_str: str,
        chat_id: str,
        user_id: Optional[str],
        update_id: int,
    ) -> str:
        p = self._find_prospect(rows, target)
        if not p:
            return f"Prospect '{target}' not found."
        domain = p.get("prospect_domain", "")
        d_hash = calculate_draft_hash(p)

        now_pkt = datetime.now(timezone.utc).isoformat()
        action = ApprovalAction(
            prospect_id=domain,
            action="deferred",
            actor_chat_id=chat_id,
            actor_user_id=user_id,
            timestamp_pkt=now_pkt,
            draft_hash=d_hash,
            previous_status=p.get("action_status", ""),
            new_status=f"deferred_until_{date_str}",
            reason=f"Deferred until {date_str}",
            update_id=update_id,
        )

        state = self.load_state()
        state.setdefault("approvals", {})[domain] = action.to_dict()
        state["last_update_id"] = max(state.get("last_update_id", 0), update_id)
        self.save_state(state)
        self.append_audit_event(action)

        return f"⏳ Deferred {domain} until {date_str}."

    def _cmd_report(self, rows: List[Dict[str, str]]) -> str:
        live = [r for r in rows if r.get("link_status") == "live"]
        return (
            "📊 Backlink Agent Status Report\n"
            f"• Mode: REPORT_ONLY (Kill Switch: ACTIVE)\n"
            f"• Tracked Prospects: {len(rows)}\n"
            f"• Confirmed Placements: {len(live)}\n"
            "• Manual Submissions: Allowed only via owner review\n"
            "• Auto Outreach: DISABLED"
        )
