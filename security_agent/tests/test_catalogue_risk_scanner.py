"""
Unit tests for Special Catalogue Risk Scanner & Compliance Firewall (Phase 14).
Validates 10 high-risk domains, cautionary IDs 158–173 & 175 isolation, and zero storefront leakage.
"""

import json
import unittest
from pathlib import Path

from security_agent.catalogue_risk_scanner import (
    CAUTIONARY_CATALOG_NUMBERS,
    PROHIBITED_RISK_DOMAINS,
    CatalogueRiskScanner,
)


class TestCatalogueRiskScanner(unittest.TestCase):

    def setUp(self):
        self.scanner = CatalogueRiskScanner()
        self.base_dir = Path(__file__).resolve().parent.parent.parent

    def test_all_10_risk_domains_defined(self):
        """Verify all 10 mandated high-risk categories are monitored."""
        expected_domains = [
            "Spam or fake engagement services",
            "Social media account stock or verification",
            "Clone or aged accounts",
            "OTP and virtual number services",
            "Education or webmail account resale",
            "Region or subscription restriction bypass",
            "Payment account resale",
            "Crypto or banking account products",
            "Platform accounts and balances",
            "Administrative/test placeholders",
        ]
        self.assertEqual(len(PROHIBITED_RISK_DOMAINS), 10)
        for domain in expected_domains:
            self.assertIn(domain, PROHIBITED_RISK_DOMAINS)

    def test_cautionary_catalog_numbers_defined(self):
        """Ensure IDs 158 to 173 and 175 are tracked."""
        expected_ids = set(range(158, 174)) | {175}
        self.assertEqual(CAUTIONARY_CATALOG_NUMBERS, expected_ids)

    def test_master_register_cautionary_entries_status(self):
        """Verify that in the master register, all cautionary IDs are strictly HOLD or BLOCKED."""
        violations = self.scanner.scan_master_register()
        self.assertEqual(violations, [], f"Master register cautionary violations: {violations}")

    def test_storefront_app_js_clean(self):
        """Verify that no cautionary item or prohibited keyword exists in app.js."""
        violations = self.scanner.scan_storefront_leakage()
        self.assertEqual(violations, [], f"app.js risk leakage: {violations}")

    def test_tools_directory_isolation(self):
        """Verify that no prohibited risk tool slug exists under /tools/."""
        violations = self.scanner.scan_tools_directories()
        self.assertEqual(violations, [], f"Tools directory risk leakage: {violations}")

    def test_sitemap_isolation(self):
        """Verify sitemap.xml does not contain any prohibited risk terms or URLs."""
        violations = self.scanner.scan_sitemap_isolation()
        self.assertEqual(violations, [], f"sitemap.xml risk leakage: {violations}")

    def test_wholesale_inventory_isolation(self):
        """Verify wholesale_inventory.json is free of cautionary items."""
        violations = self.scanner.scan_wholesale_inventory()
        self.assertEqual(violations, [], f"Wholesale inventory risk leakage: {violations}")

    def test_comprehensive_audit_result_is_clean(self):
        """Verify overall system scan returns is_clean=True with zero violations."""
        result = self.scanner.run_comprehensive_risk_audit()
        self.assertTrue(result.is_clean)
        self.assertEqual(len(result.active_storefront_violations), 0)
        self.assertEqual(len(result.sitemap_violations), 0)
        self.assertEqual(len(result.wholesale_violations), 0)
        self.assertEqual(len(result.unresolved_status_violations), 0)
        self.assertGreaterEqual(result.cautionary_entries_audited, 17)

    def test_firewall_blocks_prohibited_candidates(self):
        """Verify active firewall blocks publication attempts for all risk categories."""
        risky_candidates = [
            {"slug": "sms-otp-verification-service", "title": "Buy OTP Bypass Numbers", "meta_description": "Virtual SIM for SMS"},
            {"slug": "aged-hotmail-accounts", "title": "Aged Webmail Accounts Stock", "meta_description": "Aged Gmail and Outlook for bulk mailing"},
            {"slug": "paypal-verified-reseller", "title": "PayPal Verified Accounts", "meta_description": "Buy verified payment accounts"},
            {"slug": "bybit-crypto-account", "title": "ByBit Verified Accounts", "meta_description": "KYC passed exchange access"},
            {"slug": "tiktok-follower-boost", "title": "TikTok Fake Followers", "meta_description": "Automated engagement booster"},
            {"slug": "reddit-aged-high-karma", "title": "Reddit Aged Accounts", "meta_description": "5 year old clone accounts"},
            {"slug": "spotify-family-region-bypass", "title": "Spotify Family Plan Region Limit Resolution", "meta_description": "Circumvent territorial limit"},
            {"slug": "internal-test-placeholder", "title": "Test Placeholders", "meta_description": "Do not buy internal test item"},
        ]

        for cand in risky_candidates:
            is_valid, errors = self.scanner.validate_candidate_for_publication(cand)
            self.assertFalse(is_valid, f"Expected candidate {cand['slug']} to be blocked!")
            self.assertTrue(any("FIREWALL_BLOCKED" in err for err in errors))

    def test_firewall_permits_clean_saas_products(self):
        """Verify firewall allows legitimate productivity tools."""
        clean_candidates = [
            {"slug": "chatgpt-plus", "title": "ChatGPT Plus Shared Subscription", "meta_description": "OpenAI GPT-4o private access in Pakistan"},
            {"slug": "cursor-pro", "title": "Cursor Pro AI Code Editor", "meta_description": "Official AI-assisted IDE for engineers in Pakistan"},
            {"slug": "claude-pro", "title": "Claude 3.5 Sonnet Pro", "meta_description": "Anthropic AI subscription for researchers"},
        ]

        for cand in clean_candidates:
            is_valid, errors = self.scanner.validate_candidate_for_publication(cand)
            self.assertTrue(is_valid, f"Expected clean product {cand['slug']} to pass, got: {errors}")
            self.assertEqual(errors, [])

    def test_risk_review_json_structure_and_disclaimer(self):
        """Verify data/catalogue_risk_review.json has correct disclaimer, entries, and all cautionary items."""
        json_path = self.base_dir / "data" / "catalogue_risk_review.json"
        self.assertTrue(json_path.exists())

        with open(json_path, mode="r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("disclaimer", data)
        # Verify explicit disclaimer about risk flags vs legal findings
        self.assertIn("risk flags", data["disclaimer"].lower())
        self.assertIn("legal findings", data["disclaimer"].lower())

        entries = {e["catalog_number"]: e for e in data.get("cautionary_entries", [])}
        for num in CAUTIONARY_CATALOG_NUMBERS:
            self.assertIn(num, entries, f"Catalog ID {num} missing from catalogue_risk_review.json")
            entry = entries[num]
            self.assertIn(entry["status"], ["HOLD", "BLOCKED"])
            self.assertFalse(entry["checkout_enabled"])
            self.assertFalse(entry["merchant_feed_eligible"])
            self.assertFalse(entry["ads_eligible"])
            self.assertTrue(len(entry["evidence_findings"]) > 20)
            self.assertTrue(len(entry["operational_action"]) > 10)


if __name__ == "__main__":
    unittest.main()

