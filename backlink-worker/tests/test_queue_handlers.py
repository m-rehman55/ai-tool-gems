"""Unit tests for Cloudflare Queue Producers and Consumers."""

from __future__ import annotations

from pathlib import Path
import sqlite3
import sys
import unittest

WORKER_DIR = Path(__file__).resolve().parents[1]
if str(WORKER_DIR) not in sys.path:
    sys.path.insert(0, str(WORKER_DIR))

from src.d1_adapter import D1Adapter
from src.queue_handlers import (
    enqueue_draft_generation,
    enqueue_verifications,
    handle_queue_batch,
    process_verification_job,
)


class MockQueue:
    def __init__(self):
        self.messages = []

    async def send(self, payload):
        self.messages.append(payload)


class MockQueueMessage:
    def __init__(self, body):
        self.body = body
        self.acked = False
        self.retried = False

    def ack(self):
        self.acked = True

    def retry(self):
        self.retried = True


class MockQueueBatch:
    def __init__(self, messages):
        self.messages = [MockQueueMessage(m) for m in messages]


class TestQueueHandlers(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.conn = sqlite3.connect(":memory:")
        migration_sql = (Path(__file__).resolve().parents[1] / "migrations" / "0001_initial.sql").read_text(encoding="utf-8")
        self.conn.executescript(migration_sql)
        self.d1 = D1Adapter(sqlite_conn=self.conn)

    async def asyncTearDown(self):
        self.conn.close()

    async def test_enqueue_verifications(self):
        queue = MockQueue()
        count = await enqueue_verifications(self.d1, queue, limit=10)
        self.assertGreater(count, 0)
        self.assertEqual(len(queue.messages), count)
        self.assertEqual(queue.messages[0]["job_type"], "verify_prospect")

    async def test_enqueue_draft_generation(self):
        queue = MockQueue()
        count = await enqueue_draft_generation(self.d1, queue, limit=5)
        self.assertGreater(count, 0)
        self.assertEqual(len(queue.messages), count)
        self.assertEqual(queue.messages[0]["job_type"], "generate_draft")

    async def test_queue_consumer_respects_kill_switch(self):
        # By default, kill switch is disabled ('false')
        batch = MockQueueBatch([{
            "job_type": "verify_prospect",
            "prospect_id": "p_github_repo",
            "source_page": "https://github.com/m-rehman55/ai-tool-gems",
            "target_url": "https://aitoolgems.tech/",
            "idempotency_key": "idemp_test_1",
        }])

        await handle_queue_batch(batch, None, None, d1=self.d1)

        # Message is safely acked without executing mutations
        self.assertTrue(batch.messages[0].acked)
        runs = await self.d1.execute_query("SELECT * FROM verification_runs")
        self.assertEqual(len(runs), 0)


if __name__ == "__main__":
    unittest.main()
