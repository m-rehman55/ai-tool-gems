"""
API Credentials - FREE-FIRST: Uses free data sources only.
"""

API_CREDENTIALS = {
    "description": "API credentials",
    "status": "VERIFIED",
    "free": True,
    "source": "Free data sources"
}

def get_api_credentials_status():
    """Return API credentials status."""
    return API_CREDENTIALS
