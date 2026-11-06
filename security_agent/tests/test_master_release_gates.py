"""
Unit tests for Section 21: Master Release Gates.
Validates the 7 release gates, strict HOLD for unresolved gates, BLOCKED for hard failures,
and zero auto-approval by AI agents or scripts.
"""

import unittest
from pathlib import Path

from security_agent.master_release_gates import (
    GateStatus,
    MasterReleaseGatesEngine,
    ReleaseEligibility,
)


class TestMasterReleaseGates(unittest.TestCase):

    def setUp(self):
        self.engine = MasterReleaseGatesEngine()

    def test_all_7_release_gates_defined(self):
        """Verify all 7 mandatory release gates are declared."""
        expected = [
            "resale_usage_rights",
            "offer_accuracy",
            "delivery_warranty",
            "content_quality",
            "technical_quality",
            "analytics_privacy",
            "human_approval",
        ]
        self.assertEqual(len(self.engine.GATE_NAMES), 7)
        for g in expected:
            self.assertIn(g, self.engine.GATE_NAMES)

    def test_hard_gate_violation_results_in_blocked(self):
        """Hard policy violations (e.g., OTP bypass, aged accounts) must immediately fail to BLOCKED."""
        prohibited_items = [
            {"catalog_id": "CAT-167", "name": "SMS OTP Verification Service", "description": "Bypass 2FA"},
            {"catalog_id": "CAT-168", "name": "Aged Webmail Accounts Stock", "description": "Gmail accounts"},
            {"catalog_id": "CAT-170", "name": "PayPal Verified Reseller Accounts", "description": "Payment resale"},
        ]
        for item in prohibited_items:
            res = self.engine.evaluate_product(item)
            self.assertEqual(res.eligibility, ReleaseEligibility.BLOCKED)
            self.assertGreater(len(res.blocking_reasons), 0)

    def test_unresolved_gate_results_in_hold(self):
        """If any single gate is unresolved, product status must remain strictly HOLD."""
        # Missing human approval
        item = {
            "catalog_id": "CAT-001",
            "name": "ChatGPT Plus",
            "resale_authorization_status": "VERIFIED",
            "offer_status": "VERIFIED",
            "retail_pkr": "2300",
            "delivery": "Digital delivery after payment confirmation on WhatsApp",
            "warranty": "7 Days",
            "content_review_status": "APPROVED",
            "canonical_status": "CLEAN",
            "ga4_implementation_status": "VERIFIED",
            "approved_by": "",  # Missing human approval!
        }
        res = self.engine.evaluate_product(item)
        self.assertEqual(res.eligibility, ReleaseEligibility.HOLD)
        self.assertEqual(res.gates["human_approval"], GateStatus.UNRESOLVED)
        self.assertIn("Human approval by named owner is required. AI cannot auto-approve.", res.unresolved_reasons)

    def test_never_auto_approve_by_ai_agent(self):
        """Never auto-approve a product just because an AI agent generated a page."""
        item = {
            "catalog_id": "CAT-002",
            "name": "Cursor Pro",
            "resale_authorization_status": "VERIFIED",
            "offer_status": "VERIFIED",
            "retail_pkr": "2800",
            "delivery": "Digital delivery after payment confirmation on WhatsApp",
            "warranty": "7 Days",
            "content_review_status": "APPROVED",
            "canonical_status": "CLEAN",
            "ga4_implementation_status": "VERIFIED",
            "approved_by": "ai_agent",  # AI agent attempting auto-approval!
        }
        res = self.engine.evaluate_product(item)
        self.assertEqual(res.eligibility, ReleaseEligibility.HOLD)
        self.assertEqual(res.gates["human_approval"], GateStatus.UNRESOLVED)

    def test_fully_verified_product_with_human_approval_is_release_eligible(self):
        """When all 7 gates pass including named human owner approval, item is RELEASE_ELIGIBLE."""
        item = {
            "catalog_id": "CAT-001",
            "name": "ChatGPT Plus",
            "resale_authorization_status": "VERIFIED",
            "offer_status": "VERIFIED",
            "retail_pkr": "2300",
            "delivery": "Digital delivery after payment confirmation on WhatsApp",
            "warranty": "7 Days",
            "content_review_status": "APPROVED",
            "canonical_status": "CLEAN",
            "ga4_implementation_status": "VERIFIED",
            "approved_by": "M_Rehman_Owner",  # Explicit verified human approval
        }
        res = self.engine.evaluate_product(item)
        self.assertEqual(res.eligibility, ReleaseEligibility.RELEASE_ELIGIBLE)
        self.assertTrue(all(v == GateStatus.PASS for v in res.gates.values()))
        self.assertEqual(len(res.blocking_reasons), 0)
        self.assertEqual(len(res.unresolved_reasons), 0)

    def test_invalid_physical_shipping_fails_delivery_gate(self):
        """Digital subscriptions claiming physical shipping must fail the delivery gate."""
        item = {
            "catalog_id": "CAT-003",
            "name": "Canva Pro",
            "resale_authorization_status": "VERIFIED",
            "offer_status": "VERIFIED",
            "retail_pkr": "900",
            "delivery": "Zero-day physical shipping parcel",  # Inaccurate physical claim
            "warranty": "30 Days",
            "content_review_status": "APPROVED",
            "canonical_status": "CLEAN",
            "ga4_implementation_status": "VERIFIED",
            "approved_by": "M_Rehman_Owner",
        }
        res = self.engine.evaluate_product(item)
        self.assertEqual(res.eligibility, ReleaseEligibility.BLOCKED)
        self.assertEqual(res.gates["delivery_warranty"], GateStatus.FAIL)


if __name__ == "__main__":
    unittest.main()

