"""Unit tests for Owner-Only Telegram Approvals and Command Handling."""

from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from backlink_agent.approval import TelegramApprovalEngine, calculate_draft_hash


class TestTelegramApproval(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store_path = Path(self.temp_dir.name) / "approvals.json"
        self.audit_path = Path(self.temp_dir.name) / "approvals_audit.jsonl"
        self.engine = TelegramApprovalEngine(
            owner_chat_id="123456789",
            owner_user_id="987654321",
            store_path=self.store_path,
            audit_path=self.audit_path,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_unauthorized_chat_id_rejected(self):
        res = self.engine.handle_command(
            command_text="/backlinks",
            chat_id="999999999",  # Wrong chat ID
            chat_type="private",
            user_id="987654321",
        )
        self.assertIn("Access Denied", res)

    def test_unauthorized_user_id_rejected(self):
        res = self.engine.handle_command(
            command_text="/backlinks",
            chat_id="123456789",
            chat_type="private",
            user_id="111111111",  # Wrong user ID
        )
        self.assertIn("Access Denied", res)

    def test_group_chat_rejected(self):
        res = self.engine.handle_command(
            command_text="/backlinks",
            chat_id="123456789",
            chat_type="group",  # Group chat
            user_id="987654321",
        )
        self.assertIn("Access Denied", res)
        self.assertIn("private chat only", res)

    def test_owner_can_view_backlinks(self):
        res = self.engine.handle_command(
            command_text="/backlinks",
            chat_id="123456789",
            chat_type="private",
            user_id="987654321",
        )
        self.assertIn("Backlink Pipeline Summary", res)
        self.assertIn("Total Prospects:", res)

    def test_owner_can_view_prospect_detail(self):
        res = self.engine.handle_command(
            command_text="/backlink github.com",
            chat_id="123456789",
            chat_type="private",
            user_id="987654321",
        )
        self.assertIn("Prospect: github.com", res)
        self.assertIn("Draft Hash:", res)

    def test_approve_is_idempotent_and_creates_audit_trail(self):
        # First approval
        res1 = self.engine.handle_command(
            command_text="/approve github.com",
            chat_id="123456789",
            chat_type="private",
            user_id="987654321",
            update_id=101,
        )
        self.assertIn("Approved for Manual Submission", res1)
        self.assertIn("No automated forms or outreach sent", res1)

        # Audit file created
        self.assertTrue(self.audit_path.exists())
        lines = self.audit_path.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines), 1)

        # Second approval with same update/hash
        res2 = self.engine.handle_command(
            command_text="/approve github.com",
            chat_id="123456789",
            chat_type="private",
            user_id="987654321",
            update_id=102,
        )
        self.assertIn("Already Approved", res2)
        # Should NOT append duplicate audit event
        lines2 = self.audit_path.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(lines2), 1)

    def test_reject_records_reason(self):
        res = self.engine.handle_command(
            command_text="/reject github.com Reciprocal link demanded",
            chat_id="123456789",
            chat_type="private",
            user_id="987654321",
            update_id=103,
        )
        self.assertIn("Rejected github.com: Reciprocal link demanded", res)
        lines = self.audit_path.read_text(encoding="utf-8").strip().splitlines()
        self.assertIn("Reciprocal link demanded", lines[-1])


if __name__ == "__main__":
    unittest.main()
