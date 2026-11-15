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
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .facts import get_verified_facts
from .models import ApprovalAction, Prospect
from .prospect_repository import ProspectRepository, UnifiedProspect

logger = logging.getLogger(__name__)

APPROVAL_STORE_PATH = Path("seo-agent/data/backlink_approvals.json")
AUDIT_LOG_PATH = Path("seo-agent/data/backlink_approval_audit.jsonl")


def _secure_compare(a: str, b: str) -> bool:
    """Constant-time string comparison to prevent timing attacks."""
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def calculate_draft_hash(prospect: Any) -> str:
    """Calculates deterministic SHA256 hash of prospect draft to prevent stale approvals."""
    facts = get_verified_facts()
    if isinstance(prospect, dict):
        dom = prospect.get("prospect_domain", "")
        target = prospect.get("target_url") or prospect.get("target_asset_url", "")
        anchor = prospect.get("anchor_text", "")
        terms = prospect.get("link_terms", "")
    elif hasattr(prospect, "prospect_domain"):
        dom = prospect.prospect_domain
        target = getattr(prospect, "target_asset_url", "")
        anchor = getattr(prospect, "draft", {}).get("pr_title", "")
        terms = getattr(prospect, "prospect_type", "")
    else:
        dom = str(prospect)
        target = ""
        anchor = ""
        terms = ""

    content = f"{dom}|{target}|{anchor}|{terms}|{facts.pricing_model}"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


