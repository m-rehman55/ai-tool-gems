"""
security_agent.dependency_checker - Audits environment dependencies and supply-chain integrity.
"""

from dataclasses import dataclass, field
import subprocess
import sys
from typing import Dict, List, Any


@dataclass
class DependencyAuditResult:
    clean: bool
    broken_dependencies: List[str] = field(default_factory=list)
    raw_output: str = ""


class DependencyChecker:
    """
    Checks python environment dependencies for broken requirements or conflicts via 'pip check'.
    """

    def check_dependencies(self) -> DependencyAuditResult:
        try:
            res = subprocess.run(
                [sys.executable, "-m", "pip", "check"],
                capture_output=True,
                text=True,
                timeout=15
            )
            raw = (res.stdout + "\n" + res.stderr).strip()
            clean = (res.returncode == 0)
            broken = [line for line in raw.splitlines() if line and "No broken requirements found" not in line]

            return DependencyAuditResult(
                clean=clean,
                broken_dependencies=broken if not clean else [],
                raw_output=raw
            )
        except Exception as e:
            return DependencyAuditResult(
                clean=False,
                broken_dependencies=[f"Execution error: {str(e)}"],
                raw_output=str(e)
            )
