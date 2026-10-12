#!/usr/bin/env python3
"""
Keyword Universe & Intent Mapping for AIToolGems
------------------------------------------------
Manages deduplicated keyword universe for Pakistan AI tools & global discoverability:
1. Loads keyword mappings from CSV and JSON.
2. Checks for keyword cannibalization across existing and planned URLs.
3. Classifies search intent (transactional, commercial, informational, navigational).
4. Identifies keyword gaps not yet targeted by live pages.
"""

from __future__ import annotations
import csv
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field

@dataclass
class KeywordTarget:
    url: str
    primary_keyword: str
    secondary_keywords: List[str] = field(default_factory=list)
    intent: str = "transactional"  # transactional, commercial, informational, navigational
    market: str = "PK"
    status: str = "active"
    priority: str = "medium"

@dataclass
class CannibalizationCollision:
    primary_keyword: str
    urls: List[str]

class KeywordManager:
    """Manages keyword mappings and prevents cannibalization."""

    def __init__(self):
        self.targets: List[KeywordTarget] = []

    def _normalize_kw(self, kw: str) -> str:
        """Lowercases and strips special chars for collision checks."""
        return re.sub(r"[^a-z0-9]", "", kw.lower())

    def load_from_csv(self, file_path: Path | str):
        path = Path(file_path)
        if not path.exists():
            return
        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                sec_list = [s.strip() for s in row.get("secondary_keywords", "").split(";") if s.strip()]
                self.targets.append(
                    KeywordTarget(
                        url=row.get("url", "").strip(),
                        primary_keyword=row.get("primary_keyword", "").strip(),
                        secondary_keywords=sec_list,
                        intent=row.get("intent", "transactional").strip().lower(),
                        market=row.get("market", "PK").strip(),
                        status=row.get("status", "active").strip(),
                        priority=row.get("priority", "medium").strip(),
                    )
                )

    def load_from_json(self, file_path: Path | str):
        path = Path(file_path)
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for entry in data:
                slug = entry.get("slug", "")
                url = f"https://aitoolgems.tech/guides/{slug}/" if "guide" in slug else f"https://aitoolgems.tech/tools/{slug}/"
                self.targets.append(
                    KeywordTarget(
                        url=url,
                        primary_keyword=entry.get("primary_keyword", "").strip(),
                        secondary_keywords=entry.get("secondary_keywords", []),
                        intent=entry.get("intent", "transactional"),
                        market=entry.get("market", "PK"),
                        status="active",
                        priority=entry.get("priority", "medium"),
                    )
                )
        except Exception:
            pass

    def check_cannibalization(self) -> List[CannibalizationCollision]:
        """Detects whether multiple URLs target the same normalized primary keyword."""
        grouped: Dict[str, List[str]] = {}
        original_names: Dict[str, str] = {}

        for t in self.targets:
            if not t.primary_keyword:
                continue
            norm = self._normalize_kw(t.primary_keyword)
            if norm not in grouped:
                grouped[norm] = []
                original_names[norm] = t.primary_keyword
            grouped[norm].append(t.url)

        collisions: List[CannibalizationCollision] = []
        for norm, urls in grouped.items():
            unique_urls = list(dict.fromkeys(urls))
            if len(unique_urls) > 1:
                collisions.append(
                    CannibalizationCollision(
                        primary_keyword=original_names[norm],
                        urls=unique_urls,
                    )
                )

        return collisions

    def check_new_keyword(self, target_url: str, new_keyword: str) -> Optional[CannibalizationCollision]:
        """Checks if a new candidate keyword collides with an existing URL target."""
        norm_new = self._normalize_kw(new_keyword)
        colliding_urls = []
        for t in self.targets:
            if self._normalize_kw(t.primary_keyword) == norm_new and t.url != target_url:
                colliding_urls.append(t.url)

        if colliding_urls:
            return CannibalizationCollision(
                primary_keyword=new_keyword,
                urls=colliding_urls + [target_url],
            )
        return None
