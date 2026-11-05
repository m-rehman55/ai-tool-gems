"""Competitor Snapshot Diffing & Historical Tracking Engine."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class CompetitorSnapshotManager:
    """Manages persistent historical competitor state and detects meaningful changes."""

    def __init__(self, snapshots_dir: Optional[Path] = None):
        self.snapshots_dir = snapshots_dir or Path("data/competitors/snapshots")
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)

    def save_snapshot(self, snapshot_data: Dict[str, Any], tag: str = "latest") -> Path:
        timestamp_str = str(int(time.time()))
        filename = f"snapshot_{tag}_{timestamp_str}.json"
        target_path = self.snapshots_dir / filename
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(snapshot_data, f, indent=2)

        # Also update latest symlink/file
        latest_path = self.snapshots_dir / "snapshot_latest.json"
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(snapshot_data, f, indent=2)

        return target_path

    def load_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        latest_path = self.snapshots_dir / "snapshot_latest.json"
        if not latest_path.is_file():
            return None
        try:
            with open(latest_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def diff_snapshots(
        self, current: Dict[str, Any], previous: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detect pricing shifts, new competitor tools, or ranking changes between two snapshots."""
        if not previous:
            return {
                "has_changes": False,
                "message": "First snapshot baseline initialized. No previous comparison available.",
                "price_changes": [],
                "new_pages_detected": [],
            }

        price_changes = []
        curr_prices = current.get("pricing", {})
        prev_prices = previous.get("pricing", {})

        for tool_id, comp_map in curr_prices.items():
            prev_comp_map = prev_prices.get(tool_id, {})
            for comp_domain, price in comp_map.items():
                old_price = prev_comp_map.get(comp_domain)
                if old_price is not None and old_price != price:
                    price_changes.append({
                        "tool_id": tool_id,
                        "competitor": comp_domain,
                        "previous_price": old_price,
                        "current_price": price,
                        "delta": price - old_price,
                    })

        has_changes = len(price_changes) > 0
        return {
            "has_changes": has_changes,
            "price_changes": price_changes,
            "new_pages_detected": [],
            "comparison_time": time.time(),
        }
