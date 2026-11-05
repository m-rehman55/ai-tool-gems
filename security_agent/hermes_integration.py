"""
security_agent.hermes_integration - Connects Security Agent to HERMES Central Orchestrator.
"""

from pathlib import Path
from typing import Dict, Any

from hermes_core.contracts import TaskContract, TaskStatus, RiskClassification, ApprovalRequirement
from security_agent.secrets_scanner import SecretsScanner
from security_agent.html_safety_validator import HtmlSafetyValidator
from security_agent.dependency_checker import DependencyChecker
from security_agent.snapshot_manager import SnapshotManager


class HermesSecurityAgent:
    """
    AGENT-15-SECURITY:
    Governance, Security Firewall, Secrets Scanning, and Rollback Integrity.
    """

    AGENT_ID = "AGENT-15-SECURITY"

    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path(__file__).resolve().parent.parent
        self.secrets_scanner = SecretsScanner()
        self.html_validator = HtmlSafetyValidator()
        self.dependency_checker = DependencyChecker()
        self.snapshot_manager = SnapshotManager(self.repo_root)

    def execute_task(self, task: TaskContract) -> TaskContract:
        """
        Executes a TaskContract delegated to AGENT-15-SECURITY.
        """
        task.responsible_agent = self.AGENT_ID
        objective_lower = task.objective.lower()

        try:
            if "audit" in objective_lower:
                return self._handle_full_audit(task)
            elif "snapshot" in objective_lower:
                return self._handle_snapshot_create(task)
            elif "secrets" in objective_lower:
                return self._handle_secrets_scan(task)
            elif "html" in objective_lower or "xss" in objective_lower:
                return self._handle_html_validate(task)
            else:
                return self._handle_full_audit(task)
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.verification_evidence = {"error": f"Security agent execution error: {str(e)}"}
            return task

    def _handle_full_audit(self, task: TaskContract) -> TaskContract:
        secrets_report = self.secrets_scanner.scan_directory(self.repo_root)
        html_report = self.html_validator.validate_file(self.repo_root / "index.html")
        dep_report = self.dependency_checker.check_dependencies()

        all_clean = secrets_report.clean and html_report.is_safe and dep_report.clean

        task.status = TaskStatus.VERIFIED if all_clean else TaskStatus.FAILED
        task.verification_evidence = {
            "secrets_clean": secrets_report.clean,
            "files_scanned_for_secrets": secrets_report.total_files_scanned,
            "exposed_secrets_count": len(secrets_report.findings),
            "html_safe": html_report.is_safe,
            "html_violations_count": len(html_report.violations),
            "dependencies_clean": dep_report.clean,
            "broken_dependencies": dep_report.broken_dependencies
        }
        task.expected_output = (
            f"Security Audit Complete: Secrets={'CLEAN' if secrets_report.clean else 'EXPOSED'}, "
            f"HTML={'SAFE' if html_report.is_safe else 'VIOLATIONS'}, "
            f"Deps={'CLEAN' if dep_report.clean else 'CONFLICTS'}"
        )
        return task

    def _handle_secrets_scan(self, task: TaskContract) -> TaskContract:
        report = self.secrets_scanner.scan_directory(self.repo_root)
        task.status = TaskStatus.VERIFIED if report.clean else TaskStatus.FAILED
        task.verification_evidence = {
            "total_files_scanned": report.total_files_scanned,
            "clean": report.clean,
            "findings_count": len(report.findings),
            "findings": [f.redacted_preview for f in report.findings[:5]]
        }
        return task

    def _handle_html_validate(self, task: TaskContract) -> TaskContract:
        target_path_str = task.scope or "index.html"
        target_path = Path(target_path_str)
        if not target_path.is_absolute():
            target_path = self.repo_root / target_path_str

        res = self.html_validator.validate_file(target_path)
        task.status = TaskStatus.VERIFIED if res.is_safe else TaskStatus.FAILED
        task.verification_evidence = {
            "target": target_path_str,
            "is_safe": res.is_safe,
            "violations_count": len(res.violations),
            "violations": [v.description for v in res.violations]
        }
        return task

    def _handle_snapshot_create(self, task: TaskContract) -> TaskContract:
        manifest = self.snapshot_manager.create_snapshot(tag="task_exec")
        task.status = TaskStatus.VERIFIED
        task.verification_evidence = {
            "snapshot_id": manifest.snapshot_id,
            "files_count": manifest.files_count,
            "snapshot_dir": manifest.snapshot_dir
        }
        task.expected_output = f"Created rollback snapshot {manifest.snapshot_id} with {manifest.files_count} files"
        return task
