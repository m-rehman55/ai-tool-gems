#!/usr/bin/env python3
"""
Technical SEO Audit for AIToolGems Autonomous Growth Agent
----------------------------------------------------------
Inspects crawlability, indexing directives, canonical consistency,
metadata lengths, heading hierarchy, image accessibility, and viewport.
"""

from __future__ import annotations
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from agent.crawler import CrawledPage

@dataclass
class AuditIssue:
    severity: str        # P0_CRITICAL, P1_HIGH, P2_MEDIUM, P3_LOW
    check_type: str      # CANONICAL, TITLE, META_DESC, H1, IMAGE_ALT, STATUS_CODE, NOINDEX, SCHEMA
    url: str
    message: str
    details: Optional[str] = None
    file_path: Optional[str] = None

@dataclass
class TechnicalAuditReport:
    total_pages_audited: int
    clean_pages_count: int
    issues_by_severity: Dict[str, int] = field(default_factory=lambda: {
        "P0_CRITICAL": 0,
        "P1_HIGH": 0,
        "P2_MEDIUM": 0,
        "P3_LOW": 0,
    })
    issues: List[AuditIssue] = field(default_factory=list)
    score: int = 100

class TechnicalAuditor:
    """Performs rigorous Google / Bing Search Central compliant technical audits."""

    def __init__(self, base_url: str = "https://aitoolgems.tech"):
        self.base_url = base_url.rstrip("/")

    def audit_page(self, page: CrawledPage) -> List[AuditIssue]:
        issues: List[AuditIssue] = []

        # 1. HTTP Status Code
        if page.status_code != 200:
            issues.append(
                AuditIssue(
                    severity="P0_CRITICAL",
                    check_type="STATUS_CODE",
                    url=page.url,
                    message=f"Non-200 HTTP status returned: {page.status_code}",
                    details=page.error,
                    file_path=page.file_path,
                )
            )
            return issues  # Do not audit empty or broken response body

        # 2. Robots Indexing Directives (Utility pages like 404/admin are expected to be noindexed)
        is_utility_page = any(u in page.url for u in ["404.html", "admin.html", "googleb36d12ee905644d9", "gsc_daily_checklist"])
        if page.robots_meta and "noindex" in page.robots_meta.lower():
            if not is_utility_page:
                issues.append(
                    AuditIssue(
                        severity="P0_CRITICAL",
                        check_type="NOINDEX",
                        url=page.url,
                        message=f"Production page blocked by 'noindex' directive: '{page.robots_meta}'",
                        file_path=page.file_path,
                    )
                )

        # 3. Canonical URL
        if not page.canonical:
            if not is_utility_page:
                issues.append(
                    AuditIssue(
                        severity="P1_HIGH",
                        check_type="CANONICAL",
                        url=page.url,
                        message="Missing canonical link element",
                        file_path=page.file_path,
                    )
                )
        elif not page.canonical.startswith(self.base_url):
            issues.append(
                AuditIssue(
                    severity="P0_CRITICAL",
                    check_type="CANONICAL",
                    url=page.url,
                    message=f"Canonical URL points outside domain: '{page.canonical}'",
                    file_path=page.file_path,
                )
            )

        # 4. Title Tag (20 - 65 chars recommended)
        title_len = len(page.title)
        if title_len == 0:
            issues.append(
                AuditIssue(
                    severity="P0_CRITICAL",
                    check_type="TITLE",
                    url=page.url,
                    message="Missing <title> tag",
                    file_path=page.file_path,
                )
            )
        elif title_len < 20 or title_len > 70:
            issues.append(
                AuditIssue(
                    severity="P2_MEDIUM",
                    check_type="TITLE",
                    url=page.url,
                    message=f"Title length ({title_len} chars) outside optimal 20–70 bounds: '{page.title}'",
                    file_path=page.file_path,
                )
            )

        # 5. Meta Description (70 - 170 chars recommended)
        desc_len = len(page.meta_description)
        if desc_len == 0:
            if not is_utility_page:
                issues.append(
                    AuditIssue(
                        severity="P1_HIGH",
                        check_type="META_DESC",
                        url=page.url,
                        message="Missing meta description",
                        file_path=page.file_path,
                    )
                )
        elif desc_len < 70 or desc_len > 180:
            issues.append(
                AuditIssue(
                    severity="P2_MEDIUM",
                    check_type="META_DESC",
                    url=page.url,
                    message=f"Meta description length ({desc_len} chars) outside optimal 70–180 bounds",
                    details=page.meta_description[:100] + "...",
                    file_path=page.file_path,
                )
            )

        # 6. Heading 1 Structure (Exactly 1 required)
        h1_count = len(page.h1_list)
        if h1_count == 0:
            issues.append(
                AuditIssue(
                    severity="P1_HIGH",
                    check_type="H1",
                    url=page.url,
                    message="Missing H1 heading on page",
                    file_path=page.file_path,
                )
            )
        elif h1_count > 1:
            issues.append(
                AuditIssue(
                    severity="P2_MEDIUM",
                    check_type="H1",
                    url=page.url,
                    message=f"Multiple H1 tags ({h1_count}) found on page",
                    details="; ".join(page.h1_list[:3]),
                    file_path=page.file_path,
                )
            )

        # 7. Images Alt Attribute
        images_missing_alt = [img["src"] for img in page.images if not img.get("alt", "").strip()]
        if images_missing_alt:
            issues.append(
                AuditIssue(
                    severity="P2_MEDIUM",
                    check_type="IMAGE_ALT",
                    url=page.url,
                    message=f"{len(images_missing_alt)} image(s) missing alt text",
                    details="; ".join(images_missing_alt[:3]),
                    file_path=page.file_path,
                )
            )

        # 8. Viewport Tag
        if page.raw_html and not re.search(r"<meta[^>]+name=[\"']viewport[\"']", page.raw_html, re.IGNORECASE):
            issues.append(
                AuditIssue(
                    severity="P1_HIGH",
                    check_type="VIEWPORT",
                    url=page.url,
                    message="Missing mobile viewport meta tag",
                    file_path=page.file_path,
                )
            )

        return issues

    def audit_crawl(self, pages: List[CrawledPage]) -> TechnicalAuditReport:
        all_issues: List[AuditIssue] = []
        clean_count = 0

        for page in pages:
            page_issues = self.audit_page(page)
            if page_issues:
                all_issues.extend(page_issues)
            else:
                clean_count += 1

        counts = {
            "P0_CRITICAL": sum(1 for i in all_issues if i.severity == "P0_CRITICAL"),
            "P1_HIGH": sum(1 for i in all_issues if i.severity == "P1_HIGH"),
            "P2_MEDIUM": sum(1 for i in all_issues if i.severity == "P2_MEDIUM"),
            "P3_LOW": sum(1 for i in all_issues if i.severity == "P3_LOW"),
        }

        # Calculate score (100 base, deductions for P0: -25, P1: -5, P2: -2, P3: -1)
        deduction = (counts["P0_CRITICAL"] * 25) + (counts["P1_HIGH"] * 5) + (counts["P2_MEDIUM"] * 2) + counts["P3_LOW"]
        score = max(0, 100 - deduction)

        return TechnicalAuditReport(
            total_pages_audited=len(pages),
            clean_pages_count=clean_count,
            issues_by_severity=counts,
            issues=all_issues,
            score=score,
        )
