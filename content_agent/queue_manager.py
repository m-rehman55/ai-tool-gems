"""Editorial Queue Manager & Safe Candidate Replenishment.

Strictly enforces fail-closed queue eligibility.
Discovered topics are added with approved_for_publishing: False.
Never allows autonomous self-approval.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ContentQueueManager:
    """Manages the editorial review queue for blog articles and tool guides."""

    def __init__(self, queue_path: Optional[Path] = None):
        self.queue_path = queue_path or Path("data/seo/content-queue.json")
        self.queue_path.parent.mkdir(parents=True, exist_ok=True)

    def load_queue(self) -> List[Dict[str, Any]]:
        if not self.queue_path.is_file():
            return []
        try:
            with open(self.queue_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_queue(self, items: List[Dict[str, Any]]) -> None:
        with open(self.queue_path, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)

    def get_next_approved_candidate(self, published_slugs: set[str]) -> Tuple[Optional[Dict[str, Any]], str]:
        """Find the next eligible topic strictly requiring approved_for_publishing == True."""
        queue = self.load_queue()
        for item in queue:
            slug = item.get("slug")
            if not slug or slug in published_slugs:
                continue

            # Strict fail-closed check: MUST be explicitly boolean True
            if item.get("approved_for_publishing") is True:
                return item, "APPROVED_CANDIDATE_FOUND"

        return None, "NO_APPROVED_CANDIDATE"

    def add_proposed_candidate(self, candidate_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Add a newly researched or discovered topic proposal to the queue.

        Forces approved_for_publishing = False to prevent self-approval.
        """
        slug = candidate_data.get("slug")
        if not slug:
            return False, "Missing slug."

        queue = self.load_queue()
        for item in queue:
            if item.get("slug") == slug:
                return False, f"Slug '{slug}' already exists in editorial queue."

        # Safety override: proposals can never enter the queue pre-approved
        candidate_data["approved_for_publishing"] = False
        candidate_data["editorial_status"] = "PENDING_HUMAN_REVIEW"
        queue.append(candidate_data)
        self.save_queue(queue)
        return True, f"Candidate '{slug}' added to review queue (status: PENDING_HUMAN_REVIEW)."

    def approve_candidate(self, slug: str, approved_by: str) -> Tuple[bool, str]:
        """Explicit editorial approval gate for human or designated editor sign-off."""
        queue = self.load_queue()
        found = False
        for item in queue:
            if item.get("slug") == slug:
                item["approved_for_publishing"] = True
                item["approved_by"] = approved_by
                item["editorial_status"] = "APPROVED"
                found = True
                break

        if found:
            self.save_queue(queue)
            return True, f"Candidate '{slug}' approved for publication by {approved_by}."
        return False, f"Slug '{slug}' not found in queue."
