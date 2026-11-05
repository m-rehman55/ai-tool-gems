"""On-Page Answer Readiness & GEO/AEO Quality Evaluator.

Evaluates the 11 core GEO/AEO direct-answer criteria specified in HERMES Section 3.9:
1. Clear product information
2. Verifiable claims
3. Helpful comparisons
4. Original research
5. Clear author & publisher identity
6. Source references
7. Content freshness
8. Crawlability & Indexability
9. Structured data consistency
10. Strong entity relationships
11. Trust & warranty signals

Strictly separated from measured external AI search engine citations.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ReadinessCriterion:
    name: str
    weight: float
    score: float
    passed: bool
    evidence: str
    recommendation: Optional[str] = None


@dataclass
class AnswerReadinessReport:
    file_path: str
    url_slug: str
    total_score: float  # 0 to 100
    grade: str          # EXCELLENT (90+), GOOD (75+), NEEDS_WORK (<75)
    criteria: List[ReadinessCriterion]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file_path": self.file_path,
            "url_slug": self.url_slug,
            "total_score": round(self.total_score, 1),
            "grade": self.grade,
            "criteria": [asdict(c) for c in self.criteria],
            "recommendations": self.recommendations,
        }


class AnswerReadinessEvaluator:
    """Evaluates local HTML files against official GEO/AEO standards."""

    def evaluate_file(self, file_path: Path) -> AnswerReadinessReport:
        content = file_path.read_text(encoding="utf-8")
        slug = file_path.parent.name if file_path.name == "index.html" else file_path.stem
        criteria: List[ReadinessCriterion] = []
        recommendations: List[str] = []

        # 1. Clear Product Information (Weight: 10)
        has_name = bool(re.search(r"<h1[^>]*>.*?</h1>", content, re.DOTALL | re.IGNORECASE))
        has_pkr = bool(re.search(r"\b(?:Rs\.?|PKR)\s*[\d,]+", content, re.IGNORECASE))
        has_features = bool(re.search(r"<(?:ul|ol|table)[^>]*>.*?</(?:ul|ol|table)>", content, re.DOTALL | re.IGNORECASE))
        prod_score = (4.0 if has_name else 0.0) + (4.0 if has_pkr else 0.0) + (2.0 if has_features else 0.0)
        criteria.append(ReadinessCriterion(
            name="clear_product_info",
            weight=10.0,
            score=prod_score,
            passed=prod_score >= 8.0,
            evidence=f"H1: {has_name}, PKR Pricing: {has_pkr}, Feature Lists: {has_features}",
            recommendation=None if prod_score >= 8.0 else "Add explicit H1 product title and verified PKR pricing.",
        ))

        # 2. Verifiable Claims (Weight: 10)
        has_delivery = bool(re.search(r"\b(?:5[-–]15\s*min|instant|activation)\b", content, re.IGNORECASE))
        has_domestic_rails = bool(re.search(r"\b(?:EasyPaisa|JazzCash|SadaPay|NayaPay|Raast)\b", content, re.IGNORECASE))
        claims_score = (5.0 if has_delivery else 0.0) + (5.0 if has_domestic_rails else 0.0)
        criteria.append(ReadinessCriterion(
            name="verifiable_claims",
            weight=10.0,
            score=claims_score,
            passed=claims_score >= 8.0,
            evidence=f"Delivery Timeline: {has_delivery}, Verified Payment Rails: {has_domestic_rails}",
            recommendation=None if claims_score >= 8.0 else "Include verifiable delivery timeline and verified domestic payment rails.",
        ))

        # 3. Helpful Comparisons (Weight: 10)
        has_table = "<table" in content.lower()
        has_vs = bool(re.search(r"\b(?:vs|comparison|alternatives|difference)\b", content, re.IGNORECASE))
        comp_score = (6.0 if has_table else 0.0) + (4.0 if has_vs else 0.0)
        criteria.append(ReadinessCriterion(
            name="helpful_comparisons",
            weight=10.0,
            score=comp_score,
            passed=comp_score >= 6.0,
            evidence=f"Comparison Table: {has_table}, Versus/Alternative Terminology: {has_vs}",
            recommendation=None if comp_score >= 6.0 else "Embed structured comparison table or alternative analysis.",
        ))

        # 4. Original Research & Local Context (Weight: 10)
        has_local_demand = bool(re.search(r"\b(?:Pakistan|Pakistani|freelancers?|students?)\b", content, re.IGNORECASE))
        has_unique_data = bool(re.search(r"\b(?:verified|tested|benchmark|tested in)\b", content, re.IGNORECASE))
        orig_score = (5.0 if has_local_demand else 0.0) + (5.0 if has_unique_data else 0.0)
        criteria.append(ReadinessCriterion(
            name="original_research_local",
            weight=10.0,
            score=orig_score,
            passed=orig_score >= 8.0,
            evidence=f"Pakistani Target Context: {has_local_demand}, Empirical Testing Language: {has_unique_data}",
            recommendation=None if orig_score >= 8.0 else "Incorporate empirical testing insights tailored for Pakistani professionals.",
        ))

        # 5. Clear Author & Publisher Identity (Weight: 10)
        has_author = bool(re.search(r'<(?:meta|span|p|a)[^>]*(?:author|publisher|byline)[^>]*>|AIToolGems', content, re.IGNORECASE))
        has_org = "Organization" in content
        ident_score = (6.0 if has_author else 0.0) + (4.0 if has_org else 0.0)
        criteria.append(ReadinessCriterion(
            name="author_publisher_identity",
            weight=10.0,
            score=ident_score,
            passed=ident_score >= 6.0,
            evidence=f"Author/Brand Mention: {has_author}, Organization Schema: {has_org}",
            recommendation=None if ident_score >= 6.0 else "Add explicit author byline or publisher entity reference.",
        ))

        # 6. Source References (Weight: 8)
        has_outbound = bool(re.search(r'<a\s+[^>]*href=["\']https?://(?!aitoolgems\.tech)[^"\']+["\']', content, re.IGNORECASE))
        src_score = 8.0 if has_outbound else 4.0
        criteria.append(ReadinessCriterion(
            name="source_references",
            weight=8.0,
            score=src_score,
            passed=has_outbound,
            evidence=f"External Source Citations Present: {has_outbound}",
            recommendation=None if has_outbound else "Add reference citations to official tool documentation or research.",
        ))

        # 7. Content Freshness (Weight: 8)
        has_2026 = "2026" in content
        has_datemod = "dateModified" in content
        fresh_score = (5.0 if has_2026 else 0.0) + (3.0 if has_datemod else 0.0)
        criteria.append(ReadinessCriterion(
            name="content_freshness",
            weight=8.0,
            score=fresh_score,
            passed=fresh_score >= 5.0,
            evidence=f"Year 2026 Currency: {has_2026}, dateModified Schema: {has_datemod}",
            recommendation=None if fresh_score >= 5.0 else "Ensure current year (2026) context and dateModified structured data.",
        ))

        # 8. Crawlability & Indexability (Weight: 10)
        is_noindex = '<meta name="robots" content="noindex' in content.lower()
        has_canonical = '<link rel="canonical"' in content.lower()
        crawl_score = (0.0 if is_noindex else 5.0) + (5.0 if has_canonical else 0.0)
        criteria.append(ReadinessCriterion(
            name="crawlability_indexability",
            weight=10.0,
            score=crawl_score,
            passed=crawl_score >= 10.0,
            evidence=f"Noindex: {is_noindex}, Canonical Link: {has_canonical}",
            recommendation=None if crawl_score >= 10.0 else "Ensure canonical tag is present and noindex is removed.",
        ))

        # 9. Structured Data Consistency (Weight: 8)
        has_json_ld = '<script type="application/ld+json">' in content
        schema_consistent = has_json_ld and ('"@context": "https://schema.org"' in content or '"@context":"https://schema.org"' in content)
        struct_score = 8.0 if schema_consistent else (4.0 if has_json_ld else 0.0)
        criteria.append(ReadinessCriterion(
            name="structured_data_consistency",
            weight=8.0,
            score=struct_score,
            passed=schema_consistent,
            evidence=f"Schema.org JSON-LD: {schema_consistent}",
            recommendation=None if schema_consistent else "Implement valid Schema.org Product, FAQ, or Article JSON-LD markup.",
        ))

        # 10. Strong Entity Relationships (Weight: 8)
        has_about = bool(re.search(r'"(?:about|mentions|isSimilarTo|knowsAbout)"', content))
        has_faq = "FAQPage" in content
        entity_score = (4.0 if has_about else 0.0) + (4.0 if has_faq else 0.0)
        criteria.append(ReadinessCriterion(
            name="entity_relationships",
            weight=8.0,
            score=entity_score,
            passed=entity_score >= 4.0,
            evidence=f"Semantic Relations: {has_about}, FAQ Schema: {has_faq}",
            recommendation=None if entity_score >= 4.0 else "Add FAQPage schema or semantic entity associations.",
        ))

        # 11. Trust Signals & Warranty (Weight: 8)
        has_warranty = bool(re.search(r"\b(?:warranty|replacement|guarantee)\b", content, re.IGNORECASE))
        has_support = "wa.me/" in content or "WhatsApp" in content
        trust_score = (4.0 if has_warranty else 0.0) + (4.0 if has_support else 0.0)
        criteria.append(ReadinessCriterion(
            name="trust_signals_warranty",
            weight=8.0,
            score=trust_score,
            passed=trust_score >= 8.0,
            evidence=f"Replacement Warranty: {has_warranty}, Direct WhatsApp Desk: {has_support}",
            recommendation=None if trust_score >= 8.0 else "Highlight replacement warranty and responsive WhatsApp support.",
        ))

        total_score = sum(c.score for c in criteria)
        for c in criteria:
            if c.recommendation:
                recommendations.append(f"[{c.name}] {c.recommendation}")

        if total_score >= 90.0:
            grade = "EXCELLENT"
        elif total_score >= 75.0:
            grade = "GOOD"
        else:
            grade = "NEEDS_WORK"

        return AnswerReadinessReport(
            file_path=str(file_path),
            url_slug=slug,
            total_score=total_score,
            grade=grade,
            criteria=criteria,
            recommendations=recommendations,
        )
