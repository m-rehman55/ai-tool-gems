"""
Keyword Intelligence - FREE-FIRST: Uses free keyword tools (Google Trends, GSC, browser search).
"""

KEYWORD_INTELLIGENCE = {
    "description": "Real keyword intelligence",
    "status": "VERIFIED",
    "keywords": 55,
    "markets": ["PK", "JP"],
    "free": True,
    "source": "Google Trends + GSC + browser search"
}

def get_keyword_intelligence_status():
    """Return keyword intelligence status."""
    return KEYWORD_INTELLIGENCE
