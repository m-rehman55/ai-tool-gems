"""
Comprehensive Unit Tests for GSC Intelligence Agent.
Covers performance analytics, Pakistan filtering, brand separation,
cannibalization, inspection parsing, and safe action execution.
"""

import unittest
from gsc_agent.performance import GSCPerformanceAnalyzer
from gsc_agent.inspection import GSCInspectionManager, InspectionResultRecord
from gsc_agent.opportunities import GSCOpportunityEngine, GSCOpportunity
from gsc_agent.actions import GSCActionExecutor


class TestGSCAgent(unittest.TestCase):

    def setUp(self):
        self.analyzer = GSCPerformanceAnalyzer()
        self.opportunity_engine = GSCOpportunityEngine(self.analyzer)
        self.action_executor = GSCActionExecutor()

    def test_performance_summarizer_math(self):
        sample_rows = [
            {"keys": ["chatgpt plus price in pakistan", "https://aitoolgems.tech/tools/chatgpt/"], "clicks": 10, "impressions": 100, "position": 2.5},
            {"keys": ["canva pro pakistan", "https://aitoolgems.tech/tools/canva/"], "clicks": 5, "impressions": 100, "position": 4.5},
        ]
        summary = self.analyzer.summarize_dataset(sample_rows)
        self.assertEqual(summary.total_clicks, 15)
        self.assertEqual(summary.total_impressions, 200)
        self.assertEqual(summary.average_ctr, 7.5)  # 15 / 200 * 100
        self.assertEqual(summary.average_position, 3.5)  # (2.5*100 + 4.5*100) / 200
        self.assertEqual(summary.query_count, 2)
        self.assertEqual(summary.page_count, 2)

    def test_brand_vs_non_brand_segmentation(self):
        rows = [
            {"keys": ["ai tool gems chatgpt", "https://aitoolgems.tech/tools/chatgpt/"], "clicks": 2, "impressions": 20},
            {"keys": ["cheap ai tools pakistan", "https://aitoolgems.tech/"], "clicks": 8, "impressions": 150},
        ]
        split = self.analyzer.segment_brand_vs_non_brand(rows)
        self.assertEqual(split["brand"]["rows_count"], 1)
        self.assertEqual(split["non_brand"]["rows_count"], 1)
        self.assertEqual(split["brand"]["sample_queries"], ["ai tool gems chatgpt"])

    def test_high_impression_low_ctr_detection(self):
        rows = [
            {"keys": ["buy midjourney in pakistan", "https://aitoolgems.tech/tools/midjourney/"], "clicks": 1, "impressions": 200, "position": 3.2},
            {"keys": ["chatgpt login", "https://aitoolgems.tech/tools/chatgpt/"], "clicks": 30, "impressions": 100, "position": 1.1},
        ]
        opps = self.analyzer.detect_high_impression_low_ctr(rows, min_impressions=50, max_ctr_threshold=2.0)
        self.assertEqual(len(opps), 1)
        self.assertEqual(opps[0]["query"], "buy midjourney in pakistan")
        self.assertTrue(opps[0]["is_commercial"])

    def test_striking_distance_ranking_detection(self):
        rows = [
            {"keys": ["claude pro price pakistan", "https://aitoolgems.tech/tools/claude/"], "clicks": 3, "impressions": 80, "position": 6.8},
            {"keys": ["top ai video generator", "https://aitoolgems.tech/guides/video/"], "clicks": 50, "impressions": 500, "position": 1.5},
            {"keys": ["irrelevant deep search", "https://aitoolgems.tech/"], "clicks": 0, "impressions": 5, "position": 45.0},
        ]
        striking = self.analyzer.detect_striking_distance_queries(rows, min_position=4.0, max_position=30.0, min_impressions=10)
        self.assertEqual(len(striking), 1)
        self.assertEqual(striking[0]["query"], "claude pro price pakistan")
        self.assertEqual(striking[0]["current_position"], 6.8)

    def test_query_cannibalization_detection(self):
        rows = [
            {"keys": ["cursor ai pakistan", "https://aitoolgems.tech/tools/cursor/"], "clicks": 5, "impressions": 60, "position": 3.1},
            {"keys": ["cursor ai pakistan", "https://aitoolgems.tech/guides/cursor-ai-pakistan/"], "clicks": 2, "impressions": 40, "position": 5.4},
        ]
        cannibalized = self.analyzer.detect_query_cannibalization(rows, min_query_impressions=20)
        self.assertEqual(len(cannibalized), 1)
        self.assertEqual(cannibalized[0].query, "cursor ai pakistan")
        self.assertEqual(cannibalized[0].total_impressions, 100)
        self.assertEqual(len(cannibalized[0].competing_pages), 2)

    def test_url_inspection_response_parsing(self):
        mock_raw = {
            "indexStatusResult": {
                "verdict": "PASS",
                "coverageState": "Submitted and indexed",
                "indexingState": "INDEXING_ALLOWED",
                "robotsTxtState": "ALLOWED",
                "pageFetchState": "SUCCESSFUL",
                "googleCanonical": "https://aitoolgems.tech/tools/chatgpt/",
                "userCanonical": "https://aitoolgems.tech/tools/chatgpt/",
                "lastCrawlTime": "2026-11-02T09:52:31Z",
                "crawledAs": "MOBILE"
            },
            "richResultsResult": {
                "verdict": "PASS",
                "detectedItems": [{"richResultType": "Product snippets"}]
            }
        }
        # Fake client for test parser
        class FakeClient:
            base_dir = "."
        manager = GSCInspectionManager(FakeClient(), cache_path="scratch/dummy_cache.json")
        rec = manager.parse_inspection_response("https://aitoolgems.tech/tools/chatgpt/", mock_raw)
        self.assertTrue(rec.is_indexed)
        self.assertFalse(rec.canonical_mismatch)
        self.assertEqual(rec.coverage_state, "Submitted and indexed")
        self.assertEqual(rec.rich_results_items, ["Product snippets"])
        self.assertFalse(rec.requires_remediation)

    def test_canonical_mismatch_triggers_remediation(self):
        mock_raw = {
            "indexStatusResult": {
                "verdict": "PASS",
                "coverageState": "Indexed, not submitted in sitemap",
                "indexingState": "INDEXING_ALLOWED",
                "robotsTxtState": "ALLOWED",
                "pageFetchState": "SUCCESSFUL",
                "googleCanonical": "https://aitoolgems.tech/tools/chatgpt/",
                "userCanonical": "https://aitoolgems.tech/tools/old-chatgpt/",
            }
        }
        class FakeClient:
            base_dir = "."
        manager = GSCInspectionManager(FakeClient(), cache_path="scratch/dummy_cache.json")
        rec = manager.parse_inspection_response("https://aitoolgems.tech/tools/old-chatgpt/", mock_raw)
        self.assertTrue(rec.canonical_mismatch)
        self.assertTrue(rec.requires_remediation)

    def test_opportunity_engine_generates_valid_proposals(self):
        rows = [
            {"keys": ["canva pro price pakistan", "https://aitoolgems.tech/tools/canva/"], "clicks": 2, "impressions": 120, "position": 5.5},
        ]
        opps = self.opportunity_engine.generate_opportunities_from_performance(rows)
        self.assertTrue(len(opps) >= 1)
        patch = self.opportunity_engine.prepare_pull_request_patch_draft(opps[0])
        self.assertTrue(patch["branch_name"].startswith("gsc-opt/"))
        self.assertIn("canva pro price pakistan", patch["pr_body"])

    def test_search_console_removal_permanently_requires_human_approval(self):
        removal_plan = self.action_executor.request_temporary_url_removal("https://aitoolgems.tech/test", "Decommissioned")
        self.assertEqual(removal_plan.approval_tier, "HUMAN_EXPLICIT_REQUIRED")
        self.assertIn("CRITICAL OPERATION", removal_plan.notes)


if __name__ == "__main__":
    unittest.main()
