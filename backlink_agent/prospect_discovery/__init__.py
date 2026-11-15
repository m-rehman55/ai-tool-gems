"""Prospect Discovery module for the Backlink Intelligence Engine."""

from .competitor_gap_discovery import CompetitorGapDiscoverer
from .deduplication import ProspectDeduplicator
from .directory_discovery import DirectoryDiscoverer
from .github_awesome_discovery import GitHubAwesomeDiscoverer
from .models import DiscoveredProspect, DiscoverySource, normalize_url
from .technical_publication_discovery import TechnicalPublicationDiscoverer
from .discovery_orchestrator import DiscoveryOrchestrator

__all__ = [
    "CompetitorGapDiscoverer",
    "DirectoryDiscoverer",
    "DiscoveredProspect",
    "DiscoveryOrchestrator",
    "DiscoverySource",
    "GitHubAwesomeDiscoverer",
    "ProspectDeduplicator",
    "TechnicalPublicationDiscoverer",
    "normalize_url",
]
