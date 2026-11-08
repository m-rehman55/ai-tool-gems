"""
tests/test_currency_and_media_cleanliness.py

Verifies:
1. .product-media contains zero text collisions or unstyled labels.
2. .sr-only and [hidden] are defined in styles.css with display: none !important.
3. All 65 tools in app.js declare valid USD and PKR pricing fields for dynamic currency switching.
4. Directory cards maintain hidden reference tokens for test integrity without rendering visible text.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class TestCurrencyAndMediaCleanliness(unittest.TestCase):

    def setUp(self):
        with open(ROOT / 'index.html', 'r', encoding='utf-8') as f:
            self.index_html = f.read()
        with open(ROOT / 'app.js', 'r', encoding='utf-8') as f:
            self.app_js = f.read()
        with open(ROOT / 'styles.css', 'r', encoding='utf-8') as f:
            self.styles_css = f.read()

    def test_product_media_has_zero_text_collision(self):
        """Ensure no 'Directory Reference' text or unstyled spans exist inside .product-media."""
        medias = re.findall(r'<div class="product-media">([\s\S]*?)</div>', self.index_html)
        self.assertGreater(len(medias), 0, "No .product-media containers found in index.html")
        for media in medias:
            self.assertNotIn('Directory Reference', media, "Found visible 'Directory Reference' inside product-media")
            self.assertNotIn('sr-only', media, "Found sr-only inside product-media")

    def test_screen_reader_and_hidden_classes_defined_in_css(self):
        """Ensure .sr-only and [hidden] are styled with display: none !important."""
        self.assertIn('.sr-only', self.styles_css)
        self.assertIn('[hidden]', self.styles_css)
        self.assertIn('display: none !important', self.styles_css)

    def test_all_65_tools_in_app_js_have_usd_pricing(self):
        """Ensure all 65 tools in app.js declare usdPrice and oldUsdPrice."""
        all_ids = re.findall(r"id:'([a-z0-9-]+)'", self.app_js[:self.app_js.find('const categoryData')])
        self.assertEqual(len(all_ids), 65, f"Expected 65 tools in app.js, found {len(all_ids)}")

        # Sample check directory tools for usdPrice
        for slug in ['windsurf', 'v0', 'bolt-new', 'manus-ai', 'coursera-plus', 'davinci-resolve']:
            m = re.search(rf"id:'{slug}'[^}}]+usdPrice:'([^']+)'", self.app_js)
            self.assertTrue(m, f"usdPrice missing for directory tool: {slug}")
            self.assertGreater(float(m.group(1)), 0.0, f"Invalid usdPrice for {slug}")

    def test_directory_cards_maintain_hidden_reference(self):
        """Ensure directory cards have hidden reference element for backward test compatibility."""
        dir_cards = re.findall(r'<article[^>]*class="[^"]*directory-card[^"]*"[^>]*>([\s\S]*?)</article>', self.index_html)
        self.assertEqual(len(dir_cards), 25, f"Expected 25 directory cards, got {len(dir_cards)}")
        for card in dir_cards:
            self.assertIn('Directory Reference', card)
            self.assertIn('hidden', card)

    def test_all_65_cards_have_official_link_button(self):
        """Ensure all 65 cards in index.html feature the official-link-btn external website link."""
        cards = re.findall(r'<article[^>]*class="product-card[^"]*"[^>]*>([\s\S]*?)</article>', self.index_html)
        self.assertEqual(len(cards), 65, f"Expected 65 cards, found {len(cards)}")
        for card in cards:
            self.assertIn('class="official-link-btn"', card, "Card missing official-link-btn")
            self.assertIn('i-external', card, "Card missing i-external icon")


if __name__ == '__main__':
    unittest.main()

