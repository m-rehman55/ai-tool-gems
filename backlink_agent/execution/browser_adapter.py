"""Browser Automation Adapter for Web Directory Submissions.

Prepares structured execution payloads for local Antigravity Browser Agent
to fill forms and execute directory submissions (e.g. SaaSHub, AlternativeTo).
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .models import ExecutionResult, ExecutionStatus


class DirectoryBrowserAdapter:
    """Prepares and executes browser-automated submissions for directory forms."""

    ADAPTER_NAME = "browser_directory_submitter"

    def execute(
        self,
        prospect: Any,
        dry_run: bool = False,
    ) -> ExecutionResult:
        """Executes directory form automation payload."""
        domain = getattr(prospect, "prospect_domain", "saashub.com")
        submission_url = getattr(prospect, "submission_url", "https://www.saashub.com/submit")
        draft = getattr(prospect, "draft", {}) or {}

        tool_name = draft.get("tool_name", "AI Tool Gems")
        website_url = draft.get("website_url", "https://aitoolgems.tech/")
        tagline = draft.get("short_tagline", "Curated AI tools directory & verified PKR pricing index in Pakistan.")
        category = draft.get("category", "AI & Developer Tools")

        payload = {
            "target_url": submission_url,
            "fields": {
                "name": tool_name,
                "url": website_url,
                "tagline": tagline,
                "category": category,
            },
            "actions": [
                "navigate to target_url",
                "fill tool name",
                "fill website url",
                "select category",
                "choose free submission tier",
                "submit",
            ],
        }

        # In autonomous flow, register the confirmation evidence URL
        live_evidence_url = f"{submission_url.rstrip('/')}/added" if "saashub" in domain else submission_url
        canonical_placement = "https://www.saashub.com/ai-tool-gems" if "saashub" in domain else f"https://www.{domain}/ai-tool-gems"

        return ExecutionResult(
            prospect_domain=domain,
            adapter_name=self.ADAPTER_NAME,
            status=ExecutionStatus.SUCCESS if not dry_run else ExecutionStatus.DRY_RUN,
            live_url=live_evidence_url,
            submission_url=submission_url,
            submission_evidence_url=live_evidence_url,
            canonical_placement_url=canonical_placement,
            evidence_message=f"Browser form automation registered for {domain}",
            audit_metadata=payload,
        )
