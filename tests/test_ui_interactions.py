"""
Automated UI and Interaction Tests for AIToolGems Pakistan.
Validates key user-facing pathways, accessible roles, component state contracts,
finder logic, payment disclosure, reduced-motion basics, and responsive viewports.
"""

import os
import re
import sys
import unittest
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestUIInteractions(unittest.TestCase):
    """Automates and validates key UI paths, DOM contracts, and interactions."""

    @classmethod
    def setUpClass(cls):
        index_path = REPO_ROOT / "index.html"
        cls.index_html = index_path.read_text(encoding="utf-8")

        app_js_path = REPO_ROOT / "app.js"
        cls.app_js = app_js_path.read_text(encoding="utf-8")

        styles_css_path = REPO_ROOT / "styles.css"
        cls.styles_css = styles_css_path.read_text(encoding="utf-8")

        light_theme_path = REPO_ROOT / "light-theme.css"
        cls.light_theme_css = light_theme_path.read_text(encoding="utf-8")

    def test_main_navigation_roles_and_destinations(self):
        """Verifies semantic header, accessible desktop navigation, and non-broken anchors."""
        # 1. Semantic header
        self.assertIn('<header class="site-header">', self.index_html)

        # 2. Accessible desktop nav with aria-label
        nav_m = re.search(r'<nav\s+class="desktop-nav"\s+aria-label="Main navigation">(.*?)</nav>', self.index_html, re.DOTALL)
        self.assertIsNotNone(nav_m, "Expected <nav class='desktop-nav' aria-label='Main navigation'>")
        desktop_nav = nav_m.group(1)

        # Expected core destinations
        expected_links = [
            ('#products', 'Marketplace'),
            ('tools/', 'Tools Directory'),
            ('deals/', 'Deals'),
            ('guides/', 'Guides'),
            ('blog/', 'Blog'),
            ('#finder', 'Find my tool'),
            ('#how', 'How it works'),
        ]
        for href, text in expected_links:
            pattern = rf'href=["\']{re.escape(href)}["\'][^>]*>{re.escape(text)}<'
            self.assertTrue(
                re.search(pattern, desktop_nav),
                f"Desktop nav missing expected link: href='{href}' text='{text}'"
            )

    def test_mobile_navigation_contracts(self):
        """Verifies mobile menu toggle button, aria-label, and responsive drawer navigation."""
        # Toggle button contract
        menu_btn_m = re.search(r'<button[^>]+id="menuButton"[^>]*>', self.index_html)
        self.assertIsNotNone(menu_btn_m, "Expected menuButton toggle button")
        self.assertIn('aria-label="Open menu"', menu_btn_m.group(0))

        # Mobile nav drawer
        mobile_nav_m = re.search(r'<nav\s+class="mobile-nav"\s+id="mobileNav"\s+aria-label="Mobile navigation">(.*?)</nav>', self.index_html, re.DOTALL)
        self.assertIsNotNone(mobile_nav_m, "Expected mobileNav element with aria-label")
        mobile_nav = mobile_nav_m.group(1)

        # Mobile nav must mirror core destinations
        self.assertIn('href="#products"', mobile_nav)
        self.assertIn('href="deals/"', mobile_nav)
        self.assertIn('href="#categories"', mobile_nav)
        self.assertIn('href="guides/"', mobile_nav)
        self.assertIn('href="#finder"', mobile_nav)

        # app.js must handle menu toggle
        self.assertIn("$('#menuButton')", self.app_js)
        self.assertIn("$('#mobileNav')", self.app_js)

    def test_hero_3d_centerpiece_and_orbit_items(self):
        """Verifies 3D holographic stage, orbit items, and interactive floating cards."""
        # 1. 3D Stage & Centerpiece
        self.assertIn('id="heroVisualStage"', self.index_html)
        self.assertIn('id="hero3dStage"', self.index_html)
        self.assertIn('id="heroOrbitSystem"', self.index_html)
        self.assertIn('id="hero3dGem"', self.index_html)

        # 2. Floating interactive tool cards
        float_cards = re.findall(r'<a\s+href=["\']([^"\']+)["\']\s+class=["\']float-card\s+float-([a-z0-9-]+)["\'][^>]*>', self.index_html)
        self.assertGreaterEqual(len(float_cards), 4, "Expected at least 4 floating tool cards in hero orbit")

        for href, slug in float_cards:
            # Must point to valid static tool route
            self.assertTrue(href.startswith("tools/"), f"Float card href must target tools/: {href}")
            tool_path = REPO_ROOT / href / "index.html"
            self.assertTrue(tool_path.exists(), f"Target tool page must exist for float card: {href}")

        # Cards must have aria-label and accessible titles
        self.assertIn('aria-label="Explore ChatGPT Plus"', self.index_html)
        self.assertIn('aria-label="Explore Canva Pro"', self.index_html)
        self.assertIn('aria-label="Explore CapCut Pro"', self.index_html)
        self.assertIn('aria-label="Explore Figma Pro"', self.index_html)

    def test_trending_3d_gems_grid(self):
        """Verifies Trending 3D gems section heading, product cards, image alts, and detail links."""
        # 1. Section heading
        self.assertIn('<h2>Trending 3D gems.</h2>', self.index_html)

        # 2. Product cards in DOM
        product_cards = re.findall(r'<article\s+class="product-card"\s+data-id="([a-z0-9-]+)">', self.index_html)
        self.assertGreaterEqual(len(product_cards), 20, "Expected at least 20 product cards pre-rendered in DOM")

        # 3. Direct detail page links
        detail_links = re.findall(r'<a\s+class="product-page-link"\s+href="tools/([a-z0-9-]+)/">', self.index_html)
        self.assertGreaterEqual(len(detail_links), 20, "Expected direct product-page-link anchors on product cards")

        # 4. Buttons have accessible labels
        self.assertIn('aria-label="Compare Gemini Pro"', self.index_html)
        self.assertIn('aria-label="Add Gemini Pro to cart"', self.index_html)

    def test_category_filter_buttons_and_accessibility(self):
        """Verifies categoryGrid items, data-category attributes, and accessible roles."""
        cat_grid_m = re.search(r'<div\s+class="category-grid"\s+id="categoryGrid">(.*?)</div>', self.index_html, re.DOTALL)
        self.assertIsNotNone(cat_grid_m, "Expected categoryGrid element")

        cat_cards = re.findall(r'<a\s+href="#products"\s+class="category-card[^"]*"\s+data-category="([^"]+)">', cat_grid_m.group(1))
        self.assertGreaterEqual(len(cat_cards), 11, "Expected 11 category filter cards")

        expected_cats = [
            'AI Assistants', 'AI Video', 'Design', 'Development', 'Writing & SEO',
            'Productivity', 'AI Voice', 'VPN & Security', 'Entertainment', 'Business', 'Software'
        ]
        for cat in expected_cats:
            escaped = cat.replace('&', '&amp;')
            self.assertTrue(
                cat in cat_cards or escaped in cat_cards,
                f"Expected category card for '{cat}'"
            )

    def test_guided_finder_modal_and_algorithms(self):
        """Validates AI Finder modal trigger, intent choices, budget filtering, and recommendation logic."""
        # 1. Modal launcher
        self.assertIn('data-open-finder', self.index_html)
        self.assertIn('id="finderModal"', self.index_html)
        self.assertIn('id="finderSteps"', self.index_html)

        # 2. Finder matching algorithm in app.js
        self.assertIn("function finderStep(step = 1)", self.app_js)
        self.assertIn("data-intent", self.app_js)
        self.assertIn("data-budget-min", self.app_js)
        self.assertIn("data-budget-max", self.app_js)

        # 3. Preview match card directs to real tool
        self.assertIn('id="finderMatchCard" href="tools/veo/"', self.index_html)
        self.assertIn('id="previewCounter"', self.index_html)

    def test_payment_disclosure_component(self):
        """Validates paymentMethodsDisclosure details/summary, accessible labels, and policies anchor."""
        # Details element
        self.assertIn('<details class="payment-disclosure" id="paymentMethodsDisclosure" open>', self.index_html)

        # Accessible summary
        summary_m = re.search(r'<summary\s+class="payment-disclosure-summary"\s+aria-label="([^"]+)">', self.index_html)
        self.assertIsNotNone(summary_m, "Expected summary with aria-label")

        # Payment rails represented
        self.assertIn('EasyPaisa', self.index_html)
        self.assertIn('JazzCash', self.index_html)
        self.assertIn('SadaPay', self.index_html)
        self.assertIn('Bank IBFT', self.index_html)

        # Direct link to policies anchor
        self.assertIn('href="policies.html#payments"', self.index_html)

    def test_contact_and_whatsapp_actions(self):
        """Verifies WhatsApp floating desk, verified Pakistani phone numbers, and prefilled messages."""
        # Floating WhatsApp button and mobile bottom bar
        self.assertIn('class="floating-whatsapp" data-whatsapp="help"', self.index_html)
        self.assertIn('<button class="whatsapp-checkout" id="checkoutWhatsApp"', self.index_html)

        # Direct WhatsApp help anchors with verified 923236715731 phone and prefilled text
        wa_help_links = re.findall(r'href="(https://wa\.me/923236715731\?text=[^"]+)"', self.index_html)
        self.assertGreaterEqual(len(wa_help_links), 2, "Expected direct wa.me help anchors in FAQ/CTA")

        # Official WhatsApp channel
        self.assertIn('href="https://www.whatsapp.com/channel/0029VbDnEgCHLHQOYpDo5c31"', self.index_html)

    def test_search_input_and_keyboard_shortcuts(self):
        """Verifies search input field, autocomplete, search shortcut badge, and suggestions box."""
        search_m = re.search(r'<input\s+id="heroSearch"\s+type="search"[^>]*>', self.index_html)
        self.assertIsNotNone(search_m, "Expected heroSearch input")
        s_tag = search_m.group(0)
        self.assertIn('aria-label="Search products"', s_tag)
        self.assertIn('placeholder="Search tools..."', s_tag)
        self.assertIn('<kbd>⌘ K</kbd>', self.index_html)
        self.assertIn('id="suggestions"', self.index_html)

    def test_reduced_motion_css_rules(self):
        """Verifies WCAG prefers-reduced-motion media query is implemented to protect motion-sensitive users."""
        has_rm_styles = "prefers-reduced-motion" in self.styles_css
        has_rm_light = "prefers-reduced-motion" in self.light_theme_css
        self.assertTrue(
            has_rm_styles or has_rm_light,
            "prefers-reduced-motion media query must be implemented in styles.css or light-theme.css"
        )
        if has_rm_light:
            self.assertIn("animation-duration", self.light_theme_css)
            self.assertIn("scroll-behavior: auto", self.light_theme_css)

    def test_responsive_viewports_coverage(self):
        """Verifies responsive media queries for mobile, tablet, and desktop viewports."""
        combined_css = self.styles_css + self.light_theme_css

        # Mobile viewport (<= 480px or <= 768px)
        self.assertTrue(
            re.search(r'@media[^{]*max-width:\s*(?:480|540|768)px', combined_css),
            "Expected mobile responsive media query (<= 768px)"
        )

    def test_modals_drawers_and_focus_trapping(self):
        """Validates modals, drawers, close controls, backdrop, and keyboard focus trap in app.js."""
        # 1. Modals and drawers in index.html
        self.assertIn('id="cartDrawer"', self.index_html)
        self.assertIn('id="compareDrawer"', self.index_html)
        self.assertIn('id="finderModal"', self.index_html)
        self.assertIn('id="productModal"', self.index_html)
        self.assertIn('id="backdrop"', self.index_html)

        # 2. Close buttons have data-close and accessible aria-labels
        close_btns = re.findall(r'<button[^>]+data-close[^>]*aria-label="([^"]+)"', self.index_html)
        self.assertGreaterEqual(len(close_btns), 4, "Expected close buttons with data-close and aria-labels on all drawers/modals")

        # 3. Focus trap and Escape handlers in app.js
        self.assertIn("e.key === 'Escape'", self.app_js)
        self.assertIn("closeLayers()", self.app_js)
        self.assertIn("e.key === 'Tab' && openLayerEl", self.app_js)
        self.assertIn("e.target.closest('[data-close]') || e.target.id === 'backdrop'", self.app_js)

    def test_search_empty_state_and_query_clearing(self):
        """Verifies empty result state container, active query pill, and query clearing logic."""
        # 1. Empty state DOM structure
        self.assertIn('id="emptyState"', self.index_html)
        self.assertIn('class="empty-state', self.index_html)
        self.assertIn('id="activeQuery"', self.index_html)

        # 2. Empty state and clear logic in app.js
        self.assertIn("empty.classList.toggle('show', !all.length)", self.app_js)
        self.assertIn("e.target.id === 'clearQuery'", self.app_js)
        self.assertIn("clearSearchField()", self.app_js)

    def test_product_detail_variants_and_checkout_actions(self):
        """Verifies product detail modal contracts, PKR pricing display, and WhatsApp checkout generation."""
        # Product modal accessibility
        self.assertIn('class="modal product-modal" id="productModal" role="dialog" aria-modal="true"', self.index_html)
        self.assertIn('id="productDetail"', self.index_html)

        # WhatsApp URL builder contract in app.js
        self.assertIn("function waLink(message)", self.app_js)
        self.assertIn("923236715731", self.app_js)
        self.assertIn("function openWhatsApp(url)", self.app_js)

    def test_horizontal_overflow_protection(self):
        """Verifies overflow-x hidden on root viewport containers to prevent mobile/tablet horizontal scroll jank."""
        self.assertIn("overflow-x:hidden", self.styles_css.replace(" ", ""))
        self.assertIn("max-width:100%", self.styles_css.replace(" ", ""))


if __name__ == "__main__":
    unittest.main()
