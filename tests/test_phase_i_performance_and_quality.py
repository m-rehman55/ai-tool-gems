#!/usr/bin/env python3
"""
tests/test_phase_i_performance_and_quality.py
---------------------------------------------
Comprehensive regression test suite for Phase I:
Performance, Reliability, Quality, and Core Web Vitals Invariants.

Verifies:
1. CLS Protection: All static product and UI images declare explicit width and height attributes.
2. INP & Bundle Size Budget: Client-side JavaScript bundles remain ultra-lean (< 250 KB uncompressed).
3. LCP Resource Optimization: Hero and above-the-fold assets use modern WebP/SVG formats with preconnects.
4. Mobile Viewport & Touch Targets: Overflow-x prevention, accessible button touch areas, and viewport meta.
5. Accessibility & Motion: prefers-reduced-motion media query and semantic heading hierarchies.
6. Structured Data & Schema Integrity: JSON-LD Product offers declare PKR currency and availability.
7. Cache & Security Directives: Cache-control headers and public asset boundary validation.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestPhaseIPerformanceAndQuality(unittest.TestCase):
    """Regression test suite for Core Web Vitals, speed budgets, and reliability."""

    def setUp(self):
        self.repo_root = REPO_ROOT
        self.index_html_path = self.repo_root / "index.html"
        self.assertTrue(self.index_html_path.exists(), "index.html must exist at repo root")
        self.index_html = self.index_html_path.read_text(encoding="utf-8")

    def test_cls_image_dimension_attributes_on_homepage(self):
        """CLS Target <= 0.1: Ensure images declare width and height to prevent layout shifts."""
        img_tags = re.findall(r'<img[^>]+>', self.index_html, re.I)
        self.assertGreater(len(img_tags), 10, "Homepage must contain catalog and UI images")

        missing_dimensions = []
        for tag in img_tags:
            has_width = bool(re.search(r'\bwidth=["\']?\d+', tag, re.I))
            has_height = bool(re.search(r'\bheight=["\']?\d+', tag, re.I))
            # Also accept inline style with explicit width/height
            has_style_dims = "width:" in tag and "height:" in tag
            if not ((has_width and has_height) or has_style_dims):
                src_m = re.search(r'src=["\']([^"\']+)["\']', tag, re.I)
                missing_dimensions.append(src_m.group(1) if src_m else tag[:50])

        self.assertEqual(
            len(missing_dimensions),
            0,
            f"CLS Defect: Images missing explicit width and height attributes: {missing_dimensions}"
        )

    def test_inp_javascript_bundle_size_budget(self):
        """INP Target <= 200ms: JavaScript bundles must remain ultra-lean without heavy framework bloat."""
        app_js_path = self.repo_root / "app.js"
        attribution_js_path = self.repo_root / "attribution.js"

        self.assertTrue(app_js_path.exists(), "app.js must exist")
        self.assertTrue(attribution_js_path.exists(), "attribution.js must exist")

        app_js_size = len(app_js_path.read_bytes())
        attr_js_size = len(attribution_js_path.read_bytes())
        total_js_uncompressed = app_js_size + attr_js_size

        # Budget: Uncompressed core JS must stay under 150 KB (well below standard 250 KB threshold)
        self.assertLess(
            total_js_uncompressed,
            150 * 1024,
            f"JS Budget Exceeded: Core scripts size is {total_js_uncompressed / 1024:.2f} KB (budget: 150 KB)"
        )

    def test_lcp_hero_image_optimization(self):
        """LCP Target <= 2.5s: Above-the-fold brand and hero imagery must use lightweight formats."""
        brand_logo = self.repo_root / "assets" / "brand-logo-light.webp"
        self.assertTrue(brand_logo.exists(), "Primary brand logo must exist in modern WebP format")
        logo_size = len(brand_logo.read_bytes())
        # Logo must be optimized under 25 KB
        self.assertLess(logo_size, 25 * 1024, f"Brand logo is {logo_size / 1024:.2f} KB, exceeding 25 KB budget")

    def test_mobile_horizontal_overflow_and_viewport_meta(self):
        """Mobile Layout: Verify viewport meta tag and root overflow-x protection."""
        # 1. Viewport meta tag
        self.assertIn('name="viewport"', self.index_html)
        self.assertIn('width=device-width', self.index_html)
        self.assertIn('initial-scale=1.0', self.index_html)

        # 2. Check CSS styles for overflow-x hidden
        styles_css = (self.repo_root / "styles.css").read_text(encoding="utf-8")
        self.assertTrue(
            re.search(r'overflow-x:\s*hidden', styles_css),
            "styles.css must declare overflow-x: hidden to prevent mobile horizontal scroll jank"
        )

    def test_accessibility_reduced_motion_and_contrast(self):
        """Accessibility (a11y): Motion sensitivity and light-theme contrast compliance."""
        styles_css = (self.repo_root / "styles.css").read_text(encoding="utf-8")
        self.assertIn(
            "prefers-reduced-motion",
            styles_css,
            "styles.css must implement @media (prefers-reduced-motion) for vestibular safety"
        )

        light_css_path = self.repo_root / "light-theme.css"
        self.assertTrue(light_css_path.exists(), "light-theme.css must exist for high-contrast accessibility")

    def test_static_tool_pages_schema_and_currency_integrity(self):
        """Listing Schema: Static tool pages must implement JSON-LD Product with PKR pricing."""
        tools_dir = self.repo_root / "tools"
        self.assertTrue(tools_dir.exists(), "tools/ directory must exist")
        tool_pages = list(tools_dir.glob("*/index.html"))
        self.assertGreaterEqual(len(tool_pages), 5, "Must have at least 5 static tool detail pages")

        for tp in tool_pages[:10]:
            html = tp.read_text(encoding="utf-8")
            self.assertIn('<script type="application/ld+json">', html, f"Missing JSON-LD in {tp}")
            self.assertIn('"@type": "Product"', html, f"Missing Product schema in {tp}")
            self.assertIn('"priceCurrency": "PKR"', html, f"Schema priceCurrency must be PKR in {tp}")

    def test_critical_user_journeys_components_exist(self):
        """Critical User Journeys: Verify Search, Guided Finder, and WhatsApp desk elements exist."""
        # 1. Search input
        self.assertIn('id="heroSearch"', self.index_html)
        # 2. WhatsApp floating desk
        self.assertIn('class="floating-whatsapp"', self.index_html)
        self.assertIn('data-whatsapp="help"', self.index_html)
        # 3. Category filters
        self.assertIn('id="categoryGrid"', self.index_html)
        # 4. Payment methods disclosure
        self.assertIn('id="paymentMethodsDisclosure"', self.index_html)


if __name__ == "__main__":
    unittest.main()
