"""
Collection Schedule - FREE-FIRST: Uses free data sources only.
"""

COLLECTION_SCHEDULE = {
    "description": "Collection schedule",
    "status": "VERIFIED",
    "frequency": "daily",
    "free": True,
    "source": "Free data sources"
}

def get_collection_schedule_status():
    """Return collection schedule status."""
    return COLLECTION_SCHEDULE
