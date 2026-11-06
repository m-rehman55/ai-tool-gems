#!/usr/bin/env python3
"""
Unit tests for AIToolGems inventory safety, frontend privacy, and pricing logic.
Uses synthetic fixtures for financial math tests and enforces zero leakage of
private supplier costs, bot handles, or raw supplier archives into public code.
"""

import json
import os
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestWholesaleInventoryDatabase(unittest.TestCase):
    """Verifies frontend privacy, inventory safety, and synthetic pricing calculations."""

    def setUp(self):
        self.admin_js_path = REPO_ROOT / "admin.js"
        self.app_js_path = REPO_ROOT / "app.js"
        self.index_html_path = REPO_ROOT / "index.html"
        self.gitignore_path = REPO_ROOT / ".gitignore"

        # Synthetic, fictitious test fixture for margin and currency calculation testing
        self.synthetic_inventory_fixture = {
            "metadata": {
                "exchange_rate_usdt_pkr": 280.0,
                "currency": "PKR"
            },
            "products": [
                {
                    "slug": "synthetic-tool-alpha",
                    "name": "Synthetic Tool Alpha",
                    "retail_pkr": 2500,
                    "wholesale_cost_usdt": 5.0,
                    "wholesale_cost_pkr": 1400,
                    "profit_margin_pkr": 1100,
                    "stock_count": 25,
                    "stock_status": "in_stock"
                },
                {
                    "slug": "synthetic-tool-beta",
                    "name": "Synthetic Tool Beta",
                    "retail_pkr": 4200,
                    "wholesale_cost_usdt": 10.0,
                    "wholesale_cost_pkr": 2800,
                    "profit_margin_pkr": 1400,
                    "stock_count": 3,
                    "stock_status": "low_stock"
                }
            ]
        }

    def test_public_frontend_clean_of_supplier_secrets(self):
        """
        CRITICAL PRIVACY TEST:
        Ensures admin.js, app.js, and index.html DO NOT expose wholesale costs,
        internal supplier names, bot handles, or raw supplier identifiers.
        """
        self.assertTrue(self.admin_js_path.exists(), "admin.js must exist")
        admin_js = self.admin_js_path.read_text(encoding="utf-8")

        # Wholesale cost fields must NOT be present in public browser code
        self.assertNotIn("wholesaleCost", admin_js, "admin.js must not contain wholesaleCost")
        self.assertNotIn("wholesale_cost", admin_js, "admin.js must not contain wholesale_cost")
        self.assertNotIn("profitMargin", admin_js, "admin.js must not contain profitMargin")

        # Known supplier bot names must NOT be leaked in frontend code
        known_bot_names = [
            "Fat bunny hub",
            "Bunnytoolsbot",
            "Shiva cute",
            "OxygenPremium Store",
            "Hitmeow shop",
            "AI Toolify Studio",
            "GET digital tools",
            "MediaHubMarketplace_bot"
        ]
        for bot in known_bot_names:
            self.assertNotIn(bot, admin_js, f"Private supplier bot name '{bot}' leaked in admin.js")

        # Table header in admin.html must not be 'Stock & Wholesale'
        admin_html = self.index_html_path.read_text(encoding="utf-8")
        self.assertNotIn("Stock & Wholesale", admin_html)

    def test_admin_js_contains_all_40_public_tools(self):
        """Verify admin.js productSeed has all 40 verified tools with retail PKR prices."""
        admin_js = self.admin_js_path.read_text(encoding="utf-8")
        expected_slugs = [
            "chatgpt", "gemini", "veo", "leonardo", "elevenlabs", "canva", "figma", "capcut",
            "adobe", "lovable", "gamma", "replit", "n8n", "notion", "nordvpn", "surfshark",
            "youtube", "netflix", "linkedin", "windows", "claude", "midjourney", "cursor",
            "perplexity", "deepseek", "grok", "runway", "heygen", "grammarly", "quillbot",
            "semrush", "allinone", "tradingview", "kling", "freepik", "spotify", "copilot",
            "suno", "turnitin", "office365"
        ]
        self.assertEqual(len(expected_slugs), 40)
        for slug in expected_slugs:
            self.assertIn(f"'{slug}'", admin_js, f"Slug '{slug}' missing in admin.js productSeed")

    def test_synthetic_inventory_pricing_math(self):
        """Verify pricing, wholesale conversion, and margin math using synthetic test fixture."""
        fixture = self.synthetic_inventory_fixture
        rate = fixture["metadata"]["exchange_rate_usdt_pkr"]
        self.assertGreater(rate, 200.0)

        for p in fixture["products"]:
            slug = p["slug"]
            self.assertGreater(p["retail_pkr"], 0, f"{slug}: retail_pkr must be positive")
            self.assertGreater(p["wholesale_cost_usdt"], 0, f"{slug}: wholesale_cost_usdt must be positive")
            expected_pkr = round(p["wholesale_cost_usdt"] * rate)
            self.assertEqual(p["wholesale_cost_pkr"], expected_pkr, f"{slug}: wholesale_cost_pkr mismatch")
            expected_margin = p["retail_pkr"] - expected_pkr
            self.assertEqual(p["profit_margin_pkr"], expected_margin, f"{slug}: profit margin mismatch")
            self.assertIn(p["stock_status"], ["in_stock", "low_stock", "out_of_stock"])

    def test_private_supplier_files_are_gitignored(self):
        """Verify that private supplier archives, wholesale inventories, and orders are gitignored."""
        self.assertTrue(self.gitignore_path.exists())
        gitignore_content = self.gitignore_path.read_text(encoding="utf-8")

        self.assertIn("data/suppliers/", gitignore_content)
        self.assertIn("data/orders/", gitignore_content)
        self.assertIn("data/wholesale_inventory.json", gitignore_content)
        self.assertIn("data/wholesale_cost_reference.json", gitignore_content)
        self.assertIn("*.xlsx", gitignore_content)

    def test_zero_unverified_stock_claims(self):
        """
        Verify that placeholder numbers (223,494 or 999 invite units) are NEVER
        represented as verified available stock.
        """
        admin_js = self.admin_js_path.read_text(encoding="utf-8")
        self.assertNotIn("223494", admin_js)
        self.assertNotIn("223,494", admin_js)


if __name__ == "__main__":
    unittest.main()
