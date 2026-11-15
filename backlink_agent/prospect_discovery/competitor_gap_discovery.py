"""Competitor Backlink Gap Analysis and Ingestion Engine."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from .models import DiscoveredProspect, normalize_url

# Known toxic spam/PBN patterns identified during competitor audits (e.g. REC-11)
# Note: Blanket TLD bans (e.g. all .shop/.site) are avoided; patterns require verified spam/farm signatures
KNOWN_TOXIC_PBN_PATTERNS = [
    re.compile(r"searchwins\.", re.IGNORECASE),
    re.compile(r"solidlinkpro\.", re.IGNORECASE),
    re.compile(r"serpvilo\.", re.IGNORECASE),
    re.compile(r"backlinkblast\.", re.IGNORECASE),
    re.compile(r"pbnfarm\.", re.IGNORECASE),
    re.compile(r"freebacklink\.", re.IGNORECASE),
    re.compile(r"linkfarm\.", re.IGNORECASE),
    re.compile(r"cheapbacklinks\.", re.IGNORECASE),
    re.compile(r"spammy-directory\.", re.IGNORECASE),
    re.compile(r"bulkbacklink\.", re.IGNORECASE),
    # Verified PBN farm domains discovered during aitoolspak.tech and competitor link audits (REC-11)
    re.compile(r"(?:searchwins|solidlinkpro|indexmexa|rankzira|serpvilo|rankgoods|solidseolink|indextera|cripio|seogo|easyranklab|crisplinkpro|boldboosthub|eliteseo|crawltera|anchornaro|brightboosthub)\.", re.IGNORECASE),
    # Evidence-based spam keywords combined with suspicious/farm gTLDs
    re.compile(r"(?:^|[.-])(?:seo|pbn|blast|backlinks?|linkfarms?)[a-z0-9-]*\.(?:shop|site|online|xyz|top|bid|icu)$", re.IGNORECASE),
]


class CompetitorGapDiscoverer:
    """Discovers high-quality backlink gap opportunities from competitor profiles."""

    def __init__(self, monitored_competitors: Optional[List[str]] = None):
        self.monitored_competitors = monitored_competitors or [
            "aitoolspak.tech",
            "aitoolspak.com",
            "paktools.store",
            "subbazaar.pk",
            "toolwaly.com",
            "zippersells.com",
            "groupseotoolz.com",
            "toolzbuy.com",
        ]

    def is_toxic_pbn(self, domain: str) -> bool:
        """Adversarial check identifying toxic PBNs or link blast farm networks."""
        domain_lower = domain.lower().strip()
        for pattern in KNOWN_TOXIC_PBN_PATTERNS:
            if pattern.search(domain_lower):
                return True
        return False

    def ingest_records(
        self,
        records: List[Dict[str, Any]],
        known_aitoolgems_domains: Optional[List[str]] = None,
    ) -> List[DiscoveredProspect]:
        """Ingests raw referring domain records, filters toxic PBNs, and identifies gaps."""
        known_domains = {d.lower().strip() for d in (known_aitoolgems_domains or [])}
        discovered: List[DiscoveredProspect] = []

        for r in records:
            source_page = r.get("source_page", "") or r.get("referring_page", "") or r.get("url", "")
            target_competitor = r.get("competitor_domain", "") or r.get("target_domain", "")
            anchor = r.get("anchor_text", "")
            domain = r.get("referring_domain", "")

            if not domain and source_page:
                domain = urlparse(source_page).netloc.lower()

            if not domain or not source_page:
                continue

            # Skip toxic PBN networks
            if self.is_toxic_pbn(domain):
                continue

            # Skip if domain already links to AI Tool Gems
            if domain in known_domains:
                continue

            prospect_id = f"cgap_{hash(f'{domain}_{target_competitor}') & 0xFFFFFFFF:08x}"
            discovered.append(
                DiscoveredProspect(
                    prospect_id=prospect_id,
                    source_id="competitor_gap_engine",
                    prospect_domain=domain,
                    prospect_url=f"https://{domain}",
                    source_page_url=source_page,
                    prospect_type="competitor_backlink",
                    target_asset_url="https://aitoolgems.tech/",
                    competitor_domain=target_competitor,
                    relevance_hint=70,
                    metadata={
                        "observed_competitor_anchor": anchor,
                        "competitor_domain": target_competitor,
                        "authority_score": r.get("authority_score", 0),
                    },
                )
            )

        return discovered

    def ingest_from_csv(self, file_path: Path, known_domains: Optional[List[str]] = None) -> List[DiscoveredProspect]:
        """Loads and processes competitor backlink export from CSV file."""
        p = Path(file_path)
        if not p.exists():
            return []
        with p.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return self.ingest_records(list(reader), known_aitoolgems_domains=known_domains)
