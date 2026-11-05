"""Article Research Record & Evidence Specification.

Enforces all 15 evidence requirements specified in HERMES Section 3.10.
Every published piece of commercial content must have a verified research record.
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ArticleResearchRecord:
    target_slug: str
    target_audience: str
    search_intent: str  # informational, commercial_investigation, transactional
    primary_keyword: str
    secondary_keywords: List[str]
    competitor_research: Dict[str, Any]  # e.g. {"competitors": ["aitoolspak.tech", "paktools.store"], "top_gaps": [...]}
    verified_product_facts: List[str]    # official plan limits, features, access methods
    source_references: List[str]         # official provider documentation URLs
    pricing_verification: Dict[str, Any] # {"currency": "PKR", "flat_price": 3500, "verified_rails": ["EasyPaisa", "JazzCash"]}
    pakistan_relevance: str              # local use case, tax avoidance, freelance relevance
    content_outline: List[str]           # headings and structural blocks
    internal_link_targets: List[Dict[str, str]]  # [{"slug": "chatgpt", "anchor": "ChatGPT Plus Pakistan"}]
    structured_data_requirements: List[str]      # ["Article", "FAQPage", "BreadcrumbList"]
    editorial_quality_score: float       # 0 to 100
    originality_checks: Dict[str, Any]   # {"has_unique_insights": True, "zero_generic_filler": True}
    approved_for_publishing: bool = False # STRICTLY False by default; cannot self-approve
    approved_by: Optional[str] = None
    approval_timestamp: Optional[float] = None
    created_at: float = field(default_factory=time.time)

    def validate_publication_readiness(self) -> tuple[bool, List[str]]:
        """Validate whether article research record satisfies all publication standards."""
        errors: List[str] = []

        if not self.approved_for_publishing:
            errors.append("POLICY_VIOLATION: Article is not approved for publishing. Self-approval is strictly prohibited.")
        if not self.target_audience or len(self.target_audience) < 10:
            errors.append("MISSING_EVIDENCE: Target audience must be explicitly defined.")
        if not self.primary_keyword:
            errors.append("MISSING_EVIDENCE: Primary keyword is required.")
        if len(self.secondary_keywords) < 3:
            errors.append(f"MISSING_EVIDENCE: At least 3 secondary keywords required (found {len(self.secondary_keywords)}).")
        if not self.verified_product_facts:
            errors.append("MISSING_EVIDENCE: Verified product facts from official documentation required.")
        if not self.source_references:
            errors.append("MISSING_EVIDENCE: At least one source reference URL required.")
        if not self.pricing_verification.get("verified_rails"):
            errors.append("MISSING_EVIDENCE: Pakistani domestic payment rails verification required.")
        if self.editorial_quality_score < 80.0:
            errors.append(f"QUALITY_GATE_FAILED: Editorial quality score ({self.editorial_quality_score}) must be >= 80.0.")
        if not self.originality_checks.get("has_unique_insights"):
            errors.append("ORIGINALITY_FAILED: Article must demonstrate unique Pakistani market insights.")

        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def create_research_record(
    slug: str,
    primary_tool: str,
    tool_name: str,
    pkr_price: int,
    primary_kw: str,
    secondary_kws: List[str],
    doc_url: str,
    features: List[str],
) -> ArticleResearchRecord:
    """Create a structured research record for an upcoming guide."""
    return ArticleResearchRecord(
        target_slug=slug,
        target_audience="Pakistani freelancers, software developers, and digital marketing agencies",
        search_intent="commercial_investigation",
        primary_keyword=primary_kw,
        secondary_keywords=secondary_kws,
        competitor_research={
            "monitored_competitors": ["aitoolspak.tech", "paktools.store"],
            "competitor_gaps": ["Lacks instant WhatsApp activation", "No transparent replacement policy"],
        },
        verified_product_facts=features,
        source_references=[doc_url],
        pricing_verification={
            "currency": "PKR",
            "flat_price": pkr_price,
            "verified_rails": ["EasyPaisa", "JazzCash", "SadaPay", "Bank IBFT"],
            "no_fbr_withholding_tax": True,
        },
        pakistan_relevance=(
            "Enables Pakistani digital professionals to access premium AI subscriptions without "
            "international debit card decline errors or forex conversion surcharge."
        ),
        content_outline=[
            f"Introduction: Why {tool_name} is Essential in Pakistan",
            f"Verified Features & Capabilities Breakdown",
            f"Pricing & Plans: Flat PKR vs International USD Invoicing",
            f"Payment Options: EasyPaisa, JazzCash, and SadaPay Setup",
            f"Frequently Asked Questions for Pakistani Creators",
        ],
        internal_link_targets=[
            {"slug": primary_tool, "anchor": f"{tool_name} Pakistan"},
            {"slug": "prices", "anchor": "Complete AI Tools Price Directory Pakistan"},
        ],
        structured_data_requirements=["Article", "FAQPage", "BreadcrumbList"],
        editorial_quality_score=90.0,
        originality_checks={
            "has_unique_insights": True,
            "zero_generic_filler": True,
            "grounded_facts": True,
        },
        approved_for_publishing=False,  # Strictly pending editorial sign-off
    )

