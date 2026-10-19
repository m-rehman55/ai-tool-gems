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

    def test_phase3_category_prerendering_and_anchor_integrity(self):
        """Phase 3: Confirms all 11 categories are pre-rendered, anchors resolve, and no href='#' placeholders exist."""
        index_path = os.path.join(REPO_ROOT, 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # 1. 11 categories pre-rendered
        expected_categories = [
            'AI Assistants', 'AI Video', 'Design', 'Development', 'Writing & SEO',
            'Productivity', 'AI Voice', 'VPN & Security', 'Entertainment', 'Business', 'Software'
        ]
        for cat in expected_categories:
            escaped_cat = cat.replace('&', '&amp;')
            self.assertTrue(
                f'data-category="{cat}"' in html or f'data-category="{escaped_cat}"' in html,
                f"Expected category {cat} pre-rendered in index.html"
            )

        # 2. Zero href="#" in index.html
        self.assertNotIn('href="#"', html, "index.html must not contain empty/placeholder href='#'")

        # 3. Finder match card links directly to canonical tool page
        self.assertIn('id="finderMatchCard" href="tools/veo/"', html, "finderMatchCard must link directly to tools/veo/")

        # 4. Guide TOC fragment anchors resolve to actual heading IDs
        guide_files = [
            'guides/ai-tools-price-pakistan/index.html',
            'guides/canva-vs-figma-pakistan/index.html',
            'guides/chatgpt-vs-gemini-pakistan/index.html'
        ]
        for gf in guide_files:
            gpath = os.path.join(REPO_ROOT, gf)
            with open(gpath, 'r', encoding='utf-8') as f:
                gcontent = f.read()
            toc_match = re.search(r'<nav class=["\']toc["\'][^>]*>(.*?)</nav>', gcontent, re.DOTALL)
            self.assertIsNotNone(toc_match, f"TOC missing in {gf}")
            toc_links = re.findall(r'href=["\']#([^"\']+)["\']', toc_match.group(1))
            self.assertTrue(len(toc_links) > 0, f"Expected TOC links in {gf}")
            for fragment in toc_links:
                self.assertTrue(
                    re.search(rf'id=["\']{re.escape(fragment)}["\']', gcontent),
                    f"TOC link #{fragment} in {gf} does not match any element ID"
                )

        # 5. app.js normalizes intent matching for singular and plural
        app_js_path = os.path.join(REPO_ROOT, 'app.js')
        with open(app_js_path, 'r', encoding='utf-8') as f:
            app_js = f.read()
        self.assertIn("targetIntent === 'image' && n.startsWith('image')", app_js, "app.js must normalize image/images intent")

    def test_phase4_payment_transparency_and_policy_integrity(self):
        """Phase 4: Verifies payment classifications, truthful wording, policy fragment resolution, and security boundaries."""
        policies_path = os.path.join(REPO_ROOT, 'policies.html')
        with open(policies_path, 'r', encoding='utf-8') as f:
            policies_html = f.read()

        # 1. policies.html has dedicated id="payments" section
        self.assertIn('id="payments"', policies_html, "policies.html must contain a section with id='payments'")
        self.assertTrue(
            re.search(r'<section[^>]*id=["\']payments["\']', policies_html),
            "Expected <section> element with id='payments' in policies.html"
        )

        # 2. All 32 tool pages have links to policies.html#payments and the section exists
        tools_dir = os.path.join(REPO_ROOT, 'tools')
        tool_dirs = [d for d in os.listdir(tools_dir) if os.path.isdir(os.path.join(tools_dir, d))]
        self.assertEqual(len(tool_dirs), 32, "Expected 32 tool pages")
        for td in tool_dirs:
            tfile = os.path.join(tools_dir, td, 'index.html')
            with open(tfile, 'r', encoding='utf-8') as f:
                tcontent = f.read()
            self.assertIn('policies.html#payments', tcontent, f"{td}/index.html must link to policies.html#payments")

        # 3. Transparent 3-tier payment classification in policies.html
        self.assertIn('Verified &amp; Configured', policies_html, "policies.html must include 'Verified & Configured' classification")
        self.assertIn('Contact Owner / Inquiry-Only', policies_html, "policies.html must include 'Contact Owner / Inquiry-Only' classification")
        self.assertIn('Unsupported / Unavailable', policies_html, "policies.html must include 'Unsupported / Unavailable' classification")

        # 4. index.html payment disclosure component
        index_path = os.path.join(REPO_ROOT, 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            index_html = f.read()

        self.assertIn('id="paymentMethodsDisclosure"', index_html, "index.html must have paymentMethodsDisclosure details element")
        self.assertIn('href="policies.html#payments"', index_html, "index.html payment disclosure must link to policies.html#payments")

        # 5. Unsupported / exaggerated claims removed
        self.assertNotIn('100% Verified Local Payments', index_html, "100% Verified Local Payments claim must be removed from index.html")
        self.assertNotIn('Instant Guaranteed Activation', index_html, "Instant Guaranteed Activation claim must not be in index.html")
        self.assertNotIn('Instant 15-Minute WhatsApp Activation', index_html, "Instant 15-Minute WhatsApp Activation must not be in index.html")
        self.assertNotIn('Instant Dispatch', index_html, "Instant Dispatch must not be in index.html")
        self.assertNotIn('Instant Account Delivery', index_html, "Instant Account Delivery must not be in index.html")
        self.assertNotIn('2–15 Minute WhatsApp Activation', index_html, "2–15 Minute WhatsApp Activation must not be in index.html")
        self.assertNotIn('Fast 2 to 15 Minutes WhatsApp Activation', index_html, "Fast 2 to 15 Minutes WhatsApp Activation must not be in index.html")
        self.assertNotIn('immediate activation', index_html.lower(), "immediate activation must not be in index.html")
        self.assertNotIn('in 2 minutes', index_html.lower(), "in 2 minutes claim must not be in index.html")
        self.assertNotIn('in 3–5 minutes', index_html, "in 3–5 minutes claim must not be in index.html")
        self.assertNotIn('in 5 minutes', index_html.lower(), "in 5 minutes claim must not be in index.html")
        self.assertIn('activation after payment and availability confirmation', index_html.lower(), "Expected activation after payment confirmation wording in index.html")

        # 6. Contact protection: 03476242709 must not be published anywhere in any HTML file in the repository
        for root, dirs, files in os.walk(REPO_ROOT):
            if '.git' in root or 'node_modules' in root or '.gemini' in root:
                continue
            for f in files:
                if f.endswith('.html'):
                    fpath = os.path.join(root, f)
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as hf:
                        content = hf.read()
                    self.assertNotIn('03476242709', content, f"Found legacy number 03476242709 in {os.path.relpath(fpath, REPO_ROOT)}")

        # 7. No fake automated payment gateway scripts or credit card inputs
        self.assertNotIn('stripe.com/v3', index_html, "No Stripe checkout script should be injected")
        self.assertNotIn('<form id="card-element"', index_html, "No fake card element should be in index.html")
        self.assertNotIn('paypal.com/sdk/js', index_html, "No PayPal SDK script should be injected")

    def test_phase5_delivery_minute_claims_and_guide_tables(self):
        """Phase 5: Asserts unsupported delivery minute estimates are absent and truthful confirmation wording is present."""
        # 1. ChatGPT vs Gemini comparison table
        cg_path = os.path.join(REPO_ROOT, 'guides', 'chatgpt-vs-gemini-pakistan', 'index.html')
        with open(cg_path, 'r', encoding='utf-8') as f:
            cg_html = f.read()
        self.assertNotIn('15–30 minutes', cg_html, "15–30 minutes delivery estimate must not be in chatgpt-vs-gemini guide")
        self.assertNotIn('15-30 minutes', cg_html, "15-30 minutes delivery estimate must not be in chatgpt-vs-gemini guide")
        self.assertNotIn('10–20 minutes', cg_html, "10–20 minutes delivery estimate must not be in chatgpt-vs-gemini guide")
        self.assertNotIn('10-20 minutes', cg_html, "10-20 minutes delivery estimate must not be in chatgpt-vs-gemini guide")
        self.assertIn('Prompt delivery after payment confirmation', cg_html, "Prompt delivery confirmation required in chatgpt-vs-gemini table")

        # 2. Canva vs Figma comparison table
        cf_path = os.path.join(REPO_ROOT, 'guides', 'canva-vs-figma-pakistan', 'index.html')
        with open(cf_path, 'r', encoding='utf-8') as f:
            cf_html = f.read()
        self.assertNotIn('5–15 minutes', cf_html, "5–15 minutes delivery estimate must not be in canva-vs-figma guide")
        self.assertNotIn('5-15 minutes', cf_html, "5-15 minutes delivery estimate must not be in canva-vs-figma guide")
        self.assertNotIn('10–20 minutes', cf_html, "10–20 minutes delivery estimate must not be in canva-vs-figma guide")
        self.assertNotIn('10-20 minutes', cf_html, "10-20 minutes delivery estimate must not be in canva-vs-figma guide")
        self.assertIn('Prompt delivery after payment confirmation', cf_html, "Prompt delivery confirmation required in canva-vs-figma table")

        # 3. All-in-one Mega AI Portal tool page
        aio_path = os.path.join(REPO_ROOT, 'tools', 'allinone', 'index.html')
        with open(aio_path, 'r', encoding='utf-8') as f:
            aio_html = f.read()
        self.assertNotIn('2-minute activation', aio_html.lower(), "2-minute activation claim must not be in tools/allinone")
        self.assertNotIn('instant 2-minute', aio_html.lower(), "Instant 2-minute claim must not be in tools/allinone")
        self.assertIn('Prompt delivery after payment confirmation', aio_html, "Prompt delivery confirmation required in tools/allinone")

        # 4. app.js product catalog
        app_js_path = os.path.join(REPO_ROOT, 'app.js')
        with open(app_js_path, 'r', encoding='utf-8') as f:
            app_js = f.read()
        self.assertNotIn('Instant 2-minute activation', app_js, "Instant 2-minute activation must not be in app.js")
        self.assertNotIn("delivery:'2–5 min'", app_js.replace(' ', ''), "2–5 min delivery must not be in app.js")

        # 5. Site-wide reviewBody check across all tool pages and index.html
        for root, dirs, files in os.walk(REPO_ROOT):
            if '.git' in root or 'node_modules' in root or '.seo-cache' in root:
                continue
            for f in files:
                if f.endswith('.html'):
                    fpath = os.path.join(root, f)
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as hf:
                        content = hf.read()
                    self.assertNotIn('Fast 15-minute delivery', content, f"Found 'Fast 15-minute delivery' in {os.path.relpath(fpath, REPO_ROOT)}")
                    self.assertNotIn('Instant 2-minute activation', content, f"Found 'Instant 2-minute activation' in {os.path.relpath(fpath, REPO_ROOT)}")


if __name__ == '__main__':
    unittest.main()



