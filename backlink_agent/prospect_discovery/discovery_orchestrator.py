"""Discovery Orchestrator coordinating all discovery sources and deduplication."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from .competitor_gap_discovery import CompetitorGapDiscoverer
from .deduplication import ProspectDeduplicator
from .directory_discovery import DirectoryDiscoverer
from .github_awesome_discovery import GitHubAwesomeDiscoverer
from .models import DiscoveredProspect
from .technical_publication_discovery import TechnicalPublicationDiscoverer


class DiscoveryOrchestrator:
    """Coordinates multi-channel discovery and deduplication of backlink opportunities."""

    def __init__(
        self,
        deduplicator: Optional[ProspectDeduplicator] = None,
        competitor_discoverer: Optional[CompetitorGapDiscoverer] = None,
        directory_discoverer: Optional[DirectoryDiscoverer] = None,
        github_discoverer: Optional[GitHubAwesomeDiscoverer] = None,
        pub_discoverer: Optional[TechnicalPublicationDiscoverer] = None,
    ):
        self.deduplicator = deduplicator or ProspectDeduplicator()
        self.competitor_discoverer = competitor_discoverer or CompetitorGapDiscoverer()
        self.directory_discoverer = directory_discoverer or DirectoryDiscoverer()
        self.github_discoverer = github_discoverer or GitHubAwesomeDiscoverer()
        self.pub_discoverer = pub_discoverer or TechnicalPublicationDiscoverer()

    def run_discovery(
        self,
        competitor_records: Optional[List[Dict[str, Any]]] = None,
        known_aitoolgems_domains: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Runs full multi-channel discovery, deduplicating prospects across all sources."""
        start_time = datetime.now(timezone.utc).isoformat()
        raw_candidates: List[DiscoveredProspect] = []

        # 1. AI Directories
        dir_candidates = self.directory_discoverer.discover_candidates()
        raw_candidates.extend(dir_candidates)

        # 2. GitHub Awesome Lists
        gh_candidates = self.github_discoverer.discover_candidates()
        raw_candidates.extend(gh_candidates)

        # 3. Technical Publications (/prices/ citations)
        pub_candidates = self.pub_discoverer.discover_candidates()
        raw_candidates.extend(pub_candidates)

        # 4. Competitor Gap Analysis (if records provided or from file)
        if competitor_records:
            comp_candidates = self.competitor_discoverer.ingest_records(
                competitor_records,
                known_aitoolgems_domains=known_aitoolgems_domains,
            )
            raw_candidates.extend(comp_candidates)

        # Deduplicate
        unique_prospects = self.deduplicator.filter_unique(raw_candidates)
        completed_time = datetime.now(timezone.utc).isoformat()

        return {
            "started_at": start_time,
            "completed_at": completed_time,
            "raw_discovered_count": len(raw_candidates),
            "unique_prospects_count": len(unique_prospects),
            "duplicates_filtered": len(raw_candidates) - len(unique_prospects),
            "prospects": unique_prospects,
        }
