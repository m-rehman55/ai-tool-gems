"""
Ping History and State Tracker.
Tracks dispatched URLs, timestamps, and indexing queue states in data/ping_history.json.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List

BASE_DIR = Path(__file__).resolve().parent.parent
HISTORY_FILE = BASE_DIR / "data" / "ping_history.json"


def load_history() -> Dict[str, Any]:
    """Loads ping submission history from JSON."""
    if not HISTORY_FILE.exists():
        return {
            "total_dispatches": 0,
            "last_dispatch": None,
            "url_history": {},
            "recent_runs": []
        }
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {
            "total_dispatches": 0,
            "last_dispatch": None,
            "url_history": {},
            "recent_runs": []
        }


def record_dispatch(urls: List[str], result: Dict[str, Any]):
    """Records a dispatch event with timestamp and individual URL history."""
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    history = load_history()

    now_iso = datetime.now(timezone.utc).isoformat()
    history["total_dispatches"] = history.get("total_dispatches", 0) + 1
    history["last_dispatch"] = now_iso

    url_history = history.setdefault("url_history", {})
    for url in urls:
        url_history[url] = {
            "last_submitted": now_iso,
            "submission_count": url_history.get(url, {}).get("submission_count", 0) + 1,
            "last_status": result.get("status", "unknown")
        }

    recent_runs = history.setdefault("recent_runs", [])
    recent_runs.insert(0, {
        "timestamp": now_iso,
        "urls_count": len(urls),
        "status": result.get("status"),
        "endpoints": result.get("endpoints", {})
    })
    # Keep only the last 50 runs to prevent unbounded file growth
    history["recent_runs"] = recent_runs[:50]

    HISTORY_FILE.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
