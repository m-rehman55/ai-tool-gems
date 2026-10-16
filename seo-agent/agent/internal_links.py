#!/usr/bin/env python3
"""
Internal Link Graph & Topology Analyzer
---------------------------------------
Audits site link structure:
1. Detects orphan pages (pages with zero inbound internal links).
2. Calculates click depth from root (distance from homepage).
3. Identifies broken internal link destinations.
4. Generates contextual link recommendations between related tools and guides.
"""

from __future__ import annotations
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from agent.crawler import CrawledPage

@dataclass
class InternalLinkReport:
    total_urls: int
    orphan_pages: List[str] = field(default_factory=list)
    broken_links: List[Dict[str, str]] = field(default_factory=list)
    click_depths: Dict[str, int] = field(default_factory=dict)
    recommendations: List[Dict[str, str]] = field(default_factory=list)

class InternalLinkAnalyzer:
    """Analyzes graph topology of internal links."""

    def __init__(self, root_url: str = "https://aitoolgems.tech/"):
        self.root_url = root_url.rstrip("/") + "/"

    def _normalize_url(self, url: str, base_url: str = "https://aitoolgems.tech/") -> str:
        """Normalizes URLs for graph edge comparison."""
        import urllib.parse
        clean = url.split("#")[0].split("?")[0].strip()
        if not clean or clean.startswith("mailto:") or clean.startswith("tel:") or clean.startswith("javascript:"):
            return ""
        if not clean.startswith("http://") and not clean.startswith("https://"):
            clean = urllib.parse.urljoin(base_url, clean)
        if clean.startswith("http://aitoolgems.tech"):
            clean = "https://" + clean[len("http://"):]
        if not clean.endswith("/") and not clean.endswith(".html"):
            clean += "/"
        return clean

    def analyze_graph(self, pages: List[CrawledPage]) -> InternalLinkReport:
        all_page_urls: Set[str] = {self._normalize_url(p.url) for p in pages if p.url}
        inbound_counts: Dict[str, int] = {u: 0 for u in all_page_urls}
        adjacency: Dict[str, Set[str]] = {u: set() for u in all_page_urls}
        broken_links: List[Dict[str, str]] = []

        # Build adjacency graph
        for page in pages:
            source_url = self._normalize_url(page.url)
            for raw_dest in page.internal_links:
                dest = self._normalize_url(raw_dest, source_url)
                if not dest:
                    continue
                
                # Check if dest is in crawled set
                if dest in all_page_urls:
                    if dest != source_url:
                        adjacency[source_url].add(dest)
                        inbound_counts[dest] = inbound_counts.get(dest, 0) + 1
                else:
                    # Potential broken link or unindexed page
                    if dest.startswith("https://aitoolgems.tech"):
                        broken_links.append({
                            "source": source_url,
                            "destination": dest,
                            "file": page.file_path or "",
                        })

        # Find orphan pages (inbound == 0, excluding homepage root)
        orphan_pages = [
            u for u, count in inbound_counts.items()
            if count == 0 and u != self.root_url and not u.endswith("404.html") and not u.endswith("admin.html")
        ]

        # Calculate click depth using Breadth-First Search (BFS)
        click_depths: Dict[str, int] = {}
        queue: List[Tuple[str, int]] = [(self.root_url, 0)]
        visited: Set[str] = {self.root_url}

        while queue:
            curr, depth = queue.pop(0)
            click_depths[curr] = depth
            for neighbor in adjacency.get(curr, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, depth + 1))

        # Assign depth -1 (unreachable) for disconnected pages
        for u in all_page_urls:
            if u not in click_depths:
                click_depths[u] = -1

        # Generate contextual recommendations
        recommendations: List[Dict[str, str]] = []
        for orphan in orphan_pages:
            recommendations.append({
                "type": "FIX_ORPHAN",
                "target": orphan,
                "suggestion": f"Link to '{orphan}' from relevant category page or homepage.",
            })

        return InternalLinkReport(
            total_urls=len(all_page_urls),
            orphan_pages=orphan_pages,
            broken_links=broken_links,
            click_depths=click_depths,
            recommendations=recommendations,
        )
