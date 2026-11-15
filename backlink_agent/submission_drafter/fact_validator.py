"""Fact Validation and Truth Verification Engine for Backlink Drafts."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Tuple

from backlink_agent.facts import get_verified_facts
from .models import BaseDraft


class DraftFactValidator:
    """Enforces strict truth validation against verified_facts.yml."""

    def __init__(self):
        self.facts = get_verified_facts()

    def validate_draft(self, draft: BaseDraft) -> Tuple[bool, List[str], List[str]]:
        """Validates all text fields in a draft, returning (is_valid, violations, fact_ids)."""
        data = draft.to_dict()
        combined_text = " ".join(
            str(v) for k, v in data.items() if isinstance(v, (str, list))
        )

        violations = self.facts.validate_copy(combined_text)

        # Ensure authentic Pakistan pricing context
        lowered = combined_text.lower()
        if "usd only" in lowered or "no pkr" in lowered:
            violations.append("Prohibited: Excludes PKR pricing context")

        # Map verified fact IDs used
        fact_ids: List[str] = []
        if "ai tool gems" in lowered:
            fact_ids.append("fact_entity_brand")
        if "pkr" in lowered:
            fact_ids.append("fact_pricing_pkr")
        if "easypaisa" in lowered or "jazzcash" in lowered or "sadapay" in lowered:
            fact_ids.append("fact_payment_pakistan_rails")
        if "prices/ai-tools-pricing-pakistan.csv" in lowered or "/prices/" in lowered:
            fact_ids.append("fact_content_prices_dataset")
        if "llms.txt" in lowered:
            fact_ids.append("fact_content_llms_txt")

        return (len(violations) == 0, violations, fact_ids)
