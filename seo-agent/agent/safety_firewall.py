#!/usr/bin/env python3
"""
Safety Firewall for AIToolGems Autonomous SEO Growth Agent
----------------------------------------------------------
Production safeguards:
1. Secret redaction in logs, reports, and error messages.
2. Destructive command prevention.
3. Pricing & policy alteration freeze (human sign-off required).
4. Prompt injection detection in untrusted web pages and external text.
5. Production branch protection (least privilege enforcement).
"""

from __future__ import annotations
import re
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field

# Regex patterns for sensitive keys and tokens
SECRET_PATTERNS = [
    re.compile(r"(ghp_[a-zA-Z0-9]{36})", re.IGNORECASE),
    re.compile(r"(github_pat_[a-zA-Z0-9_]{60,})", re.IGNORECASE),
    re.compile(r"(Bearer\s+[a-zA-Z0-9_\-\.]{20,})", re.IGNORECASE),
    re.compile(r"(AIza[0-9A-Za-z-_]{35})", re.IGNORECASE),
    re.compile(r"(ya29\.[0-9A-Za-z-_]+)", re.IGNORECASE),
    re.compile(r"(\b[0-9]{8,12}:[a-zA-Z0-9_-]{35}\b)", re.IGNORECASE),  # Telegram bot token
    re.compile(r"(client_secret[=:]\s*['\"]?[a-zA-Z0-9_\-]{20,}['\"]?)", re.IGNORECASE),
    re.compile(r"(refresh_token[=:]\s*['\"]?[a-zA-Z0-9_\-\/]{20,}['\"]?)", re.IGNORECASE),
    re.compile(r"(password[=:]\s*['\"][^\n'\"]+['\"])", re.IGNORECASE),
    re.compile(r"(-----BEGIN (?:RSA )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA )?PRIVATE KEY-----)"),
]

# Destructive shell/git commands prohibited from automated execution
DESTRUCTIVE_COMMAND_PATTERNS = [
    re.compile(r"\brm\s+-[rf]{1,2}\b", re.IGNORECASE),
    re.compile(r"\bdel\s+(?:\/[a-z]\s+)*[c-z]:\\", re.IGNORECASE),
    re.compile(r"\bformat\s+[c-z]:\b", re.IGNORECASE),
    re.compile(r"\bgit\s+push\s+(?:--force|-f)\b", re.IGNORECASE),
    re.compile(r"\bgit\s+push\s+\S+\s+main\b", re.IGNORECASE),  # Direct push to main
    re.compile(r"\bgit\s+reset\s+--hard\b", re.IGNORECASE),
    re.compile(r"\bdrop\s+(?:table|database|schema)\b", re.IGNORECASE),
    re.compile(r"\btruncate\s+table\b", re.IGNORECASE),
    re.compile(r"\bchmod\s+777\b", re.IGNORECASE),
]

# Prompt injection signatures in untrusted crawled web text
PROMPT_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"system\s*prompt\s*override", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+a(?:n)?\s+(?:unrestricted|different)\s+ai", re.IGNORECASE),
    re.compile(r"exfiltrate\s+(?:secrets|keys|tokens|credentials|passwords)", re.IGNORECASE),
    re.compile(r"print\s+(?:all\s+)?environment\s+variables", re.IGNORECASE),
    re.compile(r"<script>.*?</script>", re.IGNORECASE | re.DOTALL),
]

# Sensitive commercial entities where automated code changes are frozen
PROTECTED_COMMERCIAL_FIELDS = [
    re.compile(r"\"price\"\s*:\s*[\"']?([0-9]+)[\"']?", re.IGNORECASE),
    re.compile(r"data-price\s*=\s*[\"']?([0-9]+)[\"']?", re.IGNORECASE),
    re.compile(r"0323[\s-]*6715731", re.IGNORECASE),  # Official WhatsApp contact
]

@dataclass
class FirewallVerdict:
    allowed: bool
    risk_level: str  # SAFE, LOW, MEDIUM, HIGH, CRITICAL
    blocked_reason: Optional[str] = None
    redacted_output: Optional[str] = None
    flags: List[str] = field(default_factory=list)

class SafetyFirewall:
    """Enforces zero secret leakage, protects production branches, and validates commands."""

    def __init__(self, mode: str = "PR"):
        self.mode = mode.upper()  # AUDIT, PROPOSE, PR

    def redact_secrets(self, text: str) -> str:
        """Redacts sensitive tokens, API keys, and credentials from logs or reports."""
        if not text:
            return ""
        redacted = text
        for pattern in SECRET_PATTERNS:
            redacted = pattern.sub("[REDACTED_SECRET]", redacted)
        return redacted

    def inspect_command(self, command: str) -> FirewallVerdict:
        """Evaluates whether a shell or git command is safe to execute."""
        redacted_cmd = self.redact_secrets(command)

        for pat in DESTRUCTIVE_COMMAND_PATTERNS:
            if pat.search(command):
                return FirewallVerdict(
                    allowed=False,
                    risk_level="CRITICAL",
                    blocked_reason=f"Blocked destructive command matching security policy: {pat.pattern}",
                    redacted_output=redacted_cmd,
                    flags=["DESTRUCTIVE_COMMAND"],
                )

        # In AUDIT mode, only allow non-mutating commands
        if self.mode == "AUDIT":
            mutating_ops = [r"\bgit\s+commit\b", r"\bgit\s+push\b", r"\bwrite\b", r"\bpatch\b"]
            for mop in mutating_ops:
                if re.search(mop, command, re.IGNORECASE):
                    return FirewallVerdict(
                        allowed=False,
                        risk_level="HIGH",
                        blocked_reason=f"Mutating command prohibited in AUDIT mode: {command}",
                        redacted_output=redacted_cmd,
                        flags=["AUDIT_MODE_MUTATION_BLOCKED"],
                    )

        return FirewallVerdict(
            allowed=True,
            risk_level="SAFE",
            redacted_output=redacted_cmd,
        )

    def scan_untrusted_text(self, text: str, source_url: str = "") -> FirewallVerdict:
        """Detects prompt injection attempts or malicious code inside crawled web pages."""
        flags: List[str] = []
        for pat in PROMPT_INJECTION_PATTERNS:
            if pat.search(text):
                flags.append(f"Prompt injection pattern detected: {pat.pattern}")

        if flags:
            return FirewallVerdict(
                allowed=False,
                risk_level="CRITICAL",
                blocked_reason=f"Untrusted content from '{source_url}' contains potential adversarial injection.",
                flags=flags,
            )

        return FirewallVerdict(allowed=True, risk_level="SAFE")

    def validate_diff_for_commercial_freeze(self, diff_text: str) -> FirewallVerdict:
        """Detects automated modifications to pricing or payment numbers without human approval."""
        modified_lines = [
            line.strip()
            for line in diff_text.splitlines()
            if (line.strip().startswith("+") or line.strip().startswith("-"))
            and not line.strip().startswith(("+++", "---"))
        ]
        diff_payload = "\n".join(modified_lines)

        for pat in PROTECTED_COMMERCIAL_FIELDS:
            if pat.search(diff_payload):
                return FirewallVerdict(
                    allowed=False,
                    risk_level="HIGH",
                    blocked_reason="Attempted automated modification of protected commercial pricing or payment route. Human review required.",
                    flags=["COMMERCIAL_PRICE_FREEZE"],
                )

        return FirewallVerdict(allowed=True, risk_level="SAFE")
