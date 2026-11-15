"""Telegram Opportunity Card Formatter."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backlink_agent.evidence_scoring.models import ScoredOpportunity
from backlink_agent.submission_drafter.models import (
    BaseDraft,
    DirectorySubmissionDraft,
    GitHubAwesomePRDraft,
    PublicationPitchDraft,
)
from backlink_agent.telegram_utils import split_message_into_chunks


class OpportunityCardFormatter:
    """Formats high-priority backlink opportunities into concise, actionable Telegram cards."""

    @staticmethod
    def format_card(
        opp: ScoredOpportunity,
        draft: Optional[BaseDraft] = None,
        draft_hash: Optional[str] = None,
    ) -> str:
        domain = opp.prospect_domain
        p_type = opp.prospect_type
        score = opp.score
        d_hash = draft_hash or (draft.calculate_draft_hash() if draft else "N/A")

        # Type badge without brackets to prevent Telegram link syntax errors
        if "github" in p_type:
            icon = "🐙 GitHub Awesome"
        elif "pub" in p_type:
            icon = "📰 Tech Publication"
        else:
            icon = "📁 Curated Directory"

        tier_display = score.priority_tier.replace("_", " ").upper()

        lines: List[str] = [
            f"🎯 *New Backlink Opportunity: {domain}*",
            f"{icon} • `Score: {score.total_score}/100` (`{tier_display}`)",
            "",
            "📊 *Score Breakdown:*",
            f"• Relevance: `{score.relevance}/25`",
            f"• Editorial Quality: `{score.editorial_quality}/25`",
            f"• Brand & Dataset Fit: `{score.brand_dataset_fit}/20`",
            f"• Non-Spam Quality: `{score.non_spam_quality}/15`",
            f"• Indexability: `{score.indexability}/15`",
            "",
            f"👉 *Submit Link (Click to Open):*\n{opp.source_page_url}",
            f"🎯 *Target Asset:*\n{opp.target_asset_url}",
        ]

        if opp.rationale:
            lines.append("")
            lines.append("💡 *Rationale:*")
            for r in opp.rationale[:3]:
                clean_r = r.replace("_", " ")
                lines.append(f"• {clean_r}")

        if opp.risk_factors:
            lines.append("")
            lines.append("⚠️ *Risk Factors:*")
            for rf in opp.risk_factors:
                clean_rf = rf.replace("_", " ")
                lines.append(f"• {clean_rf}")

        if draft:
            lines.append("")
            lines.append("📝 *Generated Draft Package (Tap to Copy):*")
            lines.append(f"• Draft ID: `{draft.draft_id}`")
            lines.append(f"• Draft Hash: `{d_hash}`")
            if isinstance(draft, DirectorySubmissionDraft):
                lines.append(f"• Tool Name: `{draft.tool_name}`")
                lines.append(f"• Website URL: `{draft.website_url}`")
                lines.append(f"• Tagline:\n`{draft.short_tagline}`")
                lines.append(f"• Category: `{draft.category}`")
            elif isinstance(draft, GitHubAwesomePRDraft):
                lines.append(f"• Repository: `{draft.repository_name}`")
                lines.append(f"• PR Title:\n`{draft.pr_title}`")
                lines.append(f"• Entry:\n`{draft.proposed_markdown_entry}`")
            elif isinstance(draft, PublicationPitchDraft):
                lines.append(f"• Case Study:\n`{draft.case_study_title}`")
                lines.append(f"• Cites Dataset: `{draft.csv_dataset_url}`")

            lines.append("")
            lines.append("⚡ *One-Click Actions (Tap to Copy):*")
            lines.append(f"`/approve {domain} {d_hash}`")
            lines.append(f"`/reject {domain} reason`")
        else:
            lines.append("")
            safe_action = opp.action_recommendation.replace("_", " ")
            lines.append(f"ℹ️ _Draft generation deferred (Action: {safe_action})_")

        return "\n".join(lines)
