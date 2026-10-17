"""
search_research.py - Continuous Official Google Search Research Engine.
Monitors official Google Search Central, Search Essentials, Spam Policies,
and AI Optimization documentation to provide evidence-backed authority mapping.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error

logger = logging.getLogger("hermes.search_research")


@dataclass
class GuidanceSource:
    id: str
    url: str
    title: str
    authority: str  # OFFICIAL_REQUIREMENT, OFFICIAL_RECOMMENDATION, OFFICIAL_AI_SEARCH_GUIDANCE, THIRD_PARTY_OPINION, EXPERIMENTAL_HYPOTHESIS
    topics: List[str]
    principles: List[str]
    mapped_checks: List[str]


@dataclass
class ResearchFinding:
    source_id: str
    source_url: str
    source_title: str
    authority: str
    matched_check: str
    recommended_action: str
    official_principle: str
    confidence: str = "CONFIRMED"


class SearchResearchEngine:
    """Manages continuous research against official Google Search documentation."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent.parent
        self.knowledge_file = self.base_dir / "seo-agent" / "knowledge" / "official_search_guidance.json"
        self.changelog_file = self.base_dir / "docs" / "RESEARCH_CHANGELOG.md"
        self.sources: Dict[str, GuidanceSource] = {}
        self.load_guidance()

    def load_guidance(self) -> None:
        """Loads official guidance database."""
        if not self.knowledge_file.exists():
            return
        try:
            data = json.loads(self.knowledge_file.read_text(encoding="utf-8"))
            for s in data.get("sources", []):
                src = GuidanceSource(
                    id=s["id"],
                    url=s["url"],
                    title=s["title"],
                    authority=s.get("authority", "OFFICIAL_RECOMMENDATION"),
                    topics=s.get("topics", []),
                    principles=s.get("principles", []),
                    mapped_checks=s.get("mapped_checks", []),
                )
                self.sources[src.id] = src
        except Exception as e:
            logger.error(f"Error loading guidance database: {e}")

    def check_source_reachability(self, source_id: str, timeout: float = 6.0) -> Dict[str, Any]:
        """Checks if an official Google documentation endpoint is reachable."""
        src = self.sources.get(source_id)
        if not src:
            return {"reachable": False, "error": f"Source {source_id} not found"}

        req = urllib.request.Request(
            src.url,
            headers={
                "User-Agent": "AIToolGems-HermesResearchBot/1.0 (+https://aitoolgems.tech)",
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return {
                    "reachable": resp.getcode() == 200,
                    "status_code": resp.getcode(),
                    "source_id": src.id,
                    "url": src.url,
                    "checked_at": datetime.now(timezone.utc).isoformat(),
                }
        except Exception as e:
            return {
                "reachable": False,
                "status_code": 0,
                "source_id": src.id,
                "url": src.url,
                "error": str(e),
                "checked_at": datetime.now(timezone.utc).isoformat(),
            }

    def map_issue_to_guidance(self, check_type: str) -> Optional[ResearchFinding]:
        """Maps an issue type to an official Google Search documentation principle."""
        norm_type = check_type.upper()
        for src in self.sources.values():
            if norm_type in [c.upper() for c in src.mapped_checks]:
                principle = src.principles[0] if src.principles else "Adhere to official guidelines."
                return ResearchFinding(
                    source_id=src.id,
                    source_url=src.url,
                    source_title=src.title,
                    authority=src.authority,
                    matched_check=check_type,
                    recommended_action=f"Align {check_type} with official requirement: {principle}",
                    official_principle=principle,
                )
        return None

    def record_research_changelog_entry(
        self,
        date_str: str,
        headline: str,
        details: str,
        source_id: str = "GOOGLE_SEARCH_CENTRAL",
    ) -> Path:
        """Appends a versioned entry to docs/RESEARCH_CHANGELOG.md."""
        self.changelog_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.changelog_file.exists():
            self.changelog_file.write_text(
                "# 📚 Google Search Documentation Research Changelog\n\n"
                "Versioned audit trail of official Google Search documentation reviews, "
                "algorithmic policy updates, and compliance verifications for AIToolGems.\n\n"
                "| Date | Source | Authority | Finding / Update | Action Taken |\n"
                "|------|--------|-----------|------------------|--------------|\n",
                encoding="utf-8",
            )

        src = self.sources.get(source_id)
        auth = src.authority if src else "OFFICIAL_RECOMMENDATION"
        url = src.url if src else "https://developers.google.com/search/docs"

        entry_line = f"| `{date_str}` | [{source_id}]({url}) | `{auth}` | {headline} | {details} |\n"
        with open(self.changelog_file, "a", encoding="utf-8") as f:
            f.write(entry_line)

        return self.changelog_file
