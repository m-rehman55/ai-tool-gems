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

    async def test_unauthorized_user_id_rejected_even_in_owner_chat(self):
        res = await self.engine.handle_update({
            "update_id": 4,
            "message": {
                "chat": {"id": 123456, "type": "private"},
                "from": {"id": 666666},  # Attacker spoofing sender in same chat
                "text": "/backlinks",
            },
        })
        self.assertIn("Access Denied", res)
        self.assertIn("Unauthorized sender user_id '666666'", res)

    async def test_webhook_secret_header_enforced(self):
        engine_with_secret = WorkerApprovalEngine(
            d1=self.d1,
            owner_chat_id="123456",
            owner_user_id="789012",
            webhook_secret="super-secret-token-12345",
        )
        # Invalid secret
        res_bad = await engine_with_secret.handle_update({
            "update_id": 5,
            "message": {
                "chat": {"id": 123456, "type": "private"},
                "from": {"id": 789012},
                "text": "/backlinks",
            },
        }, header_secret="wrong-token")
        self.assertIn("Unauthorized: Invalid X-Telegram-Bot-Api-Secret-Token", res_bad)

        # Valid secret
        res_ok = await engine_with_secret.handle_update({
            "update_id": 6,
            "message": {
                "chat": {"id": 123456, "type": "private"},
                "from": {"id": 789012},
                "text": "/backlinks",
            },
        }, header_secret="super-secret-token-12345")
        self.assertIn("Total Prospects in D1: 15", res_ok)

    async def test_update_id_replay_protection(self):
        update = {
            "update_id": 99991,
            "message": {
                "chat": {"id": 123456, "type": "private"},
                "from": {"id": 789012},
                "text": "/backlinks",
            },
        }
        res1 = await self.engine.handle_update(update)
        self.assertIn("Total Prospects in D1: 15", res1)

        # Second submission with same update_id
        res2 = await self.engine.handle_update(update)
        self.assertIn("already processed", res2)
        self.assertIn("Duplicate skipped safely", res2)

    async def test_approval_includes_deterministic_draft_hash(self):
        res = await self.engine.handle_update({
            "update_id": 99992,
            "message": {
                "chat": {"id": 123456, "type": "private"},
                "from": {"id": 789012},
                "text": "/approve dev.to",
            },
        })
        self.assertIn("Approved for Manual Submission: dev.to", res)
        self.assertIn("Draft Hash:", res)

        # Audit event record has draft_hash
        ev = await self.d1.execute_first(
            "SELECT payload_json FROM audit_events WHERE event_type = 'prospect_approved' ORDER BY id DESC LIMIT 1"
        )
        self.assertIn("draft_hash", ev["payload_json"])

    async def test_audit_events_immutable_trigger_blocks_update_and_delete(self):
        # Insert test audit event
        await self.d1.record_audit_event("test_event", "tester", "123", {"action": "test"})
        ev = await self.d1.execute_first("SELECT id FROM audit_events WHERE event_type = 'test_event'")
        ev_id = ev["id"]

        # Attempting UPDATE must be aborted by database trigger
        with self.assertRaises(Exception) as ctx_upd:
            await self.d1.execute_mutation(
                "UPDATE audit_events SET actor = 'tampered' WHERE id = ?",
                (ev_id,),
            )
        self.assertIn("immutable append-only ledger", str(ctx_upd.exception))

        # Attempting DELETE must be aborted by database trigger
        with self.assertRaises(Exception) as ctx_del:
            await self.d1.execute_mutation(
                "DELETE FROM audit_events WHERE id = ?",
                (ev_id,),
            )
        self.assertIn("immutable append-only ledger", str(ctx_del.exception))

    async def test_atomic_concurrent_update_claim(self):
        # First claim wins
        res1 = await self.engine.claim_telegram_update(77701, "123456", "789012", "/backlinks")
        self.assertTrue(res1)

        # Concurrent attempt with same update_id loses atomically
        res2 = await self.engine.claim_telegram_update(77701, "123456", "789012", "/backlinks")
        self.assertFalse(res2)

    async def test_draft_hash_revalidation_at_approval_time(self):
        import hashlib
        import uuid
        now_iso = "2026-11-15T00:00:00Z"
        p = await self.d1.execute_first("SELECT id, prospect_domain, target_url FROM prospects WHERE lower(prospect_domain) = 'dev.to'")
        
        # Valid draft matching content
        target_url = p["target_url"]
        proposed_anchor = "Pakistan AI Tools Pricing Index"
        pitch_copy = "We have compiled the open verified pricing index."
        valid_hash = hashlib.sha256(f"{target_url}|{proposed_anchor}|{pitch_copy}".encode("utf-8")).hexdigest()

        draft_id = f"draft_{uuid.uuid4().hex[:8]}"
        await self.d1.execute_mutation(
            "INSERT INTO drafts (id, prospect_id, target_url, proposed_anchor, pitch_copy, content_sha256, status, created_at) VALUES (?, ?, ?, ?, ?, ?, 'pending_approval', ?)",
            (draft_id, p["id"], target_url, proposed_anchor, pitch_copy, valid_hash, now_iso),
        )

        res_ok = await self.engine.handle_update({
            "update_id": 88801,
            "message": {
                "chat": {"id": 123456, "type": "private"},
                "from": {"id": 789012},
                "text": "/approve dev.to",
            },
        })
        self.assertIn("Approved for Manual Submission: dev.to", res_ok)

        # Verify draft was updated to approved
        d = await self.d1.execute_first("SELECT status, approved_by FROM drafts WHERE id = ?", (draft_id,))
        self.assertEqual(d["status"], "approved")

        # Now test tampered draft
        tampered_id = f"draft_{uuid.uuid4().hex[:8]}"
        await self.d1.execute_mutation(
            "INSERT INTO drafts (id, prospect_id, target_url, proposed_anchor, pitch_copy, content_sha256, status, created_at) VALUES (?, ?, ?, ?, ?, 'tampered_bad_hash', 'pending_approval', ?)",
            (tampered_id, p["id"], target_url, proposed_anchor, pitch_copy, now_iso),
        )
        res_tampered = await self.engine.handle_update({
            "update_id": 88802,
            "message": {
                "chat": {"id": 123456, "type": "private"},
                "from": {"id": 789012},
                "text": "/approve dev.to",
            },
        })
        self.assertIn("Draft integrity error: SHA-256 content hash mismatch", res_tampered)


if __name__ == "__main__":
    unittest.main()
