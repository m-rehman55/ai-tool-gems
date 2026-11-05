"""
analyzer.py - Bing Webmaster Search Intelligence & Cross-Engine Diagnostic Analyzer.

Analyzes:
1. Bing search performance (queries, clicks, impressions, CTR, average position).
2. Bing crawl statistics, error trends (4xx, 5xx, timeouts), and in-index progression.
3. Cross-engine gap analysis (Comparing Google Search Console vs Bing Webmaster data).
4. Bing SEO recommendations and site health diagnostics.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from bing_agent.client import BingWebmasterClient
from bing_agent.models import BingCrawlStat, BingPageStat, BingQueryStat, BingQuota

logger = logging.getLogger("bing_agent.analyzer")


@dataclass
class CrossEngineQueryInsight:
    query: str
    bing_impressions: int
    bing_clicks: int
    bing_position: float
    gsc_impressions: int
    gsc_clicks: int
    gsc_position: float
    opportunity_type: str  # "BING_BREAKTHROUGH", "BING_LAGGING", "CROSS_ENGINE_WINNER"
    recommendation: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BingAuditSummary:
    timestamp: str
    site_url: str
    is_verified: bool
    daily_quota: int
    monthly_quota: int
    total_bing_queries: int
    total_bing_impressions: int
    total_bing_clicks: int
    average_bing_position: float
    current_pages_in_index: int
    crawl_errors_count: int
    cross_engine_insights: List[CrossEngineQueryInsight] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "site_url": self.site_url,
            "is_verified": self.is_verified,
            "daily_quota": self.daily_quota,
            "monthly_quota": self.monthly_quota,
            "total_bing_queries": self.total_bing_queries,
            "total_bing_impressions": self.total_bing_impressions,
            "total_bing_clicks": self.total_bing_clicks,
            "average_bing_position": round(self.average_bing_position, 1),
            "current_pages_in_index": self.current_pages_in_index,
            "crawl_errors_count": self.crawl_errors_count,
            "cross_engine_insights": [i.to_dict() for i in self.cross_engine_insights],
            "recommendations": self.recommendations,
        }


class BingWebmasterAnalyzer:
    """Analyzes Bing Webmaster empirical data and cross-references GSC metrics."""

    def __init__(self, client: BingWebmasterClient):
        self.client = client

    def run_audit(self, gsc_dataset: Optional[Any] = None) -> BingAuditSummary:
        """Runs complete Bing Webmaster audit using live API data or safe offline baseline."""
        now_iso = datetime.now(timezone.utc).isoformat()
        site_url = self.client.default_site_url

        if not self.client.is_authorized:
            return BingAuditSummary(
                timestamp=now_iso,
                site_url=site_url,
                is_verified=False,
                daily_quota=0,
                monthly_quota=0,
                total_bing_queries=0,
                total_bing_impressions=0,
                total_bing_clicks=0,
                average_bing_position=0.0,
                current_pages_in_index=0,
                crawl_errors_count=0,
                cross_engine_insights=[],
                recommendations=["BING_API_KEY missing in environment. Set BING_API_KEY to retrieve live Bing Webmaster data."],
            )

        # 1. Verification & Quota
        sites = self.client.get_user_sites()
        is_verified = any(s.is_verified for s in sites if s.url.rstrip("/") == site_url.rstrip("/"))
        quota = self.client.get_submission_quota()

        # 2. Crawl Stats
        crawl_stats = self.client.get_crawl_stats()
        latest_crawl = crawl_stats[-1] if crawl_stats else None
        in_index = latest_crawl.in_index if latest_crawl else 0
        total_crawl_errors = sum(c.crawl_errors for c in crawl_stats[-7:]) if crawl_stats else 0

        # 3. Query Performance
        query_stats = self.client.get_query_stats()
        tot_imp = sum(q.impressions for q in query_stats)
        tot_clicks = sum(q.clicks for q in query_stats)
        valid_pos = [q.avg_impression_position for q in query_stats if q.avg_impression_position > 0]
        avg_pos = sum(valid_pos) / len(valid_pos) if valid_pos else 0.0

        # 4. Cross-Engine Analysis (Bing vs GSC)
        cross_insights: List[CrossEngineQueryInsight] = []
        gsc_queries: Dict[str, Any] = {}
        if gsc_dataset and hasattr(gsc_dataset, "queries"):
            for q in gsc_dataset.queries:
                gsc_queries[q.query.lower().strip()] = q

        for b_q in query_stats:
            q_norm = b_q.query.lower().strip()
            g_q = gsc_queries.get(q_norm)

            g_imp = g_q.impressions if g_q else 0
            g_clicks = g_q.clicks if g_q else 0
            g_pos = g_q.position if g_q else 0.0

            if b_q.avg_impression_position > 0 and b_q.avg_impression_position <= 5.0 and (not g_q or g_pos > 10.0):
                opp_type = "BING_BREAKTHROUGH"
                rec = f"Ranking #{b_q.avg_impression_position:.0f} on Bing! Protect snippet and add target anchor links."
            elif g_imp >= 10 and (b_q.impressions <= 1 or b_q.avg_impression_position > 20.0):
                opp_type = "BING_LAGGING"
                rec = "Winning impressions in Google but lagging on Bing. Submit target URL to IndexNow."
            else:
                opp_type = "CROSS_ENGINE_WINNER"
                rec = "Healthy cross-engine discovery."

            cross_insights.append(CrossEngineQueryInsight(
                query=b_q.query,
                bing_impressions=b_q.impressions,
                bing_clicks=b_q.clicks,
                bing_position=b_q.avg_impression_position,
                gsc_impressions=g_imp,
                gsc_clicks=g_clicks,
                gsc_position=g_pos,
                opportunity_type=opp_type,
                recommendation=rec,
            ))

        # 5. Formulate Strategic Recommendations
        recommendations: List[str] = []
        if in_index < 50:
            recommendations.append(
                f"Bing has {in_index} pages in its active index. Dispatch newly updated tool pages via IndexNow queue to accelerate Bing index expansion."
            )
        if total_crawl_errors > 0:
            recommendations.append(
                f"Bing reported {total_crawl_errors} crawl errors over the past 7 days. Inspect 4xx/5xx responses in server logs."
            )
        breakthroughs = [i for i in cross_insights if i.opportunity_type == "BING_BREAKTHROUGH"]
        if breakthroughs:
            recommendations.append(
                f"Capitalize on {len(breakthroughs)} Bing breakthrough queries (e.g. '{breakthroughs[0].query}') where Bing ranks in Top 5."
            )

        return BingAuditSummary(
            timestamp=now_iso,
            site_url=site_url,
            is_verified=is_verified,
            daily_quota=quota.daily_quota,
            monthly_quota=quota.monthly_quota,
            total_bing_queries=len(query_stats),
            total_bing_impressions=tot_imp,
            total_bing_clicks=tot_clicks,
            average_bing_position=avg_pos,
            current_pages_in_index=in_index,
            crawl_errors_count=total_crawl_errors,
            cross_engine_insights=cross_insights[:20],
            recommendations=recommendations,
        )

