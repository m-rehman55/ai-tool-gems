"""
discovery.py - Multi-Source Keyword Discovery, Clustering & Explainable Opportunity Scoring.
Synthesizes:
1. Source A: Search Console query analytics (real clicks, impressions, positions, CTR)
2. Source B: Free public research & Pakistani search intent (PKR, EasyPaisa, JazzCash, Roman Urdu)
3. Source C: Competitor & catalog gap analysis (missing topics across 20 tools)
4. Source D: Semantic & long-tail intent expansion (troubleshooting, pricing, workflows)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Set
from keyword_agent.gsc_data import GSCQueryRow, GSCDataset


@dataclass
class KeywordCandidate:
    keyword: str
    cluster: str
    intent: str  # "transactional", "commercial", "informational", "navigational"
    market: str = "PK"
    impressions: int = 0
    clicks: int = 0
    ctr: float = 0.0
    position: float = 0.0
    source: str = "SYNTHESIS"  # "GSC", "PUBLIC_RESEARCH", "CATALOG_GAP", "SEMANTIC"
    opportunity_score: float = 0.0
    score_breakdown: Dict[str, float] = field(default_factory=dict)
    recommended_page: str = ""
    action_type: str = "OPTIMIZE_EXISTING"  # "OPTIMIZE_EXISTING", "MONITOR", "PROPOSE_NEW_PAGE"
    pakistan_relevance: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class KeywordDiscoveryEngine:
    """Discovers, clusters, scores, and segments keyword opportunities for Pakistan AI marketplace."""

    # Pakistan localized transactional modifiers
    PK_TRANSACTIONAL_MODIFIERS = [
        "price in pakistan", "in pakistan pkr", "easypaisa", "jazzcash", "sadapay",
        "buy in pakistan", "cheap subscription", "lifetime access", "student discount",
        "official license key", "rates in rupees",
    ]

    # Intent classification patterns
    INTENT_PATTERNS = [
        ("transactional", r"(?i)\b(buy|price|pricing|cost|subscribe|subscription|purchase|pkr|rs|rupees|easypaisa|jazzcash|license|key|account)\b"),
        ("commercial", r"(?i)\b(vs|versus|alternative|alternatives|compare|comparison|review|reviews|best|top|cheap|deal|discount)\b"),
        ("informational", r"(?i)\b(how|what|why|when|where|tutorial|guide|setup|download|error|prompt|use)\b"),
        ("navigational", r"(?i)\b(login|portal|official|sign in|download|app)\b"),
    ]

    def __init__(self, catalog_tools: Optional[List[str]] = None):
        self.catalog_tools = catalog_tools or [
            "chatgpt", "gemini", "veo", "leonardo", "elevenlabs", "canva", "figma",
            "adobe", "capcut", "lovable", "gamma", "replit", "n8n", "notion",
            "nordvpn", "surfshark", "youtube", "netflix", "linkedin", "windows",
        ]

    def classify_intent(self, keyword: str) -> str:
        """Classifies search intent strictly based on lexical markers."""
        kw_lower = keyword.lower()
        for intent, pattern in self.INTENT_PATTERNS:
            if re.search(pattern, kw_lower):
                return intent
        return "informational"

    def assign_cluster(self, keyword: str) -> str:
        """Assigns the keyword to the most relevant product or topical cluster."""
        kw_lower = keyword.lower()
        for tool in self.catalog_tools:
            if tool in kw_lower:
                return f"Tool: {tool.title()}"
        
        if any(w in kw_lower for w in ["price", "pricing", "cost", "pkr", "rate", "rates"]):
            return "Commercial: Pricing & PKR Comparison"
        if any(w in kw_lower for w in ["guide", "how", "vs", "compare", "alternative"]):
            return "Informational: Guides & Comparisons"
        if any(w in kw_lower for w in ["deal", "discount", "cheap", "bundle"]):
            return "Commercial: Deals & Discounts"
        
        return "General: AI Tools Pakistan"

    def calculate_opportunity_score(
        self,
        keyword: str,
        impressions: int,
        clicks: int,
        ctr: float,
        position: float,
        intent: str,
        is_pakistan: bool,
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculates an explainable ICE-R opportunity score (0.0 to 100.0).
        Components:
        1. Relevance to core business (max 25)
        2. GSC Demand / Volume Signal (max 25)
        3. CTR / Snippet Gap (max 20)
        4. Commercial / Purchase Value (max 20)
        5. Position Striking Distance (max 10)
        """
        breakdown = {}

        # 1. Relevance (Is it a tool we sell / Pakistan market?)
        rel_score = 15.0
        kw_lower = keyword.lower()
        if any(t in kw_lower for t in self.catalog_tools):
            rel_score += 5.0
        if is_pakistan:
            rel_score += 5.0
        breakdown["relevance"] = rel_score

        # 2. Demand Signal
        if impressions >= 50:
            dem_score = 25.0
        elif impressions >= 20:
            dem_score = 20.0
        elif impressions >= 5:
            dem_score = 15.0
        elif impressions > 0:
            dem_score = 10.0
        else:
            dem_score = 5.0  # Seed or discovery query
        breakdown["demand_signal"] = dem_score

        # 3. CTR Gap (Higher score for High Impression + Low CTR)
        if impressions >= 10 and ctr < 3.0:
            ctr_gap_score = 20.0  # High CTR upside
        elif impressions >= 5 and ctr < 5.0:
            ctr_gap_score = 15.0
        elif ctr >= 10.0:
            ctr_gap_score = 5.0   # Already winning CTR
        else:
            ctr_gap_score = 10.0
        breakdown["ctr_gap"] = ctr_gap_score

        # 4. Commercial / Transactional Intent
        if intent == "transactional":
            comm_score = 20.0
        elif intent == "commercial":
            comm_score = 15.0
        elif intent == "informational":
            comm_score = 8.0
        else:
            comm_score = 5.0
        breakdown["commercial_value"] = comm_score

        # 5. Position Striking Distance (Positions 4.0 - 15.0 have highest incremental ROI)
        if 4.0 <= position <= 10.0:
            pos_score = 10.0
        elif 10.1 <= position <= 20.0:
            pos_score = 7.0
        elif 1.0 <= position <= 3.9:
            pos_score = 4.0  # Already in top positions, protect
        else:
            pos_score = 3.0
        breakdown["striking_distance"] = pos_score

        total_score = sum(breakdown.values())
        return round(total_score, 1), breakdown

    def process_gsc_queries(self, gsc_dataset: GSCDataset) -> List[KeywordCandidate]:
        """Converts raw GSC query data into scored, clustered keyword candidates."""
        candidates: List[KeywordCandidate] = []
        for q in gsc_dataset.queries:
            intent = self.classify_intent(q.query)
            cluster = self.assign_cluster(q.query)
            is_pk = bool(re.search(r"(?i)(pakistan|pkr|rs|rupee|easypaisa|jazzcash|lahore|karachi)", q.query))

            score, breakdown = self.calculate_opportunity_score(
                keyword=q.query,
                impressions=q.impressions,
                clicks=q.clicks,
                ctr=q.ctr,
                position=q.position,
                intent=intent,
                is_pakistan=is_pk,
            )

            # Recommend action based on position & CTR
            if q.position <= 3.0:
                action = "PROTECT_WINNER"
            elif q.is_low_ctr_opportunity or q.is_striking_distance:
                action = "OPTIMIZE_EXISTING"
            else:
                action = "MONITOR"

            candidates.append(KeywordCandidate(
                keyword=q.query,
                cluster=cluster,
                intent=intent,
                market="PK",
                impressions=q.impressions,
                clicks=q.clicks,
                ctr=q.ctr,
                position=q.position,
                source="GSC",
                opportunity_score=score,
                score_breakdown=breakdown,
                action_type=action,
                pakistan_relevance=is_pk,
            ))
        return candidates

    def generate_seed_discovery_clusters(self) -> List[KeywordCandidate]:
        """
        Generates baseline Pakistani search clusters for all 20 verified tools in catalog,
        ensuring comprehensive target universe even when GSC data is awaiting import.
        """
        seed_candidates: List[KeywordCandidate] = []
        for tool in self.catalog_tools:
            # 1. Primary Commercial
            p1 = f"{tool.title()} price in Pakistan"
            s1, b1 = self.calculate_opportunity_score(p1, 0, 0, 0.0, 0.0, "transactional", True)
            seed_candidates.append(KeywordCandidate(
                keyword=p1,
                cluster=f"Tool: {tool.title()}",
                intent="transactional",
                market="PK",
                source="CATALOG_GAP",
                opportunity_score=s1,
                score_breakdown=b1,
                action_type="OPTIMIZE_EXISTING",
                pakistan_relevance=True,
            ))

            # 2. Local Payment
            p2 = f"buy {tool.title()} subscription EasyPaisa JazzCash"
            s2, b2 = self.calculate_opportunity_score(p2, 0, 0, 0.0, 0.0, "transactional", True)
            seed_candidates.append(KeywordCandidate(
                keyword=p2,
                cluster=f"Tool: {tool.title()}",
                intent="transactional",
                market="PK",
                source="CATALOG_GAP",
                opportunity_score=s2,
                score_breakdown=b2,
                action_type="OPTIMIZE_EXISTING",
                pakistan_relevance=True,
            ))

            # 3. AEO Question
            p3 = f"how to pay for {tool.title()} in Pakistan without credit card"
            s3, b3 = self.calculate_opportunity_score(p3, 0, 0, 0.0, 0.0, "informational", True)
            seed_candidates.append(KeywordCandidate(
                keyword=p3,
                cluster=f"Tool: {tool.title()}",
                intent="informational",
                market="PK",
                source="PUBLIC_RESEARCH",
                opportunity_score=s3,
                score_breakdown=b3,
                action_type="OPTIMIZE_EXISTING",
                pakistan_relevance=True,
            ))

        return seed_candidates

    def segment_opportunities(self, candidates: List[KeywordCandidate]) -> Dict[str, List[KeywordCandidate]]:
        """Segments candidate opportunities into clear strategic action buckets."""
        segmented: Dict[str, List[KeywordCandidate]] = {
            "high_impact_quick_wins": [],   # High impression / low CTR or striking distance
            "pakistan_transactional": [],   # High purchase intent with PKR / local wallets
            "aeo_question_opportunities": [], # High snippet / generative answer capture
            "protect_existing_winners": [], # Top 3 positions
            "untapped_content_backlog": [], # Candidate topics for future guides
        }

        for c in sorted(candidates, key=lambda x: x.opportunity_score, reverse=True):
            if c.action_type == "PROTECT_WINNER":
                segmented["protect_existing_winners"].append(c)
            elif c.impressions >= 5 and c.ctr < 5.0 and 4.0 <= c.position <= 15.0:
                segmented["high_impact_quick_wins"].append(c)
            elif c.intent == "transactional" and c.pakistan_relevance:
                segmented["pakistan_transactional"].append(c)
            elif c.intent == "informational" and re.search(r"(?i)^(how|can|is|what)\b", c.keyword):
                segmented["aeo_question_opportunities"].append(c)
            else:
                segmented["untapped_content_backlog"].append(c)

        return segmented
