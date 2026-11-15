"""Directory Submission Package Generator."""

from __future__ import annotations

import uuid
from typing import Any, Dict

from backlink_agent.evidence_scoring.models import ScoredOpportunity
from .fact_validator import DraftFactValidator
from .models import DirectorySubmissionDraft


class DirectorySubmissionDrafter:
    """Generates pre-filled, publication-ready directory submission packages."""

    def __init__(self, validator: Optional[DraftFactValidator] = None):
        self.validator = validator or DraftFactValidator()

    def draft_submission(self, opp: ScoredOpportunity) -> DirectorySubmissionDraft:
        draft_id = f"draft_dir_{uuid.uuid4().hex[:8]}"
        directory_name = opp.prospect_domain

        short_tagline = (
            "Verified AI tools directory and transparent subscription pricing index in Pakistan PKR."
        )
        long_description = (
            "AI Tool Gems (aitoolgems.tech) is a comprehensive directory and pricing tracker covering 40+ leading AI tools "
            "including ChatGPT, Claude, Midjourney, Canva, and ElevenLabs. It provides transparent flat PKR pricing, "
            "verified local payment instructions (EasyPaisa, JazzCash, SadaPay, Raast), full duration guarantees, "
            "and machine-readable datasets (/prices/ and /llms.txt) for researchers and developers."
        )

        tags = [
            "ai tools",
            "developer tools",
            "saas directory",
            "software pricing",
            "pakistan tech",
            "ai directory",
        ]

        draft = DirectorySubmissionDraft(
            draft_id=draft_id,
            prospect_id=opp.prospect_id,
            directory_name=directory_name,
            submission_url=opp.source_page_url,
            tool_name="AI Tool Gems",
            short_tagline=short_tagline,
            long_description=long_description,
            category="AI & Developer Tools",
            tags=tags,
            pricing_model="Freemium / Commercial Subscriptions",
            website_url="https://aitoolgems.tech/",
            target_landing_page=opp.target_asset_url or "https://aitoolgems.tech/",
        )

        is_valid, violations, fact_ids = self.validator.validate_draft(draft)
        if not is_valid:
            raise ValueError(f"Draft validation failed against verified facts: {violations}")

        draft.verified_fact_ids = fact_ids
        return draft
