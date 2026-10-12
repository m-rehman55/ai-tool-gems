#!/usr/bin/env python3
"""
Content Quality & AI Search Discoverability Auditor
---------------------------------------------------
Enforces rigorous in-depth content standards:
1. Word count thresholds (guides >= 1,200 words, tool pages >= 400 words).
2. Anti-stuffing & excessive term frequency checks.
3. Raw markdown leaks (##) and placeholder text detection.
4. AI Answer Engine (GEO/AEO) discoverability signals (FAQs, comparison tables, verified PKR prices).
"""

from __future__ import annotations
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from agent.crawler import CrawledPage

IGNORED_COMMON_ENTITIES = {
    "pakistan", "subscription", "delivery", "payment", "easypaisa", "jazzcash",
    "developer", "developers", "pricing", "claude", "sonnet", "cursor", "leonardo",
    "canva", "figma", "capcut", "anthropic", "openai", "google", "replit", "lovable",
    "month", "months", "yearly", "annual", "access", "features", "official", "instant"
}

@dataclass
class QualityIssue:
    check_type: str
    message: str
    severity: str  # ERROR, WARNING
    url: str

@dataclass
class ContentQualityReport:
    url: str
    word_count: int
    quality_score: int
    passed: bool
    issues: List[QualityIssue] = field(default_factory=list)
    ai_search_readiness: Dict[str, bool] = field(default_factory=dict)

class ContentQualityAuditor:
    """Evaluates editorial depth, keyword density, and AI discoverability."""

    def __init__(self, guide_min_words: int = 1200, tool_min_words: int = 400):
        self.guide_min_words = guide_min_words
        self.tool_min_words = tool_min_words

    def audit_page_content(self, page: CrawledPage) -> ContentQualityReport:
        issues: List[QualityIssue] = []
        raw = page.raw_html
        url = page.url
        score = 100

        # 1. Unfinished templates or placeholder text
        if re.search(r"\b(TODO|PLACEHOLDER|TBD|LOREM IPSUM)\b", raw, re.IGNORECASE):
            issues.append(
                QualityIssue(
                    check_type="PLACEHOLDER_TEXT",
                    message="Detected unfinished placeholder text (TODO/TBD/Lorem Ipsum)",
                    severity="ERROR",
                    url=url,
                )
            )
            score -= 30

        # 2. Raw Markdown leakage
        if "## " in raw:
            issues.append(
                QualityIssue(
                    check_type="MARKDOWN_LEAK",
                    message="Detected raw Markdown syntax (## ) leaked into HTML body",
                    severity="ERROR",
                    url=url,
                )
            )
            score -= 20

        # 3. Word Count Thresholds
        is_guide = "/guides/" in url
        is_tool = "/tools/" in url
        min_words = self.guide_min_words if is_guide else (self.tool_min_words if is_tool else 300)

        if page.word_count < min_words:
            issues.append(
                QualityIssue(
                    check_type="WORD_COUNT_SHORTFALL",
                    message=f"Word count ({page.word_count}) below in-depth standard of {min_words} words",
                    severity="WARNING" if not is_guide else "ERROR",
                    url=url,
                )
            )
            score -= 25

        # 4. Anti-Stuffing & Repetition
        plain = re.sub(r"<[^>]+>", " ", raw).lower()
        words = re.findall(r"\b[a-z0-9_-]{5,}\b", plain)
        freq: Dict[str, int] = {}
        for w in words:
            freq[w] = freq.get(w, 0) + 1

        for w, cnt in freq.items():
            if w not in IGNORED_COMMON_ENTITIES and cnt > 30:
                issues.append(
                    QualityIssue(
                        check_type="KEYWORD_STUFFING",
                        message=f"Suspicious word repetition: '{w}' repeated {cnt} times (threshold: 30)",
                        severity="ERROR",
                        url=url,
                    )
                )
                score -= 15

        # 5. AI Search Discoverability Signals (GEO / AEO)
        ai_readiness = {
            "has_faq": bool(re.search(r"class=[\"'][^\"']*faq[^\"']*[\"']|id=[\"']faq[\"']|<dt>", raw, re.IGNORECASE)),
            "has_comparison_table": "<table" in raw.lower() or "comparison" in raw.lower(),
            "has_pkr_price": "pkr" in plain or "rs." in plain,
            "has_pakistan_payment": "easypaisa" in plain or "jazzcash" in plain,
        }

        # Bonus/penalty for AI search features
        if not ai_readiness["has_faq"] and is_guide:
            issues.append(
                QualityIssue(
                    check_type="AI_SEARCH_MISSING_FAQ",
                    message="Guide page missing FAQ section for AI Answer Engine citation",
                    severity="WARNING",
                    url=url,
                )
            )
            score -= 10

        passed = len([i for i in issues if i.severity == "ERROR"]) == 0
        final_score = max(0, min(100, score))

        return ContentQualityReport(
            url=url,
            word_count=page.word_count,
            quality_score=final_score,
            passed=passed,
            issues=issues,
            ai_search_readiness=ai_readiness,
        )
