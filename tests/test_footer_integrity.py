#!/usr/bin/env python3
"""
Test Suite: Global Footer Structural, Semantic & Link Integrity
---------------------------------------------------------------
Ensures 100% adherence to the AI Tool Gems Global Footer Architecture
defined in docs/FOOTER_REMEDIATION_PLAN.md.
"""

from __future__ import annotations
import os
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EXCLUDED_DIRS = {
    '.git', '.gemini', 'brain', 'node_modules', '.venv',
    'reports', 'test-results', 'audit', 'AI_TOOL_GEMS_COMPETITOR_INTELLIGENCE_2026-11-15',
    'data', 'scratch'
}

EXCLUDED_FILES = {
    'admin.html', '404.html', 'googleb36d12ee905644d9.html',
    'gsc_daily_checklist.html', 'privacy.html', 'terms.html'
}


class TestFooterIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html_files = []
        for root, dirs, files in os.walk(REPO_ROOT):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith('.')]
            for f in files:
                if f.endswith('.html') and f not in EXCLUDED_FILES:
                    p = Path(root) / f
                    rel_p = str(p.relative_to(REPO_ROOT)).replace('\\', '/')
                    if 'snapshots' not in rel_p and 'scratch' not in rel_p:
                        cls.html_files.append((p, rel_p))

    def test_all_customer_facing_pages_contain_canonical_site_footer(self):
        """Verifies that every customer-facing HTML page contains the canonical site-footer component."""
        self.assertGreater(len(self.html_files), 120, "Should have 120+ customer-facing pages")
        for file_path, rel_path in self.html_files:
            html = file_path.read_text(encoding='utf-8')
            self.assertIn('<footer class="site-footer" id="site-footer">', html,
                          f"File {rel_path} is missing canonical <footer class=\"site-footer\" id=\"site-footer\">")
            self.assertIn('class="footer-shell"', html, f"File {rel_path} missing footer-shell")
            self.assertIn('class="footer-payment"', html, f"File {rel_path} missing footer-payment strip")
            self.assertIn('class="footer-grid"', html, f"File {rel_path} missing footer-grid")
            self.assertIn('class="footer-bottom"', html, f"File {rel_path} missing footer-bottom")

    def test_footer_payment_strip_present_and_accurate(self):
        """Ensures domestic Pakistani payment rails and international inquiry rails are grounded and present."""
        index_html = (REPO_ROOT / 'index.html').read_text(encoding='utf-8')
        expected_rails = ['EasyPaisa', 'JazzCash', 'SadaPay', 'NayaPay', 'Raast', 'Bank IBFT']
        for rail in expected_rails:
            self.assertIn(f'<li>{rail}</li>', index_html, f"Missing domestic payment rail: {rail}")

        inquiry_rails = ['Wise', 'SWIFT Bank Wire']
        for rail in inquiry_rails:
            self.assertIn(f'<li>{rail}</li>', index_html, f"Missing international inquiry rail: {rail}")

    def test_footer_5_columns_structure_and_links(self):
        """Validates that the 5 columns contain essential marketplace, popular tool, trust, and support links."""
        index_html = (REPO_ROOT / 'index.html').read_text(encoding='utf-8')

        # Popular Subscriptions
        popular_tools = [
            'tools/chatgpt/', 'tools/claude/', 'tools/gemini/', 'tools/canva/',
            'tools/capcut/', 'tools/midjourney/', 'tools/cursor/', 'tools/copilot/',
            'tools/elevenlabs/', 'tools/nordvpn/'
        ]
        for tool in popular_tools:
            self.assertIn(f'href="{tool}"', index_html, f"Missing popular tool link: {tool}")

        # Trust & Policies
        trust_links = [
            'about.html', 'how-we-review.html', 'how-we-price.html', 'how-we-source.html',
            'product-verification.html', 'correction-policy.html', 'policies.html#warranty',
            'policies.html#refunds', 'terms-of-service/'
        ]
        for link in trust_links:
            self.assertIn(f'href="{link}"', index_html, f"Missing trust policy link: {link}")

    def test_footer_concierge_and_hours(self):
        """Validates customer concierge WhatsApp channels and verified support hours."""
        index_html = (REPO_ROOT / 'index.html').read_text(encoding='utf-8')
        self.assertIn('data-whatsapp="help"', index_html)
        self.assertIn('https://wa.me/923236715731', index_html)
        self.assertIn('09:00 AM – 12:00 AM PKT (Daily)', index_html)
        self.assertIn('Assisted WhatsApp concierge support.', index_html)

    def test_zero_broken_footer_links(self):
        """Scans all links within every footer across all pages and guarantees they resolve to valid disk files."""
        footer_regex = re.compile(r'<footer\b[^>]*>([\s\S]*?)</footer>', re.IGNORECASE)
        href_regex = re.compile(r'href=["\']([^"\']+)["\']')

        for file_path, rel_path in self.html_files:
            html = file_path.read_text(encoding='utf-8')
            m = footer_regex.search(html)
            self.assertIsNotNone(m, f"Could not find footer in {rel_path}")

            footer_html = m.group(1)
            hrefs = href_regex.findall(footer_html)

            for href in hrefs:
                if href.startswith(('mailto:', 'tel:', 'javascript:', 'data:', 'http://', 'https://')):
                    continue
                if href.startswith('#'):
                    # Local fragment check
                    frag = href[1:]
                    frag_regex = re.compile(rf'(id|name)=["\']{re.escape(frag)}["\']', re.IGNORECASE)
                    self.assertTrue(frag_regex.search(html),
                                    f"Broken fragment in {rel_path} footer: {href}")
                    continue

                # Relative link resolution
                clean_href = href.split('?')[0].split('#')[0]
                frag = href.split('#')[1] if '#' in href else None

                current_dir = file_path.parent
                target_p = (current_dir / clean_href).resolve()

                if clean_href.endswith('/') or os.path.isdir(target_p):
                    target_idx = target_p / 'index.html' if target_p.is_dir() else target_p
                    self.assertTrue(target_idx.exists(),
                                    f"Broken footer link in {rel_path}: {href} -> {target_idx}")
                    if frag:
                        target_html = target_idx.read_text(encoding='utf-8')
                        frag_regex = re.compile(rf'(id|name)=["\']{re.escape(frag)}["\']', re.IGNORECASE)
                        self.assertTrue(frag_regex.search(target_html),
                                        f"Broken anchor in {rel_path} footer: {href}")
                else:
                    self.assertTrue(target_p.exists(),
                                    f"Broken footer link in {rel_path}: {href} -> {target_p}")
                    if frag:
                        target_html = target_p.read_text(encoding='utf-8')
                        frag_regex = re.compile(rf'(id|name)=["\']{re.escape(frag)}["\']', re.IGNORECASE)
                        self.assertTrue(frag_regex.search(target_html),
                                        f"Broken anchor in {rel_path} footer: {href}")

    def test_css_system_coverage(self):
        """Verifies that .site-footer and .footer-shell are implemented across all 3 key stylesheets."""
        for sheet in ['styles.css', 'tool-page.css', 'guide.css']:
            css_content = (REPO_ROOT / sheet).read_text(encoding='utf-8')
            self.assertIn('.site-footer', css_content, f"{sheet} missing .site-footer")
            self.assertIn('.footer-shell', css_content, f"{sheet} missing .footer-shell")
            self.assertIn('.footer-payment', css_content, f"{sheet} missing .footer-payment")
            self.assertIn('.footer-grid', css_content, f"{sheet} missing .footer-grid")


if __name__ == '__main__':
    unittest.main()
