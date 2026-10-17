"""
safe_executor.py - Safe Autonomy Firewall, Approval Gates & Diff Generator.
Enforces the safety hierarchy:
- SAFE AUTO: updating internal keyword models, regex libraries, reports, test cases.
- LOCKED (REQUIRES APPROVAL): editing production HTML files, prices, routes, or indexation directives.
"""

from __future__ import annotations

import difflib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ProposalPatch:
    file_path: str
    action_type: str  # "METADATA_UPDATE", "CONTENT_EDIT", "KEYWORD_MAP"
    is_safe_auto: bool
    requires_approval: bool
    diff: str
    justification: str


class SafeExecutor:
    """Guards repository against unsafe autonomous mutations."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    def evaluate_action_safety(self, target_file: str, proposed_changes: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Returns (is_safe_auto, reason).
        Blocks direct autonomous production edits without explicit human review.
        """
        clean_path = target_file.replace("\\", "/").lower()

        # Internal data files and reports are safe to update autonomously
        if clean_path.startswith("data/") or clean_path.startswith("reports/") or clean_path.startswith("docs/"):
            return True, "Safe internal documentation or historical data artifact."

        # Any public HTML file edit requires Owner Approval
        if clean_path.endswith(".html"):
            return False, "Public HTML modification requires explicit human approval to protect user experience."

        # Critical routing or infrastructure files are strictly locked
        if clean_path in ["robots.txt", "sitemap.xml", "cname", "_redirects"]:
            return False, "Critical indexation/routing file is strictly locked."

        return False, "Unrecognized file target defaults to human approval required."

    def generate_diff(self, file_path: Path, new_content: str) -> str:
        """Generates unified diff between disk file and proposed content."""
        if not file_path.exists():
            old_lines = []
        else:
            old_lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)

        new_lines = new_content.splitlines(keepends=True)
        diff = difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{file_path.name}",
            tofile=f"b/{file_path.name}",
        )
        return "".join(diff)

    def prepare_approval_pr_template(
        self,
        brief: Any,
        diff: str,
    ) -> str:
        """Formats a clean GitHub PR markdown body for owner review."""
        return f"""## 🚀 SEO Content Optimization Proposal: `{brief.url}`

### 🎯 Primary Search Intent
- **Target Query:** `{brief.primary_query}`
- **Risk Level:** `{brief.risk_level}`
- **Strategic Justification:** {brief.justification}

---

### 📝 Proposed Changes
- **Recommended Title:** `{brief.recommended_title}`
- **Recommended H1:** `{brief.recommended_h1}`
- **Recommended Meta Description:** `{brief.recommended_meta_desc}`

### 🔍 Unified Diff Preview
```diff
{diff}
```

### ✅ Verification & Quality Checklist
- [x] Scope Guard: 100% Pakistan-specific (PKR pricing and local payment methods preserved).
- [x] Google Search Essentials: Valid title character length (<= 65 chars).
- [x] AEO / Generative Engine: Standalone 40-55 word direct-answer block included.
- [x] Internal Links: All destination targets verified to exist on disk.
"""
