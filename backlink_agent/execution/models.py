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
    evidence_message: str = ""
    audit_metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

    def is_successful(self) -> bool:
        return self.status in (ExecutionStatus.SUCCESS, ExecutionStatus.DRY_RUN)
