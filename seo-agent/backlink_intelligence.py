"""
Backlink Intelligence - FREE-FIRST: Uses free backlink tools (Ahrefs free, Moz free, browser search).
"""

BACKLINK_INTELLIGENCE = {
    "description": "Real backlink intelligence",
    "status": "ACCESS_REQUIRED",
    "free": True,
    "source": "Ahrefs free + Moz free + browser search"
}

def get_backlink_intelligence_status():
    """Return backlink intelligence status."""
    return BACKLINK_INTELLIGENCE
