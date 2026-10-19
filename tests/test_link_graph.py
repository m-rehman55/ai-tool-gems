"""
Unit tests and defect-detection fixtures for LinkGraphChecker.
Verifies both repository-wide link health and synthetic pass/fail fixtures.
"""

import os
import tempfile
import unittest
from pathlib import Path

from scripts.link_graph_checker import LinkGraphChecker, Issue, LinkGraphReport

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestLinkGraphCheckerLiveRepo(unittest.TestCase):
    """Executes checker on the actual repository and confirms zero actionable defects."""

    @classmethod
    def setUpClass(cls):
        cls.checker = LinkGraphChecker(REPO_ROOT)
        cls.report = cls.checker.run_all_checks()

    def test_live_repo_has_zero_errors(self):
        errors = self.report.errors
        error_msgs = [f"[{e.category}] {e.file}: {e.message}" for e in errors]
        self.assertEqual(len(errors), 0, f"Found {len(errors)} link-graph errors in repository:\n" + "\n".join(error_msgs))

    def test_live_repo_scans_all_files_and_sitemap(self):
        self.assertGreaterEqual(self.report.total_html_files, 70, "Expected at least 70 HTML files scanned")
        self.assertGreaterEqual(self.report.total_internal_links, 1000, "Expected at least 1,000 internal links checked")
        self.assertGreaterEqual(self.report.total_fragments_checked, 200, "Expected at least 200 fragment anchors checked")
        self.assertGreaterEqual(self.report.total_sitemap_urls, 60, "Expected at least 60 sitemap URLs verified")


