"""
Real-Time vs Historical Data - FREE-FIRST: Uses free data sources only.
"""

REAL_TIME = {
    "description": "Real-time vs historical data",
    "time_dimensions": ["CURRENT", "DAILY", "WEEKLY", "MONTHLY", "HISTORICAL"],
    "rule": "A September metric must never be presented as an October metric."
}

def get_realtime_status():
    """Return real-time vs historical status."""
    return REAL_TIME
