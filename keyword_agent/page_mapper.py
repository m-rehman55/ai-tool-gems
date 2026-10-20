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


# Verified catalog brand aliases and tool synonyms
TOOL_ALIASES: Dict[str, List[str]] = {
    "adobe": ["adobe", "illustrator", "photoshop", "creative cloud", "lightroom", "premiere pro", "after effects", "firefly"],
    "chatgpt": ["chatgpt", "chat gpt", "gpt-4o", "gpt 4o", "gpt-4", "gpt 4", "openai", "chatgpt plus", "chatgpt pro"],
    "canva": ["canva", "canva pro"],
    "capcut": ["capcut", "cap cut", "capcut pro"],
    "claude": ["claude", "claude ai", "claude 3.5", "claude 3.5 sonnet", "anthropic"],
    "linkedin": ["linkedin", "linked in", "linkedin premium", "sales navigator"],
    "nordvpn": ["nordvpn", "nord vpn"],
    "surfshark": ["surfshark", "surf shark"],
    "midjourney": ["midjourney", "mid journey"],
    "elevenlabs": ["elevenlabs", "eleven labs", "11labs"],
    "leonardo": ["leonardo", "leonardo ai", "leonardo.ai"],
    "replit": ["replit", "repl it", "repl.it"],
    "quillbot": ["quillbot", "quill bot"],
    "grammarly": ["grammarly", "grammerly"],
    "gemini": ["gemini", "google gemini", "gemini pro", "gemini advanced"],
    "veo": ["veo", "veo 3", "google veo", "veo 3 ultra"],
    "heygen": ["heygen", "hey gen"],
    "deepseek": ["deepseek", "deep seek"],
    "perplexity": ["perplexity", "perplexity ai"],
    "cursor": ["cursor", "cursor ai"],
    "lovable": ["lovable", "lovable ai", "lovable.dev"],
    "figma": ["figma", "figma pro"],
    "runway": ["runway", "runway ml", "runwayml", "gen-3", "gen 3"],
    "semrush": ["semrush", "sem rush"],
    "netflix": ["netflix", "netflix 4k", "netflix premium"],
    "youtube": ["youtube premium", "yt premium"],
    "windows": ["windows 11", "windows key", "windows 10", "ms office", "office 365"],
    "allinone": ["all in one", "all-in-one", "ai pack", "mega pack", "ai bundle", "tools bundle"],
    "notion": ["notion", "notion ai"],
    "grok": ["grok", "grok ai", "x ai"],
    "gamma": ["gamma", "gamma app", "gamma ai"],
    "n8n": ["n8n", "n8n automation", "n8n workflow"],
}


