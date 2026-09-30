"""
SERP Engine - FREE-FIRST: Uses free SERP sources (browser, SERP API free tier, Google Custom Search).
"""

SERP_ENGINE = {
    "description": "Real SERP data engine",
    "status": "ACCESS_REQUIRED",
    "markets": ["Pakistan", "Japan"],
    "free": True,
    "source": "Free SERP sources"
}

def get_serp_status():
    """Return SERP status."""
    return SERP_ENGINE
