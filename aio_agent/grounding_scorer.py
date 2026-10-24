"""
grounding_scorer.py - Google AI Overviews Grounding & RAG Readiness Scoring Engine.
Synthesizes extractability, query fan-out coverage, semantic schema, and local information gain.
Outputs a composite 0-100 AIO Score with clear actionable recommendations.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from aio_agent.extractability import ExtractabilityAuditor, ExtractabilityReport
from aio_agent.query_fanout import QueryFanOutAnalyzer, QueryFanOutAnalysis


@dataclass
class PageAIOScore:
    file_path: str
    url_slug: str
    extractability_score: float  # out of 35
    fanout_score: float         # out of 35
    schema_score: float         # out of 15
    information_gain_score: float  # out of 15
    total_aio_score: float      # out of 100
    tier: str                   # "ELITE_AIO_READY", "AIO_COMPLIANT", "NEEDS_OPTIMIZATION"
    recommendations: List[str] = field(default_factory=list)


class GroundingScorer:
    """Calculates comprehensive Google AI Overviews Grounding Score."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.extractability_auditor = ExtractabilityAuditor()
        self.fanout_analyzer = QueryFanOutAnalyzer()

    def score_page(self, file_path: Path) -> PageAIOScore:
        content = file_path.read_text(encoding="utf-8")
        slug = file_path.parent.name if file_path.name == "index.html" else file_path.stem

        recs: List[str] = []

        # 1. Extractability (Weight: 35%)
        ext_rep = self.extractability_auditor.audit_file(file_path)
        ext_scaled = (ext_rep.extractability_score / 100.0) * 35.0
        recs.extend(ext_rep.recommendations)

        # 2. Query Fan-Out (Weight: 35%)
        fan_rep = self.fanout_analyzer.analyze_file(file_path)
        fan_scaled = (fan_rep.coverage_percentage / 100.0) * 35.0
        for m in fan_rep.missing_branches:
            recs.append(f"Fan-out gap: missing {m}.")

        # 3. Schema.org Semantic Markup (Weight: 15%)
        schema_score = 0.0
        has_schema = '<script type="application/ld+json">' in content
        if has_schema:
            schema_score += 5.0
            if any(t in content for t in ["Product", "Article"]):
                schema_score += 5.0
            if "FAQPage" in content:
                schema_score += 3.0
            if "BreadcrumbList" in content:
                schema_score += 2.0
        else:
            recs.append("Missing JSON-LD schema. Add Product or Article structured data for entity recognition.")

        # 4. Information Gain (Local Pakistani Marketplace Data) (Weight: 15%)
        ig_score = 0.0
        if re.search(r"\b(?:Rs\.?|PKR)\s*[\d,]+", content, re.IGNORECASE):
            ig_score += 4.0
        if re.search(r"\b(?:EasyPaisa|JazzCash|SadaPay)\b", content, re.IGNORECASE):
            ig_score += 4.0
        if re.search(r"\b(?:warranty|replacement)\b", content, re.IGNORECASE):
            ig_score += 4.0
        if "wa.me/" in content or "WhatsApp" in content:
            ig_score += 3.0

        total = round(ext_scaled + fan_scaled + schema_score + ig_score, 1)

        if total >= 90.0:
            tier = "ELITE_AIO_READY"
        elif total >= 75.0:
            tier = "AIO_COMPLIANT"
        else:
            tier = "NEEDS_OPTIMIZATION"

        return PageAIOScore(
            file_path=str(file_path),
            url_slug=slug,
            extractability_score=round(ext_scaled, 1),
            fanout_score=round(fan_scaled, 1),
            schema_score=round(schema_score, 1),
            information_gain_score=round(ig_score, 1),
            total_aio_score=total,
            tier=tier,
            recommendations=recs,
        )

    def audit_entire_site(self) -> Dict[str, Any]:
        """Audits all canonical tool and guide pages."""
        tool_scores: List[PageAIOScore] = []
        guide_scores: List[PageAIOScore] = []

        tools_dir = self.project_dir / "tools"
        if tools_dir.exists():
            for p in sorted(tools_dir.glob("*/index.html")):
                tool_scores.append(self.score_page(p))

        guides_dir = self.project_dir / "guides"
        if guides_dir.exists():
            for p in sorted(guides_dir.glob("*/index.html")):
                guide_scores.append(self.score_page(p))

        all_scores = tool_scores + guide_scores
        avg_score = round(sum(s.total_aio_score for s in all_scores) / max(1, len(all_scores)), 1)
        elite_count = sum(1 for s in all_scores if s.tier == "ELITE_AIO_READY")
        compliant_count = sum(1 for s in all_scores if s.tier == "AIO_COMPLIANT")
        needs_opt_count = sum(1 for s in all_scores if s.tier == "NEEDS_OPTIMIZATION")

        return {
            "total_pages_audited": len(all_scores),
            "average_aio_score": avg_score,
            "elite_aio_ready": elite_count,
            "aio_compliant": compliant_count,
            "needs_optimization": needs_opt_count,
            "tool_pages": [s.__dict__ for s in tool_scores],
            "guide_pages": [s.__dict__ for s in guide_scores],
        }
