#!/usr/bin/env python3
"""
Scope Guard for AIToolGems Autonomous SEO Growth Agent
------------------------------------------------------
Enforces 100% Pakistan-exclusive operational scope for commercial activities
and strictly blocks any foreign currency or Japan (JP) related material.
"""

from __future__ import annotations
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

# Japanese Unicode character ranges (Hiragana, Katakana, CJK Unified Ideographs)
JAPANESE_CHAR_REGEX = re.compile(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]")

# Prohibited tokens & patterns indicating Japan or foreign contamination
PROHIBITED_PATTERNS = [
    (re.compile(r"\bJPY\b", re.IGNORECASE), "Prohibited currency token: JPY"),
    (re.compile(r"¥"), "Prohibited currency symbol: ¥ (Yen)"),
    (re.compile(r"\b(japanese\s+yen|yen\s+currency)\b", re.IGNORECASE), "Prohibited currency name: Japanese Yen"),
    (re.compile(r"/(?:jp|japan)(?:/|$|\.html)", re.IGNORECASE), "Prohibited JP route or URL slug"),
    (re.compile(r"\b(tokyo|osaka|kyoto|shibuya|shinjuku)\b", re.IGNORECASE), "Prohibited Japanese city/locality reference"),
    (re.compile(r"lang=[\"']ja(?:-[A-Z]{2})?[\"']", re.IGNORECASE), "Prohibited Japanese language tag"),
    (re.compile(r"hreflang=[\"']ja(?:-[A-Z]{2})?[\"']", re.IGNORECASE), "Prohibited Japanese hreflang attribute"),
]

# Required local Pakistan signals for commercial/transactional pages
PAKISTAN_SIGNALS = {
    "currency": [r"\bpkr\b", r"\brs\.?\b", r"rupees"],
    "payment": [r"easypaisa", r"jazzcash", r"bank\s+transfer", r"sadapay", r"nayapay"],
    "country": [r"pakistan", r"karachi", r"lahore", r"islamabad", r"rawalpindi", r"faisalabad"],
}

@dataclass
class ScopeViolation:
    rule: str
    message: str
    snippet: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None

@dataclass
class ScopeResult:
    passed: bool
    violations: List[ScopeViolation] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "violations_count": len(self.violations),
            "violations": [
                {
                    "rule": v.rule,
                    "message": v.message,
                    "snippet": v.snippet,
                    "file_path": v.file_path,
                    "line_number": v.line_number,
                }
                for v in self.violations
            ],
            "warnings": self.warnings,
        }

class ScopeGuard:
    """Enforces exclusive Pakistan scope and eliminates foreign / JP contamination."""

    def __init__(self, strict_local_signals: bool = True):
        self.strict_local_signals = strict_local_signals

    def check_text(self, text: str, context_name: str = "text") -> ScopeResult:
        """Inspects arbitrary text content for scope violations."""
        violations: List[ScopeViolation] = []
        warnings: List[str] = []

        if not text:
            return ScopeResult(passed=True)

        lines = text.splitlines()
        for idx, line in enumerate(lines, start=1):
            # Check Japanese script characters
            if JAPANESE_CHAR_REGEX.search(line):
                # Avoid false positives if line is explicitly discussing anti-JP filters
                if "anti-jp" not in line.lower() and "prohibited" not in line.lower() and "filter" not in line.lower():
                    violations.append(
                        ScopeViolation(
                            rule="NO_JAPANESE_SCRIPT",
                            message="Japanese script character detected",
                            snippet=line.strip()[:120],
                            file_path=context_name,
                            line_number=idx,
                        )
                    )

            # Check prohibited regex patterns
            for pattern, desc in PROHIBITED_PATTERNS:
                # Exclude self-referential test/guard statements
                if "prohibited" in line.lower() or "scope_guard" in line.lower() or "exclude" in line.lower():
                    continue
                match = pattern.search(line)
                if match:
                    violations.append(
                        ScopeViolation(
                            rule="PROHIBITED_TOKEN",
                            message=desc,
                            snippet=line.strip()[:120],
                            file_path=context_name,
                            line_number=idx,
                        )
                    )

        passed = len(violations) == 0
        return ScopeResult(passed=passed, violations=violations, warnings=warnings)

    def check_url(self, url: str) -> ScopeResult:
        """Inspects a target URL to ensure it belongs to aitoolgems.tech and has no JP paths."""
        violations: List[ScopeViolation] = []
        clean_url = url.strip()

        # Reject foreign / JP paths
        for pattern, desc in PROHIBITED_PATTERNS:
            if pattern.search(clean_url):
                violations.append(
                    ScopeViolation(
                        rule="PROHIBITED_URL_PATH",
                        message=f"{desc} in URL: {clean_url}",
                        snippet=clean_url,
                    )
                )

        # Ensure domain matches or is relative
        if clean_url.startswith("http://") or clean_url.startswith("https://"):
            if not re.search(r"https?://(?:www\.)?aitoolgems\.tech", clean_url, re.IGNORECASE):
                violations.append(
                    ScopeViolation(
                        rule="FOREIGN_DOMAIN",
                        message=f"Target URL is outside aitoolgems.tech domain: {clean_url}",
                        snippet=clean_url,
                    )
                )

        return ScopeResult(passed=len(violations) == 0, violations=violations)

    def check_transactional_page(self, html_content: str, url_or_path: str = "") -> ScopeResult:
        """Validates that a commercial/transactional page contains mandatory Pakistani signals."""
        violations: List[ScopeViolation] = []
        warnings: List[str] = []

        # First check text for foreign tokens
        base_result = self.check_text(html_content, context_name=url_or_path)
        violations.extend(base_result.violations)

        content_lower = html_content.lower()

        # Verify PKR currency signal
        has_currency = any(re.search(pat, content_lower) for pat in PAKISTAN_SIGNALS["currency"])
        if not has_currency:
            violations.append(
                ScopeViolation(
                    rule="MISSING_PKR_CURRENCY",
                    message="Transactional page is missing PKR/Rs currency signal",
                    file_path=url_or_path,
                )
            )

        # Verify Pakistani payment route
        has_payment = any(re.search(pat, content_lower) for pat in PAKISTAN_SIGNALS["payment"])
        if not has_payment:
            violations.append(
                ScopeViolation(
                    rule="MISSING_PAKISTAN_PAYMENT",
                    message="Transactional page is missing EasyPaisa/JazzCash payment signal",
                    file_path=url_or_path,
                )
            )

        return ScopeResult(passed=len(violations) == 0, violations=violations, warnings=warnings)

    def scan_file(self, file_path: Path | str) -> ScopeResult:
        """Scans a file on disk for scope violations."""
        path = Path(file_path)
        if not path.exists():
            return ScopeResult(
                passed=False,
                violations=[ScopeViolation(rule="FILE_NOT_FOUND", message=f"File not found: {path}")],
            )

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return self.check_text(content, context_name=str(path))
        except Exception as e:
            return ScopeResult(
                passed=False,
                violations=[ScopeViolation(rule="READ_ERROR", message=f"Failed to read file: {e}", file_path=str(path))],
            )
