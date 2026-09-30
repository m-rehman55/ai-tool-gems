"""
Data Provenance - FREE-FIRST: Uses free data sources only.
"""

DATA_PROVENANCE = {
    "description": "Data provenance",
    "status": "VERIFIED",
    "free": True,
    "source": "Free data sources"
}

def get_data_provenance_status():
    """Return data provenance status."""
    return DATA_PROVENANCE
