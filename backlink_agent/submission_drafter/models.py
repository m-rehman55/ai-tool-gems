"""Data models for Structured Submission Drafts and Publication Packages."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional


@dataclass
class BaseDraft:
    draft_id: str
    prospect_id: str
    draft_type: str = "base"
    status: str = "pending_owner_review"
    verified_fact_ids: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def calculate_draft_hash(self) -> str:
        """Deterministic SHA-256 content hash."""
        payload_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(payload_str.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError


@dataclass
class DirectorySubmissionDraft(BaseDraft):
    draft_type: str = "directory_package"
    directory_name: str = ""
    submission_url: str = ""
    tool_name: str = "AI Tool Gems"
    short_tagline: str = ""
    long_description: str = ""
    category: str = "AI & Developer Tools"
    tags: List[str] = field(default_factory=list)
    pricing_model: str = "Freemium / Commercial Subscriptions"
    website_url: str = "https://aitoolgems.tech/"
    favicon_url: str = "https://aitoolgems.tech/favicon.svg"
    og_image_url: str = "https://aitoolgems.tech/og-image.png"
    target_landing_page: str = "https://aitoolgems.tech/"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "draft_id": self.draft_id,
            "prospect_id": self.prospect_id,
            "draft_type": "directory_package",
            "directory_name": self.directory_name,
            "submission_url": self.submission_url,
            "tool_name": self.tool_name,
            "short_tagline": self.short_tagline,
            "long_description": self.long_description,
            "category": self.category,
            "tags": self.tags,
            "pricing_model": self.pricing_model,
            "website_url": self.website_url,
            "favicon_url": self.favicon_url,
            "og_image_url": self.og_image_url,
            "target_landing_page": self.target_landing_page,
            "verified_fact_ids": self.verified_fact_ids,
            "status": self.status,
            "created_at": self.created_at,
        }


@dataclass
class GitHubAwesomePRDraft(BaseDraft):
    draft_type: str = "github_pr"
    repository_name: str = ""
    repository_url: str = ""
    target_file: str = "README.md"
    target_category: str = "AI Tool Resources & Directories"
    proposed_markdown_entry: str = ""
    pr_title: str = ""
    commit_message: str = ""
    pr_description: str = ""
    contributing_guidelines_url: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "draft_id": self.draft_id,
            "prospect_id": self.prospect_id,
            "draft_type": "github_pr",
            "repository_name": self.repository_name,
            "repository_url": self.repository_url,
            "target_file": self.target_file,
            "target_category": self.target_category,
            "proposed_markdown_entry": self.proposed_markdown_entry,
            "pr_title": self.pr_title,
            "commit_message": self.commit_message,
            "pr_description": self.pr_description,
            "contributing_guidelines_url": self.contributing_guidelines_url,
            "verified_fact_ids": self.verified_fact_ids,
            "status": self.status,
            "created_at": self.created_at,
        }


@dataclass
class PublicationPitchDraft(BaseDraft):
    draft_type: str = "publication_pitch"
    platform_name: str = ""
    target_publication_url: str = ""
    case_study_title: str = ""
    dataset_citation_url: str = "https://aitoolgems.tech/prices/"
    csv_dataset_url: str = "https://aitoolgems.tech/prices/ai-tools-pricing-pakistan.csv"
    article_outline: List[str] = field(default_factory=list)
    key_findings_summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "draft_id": self.draft_id,
            "prospect_id": self.prospect_id,
            "draft_type": "publication_pitch",
            "platform_name": self.platform_name,
            "target_publication_url": self.target_publication_url,
            "case_study_title": self.case_study_title,
            "dataset_citation_url": self.dataset_citation_url,
            "csv_dataset_url": self.csv_dataset_url,
            "article_outline": self.article_outline,
            "key_findings_summary": self.key_findings_summary,
            "verified_fact_ids": self.verified_fact_ids,
            "status": self.status,
            "created_at": self.created_at,
        }
