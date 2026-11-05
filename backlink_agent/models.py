"""Data models and policy contracts for Backlink & Digital Authority Intelligence."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class LinkStatus(str, Enum):
    NEW = "NEW"
    ACTIVE = "ACTIVE"
    LOST = "LOST"
    TOXIC = "TOXIC"


class OpportunityType(str, Enum):
    UNLINKED_MENTION = "UNLINKED_MENTION"
    BROKEN_LINK_RECLAMATION = "BROKEN_LINK_RECLAMATION"
    LOCAL_DIRECTORY = "LOCAL_DIRECTORY"
    EDITORIAL_FEATURE = "EDITORIAL_FEATURE"
    PARTNERSHIP = "PARTNERSHIP"


class LinkRisk(str, Enum):
    LOW_ORGANIC = "LOW_ORGANIC"
    MEDIUM_OUTREACH = "MEDIUM_OUTREACH"
    HIGH_PROHIBITED = "HIGH_PROHIBITED"


FORBIDDEN_LINK_METHODS = [
    "pbn", "private blog network", "paid link", "link exchange",
    "automated comment", "fiverr backlink", "web 2.0 tier",
    "mass directory submit", "forum profile spam", "guest post farm"
]


@dataclass
class BacklinkRecord:
    source_url: str
    target_url: str
    anchor_text: str
    is_follow: bool
    domain_authority: Optional[float] = None
    toxicity_score: float = 0.0  # 0 to 100
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    status: LinkStatus = LinkStatus.ACTIVE
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


@dataclass
class LinkOpportunity:
    opportunity_id: str
    domain: str
    target_page: str
    opportunity_type: OpportunityType
    relevance_assessment: str
    acquisition_method: str
    risk_classification: LinkRisk
    evidence: str
    projected_value: str
    created_at: float = field(default_factory=time.time)

    def validate_safety(self) -> tuple[bool, List[str]]:
        """Strictly validate link acquisition method against Google Search Essentials."""
        errors: List[str] = []
        method_lower = self.acquisition_method.lower()

        for forbidden in FORBIDDEN_LINK_METHODS:
            if forbidden in method_lower:
                errors.append(f"SPAM_POLICY_VIOLATION: Prohibited backlink method '{forbidden}' detected.")

        if self.risk_classification == LinkRisk.HIGH_PROHIBITED:
            errors.append("RISK_VIOLATION: HIGH_PROHIBITED link acquisition is blocked by safety policy.")

        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["opportunity_type"] = self.opportunity_type.value
        d["risk_classification"] = self.risk_classification.value
        return d
