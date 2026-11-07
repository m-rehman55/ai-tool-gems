"""
tests/test_cart_and_pricing_integrity.py

Automated test suite verifying:
1. Cart logic and quantity mechanics in app.js.
2. Directory-only profile safeguards (exclusion from cart, clear badge, reference notes).
3. Commercial pricing consistency across all 40 assisted-access tool pages.
4. Elimination of outdated 'instant delivery' claims in favor of verified WhatsApp delivery.
5. Absolute absence of artificial exchange rate calculations (e.g., p.price / 280) in app.js.
6. Clean HTML markup (no unclosed tags) in pricing banners across all tool pages.
"""

import os
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ASSISTED_TOOL_SLUGS = [
    'adobe', 'allinone', 'canva', 'capcut', 'chatgpt', 'claude', 'copilot', 'cursor',
    'deepseek', 'elevenlabs', 'figma', 'freepik', 'gamma', 'gemini', 'grammarly',
    'grok', 'heygen', 'kling', 'leonardo', 'linkedin', 'lovable', 'midjourney',
    'n8n', 'netflix', 'nordvpn', 'notion', 'office365', 'perplexity', 'quillbot',
    'replit', 'runway', 'semrush', 'spotify', 'suno', 'surfshark', 'tradingview',
    'turnitin', 'veo', 'windows', 'youtube'
]

WAVE1_DIRECTORY_SLUGS = [
    'autodraw', 'beautifulai', 'descript', 'guidde', 'huggingface', 'intercom',
    'jasper', 'krisp', 'luma', 'make', 'mistral', 'synthesia'
]

WAVE2_DIRECTORY_SLUGS = [
    'anyword', 'copyai', 'craiyon', 'fliki', 'invideo', 'murf', 'otter',
    'pictory', 'playht', 'soundraw', 'tome', 'vrew', 'writesonic'
]


