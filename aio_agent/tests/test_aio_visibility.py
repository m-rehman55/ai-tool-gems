"""Unit tests for GEO/AEO & AI Search Visibility capabilities (AGENT-08)."""

import tempfile
import unittest
from pathlib import Path

from aio_agent.ai_visibility import AICitationRecord, AIVisibilityTracker
from aio_agent.answer_readiness import AnswerReadinessEvaluator
from aio_agent.hermes_integration import AIOHermesAgent
from hermes_core.contracts import ApprovalRequirement, RiskClassification, TaskContract, TaskStatus


class TestAIOVisibilityAndReadiness(unittest.TestCase):
    def setUp(self):
        self.evaluator = AnswerReadinessEvaluator()
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)
        self.registry_file = self.tmp_path / "citations.json"
        self.tracker = AIVisibilityTracker(registry_file=self.registry_file)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_readiness_evaluator_real_tool_page(self):
        chatgpt_path = Path("tools/chatgpt/index.html")
        if chatgpt_path.exists():
            report = self.evaluator.evaluate_file(chatgpt_path)
            self.assertGreaterEqual(report.total_score, 85.0)
            self.assertEqual(report.grade, "EXCELLENT")
            self.assertEqual(len(report.criteria), 11)

    def test_readiness_evaluator_flags_thin_content(self):
        thin_html = self.tmp_path / "thin.html"
        thin_html.write_text("<html><body><p>Hello world</p></body></html>", encoding="utf-8")
        report = self.evaluator.evaluate_file(thin_html)
        self.assertLess(report.total_score, 50.0)
        self.assertEqual(report.grade, "NEEDS_WORK")
        self.assertTrue(len(report.recommendations) > 0)

    def test_visibility_tracker_anti_fabrication_rules(self):
        status = self.tracker.get_provider_status()
        # Without PROMPTWATCH_API_KEY, must report BLOCKED_PENDING_CREDENTIALS
        self.assertEqual(status["status"], "BLOCKED_PENDING_CREDENTIALS")
        self.assertIn("data/aio/citations_registry.json", status["instructions"])

    def test_record_and_compute_citations(self):
        c1 = AICitationRecord(
            citation_id="TEST-01",
            platform="Perplexity",
            query="buy ai tool in pakistan",
            target_url="https://aitoolgems.tech/tools/chatgpt/",
            brand_mentioned=True,
            is_cited=True,
            competitors_mentioned=["paktools.store"],
            country="PK",
        )
        self.tracker.record_citation(c1)
        summary = self.tracker.compute_visibility_summary()
        self.assertEqual(summary.total_queries_audited, 4)
        self.assertEqual(summary.brand_mention_rate_pct, 100.0)
        self.assertEqual(summary.citation_frequency_pct, 100.0)
        self.assertEqual(summary.top_cited_urls[0]["url"], "https://aitoolgems.tech/tools/chatgpt/")

    def test_hermes_integration_tasks(self):
        agent = AIOHermesAgent()
        task = TaskContract(
            task_id="TEST-AIO-01",
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-08-GEO-AEO",
            objective="Audit on-page answer readiness and AI search visibility",
            scope="GEO/AEO",
            input_evidence={},
            required_tools=["aio_agent"],
            expected_output={"measured_ai_visibility": "dict"},
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["Valid GEO/AEO audit"],
        )
        completed = agent.execute_task(task)
        self.assertEqual(completed.status, TaskStatus.VERIFIED)
        self.assertIn("measured_ai_visibility", completed.actual_output)
        self.assertIn("on_page_answer_readiness", completed.actual_output)
        self.assertIn("separation_enforced", completed.actual_output)


if __name__ == "__main__":
    unittest.main()
