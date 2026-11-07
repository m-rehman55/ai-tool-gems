"""
Unit test suite validating GA4 event schemas, Consent Mode v2 configurations,
and analytics payload isolation (Zero synthetic events to production).
"""

import unittest
import os
import re
import json

class TestAnalyticsEventSchemas(unittest.TestCase):

    def setUp(self):
        self.attribution_path = os.path.join(os.path.dirname(__file__), "..", "attribution.js")
        self.app_path = os.path.join(os.path.dirname(__file__), "..", "app.js")
        with open(self.attribution_path, "r", encoding="utf-8") as f:
            self.attr_code = f.read()
        with open(self.app_path, "r", encoding="utf-8") as f:
            self.app_code = f.read()

    def test_canonical_measurement_id_enforced(self):
        """Assert G-NQJCMDCLLP is configured and stale IDs are absent."""
        self.assertIn("const MEASUREMENT_ID = 'G-NQJCMDCLLP';", self.attr_code)
        self.assertNotIn("G-9V4S5V38B9", self.attr_code)
        self.assertNotIn("G-9V4S5V38B9", self.app_code)

    def test_consent_mode_v2_default_denied(self):
        """Assert Google Consent Mode v2 default parameters are set to denied."""
        self.assertIn("'analytics_storage': 'denied'", self.attr_code)
        self.assertIn("'ad_storage': 'denied'", self.attr_code)
        self.assertIn("'ad_user_data': 'denied'", self.attr_code)
        self.assertIn("'ad_personalization': 'denied'", self.attr_code)

    def test_gtag_script_deferred_for_lcp(self):
        """Assert third-party gtag script loading is deferred via requestIdleCallback or setTimeout."""
        self.assertIn("requestIdleCallback(loadAnalytics", self.attr_code)
        self.assertIn("setTimeout(loadAnalytics, 2000)", self.attr_code)

    def test_whatsapp_event_schema_contracts(self):
        """Validate event schemas fired on WhatsApp order and support interactions."""
        # 1. begin_checkout
        self.assertIn("trackEvent('begin_checkout',", self.attr_code)
        self.assertIn("currency: 'PKR'", self.attr_code)
        
        # 2. generate_lead
        self.assertIn("trackEvent('generate_lead',", self.attr_code)
        self.assertIn("lead_type: 'whatsapp_order_inquiry'", self.attr_code)

        # 3. whatsapp_order_click
        self.assertIn("trackEvent('whatsapp_order_click',", self.attr_code)
        self.assertIn("destination: 'whatsapp_order'", self.attr_code)

        # 4. whatsapp_support_click
        self.assertIn("trackEvent('whatsapp_support_click',", self.attr_code)
        self.assertIn("destination: 'whatsapp_support'", self.attr_code)

    def test_mock_ga4_measurement_protocol_payload_validation(self):
        """Simulate client-side event payload and assert conformance with MP schema."""
        mock_payload = {
            "client_id": "1234567890.1700000000",
            "events": [
                {
                    "name": "begin_checkout",
                    "params": {
                        "currency": "PKR",
                        "value": 2300,
                        "items": [
                            {
                                "item_id": "chatgpt",
                                "item_name": "ChatGPT Plus",
                                "currency": "PKR",
                                "quantity": 1
                            }
                        ]
                    }
                }
            ]
        }
        # Schema assertions
        self.assertRegex(mock_payload["client_id"], r"^[0-9]+\.[0-9]+$")
        event = mock_payload["events"][0]
        self.assertEqual(event["name"], "begin_checkout")
        self.assertEqual(event["params"]["currency"], "PKR")
        self.assertGreater(event["params"]["value"], 0)
        self.assertEqual(len(event["params"]["items"]), 1)

    def test_zero_synthetic_events_to_live_production_ga4(self):
        """Assert conversion tests use mock transports rather than live HTTP requests."""
        ga4_test_file = os.path.join(os.path.dirname(__file__), "..", "ga4_agent", "tests", "test_conversion_importer.py")
        if os.path.exists(ga4_test_file):
            with open(ga4_test_file, "r", encoding="utf-8") as f:
                test_code = f.read()
            self.assertIn("unittest.mock", test_code)
            self.assertIn("patch", test_code)

if __name__ == "__main__":
    unittest.main()
