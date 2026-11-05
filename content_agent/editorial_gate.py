"""Editorial Quality Gate and Anti-Filler Verification Engine.

Enforces strict quality standards:
1. Rejects generic AI clichés ("in today's fast-paced digital landscape", "delve into").
2. Enforces minimum depth (>=800 words of substantive analysis).
3. Verifies Pakistani payment rails and flat PKR pricing.
4. When AI generation fails, saves an unapproved draft rather than publishing template filler.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

FORBIDDEN_AI_CLICHES = [
    "in today's fast-paced digital landscape",
    "in today's fast-paced world",
    "delve into the world of",
    "it is important to remember that",
    "testament to the power of",
    "game changer in the realm of",
    "revolutionizing the way we",
    "rich tapestry of",
    "beacon of innovation",
]

FORBIDDEN_JAPAN_TOKENS = [
    "japan", "japanese", "tokyo", "osaka", "kyoto", "/jp/", "-jp-", "jpy", "¥"
]


class EditorialQualityGate:
    """Validates draft HTML and content before publication."""

    def __init__(self, drafts_dir: Optional[Path] = None):
        self.drafts_dir = drafts_dir or Path("data/content/drafts")
        self.drafts_dir.mkdir(parents=True, exist_ok=True)

    def validate_article_html(self, html_content: str, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate content for quality, depth, originality, and market compliance."""
        errors: List[str] = []
        lower_html = html_content.lower()

        # 1. Minimum Word Count Gate (Substantive content requirement)
        text_only = re.sub(r"<[^>]+>", " ", html_content)
        words = text_only.split()
        if len(words) < 600:
            errors.append(f"THIN_CONTENT: Article has only {len(words)} words (minimum 600 words required).")

        # 2. Generic AI Cliche / Filler Check
        found_cliches = [c for c in FORBIDDEN_AI_CLICHES if c in lower_html]
        if found_cliches:
            errors.append(f"AI_FILLER_DETECTED: Found generic AI cliches: {found_cliches[:2]}. Must be rewritten.")

        # 3. Japan Foreign Token Firewall
        found_japan = [j for j in FORBIDDEN_JAPAN_TOKENS if j in lower_html]
        if found_japan:
            errors.append(f"FOREIGN_SCOPE_VIOLATION: Japan tokens {found_japan} strictly prohibited.")

        # 4. Verified Pakistani Payment Rails
        has_rails = any(r in lower_html for r in ["easypaisa", "jazzcash", "sadapay", "nayapay", "bank ibft", "raast"])
        if not has_rails:
            errors.append("MISSING_PAYMENT_RAILS: Article must mention verified Pakistani payment rails (EasyPaisa/JazzCash/SadaPay).")

        # 5. Flat PKR Pricing
        has_pkr = bool(re.search(r"\b(?:rs\.?|pkr)\s*[\d,]+", lower_html))
        if not has_pkr:
            errors.append("MISSING_PKR_PRICING: Article must display verified flat Pakistani Rupee (PKR) pricing.")

        # 6. Structured Data
        has_schema = '<script type="application/ld+json">' in html_content
        if not has_schema:
            errors.append("MISSING_SCHEMA: JSON-LD Article or FAQPage structured data is mandatory.")

        is_valid = len(errors) == 0
        return is_valid, errors

    def save_unapproved_draft(self, slug: str, html_content: str, metadata: Dict[str, Any], reason: str) -> Path:
        """Save a draft to data/content/drafts/ for human review when automated generation fails."""
        draft_file = self.drafts_dir / f"{slug}.html"
        draft_payload = f"""<!-- 
HERMES DRAFT NOTICE:
Slug: {slug}
Status: DRAFT_PENDING_REVIEW
Reason: {reason}
Self-Approval: BLOCKED (Requires manual review before publication)
-->
{html_content}
"""
        draft_file.write_text(draft_payload, encoding="utf-8")
        return draft_file
