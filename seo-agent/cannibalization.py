"""
Real Cannibalization Detection
"""

CANNIBALIZATION = {
  "description": "Real cannibalization detection",
  "use": [
    "GSC query/page data",
    "ranking URLs",
    "SERP results",
    "titles/H1",
    "semantic similarity"
  ],
  "detect": "Multiple AIToolGems URLs competing for same search intent",
  "actions": [
    "consolidate",
    "redirect",
    "differentiate intent",
    "improve internal linking",
    "canonicalize where appropriate",
    "keep both"
  ],
  "required_fields": [
    "keyword",
    "URL A",
    "URL B",
    "GSC impressions",
    "positions",
    "SERP evidence",
    "recommended action"
  ],
  "rule": "Do not consolidate pages merely because they share words."
}

def get_cannibalization_status():
    """Return cannibalization status."""
    return CANNIBALIZATION

def record_cannibalization(keyword, url_a, url_b, impressions, positions, serp_evidence, action):
    """Record cannibalization data."""
    return {
        "keyword": keyword,
        "URL A": url_a,
        "URL B": url_b,
        "GSC impressions": impressions if impressions is not None else "NOT_AVAILABLE",
        "positions": positions if positions is not None else "NOT_AVAILABLE",
        "SERP evidence": serp_evidence,
        "recommended action": action,
        "retrieved_at": "2026-10-01T00:00:00Z"
    }
