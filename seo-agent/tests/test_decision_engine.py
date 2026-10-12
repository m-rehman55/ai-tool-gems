#!/usr/bin/env python3
"""
Unit tests for DecisionEngine in seo-agent
------------------------------------------
"""

import sys
from pathlib import Path
import unittest

AGENT_DIR = Path(__file__).resolve().parent.parent
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

from agent.decision_engine import DecisionEngine, SEOOpportunity, Category, ActionTier

class TestDecisionEngine(unittest.TestCase):

    def setUp(self):
        self.engine_pr = DecisionEngine(autonomy_mode="PR")
        self.engine_audit = DecisionEngine(autonomy_mode="AUDIT")

    def test_critical_risk_is_rejected(self):
        opp = SEOOpportunity(
            id="CRIT-1",
            category=Category.TECHNICAL_P0,
            title="Adversarial Injection in target",
            target_url="https://aitoolgems.tech/",
            impact=10,
            confidence=0.9,
            effort=2,
            risk="CRITICAL",
            evidence="Malicious script detected",
            recommended_action="Reject change",
        )
        evaluated = self.engine_pr.classify_opportunity(opp)
        self.assertEqual(evaluated.tier, ActionTier.REJECT)

    def test_commercial_price_requires_human_approval(self):
        opp = SEOOpportunity(
            id="PRICE-1",
            category=Category.COMMERCIAL_PRICE,
            title="Update ChatGPT Plus Price to Rs 1,400",
            target_url="https://aitoolgems.tech/tools/chatgpt-plus-pakistan/",
            impact=8,
            confidence=0.95,
            effort=1,
            risk="LOW",
            evidence="Supplier price drop",
            recommended_action="Update price",
        )
        evaluated = self.engine_pr.classify_opportunity(opp)
        self.assertEqual(evaluated.tier, ActionTier.HUMAN_REQUIRED)

    def test_safe_technical_opportunity_creates_pr_in_pr_mode(self):
        opp = SEOOpportunity(
            id="TECH-1",
            category=Category.TECHNICAL_P1,
            title="Add missing meta description on guide",
            target_url="https://aitoolgems.tech/guides/how-to-buy-claude-pro-in-pakistan/",
            impact=7,
            confidence=0.95,
            effort=2,
            risk="SAFE",
            evidence="Meta description length is 0",
            recommended_action="Add compelling meta description",
        )
        evaluated = self.engine_pr.classify_opportunity(opp)
        self.assertEqual(evaluated.tier, ActionTier.PROPOSE_PR)

    def test_audit_mode_downgrades_actions_to_auto_report(self):
        opp = SEOOpportunity(
            id="TECH-2",
            category=Category.TECHNICAL_P1,
            title="Add missing alt text",
            target_url="https://aitoolgems.tech/tools/canva-pro-pakistan/",
            impact=5,
            confidence=0.85,
            effort=1,
            risk="SAFE",
            evidence="Alt tag missing on image",
            recommended_action="Add alt text",
        )
        evaluated = self.engine_audit.classify_opportunity(opp)
        self.assertEqual(evaluated.tier, ActionTier.AUTO_REPORT)

if __name__ == "__main__":
    unittest.main()
