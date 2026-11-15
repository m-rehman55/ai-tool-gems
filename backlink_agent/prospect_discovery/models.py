"""Data models for Prospect Discovery in the Backlink Intelligence Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse, urlunparse


def normalize_url(url: str) -> str:
    """Normalizes URL for canonical identity and deduplication."""
    if not url:
        return ""
    url = url.strip()
    if not (url.startswith("http://") or url.startswith("https://")):
        url = "https://" + url
    parsed = urlparse(url)
    scheme = "https" if parsed.scheme in ("http", "https") else parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = parsed.path.rstrip("/")
    return urlunparse((scheme, netloc, path, "", "", ""))


@dataclass
class DiscoverySource:
    """Represents an external discovery source (directory list, competitor export, RSS feed)."""

    id: str
    source_type: str  # competitor_gap, directory_index, github_awesome, tech_publication
    source_name: str
    source_url: str
    access_method: str  # local_file, public_api, static_crawl
    enabled: bool = True
    last_run_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_type": self.source_type,
            "source_name": self.source_name,
            "source_url": self.source_url,
            "access_method": self.access_method,
            "enabled": self.enabled,
            "last_run_at": self.last_run_at,
            "metadata": self.metadata,
        }


@dataclass
class DiscoveredProspect:
    """Represents a discovered candidate prospect before evidence verification and scoring."""

    prospect_id: str
    source_id: str
    prospect_domain: str
    prospect_url: str
    source_page_url: str
    prospect_type: str  # directory_class1, directory_class2, directory_class3, github_awesome, tech_publication, competitor_backlink
    target_asset_url: str = "https://aitoolgems.tech/"
    competitor_domain: Optional[str] = None
    relevance_hint: int = 50
    discovered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def canonical_identity(self) -> str:
        """Composite canonical identity for deduplication."""
        norm_source = normalize_url(self.source_page_url or self.prospect_url)
        norm_target = normalize_url(self.target_asset_url)
        key = f"{norm_source}|{norm_target}|{self.prospect_type}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prospect_id": self.prospect_id,
            "canonical_identity": self.canonical_identity,
            "source_id": self.source_id,
            "prospect_domain": self.prospect_domain,
            "prospect_url": self.prospect_url,
            "source_page_url": self.source_page_url,
            "prospect_type": self.prospect_type,
            "target_asset_url": self.target_asset_url,
            "competitor_domain": self.competitor_domain,
            "relevance_hint": self.relevance_hint,
            "discovered_at": self.discovered_at,
            "metadata": self.metadata,
        }
