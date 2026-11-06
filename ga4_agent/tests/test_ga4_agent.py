"""
Unit tests for ga4_agent (Section 3.6 - Agent 5 GA4 Conversion Intelligence).

Tests:
1. attribution.js event classification repairs (homepage excludes view_item/view_guide).
2. WhatsApp action separation (order vs support vs channel).
3. Purchase verification gate (never fires on click, requires domestic payment verification).
4. Offline conversion deduplication and phone masking (PII protection).
5. Measurement protocol payload structure and PKR currency enforcement.
6. HERMES-CEO TaskContract execution for AGENT-05-GA4.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from hermes_core.contracts import (
    ApprovalRequirement,
    RiskClassification,
    TaskContract,
    TaskStatus,
)
from ga4_agent.analyzer import GA4Analyzer
from ga4_agent.client import GA4DataClient
from ga4_agent.conversion_importer import (
    ConversionImporter,
    MEASUREMENT_ID,
)
from ga4_agent.hermes_integration import execute_ga4_task
from ga4_agent.models import GA4EcommerceFunnel, OfflineRefund, OfflineVerifiedOrder


class TestGA4Agent(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.orders_dir = self.test_dir / "data" / "orders"
        self.orders_dir.mkdir(parents=True, exist_ok=True)
        self.project_dir = Path(__file__).resolve().parent.parent.parent

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # ── 1. attribution.js Event Classification & Taxonomy Tests ───────────────

    def test_attribution_js_excludes_homepage_from_product_and_guide_events(self):
        """Verifies attribution.js does not classify homepage as product/guide due to section classes."""
        attr_file = self.project_dir / "attribution.js"
        content = attr_file.read_text(encoding="utf-8")

        # Must have explicit getPageMetadata function
        self.assertIn("getPageMetadata()", content)
        # Must check for homepage path explicitly
        self.assertIn("path === '/' || path === '/index.html'", content)
        # Must NOT have broad global section class matching for view_comparison or view_guide
        self.assertNotIn("if (document.querySelector('[class*=\"comparison\"]", content)
        self.assertNotIn("if (document.querySelector('[class*=\"guide\"]", content)
        self.assertNotIn("if (document.querySelector('[class*=\"product\"]", content)

    def test_attribution_js_separates_whatsapp_actions(self):
        """Verifies attribution.js separates WhatsApp orders from support and channel clicks."""
        attr_file = self.project_dir / "attribution.js"
        content = attr_file.read_text(encoding="utf-8")

        self.assertIn("whatsapp_order_click", content)
        self.assertIn("whatsapp_support_click", content)
        self.assertIn("whatsapp_channel_click", content)
        self.assertIn("begin_checkout", content)
        # Purchase must NEVER be fired client-side
        self.assertNotIn("trackEvent('purchase'", content)

    # ── 2. Offline Conversion & Deduplication Tests ───────────────────────────

    def test_phone_number_pii_masking(self):
        """Verifies customer phone number is masked with one-way SHA-256 hash."""
        order = OfflineVerifiedOrder.create(
            transaction_id="ATG-TEST-001",
            tool_slug="chatgpt",
            tool_name="ChatGPT Plus",
            pkr_amount=3500.0,
            payment_rail="EasyPaisa",
            raw_phone="+923001234567",
        )
        self.assertNotIn("+923001234567", order.customer_phone_hash)
        self.assertEqual(len(order.customer_phone_hash), 16)

    def test_transaction_id_deduplication(self):
        """Strictly ensures duplicate transaction IDs are rejected."""
        importer = ConversionImporter(data_dir=self.orders_dir)

        # First recording: success
        ok1, msg1 = importer.record_verified_payment(
            transaction_id="ATG-20261105-001",
            tool_slug="chatgpt",
            tool_name="ChatGPT Plus",
            pkr_amount=3500.0,
            payment_rail="EasyPaisa",
            raw_phone="+923236715731",
        )
        self.assertTrue(ok1)

        # Duplicate recording: rejected
        ok2, msg2 = importer.record_verified_payment(
            transaction_id="ATG-20261105-001",
            tool_slug="chatgpt",
            tool_name="ChatGPT Plus",
            pkr_amount=3500.0,
            payment_rail="EasyPaisa",
            raw_phone="+923236715731",
        )
        self.assertFalse(ok2)
        self.assertIn("Duplicate", msg2)

    def test_invalid_payment_rail_rejected(self):
        """Rejects unverified or foreign local payment rails."""
        importer = ConversionImporter(data_dir=self.orders_dir)
        ok, msg = importer.record_verified_payment(
            transaction_id="ATG-INVALID-001",
            tool_slug="canva",
            tool_name="Canva Pro",
            pkr_amount=1500.0,
            payment_rail="KonbiniPayJapan",  # Invalid foreign rail
            raw_phone="+923236715731",
        )
        self.assertFalse(ok)
        self.assertIn("Invalid domestic payment rail", msg)

    # ── 3. Measurement Protocol Payload & PKR Currency Tests ──────────────────

    def test_measurement_protocol_payload_structure(self):
        """Verifies compliance of GA4 server-side purchase payload."""
        order = OfflineVerifiedOrder.create(
            transaction_id="ATG-MP-001",
            tool_slug="cursor",
            tool_name="Cursor AI Pro",
            pkr_amount=5500.0,
            payment_rail="SadaPay",
            raw_phone="+923129876543",
        )
        importer = ConversionImporter(data_dir=self.orders_dir)
        payload = importer.build_measurement_protocol_payload(order)

        self.assertIn("client_id", payload)
        self.assertEqual(len(payload["events"]), 1)
        event = payload["events"][0]
        self.assertEqual(event["name"], "purchase")
        self.assertEqual(event["params"]["currency"], "PKR")
        self.assertEqual(event["params"]["value"], 5500.0)
        self.assertEqual(event["params"]["transaction_id"], "ATG-MP-001")
        self.assertEqual(event["params"]["payment_type"], "SadaPay")
        self.assertEqual(event["params"]["items"][0]["item_id"], "cursor")

    def test_refund_recording_and_deduplication(self):
        """Verifies recording and deduplication of verified refund records."""
        importer = ConversionImporter(data_dir=self.orders_dir)
        ok1, msg1 = importer.record_verified_refund(
            transaction_id="ATG-MP-001",
            refund_id="REF-20261106-001",
            tool_slug="cursor",
            tool_name="Cursor AI Pro",
            pkr_amount=5500.0,
            reason="service_incompatibility",
        )
        self.assertTrue(ok1)
        self.assertIn("successfully recorded", msg1)

        # Duplicate refund ID rejected
        ok2, msg2 = importer.record_verified_refund(
            transaction_id="ATG-MP-001",
            refund_id="REF-20261106-001",
            tool_slug="cursor",
            tool_name="Cursor AI Pro",
            pkr_amount=5500.0,
            reason="duplicate",
        )
        self.assertFalse(ok2)
        self.assertIn("Duplicate", msg2)

    def test_refund_measurement_protocol_payload(self):
        """Verifies GA4 Measurement Protocol refund event structure and PKR currency."""
        refund = OfflineRefund.create(
            transaction_id="ATG-REF-001",
            refund_id="REF-20261106-002",
            tool_slug="canva",
            tool_name="Canva Pro",
            pkr_amount=1500.0,
            reason="customer_request",
        )
        importer = ConversionImporter(data_dir=self.orders_dir)
        payload = importer.build_refund_payload(refund)

        self.assertIn("client_id", payload)
        self.assertEqual(len(payload["events"]), 1)
        event = payload["events"][0]
        self.assertEqual(event["name"], "refund")
        self.assertEqual(event["params"]["currency"], "PKR")
        self.assertEqual(event["params"]["value"], 1500.0)
        self.assertEqual(event["params"]["transaction_id"], "ATG-REF-001")
        self.assertEqual(event["params"]["items"][0]["item_id"], "canva")

    # ── 4. Funnel Metrics Calculation Tests ───────────────────────────────────

    def test_funnel_dropoff_and_conversion_rate(self):
        """Verifies calculation of checkout drop-off and conversion rates."""
        funnel = GA4EcommerceFunnel(
            period="Test Period",
            product_views=1000,
            product_selections=500,
            order_initiations=100,
            verified_purchases=25,
            currency="PKR",
            total_revenue_pkr=87500.0,
        )
        # Dropoff: (100 - 25) / 100 = 75.0%
        self.assertEqual(funnel.checkout_dropoff_pct, 75.0)
        # Overall conversion: 25 / 1000 = 2.5%
        self.assertEqual(funnel.overall_conversion_rate_pct, 2.5)

    # ── 5. HERMES-CEO Task Contract Execution Tests ──────────────────────────

    def test_hermes_ga4_task_execution(self):
        """Verifies AGENT-05-GA4 completes a TaskContract dispatched by HERMES-CEO."""
        contract = TaskContract(
            task_id="TASK-05-TEST01",
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-05-GA4",
            objective="Execute GA4 conversion audit, funnel drop-off inspection, and offline purchase workflow",
            scope="reports/ga4-agent/",
            input_evidence={"mode": "audit"},
            required_tools=["ga4_agent"],
            expected_output="ga4-audit-latest.json",
            dependencies=[],
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["Valid JSON artifact generated", "Zero unhandled exceptions"],
        )

        completed = execute_ga4_task(contract, project_dir=self.project_dir)
        self.assertEqual(completed.status, TaskStatus.VERIFIED)
        self.assertIn("execution_timestamp", completed.verification_evidence)
        self.assertIn("product_views", completed.verification_evidence)
        self.assertIn("verified_revenue_pkr", completed.verification_evidence)
        self.assertTrue(Path(completed.verification_evidence["markdown_report"]).exists())


if __name__ == "__main__":
    unittest.main()

