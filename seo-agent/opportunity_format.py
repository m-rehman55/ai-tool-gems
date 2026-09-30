"""
Opportunity Format - FREE-FIRST: Uses free data sources only.
"""

OPPORTUNITY_FORMAT = {
    "description": "Opportunity format",
    "example": {"opportunity": "...", "type": "GSC_CTR", "market": "PK", "keyword": "...", "url": "...", "evidence": {"source": "GSC", "impressions": 1234, "ctr": 0.012, "position": 8.4}, "action": "PR_REQUIRED", "created_at": "..."},
    "rule": "Never create opportunities without evidence."
}

def get_opportunity_format_status():
    """Return opportunity format status."""
    return OPPORTUNITY_FORMAT
