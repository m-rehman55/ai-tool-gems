"""Unit tests for Competitor Intelligence & SERP Radar Agent (AGENT-11)."""

import tempfile
import unittest
from pathlib import Path

from competitor_agent.competitors import get_top_10_competitors
from competitor_agent.hermes_integration import CompetitorHermesAgent
from competitor_agent.pricing_radar import get_pricing_radar_report
from competitor_agent.serp_radar import compute_share_of_voice, get_serp_radar_snapshots
from competitor_agent.snapshots import CompetitorSnapshotManager
from hermes_core.contracts import ApprovalRequirement, RiskClassification, TaskContract, TaskStatus


class TestCompetitorAgent(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)
        self.mgr = CompetitorSnapshotManager(snapshots_dir=self.tmp_path)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_top_10_competitors_registry(self):
        comps = get_top_10_competitors()
        self.assertEqual(len(comps), 10)
        domains = [c.domain for c in comps]
        self.assertIn("aitoolspak.tech", domains)
        self.assertIn("paktools.store", domains)
        self.assertIn("digitaltools.com.pk", domains)
        self.assertIn("zippersells.com", domains)

        # Confirm all have valid payment rails defined
        for c in comps:
            self.assertTrue(len(c.payment_rails) > 0)

    def test_pricing_radar_comparisons(self):
        pricing = get_pricing_radar_report()
        self.assertGreaterEqual(len(pricing), 4)

        chatgpt = next(p for p in pricing if p.tool_id == "chatgpt")
        self.assertEqual(chatgpt.aitoolgems_pkr, 3500)
        self.assertEqual(chatgpt.price_position, "PRICE_LEADER")
        self.assertGreater(chatgpt.highest_market_price, 3500)

    def test_serp_radar_and_share_of_voice(self):
        radar = get_serp_radar_snapshots()
        self.assertGreaterEqual(len(radar), 4)

        sov = compute_share_of_voice()
        self.assertIn("share_of_voice_pct", sov)
        self.assertIn("aitoolgems.tech", sov["share_of_voice_pct"])
        self.assertGreater(sov["share_of_voice_pct"]["aitoolgems.tech"], 0.0)
        self.assertEqual(sov["market_leader"], "aitoolgems.tech")

    def test_snapshot_diffing_detects_price_shifts(self):
        prev = {
            "pricing": {
                "chatgpt": {
                    "aitoolspak.tech": 3800,
                    "paktools.store": 3600,
                }
            }
        }
        curr = {
            "pricing": {
                "chatgpt": {
                    "aitoolspak.tech": 4000,  # Price increased by 200 PKR
                    "paktools.store": 3600,
                }
            }
        }
        diff = self.mgr.diff_snapshots(curr, prev)
        self.assertTrue(diff["has_changes"])
        self.assertEqual(len(diff["price_changes"]), 1)
        change = diff["price_changes"][0]
        self.assertEqual(change["competitor"], "aitoolspak.tech")
        self.assertEqual(change["delta"], 200)

    def test_hermes_integration_tasks(self):
        agent = CompetitorHermesAgent(snapshot_mgr=self.mgr)
        task = TaskContract(
            task_id="TEST-COMP-01",
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-11-COMPETITORS",
            objective="Audit Top 10 competitors, market Share of Voice, and pricing parity",
            scope="Competitor Intelligence",
            input_evidence={},
            required_tools=["competitor_radar"],
            expected_output={"audit": "dict"},
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["Valid competitor audit report"],
        )
        completed = agent.execute_task(task)
        self.assertEqual(completed.status, TaskStatus.VERIFIED)
        self.assertIn("top_10_competitors", completed.actual_output)
        self.assertEqual(completed.verification_evidence["competitors_monitored"], 10)


if __name__ == "__main__":
    unittest.main()

