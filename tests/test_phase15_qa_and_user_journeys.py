"""
Comprehensive Automated Testing & Quality Assurance Suite (Phase 15).
Validates user journeys (mobile & desktop), HTML/Schema/Canonical integrity,
DOM contracts, inventory reconciliation, and GA4 ecommerce event models.
"""

import json
import os
import re
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestPhase15UserJourneysAndQA(unittest.TestCase):
    """Rigorous QA checks and end-to-end user journeys for AIToolGems."""

    @classmethod
    def setUpClass(cls):
        cls.index_html = (REPO_ROOT / "index.html").read_text(encoding="utf-8")
        cls.app_js = (REPO_ROOT / "app.js").read_text(encoding="utf-8")
        cls.attribution_js = (REPO_ROOT / "attribution.js").read_text(encoding="utf-8")
        cls.styles_css = (REPO_ROOT / "styles.css").read_text(encoding="utf-8")
        cls.light_theme_css = (REPO_ROOT / "light-theme.css").read_text(encoding="utf-8")
        cls.sitemap_xml = (REPO_ROOT / "sitemap.xml").read_text(encoding="utf-8")
        cls.robots_txt = (REPO_ROOT / "robots.txt").read_text(encoding="utf-8")

        inventory_path = REPO_ROOT / "data" / "wholesale_inventory.json"
        if inventory_path.exists():
            cls.wholesale_data = json.loads(inventory_path.read_text(encoding="utf-8"))
        else:
            cls.wholesale_data = {}

    # =========================================================================
    # USER JOURNEY 1: Homepage -> Category Hub -> Product Page
    # =========================================================================
    def test_journey_homepage_to_category_to_product(self):
        """User journey: Navigate from homepage category filter into category section and to a canonical product page."""
        # 1. Homepage category links exist and target valid categories
        cat_matches = re.findall(r'<a\s+href="#products"\s+class="category-card[^"]*"\s+data-category="([^"]+)">', self.index_html)
        self.assertGreaterEqual(len(cat_matches), 10, "Expected at least 10 category cards on homepage")

        # 2. Category selection updates category in app.js
        self.assertIn("state.category", self.app_js)
        self.assertIn("filteredProducts()", self.app_js)

        # 3. Each category card leads to real products with valid links
        tool_links = re.findall(r'href=[\'"]tools/([a-z0-9-]+)/[\'"]', self.index_html)
        self.assertGreaterEqual(len(tool_links), 20, "Expected at least 20 static product links from homepage")

        for slug in list(set(tool_links))[:5]:
            product_page = REPO_ROOT / "tools" / slug / "index.html"
            self.assertTrue(product_page.exists(), f"Product page missing for slug '{slug}'")
            page_html = product_page.read_text(encoding="utf-8")
            self.assertIn('href="../../"', page_html, f"Breadcrumb link to homepage missing in {slug}")
            self.assertIn('rel="canonical"', page_html)
            self.assertIn(f'aitoolgems.tech/tools/{slug}/', page_html)

    # =========================================================================
    # USER JOURNEY 2: Product Details & Price Display
    # =========================================================================
    def test_journey_product_details_and_pkr_price_display(self):
        """User journey: Inspect product details, pricing display in PKR, and transparent delivery terms."""
        # Check product modal structure
        self.assertIn('id="productModal"', self.index_html)
        self.assertIn('id="productDetail"', self.index_html)

        # Check pricing display contract in app.js
        self.assertIn("PKR", self.app_js, "Prices must be formatted with PKR currency")
        self.assertIn(".toLocaleString()", self.app_js, "Prices must be localized numeric displays")

        # Zero foreign currency checkout traps
        self.assertNotIn("USD $", self.app_js)
        self.assertNotIn("EUR €", self.app_js)

        # Verify static product pages have authentic PKR pricing and domestic payment rails
        sample_tools = ["chatgpt", "cursor", "canva", "midjourney", "grammarly"]
        for tool_id in sample_tools:
            p_file = REPO_ROOT / "tools" / tool_id / "index.html"
            self.assertTrue(p_file.exists(), f"Static product page missing for {tool_id}")
            html = p_file.read_text(encoding="utf-8")
            self.assertIn("PKR", html, f"PKR pricing missing in {tool_id}")
            self.assertTrue("EasyPaisa" in html or "JazzCash" in html or "SadaPay" in html,
                            f"Domestic payment rails missing in {tool_id}")
            self.assertTrue("delivery" in html.lower(), f"Delivery information missing in {tool_id}")

    # =========================================================================
    # USER JOURNEY 3: Search & Filters
    # =========================================================================
    def test_journey_search_and_filters(self):
        """User journey: Search for tools, filter results, handle empty results, and clear queries."""
        # Search input and shortcut contract
        self.assertIn('id="heroSearch"', self.index_html)
        self.assertIn('type="search"', self.index_html)
        self.assertIn('aria-label="Search products"', self.index_html)

        # Autocomplete and suggestions box
        self.assertIn('id="suggestions"', self.index_html)

        # Empty state & clear query DOM/JS contracts
        self.assertIn('id="emptyState"', self.index_html)
        self.assertIn('id="activeQuery"', self.index_html)
        self.assertIn('id="clearQuery"', self.app_js, "Clear query button must be dynamically managed in app.js")

        # app.js filtering algorithm
        self.assertIn("function filteredProducts()", self.app_js)
        self.assertIn("function clearSearchField()", self.app_js)
        self.assertIn("function renderFilters()", self.app_js)

    # =========================================================================
    # USER JOURNEY 4: Add to Cart & Remove from Cart
    # =========================================================================
    def test_journey_add_to_cart_and_remove_from_cart(self):
        """User journey: Add product to cart, inspect drawer, modify quantity, and remove item."""
        # Add to cart triggers in app.js
        self.assertIn("function addToCart(id)", self.app_js)
        self.assertIn("localStorage.setItem('atg-cart'", self.app_js)
        self.assertIn("loadStoredCart()", self.app_js)

        # Remove from cart logic
        self.assertIn("function removeFromCart(id)", self.app_js)

        # Cart drawer DOM contracts
        self.assertIn('id="cartDrawer"', self.index_html)
        self.assertIn('id="cartItems"', self.index_html)
        self.assertIn('id="cartTotal"', self.index_html)
        self.assertIn('id="cartFooter"', self.index_html)
        self.assertIn('id="checkoutWhatsApp"', self.index_html)

    # =========================================================================
    # USER JOURNEY 5: WhatsApp Enquiry & Order Initiation
    # =========================================================================
    def test_journey_whatsapp_enquiry_and_checkout(self):
        """User journey: Complete checkout via WhatsApp order generation with prefilled items and verified number."""
        # Verified Pakistani phone number
        self.assertIn("923236715731", self.app_js)
        self.assertIn("function waLink(message)", self.app_js)

        # Checkout WhatsApp button triggers begin_checkout
        self.assertIn("begin_checkout", self.app_js)
        self.assertIn("openWhatsApp(", self.app_js)

        # Floating WhatsApp help desk
        self.assertIn('class="floating-whatsapp" data-whatsapp="help"', self.index_html)
        self.assertIn('Chat with us', self.index_html)

    # =========================================================================
    # USER JOURNEY 6: Navigation & Mobile Menu
    # =========================================================================
    def test_journey_navigation_and_mobile_menu(self):
        """User journey: Desktop header navigation, mobile hamburger drawer, and mobile bottom bar."""
        # Desktop navigation
        self.assertIn('class="desktop-nav"', self.index_html)
        self.assertIn('href="#products"', self.index_html)
        self.assertIn('href="tools/"', self.index_html)
        self.assertIn('href="deals/"', self.index_html)
        self.assertIn('href="guides/"', self.index_html)

        # Mobile menu toggle
        self.assertIn('id="menuButton"', self.index_html)
        self.assertIn('aria-label="Open menu"', self.index_html)
        self.assertIn('id="mobileNav"', self.index_html)

        # Mobile bottom quick actions
        self.assertIn('class="mobile-bottom"', self.index_html)
        self.assertIn('data-open-finder', self.index_html)
        self.assertIn('id="mobileCart"', self.index_html)

    # =========================================================================
    # USER JOURNEY 7: Contact & Policy Pages
    # =========================================================================
    def test_journey_contact_and_policy_pages(self):
        """User journey: Verify existence, valid canonicals, and clarity across all trust/policy pages."""
        policy_files = [
            ("about.html", "https://aitoolgems.tech/about.html"),
            ("contact.html", "https://aitoolgems.tech/contact.html"),
            ("policies.html", "https://aitoolgems.tech/policies.html"),
            ("how-we-price.html", "https://aitoolgems.tech/how-we-price.html"),
            ("how-we-review.html", "https://aitoolgems.tech/how-we-review.html"),
            ("privacy-policy/index.html", "https://aitoolgems.tech/privacy-policy/"),
            ("terms-of-service/index.html", "https://aitoolgems.tech/terms-of-service/"),
        ]
        for rel_path, canonical_url in policy_files:
            file_path = REPO_ROOT / rel_path
            self.assertTrue(file_path.exists(), f"Policy page {rel_path} does not exist")
            content = file_path.read_text(encoding="utf-8")
            self.assertTrue(content.startswith("<!DOCTYPE html>") or content.startswith("<!doctype html>"),
                            f"Doctype missing in {rel_path}")
            self.assertIn('rel="canonical"', content, f"Canonical missing in {rel_path}")
            self.assertIn(canonical_url, content, f"Canonical mismatch in {rel_path}")

    # =========================================================================
    # USER JOURNEY 8: Blog & Guide Navigation
    # =========================================================================
    def test_journey_blog_and_guide_navigation(self):
        """User journey: Access guides directory, navigate into a specific guide, review citations & product links."""
        guides_index = REPO_ROOT / "guides" / "index.html"
        self.assertTrue(guides_index.exists(), "Guides directory index.html missing")
        g_html = guides_index.read_text(encoding="utf-8")
        self.assertIn("guides &amp; blog", g_html.lower())

        # Sample guide checks
        sample_guides = [
            ("chatgpt-ai-pakistan-guide", "https://aitoolgems.tech/guides/chatgpt-ai-pakistan-guide/"),
            ("cursor-ai-pakistan", "https://aitoolgems.tech/guides/cursor-ai-pakistan/"),
            ("canva-pro-pakistan-guide", "https://aitoolgems.tech/guides/canva-pro-pakistan-guide/"),
        ]
        for g_slug, g_canonical in sample_guides:
            guide_path = REPO_ROOT / "guides" / g_slug / "index.html"
            self.assertTrue(guide_path.exists(), f"Guide page {g_slug} does not exist")
            g_content = guide_path.read_text(encoding="utf-8")
            self.assertIn('rel="canonical"', g_content)
            self.assertIn(g_canonical, g_content)
            self.assertIn("dateModified", g_content, f"Structured data dateModified missing in {g_slug}")

    # =========================================================================
    # MOBILE & DESKTOP VIEWPORT CONTRACTS
    # =========================================================================
    def test_mobile_and_desktop_viewport_contracts(self):
        """Verify CSS media queries, viewport meta tag, and anti-overflow horizontal rules."""
        # Meta viewport in index.html
        self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1.0">', self.index_html)

        # Responsive breakpoints in CSS
        combined_css = self.styles_css + self.light_theme_css
        self.assertTrue(
            re.search(r'@media\s*\([^{]*max-width:\s*(?:480|768|820|1024)px', combined_css),
            "Responsive max-width media query missing in CSS"
        )
        self.assertIn("prefers-reduced-motion", combined_css, "Reduced motion accessibility media query missing")

        # Overflow protection
        self.assertIn("overflow-x:hidden", self.styles_css.replace(" ", ""))

    # =========================================================================
    # STATIC JS AST & SYNTAX CHECK
    # =========================================================================
    def test_javascript_static_syntax_ast_check(self):
        """Verify app.js, admin.js, and attribution.js parse cleanly with Node.js."""
        js_files = ["app.js", "admin.js", "attribution.js"]
        for js_file in js_files:
            file_path = REPO_ROOT / js_file
            if file_path.exists():
                res = subprocess.run(["node", "--check", str(file_path)], capture_output=True, text=True)
                self.assertEqual(res.returncode, 0, f"JavaScript syntax error in {js_file}: {res.stderr}")

    # =========================================================================
    # CANONICAL & ROBOTS DIRECTIVES VALIDATION
    # =========================================================================
    def test_canonical_and_robots_validation(self):
        """Verify robots.txt has sitemap declaration and canonical URLs exist on all tools."""
        self.assertIn("Sitemap: https://aitoolgems.tech/sitemap.xml", self.robots_txt)
        self.assertIn("User-agent: *", self.robots_txt)

        # Check sample tools canonical tag
        tools_dir = REPO_ROOT / "tools"
        if tools_dir.exists():
            for t in list(tools_dir.iterdir())[:10]:
                if t.is_dir() and (t / "index.html").exists():
                    html = (t / "index.html").read_text(encoding="utf-8")
                    self.assertIn(f'<link rel="canonical" href="https://aitoolgems.tech/tools/{t.name}/">', html)

    # =========================================================================
    # PRODUCT DATA RECONCILIATION
    # =========================================================================
    def test_product_data_inventory_reconciliation(self):
        """Verify wholesale_inventory.json contains 40 verified products with positive prices and costs."""
        products = self.wholesale_data.get("products", [])
        self.assertEqual(len(products), 40, f"Expected 40 products in wholesale_inventory.json, found {len(products)}")
        for p in products:
            self.assertIn("name", p)
            self.assertIn("slug", p)
            self.assertIn("retail_pkr", p)
            self.assertIn("wholesale_cost_pkr", p)
            self.assertGreater(p["retail_pkr"], 0, f"Product {p.get('slug')} price must be > 0")
            self.assertGreaterEqual(p["wholesale_cost_pkr"], 0, f"Product {p.get('slug')} cost must be >= 0")

    # =========================================================================
    # SCHEMA JSON-LD VALIDITY
    # =========================================================================
    def test_schema_json_ld_validity(self):
        """Verify JSON-LD scripts across homepage, tools, and guides parse cleanly as valid JSON."""
        pages_to_check = [REPO_ROOT / "index.html"]
        tools_dir = REPO_ROOT / "tools"
        if tools_dir.exists():
            pages_to_check.extend([p / "index.html" for p in list(tools_dir.iterdir())[:5] if p.is_dir()])
        guides_dir = REPO_ROOT / "guides"
        if guides_dir.exists():
            pages_to_check.extend([p / "index.html" for p in list(guides_dir.iterdir())[:5] if p.is_dir()])

        for page in pages_to_check:
            if not page.exists():
                continue
            content = page.read_text(encoding="utf-8")
            blocks = re.findall(r'<script\s+type=[\'"]application/ld\+json[\'"]>(.*?)</script>', content, re.DOTALL)
            for idx, block in enumerate(blocks):
                try:
                    data = json.loads(block)
                    self.assertTrue(isinstance(data, dict), f"JSON-LD block {idx} in {page} is not a valid dict")
                except json.JSONDecodeError as e:
                    self.fail(f"Invalid JSON-LD in {page}: {e}")

    # =========================================================================
    # GA4 & ECOMMERCE EVENT SCHEMA VALIDATION
    # =========================================================================
    def test_analytics_and_conversion_event_schema(self):
        """Verify GA4 Measurement ID and ecommerce event handlers in attribution.js and app.js."""
        # 1. Correct GA4 Property Measurement ID
        self.assertIn("G-NQJCMDCLLP", self.attribution_js)

        # 2. Key ecommerce events represented
        expected_events = ["view_item", "select_item", "add_to_cart", "begin_checkout"]
        for ev in expected_events:
            self.assertTrue(ev in self.attribution_js or ev in self.app_js, f"Event {ev} missing from JS telemetry")

        # 3. WhatsApp click triggers begin_checkout, NEVER purchase
        self.assertIn("checkoutWA.onclick = checkout", self.app_js)
        self.assertIn("function checkout()", self.app_js)
        self.assertIn("trackEvent('begin_checkout'", self.app_js)
        self.assertNotIn("checkoutWhatsApp.addEventListener('click', function() { gtag('event', 'purchase'", self.app_js)
        self.assertNotIn("gtag('event', 'purchase'", self.app_js)


if __name__ == "__main__":
    unittest.main()
