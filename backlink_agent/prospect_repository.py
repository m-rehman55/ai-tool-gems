"""Unified Prospect Repository resolving opportunities across Tracker CSV and Daily Intelligence Reports."""

from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_CSV_PATH = Path("seo-agent/data/offpage_authority_tracker.csv")
DEFAULT_JSON_DIR = Path("seo-agent/reports/backlinks")


class UnifiedProspect:
    """Canonical normalized representation of a backlink prospect from any source."""

    def __init__(
        self,
        prospect_id: str,
        prospect_domain: str,
        prospect_type: str,
        submission_url: str,
        target_asset_url: str,
        score: int,
        draft_hash: str,
        source_origin: str,
        status: str = "pending_owner_review",
        draft: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.prospect_id = prospect_id
        self.prospect_domain = prospect_domain
        self.prospect_type = prospect_type
        self.submission_url = submission_url
        self.target_asset_url = target_asset_url
        self.score = score
        self.draft_hash = draft_hash
        self.source_origin = source_origin
        self.status = status
        self.draft = draft or {}
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prospect_id": self.prospect_id,
            "prospect_domain": self.prospect_domain,
            "prospect_type": self.prospect_type,
            "submission_url": self.submission_url,
            "target_asset_url": self.target_asset_url,
            "score": self.score,
            "draft_hash": self.draft_hash,
            "source_origin": self.source_origin,
            "status": self.status,
            "draft": self.draft,
            "metadata": self.metadata,
        }


