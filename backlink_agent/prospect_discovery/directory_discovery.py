"""AI Directory and Software Aggregator Discovery Engine."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from .models import DiscoveredProspect

# Seed registry of verified high-quality directories and aggregator profiles
CURATED_DIRECTORY_SEEDS: List[Dict[str, Any]] = [
    {
        "domain": "saashub.com",
        "name": "SaaSHub Software Directory",
        "submit_url": "https://www.saashub.com/services/submit",
        "directory_class": "directory_class1",
        "pricing_policy": "free_submission",
        "reciprocal_required": False,
        "relevance": 85,
    },
    {
        "domain": "startupnetwork.pk",
        "name": "Startup Network Pakistan",
        "submit_url": "https://startupnetwork.pk/sign-up/",
        "directory_class": "directory_class3",
        "pricing_policy": "free_submission",
        "reciprocal_required": False,
        "relevance": 82,
    },
    {
        "domain": "agentwebmap.com",
        "name": "Agent Web Map (llms.txt Directory)",
        "submit_url": "https://agentwebmap.com/submit",
        "directory_class": "directory_class2",
        "pricing_policy": "free_submission",
        "reciprocal_required": False,
        "relevance": 92,
    },
    {
        "domain": "therundown.ai",
        "name": "The Rundown AI Directory",
        "submit_url": "https://www.therundown.ai/tools/submit",
        "directory_class": "directory_class1",
        "pricing_policy": "editorial_review",
        "reciprocal_required": False,
        "relevance": 88,
    },
    {
        "domain": "toolpilot.ai",
        "name": "ToolPilot AI",
        "submit_url": "https://www.toolpilot.ai/pages/submit-your-ai-tool",
        "directory_class": "directory_class1",
        "pricing_policy": "demands_reciprocal_link",
        "reciprocal_required": True,
        "relevance": 25,
    },
]


class DirectoryDiscoverer:
    """Discovers and validates AI directory submission opportunities."""

    def __init__(self, seeds: Optional[List[Dict[str, Any]]] = None):
        self.seeds = seeds or CURATED_DIRECTORY_SEEDS

    def evaluate_directory_policy(self, seed: Dict[str, Any]) -> Tuple[bool, str]:
        """Evaluates directory eligibility against white-hat trust rules."""
        if seed.get("reciprocal_required", False):
            return False, "Disallowed: Mandatory reciprocal link or badge required"
        if seed.get("pricing_policy") == "paid_only":
            return False, "Disallowed: Paid link placement"
        return True, "Eligible"

    def discover_candidates(self) -> List[DiscoveredProspect]:
        """Evaluates directory registry and emits verified eligible candidates."""
        candidates = []
        for seed in self.seeds:
            eligible, reason = self.evaluate_directory_policy(seed)
            if not eligible:
                continue

            domain = seed.get("domain", "").lower()
            submit_url = seed.get("submit_url", f"https://{domain}")
            dir_class = seed.get("directory_class", "directory_class1")
            prospect_id = f"dir_{hash(domain) & 0xFFFFFFFF:08x}"

            candidates.append(
                DiscoveredProspect(
                    prospect_id=prospect_id,
                    source_id="curated_directory_registry",
                    prospect_domain=domain,
                    prospect_url=f"https://{domain}",
                    source_page_url=submit_url,
                    prospect_type=dir_class,
                    target_asset_url="https://aitoolgems.tech/",
                    relevance_hint=int(seed.get("relevance", 70)),
                    metadata={
                        "directory_name": seed.get("name"),
                        "pricing_policy": seed.get("pricing_policy"),
                        "submission_url": submit_url,
                    },
                )
            )

        return candidates
