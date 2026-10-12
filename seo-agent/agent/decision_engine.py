#!/usr/bin/env python3
"""
Decision Engine for AIToolGems Autonomous SEO Growth Agent
----------------------------------------------------------
Scores, prioritizes, and classifies candidate SEO actions based on:
Impact, Confidence, Effort, Risk, and Business Relevance.
Enforces safe action tiering (REJECT, MONITOR, AUTO_REPORT, PROPOSE_PR, HUMAN_REQUIRED).
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

class ActionTier(str, Enum):
    REJECT = "REJECT"                    # Violates safety, scope, or contains injection
    MONITOR = "MONITOR"                  # Low impact/confidence, observe metrics
    AUTO_REPORT = "AUTO_REPORT"          # Read-only audit logging & notification
    PROPOSE_PR = "PROPOSE_PR"            # Safe change proposed via dedicated Git branch + PR
    HUMAN_REQUIRED = "HUMAN_REQUIRED"    # Commercial price, policy, or DNS/security change

class Category(str, Enum):
    TECHNICAL_P0 = "TECHNICAL_P0"        # Indexing block, canonical mismatch, 404, broken schema
    TECHNICAL_P1 = "TECHNICAL_P1"        # Title tag, meta description, image alt text, broken link
    LOCAL_PAKISTAN = "LOCAL_PAKISTAN"    # Missing PKR currency, missing EasyPaisa/JazzCash signal
    AI_DISCOVERABILITY = "AI_SEARCH"     # LLM answer engine eligibility, structured FAQs, specs
    CONTENT_EXPANSION = "CONTENT_GAP"    # New high-demand keyword cluster brief/draft
    COMMERCIAL_PRICE = "PRICE_POLICY"    # Product price or licensing terms (Protected)

@dataclass
class SEOOpportunity:
    id: str
    category: Category
    title: str
    target_url: str
    impact: int                          # 1 - 10
    confidence: float                    # 0.0 - 1.0 (e.g. 0.95 for verified DOM defect, 0.4 for trend hypothesis)
    effort: int                          # 1 - 10
    risk: str                            # SAFE, LOW, MEDIUM, HIGH, CRITICAL
    evidence: str
    recommended_action: str
    files_affected: List[str] = field(default_factory=list)
    score: float = 0.0
    tier: ActionTier = ActionTier.MONITOR

class DecisionEngine:
    """Prioritizes and routes SEO tasks."""

    def __init__(self, autonomy_mode: str = "PR"):
        self.autonomy_mode = autonomy_mode.upper()

    def calculate_priority_score(self, opp: SEOOpportunity) -> float:
        """
        Calculates ICE-R Score:
        Score = (Impact * 2.0 + Confidence * 10.0) / (Effort * 0.5 + 1.0)
        Penalized by risk level.
        """
        base = (opp.impact * 2.0) + (opp.confidence * 10.0)
        effort_factor = (opp.effort * 0.5) + 1.0
        raw_score = base / effort_factor

        risk_multipliers = {
            "SAFE": 1.0,
            "LOW": 0.9,
            "MEDIUM": 0.7,
            "HIGH": 0.4,
            "CRITICAL": 0.0,
        }
        multiplier = risk_multipliers.get(opp.risk.upper(), 0.5)
        return round(raw_score * multiplier, 2)

    def classify_opportunity(self, opp: SEOOpportunity) -> SEOOpportunity:
        """Assigns priority score and actionable execution tier."""
        opp.score = self.calculate_priority_score(opp)

        # 1. Critical risk or policy violation is immediately rejected
        if opp.risk.upper() == "CRITICAL":
            opp.tier = ActionTier.REJECT
            return opp

        # 2. Commercial prices or legal policies strictly require human signoff
        if opp.category == Category.COMMERCIAL_PRICE:
            opp.tier = ActionTier.HUMAN_REQUIRED
            return opp

        # 3. Mode constraint: If running in AUDIT mode, only read-only report
        if self.autonomy_mode == "AUDIT":
            opp.tier = ActionTier.AUTO_REPORT
            return opp

        # 4. Safe improvements with high confidence (>0.7) and low/medium risk
        if opp.confidence >= 0.7 and opp.risk.upper() in ["SAFE", "LOW"]:
            opp.tier = ActionTier.PROPOSE_PR
            return opp

        # 5. Low confidence or high effort without clear evidence
        opp.tier = ActionTier.MONITOR
        return opp

    def rank_opportunities(self, opportunities: List[SEOOpportunity]) -> List[SEOOpportunity]:
        """Classifies and sorts opportunities from highest to lowest score."""
        evaluated = [self.classify_opportunity(opp) for opp in opportunities]
        # Sort by tier priority and score
        tier_weights = {
            ActionTier.PROPOSE_PR: 100,
            ActionTier.AUTO_REPORT: 80,
            ActionTier.HUMAN_REQUIRED: 60,
            ActionTier.MONITOR: 40,
            ActionTier.REJECT: 0,
        }
        return sorted(evaluated, key=lambda x: (tier_weights.get(x.tier, 0), x.score), reverse=True)
