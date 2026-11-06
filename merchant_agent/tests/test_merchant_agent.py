"""Unit tests for Google Merchant Center & Product Feed Agent (AGENT-13)."""

import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from hermes_core.contracts import ApprovalRequirement, RiskClassification, TaskContract, TaskStatus
from merchant_agent.client import GoogleMerchantClient
from merchant_agent.feed_generator import MerchantFeedGenerator, MerchantProductItem
from merchant_agent.hermes_integration import MerchantHermesAgent
from merchant_agent.validator import MerchantValidator


class TestMerchantAgent(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)
        self.gen = MerchantFeedGenerator(project_dir=self.tmp_path)
        self.val = MerchantValidator(project_dir=self.tmp_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_extract_catalog_and_generate_xml_feed(self):
        sample_items = [
            MerchantProductItem(
                sku_id="atg-chatgpt",
                title="ChatGPT Plus (Pakistan)",
                description="Verified ChatGPT subscription in Pakistan.",
                link="https://aitoolgems.tech/tools/chatgpt/",
                image_link="https://aitoolgems.tech/assets/chatgpt.png",
                availability="in_stock",
                price_pkr=3500,
                brand="OpenAI",
            ),
        ]
        xml_path = self.gen.generate_xml_feed(sample_items)
        self.assertTrue(xml_path.exists())

        # Parse XML and verify namespaces & tags
        tree = ET.parse(xml_path)
        root = tree.getroot()
        self.assertEqual(root.tag, "rss")
        channel = root.find("channel")
        self.assertIsNotNone(channel)

        item = channel.find("item")
        self.assertIsNotNone(item)
        ns = {"g": "http://base.google.com/ns/1.0"}
        self.assertEqual(item.find("g:id", ns).text, "atg-chatgpt")
        self.assertEqual(item.find("g:price", ns).text, "3500.00 PKR")
        self.assertEqual(item.find("g:availability", ns).text, "in_stock")

    def test_generate_tsv_feed(self):
        sample_items = [
            MerchantProductItem(
                sku_id="atg-claude",
                title="Claude Pro (Pakistan)",
                description="Verified Claude subscription in Pakistan.",
                link="https://aitoolgems.tech/tools/claude/",
                image_link="https://aitoolgems.tech/assets/claude.png",
                availability="in_stock",
                price_pkr=3800,
                brand="Anthropic",
            ),
        ]
        tsv_path = self.gen.generate_tsv_feed(sample_items)
        self.assertTrue(tsv_path.exists())
        lines = tsv_path.read_text(encoding="utf-8").splitlines()
        self.assertIn("id\ttitle\tdescription", lines[0])
        self.assertIn("atg-claude\tClaude Pro (Pakistan)", lines[1])

    def test_validator_detects_return_by_mail_defect_19(self):
        # Create mock tool page with ReturnByMail defect
        tool_dir = self.tmp_path / "tools" / "defect-tool"
        tool_dir.mkdir(parents=True)
        html_content = """
        <html>
          <body>
            <h1>Defect Tool</h1>
            <p>Price: Rs. 2000</p>
            <script type="application/ld+json">
              {"@type": "Offer", "hasMerchantReturnPolicy": {"returnMethod": "https://schema.org/ReturnByMail"}}
            </script>
          </body>
        </html>
        """
        (tool_dir / "index.html").write_text(html_content, encoding="utf-8")

        item = MerchantProductItem(
            sku_id="atg-defect-tool",
            title="Defect Tool",
            description="Testing defect 19",
            link="https://aitoolgems.tech/tools/defect-tool/",
            image_link="https://aitoolgems.tech/assets/img.png",
            availability="in_stock",
            price_pkr=2000,
            brand="Test",
        )
        report = self.val.validate_feed_items([item])
        self.assertFalse(report.is_feed_compliant)
        issue_types = [i.issue_type for i in report.issues]
        self.assertIn("RETURN_POLICY_ERROR", issue_types)

    def test_google_merchant_client_unconfigured(self):
        client = GoogleMerchantClient(merchant_id="")
        status = client.get_account_status()
        self.assertEqual(status["status"], "BLOCKED_PENDING_CREDENTIALS")
        self.assertIn("merchants.google.com", status["instructions"])

    def test_hermes_integration_tasks(self):
        agent = MerchantHermesAgent(project_dir=self.tmp_path)
        task = TaskContract(
            task_id="TEST-MERCHANT-01",
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-13-MERCHANT",
            objective="Generate Google Merchant Center feeds and audit schema parity",
            scope="Product Feed",
            input_evidence={},
            required_tools=["merchant_feed_generator"],
            expected_output={"feed": "dict"},
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["Valid product feed generation"],
        )
        completed = agent.execute_task(task)
        self.assertEqual(completed.status, TaskStatus.VERIFIED)
        self.assertIn("xml_exists", completed.verification_evidence)
        self.assertTrue(completed.verification_evidence["xml_exists"])

    def test_offer_level_assessment_separates_merchant_and_ads(self):
        """Verifies offer-level assessment evaluates parameters and separates Merchant vs Ads."""
        assessment = self.gen.evaluate_offer({
            "slug": "chatgpt",
            "name": "ChatGPT Plus",
            "duration": "1 Month",
            "access": "Private",
            "price": 2300,
        })
        self.assertEqual(assessment.slug, "chatgpt")
        self.assertEqual(assessment.duration, "1 Month")
        self.assertEqual(assessment.total_cost_pkr, 2300)
        self.assertIn("Prepaid flat upfront", assessment.payment_model)
        self.assertIn("Manual renewal", assessment.renewal_conditions)
        self.assertEqual(assessment.merchant_center_status, "HOLD_TERM_INSUFFICIENT")
        self.assertEqual(assessment.google_ads_search_status, "PRELIMINARY_POLICY_REVIEW")
        self.assertIn("minimum prepaid term of 12 months", assessment.merchant_center_reason)

    def test_missing_offer_terms_marked_unverified_never_fabricated(self):
        """Verifies missing duration or access model is flagged UNVERIFIED rather than fabricated."""
        assessment = self.gen.evaluate_offer({
            "slug": "custom-ai",
            "name": "Custom AI Tool",
            "price": 1500,
        })
        self.assertEqual(assessment.duration, "UNVERIFIED")
        self.assertEqual(assessment.access_model, "UNVERIFIED")
        self.assertEqual(assessment.merchant_center_status, "HOLD_UNVERIFIED_TERMS")
        self.assertEqual(assessment.google_ads_search_status, "HOLD_UNVERIFIED_TERMS")

    def test_shared_accounts_and_turnitin_marked_hold(self):
        """Verifies shared accounts and academic cheating tools are blocked under Google policies."""
        shared_assessment = self.gen.evaluate_offer({
            "slug": "netflix",
            "name": "Netflix Premium 4K",
            "duration": "1 Month",
            "access": "Shared",
            "price": 400,
        })
        self.assertEqual(shared_assessment.merchant_center_status, "HOLD_POLICY_VIOLATION")
        self.assertEqual(shared_assessment.google_ads_search_status, "HOLD_HIGH_RISK")

        turnitin_assessment = self.gen.evaluate_offer({
            "slug": "turnitin",
            "name": "Turnitin Student Account",
            "duration": "1 Month",
            "access": "Private",
            "price": 3600,
        })
        self.assertEqual(turnitin_assessment.merchant_center_status, "HOLD_POLICY_VIOLATION")
        self.assertEqual(turnitin_assessment.google_ads_search_status, "HOLD_PROHIBITED")

    def test_export_eligibility_registers(self):
        """Verifies export of durable JSON hold registers and ads matrix."""
        hold_p, ads_p = self.gen.export_eligibility_registers()
        self.assertTrue(hold_p.exists())
        self.assertTrue(ads_p.exists())

        hold_data = json.loads(hold_p.read_text(encoding="utf-8"))
        ads_data = json.loads(ads_p.read_text(encoding="utf-8"))

        self.assertGreater(len(hold_data), 0)
        self.assertGreater(len(ads_data), 0)
        # Verify hold register contains policy reasons
        self.assertTrue(all("merchant_center_reason" in item for item in hold_data))

    def test_validator_blocks_ineligible_items_in_feed(self):
        """Verifies validator detects prohibited items submitted in Merchant feed."""
        ineligible_item = MerchantProductItem(
            sku_id="atg-turnitin",
            title="Turnitin Student Account",
            description="Testing academic tool",
            link="https://aitoolgems.tech/tools/turnitin/",
            image_link="https://aitoolgems.tech/assets/turnitin.png",
            availability="in_stock",
            price_pkr=3600,
            brand="Turnitin",
        )
        report = self.val.validate_feed_items([ineligible_item])
        self.assertFalse(report.is_feed_compliant)
        issue_types = [i.issue_type for i in report.issues]
        self.assertIn("INELIGIBLE_FEED_ITEM", issue_types)


if __name__ == "__main__":
    unittest.main()

