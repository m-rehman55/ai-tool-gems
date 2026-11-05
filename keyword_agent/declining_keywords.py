"""
declining_keywords.py - GSC Historical Trend & Declining Keywords Detector.

Compares current Search Console performance against a prior comparison period
or previous historical snapshot to detect:
1. Position drop (queries slipping from striking distance or page 1).
2. Impression decay (decreasing search visibility).
3. Click loss (declining CTR or traffic loss).
4. Dropouts (queries that vanished from GSC search results).

Enables HERMES-CEO and editorial specialists to immediately remediate decaying pages
before organic traffic is lost.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from keyword_agent.gsc_data import GSCDataset, GSCQueryRow

logger = logging.getLogger("keyword_agent.declining_keywords")


@dataclass
class DecliningKeywordAnalysis:
    query: str
    severity: str  # "CRITICAL_DECLINE", "MODERATE_DECLINE", "STABLE", "GROWING", "DROPOUT"
    current_clicks: int
    previous_clicks: int
    clicks_delta: int
    clicks_change_pct: float
    current_impressions: int
    previous_impressions: int
    impressions_delta: int
    impressions_change_pct: float
    current_position: float
    previous_position: float
    position_delta: float  # Positive means dropped in rank (e.g. 4.0 -> 9.0 = +5.0 drop)
    is_pakistan: bool
    recommended_action: str
    remediation_priority: str  # "P1_URGENT", "P2_EVALUATE", "NONE"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "severity": self.severity,
            "current_clicks": self.current_clicks,
            "previous_clicks": self.previous_clicks,
            "clicks_delta": self.clicks_delta,
            "clicks_change_pct": round(self.clicks_change_pct, 1),
            "current_impressions": self.current_impressions,
            "previous_impressions": self.previous_impressions,
            "impressions_delta": self.impressions_delta,
            "impressions_change_pct": round(self.impressions_change_pct, 1),
            "current_position": round(self.current_position, 1),
            "previous_position": round(self.previous_position, 1),
            "position_delta": round(self.position_delta, 1),
            "is_pakistan": self.is_pakistan,
            "recommended_action": self.recommended_action,
            "remediation_priority": self.remediation_priority,
        }


class DecliningKeywordsEngine:
    """Analyzes period-over-period search performance to isolate declining queries."""

    def __init__(self, current_dataset: GSCDataset, previous_dataset: Optional[GSCDataset] = None):
        self.current_dataset = current_dataset
        self.previous_dataset = previous_dataset

    def analyze(self) -> List[DecliningKeywordAnalysis]:
        """
        Compares query metrics across datasets and returns categorized list of analyses.
        If previous_dataset is None or has no queries, returns an empty list.
        """
        if not self.previous_dataset or not self.previous_dataset.queries:
            return []

        curr_map: Dict[str, GSCQueryRow] = {q.query.lower().strip(): q for q in self.current_dataset.queries}
        prev_map: Dict[str, GSCQueryRow] = {q.query.lower().strip(): q for q in self.previous_dataset.queries}

        results: List[DecliningKeywordAnalysis] = []

        # Analyze queries present in previous dataset
        for q_text, prev_q in prev_map.items():
            curr_q = curr_map.get(q_text)
            is_pk = any(m in q_text for m in ["pakistan", "pkr", "rupees", "easypaisa", "jazzcash", "sadapay"])

            if curr_q:
                clicks_delta = curr_q.clicks - prev_q.clicks
                clicks_pct = ((curr_q.clicks - prev_q.clicks) / max(prev_q.clicks, 1)) * 100.0 if prev_q.clicks > 0 else 0.0

                imp_delta = curr_q.impressions - prev_q.impressions
                imp_pct = ((curr_q.impressions - prev_q.impressions) / max(prev_q.impressions, 1)) * 100.0 if prev_q.impressions > 0 else 0.0

                pos_delta = curr_q.position - prev_q.position  # e.g., 8.0 - 4.0 = +4.0 (decay)

                # Classify severity
                if (pos_delta >= 4.0 and prev_q.position <= 20.0) or (clicks_delta <= -3 and clicks_pct <= -40.0):
                    severity = "CRITICAL_DECLINE"
                    priority = "P1_URGENT"
                    action = "Immediate SERP snippet and on-page content refresh required. Check competitor moves."
                elif pos_delta >= 2.5 or (imp_delta <= -10 and imp_pct <= -25.0):
                    severity = "MODERATE_DECLINE"
                    priority = "P2_EVALUATE"
                    action = "Monitor CTR. Refresh direct-answer definitions and FAQ blocks."
                elif pos_delta <= -2.0 or clicks_pct >= 25.0:
                    severity = "GROWING"
                    priority = "NONE"
                    action = "Protect position. Expand related long-tail question coverage."
                else:
                    severity = "STABLE"
                    priority = "NONE"
                    action = "Maintain regular monitoring."

                results.append(DecliningKeywordAnalysis(
                    query=prev_q.query,
                    severity=severity,
                    current_clicks=curr_q.clicks,
                    previous_clicks=prev_q.clicks,
                    clicks_delta=clicks_delta,
                    clicks_change_pct=clicks_pct,
                    current_impressions=curr_q.impressions,
                    previous_impressions=prev_q.impressions,
                    impressions_delta=imp_delta,
                    impressions_change_pct=imp_pct,
                    current_position=curr_q.position,
                    previous_position=prev_q.position,
                    position_delta=pos_delta,
                    is_pakistan=is_pk,
                    recommended_action=action,
                    remediation_priority=priority,
                ))
            else:
                # Dropout: Query was in previous dataset but vanished in current
                if prev_q.impressions >= 10 or prev_q.clicks >= 1:
                    results.append(DecliningKeywordAnalysis(
                        query=prev_q.query,
                        severity="DROPOUT",
                        current_clicks=0,
                        previous_clicks=prev_q.clicks,
                        clicks_delta=-prev_q.clicks,
                        clicks_change_pct=-100.0,
                        current_impressions=0,
                        previous_impressions=prev_q.impressions,
                        impressions_delta=-prev_q.impressions,
                        impressions_change_pct=-100.0,
                        current_position=100.0,
                        previous_position=prev_q.position,
                        position_delta=100.0 - prev_q.position,
                        is_pakistan=is_pk,
                        recommended_action="Investigate URL indexability and canonical status. Resubmit via IndexNow.",
                        remediation_priority="P1_URGENT",
                    ))

        # Sort so critical declines and dropouts appear first
        priority_order = {"CRITICAL_DECLINE": 0, "DROPOUT": 1, "MODERATE_DECLINE": 2, "STABLE": 3, "GROWING": 4}
        results.sort(key=lambda x: (priority_order.get(x.severity, 99), -abs(x.clicks_delta)))
        return results
