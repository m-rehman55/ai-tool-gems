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

    # ── 6. State Mutation & Data-Loss Protection Tests ───────────────────────

    def test_dry_run_strictly_never_mutates_order_or_refund_state(self):
        """CRITICAL: Dry-run must generate payload preview without setting is_imported_to_ga4."""
        importer = ConversionImporter(data_dir=self.orders_dir)
        importer.record_verified_payment(
            transaction_id="SYNTH-DRYRUN-001",
            tool_slug="chatgpt",
            tool_name="ChatGPT Plus",
            pkr_amount=2300.0,
            payment_rail="EasyPaisa",
            raw_phone="+923001112233",
        )
        importer.record_verified_refund(
            transaction_id="SYNTH-DRYRUN-001",
            refund_id="REF-DRYRUN-001",
            tool_slug="chatgpt",
            tool_name="ChatGPT Plus",
            pkr_amount=2300.0,
            reason="test_dry_run",
        )

        # Execute dry runs
        res_order = importer.import_verified_orders(dry_run=True)
        self.assertEqual(res_order["status"], "dry_run")
        self.assertEqual(res_order["imported_count"], 0)

        res_refund = importer.dispatch_offline_refunds(dry_run=True)
        self.assertEqual(res_refund["status"], "dry_run")
        self.assertEqual(res_refund["imported_count"], 0)

        # Reload from disk and assert records remain NOT imported
        orders = importer.load_orders()
        self.assertEqual(len(orders), 1)
        self.assertFalse(orders[0].is_imported_to_ga4, "Dry run must NOT mark order as imported")
        self.assertIsNone(orders[0].imported_at, "Dry run must NOT set imported_at")

        refunds = importer.load_refunds()
        self.assertEqual(len(refunds), 1)
        self.assertFalse(refunds[0].is_imported_to_ga4, "Dry run must NOT mark refund as imported")
        self.assertIsNone(refunds[0].imported_at, "Dry run must NOT set imported_at")

    def test_missing_secret_returns_blocked_and_preserves_orders_and_refunds(self):
        """CRITICAL: Missing API secret must return BLOCKED_MISSING_API_SECRET and leave orders pending."""
        import os
        old_sec1 = os.environ.pop("GA4_API_SECRET", None)
        old_sec2 = os.environ.pop("GA4_MEASUREMENT_SECRET", None)
        try:
            importer = ConversionImporter(data_dir=self.orders_dir)
            importer.record_verified_payment(
                transaction_id="SYNTH-NOSECRET-001",
                tool_slug="claude",
                tool_name="Claude Pro",
                pkr_amount=2600.0,
                payment_rail="JazzCash",
                raw_phone="+923009998877",
            )
            importer.record_verified_refund(
                transaction_id="SYNTH-NOSECRET-001",
                refund_id="REF-NOSECRET-001",
                tool_slug="claude",
                tool_name="Claude Pro",
                pkr_amount=2600.0,
                reason="test_no_secret",
            )

            res_order = importer.import_verified_orders(dry_run=False)
            self.assertEqual(res_order["status"], "BLOCKED_MISSING_API_SECRET")
            self.assertEqual(res_order["imported_count"], 0)

            res_refund = importer.dispatch_offline_refunds(dry_run=False)
            self.assertEqual(res_refund["status"], "BLOCKED_MISSING_API_SECRET")
            self.assertEqual(res_refund["imported_count"], 0)

            # Assert order and refund remain pending
            orders = importer.load_orders()
            self.assertFalse(orders[0].is_imported_to_ga4)

            refunds = importer.load_refunds()
            self.assertFalse(refunds[0].is_imported_to_ga4)
        finally:
            if old_sec1:
                os.environ["GA4_API_SECRET"] = old_sec1
            if old_sec2:
                os.environ["GA4_MEASUREMENT_SECRET"] = old_sec2

    def test_failed_network_request_leaves_order_pending(self):
        """CRITICAL: Network failure must leave order pending for retry."""
        import os
        from unittest.mock import patch
        import urllib.error
        importer = ConversionImporter(data_dir=self.orders_dir)
        importer.record_verified_payment(
            transaction_id="SYNTH-NETFAIL-001",
            tool_slug="gemini",
            tool_name="Gemini Advanced",
            pkr_amount=800.0,
            payment_rail="EasyPaisa",
            raw_phone="+923005554433",
        )

        with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("Connection refused")), \
             patch.dict(os.environ, {"GA4_API_SECRET": "mock_secret_test"}):
            res = importer.import_verified_orders(dry_run=False)
            self.assertEqual(res["imported_count"], 0)

        orders = importer.load_orders()
        self.assertFalse(orders[0].is_imported_to_ga4, "Order must remain pending after network failure")

    def test_successful_http_response_marks_order_imported(self):
        """CRITICAL: HTTP 204 from GA4 MP marks order imported and sets timestamp."""
        import os
        from unittest.mock import MagicMock, patch
        importer = ConversionImporter(data_dir=self.orders_dir)
        importer.record_verified_payment(
            transaction_id="SYNTH-SUCCESS-001",
            tool_slug="midjourney",
            tool_name="Midjourney Standard",
            pkr_amount=3500.0,
            payment_rail="SadaPay",
            raw_phone="+923004443322",
        )

        mock_resp = MagicMock()
        mock_resp.status = 204
        mock_resp.__enter__.return_value = mock_resp

        with patch("urllib.request.urlopen", return_value=mock_resp), \
             patch.dict(os.environ, {"GA4_API_SECRET": "mock_secret_test"}):
            res = importer.import_verified_orders(dry_run=False)
            self.assertEqual(res["imported_count"], 1)

        orders = importer.load_orders()
        self.assertTrue(orders[0].is_imported_to_ga4, "Order must be marked imported on HTTP 204")
        self.assertIsNotNone(orders[0].imported_at)


if __name__ == "__main__":
    unittest.main()

