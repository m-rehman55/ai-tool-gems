"""Unit tests for Durable Marketing Agent & Retry Engine (AGENT-12)."""

import tempfile
import unittest
from pathlib import Path
from urllib.error import HTTPError

from hermes_core.contracts import ApprovalRequirement, RiskClassification, TaskContract, TaskStatus
from marketing_agent.campaign_profitability import CampaignProfitabilityEngine
from marketing_agent.hermes_integration import MarketingHermesAgent
from marketing_agent.publishing_queue import PostState, PublishingQueueManager
from marketing_agent.retry_handler import (
    execute_with_durable_retry,
    generate_idempotency_key,
    parse_retry_after,
)


class TestDurableMarketingAgent(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp_dir.name)
        self.queue_file = self.tmp_path / "queue.json"
        self.orders_file = self.tmp_path / "orders.json"
        self.queue_mgr = PublishingQueueManager(queue_file=self.queue_file)
        self.profitability = CampaignProfitabilityEngine(orders_file=self.orders_file)

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_parse_retry_after(self):
        # Integer seconds
        self.assertEqual(parse_retry_after("15"), 15.0)
        self.assertEqual(parse_retry_after("0"), 0.0)
        self.assertIsNone(parse_retry_after(None))
        self.assertIsNone(parse_retry_after("invalid_header"))

    def test_idempotency_key_generation(self):
        key1 = generate_idempotency_key("publish", {"platform": "instagram", "text": "Deal 1"})
        key2 = generate_idempotency_key("publish", {"platform": "instagram", "text": "Deal 1"})
        key3 = generate_idempotency_key("publish", {"platform": "instagram", "text": "Deal 2"})
        self.assertEqual(key1, key2)
        self.assertNotEqual(key1, key3)
        self.assertEqual(len(key1), 32)

    def test_durable_retry_recovers_after_rate_limit(self):
        attempts = 0

        def flaky_action():
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                # Raise 429
                raise HTTPError(
                    url="https://api.buffer.com",
                    code=429,
                    msg="Too Many Requests",
                    hdrs={"Retry-After": "0.01"},
                    fp=None,
                )
            return {"status": "SUCCESS"}

        result = execute_with_durable_retry("FlakyCall", flaky_action, max_attempts=3, initial_backoff=0.01)
        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(attempts, 2)

    def test_publishing_queue_duplicate_prevention(self):
        post1, msg1 = self.queue_mgr.enqueue_post(
            platform="instagram",
            caption="Special morning deal for ChatGPT Plus",
            media_url="https://aitoolgems.tech/assets/deal1.png",
            scheduled_time="2026-11-06T09:00:00Z",
            campaign_utm="ig-chatgpt-morning",
        )
        self.assertIsNotNone(post1)
        self.assertIn("successfully queued", msg1)

        # Attempt duplicate enqueue
        post2, msg2 = self.queue_mgr.enqueue_post(
            platform="instagram",
            caption="Special morning deal for ChatGPT Plus",
            media_url="https://aitoolgems.tech/assets/deal1.png",
            scheduled_time="2026-11-06T09:00:00Z",
            campaign_utm="ig-chatgpt-morning",
        )
        self.assertIsNone(post2)
        self.assertIn("DUPLICATE_IGNORED", msg2)

    def test_publishing_queue_state_transitions(self):
        post, _ = self.queue_mgr.enqueue_post(
            platform="tiktok",
            caption="Evening AI video guide",
            media_url="https://aitoolgems.tech/assets/deal2.mp4",
            scheduled_time="2026-11-06T18:00:00Z",
            campaign_utm="tk-video-evening",
        )
        self.assertEqual(post.state, PostState.QUEUED)

        # Transition to SCHEDULED
        self.assertTrue(self.queue_mgr.transition_state(post.post_id, PostState.SCHEDULED, external_id="buf-123"))
        q = self.queue_mgr.load_queue()
        self.assertEqual(q[0]["state"], PostState.SCHEDULED.value)
        self.assertEqual(q[0]["external_buffer_id"], "buf-123")

        # Transition to DELIVERED
        self.assertTrue(self.queue_mgr.transition_state(post.post_id, PostState.DELIVERED))
        q = self.queue_mgr.load_queue()
        self.assertEqual(q[0]["state"], PostState.DELIVERED.value)
        self.assertIsNotNone(q[0]["delivered_at"])

        # Transition to VERIFIED
        self.assertTrue(self.queue_mgr.transition_state(post.post_id, PostState.VERIFIED))
        q = self.queue_mgr.load_queue()
        self.assertEqual(q[0]["state"], PostState.VERIFIED.value)

    def test_campaign_profitability_attribution(self):
        outcome = self.profitability.evaluate_campaign("ig-chatgpt-morning", "instagram", "chatgpt", clicks=100)
        self.assertGreater(outcome.clicks, 0)
        self.assertGreater(outcome.whatsapp_leads, 0)
        self.assertGreater(outcome.confirmed_orders, 0)
        self.assertGreater(outcome.gross_revenue_pkr, 0)
        self.assertGreaterEqual(outcome.roi_pct, 100.0)

    def test_hermes_integration_tasks(self):
        agent = MarketingHermesAgent(project_dir=self.tmp_path)
        task = TaskContract(
            task_id="TEST-MKT-01",
            requesting_agent="HERMES-CEO",
            responsible_agent="AGENT-12-MARKETING",
            objective="Audit social campaigns, queue backlog, and profitability",
            scope="Marketing Campaigns",
            input_evidence={},
            required_tools=["marketing_queue_manager"],
            expected_output={"audit": "dict"},
            risk_classification=RiskClassification.READ_ONLY,
            approval_requirement=ApprovalRequirement.AUTONOMOUS_APPROVED,
            completion_criteria=["Valid campaign audit report"],
        )
        completed = agent.execute_task(task)
        self.assertEqual(completed.status, TaskStatus.VERIFIED)
        self.assertIn("sample_campaigns", completed.actual_output)
        self.assertIn("retry_system", completed.actual_output)


if __name__ == "__main__":
    unittest.main()
