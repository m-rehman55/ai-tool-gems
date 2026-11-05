"""
Unit tests for HERMES Agent 14: Conversion Journey & Trust Architecture.
"""

import unittest
from pathlib import Path

from conversion_agent.trust_auditor import TrustAuditor
from conversion_agent.friction_detector import FrictionDetector
from conversion_agent.journey_analyzer import CustomerJourneyAnalyzer
from conversion_agent.hermes_integration import HermesConversionAgent
from hermes_core.contracts import TaskContract, TaskStatus, RiskClassification, ApprovalRequirement


class TestConversionAgent(unittest.TestCase):

    def setUp(self):
        self.trust_auditor = TrustAuditor()
        self.friction_detector = FrictionDetector()
        self.analyzer = CustomerJourneyAnalyzer()
        self.agent = HermesConversionAgent()

    def test_trust_auditor_complete_signals(self):
        html = """
        <!DOCTYPE html>
        <html>
        <body>
            <h1>ChatGPT Plus in Pakistan</h1>
            <p>Price: Rs 1,800 / Month (PKR).</p>
            <p>Pay safely via EasyPaisa, JazzCash, SadaPay or Bank Transfer (IBFT).</p>
            <p>Contact our official WhatsApp desk: <a href="https://wa.me/923288823293?text=Hi">Order Now</a></p>
            <p>We provide a 30-day replacement warranty for uninterrupted access.</p>
            <p>Fulfillment window: Instant delivery within 15 to 60 minutes.</p>
            <p>Active operating hours: 10:00 AM – 11:00 PM PKT.</p>
            <p><a href="/terms-of-service/">Terms of Service & Refund Policy</a></p>
            <p><small>AI Tool Gems is an independent facilitator. All third-party trademarks belong to respective owners.</small></p>
        </body>
        </html>
        """
        result = self.trust_auditor.audit_html(html, "test_page")
        self.assertEqual(result.trust_score, 100.0)
        self.assertEqual(len(result.failed_checks), 0)
        self.assertTrue(result.signals_detected["pkr_pricing"])
        self.assertTrue(result.signals_detected["whatsapp_desk"])
        self.assertTrue(result.signals_detected["warranty_policy"])

    def test_trust_auditor_missing_signals(self):
        html = "<html><body><h1>Generic Page</h1><p>Buy tool now.</p></body></html>"
        result = self.trust_auditor.audit_html(html, "sparse_page")
        self.assertLess(result.trust_score, 30.0)
        self.assertIn("Missing PKR pricing", result.failed_checks)
        self.assertIn("Missing direct WhatsApp desk CTA", result.failed_checks)

    def test_friction_detector_identifies_unprefilled_whatsapp(self):
        html = """
        <html><body>
            <a href="https://wa.me/923288823293">Order on WhatsApp</a>
        </body></html>
        """
        report = self.friction_detector.analyze_page(html, "unprefilled")
        self.assertTrue(any(i.category == "CTA" and "pre-filled" in i.description for i in report.issues))

    def test_friction_detector_clean_prefilled_whatsapp(self):
        html = """
        <html><body>
            <a href="https://wa.me/923288823293?text=Hi%20AI%20Tool%20Gems">Order on WhatsApp</a>
            <p>Tier: Shared private profile account.</p>
            <div id="faq"><h3>Frequently Asked Questions</h3><p>Q: How do I pay?</p></div>
        </body></html>
        """
        report = self.friction_detector.analyze_page(html, "clean")
        self.assertFalse(any(i.category == "CTA" for i in report.issues))
        self.assertGreaterEqual(report.friction_score, 90.0)

    def test_customer_journey_catalog_audit(self):
        audit_res = self.analyzer.audit_catalog()
        self.assertGreater(audit_res["total_pages_audited"], 0)
        self.assertIn("average_journey_score", audit_res)
        self.assertGreaterEqual(audit_res["average_journey_score"], 60.0)

    def test_hermes_integration_tasks(self):
        task = TaskContract(
            task_id="TASK-14-TEST",
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-14-CONVERSION",
            objective="Run conversion journey and trust audit across catalog",
            scope="site-wide",
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["Valid catalog conversion analysis report"]
        )
        completed = self.agent.execute_task(task)
        self.assertEqual(completed.status, TaskStatus.VERIFIED)
        self.assertIn("average_journey_score", completed.verification_evidence)


if __name__ == "__main__":
    unittest.main()
