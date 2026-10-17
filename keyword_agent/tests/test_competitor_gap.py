"""
Unit tests for competitor gap analysis engine.
Verifies:
- Competitor URL parsing and topic classification
- Head-to-head overlap mapping to existing AIToolGems routes
- High-value gap identification
- Markdown report generation
"""

import unittest
from pathlib import Path
import tempfile
import shutil

from keyword_agent.competitor_gap import CompetitorGapAnalyzer, CompetitorGapReport


class TestCompetitorGap(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.proj_dir = Path(__file__).resolve().parent.parent.parent

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_competitor_gap_analysis_execution(self):
        analyzer = CompetitorGapAnalyzer(project_dir=self.proj_dir)
        report = analyzer.analyze_gaps()

        self.assertEqual(report.competitor_domain, "aitoolspak.tech")
        self.assertGreaterEqual(report.total_competitor_urls, 100)
        self.assertGreater(report.direct_catalog_overlaps, 15)
        self.assertGreater(report.uncovered_high_value_gaps, 5)

        # Check overlapping product
        chatgpt_item = next((g for g in report.gap_matrix if "chatgpt" in g.primary_topic.lower()), None)
        self.assertIsNotNone(chatgpt_item)
        self.assertEqual(chatgpt_item.gap_type, "EXISTING_STRENGTH")
        self.assertIn("tools/chatgpt", chatgpt_item.matching_aitoolgems_url)

        # Check uncovered gap
        grammarly_item = next((g for g in report.gap_matrix if "grammarly" in g.primary_topic.lower()), None)
        self.assertIsNotNone(grammarly_item)
        self.assertEqual(grammarly_item.gap_type, "OPPORTUNITY_TO_DOMINATE")

    def test_markdown_report_generation(self):
        analyzer = CompetitorGapAnalyzer(project_dir=self.proj_dir)
        report = analyzer.analyze_gaps()
        out_file = self.test_dir / "COMPETITOR_GAP.md"
        analyzer.export_markdown_report(report, out_file)

        self.assertTrue(out_file.exists())
        content = out_file.read_text(encoding="utf-8")
        self.assertIn("aitoolspak.tech", content)
        self.assertIn("omiijutt120", content)
        self.assertIn("Direct Overlap Domination Matrix", content)


if __name__ == "__main__":
    unittest.main()
