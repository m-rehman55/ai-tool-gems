"""
Never Fabricate Zero - FREE-FIRST: Uses free data sources only.
"""

NEVER_ZERO = {
    "description": "Never fabricate zero",
    "rule": "0 is NOT equivalent to NOT_AVAILABLE. Use 0 only when source explicitly reports zero.",
    "values": {"0": "only when source explicitly reports zero", "NO_DATA": "when source returned no records", "ACCESS_REQUIRED": "when credentials/access are missing", "ERROR": "when collection failed", "NOT_SUPPORTED": "when source cannot provide the metric", "UNKNOWN": "when state genuinely cannot be determined"}
}

def get_never_zero_status():
    """Return never-zero status."""
    return NEVER_ZERO
