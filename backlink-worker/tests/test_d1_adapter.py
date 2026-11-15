"""Unit tests for Cloudflare D1 Database Adapter and Migrations."""

from __future__ import annotations

import asyncio
from pathlib import Path
import sqlite3
import sys
import unittest

WORKER_DIR = Path(__file__).resolve().parents[1]
if str(WORKER_DIR) not in sys.path:
    sys.path.insert(0, str(WORKER_DIR))

from src.d1_adapter import D1Adapter


class TestD1Adapter(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Create in-memory SQLite simulating Cloudflare D1
        self.conn = sqlite3.connect(":memory:")
        self.migration_sql = (Path(__file__).resolve().parents[1] / "migrations" / "0001_initial.sql").read_text(encoding="utf-8")
        self.conn.executescript(self.migration_sql)
        self.d1 = D1Adapter(sqlite_conn=self.conn)

    async def asyncTearDown(self):
        self.conn.close()

    async def test_migration_seeds_15_prospects(self):
        rows = await self.d1.execute_query("SELECT count(*) as count FROM prospects")
        self.assertEqual(rows[0]["count"], 15)

    async def test_kill_switch_defaults_to_false(self):
        enabled = await self.d1.is_agent_enabled()
        self.assertFalse(enabled)

    async def test_mode_defaults_to_report_only(self):
        mode = await self.d1.get_agent_mode()
        self.assertEqual(mode, "report_only")

    async def test_claim_job_run_is_idempotent(self):
        # First claim succeeds
        c1 = await self.d1.claim_job_run("verify", "idemp_101")
        self.assertTrue(c1)

        # Second claim with identical key fails
        c2 = await self.d1.claim_job_run("verify", "idemp_101")
        self.assertFalse(c2)

    async def test_record_verification_run_updates_prospect(self):
        run_data = {
            "prospect_id": "p_github_repo",
            "source_page": "https://github.com/m-rehman55/ai-tool-gems",
            "target_url": "https://aitoolgems.tech/",
            "classification": "live_follow",
            "http_status": 200,
            "target_found": True,
            "actual_anchor_text": "AI Tool Gems",
            "rel_tokens": [],
            "final_url": "https://github.com/m-rehman55/ai-tool-gems",
            "redirect_chain": [],
            "source_noindex": False,
            "canonical_url": None,
            "response_bytes": 1024,
            "elapsed_seconds": 0.25,
            "error_message": None,
        }
        await self.d1.record_verification_run(run_data)

        # Check verification_runs table
        runs = await self.d1.execute_query("SELECT * FROM verification_runs WHERE prospect_id = 'p_github_repo'")
        self.assertEqual(len(runs), 1)
        self.assertEqual(runs[0]["classification"], "live_follow")

        # Check updated prospect status
        p = await self.d1.execute_first("SELECT * FROM prospects WHERE id = 'p_github_repo'")
        self.assertEqual(p["link_status"], "live")

    async def test_record_audit_event(self):
        await self.d1.record_audit_event("test_event", "system", "p_1", {"detail": "unit_test"})
        events = await self.d1.execute_query("SELECT * FROM audit_events WHERE event_type = 'test_event'")
        self.assertEqual(len(events), 1)
        self.assertIn("unit_test", events[0]["payload_json"])


if __name__ == "__main__":
    unittest.main()
