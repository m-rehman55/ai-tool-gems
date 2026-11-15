"""GitHub Awesome List PR Package Generator."""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from backlink_agent.evidence_scoring.models import ScoredOpportunity
from .fact_validator import DraftFactValidator
from .models import GitHubAwesomePRDraft


class GitHubAwesomePRDrafter:
    """Generates PR-ready Markdown rows, commit messages, and PR descriptions for GitHub Awesome lists."""

    def __init__(self, validator: Optional[DraftFactValidator] = None):
        self.validator = validator or DraftFactValidator()

    def draft_pr(self, opp: ScoredOpportunity) -> GitHubAwesomePRDraft:
        draft_id = f"draft_gh_{uuid.uuid4().hex[:8]}"
        repo_name = opp.source_page_url.replace("https://github.com/", "").split("/blob/")[0].rstrip("/")
        if not repo_name:
            repo_name = opp.prospect_domain

        target_category = "AI Tool Resources & Directories"
        markdown_entry = "- [AI Tool Gems](https://aitoolgems.tech/) - Curated directory of 40+ AI tools and transparent subscription pricing tracker in PKR."
        pr_title = f"Add AI Tool Gems to {target_category}"
        commit_msg = f"docs(readme): add AI Tool Gems to {target_category}"
        pr_desc = (
            "### Description\n"
            "This pull request adds **AI Tool Gems** (https://aitoolgems.tech/) under the "
            f"**{target_category}** section.\n\n"
            "### Details\n"
            "- **Name:** AI Tool Gems\n"
            "- **URL:** https://aitoolgems.tech/\n"
            "- **Description:** Directory covering 40+ leading AI tools with transparent subscription pricing and machine-readable datasets.\n"
            "- **Compliance:** Adheres to repository alphabetical ordering and contribution guidelines.\n"
        )

        draft = GitHubAwesomePRDraft(
            draft_id=draft_id,
            prospect_id=opp.prospect_id,
            repository_name=repo_name,
            repository_url=f"https://github.com/{repo_name}",
            target_file="README.md",
            target_category=target_category,
            proposed_markdown_entry=markdown_entry,
            pr_title=pr_title,
            commit_message=commit_msg,
            pr_description=pr_desc,
        )

        is_valid, violations, fact_ids = self.validator.validate_draft(draft)
        if not is_valid:
            raise ValueError(f"GitHub PR draft validation failed against verified facts: {violations}")

        draft.verified_fact_ids = fact_ids
        return draft
