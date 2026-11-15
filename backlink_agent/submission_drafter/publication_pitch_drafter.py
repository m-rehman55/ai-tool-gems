"""Technical Publication Pitch Package Generator."""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from backlink_agent.evidence_scoring.models import ScoredOpportunity
from .fact_validator import DraftFactValidator
from .models import PublicationPitchDraft


class PublicationPitchDrafter:
    """Generates technical case-study pitches citing /prices/ and /llms.txt datasets."""

    def __init__(self, validator: Optional[DraftFactValidator] = None):
        self.validator = validator or DraftFactValidator()

    def draft_pitch(self, opp: ScoredOpportunity) -> PublicationPitchDraft:
        draft_id = f"draft_pub_{uuid.uuid4().hex[:8]}"
        platform_name = opp.prospect_domain

        title = "Case Study: Tracking Commercial AI Software Pricing and Payment Rails in Emerging Tech Ecosystems (Pakistan)"
        outline = [
            "Introduction: The localized purchasing parity challenge for global AI software (ChatGPT, Claude, Midjourney).",
            "Dataset Methodology: Analyzing 40 leading AI tool subscription tiers, flat PKR pricing, and domestic settlement rails.",
            "Payment Rails Grounding: Verification of local bank IBFT, Raast, EasyPaisa, JazzCash, and SadaPay acceptance without credit cards.",
            "Open Data & Machine Consumption: Exposing machine-readable pricing via /prices/ai-tools-pricing-pakistan.csv and llms.txt.",
            "Conclusion & Reference Links: Citing the open AI Tool Gems dataset (https://aitoolgems.tech/prices/).",
        ]
        summary = (
            "A technical data-driven analysis examining subscription price parity, localized currency risk, and "
            "payment gateway friction for 40 AI developer and productivity tools in Pakistan, utilizing the public dataset "
            "maintained at https://aitoolgems.tech/prices/ai-tools-pricing-pakistan.csv."
        )

        draft = PublicationPitchDraft(
            draft_id=draft_id,
            prospect_id=opp.prospect_id,
            platform_name=platform_name,
            target_publication_url=opp.source_page_url,
            case_study_title=title,
            dataset_citation_url="https://aitoolgems.tech/prices/",
            csv_dataset_url="https://aitoolgems.tech/prices/ai-tools-pricing-pakistan.csv",
            article_outline=outline,
            key_findings_summary=summary,
        )

        is_valid, violations, fact_ids = self.validator.validate_draft(draft)
        if not is_valid:
            raise ValueError(f"Publication pitch validation failed against verified facts: {violations}")

        draft.verified_fact_ids = fact_ids
        return draft
