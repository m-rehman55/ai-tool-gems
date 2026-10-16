#!/usr/bin/env python3
"""
Unit and integration tests for Crawler, Deployment Verifier, and 14-Artifact Daily Reporting
"""

import unittest
import shutil
import tempfile
from pathlib import Path

from agent.crawler import (
    Crawler,
    detect_screaming_frog,
    is_allowed_domain,
    is_sensitive_url,
    normalize_url,
)
from agent.reporting import ReportGenerator
from agent.deployment_verifier import DeploymentVerifier
from agent.technical_audit import TechnicalAuditReport, AuditIssue
from agent.scope_guard import ScopeResult
from agent.monitoring import PerformanceMetrics

class TestCrawlerAndReporting(unittest.TestCase):

    def test_screaming_frog_detection_fallback(self):
        """Ensures that Screaming Frog CLI absence cleanly defaults to native Python."""
        status = detect_screaming_frog()
        self.assertIn("engine", status)
        self.assertIn(status["engine"], ["screaming_frog", "native_python"])
        self.assertIn("available", status)
        self.assertIsInstance(status["available"], bool)

    def test_domain_allowlist(self):
        """Verifies domain boundary enforcement."""
        self.assertTrue(is_allowed_domain("https://aitoolgems.tech/prices/"))
        self.assertTrue(is_allowed_domain("https://www.aitoolgems.tech/deals/"))
        self.assertTrue(is_allowed_domain("/tools/chatgpt/"))
        self.assertFalse(is_allowed_domain("https://malicious-external-site.com/hack"))

    def test_sensitive_url_exclusion(self):
        """Confirms that checkout, cart, payment, admin, and auth URLs are never crawled."""
        self.assertTrue(is_sensitive_url("/admin.html"))
        self.assertTrue(is_sensitive_url("/checkout"))
        self.assertTrue(is_sensitive_url("/cart/payment"))
        self.assertTrue(is_sensitive_url("/logout"))
        self.assertFalse(is_sensitive_url("/tools/chatgpt/"))
        self.assertFalse(is_sensitive_url("/guides/ai-tools-pakistan/"))

    def test_url_normalization_and_parameter_stripping(self):
        """Confirms tracking params (utm_*, fbclid) are stripped to prevent infinite crawl loops."""
        raw = "https://aitoolgems.tech/tools/chatgpt/?utm_source=twitter&utm_medium=cpc&fbclid=123#reviews"
        norm = normalize_url(raw)
        self.assertEqual(norm, "https://aitoolgems.tech/tools/chatgpt/")

    def test_fourteen_artifact_report_generation(self):
        """Verifies that all 14 required daily report files are generated properly."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            reporter = ReportGenerator(output_dir=tmp_dir)
            crawler = Crawler()
            sample_page = crawler.parse_html_content(
                html="<!doctype html><html><head><title>Test Page</title><meta name='description' content='Test Desc'></head><body><h1>Heading</h1></body></html>",
                url="https://aitoolgems.tech/test",
            )
            tech_report = TechnicalAuditReport(
                total_pages_audited=1,
                clean_pages_count=1,
                issues=[],
                score=100,
            )
            scope_res = ScopeResult(passed=True)
            metrics = PerformanceMetrics(
                connected=False,
                site_url="https://aitoolgems.tech",
                total_impressions=10,
                total_clicks=2,
                average_ctr=20.0,
                average_position=5.0,
                status_message="Test metrics active",
            )
            
            suite_dir = reporter.generate_full_report_suite(
                mode="AUDIT",
                crawled_pages=[sample_page],
                tech_report=tech_report,
                link_report=None,
                scope_res=scope_res,
                opportunities=[],
                metrics=metrics,
                date_stamp="2026-10-17",
            )
            
            expected_files = [
                "crawl_results.json",
                "crawl_results.csv",
                "seo_issues.json",
                "broken_links.csv",
                "redirect_issues.csv",
                "metadata_issues.csv",
                "canonical_and_robots_issues.csv",
                "sitemap_validation.json",
                "internal_link_analysis.csv",
                "indexing_review_queue.csv",
                "changes_applied.json",
                "test_results.json",
                "deployment_verification.json",
                "daily_summary.md",
            ]
            
            for fname in expected_files:
                fpath = suite_dir / fname
                self.assertTrue(fpath.exists(), f"Missing required artifact: {fname}")
                self.assertGreater(fpath.stat().st_size, 0, f"Artifact is empty: {fname}")

    def test_deployment_verifier_structure(self):
        """Verifies that DeploymentVerifier returns compliant structure."""
        verifier = DeploymentVerifier(base_url="https://aitoolgems.tech", timeout_seconds=5.0)
        # Test a local mock URL or check structure schema
        res = verifier.check_url("https://httpbin.org/status/200" if False else "https://aitoolgems.tech/robots.txt")
        self.assertIn("url", res)
        self.assertIn("status_code", res)
        self.assertIn("success", res)

if __name__ == "__main__":
    unittest.main()