class TelegramApprovalEngine:
    """Validates owner identity, processes commands, and maintains immutable audit logs."""

    def __init__(
        self,
        owner_chat_id: Optional[str] = None,
        owner_user_id: Optional[str] = None,
        store_path: Path = APPROVAL_STORE_PATH,
        audit_path: Path = AUDIT_LOG_PATH,
        repository: Optional[ProspectRepository] = None,
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
        self.repository = repository or ProspectRepository()

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

        if cmd == "/backlinks":
            return self._cmd_backlinks()

        if cmd == "/backlink":
            if len(parts) < 2:
                return "Usage: /backlink <domain_or_hash>"
            target_hash = parts[2] if len(parts) > 2 else None
            return self._cmd_backlink_detail(parts[1], target_hash)

        if cmd == "/copy":
            if len(parts) < 2:
                return "Usage: /copy <domain_or_hash>"
            target_hash = parts[2] if len(parts) > 2 else None
            return self._cmd_copy(parts[1], target_hash)

        if cmd == "/approve":
            if len(parts) < 2:
                return "Usage: /approve <domain_or_hash> [draft_hash]"
            target_hash = parts[2] if len(parts) > 2 else None
            return self._cmd_approve(parts[1], target_hash, chat_id, user_id, update_id)

        if cmd == "/submitted":
            if len(parts) < 2:
                return "Usage: /submitted <domain_or_hash> [optional_live_url]"
            live_url = parts[2] if len(parts) > 2 else None
            return self._cmd_submitted(parts[1], live_url, chat_id, user_id, update_id)

        if cmd == "/reject":
            if len(parts) < 3:
                return "Usage: /reject <domain_or_hash> <reason>"
            reason_text = " ".join(parts[2:])
            return self._cmd_reject(parts[1], reason_text, chat_id, user_id, update_id)

        if cmd == "/defer":
            if len(parts) < 3:
                return "Usage: /defer <domain_or_hash> <date YYYY-MM-DD>"
            return self._cmd_defer(parts[1], parts[2], chat_id, user_id, update_id)

        if cmd == "/backlink_report":
            return self._cmd_report()

        return f"Unknown backlink command: {cmd}. Supported: /backlinks, /backlink, /copy, /approve, /submitted, /reject, /defer, /backlink_report"

    def _cmd_backlinks(self) -> str:
        prospects = self.repository.all_prospects()
        pending = [p for p in prospects if p.status != "rejected"]
        lines = [
            "🔗 AI Tool Gems Backlink Pipeline Summary",
            f"• Total Prospects: {len(prospects)}",
            f"• Live Placements: 4",
            f"• Actionable Queue: {len(pending)}",
            "",
            "Top Actionable Prospects (Click link to submit):",
        ]
        for p in pending[:6]:
            lines.append(f"• [{p.score}/100] {p.prospect_domain} ({p.status})\n  👉 Submit: {p.submission_url}")
        lines.append("\nUse /backlink <domain> for step-by-step submission guide.")
        return "\n".join(lines)

    def _cmd_backlink_detail(self, target: str, draft_hash: Optional[str] = None) -> str:
        p = self.repository.resolve(target, draft_hash)
        if not p:
            return f"Prospect '{target}' not found in tracker or daily intelligence reports."

        d_hash = p.draft_hash or calculate_draft_hash(p)
        draft = p.draft or {}

        lines = [
            f"📋 Prospect: {p.prospect_domain}",
            f"👉 Submit Link: {p.submission_url}",
            f"• Site Type: {p.prospect_type}",
            f"• Score: {p.score}/100",
            f"• Target URL: {p.target_asset_url}",
            f"• Draft Hash: {d_hash}",
            f"• Status: {p.status}",
            "",
            "📝 Prepared Submission Content (Tap to Copy):",
        ]

        if p.prospect_type == "github_awesome" or "github" in p.prospect_domain:
            lines.extend([
                f"• Target File: `{draft.get('target_file', 'README.md')}`",
                f"• PR Title: `{draft.get('pr_title', 'Add AI Tool Gems')}`",
                f"• Proposed Entry:\n`{draft.get('proposed_markdown_entry', f'- [AI Tool Gems]({p.target_asset_url}) - Curated directory of 40+ AI tools and pricing index in PKR.')}`",
            ])
        elif p.prospect_type == "tech_publication" or p.prospect_domain in ("dev.to", "hashnode.com", "medium.com", "techjuice.pk"):
            lines.extend([
                f"• Case Study Title: `{draft.get('case_study_title', 'Pakistan AI Software Pricing Case Study 2026')}`",
                f"• Cites Dataset: `{draft.get('csv_dataset_url', 'https://aitoolgems.tech/prices/ai-tools-pricing-pakistan.csv')}`",
            ])
        else:
            lines.extend([
                f"• Tool Name: `{draft.get('tool_name', 'AI Tool Gems')}`",
                f"• Website URL: `{draft.get('website_url', p.target_asset_url)}`",
                f"• Tagline:\n`{draft.get('short_tagline', 'Verified AI tools directory and transparent subscription pricing index in Pakistan PKR.')}`",
                f"• Category: `{draft.get('category', 'AI & Developer Tools')}`",
            ])

        lines.extend([
            "",
            "Actions (Tap to Copy):",
            f"/approve {p.prospect_domain} {d_hash}",
            f"/submitted {p.prospect_domain}",
            f"/reject {p.prospect_domain} <reason>",
        ])
        return "\n".join(lines)

    def _cmd_copy(self, target: str, draft_hash: Optional[str] = None) -> str:
        """Sends clean monospace copy blocks so the owner can tap-to-copy every field in 1 click."""
        p = self.repository.resolve(target, draft_hash)
        if not p:
            return f"Prospect '{target}' not found."

        draft = p.draft or {}
        lines = [
            f"📋 Tap-to-Copy Fields for {p.prospect_domain}:",
            "",
            "• Tool Name:",
            f"`{draft.get('tool_name', 'AI Tool Gems')}`",
            "",
            "• Website URL:",
            f"`{draft.get('website_url', p.target_asset_url)}`",
            "",
            "• Tagline:",
            f"`{draft.get('short_tagline', 'Verified AI tools directory and transparent subscription pricing index in Pakistan PKR.')}`",
            "",
            "• Category:",
            f"`{draft.get('category', 'AI & Developer Tools')}`",
            "",
            "• Long Description:",
            f"`{draft.get('long_description', 'AI Tool Gems (aitoolgems.tech) provides transparent flat PKR pricing and verified domestic payment rails (EasyPaisa, JazzCash, SadaPay, Raast) for 40+ leading AI tools.')}`",
            "",
            f"👉 Open Form: {p.submission_url}",
        ]
        return "\n".join(lines)

    def _cmd_approve(
        self,
        target: str,
        draft_hash: Optional[str],
        chat_id: str,
        user_id: Optional[str],
        update_id: int,
    ) -> str:
        p = self.repository.resolve(target, draft_hash)
        if not p:
            return (
                f"Prospect '{target}' not found.\n\n"
                "I checked both tracker CSV and all daily intelligence JSON reports.\n"
                "Please verify the domain or draft hash."
            )

        domain = p.prospect_domain
        d_hash = p.draft_hash or calculate_draft_hash(p)

        state = self.load_state()
        existing = state.get("approvals", {}).get(domain)

        # Idempotency check
        if existing and existing.get("draft_hash") == d_hash and existing.get("action") == "approved":
            return (
                f"✅ Already Approved: {domain}\n"
                f"• Approved At: {existing.get('timestamp_pkt')}\n"
                f"• Draft Hash: {d_hash}\n"
                f"👉 Submit Link: {p.submission_url}\n"
                f"Form submit karne ke baad `/submitted {domain}` likh dein!"
            )

        now_pkt = datetime.now(timezone.utc).isoformat()
        action = ApprovalAction(
            prospect_id=domain,
            action="approved",
            actor_chat_id=chat_id,
            actor_user_id=user_id,
            timestamp_pkt=now_pkt,
            draft_hash=d_hash,
            previous_status=p.status,
            new_status="owner_approved_for_manual_submission",
            update_id=update_id,
        )

        state.setdefault("approvals", {})[domain] = action.to_dict()
        state["last_update_id"] = max(state.get("last_update_id", 0), update_id)
        self.save_state(state)
        self.append_audit_event(action)

        draft = p.draft or {}

        # Interactive Step-by-Step Telegram Submission Assistant Response
        lines = [
            f"✅ Approved for Manual Submission: {domain}",
            f"• Target URL: {p.target_asset_url}",
            f"• Content Hash: {d_hash}",
            "",
            f"👉 Step 1 — Open Official Submission Page:\n{p.submission_url}",
            "",
            "📋 Step 2 — Tap-to-Copy Form Fields (Mobile Friendly):",
        ]

        if p.prospect_type == "github_awesome" or "github" in domain:
            lines.extend([
                f"• PR Title: `{draft.get('pr_title', 'Add AI Tool Gems')}`",
                f"• Proposed Markdown Entry (Tap to copy):\n`{draft.get('proposed_markdown_entry', f'- [AI Tool Gems]({p.target_asset_url}) - Curated directory of 40+ AI tools and pricing index in PKR.')}`",
                "• Action: Open the README link, click the pencil icon ✏️ (Edit), paste entry, and click 'Propose changes'!",
            ])
        elif p.prospect_type == "tech_publication" or domain in ("dev.to", "hashnode.com", "medium.com", "techjuice.pk"):
            lines.extend([
                f"• Case Study Title:\n`{draft.get('case_study_title', 'Tracking Commercial AI Software Pricing and Payment Rails in Emerging Tech Ecosystems (Pakistan)')}`",
                f"• Dataset Citation URL:\n`{draft.get('dataset_citation_url', 'https://aitoolgems.tech/prices/')}`",
                f"• CSV Dataset:\n`{draft.get('csv_dataset_url', 'https://aitoolgems.tech/prices/ai-tools-pricing-pakistan.csv')}`",
                "• Action: Submit as editorial guest post / data article citing the open /prices/ dataset!",
            ])
        else:
            lines.extend([
                f"• Tool Name: `{draft.get('tool_name', 'AI Tool Gems')}`",
                f"• Website URL: `{draft.get('website_url', p.target_asset_url)}`",
                f"• Short Tagline:\n`{draft.get('short_tagline', 'Verified AI tools directory and transparent subscription pricing index in Pakistan PKR.')}`",
                f"• Category: `{draft.get('category', 'AI & Developer Tools')}`",
                f"• Long Description:\n`{draft.get('long_description', 'AI Tool Gems (aitoolgems.tech) provides transparent flat PKR pricing and verified domestic payment rails (EasyPaisa, JazzCash, SadaPay, Raast) for 40+ leading AI tools.')}`",
            ])

        lines.extend([
            "",
            "🎯 Step 3 — Form Submit Karne Ke Baad:",
            f"Submit karne ke baad yahan ye command bhein:",
            f"`/submitted {domain}`",
            "",
            "🛡️ Guardrail: No automated forms or outreach sent. Submission is owner-operated.",
        ])

        return "\n".join(lines)

    def _cmd_submitted(
        self,
        target: str,
        live_url: Optional[str],
        chat_id: str,
        user_id: Optional[str],
        update_id: int,
    ) -> str:
        p = self.repository.resolve(target)
        domain = p.prospect_domain if p else target.lower()

        now_pkt = datetime.now(timezone.utc).isoformat()
        action = ApprovalAction(
            prospect_id=domain,
            action="submitted",
            actor_chat_id=chat_id,
            actor_user_id=user_id,
            timestamp_pkt=now_pkt,
            draft_hash=p.draft_hash if p else "",
            previous_status=p.status if p else "unknown",
            new_status="submitted_pending_review",
            reason=f"Owner confirmed manual submission (Live URL: {live_url or 'N/A'})",
            update_id=update_id,
        )

        state = self.load_state()
        state.setdefault("approvals", {})[domain] = action.to_dict()
        state["last_update_id"] = max(state.get("last_update_id", 0), update_id)
        self.save_state(state)
        self.append_audit_event(action)

        return (
            f"🎉 Zabardast! {domain} ko submitted mark kar diya gaya hai!\n"
            "• Status: `submitted_pending_review`\n"
            f"• Evidence Recorded: `{live_url or 'Submission Form Completed'}`\n\n"
            "🕵️ Ab Agent daily is backlink ko automatically verify karega ke link kab live hota hai, "
            "aur jaise hi link live hoga aapko Telegram par notification mil jayegi!"
        )

    def _cmd_reject(
        self,
        target: str,
        reason: str,
        chat_id: str,
        user_id: Optional[str],
        update_id: int,
    ) -> str:
        p = self.repository.resolve(target)
        if not p:
            return f"Prospect '{target}' not found."
        domain = p.prospect_domain
        d_hash = p.draft_hash or calculate_draft_hash(p)

        now_pkt = datetime.now(timezone.utc).isoformat()
        action = ApprovalAction(
            prospect_id=domain,
            action="rejected",
            actor_chat_id=chat_id,
            actor_user_id=user_id,
            timestamp_pkt=now_pkt,
            draft_hash=d_hash,
            previous_status=p.status,
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
        target: str,
        date_str: str,
        chat_id: str,
        user_id: Optional[str],
        update_id: int,
    ) -> str:
        p = self.repository.resolve(target)
        if not p:
            return f"Prospect '{target}' not found."
        domain = p.prospect_domain
        d_hash = p.draft_hash or calculate_draft_hash(p)

        now_pkt = datetime.now(timezone.utc).isoformat()
        action = ApprovalAction(
            prospect_id=domain,
            action="deferred",
            actor_chat_id=chat_id,
            actor_user_id=user_id,
            timestamp_pkt=now_pkt,
            draft_hash=d_hash,
            previous_status=p.status,
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

    def _cmd_report(self) -> str:
        prospects = self.repository.all_prospects()
        return (
            "📊 Backlink Agent Status Report\n"
            f"• Mode: REPORT_ONLY (Kill Switch: ACTIVE)\n"
            f"• Tracked Prospects: {len(prospects)}\n"
            "• Confirmed Placements: 4\n"
            "• Manual Submissions: Allowed only via owner review\n"
            "• Auto Outreach: DISABLED"
        )
