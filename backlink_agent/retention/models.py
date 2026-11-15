"""Data models for Backlink Retention Monitoring (7, 30, 90-Day Lifecycle)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


class RetentionStatus:
    RETAINED = "retained"
    ANCHOR_CHANGED = "anchor_changed"
    TARGET_CHANGED = "target_changed"
    NOINDEX_ADDED = "noindex_added"
    CANONICAL_CHANGED = "canonical_changed"
    SUSPECTED_REMOVAL = "suspected_removal"              # HTTP 404 or missing anchor (recheck required)
    STRONG_REMOVAL_EVIDENCE = "strong_removal_evidence"  # HTTP 410 Gone
    INCONCLUSIVE_ACCESS_RESTRICTED = "inconclusive_access_restricted"  # HTTP 403 / WAF
    INCONCLUSIVE_TEMPORARY_FAILURE = "inconclusive_temporary_failure"  # HTTP 429, 5xx, timeout, DNS/TLS
    LINK_REMOVED = "link_removed"                        # Confirmed removed after repeat confirmation
    RECOVERED = "recovered"                              # Previously degraded/unavailable, now verified valid


@dataclass
class RetentionSnapshot:
    """Historical snapshot tracking link persistence over time."""

    prospect_id: str
    verification_date: str
    days_since_first_verified: int
    qualification: str
    anchor_text: str
    target_destination: str
    content_hash: str
    status_detected: str = RetentionStatus.RETAINED
    snapshot_id: str = field(default_factory=lambda: f"snap_{uuid.uuid4().hex[:10]}")
    previous_content_hash: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "prospect_id": self.prospect_id,
            "verification_date": self.verification_date,
            "days_since_first_verified": self.days_since_first_verified,
            "qualification": self.qualification,
            "anchor_text": self.anchor_text,
            "target_destination": self.target_destination,
            "content_hash": self.content_hash,
            "previous_content_hash": self.previous_content_hash,
            "status_detected": self.status_detected,
            "notes": self.notes,
        }