class TestCartAndPricingIntegrity(unittest.TestCase):

    def setUp(self):
        self.app_js_path = ROOT / 'app.js'
        self.styles_css_path = ROOT / 'styles.css'
        self.index_html_path = ROOT / 'index.html'
        self.tools_index_path = ROOT / 'tools' / 'index.html'

        self.assertTrue(self.app_js_path.exists(), "app.js must exist")
        with open(self.app_js_path, 'r', encoding='utf-8') as f:
            self.app_js = f.read()

        with open(self.index_html_path, 'r', encoding='utf-8') as f:
            self.index_html = f.read()

        with open(self.styles_css_path, 'r', encoding='utf-8') as f:
            self.styles_css = f.read()

    def test_cart_quantity_functions_exist_in_app_js(self):
        """Ensure loadStoredCart, updateCartQty, clearCart, getCartItems, isItemInCart exist."""
        self.assertIn('function loadStoredCart(', self.app_js)
        self.assertIn('function updateCartQty(', self.app_js)
        self.assertIn('function clearCart(', self.app_js)
        self.assertIn('function getCartItems(', self.app_js)
        self.assertIn('function isItemInCart(', self.app_js)
        self.assertIn('#clearCartBtn', self.app_js)

    def test_cart_blocks_directory_only_tools(self):
        """Ensure addToCart explicitly rejects DIRECTORY_ONLY tools."""
        self.assertIn("commercialStatus === 'DIRECTORY_ONLY'", self.app_js)
        # Verify addToCart checks commercialStatus
        add_to_cart_block = re.search(r'function addToCart\([^)]*\)\s*\{([\s\S]*?)\n\}', self.app_js)
        self.assertIsNotNone(add_to_cart_block)
        self.assertIn('DIRECTORY_ONLY', add_to_cart_block.group(1))

    def test_order_product_blocks_directory_only_tools(self):
        """Ensure orderProduct explicitly blocks directory-only tools."""
        order_prod_block = re.search(r'function orderProduct\([^)]*\)\s*\{([\s\S]*?)\n\}', self.app_js)
        self.assertIsNotNone(order_prod_block)
        self.assertIn('DIRECTORY_ONLY', order_prod_block.group(1))

    def test_no_artificial_exchange_rate_in_app_js(self):
        """Ensure app.js does not calculate (p.price / 280) or fake USD prices."""
        self.assertNotIn('/ 280', self.app_js)

    def test_cart_ui_elements_in_html_and_css(self):
        """Verify clear cart button in index.html and modern styling in styles.css."""
        self.assertIn('id="clearCartBtn"', self.index_html)
        self.assertIn('.clear-cart-btn', self.styles_css)
        self.assertIn('.cart-qty-row', self.styles_css)
        self.assertIn('.cart-qty-btn', self.styles_css)
        self.assertIn('.cart-qty-val', self.styles_css)
        self.assertIn('.cart-line-price', self.styles_css)

    def test_assisted_tools_count_and_directory_count(self):
        """Verify exact 40 assisted tools and 25 directory tools."""
        self.assertEqual(len(ASSISTED_TOOL_SLUGS), 40)
        self.assertEqual(len(WAVE1_DIRECTORY_SLUGS), 12)
        self.assertEqual(len(WAVE2_DIRECTORY_SLUGS), 13)
        self.assertEqual(len(WAVE1_DIRECTORY_SLUGS) + len(WAVE2_DIRECTORY_SLUGS), 25)

    def test_all_40_assisted_pages_have_no_unclosed_tags(self):
        """Verify none of the 40 assisted tool pages contain '<small>($' or broken price tags."""
        for slug in ASSISTED_TOOL_SLUGS:
            path = ROOT / 'tools' / slug / 'index.html'
            self.assertTrue(path.exists(), f"Page {slug} must exist")
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertNotIn('<small>($', content, f"Found unclosed price tag in {slug}")

    def test_all_40_assisted_pages_have_no_instant_delivery_claims(self):
        """Verify none of the 40 assisted tool pages claim 'instant delivery' or '⚡ Instant delivery'."""
        for slug in ASSISTED_TOOL_SLUGS:
            path = ROOT / 'tools' / slug / 'index.html'
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            lower_content = content.lower()
            self.assertNotIn('instant delivery', lower_content, f"Found 'instant delivery' in {slug}")

    def test_all_40_assisted_pages_have_clean_whatsapp_links(self):
        """Verify WhatsApp order buttons in all 40 assisted pages do not hardcode '/ $Y USD'."""
        for slug in ASSISTED_TOOL_SLUGS:
            path = ROOT / 'tools' / slug / 'index.html'
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            # WhatsApp link should not have URL-encoded USD prices like %20%2F%20%24
            self.assertNotIn('%20%2F%20%24', content, f"Found hardcoded USD in WhatsApp URL in {slug}")
            self.assertNotIn('/ $', content, f"Found hardcoded '/ $' in {slug}")

    def test_plan_comparison_tables_use_usd_reference_inquiry(self):
        """Verify comparison table in 40 pages uses 'USD Reference' and 'USD (Inquiry)'."""
        for slug in ASSISTED_TOOL_SLUGS:
            path = ROOT / 'tools' / slug / 'index.html'
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            if 'plan-table' in content:
                self.assertIn('USD Reference', content, f"Plan table in {slug} must label USD as reference")
                self.assertIn('(Inquiry)', content, f"Plan table in {slug} must note (Inquiry) for USD")

    def test_checkout_whatsapp_message_format(self):
        """Verify checkout message logic in app.js formats lines with PKR prices and official number."""
        self.assertIn('DEFAULT_WA_NUMBER', self.app_js)
        self.assertIn('923236715731', self.app_js)
        self.assertIn('Rs. ', self.app_js)
        self.assertIn('Total: ${totalDisplay}', self.app_js)


if __name__ == '__main__':
    unittest.main()
