"""
Real-Data Firewall - FREE-FIRST: Uses free data sources only.
"""

REAL_DATA_FIREWALL = {
    "description": "Real-data firewall",
    "status": "ACTIVE",
    "rules": ["REJECT_DATA", "REJECT_FABRICATED", "REJECT_ZERO"],
    "free": True,
    "source": "Free data sources"
}

def get_real_data_firewall_status():
    """Return real-data firewall status."""
    return REAL_DATA_FIREWALL
