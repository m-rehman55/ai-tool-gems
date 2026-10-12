#!/usr/bin/env python3
"""
Unit tests for Keyword Research, Content Quality & Planning
------------------------------------------------------------
"""

import sys
from pathlib import Path
import unittest

AGENT_DIR = Path(__file__).resolve().parent.parent
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

from agent.crawler import CrawledPage
from agent.keyword_research import KeywordManager, KeywordTarget
from agent.content_quality import ContentQualityAuditor
from agent.content_planner import ContentPlanner

class TestContentQuality(unittest.TestCase):

    def setUp(self):
        self.km = KeywordManager()
        self.auditor = ContentQualityAuditor(guide_min_words=500, tool_min_words=200)
        self.planner = ContentPlanner()

    def test_cannibalization_detection(self):
        self.km.targets = [
            KeywordTarget(url="https://aitoolgems.tech/tools/chatgpt/", primary_keyword="chatgpt plus pakistan"),
            KeywordTarget(url="https://aitoolgems.tech/guides/chatgpt/", primary_keyword="chatgpt plus pakistan"),
        ]
        collisions = self.km.check_cannibalization()
        self.assertEqual(len(collisions), 1)
        self.assertEqual(collisions[0].primary_keyword, "chatgpt plus pakistan")

    def test_placeholder_text_flagged(self):
        page = CrawledPage(
            url="https://aitoolgems.tech/guides/test/",
            status_code=200,
            word_count=600,
            raw_html="<html><body><h1>Test Guide</h1><p>TODO: Add pricing here. Lorem ipsum dolor sit amet.</p></body></html>",
        )
        report = self.auditor.audit_page_content(page)
        self.assertFalse(report.passed)
        self.assertTrue(any(i.check_type == "PLACEHOLDER_TEXT" for i in report.issues))

    def test_markdown_leak_flagged(self):
        page = CrawledPage(
            url="https://aitoolgems.tech/guides/test/",
            status_code=200,
            word_count=600,
            raw_html="<html><body><h1>Test</h1>## Section Heading Leaked</body></html>",
        )
        report = self.auditor.audit_page_content(page)
        self.assertFalse(report.passed)
        self.assertTrue(any(i.check_type == "MARKDOWN_LEAK" for i in report.issues))

    def test_ai_search_readiness_detection(self):
        page = CrawledPage(
            url="https://aitoolgems.tech/tools/canva-pro-pakistan/",
            status_code=200,
            word_count=450,
            raw_html="""
            <html><body>
                <h1>Canva Pro Pakistan</h1>
                <p>Price: Rs. 1,200 PKR with EasyPaisa or JazzCash checkout.</p>
                <div class="faq-container"><h3>Frequently Asked Questions</h3></div>
                <table><tr><th>Plan</th><th>Price</th></tr></table>
            </body></html>
            """,
        )
        report = self.auditor.audit_page_content(page)
        self.assertTrue(report.ai_search_readiness["has_pkr_price"])
        self.assertTrue(report.ai_search_readiness["has_pakistan_payment"])
        self.assertTrue(report.ai_search_readiness["has_faq"])
        self.assertTrue(report.ai_search_readiness["has_comparison_table"])

    def test_content_brief_generation(self):
        target = KeywordTarget(
            url="",
            primary_keyword="cursor pro pakistan",
            intent="transactional",
            market="PK",
        )
        brief = self.planner.create_guide_brief(target)
        self.assertEqual(brief.slug, "cursor-pro-pakistan")
        self.assertIn("PKR", brief.meta_description_draft)
        self.assertGreaterEqual(len(brief.suggested_h2_sections), 5)
        self.assertGreaterEqual(len(brief.faq_questions), 4)

if __name__ == "__main__":
    unittest.main()
