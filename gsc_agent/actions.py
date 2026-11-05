"""
Controlled Execution Engine for GSC Agent.
Safely prepares and validates proposed optimizations (titles, meta descriptions,
headings, canonicals, sitemaps, structured data, content briefs).
Strictly prevents automatic deletion of indexed pages or unauthorized removal requests.
"""

from __future__ import annotations
import re
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from gsc_agent.opportunities import GSCOpportunity


@dataclass
class ProposedActionPlan:
    action_id: str
    target_url: str
    action_type: str
    file_path: Optional[str]
    proposed_changes: Dict[str, Any]
    approval_tier: str  # PULL_REQUEST_REQUIRED, HUMAN_EXPLICIT_REQUIRED
    validation_status: str  # VALIDATED, PENDING_TESTS, REJECTED
    notes: str = ""


class GSCActionExecutor:
    """Coordinates controlled generation of SEO patches and safeguards against destructive actions."""

    def __init__(self, base_dir: Optional[Path | str] = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent

    def prepare_title_and_meta_patch(
        self,
        target_html_path: Path | str,
        new_title: str,
        new_meta_description: str,
        target_url: str = ""
    ) -> ProposedActionPlan:
        """Prepares a non-destructive title and meta description modification."""
        path = Path(target_html_path)
        if not path.exists():
            return ProposedActionPlan(
                action_id="ERR-NO-FILE",
                target_url=target_url,
                action_type="TITLE_META_UPDATE",
                file_path=str(path),
                proposed_changes={},
                approval_tier="HUMAN_EXPLICIT_REQUIRED",
                validation_status="REJECTED",
                notes=f"File not found: {path}"
            )

        # Title & Meta length validation
        clean_title = new_title.strip()
        clean_meta = new_meta_description.strip()
        errors = []

        if not (20 <= len(clean_title) <= 70):
            errors.append(f"Title length ({len(clean_title)} chars) outside 20–70 bounds: '{clean_title}'")
        if not (70 <= len(clean_meta) <= 170):
            errors.append(f"Meta description length ({len(clean_meta)} chars) outside 70–170 bounds: '{clean_meta}'")

        # Pakistan policy validation: no foreign yen / japan tokens
        for forbidden in ["japan", "japanese", "tokyo", "jpy", "¥"]:
            if forbidden in clean_title.lower() or forbidden in clean_meta.lower():
                errors.append(f"Foreign scope violation: '{forbidden}' is prohibited.")

        status = "VALIDATED" if not errors else "REJECTED"

        return ProposedActionPlan(
            action_id=f"ACT-TITLE-{datetime.now(timezone.utc).strftime('%H%M%S')}",
            target_url=target_url,
            action_type="TITLE_META_UPDATE",
            file_path=str(path),
            proposed_changes={
                "new_title": clean_title,
                "new_meta_description": clean_meta,
            },
            approval_tier="PULL_REQUEST_REQUIRED",
            validation_status=status,
            notes="; ".join(errors) if errors else "Title and Meta Description meet all standards."
        )

    def prepare_content_brief(
        self,
        query: str,
        target_url: str,
        secondary_keywords: List[str],
        primary_tool: str
    ) -> Dict[str, Any]:
        """Generates an evidence-backed AEO/GEO editorial content brief."""
        return {
            "target_query": query,
            "target_url": target_url,
            "primary_tool": primary_tool,
            "target_audience": "Pakistani freelancers, developers, agencies, and digital creators",
            "market_rails": ["EasyPaisa", "JazzCash", "SadaPay", "Bank IBFT"],
            "currency": "PKR",
            "outline": [
                f"1. Executive Overview: What is {primary_tool.title()}?",
                f"2. Pakistan Availability, Pricing & Official Domestic Payment Methods",
                f"3. Feature Analysis: Private vs Shared vs Team Access",
                f"4. Step-by-Step Activation via WhatsApp Support",
                f"5. Frequently Asked Questions (Pricing, Warranty, Renewal)"
            ],
            "secondary_keywords": secondary_keywords,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    def request_temporary_url_removal(
        self,
        url: str,
        reason: str
    ) -> ProposedActionPlan:
        """
        STRICT SAFETY ENFORCEMENT:
        Search Console URL removals are temporary masking tools, not permanent deletions.
        This operation is permanently classified as CRITICAL_DEPLOY and BLOCKED_PENDING_APPROVAL.
        Never executed autonomously.
        """
        return ProposedActionPlan(
            action_id=f"REMOVAL-{datetime.now(timezone.utc).strftime('%H%M%S')}",
            target_url=url,
            action_type="SEARCH_CONSOLE_REMOVAL_REQUEST",
            file_path=None,
            proposed_changes={"url_to_remove": url, "reason": reason},
            approval_tier="HUMAN_EXPLICIT_REQUIRED",
            validation_status="PENDING_TESTS",
            notes="CRITICAL OPERATION: Requires dual human approval. Autonomous execution blocked by Safety Firewall."
        )
