"""Unit tests for WP14 Durable Outbox Store, Concurrency, and Failure Injection."""

from datetime import datetime, timezone, timedelta
import shutil
import tempfile
import unittest
from pathlib import Path

from backlink_agent.telegram_delivery.models import OutboxMessage
from backlink_agent.telegram_delivery.outbox_store import LocalSQLiteOutboxStore


class TestOutboxStore(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.tmp_dir / "test_store.db"
        self.store = LocalSQLiteOutboxStore(self.db_path)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_sqlite_outbox_enqueue_and_get(self):
        msg = OutboxMessage(
            chat_id="12345",
            text="Test opportunity card",
            message_type="opportunity_card",
            prospect_domain="saashub.com",
            draft_id="d_01",
            draft_hash="hash_123",
        )
        self.store.enqueue(msg)

        retrieved = self.store.get(msg.message_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.message_id, msg.message_id)
        self.assertEqual(retrieved.chat_id, "12345")
        self.assertEqual(retrieved.status, "pending")
        self.assertEqual(retrieved.prospect_domain, "saashub.com")
        self.assertEqual(retrieved.draft_hash, "hash_123")

    def test_atomic_lease_locking_multi_worker(self):
        # Enqueue 6 messages
        for i in range(6):
            msg = OutboxMessage(chat_id="12345", text=f"Msg {i}", prospect_domain=f"domain{i}.com")
            self.store.enqueue(msg)

        # Worker 1 claims 4 messages
        worker1_claimed = self.store.claim_pending_messages(worker_id="worker_1", limit=4)
        self.assertEqual(len(worker1_claimed), 4)

        # Worker 2 concurrently claims remaining messages
        worker2_claimed = self.store.claim_pending_messages(worker_id="worker_2", limit=4)
        self.assertEqual(len(worker2_claimed), 2)

        # Verify disjoint sets (Zero double claiming)
        ids_1 = {m.message_id for m in worker1_claimed}
        ids_2 = {m.message_id for m in worker2_claimed}
        self.assertTrue(ids_1.isdisjoint(ids_2))

        # Further claims return empty
        worker3_claimed = self.store.claim_pending_messages(worker_id="worker_3", limit=4)
        self.assertEqual(len(worker3_claimed), 0)

    def test_stale_lease_recovery_after_timeout(self):
        msg = OutboxMessage(chat_id="12345", text="Crash test msg")
        self.store.enqueue(msg)

        # Worker claims message
        claimed = self.store.claim_pending_messages(worker_id="crashed_worker", limit=1)
        self.assertEqual(len(claimed), 1)

        # Simulate crash: message locked 600s ago
        stale_time = (datetime.now(timezone.utc) - timedelta(seconds=600)).isoformat()
        with self.store._get_connection() as conn:
            conn.execute(
                "UPDATE outbox_messages SET locked_at = ? WHERE message_id = ?",
                (stale_time, msg.message_id),
            )

        # Recovery sweep with 300s timeout recovers the stale lease
        recovered = self.store.recover_stale_leases(lease_timeout_seconds=300)
        self.assertEqual(recovered, 1)

        # Message is now retry_pending and can be claimed by worker 2
        recovered_msg = self.store.get(msg.message_id)
        self.assertEqual(recovered_msg.status, "retry_pending")
        self.assertEqual(recovered_msg.retry_count, 1)

        worker2_claimed = self.store.claim_pending_messages(worker_id="worker_2", limit=1)
        self.assertEqual(len(worker2_claimed), 1)
        self.assertEqual(worker2_claimed[0].message_id, msg.message_id)

    def test_lease_token_fencing_blocks_stale_worker_update(self):
        """WP15-A: A worker whose lease expired cannot update status if lease token changed."""
        msg = OutboxMessage(chat_id="12345", text="Fencing test")
        self.store.enqueue(msg)

        # Worker A claims message
        claimed_a = self.store.claim_pending_messages(worker_id="worker_a", limit=1)[0]
        token_a = claimed_a.lease_token
        self.assertIsNotNone(token_a)

        # Simulate lease expiration and Worker B taking over
        stale_time = (datetime.now(timezone.utc) - timedelta(seconds=600)).isoformat()
        with self.store._get_connection() as conn:
            conn.execute(
                "UPDATE outbox_messages SET locked_at = ? WHERE message_id = ?",
                (stale_time, msg.message_id),
            )
        self.store.recover_stale_leases(lease_timeout_seconds=300)
        claimed_b = self.store.claim_pending_messages(worker_id="worker_b", limit=1)[0]
        token_b = claimed_b.lease_token
        self.assertNotEqual(token_a, token_b)

        # Stale Worker A wakes up and attempts to mark delivered with old token
        success_a = self.store.update_delivery_status(
            message_id=msg.message_id,
            status="delivered",
            expected_lease_token=token_a,
        )
        self.assertFalse(success_a)  # Fenced out!

        # Worker B completes cleanly with active token
        success_b = self.store.update_delivery_status(
            message_id=msg.message_id,
            status="delivered",
            expected_lease_token=token_b,
        )
        self.assertTrue(success_b)
        self.assertEqual(self.store.get(msg.message_id).status, "delivered")

    def test_delivery_unknown_transition(self):
        msg = OutboxMessage(chat_id="12345", text="Timeout msg")
        self.store.enqueue(msg)

        success = self.store.update_delivery_status(
            message_id=msg.message_id,
            status="delivery_unknown",
            error_message="Dispatch timeout (delivery_unknown)",
        )
        self.assertTrue(success)

        updated = self.store.get(msg.message_id)
        self.assertEqual(updated.status, "delivery_unknown")
        self.assertIn("delivery_unknown", updated.error_message)

    def test_max_retries_transition_to_failed(self):
        msg = OutboxMessage(chat_id="12345", text="Failing msg", max_retries=2)
        self.store.enqueue(msg)

        msg.mark_retry_pending("Fail 1")
        self.store.update_delivery_status(msg.message_id, msg.status, msg.error_message)
        self.assertEqual(self.store.get(msg.message_id).status, "retry_pending")

        msg.mark_retry_pending("Fail 2")
        self.store.update_delivery_status(msg.message_id, msg.status, msg.error_message)
        updated = self.store.get(msg.message_id)
        self.assertEqual(updated.status, "failed")
        self.assertIn("Max retries exceeded", updated.error_message)

    def test_accepted_by_telegram_records_remote_id(self):
        msg = OutboxMessage(chat_id="12345", text="Live msg")
        self.store.enqueue(msg)

        self.store.update_delivery_status(
            message_id=msg.message_id,
            status="accepted_by_telegram",
            telegram_message_id=987654,
        )

        updated = self.store.get(msg.message_id)
        self.assertEqual(updated.status, "accepted_by_telegram")
        self.assertEqual(updated.telegram_message_id, 987654)
        self.assertIsNotNone(updated.delivered_at)

    def test_dry_run_simulated_isolated(self):
        msg = OutboxMessage(chat_id="12345", text="Dry run msg")
        self.store.enqueue(msg)

        self.store.update_delivery_status(
            message_id=msg.message_id,
            status="dry_run_simulated",
        )

        updated = self.store.get(msg.message_id)
        self.assertEqual(updated.status, "dry_run_simulated")
        self.assertIsNotNone(updated.delivered_at)

    def test_get_status_counts(self):
        self.store.enqueue(OutboxMessage(chat_id="1", text="m1"))
        self.store.enqueue(OutboxMessage(chat_id="2", text="m2"))
        counts = self.store.get_status_counts()
        self.assertEqual(counts["pending"], 2)
        self.assertEqual(counts["failed"], 0)


if __name__ == "__main__":
    unittest.main()
