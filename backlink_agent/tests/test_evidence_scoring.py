"""Unit tests for Opportunity Scoring and Evidence Verification Engine."""

import unittest

from backlink_agent.evidence_scoring import OpportunityScoringEngine, ScoreBreakdown, ScoredOpportunity
from backlink_agent.prospect_discovery.models import DiscoveredProspect


class TestEvidenceScoring(unittest.TestCase):
    def setUp(self):
        self.engine = OpportunityScoringEngine()

    def test_score_breakdown_calculation_and_tier(self):
        breakdown = ScoreBreakdown(
            relevance=25,
            editorial_quality=25,
            brand_dataset_fit=20,
            non_spam_quality=15,
            indexability=15,
        )
        self.assertEqual(breakdown.total_score, 100)
        self.assertEqual(breakdown.priority_tier, "high_priority")

        mid_breakdown = ScoreBreakdown(
            relevance=15,
            editorial_quality=15,
            brand_dataset_fit=10,
            non_spam_quality=10,
            indexability=10,
        )
        self.assertEqual(mid_breakdown.total_score, 60)
        self.assertEqual(mid_breakdown.priority_tier, "investigate")

        low_breakdown = ScoreBreakdown(
            relevance=10,
            editorial_quality=10,
            brand_dataset_fit=5,
            non_spam_quality=0,
            indexability=5,
        )
        self.assertEqual(low_breakdown.total_score, 30)
        self.assertEqual(low_breakdown.priority_tier, "quarantine")

    def test_tech_publication_scoring(self):
        prospect = DiscoveredProspect(
            prospect_id="p_devto",
            source_id="tech_publication",
            prospect_domain="dev.to",
            prospect_url="https://dev.to/new",
            source_page_url="https://dev.to/new",
            prospect_type="tech_publication",
            target_asset_url="https://aitoolgems.tech/prices/",
            relevance_hint=90,
        )
        scored = self.engine.score_prospect(prospect)
        self.assertGreaterEqual(scored.score.total_score, 80)
        self.assertEqual(scored.score.priority_tier, "high_priority")
        self.assertEqual(scored.action_recommendation, "draft_ready")
        self.assertIn("Direct asset citation: targets machine-readable /prices/ index", scored.rationale)

    def test_github_awesome_scoring(self):
        prospect = DiscoveredProspect(
            prospect_id="p_gh",
            source_id="github_awesome",
            prospect_domain="github.com",
            prospect_url="https://github.com/eudk/awesome-ai-tools",
            source_page_url="https://github.com/eudk/awesome-ai-tools",
            prospect_type="github_awesome",
            target_asset_url="https://aitoolgems.tech/",
            relevance_hint=95,
        )
        scored = self.engine.score_prospect(prospect)
        self.assertGreaterEqual(scored.score.total_score, 75)
        self.assertEqual(scored.action_recommendation, "draft_ready")
        self.assertEqual(scored.risk_factors, [])

    def test_reciprocal_link_demands_quarantined(self):
        prospect = DiscoveredProspect(
            prospect_id="p_bad",
            source_id="directory_index",
            prospect_domain="sketchytools.net",
            prospect_url="https://sketchytools.net/submit",
            source_page_url="https://sketchytools.net/submit",
            prospect_type="directory_class3",
            target_asset_url="https://aitoolgems.tech/",
            relevance_hint=40,
            metadata={"pricing_policy": "demands_reciprocal_link"},
        )
        scored = self.engine.score_prospect(prospect)
        self.assertEqual(scored.score.non_spam_quality, 0)
        self.assertTrue(any("reciprocal" in r.lower() for r in scored.risk_factors))

    def test_toxic_evidence_triggers_risk_factor(self):
        prospect = DiscoveredProspect(
            prospect_id="p_toxic",
            source_id="competitor_gap",
            prospect_domain="pbn-blast-network.shop",
            prospect_url="https://pbn-blast-network.shop/links",
            source_page_url="https://pbn-blast-network.shop/links",
            prospect_type="competitor_backlink",
            target_asset_url="https://aitoolgems.tech/",
            relevance_hint=20,
        )
        scored = self.engine.score_prospect(
            prospect,
            verification_evidence={"is_toxic": True, "is_noindex": True},
        )
        self.assertEqual(scored.score.non_spam_quality, 0)
        self.assertEqual(scored.score.indexability, 0)
        self.assertEqual(scored.action_recommendation, "quarantine")
        self.assertEqual(len(scored.risk_factors), 2)

    def test_scored_opportunity_serialization(self):
        breakdown = ScoreBreakdown(20, 20, 18, 15, 15)
        opp = ScoredOpportunity(
            prospect_id="p123",
            prospect_domain="example.org",
            source_page_url="https://example.org/dir",
            prospect_type="directory_class1",
            target_asset_url="https://aitoolgems.tech/",
            score=breakdown,
            rationale=["Good directory"],
        )
        d = opp.to_dict()
        self.assertEqual(d["prospect_id"], "p123")
        self.assertEqual(d["score"]["total_score"], 88)
        self.assertEqual(d["action_recommendation"], "draft_ready")


if __name__ == "__main__":
    unittest.main()