class ProspectRepository:
    """Resolves prospects across legacy CSV trackers and daily intelligence JSON reports."""

    def __init__(
        self,
        csv_path: Optional[Path] = None,
        json_dir: Optional[Path] = None,
    ):
        self.csv_path = Path(csv_path or DEFAULT_CSV_PATH)
        self.json_dir = Path(json_dir or DEFAULT_JSON_DIR)

    @staticmethod
    def normalize_domain(value: str) -> str:
        val = str(value or "").strip().lower()
        val = re.sub(r"^https?://", "", val)
        val = val.split("/")[0].split(":")[0]
        return val.removeprefix("www.")

    @staticmethod
    def normalize_hash(value: str) -> str:
        return str(value or "").strip().lower()

    def load_tracker_csv(self) -> List[UnifiedProspect]:
        results: List[UnifiedProspect] = []
        if not self.csv_path.exists():
            return results

        try:
            with self.csv_path.open("r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for idx, row in enumerate(reader, start=1):
                    domain = self.normalize_domain(row.get("prospect_domain", ""))
                    if not domain:
                        continue

                    url = row.get("prospect_url") or row.get("source_page") or f"https://{domain}"
                    target = row.get("target_url") or "https://aitoolgems.tech/"
                    score = int(row.get("relevance") or 70)
                    action_status = row.get("action_status") or "pending_owner_review"

                    prospect = UnifiedProspect(
                        prospect_id=f"csv_row_{idx}",
                        prospect_domain=domain,
                        prospect_type=row.get("site_type", "directory"),
                        submission_url=url,
                        target_asset_url=target,
                        score=score,
                        draft_hash=f"csv_{idx}_{domain[:6]}",
                        source_origin="tracker_csv",
                        status=action_status,
                        draft={
                            "tool_name": "AI Tool Gems",
                            "website_url": "https://aitoolgems.tech/",
                            "short_tagline": "Verified AI tools directory and transparent subscription pricing index in Pakistan PKR.",
                            "category": "AI & Developer Tools",
                            "submission_url": url,
                        },
                        metadata=row,
                    )
                    results.append(prospect)
        except Exception as e:
            logger.warning(f"Error reading tracker CSV: {e}")

        return results

    def load_daily_json_reports(self) -> List[UnifiedProspect]:
        results: List[UnifiedProspect] = []
        if not self.json_dir.exists():
            return results

        # Process from newest to oldest
        json_files = sorted(self.json_dir.glob("backlink_intelligence_*.json"), reverse=True)
        for jf in json_files:
            try:
                data = json.loads(jf.read_text(encoding="utf-8"))
                drafts_map: Dict[str, Dict[str, Any]] = {}
                for d_entry in data.get("drafts", []):
                    domain = self.normalize_domain(d_entry.get("domain", ""))
                    if domain:
                        drafts_map[domain] = d_entry

                for opp in data.get("opportunities", []):
                    domain = self.normalize_domain(opp.get("prospect_domain", ""))
                    if not domain:
                        continue

                    d_info = drafts_map.get(domain, {})
                    draft_obj = d_info.get("draft", {})
                    draft_hash = d_info.get("draft_hash", "") or opp.get("prospect_id", "")[:16]

                    score_info = opp.get("score", {})
                    total_score = (
                        score_info.get("total_score", 75)
                        if isinstance(score_info, dict)
                        else int(score_info or 75)
                    )

                    sub_url = (
                        opp.get("source_page_url")
                        or draft_obj.get("submission_url")
                        or f"https://{domain}"
                    )
                    target_url = (
                        opp.get("target_asset_url")
                        or draft_obj.get("target_landing_page")
                        or "https://aitoolgems.tech/"
                    )

                    prospect = UnifiedProspect(
                        prospect_id=opp.get("prospect_id", f"opp_{domain}"),
                        prospect_domain=domain,
                        prospect_type=opp.get("prospect_type", "curated_directory"),
                        submission_url=sub_url,
                        target_asset_url=target_url,
                        score=total_score,
                        draft_hash=draft_hash,
                        source_origin=jf.name,
                        status="pending_owner_review",
                        draft=draft_obj,
                        metadata=opp,
                    )
                    results.append(prospect)
            except Exception as e:
                logger.warning(f"Error reading intelligence JSON {jf.name}: {e}")

        return results

    def all_prospects(self) -> List[UnifiedProspect]:
        """Loads and deduplicates all prospects across daily JSON reports and legacy tracker CSV."""
        json_prospects = self.load_daily_json_reports()
        csv_prospects = self.load_tracker_csv()

        combined: Dict[str, UnifiedProspect] = {}

        # Give priority to richest daily intelligence reports
        for p in json_prospects:
            if p.prospect_domain not in combined:
                combined[p.prospect_domain] = p

        # Supplement with legacy CSV prospects not in JSON
        for p in csv_prospects:
            if p.prospect_domain not in combined:
                combined[p.prospect_domain] = p

        return list(combined.values())

    def resolve(
        self,
        identifier: str,
        prospect_hash: Optional[str] = None,
    ) -> Optional[UnifiedProspect]:
        """Resolves a prospect by domain name, draft hash, row index, or draft ID."""
        clean_id = self.normalize_domain(identifier)
        clean_hash = self.normalize_hash(prospect_hash) if prospect_hash else ""

        prospects = self.all_prospects()

        # 1. Exact match by draft hash if identifier is a hash
        if not clean_hash and len(clean_id) in (8, 16) and not "." in clean_id:
            for p in prospects:
                if p.draft_hash.lower().startswith(clean_id) or p.prospect_id.lower().startswith(clean_id):
                    return p

        # 2. Match by domain and optional hash
        matches = []
        for p in prospects:
            dom = p.prospect_domain.lower()
            if (
                dom == clean_id
                or dom.removeprefix("www.") == clean_id
                or dom.split(".")[0] == clean_id
            ):
                if clean_hash:
                    if p.draft_hash.lower().startswith(clean_hash) or clean_hash.startswith(p.draft_hash.lower()[:8]):
                        return p
                matches.append(p)

        if len(matches) == 1:
            return matches[0]

        # 3. Numeric row lookup (1-based index)
        if clean_id.isdigit():
            idx = int(clean_id)
            if 1 <= idx <= len(prospects):
                return prospects[idx - 1]

        # 4. Partial domain search fallback
        for p in prospects:
            if clean_id in p.prospect_domain.lower():
                return p

        return None
