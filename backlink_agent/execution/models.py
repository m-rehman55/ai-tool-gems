"""Data models for Backlink Execution Adapters."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    DRY_RUN = "dry_run"


@dataclass
class ExecutionResult:
    prospect_domain: str
    adapter_name: str
    status: ExecutionStatus
    live_url: Optional[str] = None
    submission_url: Optional[str] = None
    submission_evidence_url: Optional[str] = None
    canonical_placement_url: Optional[str] = None
    evidence_message: str = ""
    audit_metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

    def get_effective_evidence_url(self) -> str:
        """Returns the primary evidence URL for audit tracking."""
        return self.submission_evidence_url or self.live_url or self.canonical_placement_url or "N/A"

    def is_successful(self) -> bool:
        return self.status in (ExecutionStatus.SUCCESS, ExecutionStatus.DRY_RUN)
