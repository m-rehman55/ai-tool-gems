"""
Never Fabricate Zero - FREE-FIRST: Uses free data sources only.

Never Fabricate Zero
"""
Never Fabricate Zero - FREE-FIRST: Uses free data sources only.


NEVER_ZERO = {
  "description": "Never fabricate zero",
  "rule": "0 is NOT equivalent to NOT_AVAILABLE. Use 0 only when source explicitly reports zero.",
  "values": {
    "0": "only when source explicitly reports zero",
    "NO_DATA": "when source returned no records",
    "ACCESS_REQUIRED": "when credentials/access are missing",
    "ERROR": "when collection failed",
    "NOT_SUPPORTED": "when source cannot provide the metric",
    "UNKNOWN": "when state genuinely cannot be determined"
  }
}

def get_never_zero_status():
    """
Never Fabricate Zero - FREE-FIRST: Uses free data sources only.
Return never-zero status."""
Never Fabricate Zero - FREE-FIRST: Uses free data sources only.

    return NEVER_ZERO

def validate_zero(value, source_reported_zero):
    """
Never Fabricate Zero - FREE-FIRST: Uses free data sources only.
Validate zero values."""
Never Fabricate Zero - FREE-FIRST: Uses free data sources only.

    if value == 0 or value == "0":
        if not source_reported_zero:
            return {"valid": False, "action": "REJECT_DATA", "reason": "Source did not report zero"}
    return {"valid": True}
