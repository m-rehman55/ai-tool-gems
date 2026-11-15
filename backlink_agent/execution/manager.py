"""Autonomous Execution Manager for Backlink Agent.

Orchestrates automated execution across adapters (GitHub PR, Dev.to API,
Email Pitch, Browser Subagent) and automatically transitions prospects
to `submitted_pending_review` without requiring manual `/submitted` commands.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple

from backlink_agent.prospect_repository import ProspectRepository
from .browser_adapter import DirectoryBrowserAdapter
from .devto_adapter import DevtoAPIAdapter
from .email_adapter import EmailPitchAdapter
from .github_adapter import GitHubPRAdapter
from .models import ExecutionResult, ExecutionStatus


class ExecutionManager:
    """Coordinates zero-touch automated execution and status synchronization."""

    def __init__(
        self,
        repository: Optional[ProspectRepository] = None,
        approval_engine: Optional[Any] = None,
    ):
        self.repository = repository or ProspectRepository()
        self.approval_engine = approval_engine
        self.github_adapter = GitHubPRAdapter()
        self.devto_adapter = DevtoAPIAdapter()
        self.email_adapter = EmailPitchAdapter()
        self.browser_adapter = DirectoryBrowserAdapter()

    def resolve_adapter(self, prospect: Any):
        """Resolves the best automated execution adapter for the prospect."""
        domain = getattr(prospect, "prospect_domain", "").lower()
        p_type = getattr(prospect, "prospect_type", "").lower()

        if "github" in domain or p_type == "github_awesome":
            return self.github_adapter
        if domain == "dev.to":
            return self.devto_adapter
        if domain == "techjuice.pk" or (p_type == "tech_publication" and "medium" not in domain):
            return self.email_adapter
        return self.browser_adapter

    def execute_prospect(
        self,
        target: str,
        draft_hash: Optional[str] = None,
        dry_run: bool = False,
        chat_id: str = "system",
        user_id: Optional[str] = None,
        update_id: int = 0,
    ) -> Tuple[ExecutionResult, str]:
        """Executes the prospect via its automated adapter and auto-registers submission."""
        p = self.repository.resolve(target, draft_hash)
        if not p:
            err_res = ExecutionResult(
                prospect_domain=target,
                adapter_name="unknown",
                status=ExecutionStatus.FAILED,
                error_message=f"Prospect '{target}' not found in tracker or registries.",
            )
            return err_res, f"❌ Prospect '{target}' not found in repository or registries."

        adapter = self.resolve_adapter(p)
        result = adapter.execute(p, dry_run=dry_run)

        if result.is_successful():
            # Auto-submit transition
            if self.approval_engine:
                self.approval_engine._cmd_submitted(
                    target=p.prospect_domain,
                    live_url=result.live_url,
                    chat_id=chat_id,
                    user_id=user_id,
                    update_id=update_id,
                )

            status_label = "Live Submitted" if result.status == ExecutionStatus.SUCCESS else "Dry-Run Simulated"
            reply_lines = [
                f"🚀 Autonomous Execution Successful! ({status_label})",
                f"• Target: {p.prospect_domain}",
                f"• Adapter: `{result.adapter_name}`",
                f"• Live Evidence / URL: {result.live_url}",
                "• Status: `submitted_pending_review` (Auto-Updated)",
                "",
                "🕵️ Zero-touch loop complete: Daily automated verification is now actively tracking this link!",
            ]
            return result, "\n".join(reply_lines)
        else:
            reply_lines = [
                f"⚠️ Autonomous Execution Failed for {p.prospect_domain}",
                f"• Adapter: `{result.adapter_name}`",
                f"• Error: {result.error_message}",
                "",
                "Aap manual command `/backlink {target}` use karke submission form open kar sakte hain.",
            ]
            return result, "\n".join(reply_lines)
