"""
query_fanout.py - Analyzes Google's Query Fan-Out Intent Coverage.
According to official Google Search Central documentation, generative search models
use 'query fan-out' to break down complex user searches into multiple sub-questions.
This module verifies whether a given page provides direct answers across all 5 key fan-out vectors:
1. Commercial Pricing Vector: "How much does it cost in Pakistan (PKR)?"
2. Payment Rails Vector: "Can I pay using EasyPaisa, JazzCash, or SadaPay?"
3. Fulfillment Vector: "How is access delivered or activated?"
4. Trust & Warranty Vector: "Is there a replacement warranty or refund guarantee?"
5. Comparison/Feature Vector: "Who is this best for and how does it compare to alternatives?"
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Set


@dataclass
class FanOutBranchResult:
    branch_name: str
    description: str
    is_satisfied: bool
    matched_snippet: Optional[str] = None


@dataclass
class QueryFanOutAnalysis:
    file_path: str
    url_slug: str
    branches: Dict[str, FanOutBranchResult] = field(default_factory=dict)
    coverage_percentage: float = 0.0  # 0 to 100%
    missing_branches: List[str] = field(default_factory=list)


class QueryFanOutAnalyzer:
    """Evaluates how effectively an HTML document satisfies Google AI Overviews query fan-out branches."""

    BRANCH_PATTERNS = {
        "pricing_in_pkr": {
            "desc": "Verified pricing in Pakistani Rupees (PKR / Rs.)",
            "regex": r"(?i)\b(?:Rs\.?|PKR)\s*[\d,]+",
        },
        "domestic_payment_rails": {
            "desc": "Domestic payment options (EasyPaisa, JazzCash, SadaPay, Bank IBFT)",
            "regex": r"(?i)\b(?:EasyPaisa|JazzCash|SadaPay|Nayapay|Bank\s+IBFT|Raast)\b",
        },
        "fulfillment_delivery": {
            "desc": "Clear delivery timeline & manual order verification on WhatsApp",
            "regex": r"(?i)\b(?:delivery|confirmation|order\s+verification|dispatch|activation)\b",
        },
        "trust_warranty": {
            "desc": "Explicit replacement warranty or customer protection policy",
            "regex": r"(?i)\b(?:warranty|replacement|guarantee|7-day|30-day|policies\.html)\b",
        },
        "comparison_use_cases": {
            "desc": "Audience fit, features included, or comparison with alternatives",
            "regex": r"(?i)\b(?:best\s+for|comparison|compare|alternatives?|features|included)\b",
        },
    }

    def analyze_file(self, file_path: Path) -> QueryFanOutAnalysis:
        content = file_path.read_text(encoding="utf-8")
        slug = file_path.parent.name if file_path.name == "index.html" else file_path.stem

        results: Dict[str, FanOutBranchResult] = {}
        missing: List[str] = []
        satisfied_count = 0

        for key, config in self.BRANCH_PATTERNS.items():
            match = re.search(config["regex"], content)
            satisfied = bool(match)
            snippet = None
            if match:
                start = max(0, match.start() - 20)
                end = min(len(content), match.end() + 20)
                snippet = re.sub(r"\s+", " ", content[start:end]).strip()
                satisfied_count += 1
            else:
                missing.append(config["desc"])

            results[key] = FanOutBranchResult(
                branch_name=key,
                description=config["desc"],
                is_satisfied=satisfied,
                matched_snippet=snippet,
            )

        total_branches = len(self.BRANCH_PATTERNS)
        coverage_pct = round((satisfied_count / total_branches) * 100.0, 1)

        return QueryFanOutAnalysis(
            file_path=str(file_path),
            url_slug=slug,
            branches=results,
            coverage_percentage=coverage_pct,
            missing_branches=missing,
        )
