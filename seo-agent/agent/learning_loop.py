"""
learning_loop.py - Deterministic Learning & Self-Improvement Engine.
Tracks historical remediation outcomes, calculates success/false-positive rates per category,
and enforces immutable security boundaries preventing self-weakening.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("hermes.learning_loop")

# Protected critical systems that MUST NOT be autonomously modified or weakened
PROTECTED_GUARD_RULES = [
    "scope_guard.py",
    "safety_firewall.py",
    "GSC_CLIENT_SECRET",
    "TELEGRAM_BOT_TOKEN",
    "GEMINI_API_KEY",
    "deployment_authority",
    "price_freeze",
    "pakistan_exclusive",
]


@dataclass
class RemediationHistory:
    total_runs: int = 0
    total_issues_logged: int = 0
    fixes_attempted: int = 0
    fixes_verified: int = 0
    fixes_reverted: int = 0
    false_positives: Dict[str, int] = field(default_factory=dict)
    issue_recurrence: Dict[str, int] = field(default_factory=dict)
    success_rate_by_type: Dict[str, float] = field(default_factory=dict)
    last_updated: str = ""


class LearningFeedbackLoop:
    """Manages deterministic learning from verified outcomes and guards safety boundaries."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent.parent
        self.knowledge_file = self.base_dir / "seo-agent" / "knowledge" / "remediation_learnings.json"
        self.history = self.load_history()

    def load_history(self) -> RemediationHistory:
        """Loads historical learnings from persistent storage."""
        if not self.knowledge_file.exists():
            return RemediationHistory(
                total_runs=1,
                total_issues_logged=0,
                fixes_attempted=1,
                fixes_verified=1,
                fixes_reverted=0,
                false_positives={},
                issue_recurrence={},
                success_rate_by_type={"TECHNICAL_P0": 1.0, "CANONICAL": 1.0, "SCHEMA": 1.0, "ORPHAN_LINK": 0.95},
                last_updated=datetime.now(timezone.utc).isoformat(),
            )
        try:
            data = json.loads(self.knowledge_file.read_text(encoding="utf-8"))
            return RemediationHistory(**data)
        except Exception as e:
            logger.warning(f"Could not load learning history, using defaults: {e}")
            return RemediationHistory(last_updated=datetime.now(timezone.utc).isoformat())

    def save_history(self) -> None:
        """Persists learning history to disk."""
        self.knowledge_file.parent.mkdir(parents=True, exist_ok=True)
        self.history.last_updated = datetime.now(timezone.utc).isoformat()
        self.knowledge_file.write_text(
            json.dumps(asdict(self.history), indent=2),
            encoding="utf-8",
        )

    def record_run(
        self,
        issues_detected: List[Dict[str, Any]],
        fixes_applied: List[Dict[str, Any]],
        reverted_count: int = 0,
    ) -> None:
        """Updates learning parameters based on a completed run."""
        self.history.total_runs += 1
        self.history.total_issues_logged += len(issues_detected)
        self.history.fixes_attempted += len(fixes_applied)
        self.history.fixes_verified += (len(fixes_applied) - reverted_count)
        self.history.fixes_reverted += reverted_count

        # Track recurrence
        for iss in issues_detected:
            c_type = iss.get("check_type", "UNKNOWN")
            self.history.issue_recurrence[c_type] = self.history.issue_recurrence.get(c_type, 0) + 1

        # Re-compute success rate
        for fix in fixes_applied:
            c_type = fix.get("category", "GENERAL")
            prev_rate = self.history.success_rate_by_type.get(c_type, 1.0)
            if reverted_count > 0:
                self.history.success_rate_by_type[c_type] = round(max(0.1, prev_rate * 0.9), 2)
            else:
                self.history.success_rate_by_type[c_type] = round(min(1.0, prev_rate * 1.02), 2)

        self.save_history()

    def flag_false_positive(self, check_type: str, url: str) -> None:
        """Records a verified false positive to suppress recurring spam warnings."""
        key = f"{check_type}:{url}"
        self.history.false_positives[key] = self.history.false_positives.get(key, 0) + 1
        self.save_history()

    def get_confidence_multiplier(self, category: str) -> float:
        """Returns priority multiplier based on historical fix reliability."""
        return self.history.success_rate_by_type.get(category, 0.9)

    def verify_safety_immutability(self, proposed_changes: List[str]) -> bool:
        """
        Critical Safeguard: Enforces that proposed changes NEVER touch protected
        firewall rules, credential handlers, or deployment policies.
        Returns True if safe, False if an unauthorized mutation is attempted.
        """
        for item in proposed_changes:
            item_lower = item.lower()
            for protected in PROTECTED_GUARD_RULES:
                if protected.lower() in item_lower:
                    logger.critical(
                        f"SECURITY_HALT: Self-modification attempt blocked for protected rule: {protected}"
                    )
                    return False
        return True
