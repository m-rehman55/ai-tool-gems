"""Telegram Outcome Notification Formatter for Lifecycle Events."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


class OutcomeNotificationFormatter:
    """Formats actionable lifecycle event notifications for owner Telegram."""

    @staticmethod
    def format_submission_reminder(
        domain: str,
        prospect_id: str,
        draft_id: str,
        draft_hash: str,
        submission_url: str,
    ) -> str:
        lines = [
            f"🔔 *Manual Submission Action Required: {domain}*",
            f"• Prospect ID: `{prospect_id}`",
            f"• Draft ID: `{draft_id}`",
            f"• Verified Draft Hash: `{draft_hash}`",
            f"• Destination URL: `{submission_url}`",
            "",
            "📝 *Next Step:*",
            "Please complete manual submission in browser. Once submitted, record proof via:",
            f"`/confirm_submitted {domain} <submission_ref>`",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_publication_verified(
        domain: str,
        prospect_id: str,
        publication_url: str,
        qualification: str,
        anchor_text: str,
        rel_tokens: List[str],
    ) -> str:
        rel_str = ", ".join(rel_tokens) if rel_tokens else "none (dofollow)"
        lines = [
            f"🎉 *Backlink Verified Live: {domain}*",
            f"• Page: `{publication_url}`",
            f"• Anchor Text: _{anchor_text}_",
            f"• Qualification: `{qualification.upper()}`",
            f"• Rel Attributes: `{rel_str}`",
            "• Search Engine Indexable: ✅ Yes",
            "",
            "📈 *Lifecycle State:* `BACKLINK_VERIFIED`",
            "Scheduled for automated 7-day retention verification.",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_retention_milestone(
        domain: str,
        days: int,
        publication_url: str,
        qualification: str,
    ) -> str:
        lines = [
            f"🏅 *Backlink Retention Milestone Reached: {domain}*",
            f"• Active Duration: *{days} Days Confirmed*",
            f"• Publication URL: `{publication_url}`",
            f"• Qualification: `{qualification}`",
            "",
            "✨ *Status:* Retained cleanly without modification or removal.",
        ]
        return "\n".join(lines)

    @staticmethod
    def format_link_alert(
        domain: str,
        alert_type: str,
        details: str,
        publication_url: str,
    ) -> str:
        lines = [
            f"⚠️ *Backlink Status Alert: {domain}*",
            f"• Event: *{alert_type.upper()}*",
            f"• Details: {details}",
            f"• Monitored URL: `{publication_url}`",
            "",
            "Action: Investigating change; previous verified state preserved in audit log.",
        ]
        return "\n".join(lines)
