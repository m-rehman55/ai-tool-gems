"""
Search Performance Intelligence Engine for GSC Agent.
Performs deep analysis: Pakistan filtering, date comparisons,
brand vs non-brand separation, striking distance ranking (4-30),
high-impression/low-CTR opportunities, and cannibalization detection.
"""

from __future__ import annotations
import re
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple

BRAND_PATTERNS = [
    re.compile(r"\b(ai\s*tool\s*gems?|aitoolgems?|toolgems?)\b", re.IGNORECASE)
]

COMMERCIAL_PATTERNS = [
    re.compile(r"\b(buy|price|cost|rate|pkr|rs|subscription|cheap|discount|pakistan|karachi|lahore)\b", re.IGNORECASE)
]


@dataclass
class PerformanceSummary:
    total_clicks: int = 0
    total_impressions: int = 0
    average_ctr: float = 0.0
    average_position: float = 0.0
    query_count: int = 0
    page_count: int = 0


@dataclass
class CannibalizationRecord:
    query: str
    total_impressions: int
    competing_pages: List[Dict[str, Any]] = field(default_factory=list)


class GSCPerformanceAnalyzer:
    """Analyzes raw Google Search Console dataset with rigorous segmentation."""

    def __init__(self, brand_patterns: Optional[List[re.Pattern]] = None):
        self.brand_patterns = brand_patterns or BRAND_PATTERNS

    def is_brand_query(self, query: str) -> bool:
        return any(p.search(query) for p in self.brand_patterns)

    def is_commercial_query(self, query: str) -> bool:
        return any(p.search(query) for p in COMMERCIAL_PATTERNS)

    def summarize_dataset(self, rows: List[Dict[str, Any]]) -> PerformanceSummary:
        """Calculates exact aggregate metrics across rows without assumptions."""
        if not rows:
            return PerformanceSummary()

        clicks = sum(int(r.get("clicks", 0)) for r in rows)
        impressions = sum(int(r.get("impressions", 0)) for r in rows)
        ctr = (clicks / impressions * 100.0) if impressions > 0 else 0.0

        # Weighted average position
        weighted_pos = sum(float(r.get("position", 0.0)) * int(r.get("impressions", 1)) for r in rows)
        avg_pos = (weighted_pos / impressions) if impressions > 0 else 0.0

        unique_queries = set()
        unique_pages = set()

        for r in rows:
            keys = r.get("keys", [])
            if len(keys) >= 2:
                unique_queries.add(keys[0])
                unique_pages.add(keys[1])
            elif len(keys) == 1:
                val = keys[0]
                if val.startswith("http"):
                    unique_pages.add(val)
                else:
                    unique_queries.add(val)

        return PerformanceSummary(
            total_clicks=clicks,
            total_impressions=impressions,
            average_ctr=round(ctr, 2),
            average_position=round(avg_pos, 1),
            query_count=len(unique_queries),
            page_count=len(unique_pages),
        )

    def segment_brand_vs_non_brand(
        self,
        rows: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Separates dataset into Brand and Non-Brand segments."""
        brand_rows = []
        non_brand_rows = []

        for r in rows:
            keys = r.get("keys", [])
            query = keys[0] if keys and not keys[0].startswith("http") else ""
            if query and self.is_brand_query(query):
                brand_rows.append(r)
            else:
                non_brand_rows.append(r)

        return {
            "brand": {
                "summary": self.summarize_dataset(brand_rows),
                "rows_count": len(brand_rows),
                "sample_queries": [r["keys"][0] for r in brand_rows[:5] if "keys" in r],
            },
            "non_brand": {
                "summary": self.summarize_dataset(non_brand_rows),
                "rows_count": len(non_brand_rows),
                "sample_queries": [r["keys"][0] for r in non_brand_rows[:5] if "keys" in r],
            }
        }

    def detect_high_impression_low_ctr(
        self,
        rows: List[Dict[str, Any]],
        min_impressions: int = 30,
        max_ctr_threshold: float = 2.5
    ) -> List[Dict[str, Any]]:
        """Identifies search queries with substantial search exposure but poor click-through rate."""
        candidates = []
        for r in rows:
            imp = int(r.get("impressions", 0))
            clicks = int(r.get("clicks", 0))
            ctr = float(r.get("ctr", 0.0)) * 100.0 if "ctr" in r else ((clicks / imp * 100.0) if imp > 0 else 0.0)
            pos = float(r.get("position", 0.0))

            if imp >= min_impressions and ctr <= max_ctr_threshold:
                keys = r.get("keys", [])
                query = keys[0] if len(keys) > 0 else "unknown"
                page = keys[1] if len(keys) > 1 else ""
                candidates.append({
                    "query": query,
                    "target_page": page,
                    "impressions": imp,
                    "clicks": clicks,
                    "ctr_percent": round(ctr, 2),
                    "position": round(pos, 1),
                    "is_commercial": self.is_commercial_query(query),
                    "opportunity_type": "CTR_TITLE_META_REVISION"
                })

        # Sort descending by impressions
        candidates.sort(key=lambda x: x["impressions"], reverse=True)
        return candidates

    def detect_striking_distance_queries(
        self,
        rows: List[Dict[str, Any]],
        min_position: float = 4.0,
        max_position: float = 30.0,
        min_impressions: int = 15
    ) -> List[Dict[str, Any]]:
        """Identifies queries ranking on the brink of top positions (Rank 4 to 30) for fast wins."""
        opportunities = []
        for r in rows:
            pos = float(r.get("position", 0.0))
            imp = int(r.get("impressions", 0))
            clicks = int(r.get("clicks", 0))

            if min_position <= pos <= max_position and imp >= min_impressions:
                keys = r.get("keys", [])
                query = keys[0] if len(keys) > 0 else "unknown"
                page = keys[1] if len(keys) > 1 else ""
                opportunities.append({
                    "query": query,
                    "target_page": page,
                    "current_position": round(pos, 1),
                    "impressions": imp,
                    "clicks": clicks,
                    "is_commercial": self.is_commercial_query(query),
                    "opportunity_type": "RANKING_CONTENT_EXPANSION"
                })

        opportunities.sort(key=lambda x: (x["is_commercial"], x["impressions"]), reverse=True)
        return opportunities

    def detect_query_cannibalization(
        self,
        rows: List[Dict[str, Any]],
        min_query_impressions: int = 20
    ) -> List[CannibalizationRecord]:
        """Detects instances where multiple pages compete in the SERP for the identical query."""
        query_page_map: Dict[str, List[Dict[str, Any]]] = {}

        for r in rows:
            keys = r.get("keys", [])
            if len(keys) < 2:
                continue
            query, page = keys[0], keys[1]
            imp = int(r.get("impressions", 0))
            clicks = int(r.get("clicks", 0))
            pos = float(r.get("position", 0.0))

            if query not in query_page_map:
                query_page_map[query] = []
            query_page_map[query].append({
                "page": page,
                "impressions": imp,
                "clicks": clicks,
                "position": round(pos, 1)
            })

        cannibalized: List[CannibalizationRecord] = []
        for q, pages in query_page_map.items():
            if len(pages) > 1:
                total_imp = sum(p["impressions"] for p in pages)
                if total_imp >= min_query_impressions:
                    # Sort pages descending by impressions
                    pages.sort(key=lambda x: x["impressions"], reverse=True)
                    cannibalized.append(
                        CannibalizationRecord(
                            query=q,
                            total_impressions=total_imp,
                            competing_pages=pages
                        )
                    )

        cannibalized.sort(key=lambda x: x.total_impressions, reverse=True)
        return cannibalized

    def compare_periods(
        self,
        current_rows: List[Dict[str, Any]],
        prior_rows: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compares current period vs prior period to uncover gaining and declining keywords & pages."""
        cur_summary = self.summarize_dataset(current_rows)
        prior_summary = self.summarize_dataset(prior_rows)

        # Build mapping for prior
        prior_map = {}
        for r in prior_rows:
            keys = r.get("keys", [])
            key_id = "::".join(keys)
            prior_map[key_id] = {
                "clicks": int(r.get("clicks", 0)),
                "impressions": int(r.get("impressions", 0)),
                "position": float(r.get("position", 0.0))
            }

        gaining = []
        declining = []

        for r in current_rows:
            keys = r.get("keys", [])
            key_id = "::".join(keys)
            cur_clicks = int(r.get("clicks", 0))
            cur_imp = int(r.get("impressions", 0))
            cur_pos = float(r.get("position", 0.0))

            prior = prior_map.get(key_id)
            if prior:
                click_diff = cur_clicks - prior["clicks"]
                imp_diff = cur_imp - prior["impressions"]
                pos_diff = prior["position"] - cur_pos  # positive means improved rank

                item = {
                    "key": key_id,
                    "current": {"clicks": cur_clicks, "impressions": cur_imp, "position": cur_pos},
                    "prior": prior,
                    "click_change": click_diff,
                    "impression_change": imp_diff,
                    "rank_change": round(pos_diff, 1)
                }
                if click_diff > 0 or imp_diff >= 10:
                    gaining.append(item)
                elif click_diff < 0 or imp_diff <= -10:
                    declining.append(item)
            else:
                # Brand new keyword/page in current period
                if cur_imp >= 5:
                    gaining.append({
                        "key": key_id,
                        "current": {"clicks": cur_clicks, "impressions": cur_imp, "position": cur_pos},
                        "prior": None,
                        "click_change": cur_clicks,
                        "impression_change": cur_imp,
                        "rank_change": 0.0,
                        "status": "NEW_DISCOVERY"
                    })

        gaining.sort(key=lambda x: x["click_change"], reverse=True)
        declining.sort(key=lambda x: x["click_change"])

        return {
            "current_period": cur_summary.__dict__,
            "prior_period": prior_summary.__dict__,
            "deltas": {
                "click_change": cur_summary.total_clicks - prior_summary.total_clicks,
                "impression_change": cur_summary.total_impressions - prior_summary.total_impressions,
                "ctr_change": round(cur_summary.average_ctr - prior_summary.average_ctr, 2),
                "pos_change": round(prior_summary.average_position - cur_summary.average_position, 1),
            },
            "gaining_count": len(gaining),
            "declining_count": len(declining),
            "top_gaining": gaining[:10],
            "top_declining": declining[:10],
        }
