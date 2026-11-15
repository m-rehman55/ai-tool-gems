"""100-Point Multi-Factor Opportunity Scoring Engine."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from backlink_agent.prospect_discovery.models import DiscoveredProspect
from .models import ScoreBreakdown, ScoredOpportunity


class OpportunityScoringEngine:
    """Evaluates candidate backlink prospects across 5 core dimensions (0-100 total)."""

    def score_prospect(
        self,
        prospect: DiscoveredProspect,
        verification_evidence: Optional[Dict[str, Any]] = None,
    ) -> ScoredOpportunity:
        evidence = verification_evidence or {}
        rationale: List[str] = []
        risk_factors: List[str] = []

        # 1. Relevance (0 - 25 points)
        relevance_score = 15  # baseline
        p_type = prospect.prospect_type
        if p_type == "tech_publication":
            relevance_score = 25
            rationale.append("High topical alignment: technical case study citing pricing datasets")
        elif p_type in ("directory_class1", "directory_class2"):
            relevance_score = 22
            rationale.append("Strong directory match: curated AI software aggregator")
        elif p_type == "github_awesome":
            relevance_score = 20
            rationale.append("High relevance: curated developer repository list")
        elif p_type == "competitor_backlink":
            relevance_score = 18
            rationale.append("Proven competitor link context: existing industry citation")

        # 2. Editorial Quality (0 - 25 points)
        editorial_score = 18
        domain = prospect.prospect_domain.lower()
        if domain in ("github.com", "dev.to", "hashnode.com", "medium.com"):
            editorial_score = 25
            rationale.append("Established platform with strict human/community curation")
        elif "saashub.com" in domain or "startupnetwork.pk" in domain:
            editorial_score = 22
            rationale.append("Verified editorial review process on submissions")
        elif evidence.get("has_editorial_guidelines"):
            editorial_score = 20

        # 3. Brand & Dataset Fit (0 - 20 points)
        brand_score = 15
        target = prospect.target_asset_url or ""
        if "/prices/" in target or "pricing" in target:
            brand_score = 20
            rationale.append("Direct asset citation: targets machine-readable /prices/ index")
        elif p_type in ("directory_class1", "directory_class2"):
            brand_score = 18
            rationale.append("Clean commercial match: 40 tools catalog representation")

        # 4. Non-Spam & Non-Reciprocal Quality (0 - 15 points)
        spam_score = 15
        metadata = prospect.metadata or {}
        if metadata.get("pricing_policy") == "demands_reciprocal_link":
            spam_score = 0
            risk_factors.append("Demands reciprocal backlink (violates Google Webmaster Guidelines)")
        if metadata.get("pricing_policy") == "paid_only":
            spam_score = 2
            risk_factors.append("Requires paid link placement")
        if evidence.get("is_toxic"):
            spam_score = 0
            risk_factors.append("Suspected link farm / PBN footprint")

        # 5. Indexability & Authority (0 - 15 points)
        index_score = 12
        if domain in ("github.com", "dev.to", "hashnode.com", "saashub.com"):
            index_score = 15
            rationale.append("High domain authority (DA 70+) and guaranteed search engine indexing")
        elif evidence.get("is_noindex"):
            index_score = 0
            risk_factors.append("Source page has meta noindex tag")

        breakdown = ScoreBreakdown(
            relevance=relevance_score,
            editorial_quality=editorial_score,
            brand_dataset_fit=brand_score,
            non_spam_quality=spam_score,
            indexability=index_score,
        )

        priority = breakdown.priority_tier
        if priority == "high_priority":
            action = "draft_ready"
        elif priority == "investigate":
            action = "investigate"
        else:
            action = "quarantine"

        return ScoredOpportunity(
            prospect_id=prospect.prospect_id,
            prospect_domain=prospect.prospect_domain,
            source_page_url=prospect.source_page_url,
            prospect_type=prospect.prospect_type,
            target_asset_url=prospect.target_asset_url,
            score=breakdown,
            rationale=rationale,
            risk_factors=risk_factors,
            action_recommendation=action,
        )
