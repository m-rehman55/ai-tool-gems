"""Unit tests for Content Research & Editorial Intelligence Agent (AGENT-09)."""

import tempfile
import unittest
from pathlib import Path

from content_agent.editorial_gate import EditorialQualityGate
from content_agent.hermes_integration import ContentHermesAgent
from content_agent.queue_manager import ContentQueueManager
from content_agent.research import ArticleResearchRecord, create_research_record
from hermes_core.contracts import ApprovalRequirement, RiskClassification, TaskContract, TaskStatus


class TestContentAgent(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)
        self.queue_file = self.tmp_path / "content-queue.json"
        self.drafts_dir = self.tmp_path / "drafts"
        self.mgr = ContentQueueManager(queue_path=self.queue_file)
        self.gate = EditorialQualityGate(drafts_dir=self.drafts_dir)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_research_record_all_15_evidence_fields(self):
        rec = create_research_record(
            slug="cursor-ai-pakistan-guide",
            primary_tool="cursor",
            tool_name="Cursor AI",
            pkr_price=5500,
            primary_kw="Cursor AI Pakistan",
            secondary_kws=["Cursor price in Pakistan", "Cursor EasyPaisa", "Cursor subscription PKR"],
            doc_url="https://cursor.com",
            features=["AI autocomplete", "Multi-file editing"],
        )
        d = rec.to_dict()
        # Verify all 15 required evidence fields
        fields_15 = [
            "target_slug", "target_audience", "search_intent", "primary_keyword",
            "secondary_keywords", "competitor_research", "verified_product_facts",
            "source_references", "pricing_verification", "pakistan_relevance",
            "content_outline", "internal_link_targets", "structured_data_requirements",
            "editorial_quality_score", "originality_checks", "approved_for_publishing",
        ]
        for f in fields_15:
            self.assertIn(f, d, f"Missing required evidence field: {f}")

        # Strictly False by default
        self.assertFalse(rec.approved_for_publishing)
        is_ready, errors = rec.validate_publication_readiness()
        self.assertFalse(is_ready)
        self.assertTrue(any("POLICY_VIOLATION" in e for e in errors))

    def test_queue_manager_fail_closed_and_zero_self_approval(self):
        # 1. Unapproved candidate in queue
        self.mgr.add_proposed_candidate({
            "slug": "unapproved-guide",
            "title": "Unapproved Guide Title",
            "approved_for_publishing": False,
        })
        cand, status = self.mgr.get_next_approved_candidate(published_slugs=set())
        self.assertIsNone(cand)
        self.assertEqual(status, "NO_APPROVED_CANDIDATE")

        # 2. Add with attempted self-approval -> manager forces False
        self.mgr.add_proposed_candidate({
            "slug": "sneak-approval-guide",
            "title": "Sneak Title",
            "approved_for_publishing": True,  # Attempted bypass
        })
        cand, status = self.mgr.get_next_approved_candidate(published_slugs=set())
        self.assertIsNone(cand)  # Forced to False, so cannot publish

        # 3. Explicit human approval gate
        success, _ = self.mgr.approve_candidate("sneak-approval-guide", approved_by="Human Editor")
        self.assertTrue(success)
        cand, status = self.mgr.get_next_approved_candidate(published_slugs=set())
        self.assertIsNotNone(cand)
        self.assertEqual(cand["slug"], "sneak-approval-guide")
        self.assertEqual(status, "APPROVED_CANDIDATE_FOUND")

    def test_quality_gate_rejects_thin_and_cliche_content(self):
        # Thin content
        is_val, errors = self.gate.validate_article_html("<p>Short thin text</p>", {})
        self.assertFalse(is_val)
        self.assertTrue(any("THIN_CONTENT" in e for e in errors))

        # Generic AI filler cliches
        long_filler = " ".join(["word"] * 700) + " In today's fast-paced digital landscape we explore tools."
        is_val2, errors2 = self.gate.validate_article_html(long_filler, {})
        self.assertFalse(is_val2)
        self.assertTrue(any("AI_FILLER_DETECTED" in e for e in errors2))

    def test_quality_gate_rejects_japan_scope(self):
        long_text = " ".join(["word"] * 700) + " Pricing for customers in Tokyo Japan is 5000 JPY."
        is_val, errors = self.gate.validate_article_html(long_text, {})
        self.assertFalse(is_val)
        self.assertTrue(any("FOREIGN_SCOPE_VIOLATION" in e for e in errors))

    def test_quality_gate_approves_compliant_guide(self):
        valid_html = """
        <article>
          <h1>Cursor AI in Pakistan: Pricing & Features (2026)</h1>
          <p>Complete guide for Pakistani developers looking to buy Cursor AI subscription in Pakistan.</p>
          <p>""" + " ".join(["Verified technical code completion features across multiple repositories."] * 80) + """</p>
          <p>The verified flat subscription price is Rs. 5,500 per month without international card declines.</p>
          <p>Pakistani payment rails supported: EasyPaisa, JazzCash, SadaPay, and direct Bank IBFT transfer.</p>
          <script type="application/ld+json">{"@context":"https://schema.org","@type":"Article"}</script>
        </article>
        """
        is_val, errors = self.gate.validate_article_html(valid_html, {})
        self.assertTrue(is_val, f"Unexpected validation errors: {errors}")
        self.assertEqual(len(errors), 0)

    def test_save_unapproved_draft_on_failure(self):
        draft_path = self.gate.save_unapproved_draft("failed-gemini-guide", "<p>Draft body</p>", {}, "Gemini API Quota Exceeded")
        self.assertTrue(draft_path.exists())
        content = draft_path.read_text(encoding="utf-8")
        self.assertIn("Status: DRAFT_PENDING_REVIEW", content)
        self.assertIn("Self-Approval: BLOCKED", content)

    def test_hermes_integration_tasks(self):
        agent = ContentHermesAgent()
        task = TaskContract(
            task_id="TEST-CONTENT-01",
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-09-CONTENT",
            objective="Audit content queue and verify zero self-approval policy",
            scope="Content Queue",
            input_evidence={},
            required_tools=["content_queue_manager"],
            expected_output={"queue": "dict"},
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["Valid queue audit"],
        )
        completed = agent.execute_task(task)
        self.assertEqual(completed.status, TaskStatus.VERIFIED)
        self.assertTrue(completed.actual_output["self_approval_prevented"])
        self.assertGreater(completed.actual_output["total_queue_items"], 0)


if __name__ == "__main__":
    unittest.main()
