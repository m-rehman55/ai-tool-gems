"""
GA4 Connector - FREE-FIRST: Uses GA4 API only (free).
"""

GA4 = {
    "description": "Google Analytics 4 connector",
    "status": "ACCESS_REQUIRED",
    "required_fields": ["users", "sessions", "engaged sessions", "engagement rate", "landing pages", "traffic acquisition", "organic search traffic", "conversions"],
    "free": True,
    "source": "Google Analytics 4 API"
}

def get_ga4_status():
    """Return GA4 status."""
    return GA4
