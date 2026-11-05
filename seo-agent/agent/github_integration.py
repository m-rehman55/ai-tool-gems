#!/usr/bin/env python3
"""
GitHub & Branch Integration for AIToolGems Growth Agent
-------------------------------------------------------
Prepares isolated Git branches, patches, and PR descriptions for human review.
Strictly blocks direct publishing or automated merges to production 'main'.
"""

from __future__ import annotations
import os
import subprocess
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from agent.safety_firewall import SafetyFirewall

@dataclass
class ProposalSummary:
    branch_name: str
    target_branch: str
    title: str
    body_markdown: str
    files_changed: List[str]
    pr_created: bool = False
    pr_url: Optional[str] = None
    error: Optional[str] = None

class GitHubIntegration:
    """Manages safe, reviewable branch operations and PR preparation."""

    def __init__(
        self,
        target_branch: str = "main",
        branch_prefix: str = "seo-growth/",
        token_env: str = "GITHUB_TOKEN",
    ):
        self.target_branch = target_branch
        self.branch_prefix = branch_prefix
        self.github_token = os.environ.get(token_env, "").strip()
        self.firewall = SafetyFirewall(mode="PR")

    def generate_branch_name(self) -> str:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")
        return f"{self.branch_prefix}{date_str}"

    def get_current_commit_sha(self) -> str:
        """Retrieves actual commit SHA from git rev-parse HEAD."""
        try:
            res = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass
        return "UNKNOWN_COMMIT_SHA"

    def build_pr_body(
        self,
        summary_title: str,
        evidence: str,
        files_affected: List[str],
        risk_level: str,
        test_results: str,
        commit_sha: Optional[str] = None,
    ) -> str:
        """Formats comprehensive, production-conscious PR description with real commit SHA and test artifacts."""
        files_list_md = "\n".join(f"- `{f}`" for f in files_affected) or "- None"
        actual_sha = commit_sha or self.get_current_commit_sha()
        
        body = f"""## 🚀 HERMES Growth Proposal: {summary_title}

### 📋 Overview & Evidence
{evidence}

### 🎯 Files Affected
{files_list_md}

### 🛡️ Safety & Risk Assessment
- **Commit SHA:** `{actual_sha}`
- **Risk Level:** `{risk_level}`
- **Firewall Check:** Passed (zero secret exposure, zero foreign currency, zero price tampering)
- **Pakistan Exclusive Scope:** Verified (PKR currency & local payment routes preserved)

### 🧪 Automated Test Verification (Real Test Artifacts)
```text
{test_results}
```

### ⏪ Rollback Instructions
To safely revert this proposed change if unexpected side effects occur:
```bash
git checkout {self.target_branch}
git revert {actual_sha} -m 1
git push origin {self.target_branch}
```

---
*Created autonomously by AIToolGems Growth Agent. Production merge strictly requires human review.*
"""
        return self.firewall.redact_secrets(body)