class PageMapper:
    """Discovers real repository pages, maps search keywords, and guards against cannibalization."""

    def __init__(self, project_dir: Union[Path, str]):
        self.project_dir = Path(project_dir)
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
        for p in ["about.html", "contact.html", "how-we-review.html", "how-we-price.html", "policies.html", "privacy-policy/index.html", "terms-of-service/index.html"]:
            pf = self.project_dir / p
            if pf.exists():
                clean_path = p.replace("index.html", "") if p.endswith("index.html") else p
                url = f"https://aitoolgems.tech/{clean_path}"
                self.routes[url] = SiteRoute(
                    url=url,
                    relative_path=p,
                    page_type="trust",
                    primary_topic=p.split("/")[0].replace(".html", "").replace("-", " ").title(),
                )

    @staticmethod
    def normalize_keyword(kw: str) -> str:
        """Strips punctuation, stop words, and sorts tokens for order-invariant intent collision checks."""
        clean = re.sub(r"[^a-z0-9\s]", "", kw.lower())
        tokens = [t for t in clean.split() if t not in {"in", "for", "the", "a", "an", "and", "or", "to", "of", "with"}]
        return " ".join(sorted(tokens))

    def _matches_tool(self, slug: str, kw_lower: str) -> bool:
        """Checks if a query contains the tool slug or any of its documented aliases using word boundaries."""
        kw_clean = re.sub(r"[\-_./'\"]+", " ", kw_lower)
        all_terms = [slug] + TOOL_ALIASES.get(slug, [])
        for term in all_terms:
            term_clean = re.sub(r"[\-_./'\"]+", " ", term.lower())
            if re.search(rf"\b{re.escape(term_clean)}\b", kw_clean):
                return True
            # For multi-word terms like 'chat gpt' or 'nord vpn', also check compact version in kw_clean
            compact = re.sub(r"\s+", "", term_clean)
            if len(compact) >= 4 and re.search(rf"\b{re.escape(compact)}\b", kw_clean):
                return True
        return False

    def find_best_url(self, keyword: str, intent: str = "transactional") -> PageMappingResult:
        """Maps a keyword to the single best existing repository route using intent-first routing."""
        kw_lower = keyword.lower()
        is_pk_query = bool(re.search(r"(?i)(pakistan|pakistani|pkr|rs\.?|rupees?|easypaisa|jazzcash|sadapay|nayapay|lahore|karachi|islamabad|rawalpindi|faisalabad)", keyword))

        # 1. Multi-tool comparison & alternative guide matches
        # A) Explicit multi-tool comparison (vs, versus, compare): requires 2+ tool names in slug
        if any(w in kw_lower for w in ["vs", "versus", "compare", "comparison"]):
            for url, route in self.routes.items():
                if route.page_type == "guide":
                    slug = Path(route.relative_path).parent.name
                    # Global queries must not automatically map to Pakistan-only guides
                    if "-pakistan" in slug and not is_pk_query:
                        continue
                    slug_words = [sw for sw in slug.split("-") if len(sw) > 3 and sw not in {"tools", "pakistan", "best", "guide", "price"}]
                    if sum(1 for sw in slug_words if sw in kw_lower) >= 2:
                        return PageMappingResult(
                            keyword=keyword,
                            intent=intent,
                            best_url=url,
                            relative_path=route.relative_path,
                            mapping_confidence=0.95,
                            action_type="OPTIMIZE_EXISTING",
                            rational_justification=f"Educational multi-tool comparison query aligns with guide: {slug}.",
                        )

            # If it's a global comparison without a dedicated global guide, route to relevant primary tool page or research
            if not is_pk_query:
                kw_clean = re.sub(r"[\-_./'\"]+", " ", kw_lower)
                comparison_candidates: List[Tuple[str, str, str, int]] = []
                tool_slugs = [
                    Path(route.relative_path).parent.name
                    for route in self.routes.values()
                    if route.page_type == "tool"
                ]
                for tool_slug in tool_slugs:
                    if self._matches_tool(tool_slug, kw_lower) and f"https://aitoolgems.tech/tools/{tool_slug}/" in self.routes:
                        p = kw_clean.find(tool_slug)
                        if p == -1:
                            for alias in TOOL_ALIASES.get(tool_slug, []):
                                a_clean = re.sub(r"[\-_./'\"]+", " ", alias.lower())
                                p_a = kw_clean.find(a_clean)
                                if p_a != -1 and (p == -1 or p_a < p):
                                    p = p_a
                        if p == -1:
                            p = 9999
                        url = f"https://aitoolgems.tech/tools/{tool_slug}/"
                        rel_p = f"tools/{tool_slug}/index.html"
                        comparison_candidates.append((tool_slug, url, rel_p, p))

                if comparison_candidates:
                    comparison_candidates.sort(key=lambda c: c[3])
                    primary_slug, primary_url, primary_rel_p, _ = comparison_candidates[0]
                    competing = [c[1] for c in comparison_candidates]
                    slug_list_str = ", ".join(c[0] for c in comparison_candidates)
                    return PageMappingResult(
                        keyword=keyword,
                        intent=intent,
                        best_url=primary_url,
                        relative_path=primary_rel_p,
                        mapping_confidence=0.80,
                        action_type="MONITOR",
                        competing_urls=competing,
                        rational_justification=f"Global comparison query ({slug_list_str}) mapped to '{primary_slug}' for monitoring; dedicated global guide requires genuine content proposal.",
                    )

        # B) Alternative queries (alternative, alternatives): maps to alternative guides
        if any(w in kw_lower for w in ["alternative", "alternatives"]):
            for url, route in self.routes.items():
                if route.page_type == "guide" and "alternative" in route.relative_path:
                    slug = Path(route.relative_path).parent.name
                    slug_words = [sw for sw in slug.split("-") if len(sw) > 3 and sw not in {"tools", "pakistan", "best", "guide", "price", "alternative", "alternatives"}]
                    if any(sw in kw_lower for sw in slug_words):
                        return PageMappingResult(
                            keyword=keyword,
                            intent=intent,
                            best_url=url,
                            relative_path=route.relative_path,
                            mapping_confidence=0.95,
                            action_type="OPTIMIZE_EXISTING",
                            rational_justification=f"Alternative query aligns with dedicated alternative guide: {slug}.",
                        )

        # 2. Audience workflows (student, creator, freelancer, developer, business)
        if any(w in kw_lower for w in ["student", "academic", "creator", "freelancer", "developer", "business"]):
            for url, route in self.routes.items():
                if route.page_type == "guide":
                    slug = Path(route.relative_path).parent.name
                    if any(w in slug for w in ["student", "creator", "developer", "business"]):
                        if any(w in kw_lower for w in slug.split("-")):
                            return PageMappingResult(
                                keyword=keyword,
                                intent=intent,
                                best_url=url,
                                relative_path=route.relative_path,
                                mapping_confidence=0.92,
                                action_type="OPTIMIZE_EXISTING",
                                rational_justification=f"Audience workflow query aligns with dedicated persona guide: {slug}.",
                            )

        # 3. Topical Category Guides (e.g. AI video generators / editors)
        if any(w in kw_lower for w in ["video generator", "video generators", "video editing", "ai video"]):
            video_guide_url = "https://aitoolgems.tech/guides/best-ai-video-generators-pakistan/"
            if video_guide_url in self.routes:
                return PageMappingResult(
                    keyword=keyword,
                    intent=intent,
                    best_url=video_guide_url,
                    relative_path="guides/best-ai-video-generators-pakistan/index.html",
                    mapping_confidence=0.92,
                    action_type="OPTIMIZE_EXISTING",
                    rational_justification="Topical category query for AI video generation/editing in Pakistan aligns with dedicated guide: best-ai-video-generators-pakistan.",
                )

        # 4. Direct Tool Matches (Buy, price, rate, subscription, local payment, aliases)
        kw_clean = re.sub(r"[\-_./'\"]+", " ", kw_lower)
        matching_tools: List[Tuple[str, str, str, int]] = []
        for url, route in self.routes.items():
            if route.page_type == "tool":
                slug = Path(route.relative_path).parent.name
                if self._matches_tool(slug, kw_lower):
                    p = kw_clean.find(slug)
                    if p == -1:
                        for alias in TOOL_ALIASES.get(slug, []):
                            a_clean = re.sub(r"[\-_./'\"]+", " ", alias.lower())
                            p_a = kw_clean.find(a_clean)
                            if p_a != -1 and (p == -1 or p_a < p):
                                p = p_a
                    if p == -1:
                        p = 9999
                    matching_tools.append((slug, url, route.relative_path, p))

        # Sort matching tools by first appearance in search query
        matching_tools.sort(key=lambda m: m[3])

        # Exactly one tool matched -> clean unambiguous routing
        if len(matching_tools) == 1:
            slug, url, rel_p, _ = matching_tools[0]

            # Adobe sub-app bundle inclusion vs full suite distinction
            if slug == "adobe":
                subapps = ["illustrator", "photoshop", "premiere pro", "premiere", "after effects", "lightroom", "firefly"]
                matched_subapp = next((sa for sa in subapps if re.search(rf"\b{re.escape(sa)}\b", kw_clean)), None)
                if matched_subapp:
                    return PageMappingResult(
                        keyword=keyword,
                        intent=intent,
                        best_url=url,
                        relative_path=rel_p,
                        mapping_confidence=0.90,
                        action_type="OPTIMIZE_EXISTING",
                        rational_justification=f"Bundle inclusion match: Standalone '{matched_subapp}' is not sold individually on AI Tool Gems; maps to Adobe Creative Cloud All Apps suite (/tools/adobe/) which includes '{matched_subapp}' with explicit on-page clarification.",
                    )

            # ChatGPT tier distinction (Plus vs Pro)
            if slug == "chatgpt" and "pro" in kw_clean:
                return PageMappingResult(
                    keyword=keyword,
                    intent=intent,
                    best_url=url,
                    relative_path=rel_p,
                    mapping_confidence=0.90,
                    action_type="OPTIMIZE_EXISTING",
                    rational_justification="Plan distinction match: Query targets '$200 ChatGPT Pro' tier; maps to /tools/chatgpt/ where on-page content explicitly clarifies Pro is not stocked and presents available ChatGPT Plus offer.",
                )

            return PageMappingResult(
                keyword=keyword,
                intent=intent,
                best_url=url,
                relative_path=rel_p,
                mapping_confidence=0.95,
                action_type="OPTIMIZE_EXISTING",
                rational_justification=f"Exact commercial/transactional tool match for '{slug}' (or recognized alias) maps directly to official product page.",
            )

        # Multiple tools matched without explicit comparison -> flag ambiguous intent for manual review
        if len(matching_tools) > 1:
            competing = [m[1] for m in matching_tools]
            primary_slug, primary_url, primary_rel_p, _ = matching_tools[0]
            return PageMappingResult(
                keyword=keyword,
                intent=intent,
                best_url=primary_url,
                relative_path=primary_rel_p,
                mapping_confidence=0.75,
                action_type="MANUAL_REVIEW",
                competing_urls=competing,
                rational_justification=f"Query references multiple candidate tools ({', '.join([m[0] for m in matching_tools])}) without comparison keywords; flagged for manual intent review.",
            )

        # 5. Check for general pricing queries across tools or unstocked tool queries
        if any(w in kw_lower for w in ["price", "prices", "pricing", "rate", "rates", "cost", "fee"]):
            prices_url = "https://aitoolgems.tech/prices/"
            if prices_url in self.routes:
                # If specific transactional purchase terms exist without matching any catalog tool, flag for unstocked manual review
                if any(w in kw_lower for w in ["buy", "subscription", "account", "key", "license"]) or not any(w in kw_lower for w in ["all", "compare", "tools", "list", "directory", "prices", "pricing"]):
                    return PageMappingResult(
                        keyword=keyword,
                        intent=intent,
                        best_url=prices_url,
                        relative_path="prices/index.html",
                        mapping_confidence=0.60,
                        action_type="MANUAL_REVIEW",
                        rational_justification="No catalog tool or recognized product matched the search query; mapped to prices directory with manual review flagged for unstocked tool demand.",
                    )
                return PageMappingResult(
                    keyword=keyword,
                    intent=intent,
                    best_url=prices_url,
                    relative_path="prices/index.html",
                    mapping_confidence=0.90,
                    action_type="OPTIMIZE_EXISTING",
                    rational_justification="Broad multi-tool pricing query maps to central /prices/ directory.",
                )

        # 5. Check for general deals / discounts queries
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
