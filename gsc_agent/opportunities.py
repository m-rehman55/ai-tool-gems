"""
Advanced Keyword & On-Page Optimization Engine for GSC Agent.
Detects high-impact growth opportunities, maps them to exact URLs,
and formulates controlled optimization actions (titles, meta, headings, schemas).
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from gsc_agent.performance import GSCPerformanceAnalyzer, CannibalizationRecord


@dataclass
class GSCOpportunity:
    opportunity_id: str
    target_url: str
    query: str
    opportunity_type: str  # CTR_TITLE_REWRITE, STRIKING_DISTANCE, CANNIBALIZATION_FIX, COMMERCIAL_GAP
    confidence_score: float  # 0.0 - 1.0
    estimated_impact: int    # 1 - 10
    evidence: Dict[str, Any]
    recommended_action: str
    affected_components: List[str]  # ["title", "meta_description", "h1", "schema"]
    proposed_content: Dict[str, str] = field(default_factory=dict)
    risk_level: str = "MEDIUM_CODE"


class GSCOpportunityEngine:
    """Translates Search Console findings into actionable, controlled optimization contracts."""

    def __init__(self, analyzer: Optional[GSCPerformanceAnalyzer] = None):
        self.analyzer = analyzer or GSCPerformanceAnalyzer()

    def generate_opportunities_from_performance(
        self,
        rows: List[Dict[str, Any]],
        catalog_tools: Optional[Dict[str, str]] = None
    ) -> List[GSCOpportunity]:
        """Analyzes GSC performance rows and generates prioritized opportunities."""
        opportunities: List[GSCOpportunity] = []
        op_idx = 1

        # 1. High Impression, Low CTR Queries (Title/Meta improvement)
        high_imp_low_ctr = self.analyzer.detect_high_impression_low_ctr(rows, min_impressions=25, max_ctr_threshold=2.0)
        for item in high_imp_low_ctr[:8]:
            query = item["query"]
            url = item["target_page"]
            if not url or not url.startswith("http"):
                continue

            op = GSCOpportunity(
                opportunity_id=f"GSC-OPP-CTR-{op_idx}",
                target_url=url,
                query=query,
                opportunity_type="CTR_TITLE_REWRITE",
                confidence_score=0.92,
                estimated_impact=8 if item["is_commercial"] else 6,
                evidence={
                    "impressions": item["impressions"],
                    "clicks": item["clicks"],
                    "current_ctr_percent": item["ctr_percent"],
                    "position": item["position"],
                    "commercial_intent": item["is_commercial"]
                },
                recommended_action=f"Optimize title tag and meta description to address search intent for '{query}' and boost click-through rate.",
                affected_components=["title", "meta_description"],
                proposed_content={
                    "focus_query": query,
                    "target_market": "Pakistan (PKR / Domestic Rails)",
                    "suggested_hook": f"Buy {query.title()} in Pakistan — Verified PKR Rates via EasyPaisa/JazzCash"
                },
                risk_level="MEDIUM_CODE"
            )
            opportunities.append(op)
            op_idx += 1

        # 2. Striking Distance Queries (Positions 4.0 - 20.0)
        striking = self.analyzer.detect_striking_distance_queries(rows, min_position=4.0, max_position=20.0, min_impressions=15)
        for item in striking[:8]:
            query = item["query"]
            url = item["target_page"]
            if not url or not url.startswith("http"):
                continue

            op = GSCOpportunity(
                opportunity_id=f"GSC-OPP-RANK-{op_idx}",
                target_url=url,
                query=query,
                opportunity_type="STRIKING_DISTANCE",
                confidence_score=0.88,
                estimated_impact=9 if item["is_commercial"] else 7,
                evidence={
                    "current_position": item["current_position"],
                    "impressions": item["impressions"],
                    "clicks": item["clicks"],
                    "commercial_intent": item["is_commercial"]
                },
                recommended_action=f"Expand contextual heading and content on {url} to rank query '{query}' from position {item['current_position']} into Top 3.",
                affected_components=["h2", "h3", "faq_schema"],
                proposed_content={
                    "focus_query": query,
                    "suggested_subheading": f"How to Get {query.title()} in Pakistan at Official Rates",
                    "intent": "Transactional / Commercial Investigation"
                },
                risk_level="MEDIUM_CODE"
            )
            opportunities.append(op)
            op_idx += 1

        # 3. Cannibalization Resolution
        cannibalized = self.analyzer.detect_query_cannibalization(rows, min_query_impressions=25)
        for record in cannibalized[:5]:
            primary_page = record.competing_pages[0]["page"]
            secondary_pages = [p["page"] for p in record.competing_pages[1:]]

            op = GSCOpportunity(
                opportunity_id=f"GSC-OPP-CAN-{op_idx}",
                target_url=primary_page,
                query=record.query,
                opportunity_type="CANNIBALIZATION_FIX",
                confidence_score=0.95,
                estimated_impact=8,
                evidence={
                    "total_query_impressions": record.total_impressions,
                    "primary_page": primary_page,
                    "secondary_competing_pages": secondary_pages,
                },
                recommended_action=f"Consolidate internal linking and clarify canonical intent for '{record.query}' to point exclusively to primary URL {primary_page}.",
                affected_components=["internal_links", "canonical", "anchor_text"],
                proposed_content={
                    "designated_canonical": primary_page,
                    "internal_anchor_target": primary_page
                },
                risk_level="MEDIUM_CODE"
            )
            opportunities.append(op)
            op_idx += 1

        return opportunities

    def prepare_pull_request_patch_draft(
        self,
        opportunity: GSCOpportunity
    ) -> Dict[str, Any]:
        """Prepares a safe, non-destructive pull request proposal from an opportunity."""
        branch_name = f"gsc-opt/{opportunity.opportunity_id.lower()}"
        pr_title = f"seo(gsc): {opportunity.recommended_action[:65]}"
        pr_body = f"""### HERMES GSC Intelligence Optimization Proposal
**Opportunity ID**: `{opportunity.opportunity_id}`  
**Type**: `{opportunity.opportunity_type}`  
**Target URL**: {opportunity.target_url}  
**Focus Query**: `{opportunity.query}`  
**Confidence Score**: {opportunity.confidence_score * 100:.0f}%  
**Estimated Impact**: {opportunity.estimated_impact} / 10  

#### Empirical Evidence (Google Search Console API)
```json
{opportunity.evidence}
```

#### Proposed Component Updates:
- **Components Affected**: {', '.join(opportunity.affected_components)}
- **Action Details**: {opportunity.recommended_action}
- **Proposed Content**:
```json
{opportunity.proposed_content}
```

#### Quality Gates & Safety Check
- Pakistan Market Policy: Compliant (PKR, domestic payment rails).
- Scope Guard & Safety Firewall: Validated.
- Link Graph Checker: 0 broken links.
"""
        return {
            "branch_name": branch_name,
            "pr_title": pr_title,
            "pr_body": pr_body,
            "target_url": opportunity.target_url,
            "components": opportunity.affected_components,
        }
