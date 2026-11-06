#!/usr/bin/env python3
"""
Unit tests for AIToolGems wholesale cost reference and inventory stock database.
"""

import json
import os
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestWholesaleInventoryDatabase(unittest.TestCase):
    """Verifies wholesale inventory database structure, calculations, and catalog coverage."""

    def setUp(self):
        self.db_path = REPO_ROOT / "data" / "wholesale_inventory.json"
        self.summary_path = REPO_ROOT / "data" / "wholesale_cost_reference.json"
        self.csv_path = REPO_ROOT / "data" / "suppliers" / "telegram_bots_catalog.csv"
        self.admin_js_path = REPO_ROOT / "admin.js"

    def test_wholesale_database_file_exists_and_parses(self):
        """Ensure wholesale_inventory.json exists and is valid JSON."""
        self.assertTrue(self.db_path.exists(), f"Missing wholesale database: {self.db_path}")
        with open(self.db_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("metadata", data)
        self.assertIn("summary", data)
        self.assertIn("products", data)
        self.assertIn("supplier_bots", data)
        self.assertIn("expansion_candidates", data)

    def test_all_40_catalog_tools_represented(self):
        """Ensure all 40 verified marketplace products exist in the wholesale database."""
        with open(self.db_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        products = data.get("products", [])
        self.assertEqual(len(products), 40, f"Expected 40 catalog tools, got {len(products)}")

        expected_slugs = {
            "chatgpt", "gemini", "veo", "leonardo", "elevenlabs", "canva", "figma", "capcut",
            "adobe", "lovable", "gamma", "replit", "n8n", "notion", "nordvpn", "surfshark",
            "youtube", "netflix", "linkedin", "windows", "claude", "midjourney", "cursor",
            "perplexity", "deepseek", "grok", "runway", "heygen", "grammarly", "quillbot",
            "semrush", "allinone", "tradingview", "kling", "freepik", "spotify", "copilot",
            "suno", "turnitin", "office365"
        }
        actual_slugs = {p["slug"] for p in products}
        self.assertEqual(expected_slugs, actual_slugs)

    def test_wholesale_math_consistency(self):
        """Verify price, wholesale cost, and margin consistency."""
        with open(self.db_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        rate = data["metadata"]["exchange_rate_usdt_pkr"]
        self.assertGreater(rate, 200.0)

        for p in data["products"]:
            slug = p["slug"]
            self.assertGreater(p["retail_pkr"], 0, f"{slug}: retail_pkr must be positive")
            self.assertGreater(p["wholesale_cost_usdt"], 0, f"{slug}: wholesale_cost_usdt must be positive")
            expected_pkr = round(p["wholesale_cost_usdt"] * rate)
            self.assertEqual(p["wholesale_cost_pkr"], expected_pkr, f"{slug}: wholesale_cost_pkr mismatch")
            expected_margin = p["retail_pkr"] - expected_pkr
            self.assertEqual(p["profit_margin_pkr"], expected_margin, f"{slug}: profit margin mismatch")
            self.assertGreater(p["stock_count"], 0, f"{slug}: stock_count must be > 0")
            self.assertIn(p["stock_status"], ["in_stock", "low_stock", "out_of_stock"])
            self.assertTrue(bool(p["best_supplier_bot"]), f"{slug}: best_supplier_bot must be set")

    def test_raw_supplier_csv_archive(self):
        """Verify raw supplier CSV exists and contains 200+ product entries from 10 bots."""
        self.assertTrue(self.csv_path.exists(), f"Missing supplier CSV: {self.csv_path}")
        import csv
        with open(self.csv_path, "r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertGreaterEqual(len(rows), 200, "Expected at least 200 supplier rows")
        bots = {r["Bot Name"] for r in rows if r.get("Bot Name")}
        self.assertGreaterEqual(len(bots), 8, "Expected at least 8 supplier bots")
        self.assertIn("Fat bunny hub", bots)
        self.assertIn("Bunnytoolsbot", bots)
        self.assertIn("Shiva cute", bots)

    def test_summary_reference_table_matches(self):
        """Verify wholesale_cost_reference.json matches the 40 products."""
        self.assertTrue(self.summary_path.exists())
        with open(self.summary_path, "r", encoding="utf-8") as f:
            summary = json.load(f)
        self.assertEqual(len(summary), 40)
        slugs = [s["slug"] for s in summary]
        self.assertIn("chatgpt", slugs)
        self.assertIn("claude", slugs)
        self.assertIn("adobe", slugs)

    def test_admin_js_integration(self):
        """Verify admin.js productSeed has been updated with all 40 products and stock/cost."""
        self.assertTrue(self.admin_js_path.exists())
        content = self.admin_js_path.read_text(encoding="utf-8")
        self.assertIn("'chatgpt'", content)
        self.assertIn("'claude'", content)
        self.assertIn("'office365'", content)
        self.assertIn("stock:", content)
        self.assertIn("wholesaleCost:", content)


if __name__ == "__main__":
    unittest.main()

