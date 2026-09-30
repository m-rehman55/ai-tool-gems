"""
Data Quality Score - FREE-FIRST: Uses free data sources only.
"""

DATA_QUALITY_SCORE = {
    "description": "Data quality score",
    "status": "VERIFIED",
    "free": True,
    "source": "Free data sources"
}

def get_data_quality_score_status():
    """Return data quality score status."""
    return DATA_QUALITY_SCORE
