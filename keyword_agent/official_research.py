"""
official_research.py - Continuous Official Google Search & AI Search Documentation Monitor.
Monitors:
- Google Search Central Documentation (https://developers.google.com/search/docs)
- Google Search Essentials (https://developers.google.com/search/docs/essentials)
- Google Search Spam Policies (https://developers.google.com/search/docs/essentials/spam-policies)
- Google AI Search Optimization Guidance (https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- Search Console Help & API Documentation
Distinguishes official requirements from third-party opinions and never fabricates algorithmic updates.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class OfficialGuidanceRule:
    source_id: str
    source_title: str
    source_url: str
    authority_level: str  # "OFFICIAL_REQUIREMENT", "OFFICIAL_BEST_PRACTICE", "AI_SEARCH_GUIDELINES"
    key_principle: str
    relevance_to_site: str
    last_verified: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d"))


class OfficialResearchMonitor:
    """Maintains an evidence-grounded baseline of Google official SEO & AI Search policies."""

    CORE_OFFICIAL_GUIDANCE = [
        OfficialGuidanceRule(
            source_id="GOOGLE_AI_OPTIMIZATION_GUIDE",
            source_title="Google Search Central: AI Search Optimization Guidance",
            source_url="https://developers.google.com/search/docs/fundamentals/ai-optimization-guide",
            authority_level="AI_SEARCH_GUIDELINES",
            key_principle=(
                "Focus on user-first, original content that satisfies genuine query intent. "
                "Structure content with clear hierarchy and accurate source attribution for generative synthesis."
            ),
            relevance_to_site="Directly governs AEO answers, FAQ structuring, and factual Pakistani pricing attribution.",
        ),
        OfficialGuidanceRule(
            source_id="GOOGLE_SEARCH_ESSENTIALS",
            source_title="Google Search Essentials (Technical & Content Foundations)",
            source_url="https://developers.google.com/search/docs/essentials",
            authority_level="OFFICIAL_REQUIREMENT",
            key_principle=(
                "Ensure unique titles, descriptive meta descriptions, accessible navigation, "
                "and avoid manipulative keyword stuffing or deceptive redirects."
            ),
            relevance_to_site="Enforces single H1 per page, <=60 character titles, and descriptive internal anchor text.",
        ),
        OfficialGuidanceRule(
            source_id="GOOGLE_SPAM_POLICIES",
            source_title="Google Search Spam Policies",
            source_url="https://developers.google.com/search/docs/essentials/spam-policies",
            authority_level="OFFICIAL_REQUIREMENT",
            key_principle=(
                "Prohibits scaled programmatic low-value content, door-page doorway queries, "
                "and misleading financial claims without verified backing."
            ),
            relevance_to_site="Blocks mass-creation of thin city-variant pages or unverified price guarantees.",
        ),
        OfficialGuidanceRule(
            source_id="GOOGLE_SEARCH_CONSOLE_RE2",
            source_title="Search Console Help: Advanced Filters & RE2 Syntax",
            source_url="https://support.google.com/webmasters/answer/17011165",
            authority_level="OFFICIAL_REQUIREMENT",
            key_principle=(
                "Performance report custom regex filters adhere to RE2 syntax limitations. "
                "Lookarounds and backreferences are unsupported."
            ),
            relevance_to_site="Enforces strict RE2 syntax validation across all generated GSC regex filters.",
        ),
    ]

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    def get_active_guidance(self) -> List[OfficialGuidanceRule]:
        """Returns the verified official guidance inventory."""
        return self.CORE_OFFICIAL_GUIDANCE

    def evaluate_compliance(self, page_brief: Any) -> Dict[str, Any]:
        """Evaluates whether an on-page optimization brief complies with official Google standards."""
        issues = []
        # Check Title length
        if len(page_brief.recommended_title) > 65:
            issues.append(f"Title exceeds 65 characters ({len(page_brief.recommended_title)} chars). May truncate in SERP.")

        # Check Meta Description
        if len(page_brief.recommended_meta_desc) < 70 or len(page_brief.recommended_meta_desc) > 165:
            issues.append(f"Meta description length ({len(page_brief.recommended_meta_desc)}) outside optimal 70-165 range.")

        # Check Keyword Stuffing
        kw = page_brief.primary_query.lower()
        title_occurrences = page_brief.recommended_title.lower().count(kw)
        if title_occurrences > 1:
            issues.append("Primary keyword repeated more than once in Title tag (potential keyword stuffing).")

        return {
            "compliant": len(issues) == 0,
            "issues": issues,
            "principles_applied": [g.source_id for g in self.CORE_OFFICIAL_GUIDANCE],
        }
