"""
page_mapper.py - Real Route Discovery, Keyword-to-Page Mapping & Cannibalization Firewall.
Inspects actual repository routes, maps candidate keywords to the single best existing URL,
and prevents keyword cannibalization collisions.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class SiteRoute:
    url: str
    relative_path: str
    page_type: str  # "tool", "guide", "homepage", "prices", "deals", "trust"
    primary_topic: str
    title: str = ""
    h1: str = ""


@dataclass
class CannibalizationCollision:
    normalized_intent: str
    competing_urls: List[str]
    sample_queries: List[str]
    severity: str  # "HIGH", "MEDIUM"
    recommended_action: str


@dataclass
class PageMappingResult:
    keyword: str
    intent: str
    best_url: str
    relative_path: str
    mapping_confidence: float  # 0.0 - 1.0
    action_type: str  # "OPTIMIZE_EXISTING", "MONITOR", "PROPOSE_NEW_PAGE", "CONSOLIDATE"
    competing_urls: List[str] = field(default_factory=list)
    rational_justification: str = ""


class PageMapper:
    """Discovers real repository pages, maps search keywords, and guards against cannibalization."""

    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.routes: Dict[str, SiteRoute] = {}
        self.url_by_keyword_norm: Dict[str, List[str]] = {}
        self._discover_routes()

    def _discover_routes(self) -> None:
        """Inspects disk to build accurate, uninvented catalog of live site routes."""
        # 1. Homepage
        idx_file = self.project_dir / "index.html"
        if idx_file.exists():
            self.routes["https://aitoolgems.tech/"] = SiteRoute(
                url="https://aitoolgems.tech/",
                relative_path="index.html",
                page_type="homepage",
                primary_topic="Pakistan AI tools marketplace homepage",
            )

        # 2. Prices & Deals
        for sec in ["prices", "deals"]:
            sec_idx = self.project_dir / sec / "index.html"
            if sec_idx.exists():
                url = f"https://aitoolgems.tech/{sec}/"
                self.routes[url] = SiteRoute(
                    url=url,
                    relative_path=f"{sec}/index.html",
                    page_type=sec,
                    primary_topic=f"Pakistan AI {sec} directory",
                )

        # 3. Product tool pages (/tools/*/)
        tools_dir = self.project_dir / "tools"
        if tools_dir.exists():
            for t_dir in tools_dir.iterdir():
                if t_dir.is_dir() and (t_dir / "index.html").exists():
                    slug = t_dir.name
                    url = f"https://aitoolgems.tech/tools/{slug}/"
                    self.routes[url] = SiteRoute(
                        url=url,
                        relative_path=f"tools/{slug}/index.html",
                        page_type="tool",
                        primary_topic=f"{slug.title()} tool page",
                    )

        # 4. Guides (/guides/*/)
        guides_dir = self.project_dir / "guides"
        if guides_dir.exists():
            for g_dir in guides_dir.iterdir():
                if g_dir.is_dir() and (g_dir / "index.html").exists():
                    slug = g_dir.name
                    url = f"https://aitoolgems.tech/guides/{slug}/"
                    self.routes[url] = SiteRoute(
                        url=url,
                        relative_path=f"guides/{slug}/index.html",
                        page_type="guide",
                        primary_topic=f"{slug.replace('-', ' ').title()} guide",
                    )

        # 5. Trust / Policy pages
        for p in ["about.html", "contact.html", "how-we-review.html", "how-we-price.html", "policies.html"]:
            pf = self.project_dir / p
            if pf.exists():
                url = f"https://aitoolgems.tech/{p}"
                self.routes[url] = SiteRoute(
                    url=url,
                    relative_path=p,
                    page_type="trust",
                    primary_topic=p.replace(".html", "").replace("-", " ").title(),
                )

    @staticmethod
    def normalize_keyword(kw: str) -> str:
        """Strips punctuation, stop words, and sorts tokens for order-invariant intent collision checks."""
        clean = re.sub(r"[^a-z0-9\s]", "", kw.lower())
        tokens = [t for t in clean.split() if t not in {"in", "for", "the", "a", "an", "and", "or", "to", "of", "with"}]
        return " ".join(sorted(tokens))

    def find_best_url(self, keyword: str, intent: str = "transactional") -> PageMappingResult:
        """Maps a keyword to the single best existing repository route."""
        kw_lower = keyword.lower()
        norm_kw = self.normalize_keyword(keyword)

        # Check for tool matches
        for url, route in self.routes.items():
            if route.page_type == "tool":
                slug = Path(route.relative_path).parent.name
                if slug in kw_lower:
                    return PageMappingResult(
                        keyword=keyword,
                        intent=intent,
                        best_url=url,
                        relative_path=route.relative_path,
                        mapping_confidence=0.95,
                        action_type="OPTIMIZE_EXISTING",
                        rational_justification=f"Exact tool match for '{slug}' maps directly to official product page.",
                    )

        # Check for general pricing queries across tools
        if any(w in kw_lower for w in ["prices", "pricing", "rate", "rates", "cost"]):
            prices_url = "https://aitoolgems.tech/prices/"
            if prices_url in self.routes:
                return PageMappingResult(
                    keyword=keyword,
                    intent=intent,
                    best_url=prices_url,
                    relative_path="prices/index.html",
                    mapping_confidence=0.90,
                    action_type="OPTIMIZE_EXISTING",
                    rational_justification="Broad multi-tool pricing query maps to central /prices/ directory.",
                )

        # Check for general deals / discounts queries
        if any(w in kw_lower for w in ["deal", "deals", "discount", "cheap", "bundle"]):
            deals_url = "https://aitoolgems.tech/deals/"
            if deals_url in self.routes:
                return PageMappingResult(
                    keyword=keyword,
                    intent=intent,
                    best_url=deals_url,
                    relative_path="deals/index.html",
                    mapping_confidence=0.90,
                    action_type="OPTIMIZE_EXISTING",
                    rational_justification="Broad savings & discount query maps to central /deals/ catalog.",
                )

        # Check for guide matches (comparisons, vs, how-to)
        if any(w in kw_lower for w in ["vs", "compare", "alternative", "guide", "how"]):
            # Look for exact guide match
            for url, route in self.routes.items():
                if route.page_type == "guide":
                    slug = Path(route.relative_path).parent.name
                    # Filter out overly generic words like 'tools', 'pakistan', 'best'
                    slug_words = [sw for sw in slug.split("-") if len(sw) > 3 and sw not in {"tools", "pakistan", "best", "guide"}]
                    if any(sw in kw_lower for sw in slug_words):
                        return PageMappingResult(
                            keyword=keyword,
                            intent=intent,
                            best_url=url,
                            relative_path=route.relative_path,
                            mapping_confidence=0.85,
                            action_type="OPTIMIZE_EXISTING",
                            rational_justification=f"Educational comparison query aligns with existing guide: {slug}.",
                        )

        # Default fallback to Homepage
        home_url = "https://aitoolgems.tech/"
        return PageMappingResult(
            keyword=keyword,
            intent=intent,
            best_url=home_url,
            relative_path="index.html",
            mapping_confidence=0.75,
            action_type="OPTIMIZE_EXISTING",
            rational_justification="Broad generic brand/marketplace intent maps to root homepage.",
        )

    def detect_cannibalization(self, mappings: List[PageMappingResult]) -> List[CannibalizationCollision]:
        """Detects whether multiple pages are competing for the exact same primary search intent."""
        intent_to_urls: Dict[str, Set[str]] = {}
        intent_to_queries: Dict[str, List[str]] = {}

        for m in mappings:
            norm = self.normalize_keyword(m.keyword)
            intent_to_urls.setdefault(norm, set()).add(m.best_url)
            intent_to_queries.setdefault(norm, []).append(m.keyword)

        collisions: List[CannibalizationCollision] = []
        for norm, urls in intent_to_urls.items():
            if len(urls) > 1:
                urls_list = list(urls)
                collisions.append(CannibalizationCollision(
                    normalized_intent=norm,
                    competing_urls=urls_list,
                    sample_queries=intent_to_queries[norm][:5],
                    severity="HIGH" if len(urls_list) > 2 else "MEDIUM",
                    recommended_action=(
                        f"Consolidate intent to single canonical authority: '{urls_list[0]}'. "
                        f"Add cross-links with distinctive secondary anchor text."
                    ),
                ))
        return collisions
