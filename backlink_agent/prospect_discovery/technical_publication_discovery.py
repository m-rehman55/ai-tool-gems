"""Technical Publication and Data Citation Discovery Engine."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import DiscoveredProspect

CURATED_TECH_PUBLICATIONS: List[Dict[str, Any]] = [
    {
        "platform": "dev.to",
        "name": "Dev.to Developer Community",
        "domain": "dev.to",
        "citation_target": "https://aitoolgems.tech/prices/",
        "angle": "Open Data & Python Scraping: Documenting Pakistani AI Software Pricing",
        "relevance": 85,
    },
    {
        "platform": "hashnode.com",
        "name": "Hashnode Engineering Blog",
        "domain": "hashnode.com",
        "citation_target": "https://aitoolgems.tech/prices/",
        "angle": "Engineering Technical Guide: Building a Machine-Readable AI Pricing Index (CSV/JSON/llms.txt)",
        "relevance": 83,
    },
    {
        "platform": "medium.com",
        "name": "Medium Tech Publications",
        "domain": "medium.com",
        "citation_target": "https://aitoolgems.tech/prices/",
        "angle": "AI Industry Economics: Software Subscription Costs Across Emerging South Asian Markets",
        "relevance": 80,
    },
]


class TechnicalPublicationDiscoverer:
    """Discovers editorial and developer publication citation opportunities for /prices/ datasets."""

    def __init__(self, platforms: Optional[List[Dict[str, Any]]] = None):
        self.platforms = platforms or CURATED_TECH_PUBLICATIONS

    def discover_candidates(self) -> List[DiscoveredProspect]:
        """Emits citation prospects targeting technical case studies and open datasets."""
        candidates = []
        for p in self.platforms:
            domain = p.get("domain", "")
            target = p.get("citation_target", "https://aitoolgems.tech/prices/")
            prospect_id = f"pub_{hash(domain) & 0xFFFFFFFF:08x}"

            candidates.append(
                DiscoveredProspect(
                    prospect_id=prospect_id,
                    source_id="tech_publication_registry",
                    prospect_domain=domain,
                    prospect_url=f"https://{domain}",
                    source_page_url=f"https://{domain}",
                    prospect_type="tech_publication",
                    target_asset_url=target,
                    relevance_hint=int(p.get("relevance", 80)),
                    metadata={
                        "platform_name": p.get("name"),
                        "editorial_angle": p.get("angle"),
                        "citation_target": target,
                    },
                )
            )

        return candidates
