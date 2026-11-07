"""
Unit test suite validating catalogue accounting, structured-data metadata alignment,
and commercial boundary invariants across legacy assisted and directory-only profiles.
"""

import unittest
import os
import re
import xml.etree.ElementTree as ET

class TestCatalogueConsistency(unittest.TestCase):

    def setUp(self):
        self.root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.tools_dir = os.path.join(self.root_dir, "tools")
        self.index_html_path = os.path.join(self.root_dir, "index.html")
        self.tools_index_path = os.path.join(self.tools_dir, "index.html")
        self.sitemap_path = os.path.join(self.root_dir, "sitemap.xml")

        self.legacy_40_slugs = [
            'adobe', 'allinone', 'canva', 'capcut', 'chatgpt', 'claude', 'copilot', 'cursor',
            'deepseek', 'elevenlabs', 'figma', 'freepik', 'gamma', 'gemini', 'grammarly',
            'grok', 'heygen', 'kling', 'leonardo', 'linkedin', 'lovable', 'midjourney',
            'n8n', 'netflix', 'nordvpn', 'notion', 'office365', 'perplexity', 'quillbot',
            'replit', 'runway', 'semrush', 'spotify', 'suno', 'surfshark', 'tradingview',
            'turnitin', 'veo', 'windows', 'youtube'
        ]

        self.wave1_slugs = [
            'bolt-new', 'coursera-plus', 'descript', 'firecrawl', 'invideo-ai', 'make',
            'manus-ai', 'opus-clip', 'qwen', 'udemy-personal', 'v0', 'windsurf'
        ]

        self.wave2_slugs = [
            'ahrefs', 'chatprd', 'davinci-resolve', 'domo-ai', 'genspark', 'hailuo-ai',
            'higgsfield', 'morphic', 'notebooklm', 'quizlet', 'railway', 'skillshare', 'supabase'
        ]

    def test_homepage_metadata_reflects_pakistan_and_worldwide(self):
        """Verify homepage metadata includes Pakistan, PKR, and Worldwide positioning without unsupported USD claims."""
        with open(self.index_html_path, "r", encoding="utf-8") as f:
            html = f.read()

        m_title = re.search(r'<title>(.*?)</title>', html)
        self.assertTrue(m_title, "Homepage title missing")
        self.assertIn("Pakistan", m_title.group(1))
        self.assertIn("PKR", m_title.group(1))
        self.assertIn("Worldwide", m_title.group(1))
        self.assertNotIn("(USD)", m_title.group(1), "Homepage title must not claim direct USD pricing")

        m_desc = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html)
        self.assertTrue(m_desc, "Homepage meta description missing")
        self.assertIn("Pakistan", m_desc.group(1))
        self.assertIn("PKR", m_desc.group(1))
        self.assertNotIn("USD rates", m_desc.group(1), "Meta description must not claim verified USD rates")
        self.assertNotIn("USD prices", m_desc.group(1), "Meta description must not claim USD prices")

    def test_tools_index_metadata_free_from_outdated_count(self):
        """Verify tools/index.html Open Graph description does not state outdated 'all 20'."""
        with open(self.tools_index_path, "r", encoding="utf-8") as f:
            html = f.read()

        m_og_desc = re.search(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']', html)
        self.assertTrue(m_og_desc, "tools/index.html og:description missing")
        self.assertNotIn("all 20", m_og_desc.group(1).lower())

        m_tw_desc = re.search(r'<meta\s+name=["\']twitter:description["\']\s+content=["\'](.*?)["\']', html)
        self.assertTrue(m_tw_desc, "tools/index.html twitter:description missing")
        self.assertNotIn("all 20", m_tw_desc.group(1).lower())

    def test_tools_directory_metadata_distinguishes_assisted_vs_directory_models(self):
        """Ensure directory-wide metadata does not promise WhatsApp delivery for directory-only profiles."""
        with open(self.tools_index_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Meta description must distinguish 40 assisted vs 25 directory
        m_desc = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html)
        self.assertTrue(m_desc, "tools/index.html meta description missing")
        desc = m_desc.group(1)
        self.assertIn("65", desc)
        self.assertIn("40", desc)
        self.assertIn("25", desc)
        self.assertNotIn("Fast WhatsApp delivery via EasyPaisa", desc)

        # Open Graph & Twitter descriptions must match
        m_og_desc = re.search(r'<meta\s+property=["\']og:description["\']\s+content=["\'](.*?)["\']', html)
        self.assertTrue(m_og_desc)
        self.assertEqual(desc, m_og_desc.group(1))

        m_tw_desc = re.search(r'<meta\s+name=["\']twitter:description["\']\s+content=["\'](.*?)["\']', html)
        self.assertTrue(m_tw_desc)
        self.assertEqual(desc, m_tw_desc.group(1))

        # Check lead paragraph and quick summary in page body
        self.assertIn("65 verified AI tools", html)
        self.assertIn("25 directory reference", html)

        # Ensure all 40 legacy tools retain assisted WhatsApp order flow
        for slug in self.legacy_40_slugs:
            p = os.path.join(self.tools_dir, slug, "index.html")
            with open(p, "r", encoding="utf-8") as tool_f:
                tool_html = tool_f.read()
            self.assertTrue(
                bool(re.search(r'https://wa\.me/\d+', tool_html)),
                f"Assisted tool {slug} must preserve WhatsApp purchase flow"
            )

    def test_all_legacy_40_contain_standardized_warranty(self):
        """Assert all 40 legacy listings display the Assisted Access Replacement Warranty."""
        for slug in self.legacy_40_slugs:
            p = os.path.join(self.tools_dir, slug, "index.html")
            self.assertTrue(os.path.exists(p), f"Missing legacy tool file: {p}")
            with open(p, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertIn(
                "Assisted Access Replacement Warranty",
                content,
                f"Tool {slug} missing standardized Assisted Access Replacement Warranty disclosure"
            )

    def test_directory_tools_invariants_and_checkout_exclusion(self):
        """Assert directory profiles (Wave 1 & Wave 2) enforce directory-only badge and exclude purchase checkout."""
        for slug in self.wave1_slugs + self.wave2_slugs:
            p = os.path.join(self.tools_dir, slug, "index.html")
            self.assertTrue(os.path.exists(p), f"Missing directory tool file: {p}")
            with open(p, "r", encoding="utf-8") as f:
                content = f.read()

            # Must have directory indicator
            has_badge = bool(re.search(r'directory-badge|DIRECTORY REFERENCE ONLY|DIRECTORY ONLY|Directory Listing|Official Vendor \(Directory\)', content, re.I))
            self.assertTrue(has_badge, f"Directory profile {slug} missing directory indicator")

            # Must not have fake order CTA or simulated PKR checkout
            self.assertNotIn('data-step-action="whatsapp"', content)
            self.assertNotIn('Direct Concierge Checkout', content)

    def test_wave2_tools_quarantined_noindex(self):
        """Assert all 13 Wave 2 tools on main have meta robots noindex, follow."""
        for slug in self.wave2_slugs:
            p = os.path.join(self.tools_dir, slug, "index.html")
            with open(p, "r", encoding="utf-8") as f:
                content = f.read()
            m_robots = re.search(r'<meta\s+name=["\']robots["\']\s+content=["\']([^"\']+)["\']', content)
            self.assertTrue(m_robots, f"Missing robots tag in Wave 2 profile {slug}")
            self.assertEqual(m_robots.group(1).strip(), "noindex, follow")

    def test_sitemap_accounting_and_exclusion_invariants(self):
        """Verify sitemap contains exactly 52 tool URLs and excludes Wave 2 and Japan URLs."""
        tree = ET.parse(self.sitemap_path)
        root = tree.getroot()
        urls = [elem.text for elem in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]

        tool_urls = [u for u in urls if '/tools/' in u and u != 'https://aitoolgems.tech/tools/']
        self.assertEqual(len(tool_urls), 52, f"Expected exactly 52 tool URLs in sitemap, found {len(tool_urls)}")

        # No Wave 2 in sitemap
        for slug in self.wave2_slugs:
            target = f"https://aitoolgems.tech/tools/{slug}/"
            self.assertNotIn(target, urls, f"Quarantined Wave 2 tool {slug} must not be in sitemap")

        # No Japan in sitemap
        for u in urls:
            self.assertNotIn("/jp/", u, f"Japan URL found in sitemap: {u}")

if __name__ == "__main__":
    unittest.main()
