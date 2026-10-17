"""
test_research_learning_intelligence.py
Unit & regression tests for:
1. SearchResearchEngine (Official Google Search Central & Essentials mapping)
2. LearningFeedbackLoop (Self-improvement & Safety Immutability Guard)
3. SearchIntelligenceEngine (GSC CTR Opportunities, AI Search & Cadence Reviews)
"""

import unittest
from pathlib import Path
import tempfile
import json

from agent.search_research import SearchResearchEngine, GuidanceSource, ResearchFinding
from agent.learning_loop import LearningFeedbackLoop, RemediationHistory, PROTECTED_GUARD_RULES
from agent.search_intelligence import SearchIntelligenceEngine, CTROpportunity, AISearchAuditResult


class DummyQuery:
    def __init__(self, query: str, impressions: int, clicks: int, ctr: float, position: float):
        self.query = query
        self.impressions = impressions
        self.clicks = clicks
        self.ctr = ctr
        self.position = position


class TestResearchLearningIntelligence(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        # Create minimal required mock structure
        (self.base_dir / "llms.txt").write_text("# Mock llms.txt\n" + ("content " * 100), encoding="utf-8")
        (self.base_dir / "llms-full.txt").write_text("# Mock llms-full.txt\n" + ("full " * 250), encoding="utf-8")
        tools_dir = self.base_dir / "tools" / "test-tool"
        tools_dir.mkdir(parents=True, exist_ok=True)
        (tools_dir / "index.html").write_text('<html><script type="application/ld+json">{"@type": "Product"}</script></html>', encoding="utf-8")

    def tearDown(self):
        self.temp_dir.cleanup()

    # --- 1. Official Google Search Research Tests ---
    def test_search_research_guidance_mapping(self):
        engine = SearchResearchEngine()
        self.assertGreater(len(engine.sources), 3)

        # Test mapping of technical issue to official Google Search Central
        finding = engine.map_issue_to_guidance("STATUS_CODE")
        self.assertIsNotNone(finding)
        self.assertEqual(finding.source_id, "GOOGLE_SEARCH_CENTRAL")
        self.assertEqual(finding.authority, "OFFICIAL_REQUIREMENT")
        self.assertIn("developers.google.com/search/docs", finding.source_url)

        # Test mapping of title issue to Google Search Essentials
        title_finding = engine.map_issue_to_guidance("TITLE")
        self.assertIsNotNone(title_finding)
        self.assertEqual(title_finding.source_id, "GOOGLE_SEARCH_ESSENTIALS")

        # Test mapping of AI Search / Schema to Google AI Optimization Guide
        ai_finding = engine.map_issue_to_guidance("SCHEMA_PRODUCT")
        self.assertIsNotNone(ai_finding)
        self.assertEqual(ai_finding.source_id, "GOOGLE_AI_OPTIMIZATION_GUIDE")
        self.assertEqual(ai_finding.authority, "OFFICIAL_AI_SEARCH_GUIDANCE")

    def test_record_research_changelog(self):
        engine = SearchResearchEngine(base_dir=self.base_dir)
        changelog = engine.record_research_changelog_entry(
            date_str="2026-10-17",
            headline="Google Search Central Documentation verified",
            details="Confirmed compliance with canonicalization guidelines",
            source_id="GOOGLE_SEARCH_CENTRAL",
        )
        self.assertTrue(changelog.exists())
        content = changelog.read_text(encoding="utf-8")
        self.assertIn("GOOGLE_SEARCH_CENTRAL", content)
        self.assertIn("canonicalization guidelines", content)

    # --- 2. Deterministic Learning Feedback Loop Tests ---
    def test_learning_loop_tracking_and_confidence(self):
        loop = LearningFeedbackLoop(base_dir=self.base_dir)
        initial_confidence = loop.get_confidence_multiplier("TECHNICAL_P0")
        self.assertGreaterEqual(initial_confidence, 0.9)

        # Record a run with a successful fix
        loop.record_run(
            issues_detected=[{"check_type": "STATUS_CODE"}],
            fixes_applied=[{"category": "TECHNICAL_P0"}],
            reverted_count=0,
        )
        self.assertEqual(loop.history.total_runs, 2)
        self.assertEqual(loop.history.issue_recurrence.get("STATUS_CODE"), 1)

    def test_learning_loop_safety_immutability(self):
        loop = LearningFeedbackLoop(base_dir=self.base_dir)

        # Safe changes must pass
        safe_changes = ["Update meta description in index.html", "Fix internal anchor in blog.html"]
        self.assertTrue(loop.verify_safety_immutability(safe_changes))

        # Attempts to touch protected firewall or tokens MUST BE BLOCKED
        for protected in ["safety_firewall.py", "scope_guard.py", "GSC_CLIENT_SECRET", "TELEGRAM_BOT_TOKEN", "price_freeze"]:
            unsafe_changes = [f"Modify {protected} to bypass validation"]
            self.assertFalse(
                loop.verify_safety_immutability(unsafe_changes),
                f"Failed to block mutation of protected rule: {protected}",
            )

    # --- 3. Search Intelligence, AI Search & Cadence Tests ---
    def test_ctr_opportunity_mining(self):
        intelligence = SearchIntelligenceEngine(base_dir=self.base_dir)
        queries = [
            DummyQuery("chatgpt plus pakistan", impressions=120, clicks=2, ctr=1.6, position=5.2),
            DummyQuery("canva pro price pkr", impressions=4, clicks=1, ctr=25.0, position=2.0),
        ]
        opps = intelligence.analyze_gsc_opportunities(queries)
        self.assertEqual(len(opps), 1)
        self.assertEqual(opps[0].query, "chatgpt plus pakistan")
        self.assertIn("Refine title/meta description", opps[0].recommended_action)

    def test_ai_search_readiness_audit(self):
        intelligence = SearchIntelligenceEngine(base_dir=self.base_dir)
        audit = intelligence.audit_ai_search_readiness()
        self.assertTrue(audit.llms_txt_present)
        self.assertTrue(audit.llms_full_txt_present)
        self.assertGreaterEqual(audit.ai_readiness_score, 50)

    def test_cadence_review_generation(self):
        intelligence = SearchIntelligenceEngine(base_dir=self.base_dir)
        queries = [DummyQuery("claude ai pakistan", 50, 1, 2.0, 4.5)]
        
        # Test weekly review creation
        weekly_file = intelligence.generate_weekly_consolidated_review(
            crawled_count=60,
            issues_count=0,
            gsc_queries=queries,
            date_str="2026-10-17",
        )
        self.assertTrue(weekly_file.exists())
        self.assertIn("AIToolGems Weekly SEO & GEO Consolidated Review", weekly_file.read_text(encoding="utf-8"))

        # Test monthly roadmap creation
        monthly_file = intelligence.generate_monthly_roadmap(date_str="2026-10-17")
        self.assertTrue(monthly_file.exists())
        self.assertIn("AIToolGems Monthly SEO Strategic Roadmap", monthly_file.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
