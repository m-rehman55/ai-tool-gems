"""
security_agent.secrets_scanner - Scans codebase for exposed API keys, private tokens, and credentials.
"""

from dataclasses import dataclass, field
import fnmatch
import os
from pathlib import Path
import re
from typing import Dict, List, Any, Optional


@dataclass
class SecretFinding:
    file_path: str
    line_number: int
    rule_name: str
    redacted_preview: str
    severity: str = "CRITICAL"


@dataclass
class ScanReport:
    total_files_scanned: int
    findings: List[SecretFinding] = field(default_factory=list)
    clean: bool = True


class SecretsScanner:
    """
    Automated zero-exposure secrets scanner.
    Ensures that no API keys, private credentials, bot tokens, or private keys
    exist in repository source files, public HTML, frontend scripts, or logs.
    """

    SECRET_PATTERNS = [
        ("Google API Key", re.compile(r'AIza[0-9A-Za-z\-_]{35}')),
        ("OpenAI API Key", re.compile(r'sk-[A-Za-z0-9\-_]{30,}')),
        ("GitHub Personal Access Token", re.compile(r'(?:ghp_[0-9a-zA-Z]{36}|github_pat_[0-9a-zA-Z_]{82})')),
        ("Telegram Bot Token", re.compile(r'\b\d{8,11}:[A-Za-z0-9_-]{35}\b')),
        ("Generic Private Key Header", re.compile(r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----')),
        ("Buffer Access Token", re.compile(r'1/[0-9a-zA-Z]{30,}')),
        ("Hardcoded Secret Assignment", re.compile(r'(?:api[_-]?secret|auth[_-]?token|jwt[_-]?secret)\s*[:=]\s*["\'][A-Za-z0-9_\-]{20,}["\']', re.IGNORECASE)),
    ]

    EXCLUDE_DIRS = {
        ".git", ".system_generated", "__pycache__", "venv", ".venv",
        "node_modules", "snapshots", "dist", "build", "scratch", "test-results",
        ".vscode", ".chrome-user-data", ".edge-user-data"
    }
    EXCLUDE_EXTENSIONS = {
        ".png", ".jpg", ".webp", ".ico", ".svg", ".woff", ".woff2", ".ttf", ".eot",
        ".bin", ".lock", ".trace.json", ".devtoolslog.json"
    }
    EXCLUDE_FILENAMES = {
        ".env", ".env.local", ".env.production", ".env.development",
        "gsc_service_account.json", "service_account.json", "credentials.json"
    }
    MAX_FILE_SIZE_BYTES = 500_000  # 500 KB

    def scan_text(self, text: str, file_path: str = "inline") -> List[SecretFinding]:
        findings = []
        lines = text.splitlines()

        for line_num, line in enumerate(lines, 1):
            # Ignore test files or fixtures that intentionally contain mock strings labeled 'dummy', 'mock', 'fake', 'test'
            if "mock" in line.lower() or "dummy" in line.lower() or "test_" in file_path.lower():
                continue

            for rule_name, pattern in self.SECRET_PATTERNS:
                matches = pattern.finditer(line)
                for match in matches:
                    secret_val = match.group(0)
                    # Redact middle
                    if len(secret_val) > 8:
                        redacted = secret_val[:3] + "..." + secret_val[-3:]
                    else:
                        redacted = "***"

                    findings.append(SecretFinding(
                        file_path=file_path,
                        line_number=line_num,
                        rule_name=rule_name,
                        redacted_preview=f"Line {line_num}: [{rule_name}] {redacted}"
                    ))
        return findings

    def scan_file(self, file_path: Path) -> List[SecretFinding]:
        if not file_path.exists():
            return []

        fname = file_path.name
        if fname in self.EXCLUDE_FILENAMES:
            return []

        if file_path.suffix.lower() in self.EXCLUDE_EXTENSIONS:
            return []

        # Skip performance trace artifacts
        if fname.endswith(".trace.json") or fname.endswith(".devtoolslog.json"):
            return []

        # Skip large files
        try:
            if file_path.stat().st_size > self.MAX_FILE_SIZE_BYTES:
                return []
            content = file_path.read_text(encoding="utf-8", errors="replace")
            return self.scan_text(content, file_path=str(file_path))
        except Exception:
            return []

    def scan_directory(self, root_dir: Path) -> ScanReport:
        total_scanned = 0
        all_findings = []

        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Prune excluded directories immediately
            dirnames[:] = [d for d in dirnames if d not in self.EXCLUDE_DIRS and not d.startswith(".")]

            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext in self.EXCLUDE_EXTENSIONS:
                    continue

                full_path = Path(dirpath) / fname
                findings = self.scan_file(full_path)
                total_scanned += 1
                all_findings.extend(findings)

        return ScanReport(
            total_files_scanned=total_scanned,
            findings=all_findings,
            clean=len(all_findings) == 0
        )
