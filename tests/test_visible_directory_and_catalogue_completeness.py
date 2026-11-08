"""
tests/test_visible_directory_and_catalogue_completeness.py

Automated acceptance test suite verifying:
1. tools/index.html table completeness: exactly 65 rows (40 assisted + 25 directory).
2. index.html productGrid completeness: all 65 tools pre-rendered in DOM.
3. Zero syntax errors in app.js.
4. Catalogue consistency: 40 assisted commercial products + 25 directory reference profiles.
5. Directory-only tools cannot be added to cart.
"""

import os
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CANONICAL_40_ASSISTED = [
    'adobe', 'allinone', 'canva', 'capcut', 'chatgpt', 'claude', 'copilot', 'cursor',
    'deepseek', 'elevenlabs', 'figma', 'freepik', 'gamma', 'gemini', 'grammarly',
    'grok', 'heygen', 'kling', 'leonardo', 'linkedin', 'lovable', 'midjourney',
    'n8n', 'netflix', 'nordvpn', 'notion', 'office365', 'perplexity', 'quillbot',
    'replit', 'runway', 'semrush', 'spotify', 'suno', 'surfshark', 'tradingview',
    'turnitin', 'veo', 'windows', 'youtube'
]

DIRECTORY_25_PROFILES = [
    'bolt-new', 'coursera-plus', 'descript', 'firecrawl', 'invideo-ai', 'make',
    'manus-ai', 'opus-clip', 'qwen', 'udemy-personal', 'v0', 'windsurf',
    'ahrefs', 'chatprd', 'davinci-resolve', 'domo-ai', 'genspark', 'hailuo-ai',
    'higgsfield', 'morphic', 'notebooklm', 'quizlet', 'railway', 'skillshare', 'supabase'
]


class TestVisibleDirectoryAndCatalogueCompleteness(unittest.TestCase):

    def setUp(self):
        self.tools_index_path = ROOT / 'tools' / 'index.html'
        self.index_html_path = ROOT / 'index.html'
        self.app_js_path = ROOT / 'app.js'

        with open(self.tools_index_path, 'r', encoding='utf-8') as f:
            self.tools_html = f.read()

        with open(self.index_html_path, 'r', encoding='utf-8') as f:
            self.index_html = f.read()

        with open(self.app_js_path, 'r', encoding='utf-8') as f:
            self.app_js = f.read()

    def test_app_js_has_zero_syntax_errors(self):
        """Assert app.js passes node syntax check with exit code 0."""
        res = subprocess.run(['node', '-c', str(self.app_js_path)], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, f"app.js syntax error: {res.stderr}")

    def test_tools_index_table_has_exactly_65_data_rows(self):
        """Assert tools/index.html table exposes exactly 65 tool rows (40 assisted + 25 directory)."""
        table_rows = re.findall(r'<tr[^>]*>([\s\S]*?)</tr>', self.tools_html)
        data_rows = []
        for tr in table_rows:
            m = re.search(r'href=["\']([\w-]+)/["\']', tr)
            if m:
                slug = m.group(1)
                is_dir = "official vendor" in tr.lower() or "directory" in tr.lower()
                data_rows.append((slug, is_dir))

        self.assertEqual(len(data_rows), 65, f"Expected 65 rows in tools/index.html table, got {len(data_rows)}")
        assisted = [r[0] for r in data_rows if not r[1]]
        directory = [r[0] for r in data_rows if r[1]]

        self.assertEqual(len(assisted), 40, f"Expected 40 assisted rows, got {len(assisted)}")
        self.assertEqual(len(directory), 25, f"Expected 25 directory rows, got {len(directory)}")

    def test_all_12_previously_missing_tools_in_tools_table(self):
        """Verify the 12 tools previously missing from tools/index.html are present."""
        twelve_tools = [
            'claude', 'midjourney', 'cursor', 'perplexity', 'deepseek',
            'grok', 'runway', 'heygen', 'grammarly', 'quillbot', 'semrush', 'allinone'
        ]
        for tool in twelve_tools:
            self.assertIn(f'href="{tool}/"', self.tools_html, f"Missing {tool} link in tools/index.html")

    def test_homepage_pre_renders_all_65_cards(self):
        """Assert index.html productGrid contains all 65 pre-rendered tool cards."""
        card_ids = re.findall(r'<article[^>]*data-id="([^"]+)"[^>]*>', self.index_html)
        self.assertEqual(len(card_ids), 65, f"Expected 65 cards in index.html, got {len(card_ids)}")
        self.assertEqual(len(set(card_ids)), 65, "Expected 65 unique card IDs in index.html")

        # Verify all 40 commercial present
        for slug in CANONICAL_40_ASSISTED:
            self.assertIn(slug, card_ids, f"Commercial card {slug} missing from index.html")

        # Verify all 25 directory present
        for slug in DIRECTORY_25_PROFILES:
            self.assertIn(slug, card_ids, f"Directory card {slug} missing from index.html")

    def test_all_65_tool_detail_pages_exist_and_accessible(self):
        """Verify all 65 tool detail pages exist on disk with valid index.html."""
        for slug in CANONICAL_40_ASSISTED + DIRECTORY_25_PROFILES:
            page_path = ROOT / 'tools' / slug / 'index.html'
            self.assertTrue(page_path.exists(), f"Detail page tools/{slug}/index.html must exist")

    def test_directory_cards_have_no_add_to_cart_action(self):
        """Verify directory cards in index.html do NOT contain data-add or buy now actions."""
        # Find directory card blocks
        dir_cards = re.findall(r'<article[^>]*class="[^"]*directory-card[^"]*"[^>]*>([\s\S]*?)</article>', self.index_html)
        self.assertEqual(len(dir_cards), 25, f"Expected 25 directory card blocks, got {len(dir_cards)}")
        for card in dir_cards:
            self.assertNotIn('data-add=', card, "Directory card must not have data-add attribute")
            self.assertNotIn('data-order=', card, "Directory card must not have data-order attribute")
            self.assertIn('Directory Reference', card, "Directory card must declare Directory Reference")


if __name__ == '__main__':
    unittest.main()

