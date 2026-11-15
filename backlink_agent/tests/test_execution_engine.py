"""Unit tests for WP20 Autonomous Backlink Execution Engine."""

from __future__ import annotations

import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from backlink_agent.approval import TelegramApprovalEngine
from backlink_agent.execution.browser_adapter import DirectoryBrowserAdapter
from backlink_agent.execution.devto_adapter import DevtoAPIAdapter
from backlink_agent.execution.email_adapter import EmailPitchAdapter
from backlink_agent.execution.github_adapter import GitHubPRAdapter
from backlink_agent.execution.models import ExecutionResult, ExecutionStatus
from backlink_agent.execution.manager import ExecutionManager
from backlink_agent.prospect_repository import ProspectRepository


class TestExecutionEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.store_path = Path(self.temp_dir.name) / "approvals.json"
        self.audit_path = Path(self.temp_dir.name) / "approvals_audit.jsonl"
        self.approval_engine = TelegramApprovalEngine(
            owner_chat_id="123456789",
            owner_user_id="987654321",
            store_path=self.store_path,
            audit_path=self.audit_path,
        )
        self.repository = ProspectRepository()
        self.manager = ExecutionManager(
            repository=self.repository,
            approval_engine=self.approval_engine,
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    # -------------------------------------------------------------------------
    # 1. GitHub PR Adapter Tests
    # -------------------------------------------------------------------------
    def test_github_adapter_extract_repo_and_link_check(self):
        adapter = GitHubPRAdapter()
        repo = adapter.extract_repo_name("https://github.com/eudk/awesome-ai-tools")
        self.assertEqual(repo, "eudk/awesome-ai-tools")

        repo_blob = adapter.extract_repo_name("https://github.com/eudk/awesome-ai-tools/blob/main/README.md")
        self.assertEqual(repo_blob, "eudk/awesome-ai-tools")

        sample_readme = "# Awesome AI\n- [ChatGPT](https://chat.openai.com/)\n"
        self.assertFalse(adapter.check_if_link_exists(sample_readme, "aitoolgems.tech"))

        sample_with_link = "# Awesome AI\n- [AI Tool Gems](https://aitoolgems.tech/)\n"
        self.assertTrue(adapter.check_if_link_exists(sample_with_link, "aitoolgems.tech"))

    def test_github_adapter_insert_markdown_entry(self):
        adapter = GitHubPRAdapter()
        readme = (
            "# Awesome AI Tools\n\n"
            "## AI Tool Resources & Directories\n"
            "- [Resource 1](https://example.com/1)\n"
            "- [Resource 2](https://example.com/2)\n\n"
            "## Audio\n"
            "- [Audio 1](https://example.com/audio)\n"
        )
        new_entry = "- [AI Tool Gems](https://aitoolgems.tech/) - Directory in PKR."
        updated = adapter.insert_markdown_entry(readme, new_entry, "AI Tool Resources & Directories")
        self.assertIn(new_entry, updated)
        # Entry should be before Audio section
        self.assertTrue(updated.index(new_entry) < updated.index("## Audio"))

    def test_github_adapter_dry_run_execution(self):
        adapter = GitHubPRAdapter()
        prospect = self.repository.resolve("eudk/awesome-ai-tools") or self.repository.resolve("github.com")
        self.assertIsNotNone(prospect)

        res = adapter.execute(prospect, dry_run=True)
        self.assertEqual(res.status, ExecutionStatus.DRY_RUN)
        self.assertTrue(res.is_successful())
        self.assertIn("pull", res.live_url)

    # -------------------------------------------------------------------------
    # 2. Dev.to API Adapter Tests
    # -------------------------------------------------------------------------
    def test_devto_adapter_dry_run_content(self):
        adapter = DevtoAPIAdapter()
        prospect = self.repository.resolve("dev.to")
        self.assertIsNotNone(prospect)

        res = adapter.execute(prospect, dry_run=True)
        self.assertEqual(res.status, ExecutionStatus.DRY_RUN)
        self.assertTrue(res.is_successful())
        self.assertIn("dev.to", res.live_url)

    def test_devto_adapter_mocked_live_success(self):
        adapter = DevtoAPIAdapter(api_key="fake-test-key-12345")
        prospect = self.repository.resolve("dev.to")
        self.assertIsNotNone(prospect)

        mock_response_data = {
            "id": 987654,
            "title": "Tracking Commercial AI Software Pricing",
            "url": "https://dev.to/aitoolgems/tracking-commercial-ai-software-pricing-987654",
            "slug": "tracking-commercial-ai-software-pricing-987654",
        }
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_response_data).encode("utf-8")
        mock_response.__enter__.return_value = mock_response

        with patch("urllib.request.urlopen", return_value=mock_response):
            res = adapter.execute(prospect, dry_run=False)

        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        self.assertEqual(res.live_url, "https://dev.to/aitoolgems/tracking-commercial-ai-software-pricing-987654")

    # -------------------------------------------------------------------------
    # 3. Email & Browser Adapters Tests
    # -------------------------------------------------------------------------
    def test_email_pitch_adapter_dry_run(self):
        adapter = EmailPitchAdapter()
        prospect = self.repository.resolve("techjuice.pk")
        self.assertIsNotNone(prospect)

        res = adapter.execute(prospect, dry_run=True)
        self.assertEqual(res.status, ExecutionStatus.DRY_RUN)
        self.assertIn("editors@techjuice.pk", res.live_url)

    def test_browser_directory_adapter(self):
        adapter = DirectoryBrowserAdapter()
        prospect = self.repository.resolve("saashub.com")
        self.assertIsNotNone(prospect)

        res = adapter.execute(prospect, dry_run=False)
        self.assertEqual(res.status, ExecutionStatus.SUCCESS)
        self.assertIn("saashub.com", res.live_url)

    # -------------------------------------------------------------------------
    # 4. Execution Manager & Routing Tests
    # -------------------------------------------------------------------------
    def test_manager_routes_prospects_correctly(self):
        gh_p = self.repository.resolve("github.com")
        devto_p = self.repository.resolve("dev.to")
        tech_p = self.repository.resolve("techjuice.pk")
        saas_p = self.repository.resolve("saashub.com")

        self.assertIsInstance(self.manager.resolve_adapter(gh_p), GitHubPRAdapter)
        self.assertIsInstance(self.manager.resolve_adapter(devto_p), DevtoAPIAdapter)
        self.assertIsInstance(self.manager.resolve_adapter(tech_p), EmailPitchAdapter)
        self.assertIsInstance(self.manager.resolve_adapter(saas_p), DirectoryBrowserAdapter)

    def test_manager_auto_submits_and_updates_audit(self):
        res, reply = self.manager.execute_prospect(
            target="dev.to",
            dry_run=True,
            chat_id="123456789",
            user_id="987654321",
            update_id=501,
        )
        self.assertTrue(res.is_successful())
        self.assertIn("Autonomous Execution Successful", reply)
        self.assertIn("submitted_pending_review", reply)

        # Confirm audit event was recorded in approvals.json
        state = self.approval_engine.load_state()
        devto_approval = state.get("approvals", {}).get("dev.to")
        self.assertIsNotNone(devto_approval)
        self.assertEqual(devto_approval.get("new_status"), "submitted_pending_review")

        # Confirm audit log entry
        lines = self.audit_path.read_text(encoding="utf-8").strip().splitlines()
        self.assertTrue(any("dev.to" in line and "submitted" in line for line in lines))

    # -------------------------------------------------------------------------
    # 5. Telegram /execute Command Integration
    # -------------------------------------------------------------------------
    def test_telegram_execute_command_happy_path(self):
        reply = self.approval_engine.handle_command(
            command_text="/execute saashub.com",
            chat_id="123456789",
            chat_type="private",
            user_id="987654321",
            update_id=502,
        )
        self.assertIn("Autonomous Execution Successful", reply)
        self.assertIn("saashub.com", reply)
        self.assertIn("submitted_pending_review", reply)

    def test_approve_response_includes_auto_execute_hint(self):
        reply = self.approval_engine.handle_command(
            command_text="/approve dev.to",
            chat_id="123456789",
            chat_type="private",
            user_id="987654321",
            update_id=503,
        )
        self.assertIn("/execute dev.to", reply)
        self.assertIn("Zero-Touch Auto-Execute", reply)


if __name__ == "__main__":
    unittest.main()
