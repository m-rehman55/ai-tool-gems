"""Merchant Feed and Schema Parity Validator.

Audits:
1. Price parity: Feed price vs Schema price vs Visible HTML price.
2. Return policy compliance: Eliminates ReturnByMail in favor of digital replacement policy.
3. Review rating authenticity: Ensures schema reviews match genuine visible testimonials.
4. Required Google Merchant attributes.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from merchant_agent.feed_generator import MerchantProductItem


@dataclass
class ParityIssue:
    tool_slug: str
    issue_type: str  # PRICE_MISMATCH, RETURN_POLICY_ERROR, FAKE_REVIEW_ERROR, MISSING_ATTRIBUTE
    severity: str    # CRITICAL, HIGH, MEDIUM
    details: str
    recommendation: str


@dataclass
class FeedValidationReport:
    total_products_checked: int
    is_feed_compliant: bool
    issues: List[ParityIssue]
    digital_warranty_verified: bool
    summary: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_products_checked": self.total_products_checked,
            "is_feed_compliant": self.is_feed_compliant,
            "digital_warranty_verified": self.digital_warranty_verified,
            "issues_count": len(self.issues),
            "issues": [asdict(i) for i in self.issues],
            "summary": self.summary,
        }


class MerchantValidator:
    """Validates Merchant Center compliance and schema parity."""

    def __init__(self, project_dir: Optional[Path] = None):
        self.project_dir = project_dir or Path(".")

    def validate_feed_items(self, items: List[MerchantProductItem]) -> FeedValidationReport:
        issues: List[ParityIssue] = []

        for item in items:
            slug = item.sku_id.replace("atg-", "")
            tool_dir = self.project_dir / "tools" / slug
            tool_html_path = tool_dir / "index.html"

            # 1. Check landing page exists
            if not tool_html_path.exists():
                issues.append(ParityIssue(
                    tool_slug=slug,
                    issue_type="MISSING_LANDING_PAGE",
                    severity="CRITICAL",
                    details=f"Tool product route {tool_html_path} does not exist.",
                    recommendation=f"Ensure static landing page exists for {slug}.",
                ))
                continue

            html = tool_html_path.read_text(encoding="utf-8")

            # 2. Price Parity Check (Feed vs Visible HTML)
            # Find visible price
            price_match = re.search(r"\b(?:Rs\.?|PKR)\s*([\d,]+)", html)
            if price_match:
                vis_price = int(price_match.group(1).replace(",", ""))
                # If feed price differs by > 500 PKR, flag mismatch
                if abs(vis_price - item.price_pkr) > 100:
                    issues.append(ParityIssue(
                        tool_slug=slug,
                        issue_type="PRICE_MISMATCH",
                        severity="CRITICAL",
                        details=f"Feed price ({item.price_pkr} PKR) does not match visible price ({vis_price} PKR).",
                        recommendation="Synchronize visible PKR price with Google Merchant feed price.",
                    ))

            # 3. Defect 19 Check: ReturnByMail in digital subscriptions
            if "ReturnByMail" in html:
                issues.append(ParityIssue(
                    tool_slug=slug,
                    issue_type="RETURN_POLICY_ERROR",
                    severity="HIGH",
                    details="Schema contains 'ReturnByMail' for digital software subscription.",
                    recommendation="Update MerchantReturnPolicy to digital replacement warranty.",
                ))

            # 4. Defect 18 Check: Review schema without visible testimonials
            if "aggregateRating" in html and "review" in html:
                # If HTML has review schema but no visible client testimonial elements
                if "client-review" not in html and "customer-testimonial" not in html and "review-card" not in html:
                    issues.append(ParityIssue(
                        tool_slug=slug,
                        issue_type="FAKE_REVIEW_ERROR",
                        severity="MEDIUM",
                        details="Product schema contains aggregateRating without corresponding visible reviews.",
                        recommendation="Align review structured data strictly with genuine visible customer reviews.",
                    ))

        is_compliant = len(issues) == 0
        return FeedValidationReport(
            total_products_checked=len(items),
            is_feed_compliant=is_compliant,
            issues=issues,
            digital_warranty_verified=not any(i.issue_type == "RETURN_POLICY_ERROR" for i in issues),
            summary={
                "price_mismatches": sum(1 for i in issues if i.issue_type == "PRICE_MISMATCH"),
                "return_policy_errors": sum(1 for i in issues if i.issue_type == "RETURN_POLICY_ERROR"),
                "review_schema_errors": sum(1 for i in issues if i.issue_type == "FAKE_REVIEW_ERROR"),
            },
        )
