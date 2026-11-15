"""Technical Publication and Data Citation Discovery Engine."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .models import DiscoveredProspect

CURATED_TECH_PUBLICATIONS: List[Dict[str, Any]] = [
    {
        "platform": "dev.to",
        "name": "Dev.to Developer Community",
        "domain": "dev.to",
        "submit_url": "https://dev.to/new",
        "login_url": "https://dev.to/enter",
        "login_method": "Sign in with GitHub or Google (Free 1-Click)",
        "citation_target": "https://aitoolgems.tech/prices/",
        "angle": "Open Data & Python Scraping: Documenting Pakistani AI Software Pricing",
        "relevance": 85,
    },
    {
        "platform": "hashnode.com",
        "name": "Hashnode Engineering Blog",
        "domain": "hashnode.com",
        "submit_url": "https://hashnode.com/onboard",
        "login_url": "https://hashnode.com/login",
        "login_method": "Sign in with Google or GitHub (Free 1-Click)",
        "citation_target": "https://aitoolgems.tech/prices/",
        "angle": "Engineering Technical Guide: Building a Machine-Readable AI Pricing Index (CSV/JSON/llms.txt)",
        "relevance": 83,
    },
    {
        "platform": "medium.com",
        "name": "Medium Tech Publications",
        "domain": "medium.com",
        "submit_url": "https://medium.com/new-story",
        "login_url": "https://medium.com/m/signin",
        "login_method": "Sign in with Google (Click top-right 'Sign in' -> Google)",
        "citation_target": "https://aitoolgems.tech/prices/",
        "angle": "AI Industry Economics: Software Subscription Costs Across Emerging South Asian Markets",
        "relevance": 80,
    },
    {
        "platform": "techjuice.pk",
        "name": "TechJuice Pakistan Tech Media",
        "domain": "techjuice.pk",
        "submit_url": "https://www.techjuice.pk/contact/",
        "login_url": "https://www.techjuice.pk/contact/",
        "login_method": "No login needed — Open Contact Form or email editor@techjuice.pk",
        "citation_target": "https://aitoolgems.tech/prices/",
        "angle": "Pakistani AI Ecosystem: 2026 Price Index & Local Currency Software Adoption Trends",
        "relevance": 90,
    },
    {
        "platform": "propakistani.pk",
        "name": "ProPakistani Tech News & Analysis",
        "domain": "propakistani.pk",
        "submit_url": "https://propakistani.pk/contact-us/",
        "login_url": "https://propakistani.pk/contact-us/",
        "login_method": "No login needed — Editorial Contact Form or email tips@propakistani.pk",
        "citation_target": "https://aitoolgems.tech/prices/",
        "angle": "Pakistan Tech & Economy: First Open AI Software Pricing Index (PKR Flat Parity & Domestic Payments)",
        "relevance": 92,
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
            submit_url = p.get("submit_url", f"https://{domain}")
            prospect_id = f"pub_{hash(domain) & 0xFFFFFFFF:08x}"

            candidates.append(
                DiscoveredProspect(
                    prospect_id=prospect_id,
                    source_id="tech_publication_registry",
                    prospect_domain=domain,
                    prospect_url=f"https://{domain}",
                    source_page_url=submit_url,
                    prospect_type="tech_publication",
                    target_asset_url=target,
                    relevance_hint=int(p.get("relevance", 80)),
                    metadata={
                        "platform_name": p.get("name"),
                        "editorial_angle": p.get("angle"),
                        "citation_target": target,
                        "submit_url": submit_url,
                        "login_url": p.get("login_url", f"https://{domain}"),
                        "login_method": p.get("login_method", "Standard Login"),
                    },
                )
            )

        return candidates
