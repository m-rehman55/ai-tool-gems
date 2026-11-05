"""SERP Radar & Competitor Ranking Overlap Engine."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SERPQuerySnapshot:
    query: str
    search_volume_tier: str  # HIGH, MEDIUM, LOW
    aitoolgems_rank: Optional[int]
    top_competitors_ranked: List[Dict[str, Any]]  # [{"domain": "aitoolspak.tech", "rank": 2}]
    serp_features_present: List[str]             # ["AI_OVERVIEW", "FAQ_RICH_RESULT", "SNIPPET"]
    content_gap_opportunity: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


PAKISTAN_SERP_RADAR: List[SERPQuerySnapshot] = [
    SERPQuerySnapshot(
        query="buy chatgpt plus in pakistan",
        search_volume_tier="HIGH",
        aitoolgems_rank=2,
        top_competitors_ranked=[
            {"domain": "paktools.store", "rank": 1},
            {"domain": "aitoolspak.tech", "rank": 3},
            {"domain": "digitaltools.com.pk", "rank": 5},
        ],
        serp_features_present=["AI_OVERVIEW", "FAQ_RICH_RESULT"],
        content_gap_opportunity="Highlight instant 5-minute WhatsApp activation and EasyPaisa domestic flow in meta description.",
    ),
    SERPQuerySnapshot(
        query="claude pro price in pakistan 2026",
        search_volume_tier="HIGH",
        aitoolgems_rank=1,
        top_competitors_ranked=[
            {"domain": "aitoolspak.tech", "rank": 2},
            {"domain": "toolwaly.com", "rank": 4},
        ],
        serp_features_present=["SNIPPET", "AI_OVERVIEW"],
        content_gap_opportunity="Maintain rank #1 by updating Claude 3.5 Sonnet benchmark comparison table.",
    ),
    SERPQuerySnapshot(
        query="midjourney subscription pakistan easypaisa",
        search_volume_tier="MEDIUM",
        aitoolgems_rank=1,
        top_competitors_ranked=[
            {"domain": "paktools.store", "rank": 3},
            {"domain": "groupseotoolz.com", "rank": 4},
        ],
        serp_features_present=["FAQ_RICH_RESULT"],
        content_gap_opportunity="Clarify private server Discord bot setup vs shared group bot.",
    ),
    SERPQuerySnapshot(
        query="ai tools bundle subscription pakistan price",
        search_volume_tier="HIGH",
        aitoolgems_rank=2,
        top_competitors_ranked=[
            {"domain": "seotoolzbundle.com", "rank": 1},
            {"domain": "aitoolspak.tech", "rank": 4},
        ],
        serp_features_present=["AI_OVERVIEW", "SNIPPET"],
        content_gap_opportunity="Build dedicated bundle landing page targeting freelancers requiring 3+ tools.",
    ),
]


def get_serp_radar_snapshots() -> List[SERPQuerySnapshot]:
    return PAKISTAN_SERP_RADAR


def compute_share_of_voice() -> Dict[str, Any]:
    """Calculate organic search Share of Voice across tracked queries."""
    radar = get_serp_radar_snapshots()
    sov_points: Dict[str, int] = {"aitoolgems.tech": 0}

    for snap in radar:
        # 1st place: 10 pts, 2nd: 7 pts, 3rd: 5 pts, 4th: 3 pts, 5th: 1 pt
        points_map = {1: 10, 2: 7, 3: 5, 4: 3, 5: 1}

        if snap.aitoolgems_rank and snap.aitoolgems_rank in points_map:
            sov_points["aitoolgems.tech"] += points_map[snap.aitoolgems_rank]

        for comp in snap.top_competitors_ranked:
            domain = comp.get("domain", "")
            rank = comp.get("rank")
            if domain and rank in points_map:
                sov_points[domain] = sov_points.get(domain, 0) + points_map[rank]

    total_points = sum(sov_points.values())
    sov_percentages = {
        domain: round((pts / total_points * 100.0), 1) if total_points else 0.0
        for domain, pts in sorted(sov_points.items(), key=lambda x: x[1], reverse=True)
    }

    return {
        "tracked_queries_count": len(radar),
        "total_serp_points": total_points,
        "share_of_voice_pct": sov_percentages,
        "market_leader": max(sov_percentages.items(), key=lambda x: x[1])[0] if sov_percentages else "None",
    }

