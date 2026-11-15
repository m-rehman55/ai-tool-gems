"""Unit tests for Verified Facts Source of Truth and Copy Grounding."""

from __future__ import annotations

import unittest

from backlink_agent.facts import get_verified_facts


class TestVerifiedFacts(unittest.TestCase):

    def setUp(self):
        self.facts = get_verified_facts()

    def test_facts_attributes_loaded(self):
        self.assertEqual(self.facts.brand_name, "AI Tool Gems")
        self.assertEqual(self.facts.website_url, "https://aitoolgems.tech")
        self.assertEqual(self.facts.primary_market, "Pakistan")
        self.assertEqual(self.facts.catalog_tools_count, 40)
        self.assertIn("EasyPaisa", self.facts.verified_payment_rails_pk)
        self.assertIn("JazzCash", self.facts.verified_payment_rails_pk)
        self.assertIn("SadaPay", self.facts.verified_payment_rails_pk)

    def test_disallowed_gateway_flagged_in_copy(self):
        bad_copy = "We offer instant Stripe checkout and PayPal for all AI tools."
        violations = self.facts.validate_copy(bad_copy)
        self.assertTrue(any("Stripe/PayPal" in v for v in violations))

    def test_reciprocal_badge_flagged_in_copy(self):
        bad_copy = "We agree to place your reciprocal footer badge on our homepage."
        violations = self.facts.validate_copy(bad_copy)
        self.assertTrue(any("Reciprocal" in v for v in violations))

    def test_unauthorized_endorsement_flagged(self):
        bad_copy = "AI Tool Gems is an official partner of OpenAI and authorized distributor."
        violations = self.facts.validate_copy(bad_copy)
        self.assertTrue(any("endorsement" in v for v in violations))

    def test_compliant_copy_passes(self):
        good_copy = (
            "AI Tool Gems tracks 40 commercial AI tool subscriptions in Pakistani Rupees (PKR) "
            "with EasyPaisa, JazzCash, and SadaPay verified payment guidance and downloadable "
            "pricing datasets at https://aitoolgems.tech/prices/."
        )
        violations = self.facts.validate_copy(good_copy)
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
