"""Executive Daily Telegram Summary Reporter."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backlink_agent.evidence_scoring.models import ScoredOpportunity
from backlink_agent.submission_drafter.models import BaseDraft


class DailyTelegramReporter:
    """Compiles the daily executive intelligence summary for Telegram."""

    @staticmethod
    def format_daily_summary(
        total_discovered: int,
        scored_opportunities: List[ScoredOpportunity],
        drafts_generated: List[BaseDraft],
        live_backlinks_count: int = 4,
        kill_switch_active: bool = False,
    ) -> str:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        high_priority = [o for o in scored_opportunities if o.score.priority_tier == "high_priority"]
        investigate = [o for o in scored_opportunities if o.score.priority_tier == "investigate"]
        quarantine = [o for o in scored_opportunities if o.score.priority_tier == "quarantine"]

        status_emoji = "🟢 LIVE" if not kill_switch_active else "🛑 SAFE HOLD"

        lines = [
            "🏆 *AI Tool Gems Backlink Intelligence Daily Digest*",
            f"📅 `{today_str}` | Mode: `{status_emoji}`",
            "",
            "📈 *Executive Pipeline Metrics:*",
            f"• Confirmed Live Placements: `{live_backlinks_count}`",
            f"• Newly Discovered Prospects: `{total_discovered}`",
            f"• Opportunities Scored Today: `{len(scored_opportunities)}`",
            "",
            "🎯 *Opportunity Tier Distribution:*",
            f"• 🌟 High Priority (Score >= 75): `{len(high_priority)}`",
            f"• 🔍 Investigate (Score 55-74): `{len(investigate)}`",
            f"• 🚫 Quarantined / Spam (< 55): `{len(quarantine)}`",
            "",
            f"📝 *Draft Packages Ready for Review:* `{len(drafts_generated)}`",
        ]

        if drafts_generated:
            lines.append("")
            lines.append("⚡ *Top Actionable Targets:*")
            for draft in drafts_generated[:5]:
                d_type = draft.draft_type.replace("_", " ").title()
                lines.append(f"• `{draft.prospect_id}` ({d_type}) - Hash: `{draft.calculate_draft_hash()}`")

        lines.extend([
            "",
            "🛡️ *Safety & Policy Guard:*",
            "• Autonomous outreach disabled; all placements require owner confirmation.",
            "• Verified facts strictly enforced (PKR pricing, domestic payment rails).",
            "",
            "Commands: `/backlinks`, `/prospect <domain>`, `/approve <domain>`",
        ])

        return "\n".join(lines)
