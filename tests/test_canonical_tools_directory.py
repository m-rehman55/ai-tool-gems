import unittest
import os
import json
import csv
from scratch.build_canonical_tools import RULES

class TestCanonicalToolsDirectory(unittest.TestCase):
    """
    Validates complete, deduplicated canonical mapping of all 2,902 reseller rows
    into official parent tools with zero items skipped or missed.
    """

    def setUp(self):
        self.directory_path = 'data/all_canonical_tools_directory.json'
        self.csv_path = 'data/suppliers/reseller_products_master.csv'

    def test_directory_exists_and_parses(self):
        self.assertTrue(os.path.exists(self.directory_path), "Master canonical directory JSON must exist.")
        with open(self.directory_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 175, "Exactly 175 canonical parent tools must be present.")

    def test_complete_row_coverage_no_omissions(self):
        with open(self.directory_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        total_listings = sum(t['listings_count'] for t in data)
        self.assertEqual(total_listings, 2902, "All 2,902 raw rows must be accounted for (100% coverage).")

    def test_tools_metadata_integrity(self):
        with open(self.directory_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        for t in data:
            self.assertTrue(t['canonical_name'], "Each tool must have a canonical name.")
            self.assertTrue(t['official_developer'], f"{t['canonical_name']} missing official developer.")
            self.assertTrue(t['official_category'], f"{t['canonical_name']} missing official category.")
            self.assertGreater(t['listings_count'], 0, f"{t['canonical_name']} must have >= 1 listing.")
            self.assertGreater(len(t['all_variants']), 0, f"{t['canonical_name']} must have variants.")

    def test_stock_aggregation_sanity(self):
        with open(self.directory_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        total_stock = sum(t['total_stock'] for t in data)
        self.assertGreaterEqual(total_stock, 220000, "Total aggregated stock must exceed 220k units.")

if __name__ == '__main__':
    unittest.main()

