"""Unit tests for Backlink & Digital Authority Intelligence Agent (AGENT-10)."""

import tempfile
import unittest
from pathlib import Path

from backlink_agent.hermes_integration import BacklinkHermesAgent
from backlink_agent.models import BacklinkRecord, LinkOpportunity, LinkRisk, LinkStatus, OpportunityType
from backlink_agent.pakistan_authority import get_pakistan_authority_opportunities
from backlink_agent.providers import BacklinkProviderManager
from backlink_agent.toxicity_analyzer import ToxicityScanner
from hermes_core.contracts import ApprovalRequirement, RiskClassification, TaskContract, TaskStatus


class TestBacklinkAgent(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)
        self.inventory_path = self.tmp_path / "inventory.json"
        self.mgr = BacklinkProviderManager(inventory_path=self.inventory_path)
        self.scanner = ToxicityScanner()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_backlink_record_and_inventory_persistence(self):
        inv = self.mgr.load_inventory()
        self.assertGreaterEqual(len(inv), 3)

        rec = BacklinkRecord(
            source_url="https://propakistani.pk/sample-article/",
            target_url="https://aitoolgems.tech/tools/chatgpt/",
            anchor_text="buy chatgpt plus in pakistan",
            is_follow=True,
            domain_authority=65.0,
        )
        self.mgr.add_backlink_record(rec)
        updated = self.mgr.load_inventory()
        self.assertEqual(len(updated), len(inv) + 1)
        self.assertTrue(any(i["source_url"] == rec.source_url for i in updated))

    def test_anti_spam_safety_rules_reject_pbn_and_paid_links(self):
        # 1. Reject PBN
        opp_pbn = LinkOpportunity(
            opportunity_id="BAD-01",
            domain="cheap-pbn-network.com",
            target_page="https://aitoolgems.tech/",
            opportunity_type=OpportunityType.EDITORIAL_FEATURE,
            relevance_assessment="PBN network backlink",
            acquisition_method="Buy 50 PBN private blog network links",
            risk_classification=LinkRisk.HIGH_PROHIBITED,
            evidence="Fiverr gig",
            projected_value="Spam",
        )
        is_safe, errors = opp_pbn.validate_safety()
        self.assertFalse(is_safe)
        self.assertTrue(any("SPAM_POLICY_VIOLATION" in e for e in errors))

        # 2. Reject Automated Comment Spam
        opp_comment = LinkOpportunity(
            opportunity_id="BAD-02",
            domain="blog-comments.com",
            target_page="https://aitoolgems.tech/",
            opportunity_type=OpportunityType.PARTNERSHIP,
            relevance_assessment="Comment backlinks",
            acquisition_method="Automated comment posting bot",
            risk_classification=LinkRisk.HIGH_PROHIBITED,
            evidence="GSA search engine ranker",
            projected_value="Spam",
        )
        is_safe2, errors2 = opp_comment.validate_safety()
        self.assertFalse(is_safe2)

    def test_pakistan_authority_opportunities_compliance(self):
        opps = get_pakistan_authority_opportunities()
        self.assertGreaterEqual(len(opps), 4)
        domains = [o.domain for o in opps]
        self.assertIn("pasha.org.pk", domains)
        self.assertIn("techjuice.pk", domains)

        for o in opps:
            is_safe, errors = o.validate_safety()
            self.assertTrue(is_safe, f"Opportunity {o.domain} violated safety policy: {errors}")

    def test_toxicity_scanner_detects_spam_tlds_and_anchors(self):
        # Spam TLD
        spam_rec = BacklinkRecord(
            source_url="http://free-bonus-spins.xyz/review/",
            target_url="https://aitoolgems.tech/",
            anchor_text="best online casino betting",
            is_follow=True,
            domain_authority=2.0,
        )
        score, flags = self.scanner.evaluate_link(spam_rec)
        self.assertGreaterEqual(score, 50.0)
        self.assertTrue(any("Spam TLD" in f for f in flags))
        self.assertTrue(any("Toxic anchor" in f for f in flags))

        # Clean link
        clean_rec = BacklinkRecord(
            source_url="https://github.com/m-rehman55/ai-tool-gems",
            target_url="https://aitoolgems.tech/",
            anchor_text="AI Tool Gems",
            is_follow=True,
            domain_authority=96.0,
        )
        clean_score, clean_flags = self.scanner.evaluate_link(clean_rec)
        self.assertEqual(clean_score, 0.0)
        self.assertEqual(len(clean_flags), 0)

    def test_toxicity_scanner_generates_disavow(self):
        toxic_links = [
            BacklinkRecord(
                source_url="http://bad-spammer-domain.xyz/page1",
                target_url="https://aitoolgems.tech/",
                anchor_text="casino",
                is_follow=True,
                toxicity_score=95.0,
            ),
            BacklinkRecord(
                source_url="http://bad-spammer-domain.xyz/page2",
                target_url="https://aitoolgems.tech/",
                anchor_text="betting",
                is_follow=True,
                toxicity_score=95.0,
            ),
        ]
        disavow_text = self.scanner.generate_disavow_file(toxic_links)
        self.assertIn("domain:bad-spammer-domain.xyz", disavow_text)
        # Deduplicated domain check
        self.assertEqual(disavow_text.count("domain:bad-spammer-domain.xyz"), 1)

    def test_hermes_integration_tasks(self):
        agent = BacklinkHermesAgent(provider_mgr=self.mgr)
        task = TaskContract(
            task_id="TEST-BACKLINK-01",
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-10-BACKLINKS",
            objective="Audit referring domains, dofollow ratio, and scan for toxic links",
            scope="Backlink Profile",
            input_evidence={},
            required_tools=["backlink_provider_manager"],
            expected_output={"audit": "dict"},
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["Valid backlink audit report"],
        )
        completed = agent.execute_task(task)
        self.assertEqual(completed.status, TaskStatus.VERIFIED)
        self.assertIn("referring_domains", completed.verification_evidence)
        self.assertGreater(completed.verification_evidence["total_backlinks"], 0)


if __name__ == "__main__":
    unittest.main()

