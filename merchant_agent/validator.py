"""Merchant Feed and Schema Parity Validator.

Audits:
1. Offer-level policy compliance: Differentiates Merchant Center Shopping from Google Ads Search.
2. Prohibits ineligible feed submissions: Blocks shared accounts, academic cheating aids, and terms < 12m.
3. Price parity: Feed price vs Schema price vs Visible HTML price.
4. Return policy compliance: Eliminates ReturnByMail in favor of digital replacement policy.
5. Review rating authenticity: Ensures schema reviews match genuine visible testimonials.
6. Required Google Merchant attributes.
"""

from __future__ import annotations

import json
import re
import struct
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from merchant_agent.feed_generator import MerchantFeedGenerator, MerchantProductItem, OfferPolicyAssessment


def _get_png_dimensions(path: Path) -> Tuple[int, int]:
    """Reads PNG image dimensions using standard library struct with Pillow fallback."""
    try:
        with open(path, "rb") as f:
            header = f.read(24)
            if header.startswith(b"\x89PNG\r\n\x1a\n") and header[12:16] == b"IHDR":
                return struct.unpack(">II", header[16:24])
    except Exception:
        pass
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        pass
    return 0, 0


@dataclass
class ParityIssue:
    tool_slug: str
    issue_type: str  # PRICE_MISMATCH, RETURN_POLICY_ERROR, FAKE_REVIEW_ERROR, MISSING_ATTRIBUTE, INELIGIBLE_FEED_ITEM
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
        self.feed_generator = MerchantFeedGenerator(self.project_dir)

    def validate_feed_items(self, items: List[MerchantProductItem]) -> FeedValidationReport:
        issues: List[ParityIssue] = []

        prohibited_slugs = {"turnitin", "netflix", "surfshark", "semrush", "veo"}

        for item in items:
            slug = item.sku_id.replace("atg-", "")
            tool_dir = self.project_dir / "tools" / slug
            tool_html_path = tool_dir / "index.html"

            # 0. Check against strict prohibited / policy violation list in Shopping feed
            if slug in prohibited_slugs:
                issues.append(ParityIssue(
                    tool_slug=slug,
                    issue_type="INELIGIBLE_FEED_ITEM",
                    severity="CRITICAL",
                    details=f"Tool '{slug}' is strictly ineligible for Google Merchant Center (policy violation / shared account).",
                    recommendation="Remove offer from active Merchant Center feed and record in merchant_hold_register.json.",
                ))

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
            price_match = re.search(r"\b(?:Rs\.?|PKR)\s*([\d,]+)", html)
            if price_match:
                vis_price = int(price_match.group(1).replace(",", ""))
                # If feed price differs by > 100 PKR, flag mismatch
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
                if "client-review" not in html and "customer-testimonial" not in html and "review-card" not in html:
                    issues.append(ParityIssue(
                        tool_slug=slug,
                        issue_type="FAKE_REVIEW_ERROR",
                        severity="MEDIUM",
                        details="Product schema contains aggregateRating without corresponding visible reviews.",
                        recommendation="Align review structured data strictly with genuine visible customer reviews.",
                    ))

            # 5. Google Merchant Center Image Dimensions Check (Minimum 100x100 px)
            logo_path = self.project_dir / "assets" / "product-logos" / f"{slug}.png"
            if not logo_path.exists():
                logo_path = self.project_dir / "assets" / f"{slug}.png"
            if logo_path.exists():
                try:
                    w, h = _get_png_dimensions(logo_path)
                    if w < 100 or h < 100:
                        issues.append(ParityIssue(
                            tool_slug=slug,
                            issue_type="IMAGE_DIMENSION_ERROR",
                            severity="CRITICAL",
                            details=f"Image dimensions ({w}x{h}) are below Google Merchant Center minimum requirement of 100x100 pixels.",
                            recommendation=f"Upscale or replace {slug}.png to at least 256x256 pixels.",
                        ))
                except Exception as img_err:
                    issues.append(ParityIssue(
                        tool_slug=slug,
                        issue_type="IMAGE_DIMENSION_ERROR",
                        severity="HIGH",
                        details=f"Unable to read image {logo_path}: {img_err}",
                        recommendation=f"Ensure valid PNG image exists for {slug}.",
                    ))

            # 6. Country & Currency Enforcement (Pakistan PK and PKR exclusively)
            if item.shipping_country != "PK":
                issues.append(ParityIssue(
                    tool_slug=slug,
                    issue_type="SHIPPING_COUNTRY_ERROR",
                    severity="CRITICAL",
                    details=f"Unsupported shipping country '{item.shipping_country}'. Only Pakistan ('PK') is permitted.",
                    recommendation="Set shipping country to 'PK' and restrict feed targeting to Pakistan.",
                ))

            if not item.shipping_price.endswith("PKR"):
                issues.append(ParityIssue(
                    tool_slug=slug,
                    issue_type="UNSUPPORTED_CURRENCY_ERROR",
                    severity="CRITICAL",
                    details=f"Shipping price currency '{item.shipping_price}' is unsupported. Only PKR is accepted.",
                    recommendation="Ensure shipping price is specified in PKR (e.g., '0.00 PKR').",
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
                "ineligible_feed_items": sum(1 for i in issues if i.issue_type == "INELIGIBLE_FEED_ITEM"),
                "image_dimension_errors": sum(1 for i in issues if i.issue_type == "IMAGE_DIMENSION_ERROR"),
                "shipping_country_errors": sum(1 for i in issues if i.issue_type == "SHIPPING_COUNTRY_ERROR"),
                "currency_errors": sum(1 for i in issues if i.issue_type == "UNSUPPORTED_CURRENCY_ERROR"),
            },
        )

    def validate_offer_policy_compliance(self) -> Dict[str, Any]:
        """Comprehensive audit of all 40 catalog tools across Merchant Center and Google Ads."""
        assessments = self.feed_generator.evaluate_all_catalog_offers()
        
        mc_summary: Dict[str, int] = {}
        gads_summary: Dict[str, int] = {}

        for a in assessments:
            mc_summary[a.merchant_center_status] = mc_summary.get(a.merchant_center_status, 0) + 1
            gads_summary[a.google_ads_search_status] = gads_summary.get(a.google_ads_search_status, 0) + 1

        return {
            "total_catalog_offers": len(assessments),
            "merchant_center_breakdown": mc_summary,
            "google_ads_search_breakdown": gads_summary,
            "all_merchant_items_on_hold": all(a.merchant_center_status != "ELIGIBLE" for a in assessments),
            "google_ads_search_eligible_count": gads_summary.get("PRELIMINARY_POLICY_REVIEW", 0),
        }
