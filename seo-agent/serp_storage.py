"""
SERP Snapshot Storage
"""

SERP_STORAGE = {
  "description": "SERP snapshot storage",
  "structure": "serp/{date}/{market}/keyword.json",
  "track_changes": [
    "position_changed",
    "new_domain",
    "lost_domain",
    "new_feature",
    "lost_feature",
    "intent_change",
    "title_change",
    "snippet_change"
  ],
  "rule": "Track real SERP changes, not just zero."
}

def get_serp_storage_status():
    """Return SERP storage status."""
    return SERP_STORAGE

def store_snapshot(keyword, market, date, data):
    """Store a SERP snapshot."""
    return {"keyword": keyword, "market": market, "date": date, "data": data, "stored": True}
