"""
security_agent.html_safety_validator - Validates HTML for XSS, SSRF, Path Traversal, and Prompt Injection risks.
"""

from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Dict, List, Any


@dataclass
class SafetyViolation:
    rule: str
    severity: str  # HIGH, MEDIUM, LOW
    description: str
    snippet: str


@dataclass
class SafetyAuditResult:
    target: str
    is_safe: bool
    violations: List[SafetyViolation] = field(default_factory=list)


class HtmlSafetyValidator:
    """
    Validates HTML content and web resources for application security threats:
    - XSS: Malicious inline handlers, javascript: URIs, rogue script tags
    - SSRF: Localhost, private RFC1918 IPs, cloud metadata IP (169.254.169.254)
    - Path Traversal: Excessive or illegal '../' escapes in links/assets
    - Prompt Injection: Adversarial override tokens in public or generated text
    """

    PRIVATE_IP_REGEX = re.compile(
        r'\b(?:127\.\d{1,3}\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|'
        r'172\.(?:1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|'
        r'192\.168\.\d{1,3}\.\d{1,3}|169\.254\.\d{1,3}\.\d{1,3}|localhost)\b',
        re.IGNORECASE
    )

    PROMPT_INJECTION_PATTERNS = [
        re.compile(r'ignore\s+(?:all\s+)?previous\s+instructions', re.IGNORECASE),
        re.compile(r'system\s+prompt\s*:', re.IGNORECASE),
        re.compile(r'you\s+are\s+now\s+(?:in\s+)?developer\s+mode', re.IGNORECASE),
        re.compile(r'<\|im_start\|>|<\|im_end\|>', re.IGNORECASE),
    ]

    INLINE_EVENT_HANDLER = re.compile(r'\bon(?:load|error|click|mouseover|focus|blur)\s*=\s*["\'][^"\']*javascript:[^"\']*["\']', re.IGNORECASE)
    JAVASCRIPT_URI = re.compile(r'href\s*=\s*["\']\s*javascript:[^"\']*["\']', re.IGNORECASE)

    SANCTIONED_SCRIPTS = {
        "pagead2.googlesyndication.com",
        "www.googletagmanager.com",
        "app.js",
        "attribution.js",
        "search.js"
    }

    def validate_html(self, html_content: str, target: str = "inline") -> SafetyAuditResult:
        violations: List[SafetyViolation] = []

        # 1. Check for javascript: URI in links
        js_uris = self.JAVASCRIPT_URI.findall(html_content)
        for match in js_uris:
            violations.append(SafetyViolation(
                rule="NO_JAVASCRIPT_URI",
                severity="HIGH",
                description="Detected unsafe javascript: pseudoprotocol URI in hyperlink.",
                snippet=match[:80]
            ))

        # 2. Check for inline event handler with javascript:
        handlers = self.INLINE_EVENT_HANDLER.findall(html_content)
        for h in handlers:
            violations.append(SafetyViolation(
                rule="NO_INLINE_JS_HANDLERS",
                severity="HIGH",
                description="Detected malicious or unsafe inline JavaScript event handler.",
                snippet=h[:80]
            ))

        # 3. Check for SSRF / Private IP destinations in iframes or action URLs
        private_ips = self.PRIVATE_IP_REGEX.findall(html_content)
        for ip in private_ips:
            # Check if inside an iframe src or form action
            if f'src="{ip}' in html_content or f'action="{ip}' in html_content or f'src="http://{ip}' in html_content:
                violations.append(SafetyViolation(
                    rule="NO_SSRF_INTERNAL_DESTINATION",
                    severity="HIGH",
                    description=f"Detected SSRF vulnerability: Reference to private/metadata IP address {ip}.",
                    snippet=f"Target: {ip}"
                ))

        # 4. Check Path Traversal
        traversal_matches = re.findall(r'(?:href|src)\s*=\s*["\'](?:\.\./){3,}[^"\']*["\']', html_content)
        for t in traversal_matches:
            violations.append(SafetyViolation(
                rule="NO_PATH_TRAVERSAL",
                severity="HIGH",
                description="Detected potential path traversal pattern (excessive '../' directory climbing).",
                snippet=t[:80]
            ))

        # 5. Check Prompt Injection
        for p in self.PROMPT_INJECTION_PATTERNS:
            matches = p.findall(html_content)
            for m in matches:
                violations.append(SafetyViolation(
                    rule="NO_PROMPT_INJECTION_TOKENS",
                    severity="MEDIUM",
                    description=f"Detected adversarial prompt injection phrase: '{m}'.",
                    snippet=m
                ))

        is_safe = len([v for v in violations if v.severity == "HIGH"]) == 0

        return SafetyAuditResult(
            target=target,
            is_safe=is_safe,
            violations=violations
        )

    def validate_file(self, file_path: Path) -> SafetyAuditResult:
        if not file_path.exists():
            return SafetyAuditResult(
                target=str(file_path),
                is_safe=False,
                violations=[SafetyViolation("FILE_NOT_FOUND", "HIGH", "File does not exist", str(file_path))]
            )
        content = file_path.read_text(encoding="utf-8", errors="replace")
        return self.validate_html(content, target=str(file_path))