class TestLinkGraphCheckerFixtures(unittest.TestCase):
    """Tests synthetic failure and edge cases using temporary fixture workspaces."""

    def create_mock_workspace(self, files: dict[str, str]) -> Path:
        temp_dir = Path(tempfile.mkdtemp(prefix="aitoolgems_link_fixture_"))
        for rel_path, content in files.items():
            file_path = temp_dir / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
        return temp_dir

    def test_fixture_detects_broken_internal_link(self):
        files = {
            "index.html": '<!doctype html><html><body><a href="tools/ghost-tool/">Ghost</a></body></html>',
            "sitemap.xml": '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://aitoolgems.tech/</loc></url></urlset>',
            "app.js": 'const products = []; const STATIC_TOOL_PAGES = new Set([]);'
        }
        workspace = self.create_mock_workspace(files)
        checker = LinkGraphChecker(workspace)
        report = checker.run_all_checks()
        broken = [i for i in report.errors if i.category == "BROKEN_INTERNAL_LINK"]
        self.assertGreaterEqual(len(broken), 1, "Expected BROKEN_INTERNAL_LINK to be detected")
        self.assertIn("tools/ghost-tool/", broken[0].target)

    def test_fixture_detects_missing_fragment_anchor(self):
        files = {
            "index.html": '<!doctype html><html><body><a href="#nonExistentSection">Jump</a><a href="about.html#missingTarget">About Missing</a></body></html>',
            "about.html": '<!doctype html><html><head><title>About</title></head><body><h1 id="realSection">About Us</h1></body></html>',
            "sitemap.xml": '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://aitoolgems.tech/</loc></url><url><loc>https://aitoolgems.tech/about.html</loc></url></urlset>',
            "app.js": 'const products = []; const STATIC_TOOL_PAGES = new Set([]);'
        }
        workspace = self.create_mock_workspace(files)
        checker = LinkGraphChecker(workspace)
        report = checker.run_all_checks()
        missing_frags = [i for i in report.errors if i.category == "MISSING_FRAGMENT"]
        self.assertEqual(len(missing_frags), 2, "Expected 2 missing fragment errors")
        targets = [mf.target for mf in missing_frags]
        self.assertIn("#nonExistentSection", targets)
        self.assertIn("about.html#missingTarget", targets)

    def test_fixture_detects_orphan_public_page(self):
        files = {
            "index.html": '<!doctype html><html><body><a href="linked.html">Linked</a></body></html>',
            "linked.html": '<!doctype html><html><body><p>Linked</p></body></html>',
            "isolated.html": '<!doctype html><html><body><p>Nobody links to me!</p></body></html>',
            "sitemap.xml": '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://aitoolgems.tech/</loc></url></urlset>',
            "app.js": 'const products = []; const STATIC_TOOL_PAGES = new Set([]);'
        }
        workspace = self.create_mock_workspace(files)
        checker = LinkGraphChecker(workspace)
        report = checker.run_all_checks()
        orphans = [i for i in report.errors if i.category == "ORPHAN_PAGE"]
        self.assertEqual(len(orphans), 1, "Expected exactly 1 orphan page error")
        self.assertEqual(orphans[0].file, "isolated.html")

    def test_fixture_allows_documented_orphan_exceptions(self):
        files = {
            "index.html": '<!doctype html><html><body><p>Home</p></body></html>',
            "404.html": '<!doctype html><html><head><meta name="robots" content="noindex"></head><body>Not found</body></html>',
            "admin.html": '<!doctype html><html><head><meta name="robots" content="noindex"></head><body>Admin</body></html>',
            "sitemap.xml": '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://aitoolgems.tech/</loc></url></urlset>',
            "app.js": 'const products = []; const STATIC_TOOL_PAGES = new Set([]);'
        }
        workspace = self.create_mock_workspace(files)
        checker = LinkGraphChecker(workspace)
        report = checker.run_all_checks()
        orphans = [i for i in report.errors if i.category == "ORPHAN_PAGE"]
        self.assertEqual(len(orphans), 0, "Documented exceptions (404, admin) must not be flagged as orphans")

    def test_fixture_detects_duplicate_product_id(self):
        files = {
            "index.html": '<!doctype html><html><body></body></html>',
            "sitemap.xml": '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://aitoolgems.tech/</loc></url></urlset>',
            "app.js": """
            const products = [
              {id:'chatgpt',name:'ChatGPT Plus'},
              {id:'chatgpt',name:'Duplicate ChatGPT'}
            ];
            const STATIC_TOOL_PAGES = new Set([]);
            """
        }
        workspace = self.create_mock_workspace(files)
        checker = LinkGraphChecker(workspace)
        report = checker.run_all_checks()
        dupes = [i for i in report.errors if i.category == "DUPLICATE_PRODUCT_ID"]
        self.assertEqual(len(dupes), 1, "Expected duplicate product ID defect")
        self.assertEqual(dupes[0].target, "chatgpt")

    def test_fixture_detects_missing_tool_route(self):
        files = {
            "index.html": '<!doctype html><html><body></body></html>',
            "sitemap.xml": '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://aitoolgems.tech/</loc></url></urlset>',
            "app.js": """
            const products = [
              {id:'magic-tool',name:'Magic Tool'}
            ];
            const STATIC_TOOL_PAGES = new Set(['magic-tool']);
            """
        }
        workspace = self.create_mock_workspace(files)
        checker = LinkGraphChecker(workspace)
        report = checker.run_all_checks()
        missing_routes = [i for i in report.errors if i.category == "MISSING_TOOL_ROUTE"]
        self.assertEqual(len(missing_routes), 1, "Expected MISSING_TOOL_ROUTE error")
        self.assertEqual(missing_routes[0].target, "magic-tool")

    def test_fixture_detects_invalid_whatsapp_number(self):
        files = {
            "index.html": '<!doctype html><html><body><a href="https://wa.me/923001234567?text=Hi">Order</a></body></html>',
            "sitemap.xml": '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://aitoolgems.tech/</loc></url></urlset>',
            "app.js": 'const products = []; const STATIC_TOOL_PAGES = new Set([]);'
        }
        workspace = self.create_mock_workspace(files)
        checker = LinkGraphChecker(workspace)
        report = checker.run_all_checks()
        wa_errors = [i for i in report.errors if i.category == "INVALID_WHATSAPP_ACTION"]
        self.assertEqual(len(wa_errors), 1, "Expected INVALID_WHATSAPP_ACTION for unverified number")

    def test_fixture_detects_broken_local_asset(self):
        files = {
            "index.html": '<!doctype html><html><body><img src="assets/missing-banner.png" alt="Missing"></body></html>',
            "sitemap.xml": '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://aitoolgems.tech/</loc></url></urlset>',
            "app.js": 'const products = []; const STATIC_TOOL_PAGES = new Set([]);'
        }
        workspace = self.create_mock_workspace(files)
        checker = LinkGraphChecker(workspace)
        report = checker.run_all_checks()
        asset_errors = [i for i in report.errors if i.category == "BROKEN_ASSET"]
        self.assertEqual(len(asset_errors), 1, "Expected BROKEN_ASSET error for missing local image")
        self.assertEqual(asset_errors[0].target, "assets/missing-banner.png")


if __name__ == "__main__":
    unittest.main()
