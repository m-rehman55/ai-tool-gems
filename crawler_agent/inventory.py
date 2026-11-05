"""
Persistent URL Inventory Database for Crawler Agent.
Maintains state machine transitions:
DISCOVERED -> CRAWLED -> ANALYZED -> FIX_REQUIRED -> APPROVED -> DEPLOYED -> VERIFIED.
Stores crawl history, hashes, and audit outcomes.
"""

from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional

from crawler_agent.models import CrawlRecord, URLCrawlState


class URLInventoryDatabase:
    """Manages persistent inventory of all URLs and their technical audit lifecycle."""

    def __init__(self, storage_path: Optional[Path | str] = None, base_dir: Optional[Path | str] = None):
        base = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
        self.storage_file = Path(storage_path) if storage_path else (base / "data" / "seo" / "url_inventory_db.json")
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self.records: Dict[str, CrawlRecord] = {}
        self.load()

    def load(self) -> None:
        if self.storage_file.exists():
            try:
                raw = json.loads(self.storage_file.read_text(encoding="utf-8"))
                for url, data in raw.get("urls", {}).items():
                    self.records[url] = CrawlRecord.from_dict(data)
            except Exception:
                self.records = {}

    def save(self) -> None:
        data = {
            "version": "2.0.0",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "total_urls": len(self.records),
            "urls": {url: rec.to_dict() for url, rec in self.records.items()}
        }
        self.storage_file.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def register_url(self, url: str) -> CrawlRecord:
        clean_url = url.strip()
        if clean_url not in self.records:
            self.records[clean_url] = CrawlRecord(url=clean_url, state=URLCrawlState.DISCOVERED)
            self.save()
        return self.records[clean_url]

    def upsert_crawl_record(self, record: CrawlRecord) -> None:
        """Updates URL inventory with new crawl results and triggers state transition."""
        url = record.url
        existing = self.records.get(url)

        if existing:
            # Preserve state if already in FIX_REQUIRED or APPROVED
            if existing.state in (URLCrawlState.FIX_REQUIRED, URLCrawlState.APPROVED):
                record.state = existing.state
            else:
                record.state = URLCrawlState.CRAWLED
        else:
            record.state = URLCrawlState.CRAWLED

        record.last_crawled_at = datetime.now(timezone.utc).isoformat()
        self.records[url] = record
        self.save()

    def update_analysis_outcome(self, url: str, issues: List[str]) -> None:
        record = self.records.get(url)
        if not record:
            return

        record.issues_detected = issues
        record.last_analyzed_at = datetime.now(timezone.utc).isoformat()

        if len(issues) > 0:
            record.transition_to(URLCrawlState.FIX_REQUIRED)
        else:
            record.transition_to(URLCrawlState.ANALYZED)
        self.save()

    def get_by_state(self, state: URLCrawlState) -> List[CrawlRecord]:
        return [r for r in self.records.values() if r.state == state]
