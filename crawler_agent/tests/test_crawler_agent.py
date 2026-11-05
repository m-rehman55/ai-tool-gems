"""
Comprehensive Unit Tests for Crawler Agent (Agent 2).
Covers multi-page crawling, heading hierarchy validation, broken links,
orphan page detection, state machine transitions, and technical SEO health scoring.
"""

import unittest
import tempfile
import shutil
from pathlib import Path

from crawler_agent.models import URLCrawlState, CrawlRecord
from crawler_agent.engine import CrawlerEngine, AdvancedHTMLParser
from crawler_agent.analyzer import TechnicalSEOAnalyzer
from crawler_agent.inventory import URLInventoryDatabase


class TestCrawlerAgent(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.engine = CrawlerEngine(base_url="https://aitoolgems.tech", base_dir=self.test_dir)
        self.analyzer = TechnicalSEOAnalyzer(base_url="https://aitoolgems.tech")
        self.db_path = Path(self.test_dir) / "inventory_test.json"
        self.inventory = URLInventoryDatabase(storage_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_advanced_html_parser_heading_hierarchy(self):
        # 1. Valid hierarchy
        html_valid = """<!DOCTYPE html><html><head><title>Test Valid</title></head><body>
        <h1>Primary H1</h1><h2>Section 1</h2><h3>Subsection A</h3>
        </body></html>"""
        record_valid = self.engine.parse_html(html_valid, "https://aitoolgems.tech/valid/")
        self.assertTrue(record_valid.headings.hierarchy_valid)
        self.assertFalse(record_valid.headings.missing_h1)
        self.assertEqual(record_valid.headings.h1_list, ["Primary H1"])

        # 2. Missing H1
        html_missing_h1 = """<!DOCTYPE html><html><head><title>No H1</title></head><body>
        <h2>Section 1</h2>
        </body></html>"""
        record_no_h1 = self.engine.parse_html(html_missing_h1, "https://aitoolgems.tech/no-h1/")
        self.assertTrue(record_no_h1.headings.missing_h1)
        self.assertFalse(record_no_h1.headings.hierarchy_valid)

        # 3. Skipped tier (H1 then H3 without H2)
        html_skipped = """<!DOCTYPE html><html><head><title>Skipped Tier</title></head><body>
        <h1>Primary</h1><h3>Direct H3 without H2</h3>
        </body></html>"""
        record_skipped = self.engine.parse_html(html_skipped, "https://aitoolgems.tech/skipped/")
        self.assertFalse(record_skipped.headings.hierarchy_valid)
        self.assertTrue(any("hierarchy violation" in issue.lower() for issue in record_skipped.headings.issues))

    def test_image_alt_and_mixed_content_detection(self):
        html = """<!DOCTYPE html><html><head><title>Media Test</title></head><body>
        <h1>Images</h1>
        <img src="https://aitoolgems.tech/assets/logo.webp" alt="Logo" loading="lazy">
        <img src="https://aitoolgems.tech/assets/banner.png">
        <img src="http://insecure-cdn.com/ad.jpg" alt="Mixed Ad">
        </body></html>"""
        record = self.engine.parse_html(html, "https://aitoolgems.tech/media/")
        self.assertTrue(record.has_mixed_content)
        self.assertEqual(len(record.images), 3)

        missing_alts = [img for img in record.images if img.is_missing_alt]
        self.assertEqual(len(missing_alts), 1)
        self.assertEqual(missing_alts[0].src, "https://aitoolgems.tech/assets/banner.png")

    def test_technical_audit_score_and_issue_classification(self):
        clean_page = self.engine.parse_html(
            """<html><head><title>Clean</title><link rel="canonical" href="https://aitoolgems.tech/clean/" /></head>
            <body><h1>Clean</h1><h2>Sub</h2><p>""" + "Word " * 250 + """</p></body></html>""",
            "https://aitoolgems.tech/clean/"
        )
        broken_page = self.engine.parse_html(
            """<html><head><title>Broken</title></head><body><p>Bad</p></body></html>""",
            "https://aitoolgems.tech/broken/",
            status_code=404
        )
        broken_page.error_message = "HTTP 404 Not Found"

        summary = self.analyzer.audit_crawl_dataset([clean_page, broken_page])
        self.assertEqual(summary.total_urls_scanned, 2)
        self.assertEqual(summary.broken_links_count, 1)
        self.assertTrue(summary.technical_health_score < 100.0)

    def test_url_inventory_state_machine_lifecycle(self):
        # 1. Register -> DISCOVERED
        url = "https://aitoolgems.tech/tools/new-tool/"
        rec = self.inventory.register_url(url)
        self.assertEqual(rec.state, URLCrawlState.DISCOVERED)

        # 2. Upsert crawl record -> CRAWLED
        crawl_rec = self.engine.parse_html("<html><body><h1>Tool</h1></body></html>", url)
        self.inventory.upsert_crawl_record(crawl_rec)
        updated = self.inventory.records[url]
        self.assertEqual(updated.state, URLCrawlState.CRAWLED)

        # 3. Analyze with issues -> FIX_REQUIRED
        self.inventory.update_analysis_outcome(url, issues=["Missing canonical tag"])
        self.assertEqual(self.inventory.records[url].state, URLCrawlState.FIX_REQUIRED)

        # 4. Analyze clean -> ANALYZED
        self.inventory.update_analysis_outcome(url, issues=[])
        self.assertEqual(self.inventory.records[url].state, URLCrawlState.ANALYZED)

    def test_orphan_page_detection(self):
        p1 = self.engine.parse_html(
            """<html><head><title>P1</title><link rel="canonical" href="https://aitoolgems.tech/" /></head>
            <body><h1>Home</h1><a href="https://aitoolgems.tech/linked/">Linked</a></body></html>""",
            "https://aitoolgems.tech/"
        )
        p2 = self.engine.parse_html(
            """<html><head><title>P2</title><link rel="canonical" href="https://aitoolgems.tech/linked/" /></head>
            <body><h1>Linked</h1></body></html>""",
            "https://aitoolgems.tech/linked/"
        )
        p3_orphan = self.engine.parse_html(
            """<html><head><title>Orphan</title><link rel="canonical" href="https://aitoolgems.tech/orphan/" /></head>
            <body><h1>Orphan</h1></body></html>""",
            "https://aitoolgems.tech/orphan/"
        )

        summary = self.analyzer.audit_crawl_dataset([p1, p2, p3_orphan])
        self.assertEqual(summary.orphan_pages_count, 1)


if __name__ == "__main__":
    unittest.main()
