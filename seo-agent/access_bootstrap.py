"""
Access Bootstrap - FREE-FIRST: Uses free data sources only.
"""

ACCESS_BOOTSTRAP = {
    "description": "Access bootstrap",
    "status": "ACCESS_REQUIRED",
    "free": True,
    "source": "Free data sources"
}

def get_access_bootstrap_status():
    """Return access bootstrap status."""
    return ACCESS_BOOTSTRAP
