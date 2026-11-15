"""GitHub Awesome List Discovery and Contribution Guideline Analyzer."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from .models import DiscoveredProspect

CURATED_GITHUB_REPOS: List[Dict[str, Any]] = [
    {
        "repo_url": "https://github.com/eudk/awesome-ai-tools",
        "repo_name": "eudk/awesome-ai-tools",
        "target_file": "README.md",
        "allowed_categories": ["AI Tool Resources & Directories", "Directories"],
        "allows_directories": True,
        "relevance": 88,
    },
    {
        "repo_url": "https://github.com/steven2358/awesome-generative-ai",
        "repo_name": "steven2358/awesome-generative-ai",
        "target_file": "README.md",
        "allowed_categories": ["Directories & Search", "Tools"],
        "allows_directories": True,
        "relevance": 85,
    },
    {
        "repo_url": "https://github.com/filipecalegario/awesome-generative-ai",
        "repo_name": "filipecalegario/awesome-generative-ai",
        "target_file": "README.md",
        "allowed_categories": ["Directories & Aggregators", "Platforms"],
        "allows_directories": True,
        "relevance": 88,
    },
    {
        "repo_url": "https://github.com/OuterSpacee/awesome-ai-tools",
        "repo_name": "OuterSpacee/awesome-ai-tools",
        "target_file": "README.md",
        "allowed_categories": ["Audio", "Video", "Text"],
        "allows_directories": False,  # Category mismatch identified during prior audit
        "relevance": 45,
    },
]


class GitHubAwesomeDiscoverer:
    """Discovers PR-eligible GitHub Awesome lists with matching directory categories."""

    def __init__(self, repos: Optional[List[Dict[str, Any]]] = None):
        self.repos = repos or CURATED_GITHUB_REPOS

    def is_eligible_repository(self, repo_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Checks if repo accepts software directory or pricing resource submissions."""
        if not repo_info.get("allows_directories", False):
            return False, "Ineligible: Repository contribution rules disallow directory/aggregator submissions"
        return True, "Eligible"

    def discover_candidates(self) -> List[DiscoveredProspect]:
        """Scans repository registry and emits eligible Awesome list prospects."""
        candidates = []
        for r in self.repos:
            eligible, reason = self.is_eligible_repository(r)
            if not eligible:
                continue

            repo_name = r.get("repo_name", "")
            repo_url = r.get("repo_url", "")
            prospect_id = f"gh_{hash(repo_name) & 0xFFFFFFFF:08x}"

            candidates.append(
                DiscoveredProspect(
                    prospect_id=prospect_id,
                    source_id="github_awesome_registry",
                    prospect_domain="github.com",
                    prospect_url=repo_url,
                    source_page_url=f"{repo_url}/blob/main/{r.get('target_file', 'README.md')}",
                    prospect_type="github_awesome",
                    target_asset_url="https://aitoolgems.tech/",
                    relevance_hint=int(r.get("relevance", 75)),
                    metadata={
                        "repo_name": repo_name,
                        "target_file": r.get("target_file", "README.md"),
                        "allowed_categories": r.get("allowed_categories", []),
                    },
                )
            )

        return candidates
