"""
Regression and Integrity Tests for AIToolGems Pakistan.
Enforces zero-cost policy, no fabricated order popups, no client-side secret exposure,
valid tool page routes, and sitemap consistency.
"""

import os
import re
import unittest
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestIntegrityAndRegressions(unittest.TestCase):

    def test_no_fabricated_order_toast_in_app_js(self):
        """Phase 2: Confirms initLiveOrderToast, live-order-toast, and hardcoded order arrays are absent."""
        app_js_path = os.path.join(REPO_ROOT, 'app.js')
        with open(app_js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertNotIn('initLiveOrderToast', content, "initLiveOrderToast should be removed from app.js")
        self.assertNotIn('live-order-toast', content, "live-order-toast class should not exist in app.js")
        self.assertNotIn('⚡ Verified EasyPaisa', content, "Fake '⚡ Verified EasyPaisa' order ticker must be absent")
        self.assertNotIn('Hamza K.', content, "Fabricated customer order names must not be present in app.js")

    def test_no_exposed_api_secrets_in_client_js(self):
        """Phase 3 & Security: Ensures no private API keys or tokens are in frontend scripts."""
        client_files = [
            'app.js',
            'attribution.js',
            'admin.js',
            os.path.join('chatbot', 'widget.js')
        ]
        secret_patterns = [
            r'sk-[a-zA-Z0-9]{20,}',       # OpenAI secret keys
            r'ghp_[a-zA-Z0-9]{20,}',      # GitHub personal access tokens
            r'AIzaSy[a-zA-Z0-9_-]{33}',   # Google API keys
            r'xox[baprs]-[a-zA-Z0-9-]+',  # Slack tokens
        ]
        for rel_path in client_files:
            full_path = os.path.join(REPO_ROOT, rel_path)
            if not os.path.exists(full_path):
                continue
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            for pattern in secret_patterns:
                matches = re.findall(pattern, content)
                self.assertEqual(len(matches), 0, f"Found potential secret match {pattern} in {rel_path}")

    def test_all_catalog_tools_have_valid_routes(self):
        """Phase 4: Confirms all static tools exist and other catalog tools route safely to product modal."""
        app_js_path = os.path.join(REPO_ROOT, 'app.js')
        with open(app_js_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract STATIC_TOOL_PAGES
        match = re.search(r"STATIC_TOOL_PAGES\s*=\s*new\s*Set\(\[\s*([^\]]+)\]\)", content)
        self.assertIsNotNone(match, "STATIC_TOOL_PAGES Set must be defined in app.js")
        static_ids = [s.strip().strip("'\"") for s in match.group(1).split(',') if s.strip()]

        for tool_id in static_ids:
            tool_page = os.path.join(REPO_ROOT, 'tools', tool_id, 'index.html')
            self.assertTrue(
                os.path.exists(tool_page),
                f"Static tool route for '{tool_id}' must exist at tools/{tool_id}/index.html"
            )

        # All products in catalog must either be in STATIC_TOOL_PAGES or route to #productModal
        all_ids = re.findall(r"id:'([a-z0-9-]+)',name:", content)
        self.assertGreater(len(all_ids), 20, "Catalog should have 20+ tools")
        for tool_id in all_ids:
            if tool_id not in static_ids:
                # Must be configured to trigger modal instead of broken static link
                self.assertNotIn(f'href="tools/{tool_id}/"', content, f"Tool '{tool_id}' has no static page so must not link to tools/{tool_id}/")

    def test_sitemap_contains_all_indexable_pages(self):
        """Phase 5: Confirms sitemap.xml exists, parses cleanly, and contains all canonical pages."""
        sitemap_path = os.path.join(REPO_ROOT, 'sitemap.xml')
        self.assertTrue(os.path.exists(sitemap_path), "sitemap.xml must exist in repo root")

        tree = ET.parse(sitemap_path)
        root = tree.getroot()
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [elem.text for elem in root.findall('ns:url/ns:loc', namespace)]

        self.assertGreater(len(urls), 50, "Sitemap should contain all 50+ indexable URLs")
        self.assertIn('https://aitoolgems.tech/', urls)
        self.assertIn('https://aitoolgems.tech/tools/', urls)
        self.assertIn('https://aitoolgems.tech/guides/', urls)
        self.assertIn('https://aitoolgems.tech/prices/', urls)

        # Noindex pages should NOT be in sitemap
        for url in urls:
            self.assertNotIn('admin.html', url, "admin.html must not be in sitemap")
            self.assertNotIn('404.html', url, "404.html must not be in sitemap")
            self.assertNotIn('gsc_daily_checklist.html', url, "gsc_daily_checklist must not be in sitemap")

    def test_adsense_single_publisher_id(self):
        """Phase 6: Confirms Google AdSense publisher ID is consistent and not duplicated in ads.txt."""
        ads_txt_path = os.path.join(REPO_ROOT, 'ads.txt')
        with open(ads_txt_path, 'r', encoding='utf-8') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]

        self.assertEqual(len(lines), 1, "ads.txt should contain exactly one verified entry")
        self.assertTrue(lines[0].startswith("google.com, pub-5286528878404514, DIRECT, f08c47fec0942fa0"))

    def test_phase1_breadcrumbs_and_contrast_integrity(self):
        """Phase 1: Verifies all static tool pages have clickable breadcrumbs and light-theme contrast overrides."""
        # 1. Breadcrumbs check across all 32 tools
        tools_dir = os.path.join(REPO_ROOT, 'tools')
        subdirs = [d for d in os.listdir(tools_dir) if os.path.isdir(os.path.join(tools_dir, d))]
        self.assertEqual(len(subdirs), 32, "Expected exactly 32 tool directories in tools/")
        for d in subdirs:

            fp = os.path.join(tools_dir, d, 'index.html')
            self.assertTrue(os.path.exists(fp), f"Expected {fp} to exist")
            with open(fp, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertIn('<a href="../../">Home</a>', content, f"{d} breadcrumbs must contain clickable link to Home")
            self.assertIn('<a href="../../tools/">AI tools</a>', content, f"{d} breadcrumbs must contain link to AI tools directory")

        # 2. Contrast overrides check in light-theme.css
        light_theme_path = os.path.join(REPO_ROOT, 'light-theme.css')
        with open(light_theme_path, 'r', encoding='utf-8') as f:
            lt_content = f.read()
        self.assertIn('.float-card span', lt_content, "light-theme.css must override .float-card span")
        self.assertIn('.stack-item span', lt_content, "light-theme.css must override .stack-item span")
        self.assertIn('.finder-preview > p', lt_content, "light-theme.css must override .finder-preview > p")


if __name__ == '__main__':
    unittest.main()

