"""
HERMES Multi-Agent Executive Protocol — Task Contracts & Global Registry
------------------------------------------------------------------------
Implements strict task contracts, state machines, dependency graphs,
and inter-agent handoffs for HERMES-CEO and specialist agents.
"""

from __future__ import annotations
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Set


class TaskStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED_PENDING_CREDENTIALS = "BLOCKED_PENDING_CREDENTIALS"
    BLOCKED_PENDING_APPROVAL = "BLOCKED_PENDING_APPROVAL"
    IMPLEMENTED = "IMPLEMENTED"
    TESTED = "TESTED"
    VERIFIED = "VERIFIED"
    DEPLOYED = "DEPLOYED"
    FAILED = "FAILED"


class RiskClassification(str, Enum):
    READ_ONLY = "READ_ONLY"
    LOW_REVERSIBLE = "LOW_REVERSIBLE"
    MEDIUM_CODE = "MEDIUM_CODE"
    HIGH_COMMERCIAL = "HIGH_COMMERCIAL"
    CRITICAL_DEPLOY = "CRITICAL_DEPLOY"


class ApprovalRequirement(str, Enum):
    AUTONOMOUS_APPROVED = "AUTONOMOUS_APPROVED"
    PULL_REQUEST_REQUIRED = "PULL_REQUEST_REQUIRED"
    HUMAN_EXPLICIT_REQUIRED = "HUMAN_EXPLICIT_REQUIRED"


class EvidenceTier(str, Enum):
    LIVE_API = "LIVE_API"
    LIVE_BROWSER = "LIVE_BROWSER"
    LIVE_REPOSITORY = "LIVE_REPOSITORY"
    CACHED = "CACHED"
    HISTORICAL = "HISTORICAL"
    ESTIMATED = "ESTIMATED"
    INFERRED = "INFERRED"
    UNVERIFIED = "UNVERIFIED"


class EvidenceUpgradeViolation(Exception):
    """Raised when an agent attempts to upgrade an estimate or inference into verified evidence."""
    pass


@dataclass
class EvidenceContract:
    """Formal evidence contract enforcing truthfulness and provenance rules."""
    evidence_id: str
    source_agent: str
    tier: EvidenceTier
    description: str
    data: Dict[str, Any] = field(default_factory=dict)
    provenance_uri: Optional[str] = None
    collected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    verified_by: Optional[str] = None
    is_verified: bool = False

    def __post_init__(self):
        if self.tier in (EvidenceTier.ESTIMATED, EvidenceTier.INFERRED, EvidenceTier.UNVERIFIED):
            self.is_verified = False

    @staticmethod
    def validate_evidence_upgrade(source_tier: EvidenceTier, target_tier: EvidenceTier) -> bool:
        """
        Enforces H2: An agent must never upgrade an estimate or inference into verified evidence.
        """
        unverified_tiers = {EvidenceTier.ESTIMATED, EvidenceTier.INFERRED, EvidenceTier.UNVERIFIED}
        verified_tiers = {EvidenceTier.LIVE_API, EvidenceTier.LIVE_BROWSER, EvidenceTier.LIVE_REPOSITORY}
        if source_tier in unverified_tiers and target_tier in verified_tiers:
            raise EvidenceUpgradeViolation(
                f"ILLEGAL_EVIDENCE_UPGRADE: Attempted to upgrade {source_tier.value} to {target_tier.value}. "
                "An agent must never upgrade an estimate or inference into verified evidence."
            )
        return True


@dataclass
class TaskContract:
    """Formal contract required for every inter-agent task handoff."""
    task_id: str
    requesting_agent: str
    responsible_agent: str
    objective: str
    scope: str
    risk_classification: RiskClassification
    approval_requirement: ApprovalRequirement
    completion_criteria: List[str]
    input_evidence: Dict[str, Any] = field(default_factory=dict)
    required_tools: List[str] = field(default_factory=list)
    expected_output: str = ""
    dependencies: List[str] = field(default_factory=list)
    verification_evidence: Dict[str, Any] = field(default_factory=dict)
    status: TaskStatus = TaskStatus.NOT_STARTED
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    assigned_budget_seconds: int = 300
    execution_time_seconds: float = 0.0
    error_message: Optional[str] = None
    permission_level: str = "WORKSPACE_WRITE"
    verification_method: str = "AUTOMATED_UNIT_TEST"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    blocker: Optional[str] = None

    @property
    def owner_agent(self) -> str:
        return self.responsible_agent

    @property
    def risk_level(self) -> RiskClassification:
        return self.risk_classification

    @property
    def acceptance_criteria(self) -> List[str]:
        return self.completion_criteria

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["risk_classification"] = self.risk_classification.value
        data["approval_requirement"] = self.approval_requirement.value
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> TaskContract:
        d = dict(data)
        d["risk_classification"] = RiskClassification(d["risk_classification"])
        d["approval_requirement"] = ApprovalRequirement(d["approval_requirement"])
        d["status"] = TaskStatus(d["status"])
        return cls(**d)

    def mark_in_progress(self) -> None:
        self.status = TaskStatus.IN_PROGRESS
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def mark_implemented(self, evidence: Dict[str, Any]) -> None:
        self.status = TaskStatus.IMPLEMENTED
        self.verification_evidence.update(evidence)
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def mark_tested(self, test_results: Dict[str, Any]) -> None:
        self.status = TaskStatus.TESTED
        self.verification_evidence["tests"] = test_results
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def mark_verified(self, verification_data: Dict[str, Any]) -> None:
        self.status = TaskStatus.VERIFIED
        self.verification_evidence["verification"] = verification_data
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def mark_failed(self, error: str) -> None:
        self.status = TaskStatus.FAILED
        self.error_message = error
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def mark_blocked_credentials(self, missing_credential: str) -> None:
        self.status = TaskStatus.BLOCKED_PENDING_CREDENTIALS
        self.error_message = f"Blocked pending credential: {missing_credential}"
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def mark_blocked_approval(self, reason: str) -> None:
        self.status = TaskStatus.BLOCKED_PENDING_APPROVAL
        self.error_message = f"Blocked pending approval: {reason}"
        self.updated_at = datetime.now(timezone.utc).isoformat()


