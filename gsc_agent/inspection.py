"""
URL Inspection & Indexing Intelligence Engine for GSC Agent.
Interacts with the Google Search Console URL Inspection API,
evaluates indexing states, canonical mismatches, rich result health,
and maintains persistent inspection caches to respect API quotas.
"""

from __future__ import annotations
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

from gsc_agent.client import GSCClient


@dataclass
class InspectionResultRecord:
    url: str
    verdict: str  # PASS, NEUTRAL, FAIL
    coverage_state: str
    indexing_state: str
    robots_txt_state: str
    page_fetch_state: str
    google_canonical: str
    user_canonical: str
    last_crawl_time: Optional[str]
    crawled_as: str
    referring_urls: List[str] = field(default_factory=list)
    sitemap: Optional[str] = None
    rich_results_verdict: Optional[str] = None
    rich_results_items: List[str] = field(default_factory=list)
    canonical_mismatch: bool = False
    is_indexed: bool = False
    requires_remediation: bool = False
    inspected_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class GSCInspectionManager:
    """Manages batch URL inspections with caching and quota preservation."""

    def __init__(self, client: GSCClient, cache_path: Optional[Path | str] = None):
        self.client = client
        if cache_path:
            self.cache_file = Path(cache_path)
        else:
            self.cache_file = client.base_dir / "data" / "seo" / "inspection_cache.json"

        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        self.cache: Dict[str, Dict[str, Any]] = self._load_cache()

    def _load_cache(self) -> Dict[str, Dict[str, Any]]:
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save_cache(self) -> None:
        self.cache_file.write_text(json.dumps(self.cache, indent=2), encoding="utf-8")

    def inspect_url_with_cache(
        self,
        target_url: str,
        max_cache_age_days: int = 7,
        force_refresh: bool = False
    ) -> InspectionResultRecord:
        """Inspects single URL via GSC API or returns valid cached record."""
        cached = self.cache.get(target_url)
        now = datetime.now(timezone.utc)

        if cached and not force_refresh:
            inspected_at_str = cached.get("inspected_at")
            if inspected_at_str:
                try:
                    inspected_at = datetime.fromisoformat(inspected_at_str.replace("Z", "+00:00"))
                    if now - inspected_at < timedelta(days=max_cache_age_days):
                        return InspectionResultRecord(**cached)
                except Exception:
                    pass

        # Call live API
        raw = self.client.inspect_url(target_url)
        record = self.parse_inspection_response(target_url, raw)

        # Store in cache
        self.cache[target_url] = asdict(record)
        self._save_cache()
        return record

    def parse_inspection_response(self, target_url: str, raw: Dict[str, Any]) -> InspectionResultRecord:
        """Parses Google URL Inspection response into a structured record."""
        idx = raw.get("indexStatusResult", {})
        verdict = idx.get("verdict", "UNKNOWN")
        cov = idx.get("coverageState", "Unknown")
        indexing_state = idx.get("indexingState", "UNKNOWN")
        robots = idx.get("robotsTxtState", "UNKNOWN")
        fetch = idx.get("pageFetchState", "UNKNOWN")
        g_canonical = idx.get("googleCanonical", "")
        u_canonical = idx.get("userCanonical", "")
        last_crawl = idx.get("lastCrawlTime")
        crawled_as = idx.get("crawledAs", "UNKNOWN")
        referring = idx.get("referringUrls", [])
        sitemap = idx.get("sitemap")

        # Canonical check
        canonical_mismatch = bool(g_canonical and u_canonical and g_canonical.rstrip("/") != u_canonical.rstrip("/"))

        # Rich results check
        rich = raw.get("richResultsResult", {})
        rich_verdict = rich.get("verdict")
        detected_items = [item.get("richResultType", "item") for item in rich.get("detectedItems", [])]

        is_indexed = (verdict == "PASS" and "indexed" in cov.lower())
        requires_remediation = (
            not is_indexed or
            canonical_mismatch or
            robots != "ALLOWED" or
            fetch != "SUCCESSFUL" or
            "error" in cov.lower()
        )

        return InspectionResultRecord(
            url=target_url,
            verdict=verdict,
            coverage_state=cov,
            indexing_state=indexing_state,
            robots_txt_state=robots,
            page_fetch_state=fetch,
            google_canonical=g_canonical,
            user_canonical=u_canonical,
            last_crawl_time=last_crawl,
            crawled_as=crawled_as,
            referring_urls=referring,
            sitemap=sitemap,
            rich_results_verdict=rich_verdict,
            rich_results_items=detected_items,
            canonical_mismatch=canonical_mismatch,
            is_indexed=is_indexed,
            requires_remediation=requires_remediation,
        )

    def inspect_url_batch(
        self,
        urls: List[str],
        rate_limit_pause_seconds: float = 0.5,
        max_batch_size: int = 50
    ) -> List[InspectionResultRecord]:
        """Batch inspects URLs respecting rate limits and quota preservation."""
        results: List[InspectionResultRecord] = []
        subset = urls[:max_batch_size]

        for idx, url in enumerate(subset, start=1):
            try:
                rec = self.inspect_url_with_cache(url)
                results.append(rec)
            except Exception as e:
                # Fallback record on API quota or failure
                results.append(
                    InspectionResultRecord(
                        url=url,
                        verdict="ERROR",
                        coverage_state=f"API Error: {e}",
                        indexing_state="ERROR",
                        robots_txt_state="UNKNOWN",
                        page_fetch_state="ERROR",
                        google_canonical="",
                        user_canonical="",
                        last_crawl_time=None,
                        crawled_as="UNKNOWN",
                        requires_remediation=True
                    )
                )
            if idx < len(subset):
                time.sleep(rate_limit_pause_seconds)

        return results

