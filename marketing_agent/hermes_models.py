"""Typed contracts for the Hermes SEO operating system."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class DataStatus(str, Enum):
    VERIFIED = "VERIFIED"
    ZERO = "ZERO"
    NO_DATA = "NO_DATA"
    ACCESS_REQUIRED = "ACCESS_REQUIRED"
    NOT_AVAILABLE = "NOT_AVAILABLE"
    ERROR = "ERROR"
    NOT_SUPPORTED = "NOT_SUPPORTED"


class ActionDecision(str, Enum):
    AUTO_SAFE = "AUTO_SAFE"
    AUTO_FIX = "AUTO_FIX"
    PR_REQUIRED = "PR_REQUIRED"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    REJECT = "REJECT"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass(frozen=True)
class RunContext:
    mode: str
    site_url: str
    repository: str
    run_id: str
    started_at: str = field(default_factory=utc_now)


@dataclass(frozen=True)
class Provenance:
    source: str
    source_identifier: str
    retrieved_at: str
    market: str | None = None
    country: str | None = None
    language: str | None = None
    device: str | None = None
    date_range: str | None = None
    confidence: str = "unknown"
    status: DataStatus = DataStatus.VERIFIED


@dataclass(frozen=True)
class MetricRecord:
    metric: str
    value: Any
    provenance: Provenance

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["provenance"]["status"] = self.provenance.status.value
        return result


@dataclass
class ConnectorResult:
    name: str
    status: DataStatus
    source: str
    records: list[MetricRecord] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "source": self.source,
            "records": [record.to_dict() for record in self.records],
            "details": self.details,
            "error": self.error,
        }


@dataclass(frozen=True)
class SEOAction:
    action: str
    decision: ActionDecision
    reason: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["decision"] = self.decision.value
        return result


def status_value(status: DataStatus | str) -> str:
    return status.value if isinstance(status, DataStatus) else str(status)
