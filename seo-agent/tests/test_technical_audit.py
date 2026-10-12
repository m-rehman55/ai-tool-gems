#!/usr/bin/env python3
"""
Unit tests for Technical SEO Audit & Schema Validator in seo-agent
------------------------------------------------------------------
"""

import sys
from pathlib import Path
import unittest

AGENT_DIR = Path(__file__).resolve().parent.parent
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

from agent.crawler import CrawledPage, Crawler
from agent.technical_audit import TechnicalAuditor
from agent.schema_validator import SchemaValidator
from agent.internal_links import InternalLinkAnalyzer

class TestTechnicalAudit(unittest.TestCase):

    def setUp(self):
        self.auditor = TechnicalAuditor()
        self.schema_val = SchemaValidator()
        self.link_analyzer = InternalLinkAnalyzer()

    def test_clean_page_has_no_issues(self):
        page = CrawledPage(
            url="https://aitoolgems.tech/tools/chatgpt-plus-pakistan/",
            status_code=200,
            title="ChatGPT Plus Pakistan | Buy Subscription in PKR",
            meta_description="Buy ChatGPT Plus in Pakistan with PKR pricing. Instant delivery via EasyPaisa and JazzCash. Verified AI subscription provider.",
            canonical="https://aitoolgems.tech/tools/chatgpt-plus-pakistan/",
            h1_list=["ChatGPT Plus in Pakistan"],
            images=[{"src": "chatgpt.png", "alt": "ChatGPT Plus logo"}],
            raw_html="<html><head><meta name='viewport' content='width=device-width'></head></html>",
        )
        issues = self.auditor.audit_page(page)
        self.assertEqual(len(issues), 0)

    def test_missing_title_flagged_critical(self):
        page = CrawledPage(
            url="https://aitoolgems.tech/tools/sample/",
            status_code=200,
            title="",
            canonical="https://aitoolgems.tech/tools/sample/",
            h1_list=["Sample Tool"],
            raw_html="<meta name='viewport' content='width=device-width'>",
        )
        issues = self.auditor.audit_page(page)
        self.assertTrue(any(i.check_type == "TITLE" and i.severity == "P0_CRITICAL" for i in issues))

    def test_multiple_h1_flagged(self):
        page = CrawledPage(
            url="https://aitoolgems.tech/tools/sample/",
            status_code=200,
            title="Valid Title For Sample Tool In Pakistan",
            meta_description="Valid meta description with appropriate length to satisfy the 70 to 170 character bounds requirement.",
            canonical="https://aitoolgems.tech/tools/sample/",
            h1_list=["First Heading", "Second Heading"],
            raw_html="<meta name='viewport' content='width=device-width'>",
        )
        issues = self.auditor.audit_page(page)
        self.assertTrue(any(i.check_type == "H1" and i.severity == "P2_MEDIUM" for i in issues))

    def test_schema_product_currency_validation(self):
        valid_schema = """{
            "@type": "Product",
            "name": "Claude Pro",
            "description": "Claude Pro AI Assistant",
            "offers": {
                "@type": "Offer",
                "price": "5500",
                "priceCurrency": "PKR",
                "availability": "https://schema.org/InStock"
            }
        }"""
        issues = self.schema_val.validate_page_schemas([valid_schema], "https://aitoolgems.tech/tools/claude/")
        self.assertEqual(len(issues), 0)

        invalid_schema = """{
            "@type": "Product",
            "name": "Claude Pro",
            "description": "Claude Pro AI Assistant",
            "offers": {
                "@type": "Offer",
                "price": "20",
                "priceCurrency": "USD"
            }
        }"""
        bad_issues = self.schema_val.validate_page_schemas([invalid_schema], "https://aitoolgems.tech/tools/claude/")
        self.assertTrue(any("currency mismatch" in i.message.lower() for i in bad_issues))

    def test_internal_links_orphan_detection(self):
        p1 = CrawledPage(
            url="https://aitoolgems.tech/",
            status_code=200,
            internal_links=["https://aitoolgems.tech/tools/chatgpt/"],
        )
        p2 = CrawledPage(
            url="https://aitoolgems.tech/tools/chatgpt/",
            status_code=200,
            internal_links=["https://aitoolgems.tech/"],
        )
        p3 = CrawledPage(
            url="https://aitoolgems.tech/guides/orphan-guide/",
            status_code=200,
            internal_links=[],
        )
        report = self.link_analyzer.analyze_graph([p1, p2, p3])
        self.assertIn("https://aitoolgems.tech/guides/orphan-guide/", report.orphan_pages)

if __name__ == "__main__":
    unittest.main()
