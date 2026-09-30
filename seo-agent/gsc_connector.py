"""
GSC Connector - FREE-FIRST: Uses GSC API only (free).
"""

GSC = {
    "description": "Google Search Console connector",
    "status": "ACCESS_REQUIRED",
    "required_fields": ["clicks", "impressions", "CTR", "average position", "queries", "pages", "countries", "devices"],
    "free": True,
    "source": "Google Search Console API"
}

def get_gsc_status():
    """Return GSC status."""
    return GSC
