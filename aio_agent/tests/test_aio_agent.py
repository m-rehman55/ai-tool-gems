"""
test_aio_agent.py - Unit tests for Google AI Overviews & Grounding Agent.
Verifies:
- Extractability auditing (Single H1, quick-answer length, PKR tokens)
- Query fan-out branch satisfaction
- Machine knowledge synchronization (llms.txt)
- Grounding scoring math and tier classification
- CLI commands execution
"""

import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from aio_agent.extractability import ExtractabilityAuditor
from aio_agent.query_fanout import QueryFanOutAnalyzer
from aio_agent.llms_sync import LLMsSyncEngine
from aio_agent.grounding_scorer import GroundingScorer
from aio_agent.cli import main


class TestAIOAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.proj_dir = Path(__file__).resolve().parent.parent.parent

    def test_extractability_on_chatgpt_page(self):
        auditor = ExtractabilityAuditor()
        cg_path = self.proj_dir / "tools" / "chatgpt" / "index.html"
        self.assertTrue(cg_path.exists())

        rep = auditor.audit_file(cg_path)
        self.assertTrue(rep.has_h1)
        self.assertEqual(rep.h1_count, 1)
        self.assertTrue(rep.has_direct_answer)
        self.assertTrue(rep.has_pkr_price)
        self.assertTrue(rep.has_payment_rails)
        self.assertTrue(rep.has_warranty_info)
        self.assertTrue(rep.has_delivery_terms)
        self.assertGreaterEqual(rep.extractability_score, 85.0)

    def test_query_fanout_coverage(self):
        analyzer = QueryFanOutAnalyzer()
        guide_path = self.proj_dir / "guides" / "chatgpt-vs-claude-pakistan" / "index.html"
        self.assertTrue(guide_path.exists())

        res = analyzer.analyze_file(guide_path)
        self.assertEqual(res.coverage_percentage, 100.0)
        self.assertEqual(len(res.missing_branches), 0)
        self.assertTrue(res.branches["pricing_in_pkr"].is_satisfied)
        self.assertTrue(res.branches["domestic_payment_rails"].is_satisfied)
        self.assertTrue(res.branches["fulfillment_delivery"].is_satisfied)
        self.assertTrue(res.branches["trust_warranty"].is_satisfied)
        self.assertTrue(res.branches["comparison_use_cases"].is_satisfied)

    def test_grounding_scorer_on_live_pages(self):
        scorer = GroundingScorer(self.proj_dir)
        leo_path = self.proj_dir / "tools" / "leonardo" / "index.html"
        self.assertTrue(leo_path.exists())

        score_res = scorer.score_page(leo_path)
        self.assertGreaterEqual(score_res.total_aio_score, 80.0)
        self.assertIn(score_res.tier, ["ELITE_AIO_READY", "AIO_COMPLIANT"])

    def test_llms_sync_engine(self):
        engine = LLMsSyncEngine(self.proj_dir)
        live_guides = engine.discover_live_guides()
        live_tools = engine.discover_live_tools()

        self.assertGreaterEqual(len(live_guides), 20)
        self.assertGreaterEqual(len(live_tools), 30)

        # Execute sync
        res = engine.sync()
        self.assertGreaterEqual(res.tools_synced, 30)
        self.assertGreaterEqual(res.guides_synced, 20)

        # Check llms.txt contains newly added guides
        llms_txt = (self.proj_dir / "llms.txt").read_text(encoding="utf-8")
        self.assertIn("chatgpt-vs-claude-pakistan", llms_txt)
        self.assertIn("capcut-vs-runway-pakistan", llms_txt)

    def test_cli_execution(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            ret = main(["audit"])
        self.assertEqual(ret, 0)
        output = buf.getvalue()
        self.assertIn("[AIO AGENT] Google AI Overviews & Grounding Audit", output)
        self.assertIn("Average AIO Score", output)


if __name__ == "__main__":
    unittest.main()
