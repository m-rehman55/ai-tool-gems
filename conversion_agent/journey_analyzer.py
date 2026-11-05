"""
conversion_agent.journey_analyzer - Evaluates complete customer journeys from discovery to conversion.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional

from conversion_agent.trust_auditor import TrustAuditor, TrustAuditResult
from conversion_agent.friction_detector import FrictionDetector, FrictionAuditReport


@dataclass
class CustomerJourneyReport:
    identifier: str
    overall_readiness_score: float  # (trust_score * 0.5 + friction_score * 0.5)
    trust_audit: TrustAuditResult
    friction_audit: FrictionAuditReport
    journey_stages: Dict[str, str] = field(default_factory=dict)
    critical_recommendations: List[str] = field(default_factory=list)


class CustomerJourneyAnalyzer:
    """
    Evaluates end-to-end customer journey from search discovery to order completion.
    Stages:
    1. Search Landing: Clarity of H1, value proposition, local intent.
    2. Trust Evaluation: Upfront PKR price, domestic payment rails, replacement warranty.
    3. Consideration & Comparison: Tool features, plan types, objection-handling FAQs.
    4. WhatsApp Order Initiation: Direct, frictionless prefilled WhatsApp link.
    5. Post-Order Reassurance: Stated operating hours (PKT) and delivery timeframe.
    """

    def __init__(self, repo_root: Optional[Path] = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent
        self.trust_auditor = TrustAuditor()
        self.friction_detector = FrictionDetector()

    def analyze_html(self, html_content: str, identifier: str = "inline") -> CustomerJourneyReport:
        trust_res = self.trust_auditor.audit_html(html_content, identifier=identifier)
        friction_res = self.friction_detector.analyze_page(html_content, identifier=identifier)

        overall_score = round((trust_res.trust_score * 0.55) + (friction_res.friction_score * 0.45), 1)

        journey_stages = {
            "search_landing": "OPTIMAL" if trust_res.signals_detected.get("pkr_pricing") else "NEEDS_IMPROVEMENT",
            "trust_evaluation": "STRONG" if trust_res.trust_score >= 80.0 else "MODERATE" if trust_res.trust_score >= 60.0 else "WEAK",
            "objection_handling": "PASS" if friction_res.metrics.get("has_faq_section") else "MISSING_FAQS",
            "checkout_initiation": "OPTIMAL" if trust_res.signals_detected.get("whatsapp_desk") and not any(i.category == "CTA" for i in friction_res.issues) else "FRICTION_DETECTED"
        }

        critical_recs = []
        for rec in trust_res.recommendations:
            critical_recs.append(f"[Trust] {rec}")
        for issue in friction_res.issues:
            critical_recs.append(f"[{issue.category} Friction] {issue.remediation}")

        return CustomerJourneyReport(
            identifier=identifier,
            overall_readiness_score=overall_score,
            trust_audit=trust_res,
            friction_audit=friction_res,
            journey_stages=journey_stages,
            critical_recommendations=critical_recs
        )

    def analyze_file(self, file_path: Path) -> CustomerJourneyReport:
        if not file_path.exists():
            raise FileNotFoundError(f"Page file not found: {file_path}")
        html_content = file_path.read_text(encoding="utf-8", errors="replace")
        return self.analyze_html(html_content, identifier=str(file_path))

    def audit_catalog(self) -> Dict[str, Any]:
        """
        Audits homepage, key landing pages, and all tool pages in the repository.
        """
        target_files = [
            self.repo_root / "index.html",
            self.repo_root / "terms-of-service" / "index.html",
            self.repo_root / "privacy-policy" / "index.html"
        ]

        tools_dir = self.repo_root / "tools"
        if tools_dir.exists():
            for tool_folder in sorted(tools_dir.iterdir()):
                tool_index = tool_folder / "index.html"
                if tool_index.exists():
                    target_files.append(tool_index)

        reports = []
        total_score = 0.0

        for f in target_files:
            if f.exists():
                rep = self.analyze_file(f)
                reports.append(rep)
                total_score += rep.overall_readiness_score

        avg_score = round(total_score / len(reports), 1) if reports else 0.0

        return {
            "total_pages_audited": len(reports),
            "average_journey_score": avg_score,
            "high_friction_pages": [r.identifier for r in reports if r.overall_readiness_score < 75.0],
            "reports_summary": [
                {
                    "identifier": Path(r.identifier).name if "/" in r.identifier or "\\" in r.identifier else r.identifier,
                    "overall_score": r.overall_readiness_score,
                    "trust_score": r.trust_audit.trust_score,
                    "friction_score": r.friction_audit.friction_score,
                    "issues_count": len(r.friction_audit.issues)
                }
                for r in reports
            ]
        }
