"""Data models for Backlink Acquisition Lifecycle and Manual Submission Evidence."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional
import uuid


class LifecycleState:
    """Canonical states in the Backlink Acquisition Lifecycle."""

    DISCOVERED = "discovered"
    EVIDENCE_VERIFIED = "evidence_verified"
    SCORED = "scored"
    DRAFT_READY = "draft_ready"
    OWNER_APPROVED = "owner_approved"
    MANUALLY_SUBMITTED = "manually_submitted"
    PUBLISHED = "published"
    BACKLINK_VERIFIED = "backlink_verified"
    RETAINED = "retained"

    # Terminal / Side / Failure States
    QUARANTINED = "quarantined"
    REJECTED = "rejected"
    SUBMISSION_FAILED = "submission_failed"
    PUBLICATION_PENDING = "publication_pending"
    VERIFICATION_FAILED = "verification_failed"
    VERIFICATION_INCONCLUSIVE = "verification_inconclusive"
    LINK_CHANGED = "link_changed"
    LINK_REMOVED = "link_removed"
    EXPIRED = "expired"


# Allowed state transition matrix (from_state -> set of valid to_states)
VALID_TRANSITION_GRAPH = {
    LifecycleState.DISCOVERED: {
        LifecycleState.EVIDENCE_VERIFIED,
        LifecycleState.QUARANTINED,
        LifecycleState.EXPIRED,
    },
    LifecycleState.EVIDENCE_VERIFIED: {
        LifecycleState.SCORED,
        LifecycleState.QUARANTINED,
        LifecycleState.EXPIRED,
    },
    LifecycleState.SCORED: {
        LifecycleState.DRAFT_READY,
        LifecycleState.QUARANTINED,
        LifecycleState.EXPIRED,
    },
    LifecycleState.DRAFT_READY: {
        LifecycleState.OWNER_APPROVED,
        LifecycleState.REJECTED,
        LifecycleState.EXPIRED,
    },
    LifecycleState.OWNER_APPROVED: {
        LifecycleState.MANUALLY_SUBMITTED,
        LifecycleState.SUBMISSION_FAILED,
        LifecycleState.REJECTED,
    },
    LifecycleState.MANUALLY_SUBMITTED: {
        LifecycleState.PUBLICATION_PENDING,
        LifecycleState.PUBLISHED,
        LifecycleState.SUBMISSION_FAILED,
    },
    LifecycleState.PUBLICATION_PENDING: {
        LifecycleState.PUBLISHED,
        LifecycleState.VERIFICATION_INCONCLUSIVE,
        LifecycleState.EXPIRED,
    },
    LifecycleState.PUBLISHED: {
        LifecycleState.BACKLINK_VERIFIED,
        LifecycleState.VERIFICATION_FAILED,
        LifecycleState.VERIFICATION_INCONCLUSIVE,
    },
    LifecycleState.BACKLINK_VERIFIED: {
        LifecycleState.RETAINED,
        LifecycleState.LINK_CHANGED,
        LifecycleState.LINK_REMOVED,
        LifecycleState.VERIFICATION_INCONCLUSIVE,
    },
    LifecycleState.RETAINED: {
        LifecycleState.RETAINED,
        LifecycleState.LINK_CHANGED,
        LifecycleState.LINK_REMOVED,
        LifecycleState.VERIFICATION_INCONCLUSIVE,
    },
    LifecycleState.VERIFICATION_INCONCLUSIVE: {
        LifecycleState.BACKLINK_VERIFIED,
        LifecycleState.VERIFICATION_FAILED,
        LifecycleState.LINK_REMOVED,
    },
    LifecycleState.LINK_CHANGED: {
        LifecycleState.BACKLINK_VERIFIED,
        LifecycleState.LINK_REMOVED,
    },
    LifecycleState.LINK_REMOVED: {
        LifecycleState.EXPIRED,
    },
    LifecycleState.QUARANTINED: set(),  # Terminal unless owner explicit reset
    LifecycleState.REJECTED: set(),     # Terminal unless owner explicit reset
    LifecycleState.SUBMISSION_FAILED: {
        LifecycleState.MANUALLY_SUBMITTED,
        LifecycleState.REJECTED,
    },
    LifecycleState.VERIFICATION_FAILED: {
        LifecycleState.LINK_REMOVED,
        LifecycleState.EXPIRED,
    },
    LifecycleState.EXPIRED: set(),
}


@dataclass
class ManualSubmissionEvidence:
    """Captures proof of manual owner submission. (Zero credentials/passwords permitted)."""

    prospect_id: str
    draft_id: str
    draft_hash: str
    submission_destination: str
    submission_method: str  # web_form, github_pr, editorial_pitch
    evidence_ref: str  # PR URL, ticket confirmation, or reference screenshot path
    submission_date: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    optional_publication_url: Optional[str] = None
    notes: Optional[str] = None

    def validate_no_secrets(self) -> None:
        """Adversarial check: strictly prevents storing passwords, tokens, or private keys."""
        combined = f"{self.submission_destination} {self.evidence_ref} {self.notes or ''}".lower()
        forbidden = ["password", "secret", "bearer", "token", "private_key", "passwd"]
        for f in forbidden:
            if f in combined:
                raise ValueError(f"Prohibited secret keyword '{f}' detected in submission evidence")

    def to_dict(self) -> Dict[str, Any]:
        self.validate_no_secrets()
        return {
            "prospect_id": self.prospect_id,
            "draft_id": self.draft_id,
            "draft_hash": self.draft_hash,
            "submission_destination": self.submission_destination,
            "submission_method": self.submission_method,
            "evidence_ref": self.evidence_ref,
            "submission_date": self.submission_date,
            "optional_publication_url": self.optional_publication_url,
            "notes": self.notes,
        }


@dataclass
class LifecycleTransitionRecord:
    """Immutable audit record of a state change in the acquisition lifecycle."""

    prospect_id: str
    from_state: str
    to_state: str
    actor: str  # owner, verifier_engine, scoring_engine, discovery_engine
    reason: str
    transition_id: str = field(default_factory=lambda: f"trans_{uuid.uuid4().hex[:12]}")
    evidence_data: Dict[str, Any] = field(default_factory=dict)
    idempotency_key: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "prospect_id": self.prospect_id,
            "from_state": self.from_state,
            "to_state": self.to_state,
            "actor": self.actor,
            "reason": self.reason,
            "evidence_data": self.evidence_data,
            "idempotency_key": self.idempotency_key,
            "timestamp": self.timestamp,
        }
