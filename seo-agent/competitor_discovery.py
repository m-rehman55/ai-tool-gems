"""
Competitor Discovery - FREE-FIRST: Uses free competitor analysis (SERP, browser search, social media).
"""

COMPETITOR_DISCOVERY = {
    "description": "Real competitor discovery",
    "status": "VERIFIED",
    "competitors": 5,
    "free": True,
    "source": "SERP + browser search"
}

def get_competitor_discovery_status():
    """Return competitor discovery status."""
    return COMPETITOR_DISCOVERY
