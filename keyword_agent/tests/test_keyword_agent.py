"""
Unit test suite for keyword_agent.
Tests:
- GSC Data Engine (CSV parsing, CTR normalization, historical snapshot management)
- RE2 Regex Engine (validation, lookahead blocking, backreference blocking, matching)
- Keyword Discovery (intent classification, cluster assignment, opportunity scoring)
- Page Mapper (route discovery, best URL matching, cannibalization collision detection)
- Content Optimizer (live HTML extraction, AEO answer formatting, verified link checking)
- Safe Autonomy Firewall (safe auto actions vs locked approval gate)
"""

import unittest
from pathlib import Path
import tempfile
import shutil

from keyword_agent.gsc_data import GSCDataEngine, GSCQueryRow, GSCDataset
from keyword_agent.regex_engine import RE2Validator, GSCFilterLibrary, GSCFilterDefinition
from keyword_agent.discovery import KeywordDiscoveryEngine, KeywordCandidate
from keyword_agent.page_mapper import PageMapper, PageMappingResult
from keyword_agent.content_optimizer import ContentOptimizer
from keyword_agent.safe_executor import SafeExecutor
from keyword_agent.reporting import KeywordReportGenerator


class TestKeywordAgent(unittest.TestCase):

    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.exports_dir = self.test_dir / "exports"
        self.history_dir = self.test_dir / "history"
        self.reports_dir = self.test_dir / "reports"
        self.docs_dir = self.test_dir / "docs"
        for d in [self.exports_dir, self.history_dir, self.reports_dir, self.docs_dir]:
            d.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # ── GSC Data Engine Tests ──────────────────────────────────────────────────

    def test_gsc_csv_parsing(self):
        csv_file = self.exports_dir / "Queries.csv"
        csv_file.write_text(
            "Top queries,Clicks,Impressions,CTR,Position\n"
            "chatgpt price in pakistan,25,500,5.0%,2.1\n"
            "buy canva pro easypaisa,10,120,8.33%,4.5\n"
            "cursor ai pro,2,80,2.5%,11.2\n",
            encoding="utf-8",
        )

        engine = GSCDataEngine(self.exports_dir, self.history_dir, auto_extract=False)
        dataset = engine.load_dataset()

        self.assertEqual(dataset.source, "MANUAL_EXPORT")
        self.assertEqual(len(dataset.queries), 3)
        self.assertEqual(dataset.total_clicks, 37)
        self.assertEqual(dataset.total_impressions, 700)
        self.assertEqual(dataset.queries[0].query, "chatgpt price in pakistan")
        self.assertEqual(dataset.queries[0].clicks, 25)
        self.assertEqual(dataset.queries[0].ctr, 5.0)
        self.assertEqual(dataset.queries[0].position, 2.1)

    def test_gsc_empty_graceful_handling(self):
        engine = GSCDataEngine(self.exports_dir, self.history_dir, auto_extract=False)
        dataset = engine.load_dataset()
        self.assertEqual(dataset.source, "NO_DATA")
        self.assertIn("Google Search Console data unavailable", dataset.status_message)
        self.assertEqual(dataset.total_clicks, 0)

    def test_gsc_snapshot_saving_and_restoring(self):
        engine = GSCDataEngine(self.exports_dir, self.history_dir, auto_extract=False)
        dataset = GSCDataset(
            source="MANUAL_EXPORT",
            status_message="Test run",
            queries=[GSCQueryRow(query="test query", clicks=5, impressions=100, ctr=5.0, position=3.2)],
            total_clicks=5,
            total_impressions=100,
            average_ctr=5.0,
            average_position=3.2,
        )
        engine.save_historical_snapshot(dataset)

        # Restore from history
        restored = engine.get_latest_historical_snapshot()
        self.assertIsNotNone(restored)
        self.assertEqual(restored.total_clicks, 5)
        self.assertEqual(len(restored.queries), 1)

    # ── RE2 Regex Engine Tests ────────────────────────────────────────────────

    def test_re2_validator_accepts_valid_syntax(self):
        valid_patterns = [
            r"(?i)(chatgpt|canva|figma)",
            r"(?i)\b(buy|price|cost)\b",
            r"^https?://aitoolgems\.tech/tools/",
            r"(?i)^(how|what|why)\b",
        ]
        for pat in valid_patterns:
            res = RE2Validator.validate(pat)
            self.assertTrue(res.is_valid_re2, f"Expected valid RE2: {pat}")

    def test_re2_validator_blocks_unsupported_features(self):
        # Lookahead
        res1 = RE2Validator.validate(r"chatgpt(?= plus)")
        self.assertFalse(res1.is_valid_re2)
        self.assertTrue(any("Lookahead" in e for e in res1.unsupported_features))

        # Lookbehind
        res2 = RE2Validator.validate(r"(?<=buy )canva")
        self.assertFalse(res2.is_valid_re2)
        self.assertTrue(any("Lookbehind" in e for e in res2.unsupported_features))

        # Backreference
        res3 = RE2Validator.validate(r"(ai) tool \1")
        self.assertFalse(res3.is_valid_re2)
        self.assertTrue(any("Backreference" in e for e in res3.unsupported_features))

    def test_core_filters_all_re2_compliant(self):
        lib = GSCFilterLibrary()
        filters = lib.get_core_filters()
        self.assertGreaterEqual(len(filters), 10)
        for f in filters:
            self.assertTrue(f.is_re2_validated, f"Filter {f.name} failed RE2 validation: {f.regex}")

    def test_filter_matching_behavior(self):
        lib = GSCFilterLibrary()
        filters = {f.name: f for f in lib.get_core_filters()}

        # Test Pakistan Intent filter
        pk_filter = filters["Pakistan & Local Payment Intent"]
        matched, non_matched = lib.test_filter(
            pk_filter,
            ["chatgpt price in pakistan", "buy canva easypaisa", "midjourney pkr", "what is quantum computing"]
        )
        self.assertIn("chatgpt price in pakistan", matched)
        self.assertIn("buy canva easypaisa", matched)
        self.assertIn("midjourney pkr", matched)
        self.assertIn("what is quantum computing", non_matched)

        # Test Non-Brand Filter (Doesn't match regex)
        nb_filter = filters["Non-Brand Organic Queries"]
        matched_nb, non_matched_nb = lib.test_filter(
            nb_filter,
            ["ai tool gems login", "aitoolgems reviews", "canva pro price pakistan"]
        )
        self.assertIn("canva pro price pakistan", matched_nb)
        self.assertIn("ai tool gems login", non_matched_nb)

    # ── Keyword Discovery & Opportunity Scoring Tests ────────────────────────

    def test_intent_classification(self):
        disc = KeywordDiscoveryEngine()
        self.assertEqual(disc.classify_intent("buy chatgpt plus pkr"), "transactional")
        self.assertEqual(disc.classify_intent("chatgpt vs claude 3.5 sonnet"), "commercial")
        self.assertEqual(disc.classify_intent("how to use midjourney for beginners"), "informational")

    def test_cluster_assignment(self):
        disc = KeywordDiscoveryEngine()
        self.assertEqual(disc.assign_cluster("canva pro lifetime subscription"), "Tool: Canva")
        self.assertEqual(disc.assign_cluster("elevenlabs urdu voices"), "Tool: Elevenlabs")
        self.assertEqual(disc.assign_cluster("best ai tools price in pakistan"), "Commercial: Pricing & PKR Comparison")

    def test_opportunity_scoring_math(self):
        disc = KeywordDiscoveryEngine()
        # High impression, striking distance, transactional, Pakistan intent
        score, breakdown = disc.calculate_opportunity_score(
            keyword="chatgpt price in pakistan",
            impressions=60,
            clicks=2,
            ctr=3.3,
            position=6.2,
            intent="transactional",
            is_pakistan=True,
        )
        self.assertGreaterEqual(score, 80.0)
        self.assertEqual(breakdown["relevance"], 25.0)
        self.assertEqual(breakdown["demand_signal"], 25.0)
        self.assertEqual(breakdown["commercial_value"], 20.0)
        self.assertEqual(breakdown["striking_distance"], 10.0)

    # ── Page Mapping & Cannibalization Tests ─────────────────────────────────

    def test_page_mapping_and_collision_detection(self):
        proj_dir = Path(__file__).resolve().parent.parent.parent
        mapper = PageMapper(project_dir=proj_dir)

        # Chatgpt query must map to chatgpt tool page
        res = mapper.find_best_url("chatgpt plus subscription price in pakistan")
        self.assertEqual(res.best_url, "https://aitoolgems.tech/tools/chatgpt/")
        self.assertEqual(res.action_type, "OPTIMIZE_EXISTING")

        # Generic price comparison query must map to prices page
        res_price = mapper.find_best_url("compare ai tools prices in rupees")
        self.assertEqual(res_price.best_url, "https://aitoolgems.tech/prices/")

        # Detect collision if two mappings target same normalized query
        m1 = PageMappingResult(
            keyword="buy canva pro pakistan",
            intent="transactional",
            best_url="https://aitoolgems.tech/tools/canva/",
            relative_path="tools/canva/index.html",
            mapping_confidence=0.9,
            action_type="OPTIMIZE_EXISTING",
        )
        m2 = PageMappingResult(
            keyword="canva pro buy in pakistan",
            intent="transactional",
            best_url="https://aitoolgems.tech/guides/canva-pro/",
            relative_path="guides/canva-pro/index.html",
            mapping_confidence=0.8,
            action_type="OPTIMIZE_EXISTING",
        )
        collisions = mapper.detect_cannibalization([m1, m2])
        self.assertEqual(len(collisions), 1)
        self.assertIn("https://aitoolgems.tech/tools/canva/", collisions[0].competing_urls)
        self.assertIn("https://aitoolgems.tech/guides/canva-pro/", collisions[0].competing_urls)

    def test_intent_mapping_transactional_vs_comparison(self):
        """Verifies transactional purchase queries map to tool product pages while vs queries map to comparison guides."""
        proj_dir = Path(__file__).resolve().parent.parent.parent
        mapper = PageMapper(project_dir=proj_dir)

        # Transactional & price queries
        r_cg = mapper.find_best_url("buy chatgpt plus in pakistan easypaisa", "transactional")
        self.assertEqual(r_cg.best_url, "https://aitoolgems.tech/tools/chatgpt/")
        self.assertEqual(r_cg.action_type, "OPTIMIZE_EXISTING")

        r_canva = mapper.find_best_url("canva pro price in pakistan jazzcash", "transactional")
        self.assertEqual(r_canva.best_url, "https://aitoolgems.tech/tools/canva/")

        r_li = mapper.find_best_url("linkedin premium price in pakistan", "transactional")
        self.assertEqual(r_li.best_url, "https://aitoolgems.tech/tools/linkedin/")

        r_cap = mapper.find_best_url("capcut pro price in pakistan", "transactional")
        self.assertEqual(r_cap.best_url, "https://aitoolgems.tech/tools/capcut/")

        # Local comparison query maps to Pakistan comparison guide
        r_vs = mapper.find_best_url("chatgpt vs gemini price in pakistan", "commercial")
        self.assertEqual(r_vs.best_url, "https://aitoolgems.tech/guides/chatgpt-vs-gemini-pakistan/")
        self.assertEqual(r_vs.action_type, "OPTIMIZE_EXISTING")

    def test_brand_and_tool_name_aliases_mapping(self):
        """Verifies that common tool aliases (illustrator, photoshop, chat gpt, nord vpn) correctly map to product pages."""
        proj_dir = Path(__file__).resolve().parent.parent.parent
        mapper = PageMapper(project_dir=proj_dir)

        r_ill = mapper.find_best_url("illustrator price in pakistan", "transactional")
        self.assertEqual(r_ill.best_url, "https://aitoolgems.tech/tools/adobe/")
        self.assertIn("adobe", r_ill.rational_justification)

        r_ps = mapper.find_best_url("photoshop subscription in rupees", "transactional")
        self.assertEqual(r_ps.best_url, "https://aitoolgems.tech/tools/adobe/")

        r_cg_space = mapper.find_best_url("chat gpt pro price in pakistan", "transactional")
        self.assertEqual(r_cg_space.best_url, "https://aitoolgems.tech/tools/chatgpt/")

        r_vpn_space = mapper.find_best_url("nord vpn price in pakistan", "transactional")
        self.assertEqual(r_vpn_space.best_url, "https://aitoolgems.tech/tools/nordvpn/")

    def test_global_vs_pakistan_comparison_mapping(self):
        """Verifies that global comparison queries do NOT map to -pakistan guides and are flagged for monitoring."""
        proj_dir = Path(__file__).resolve().parent.parent.parent
        mapper = PageMapper(project_dir=proj_dir)

        # Global query without Pakistan intent
        r_global = mapper.find_best_url("canva vs figma comparison", "commercial")
        self.assertEqual(r_global.best_url, "https://aitoolgems.tech/tools/canva/")
        self.assertEqual(r_global.action_type, "MONITOR")
        self.assertNotIn("-pakistan", r_global.best_url)

        # Pakistan-specific comparison query
        r_pk = mapper.find_best_url("canva vs figma price in pakistan", "commercial")
        self.assertEqual(r_pk.best_url, "https://aitoolgems.tech/guides/canva-vs-figma-pakistan/")
        self.assertEqual(r_pk.action_type, "OPTIMIZE_EXISTING")

    def test_ambiguous_multi_tool_query_detection(self):
        """Verifies that queries referencing multiple tools without comparison intent are flagged for MANUAL_REVIEW."""
        proj_dir = Path(__file__).resolve().parent.parent.parent
        mapper = PageMapper(project_dir=proj_dir)

        r_ambig = mapper.find_best_url("chatgpt canva bundle offer", "transactional")
        self.assertEqual(r_ambig.action_type, "MANUAL_REVIEW")
        self.assertGreaterEqual(len(r_ambig.competing_urls), 2)
        self.assertIn("https://aitoolgems.tech/tools/chatgpt/", r_ambig.competing_urls)
        self.assertIn("https://aitoolgems.tech/tools/canva/", r_ambig.competing_urls)

    def test_phase_6b1_realistic_keyword_mappings_and_alias_hardening(self):
        """Phase 6B.1: Verifies realistic keyword mappings, word boundaries, alias variations, and multi-tool routing."""
        proj_dir = Path(__file__).resolve().parent.parent.parent
        mapper = PageMapper(project_dir=proj_dir)

        # 1. Transactional & tool aliases
        cases = [
            ("buy chatgpt plus in pakistan easypaisa", "https://aitoolgems.tech/tools/chatgpt/", "OPTIMIZE_EXISTING", 0.95),
            ("chatgpt pro price in pakistan", "https://aitoolgems.tech/tools/chatgpt/", "OPTIMIZE_EXISTING", 0.90),
            ("adobe illustrator price in pakistan", "https://aitoolgems.tech/tools/adobe/", "OPTIMIZE_EXISTING", 0.90),
            ("photoshop price in pakistan", "https://aitoolgems.tech/tools/adobe/", "OPTIMIZE_EXISTING", 0.90),
            ("capcut pro price in pakistan", "https://aitoolgems.tech/tools/capcut/", "OPTIMIZE_EXISTING", 0.95),
            ("nord vpn price in pakistan", "https://aitoolgems.tech/tools/nordvpn/", "OPTIMIZE_EXISTING", 0.95),
            ("windows 11 key price", "https://aitoolgems.tech/tools/windows/", "OPTIMIZE_EXISTING", 0.95),
            ("buy chat-gpt in pakistan", "https://aitoolgems.tech/tools/chatgpt/", "OPTIMIZE_EXISTING", 0.95),
            ("nord-vpn price in pakistan", "https://aitoolgems.tech/tools/nordvpn/", "OPTIMIZE_EXISTING", 0.95),
            ("chatgpt's best plan", "https://aitoolgems.tech/tools/chatgpt/", "OPTIMIZE_EXISTING", 0.95),
            ("ai tools for students", "https://aitoolgems.tech/guides/students/", "OPTIMIZE_EXISTING", 0.92),
            ("ai tools for developers", "https://aitoolgems.tech/guides/developers/", "OPTIMIZE_EXISTING", 0.92),
        ]
        for query, expected_url, expected_action, min_conf in cases:
            res = mapper.find_best_url(query)
            self.assertEqual(res.best_url, expected_url, f"Failed URL for query: {query}")
            self.assertEqual(res.action_type, expected_action, f"Failed action for query: {query}")
            self.assertGreaterEqual(res.mapping_confidence, min_conf, f"Low confidence for query: {query}")

        # Assert specific bundle inclusion explanation for Adobe subapps
        r_adobe_sub = mapper.find_best_url("adobe illustrator price in pakistan")
        self.assertIn("Bundle inclusion match", r_adobe_sub.rational_justification)
        self.assertIn("Creative Cloud All Apps", r_adobe_sub.rational_justification)

        # Assert tier distinction explanation for ChatGPT Pro
        r_cg_pro = mapper.find_best_url("chatgpt pro price in pakistan")
        self.assertIn("Plan distinction match", r_cg_pro.rational_justification)
        self.assertIn("Pro is not stocked", r_cg_pro.rational_justification)

        # 2. Multi-tool global comparisons
        r_3tool = mapper.find_best_url("chatgpt vs claude vs gemini", "commercial")
        self.assertEqual(r_3tool.best_url, "https://aitoolgems.tech/tools/chatgpt/")
        self.assertEqual(r_3tool.action_type, "MONITOR")
        self.assertEqual(r_3tool.mapping_confidence, 0.80)
        self.assertEqual(len(r_3tool.competing_urls), 3)
        self.assertIn("https://aitoolgems.tech/tools/chatgpt/", r_3tool.competing_urls)
        self.assertIn("https://aitoolgems.tech/tools/claude/", r_3tool.competing_urls)
        self.assertIn("https://aitoolgems.tech/tools/gemini/", r_3tool.competing_urls)

        # 3. Multi-tool ambiguous query (ordering preservation)
        r_bundle = mapper.find_best_url("chatgpt canva bundle price", "transactional")
        self.assertEqual(r_bundle.best_url, "https://aitoolgems.tech/tools/chatgpt/")
        self.assertEqual(r_bundle.action_type, "MANUAL_REVIEW")
        self.assertEqual(r_bundle.mapping_confidence, 0.75)
        self.assertEqual(len(r_bundle.competing_urls), 2)
        self.assertEqual(r_bundle.competing_urls[0], "https://aitoolgems.tech/tools/chatgpt/")
        self.assertEqual(r_bundle.competing_urls[1], "https://aitoolgems.tech/tools/canva/")

        # 4. Word boundary negative tests (avoid false-positive substrings)
        r_canvas = mapper.find_best_url("html canvas drawing tutorial", "informational")
        self.assertNotEqual(r_canvas.best_url, "https://aitoolgems.tech/tools/canva/")

        r_precursor = mapper.find_best_url("precursor chemical list", "informational")
        self.assertNotEqual(r_precursor.best_url, "https://aitoolgems.tech/tools/cursor/")

    # ── Content Optimizer Tests ──────────────────────────────────────────────

    def test_content_optimizer_live_extraction(self):
        proj_dir = Path(__file__).resolve().parent.parent.parent
        optimizer = ContentOptimizer(project_dir=proj_dir)
        brief = optimizer.generate_optimization_brief(
            url="https://aitoolgems.tech/tools/chatgpt/",
            relative_path="tools/chatgpt/index.html",
            primary_query="chatgpt price in pakistan",
            target_cluster="Tool: Chatgpt",
            opportunity_score=90.0,
        )

        self.assertIn("chatgpt", brief.recommended_title.lower())
        self.assertIn("pakistan", brief.recommended_title.lower())
        self.assertTrue(brief.requires_approval)
        self.assertIn("Requires human owner review", brief.approval_reason)
        self.assertEqual(len(brief.aeo_answers), 1)
        # Direct answer text length between 40 and 65 words
        words = len(brief.aeo_answers[0].direct_answer_text.split())
        self.assertTrue(35 <= words <= 70, f"Word count {words} outside target range.")

    # ── Safe Autonomy Firewall Tests ─────────────────────────────────────────

    def test_safe_executor_protects_public_html(self):
        proj_dir = Path(__file__).resolve().parent.parent.parent
        executor = SafeExecutor(project_dir=proj_dir)

        # Internal data is safe auto
        is_safe, _ = executor.evaluate_action_safety("data/seo/keyword-map.json", {})
        self.assertTrue(is_safe)

        # Public HTML is locked behind human review
        is_safe_html, reason = executor.evaluate_action_safety("tools/chatgpt/index.html", {})
        self.assertFalse(is_safe_html)
        self.assertIn("Public HTML modification requires explicit human approval", reason)

        # Robots.txt is locked
        is_safe_robots, _ = executor.evaluate_action_safety("robots.txt", {})
        self.assertFalse(is_safe_robots)


    # ── International & Dual-Market SEO Growth Tests ───────────────────────

    def test_international_discovery_clusters(self):
        disc = KeywordDiscoveryEngine()
        intl_clusters = disc.generate_international_discovery_clusters()
        self.assertGreaterEqual(len(intl_clusters), 10)
        for c in intl_clusters:
            self.assertEqual(c.market, "GLOBAL")
            self.assertEqual(c.country_market, "International / Global")
            self.assertFalse(c.pakistan_relevance)
            self.assertIsNotNone(c.content_gap)
            self.assertIn(c.priority, ["P1 - Immediate", "P2 - Secondary", "P3 - Backlog"])
            self.assertIn(c.strategic_classification, [
                "Suitable for an existing page",
                "Requires a genuinely distinct new page",
                "Research-only/not ready"
            ])
            # Crucial rule: Never assign global keywords to Pakistan-only guides
            self.assertNotIn("-pakistan", c.recommended_page.lower(), f"Global keyword {c.keyword} was assigned to Pakistan guide {c.recommended_page}")

    def test_dual_market_opportunity_segmentation(self):
        disc = KeywordDiscoveryEngine()
        candidates = disc.generate_seed_discovery_clusters() + disc.generate_international_discovery_clusters()
        segmented = disc.segment_opportunities(candidates)

        self.assertIn("pakistan_transactional", segmented)
        self.assertIn("international_growth_opportunities", segmented)
        self.assertIn("international_audience_workflows", segmented)

        self.assertGreaterEqual(len(segmented["pakistan_transactional"]), 1)
        self.assertGreaterEqual(len(segmented["international_growth_opportunities"]), 1)
        self.assertGreaterEqual(len(segmented["international_audience_workflows"]), 1)

    def test_filters_12_and_13_re2_valid(self):
        lib = GSCFilterLibrary()
        filters = {f.name: f for f in lib.get_core_filters()}
        self.assertIn("Global Comparisons & Alternatives", filters)
        self.assertIn("International Inquiries & Cross-Border Access", filters)

        f12 = filters["Global Comparisons & Alternatives"]
        self.assertTrue(f12.is_re2_validated)
        matched12, _ = lib.test_filter(f12, ["chatgpt vs claude for coding", "midjourney alternatives for creators"])
        self.assertEqual(len(matched12), 2)

        f13 = filters["International Inquiries & Cross-Border Access"]
        self.assertTrue(f13.is_re2_validated)
        matched13, _ = lib.test_filter(f13, ["buy ai tools outside pakistan", "pay ai tools via wise"])
        self.assertEqual(len(matched13), 2)


if __name__ == "__main__":
    unittest.main()

