"""
Real-Data Firewall - FREE-FIRST: Uses free data sources only.

Real-Data Firewall
"""
Real-Data Firewall - FREE-FIRST: Uses free data sources only.


DATA_FIREWALL = {
  "description": "Real-data firewall",
  "validate": [
    "Is this number from a real source?",
    "Is the source identified?",
    "Is retrieval time known?",
    "Is market known?",
    "Is country known where relevant?",
    "Is currency known where relevant?",
    "Can the metric be reproduced?"
  ],
  "rule": "If NO \u2192 REJECT_DATA. Do not store it as verified intelligence."
}

def validate_data(value, source, retrieval_time, market, country, currency, reproducible):
    """
Real-Data Firewall - FREE-FIRST: Uses free data sources only.
Validate data before storing."""
Real-Data Firewall - FREE-FIRST: Uses free data sources only.

    checks = {
        "real source": source is not None,
        "source identified": source is not None,
        "retrieval time known": retrieval_time is not None,
        "market known": market is not None,
        "country known": country is not None,
        "currency known": currency is not None,
        "reproducible": reproducible
    }
    failed = [k for k, v in checks.items() if not v]
    return {"valid": len(failed) == 0, "failed": failed, "action": "REJECT_DATA" if failed else "ACCEPT"}
