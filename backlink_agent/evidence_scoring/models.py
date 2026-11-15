"""Data models for Evidence Verification and Multi-Factor Opportunity Scoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class ScoreBreakdown:
    relevance: int = 0          # 0 - 25
    editorial_quality: int = 0  # 0 - 25
    brand_dataset_fit: int = 0  # 0 - 20
    non_spam_quality: int = 0   # 0 - 15
    indexability: int = 0       # 0 - 15

    @property
    def total_score(self) -> int:
        raw = (
            self.relevance
            + self.editorial_quality
            + self.brand_dataset_fit
            + self.non_spam_quality
            + self.indexability
        )
        return max(0, min(100, raw))

    @property
    def priority_tier(self) -> str:
        s = self.total_score
        if s >= 75:
            return "high_priority"  # Advance to draft
        elif s >= 55:
            return "investigate"    # Hold / manual review
        else:
            return "quarantine"     # Reject / spam quarantine

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relevance": self.relevance,
            "editorial_quality": self.editorial_quality,
            "brand_dataset_fit": self.brand_dataset_fit,
            "non_spam_quality": self.non_spam_quality,
            "indexability": self.indexability,
            "total_score": self.total_score,
            "priority_tier": self.priority_tier,
        }


@dataclass
class ScoredOpportunity:
    prospect_id: str
    prospect_domain: str
    source_page_url: str
    prospect_type: str
    target_asset_url: str
    score: ScoreBreakdown
    rationale: List[str] = field(default_factory=list)
    risk_factors: List[str] = field(default_factory=list)
    action_recommendation: str = "draft_ready"
    scored_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prospect_id": self.prospect_id,
            "prospect_domain": self.prospect_domain,
            "source_page_url": self.source_page_url,
            "prospect_type": self.prospect_type,
            "target_asset_url": self.target_asset_url,
            "score": self.score.to_dict(),
            "rationale": self.rationale,
            "risk_factors": self.risk_factors,
            "action_recommendation": self.action_recommendation,
            "scored_at": self.scored_at,
        }