class TaskRegistry:
    """Persistent Global Task Registry and Dependency Graph Engine."""

    def __init__(self, storage_path: Optional[Path | str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            base_dir = Path(__file__).resolve().parent.parent
            self.storage_path = base_dir / "data" / "tasks" / "registry.json"

        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.tasks: Dict[str, TaskContract] = {}
        self.load()

    def load(self) -> None:
        if self.storage_path.exists():
            try:
                raw = json.loads(self.storage_path.read_text(encoding="utf-8"))
                for tid, tdata in raw.get("tasks", {}).items():
                    self.tasks[tid] = TaskContract.from_dict(tdata)
            except Exception:
                self.tasks = {}

    def save(self) -> None:
        data = {
            "version": "1.0.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "task_count": len(self.tasks),
            "tasks": {tid: t.to_dict() for tid, t in self.tasks.items()}
        }
        self.storage_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def register_task(self, task: TaskContract) -> TaskContract:
        self.tasks[task.task_id] = task
        self.save()
        return task

    def update_task_status(self, task_id: str, status: TaskStatus, verification_evidence: Optional[Dict[str, Any]] = None) -> Optional[TaskContract]:
        task = self.tasks.get(task_id)
        if not task:
            return None
        task.status = status
        if verification_evidence:
            task.verification_evidence = verification_evidence
        self.save()
        return task

    def get_task(self, task_id: str) -> Optional[TaskContract]:
        if task_id not in self.tasks:
            self.load()
        return self.tasks.get(task_id)

    def create_task(
        self,
        requesting_agent: str,
        responsible_agent: str,
        objective: str,
        scope: str,
        risk_classification: RiskClassification,
        approval_requirement: ApprovalRequirement,
        completion_criteria: List[str],
        input_evidence: Optional[Dict[str, Any]] = None,
        dependencies: Optional[List[str]] = None,
        expected_output: str = "",
        required_tools: Optional[List[str]] = None,
        budget_seconds: int = 300,
    ) -> TaskContract:
        prefix = responsible_agent.replace("AGENT-", "").replace("HERMES-", "").split("-")[0]
        random_suffix = uuid.uuid4().hex[:6].upper()
        task_id = f"TASK-{prefix}-{random_suffix}"

        task = TaskContract(
            task_id=task_id,
            requesting_agent=requesting_agent,
            responsible_agent=responsible_agent,
            objective=objective,
            scope=scope,
            risk_classification=risk_classification,
            approval_requirement=approval_requirement,
            completion_criteria=completion_criteria,
            input_evidence=input_evidence or {},
            dependencies=dependencies or [],
            expected_output=expected_output,
            required_tools=required_tools or [],
            assigned_budget_seconds=budget_seconds,
        )
        return self.register_task(task)

    def can_execute(self, task_id: str) -> tuple[bool, str]:
        """Validates that all upstream task dependencies are satisfied."""
        task = self.tasks.get(task_id)
        if not task:
            return False, f"Task {task_id} not found in registry."

        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task:
                return False, f"Missing required dependency task {dep_id}."
            if dep_task.status not in (TaskStatus.VERIFIED, TaskStatus.DEPLOYED, TaskStatus.TESTED):
                return False, f"Dependency {dep_id} is in status {dep_task.status.value}, expected VERIFIED/DEPLOYED."

        return True, "All dependencies met."

    def detect_duplicate_task(self, objective: str, responsible_agent: str) -> Optional[TaskContract]:
        """Detects if an active or pending task with identical objective already exists."""
        clean_obj = objective.strip().lower()
        for t in self.tasks.values():
            if t.responsible_agent == responsible_agent and t.objective.strip().lower() == clean_obj:
                if t.status in (TaskStatus.IN_PROGRESS, TaskStatus.NOT_STARTED, TaskStatus.BLOCKED_PENDING_APPROVAL):
                    return t
        return None

    def list_pending_approvals(self) -> List[TaskContract]:
        return [t for t in self.tasks.values() if t.status == TaskStatus.BLOCKED_PENDING_APPROVAL]

    def list_by_status(self, status: TaskStatus) -> List[TaskContract]:
        return [t for t in self.tasks.values() if t.status == status]
