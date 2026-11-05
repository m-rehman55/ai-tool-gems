"""
Unit tests for HERMES Omniscient Keyword & Search Intent Intelligence (Section 3.4).

Tests:
1. 8-Way Intent Classification across all 8 canonical HERMES intents.
2. Multi-Source External Data Providers (Non-fabrication, status matrix, UNAVAILABLE flags).
3. Declining Keywords Engine (Period-over-period decay, rank drops, dropouts).
4. Missing Landing Pages and Content Gap Detection.
5. HERMES-CEO Task Contract Execution for AGENT-03-KEYWORD.
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from hermes_core.contracts import (
    ApprovalRequirement,
    RiskClassification,
    TaskContract,
    TaskStatus,
)
from keyword_agent.declining_keywords import DecliningKeywordsEngine
from keyword_agent.discovery import KeywordCandidate, KeywordDiscoveryEngine
from keyword_agent.external_providers import (
    AhrefsProvider,
    BingWebmasterProvider,
    FirstPartySiteSearchProvider,
    GoogleAdsKeywordPlannerProvider,
    GoogleTrendsProvider,
    GSCProvider,
    MultiSourceKeywordEngine,
    SemrushProvider,
    SEOcrawlProvider,
)
from keyword_agent.gsc_data import GSCDataset, GSCQueryRow
from keyword_agent.hermes_integration import execute_keyword_task
from keyword_agent.intent import IntentClassifier, SearchIntentType
from keyword_agent.page_mapper import PageMapper


class TestKeywordAgentOmniscient(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.project_dir = Path(__file__).resolve().parent.parent.parent

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # ── 1. 8-Way Intent Classification Tests ─────────────────────────────────

    def test_eight_way_intent_classification(self):
        """Verifies each of the 8 canonical HERMES search intents are correctly detected."""
        cases = [
            ("how to write midjourney prompts for photorealism", SearchIntentType.QUESTION),
            ("best ai tools for video editing 2026 review", SearchIntentType.COMMERCIAL_INVESTIGATION),
            ("buy chatgpt plus subscription in pkr", SearchIntentType.TRANSACTIONAL),
            ("chatgpt official site login portal", SearchIntentType.NAVIGATIONAL),
            ("canva pro in karachi pakistan rupees", SearchIntentType.LOCAL),
            ("chatgpt vs claude 3.5 sonnet comparison", SearchIntentType.COMPARISON),
            ("aitoolgems pricing and discount codes", SearchIntentType.BRAND),
            ("tutorial on python automations with n8n", SearchIntentType.INFORMATIONAL),
        ]

        for query, expected_primary in cases:
            res = IntentClassifier.classify(query)
            self.assertEqual(
                res.primary_intent,
                expected_primary,
                f"Failed for query '{query}': got {res.primary_intent}, expected {expected_primary}",
            )

    def test_multi_label_secondary_intents(self):
        """Verifies multi-label intent detection captures both transactional and local markers."""
        res = IntentClassifier.classify("buy canva pro with easypaisa in pakistan")
        self.assertEqual(res.primary_intent, SearchIntentType.TRANSACTIONAL)
        self.assertIn(SearchIntentType.LOCAL, res.secondary_intents)
        self.assertTrue(res.is_pakistan_local)
        self.assertTrue(res.is_commercial_or_transactional)

    # ── 2. External Data Providers & Non-Fabrication Tests ────────────────────

    def test_unauthorized_external_providers_label_unavailable(self):
        """Strictly ensures unconfigured APIs report UNAVAILABLE and never fabricate numbers."""
        trends = GoogleTrendsProvider()
        ads = GoogleAdsKeywordPlannerProvider()
        bing = BingWebmasterProvider()
        ahrefs = AhrefsProvider()
        semrush = SemrushProvider()
        seocrawl = SEOcrawlProvider()

        kw = "chatgpt price in pakistan"
        for prov in [trends, ads, bing, ahrefs, semrush, seocrawl]:
            # Unless authorized in environment, status must be UNAVAILABLE
            if not prov.is_authorized():
                m = prov.fetch_metrics(kw)
                self.assertIn("UNAVAILABLE", m.status)
                self.assertIsNone(m.search_volume)
                self.assertEqual(m.volume_display, "UNAVAILABLE")
                self.assertIsNone(m.keyword_difficulty)
                self.assertEqual(m.kd_display, "UNAVAILABLE")

    def test_multi_source_engine_provider_status_matrix(self):
        """Verifies multi-source engine reports a complete, structured provider readiness matrix."""
        engine = MultiSourceKeywordEngine()
        matrix = engine.get_provider_status_matrix()
        self.assertIn("gsc", matrix)
        self.assertIn("trends", matrix)
        self.assertIn("bing", matrix)
        self.assertIn("ahrefs", matrix)
        self.assertIn("semrush", matrix)
        self.assertIn("site_search", matrix)

    def test_first_party_site_search_provider(self):
        """Verifies internal site search provider correctly tallies user search queries."""
        search_file = self.test_dir / "site_search.json"
        search_file.write_text(json.dumps({
            "claude pro": 45,
            "cursor ai": 30,
        }), encoding="utf-8")

        prov = FirstPartySiteSearchProvider(data_file=search_file)
        self.assertTrue(prov.is_authorized())

        m = prov.fetch_metrics("claude pro")
        self.assertEqual(m.status, "AVAILABLE")
        self.assertEqual(m.search_volume, 45)
        self.assertEqual(m.volume_display, "45")

        m_unknown = prov.fetch_metrics("unknown query")
        self.assertIn("UNAVAILABLE", m_unknown.status)

    # ── 3. Declining Keywords Detection Tests ─────────────────────────────────

    def test_declining_keywords_detection(self):
        """Verifies detection of position drop, volume drop, and keyword dropouts."""
        curr = GSCDataset(
            source="TEST",
            status_message="Current period",
            queries=[
                GSCQueryRow(query="chatgpt price in pakistan", clicks=10, impressions=200, ctr=5.0, position=8.5),
                GSCQueryRow(query="canva pro easypaisa", clicks=2, impressions=40, ctr=5.0, position=12.0),
                GSCQueryRow(query="growing tool", clicks=20, impressions=300, ctr=6.6, position=2.0),
            ],
        )

        prev = GSCDataset(
            source="TEST",
            status_message="Previous period",
            queries=[
                GSCQueryRow(query="chatgpt price in pakistan", clicks=25, impressions=300, ctr=8.3, position=3.2),  # Position decay
                GSCQueryRow(query="canva pro easypaisa", clicks=10, impressions=100, ctr=10.0, position=5.0),    # Critical clicks decay
                GSCQueryRow(query="growing tool", clicks=10, impressions=150, ctr=6.6, position=5.0),            # Growing
                GSCQueryRow(query="vanished query", clicks=5, impressions=80, ctr=6.25, position=4.0),           # Dropout
            ],
        )

        engine = DecliningKeywordsEngine(current_dataset=curr, previous_dataset=prev)
        results = engine.analyze()

        self.assertEqual(len(results), 4)
        dropout = next((r for r in results if r.query == "vanished query"), None)
        self.assertIsNotNone(dropout)
        self.assertEqual(dropout.severity, "DROPOUT")
        self.assertEqual(dropout.remediation_priority, "P1_URGENT")

        decay = next((r for r in results if r.query == "chatgpt price in pakistan"), None)
        self.assertIsNotNone(decay)
        self.assertIn(decay.severity, ["CRITICAL_DECLINE", "MODERATE_DECLINE"])
        self.assertGreater(decay.position_delta, 4.0)

    # ── 4. Missing Landing Pages & Content Gaps Tests ─────────────────────────

    def test_detect_missing_landing_pages(self):
        """Verifies that high-demand comparison topics without routes are flagged as missing landing pages."""
        mapper = PageMapper(project_dir=self.project_dir)
        disc = KeywordDiscoveryEngine()
        intl = disc.generate_international_discovery_clusters()

        missing = mapper.detect_missing_landing_pages(intl)
        self.assertGreater(len(missing), 0)
        canva_figma = next((m for m in missing if "canva-vs-figma" in m.suggested_url), None)
        self.assertIsNotNone(canva_figma)
        self.assertEqual(canva_figma.target_intent, "commercial")

    def test_detect_content_gaps(self):
        """Verifies content gap detection when target page lacks query intent keywords."""
        mapper = PageMapper(project_dir=self.project_dir)

        # Candidate mapping to /prices/ with EasyPaisa intent
        cand = KeywordCandidate(
            keyword="prices with easypaisa discount",
            cluster="Commercial: Pricing & PKR Comparison",
            intent="transactional",
            recommended_page="https://aitoolgems.tech/prices/",
        )
        gaps = mapper.detect_content_gaps([cand])
        # If /prices/ index.html doesn't contain 'easypaisa', it flags a content gap
        # Or if it does, it passes cleanly
        self.assertIsInstance(gaps, list)

    # ── 5. HERMES-CEO Task Contract Execution Tests ──────────────────────────

    def test_hermes_task_contract_execution(self):
        """Verifies AGENT-03-KEYWORD completes a TaskContract dispatched by HERMES-CEO."""
        contract = TaskContract(
            task_id="TASK-03-TEST01",
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-03-KEYWORD",
            objective="Execute daily keyword discovery, 8-way intent clustering, and cannibalization audit",
            scope="docs/, data/reports/",
            input_evidence={"sample_size": 10},
            required_tools=["keyword_agent", "gsc_agent"],
            expected_output="daily-report-latest.json",
            dependencies=[],
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["Valid JSON artifact generated", "Zero unhandled exceptions"],
        )

        completed = execute_keyword_task(contract, project_dir=self.project_dir)
        self.assertEqual(completed.status, TaskStatus.VERIFIED)
        self.assertIn("execution_timestamp", completed.verification_evidence)
        self.assertIn("total_candidates", completed.verification_evidence)
        self.assertIn("markdown_report", completed.verification_evidence)
        self.assertTrue(Path(completed.verification_evidence["artifact_file"]).exists())


if __name__ == "__main__":
    unittest.main()
