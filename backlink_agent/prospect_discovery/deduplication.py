"""Deduplication and canonical identity engine for Backlink Prospects."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Set

from .models import DiscoveredProspect, normalize_url


class ProspectDeduplicator:
    """Detects and filters out duplicate prospects using canonical composite identities."""

    def __init__(self, existing_identities: Optional[Iterable[str]] = None):
        self._seen_identities: Set[str] = set(existing_identities or [])
        self._seen_domains_and_targets: Set[str] = set()

    def is_duplicate(self, prospect: DiscoveredProspect) -> bool:
        """Checks if prospect has already been discovered or recorded."""
        identity = prospect.canonical_identity
        if identity in self._seen_identities:
            return True
        return False

    def register(self, prospect: DiscoveredProspect) -> bool:
        """Registers a prospect if new, returning True if accepted or False if duplicate."""
        if self.is_duplicate(prospect):
            return False
        self._seen_identities.add(prospect.canonical_identity)
        norm_domain = normalize_url(prospect.prospect_domain)
        norm_target = normalize_url(prospect.target_asset_url)
        self._seen_domains_and_targets.add(f"{norm_domain}|{norm_target}")
        return True

    def filter_unique(self, prospects: List[DiscoveredProspect]) -> List[DiscoveredProspect]:
        """Filters a batch of discovered prospects, returning only unique new items."""
        unique_prospects = []
        for p in prospects:
            if self.register(p):
                unique_prospects.append(p)
        return unique_prospects

    @property
    def seen_count(self) -> int:
        return len(self._seen_identities)
