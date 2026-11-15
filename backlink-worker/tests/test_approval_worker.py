"""Unit tests for Cloudflare Worker Approval Engine."""

from __future__ import annotations

from pathlib import Path
import sqlite3
import sys
import unittest

WORKER_DIR = Path(__file__).resolve().parents[1]
if str(WORKER_DIR) not in sys.path:
    sys.path.insert(0, str(WORKER_DIR))

from src.approval_worker import WorkerApprovalEngine
from src.d1_adapter import D1Adapter


class TestApprovalWorker(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.conn = sqlite3.connect(":memory:")
        migration_sql = (Path(__file__).resolve().parents[1] / "migrations" / "0001_initial.sql").read_text(encoding="utf-8")
        self.conn.executescript(migration_sql)
        self.d1 = D1Adapter(sqlite_conn=self.conn)
        self.engine = WorkerApprovalEngine(
            d1=self.d1,
            owner_chat_id="123456",
            owner_user_id="789012",
        )

    async def asyncTearDown(self):
        self.conn.close()

    async def test_unauthorized_chat_rejected(self):
        res = await self.engine.handle_update({
            "update_id": 1,
            "message": {
                "chat": {"id": 999999, "type": "private"},
                "from": {"id": 789012},
                "text": "/backlinks",
            },
        })
        self.assertIn("Access Denied", res)

    async def test_group_chat_rejected(self):
        res = await self.engine.handle_update({
            "update_id": 1,
            "message": {
                "chat": {"id": 123456, "type": "group"},
                "from": {"id": 789012},
                "text": "/backlinks",
            },
        })
        self.assertIn("Access Denied", res)

    async def test_owner_can_query_backlinks(self):
        res = await self.engine.handle_update({
            "update_id": 2,
            "message": {
                "chat": {"id": 123456, "type": "private"},
                "from": {"id": 789012},
                "text": "/backlinks",
            },
        })
        self.assertIn("Total Prospects in D1: 15", res)

    async def test_owner_can_approve_prospect_in_d1(self):
        res = await self.engine.handle_update({
            "update_id": 3,
            "message": {
                "chat": {"id": 123456, "type": "private"},
                "from": {"id": 789012},
                "text": "/approve github.com",
            },
        })
        self.assertIn("Approved for Manual Submission: github.com", res)

        # Verify D1 was updated
        p = await self.d1.execute_first("SELECT action_status FROM prospects WHERE lower(prospect_domain) = 'github.com'")
        self.assertEqual(p["action_status"], "owner_approved_for_manual_submission")


if __name__ == "__main__":
    unittest.main()
