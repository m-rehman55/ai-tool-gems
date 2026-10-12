#!/usr/bin/env python3
"""
Unit tests for ScopeGuard in seo-agent
-------------------------------------
Verifies Pakistan-exclusive scope enforcement and foreign/JP material blocking.
"""

import sys
from pathlib import Path
import unittest

# Ensure seo-agent directory is on Python path
AGENT_DIR = Path(__file__).resolve().parent.parent
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

from agent.scope_guard import ScopeGuard, ScopeResult

class TestScopeGuard(unittest.TestCase):

    def setUp(self):
        self.guard = ScopeGuard()

    def test_clean_pakistani_content_passes(self):
        text = """
        Buy ChatGPT Plus in Pakistan with PKR pricing.
        Pay conveniently via EasyPaisa or JazzCash.
        Official delivery in Lahore and Karachi within minutes.
        """
        res = self.guard.check_text(text)
        self.assertTrue(res.passed)
        self.assertEqual(len(res.violations), 0)

    def test_jpy_currency_token_blocked(self):
        text = "ChatGPT Plus subscription cost: 3000 JPY per month."
        res = self.guard.check_text(text)
        self.assertFalse(res.passed)
        self.assertTrue(any("JPY" in v.message for v in res.violations))

    def test_yen_symbol_blocked(self):
        text = "Price: ¥2500 per month."
        res = self.guard.check_text(text)
        self.assertFalse(res.passed)
        self.assertTrue(any("¥" in v.message for v in res.violations))

    def test_japanese_script_blocked(self):
        text = "Claude Pro official guide: こんにちは"
        res = self.guard.check_text(text)
        self.assertFalse(res.passed)
        self.assertTrue(any(v.rule == "NO_JAPANESE_SCRIPT" for v in res.violations))

    def test_jp_url_path_blocked(self):
        url = "https://aitoolgems.tech/jp/chatgpt-plus/"
        res = self.guard.check_url(url)
        self.assertFalse(res.passed)
        self.assertTrue(any("Prohibited JP route" in v.message for v in res.violations))

    def test_foreign_domain_blocked(self):
        url = "https://otherdomain.com/tools/claude/"
        res = self.guard.check_url(url)
        self.assertFalse(res.passed)
        self.assertTrue(any(v.rule == "FOREIGN_DOMAIN" for v in res.violations))

    def test_transactional_page_requires_pkr_and_easypaisa(self):
        # Missing PKR and EasyPaisa
        missing_both = "<html><body><h1>ChatGPT Plus</h1><p>Buy now for USD 20 with Credit Card</p></body></html>"
        res1 = self.guard.check_transactional_page(missing_both, "tools/chatgpt.html")
        self.assertFalse(res1.passed)
        self.assertTrue(any(v.rule == "MISSING_PKR_CURRENCY" for v in res1.violations))
        self.assertTrue(any(v.rule == "MISSING_PAKISTAN_PAYMENT" for v in res1.violations))

        # Complete Pakistani transactional signals
        valid_page = "<html><body><h1>ChatGPT Plus</h1><p>Price: Rs. 1,500 PKR via EasyPaisa or JazzCash</p></body></html>"
        res2 = self.guard.check_transactional_page(valid_page, "tools/chatgpt.html")
        self.assertTrue(res2.passed)

if __name__ == "__main__":
    unittest.main()
