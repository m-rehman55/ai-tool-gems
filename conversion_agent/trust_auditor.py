"""
conversion_agent.trust_auditor - Audits commercial trust architecture and transparency signals.
"""

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Dict, List, Any


@dataclass
class TrustAuditResult:
    url_or_path: str
    trust_score: float  # 0.0 to 100.0
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    signals_detected: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)


class TrustAuditor:
    """
    Audits trust signals required for Pakistani commercial AI subscription transactions:
    1. Verified PKR pricing visible upfront
    2. Domestic Pakistani payment rails (EasyPaisa, JazzCash, SadaPay, Raast, Bank IBFT)
    3. Official WhatsApp support desk link (+92 328 8823293)
    4. Replacement warranty explicitly stated
    5. Realistic delivery timeframe (15-60 mins PKT)
    6. Operating hours stated in Pakistan Standard Time (PKT)
    7. Terms of Service & refund policy link
    8. Nominative fair use / independent entity disclaimer
    """

    SUPPORTED_PAYMENT_RAILS = ["easypaisa", "jazzcash", "sadapay", "nayapay", "raast", "bank transfer", "ibft"]
    OFFICIAL_WHATSAPP_PHONE = "923288823293"

    def audit_html(self, html_content: str, identifier: str = "inline") -> TrustAuditResult:
        passed = []
        failed = []
        recommendations = []
        signals = {}

        html_lower = html_content.lower()

        # 1. PKR Pricing
        has_pkr = bool(re.search(r'(?:rs\.?|pkr)\s*[\d,]+', html_lower) or "pkr" in html_lower)
        signals["pkr_pricing"] = has_pkr
        if has_pkr:
            passed.append("PKR pricing visible")
        else:
            failed.append("Missing PKR pricing")
            recommendations.append("Ensure price is explicitly stated in PKR with no ambiguity.")

        # 2. Local Payment Rails
        detected_rails = [rail for rail in self.SUPPORTED_PAYMENT_RAILS if rail in html_lower]
        signals["detected_payment_rails"] = detected_rails
        if len(detected_rails) >= 2:
            passed.append(f"Pakistani payment rails ({', '.join(detected_rails[:3])})")
        else:
            failed.append("Insufficient domestic payment rails displayed")
            recommendations.append("Highlight EasyPaisa, JazzCash, SadaPay, and Bank IBFT clearly.")

        # 3. WhatsApp Desk Visibility
        has_wa = bool(self.OFFICIAL_WHATSAPP_PHONE in html_content or "wa.me" in html_lower or "whatsapp" in html_lower)
        signals["whatsapp_desk"] = has_wa
        if has_wa:
            passed.append("Official WhatsApp support desk integrated")
        else:
            failed.append("Missing direct WhatsApp desk CTA")
            recommendations.append("Add direct WhatsApp CTA for immediate customer order assistance.")

        # 4. Replacement Warranty
        has_warranty = bool("warranty" in html_lower or "replacement" in html_lower)
        signals["warranty_policy"] = has_warranty
        if has_warranty:
            passed.append("Replacement warranty guarantee stated")
        else:
            failed.append("Missing replacement warranty reassurance")
            recommendations.append("Clearly state the replacement warranty coverage to build consumer confidence.")

        # 5. Delivery Timeframe
        has_delivery_time = bool(re.search(r'(?:15\s*(?:-|to)\s*60\s*min|instant|delivery|within\s*\d+\s*min)', html_lower))
        signals["delivery_timeframe"] = has_delivery_time
        if has_delivery_time:
            passed.append("Fulfillment timeframe communicated")
        else:
            failed.append("Missing transparent delivery timeframe")
            recommendations.append("State clear 15-60 minute delivery expectation during PKT operating hours.")

        # 6. Operating Hours
        has_hours = bool("pkt" in html_lower or "operating hours" in html_lower or "10:00" in html_lower)
        signals["operating_hours"] = has_hours
        if has_hours:
            passed.append("Operating hours or PKT schedule specified")
        else:
            failed.append("Missing Pakistan operating hours")
            recommendations.append("Specify support desk operating hours (e.g. 10:00 AM – 11:00 PM PKT).")

        # 7. Terms / Policy Link
        has_terms = bool("terms" in html_lower or "privacy" in html_lower or "policy" in html_lower)
        signals["policy_links"] = has_terms
        if has_terms:
            passed.append("Terms and refund policy links accessible")
        else:
            failed.append("Missing terms or policy link")
            recommendations.append("Provide clickable link to Terms of Service and refund/replacement policy.")

        # 8. Independent Business Disclaimer (Defect 20)
        has_disclaimer = bool("independent" in html_lower or "not affiliated" in html_lower or "trademark" in html_lower or "disclaimer" in html_lower)
        signals["independent_disclaimer"] = has_disclaimer
        if has_disclaimer:
            passed.append("Independent service & trademark disclaimer present")
        else:
            failed.append("Missing independent service / trademark disclaimer")
            recommendations.append("Add clear nominative fair-use disclaimer stating independence from software vendors.")

        # Compute score out of 100
        total_checks = 8
        score = round((len(passed) / total_checks) * 100.0, 1)

        return TrustAuditResult(
            url_or_path=identifier,
            trust_score=score,
            passed_checks=passed,
            failed_checks=failed,
            signals_detected=signals,
            recommendations=recommendations
        )

    def audit_file(self, file_path: Path) -> TrustAuditResult:
        if not file_path.exists():
            return TrustAuditResult(
                url_or_path=str(file_path),
                trust_score=0.0,
                failed_checks=["File does not exist"],
                recommendations=["Ensure path is valid."]
            )
        content = file_path.read_text(encoding="utf-8", errors="replace")
        return self.audit_html(content, identifier=str(file_path))
