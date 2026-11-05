"""
conversion_agent.friction_detector - Identifies conversion friction, UX obstacles, and checkout hurdles.
"""

from dataclasses import dataclass, field
import re
from typing import Dict, List, Any


@dataclass
class FrictionIssue:
    severity: str  # HIGH, MEDIUM, LOW
    category: str  # CTA, PRICING, FAQ, MOBILE, CLARITY
    description: str
    remediation: str


@dataclass
class FrictionAuditReport:
    identifier: str
    friction_score: float  # 0 to 100, where 100 means zero friction (ideal)
    issues: List[FrictionIssue] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)


class FrictionDetector:
    """
    Scans HTML pages for conversion friction points:
    - Missing or un-prefilled WhatsApp CTAs
    - Missing plan type clarification (private vs shared)
    - Ambiguous renewal or delivery terms
    - Empty anchor placeholders (href="#")
    - Absence of FAQs answering core purchase objections
    """

    def analyze_page(self, html_content: str, identifier: str = "inline") -> FrictionAuditReport:
        issues: List[FrictionIssue] = []
        metrics: Dict[str, Any] = {}
        html_lower = html_content.lower()

        # 1. Inspect WhatsApp CTA and Prefill
        wa_links = re.findall(r'href=[\'"](https?://wa\.me/[^\'"\s]+|https?://api\.whatsapp\.com/[^\'"\s]+)[\'"]', html_content)
        metrics["whatsapp_links_count"] = len(wa_links)
        
        has_prefill = False
        valid_phone = False
        for link in wa_links:
            if "text=" in link:
                has_prefill = True
            if "923288823293" in link or "92" in link:
                valid_phone = True

        if not wa_links:
            # Check if there is data-action or JS-driven whatsapp button
            has_js_wa = "openwhatsapp" in html_lower or "whatsapp" in html_lower
            metrics["has_js_wa"] = has_js_wa
            if not has_js_wa:
                issues.append(FrictionIssue(
                    severity="HIGH",
                    category="CTA",
                    description="No direct WhatsApp conversion CTA found on page.",
                    remediation="Add sticky or high-visibility WhatsApp order button."
                ))
        else:
            if not has_prefill:
                issues.append(FrictionIssue(
                    severity="MEDIUM",
                    category="CTA",
                    description="WhatsApp link missing pre-filled message text. User lands on blank chat.",
                    remediation="Include prefilled query parameter e.g. ?text=Hi%20AI%20Tool%20Gems,%20I%20want%20to%20order..."
                ))
            if not valid_phone:
                issues.append(FrictionIssue(
                    severity="HIGH",
                    category="CTA",
                    description="WhatsApp phone number missing country code +92.",
                    remediation="Format phone number with country code 923288823293."
                ))

        # 2. Plan clarity (private vs shared / subscription duration)
        has_plan_type = bool("shared" in html_lower or "private" in html_lower or "account" in html_lower or "subscription" in html_lower)
        metrics["has_plan_clarity"] = has_plan_type
        if not has_plan_type:
            issues.append(FrictionIssue(
                severity="MEDIUM",
                category="PRICING",
                description="Account access type (Shared vs Private) is not clearly articulated.",
                remediation="Explicitly specify whether the tier is a Shared profile or Private login."
            ))

        # 3. Dead placeholder links
        dead_hash_links = re.findall(r'href=[\'"]#[\'"]', html_content)
        metrics["dead_hash_links"] = len(dead_hash_links)
        if len(dead_hash_links) > 3:
            issues.append(FrictionIssue(
                severity="LOW",
                category="MOBILE",
                description=f"Detected {len(dead_hash_links)} empty href='#' placeholders causing user scroll jumps.",
                remediation="Replace href='#' with semantic buttons or explicit anchor fragment IDs."
            ))

        # 4. FAQ Objection Handling
        has_faq = bool("faq" in html_lower or "frequently asked" in html_lower or "schema.org/faqpage" in html_lower)
        metrics["has_faq_section"] = has_faq
        if not has_faq:
            issues.append(FrictionIssue(
                severity="MEDIUM",
                category="FAQ",
                description="No FAQ section addressing buyer objections (activation, payment, stability).",
                remediation="Add an accordion FAQ answering: How do I pay? How fast is delivery? What is the warranty?"
            ))

        # 5. Calculate Friction Score (100 is frictionless)
        penalty = 0.0
        for issue in issues:
            if issue.severity == "HIGH":
                penalty += 25.0
            elif issue.severity == "MEDIUM":
                penalty += 12.0
            elif issue.severity == "LOW":
                penalty += 5.0
        
        friction_score = max(0.0, round(100.0 - penalty, 1))

        return FrictionAuditReport(
            identifier=identifier,
            friction_score=friction_score,
            issues=issues,
            metrics=metrics
        )

