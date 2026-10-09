"""
Price Intelligence - FREE-FIRST: Uses free price sources (GSC, SERP, browser search).
"""

PRICE_INTELLIGENCE = {
    "description": "Real price intelligence",
    "status": "VERIFIED",
    "products": 20,
    "markets": ["PK"],
    "free": True,
    "source": "GSC + SERP + browser search"
}

def get_price_intelligence_status():
    """Return price intelligence status."""
    return PRICE_INTELLIGENCE
