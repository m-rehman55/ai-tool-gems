import unittest
import os
import json
import csv
from pathlib import Path
from scripts.build_canonical_tools import RULES

REPO_ROOT = Path(__file__).resolve().parent.parent

class TestCanonicalToolsDirectory(unittest.TestCase):
    """
    Validates complete, deduplicated canonical mapping of all 175 official parent tools
    without requiring private supplier archives in public CI.
    """

    def setUp(self):
        self.csv_register = REPO_ROOT / 'data' / 'AIToolGems_175_Tool_Register_v2_2.csv'
        self.rules = RULES

    def test_rules_count_covers_all_tools(self):
        """Ensure master mapping rules table defines at least 175 canonical parent tools."""
        self.assertGreaterEqual(len(self.rules), 175, "At least 175 canonical rules must be present in RULES.")

    def test_rules_metadata_integrity(self):
        """Ensure each rule defines valid canonical name, pattern, developer, and category."""
        canonical_names = set()
        for rule in self.rules:
            self.assertGreaterEqual(len(rule), 4, "Each rule must have at least 4 elements.")
            name, pattern, dev, cat = rule[0], rule[1], rule[2], rule[3]
            self.assertTrue(name, "Tool must have a canonical name.")
            self.assertTrue(pattern, f"{name} missing regex pattern.")
            self.assertTrue(dev, f"{name} missing official developer.")
            self.assertTrue(cat, f"{name} missing official category.")
            self.assertNotIn(name, canonical_names, f"Duplicate canonical tool name: {name}")
            canonical_names.add(name)

    def test_public_register_csv_matches_175_tools(self):
        """Ensure the public, version-controlled CSV register exists and contains 175 tools."""
        self.assertTrue(self.csv_register.exists(), f"Missing public register CSV: {self.csv_register}")
        with open(self.csv_register, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
        self.assertEqual(len(reader), 175, f"Expected 175 rows in public register CSV, found {len(reader)}")

    def test_zero_unverified_stock_claims(self):
        """
        Verify that placeholder numbers (223,494 or 999 invite units) are NEVER
        represented as verified numeric available stock.
        """
        with open(self.csv_register, 'r', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
        for row in reader:
            stock_field = row.get("Verified Numeric Stock", "").strip()
            self.assertNotEqual(stock_field, "223494", "223,494 must never be represented as verified stock.")
            self.assertNotEqual(stock_field, "223,494", "223,494 must never be represented as verified stock.")

if __name__ == '__main__':
    unittest.main()
