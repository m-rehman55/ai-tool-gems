"""
Access Bootstrap - FREE-FIRST: Uses free data sources only.

Access Bootstrap
"""
Access Bootstrap - FREE-FIRST: Uses free data sources only.


BOOTSTRAP = {
  "description": "Access bootstrap for missing sources",
  "rule": "If a required source is unavailable, create a clear setup report. Do not pretend the source is connected.",
  "example": "GSC: ACCESS_REQUIRED \u2192 Need Search Console property access for https://aitoolgems.tech/"
}

def get_bootstrap_status():
    """
Access Bootstrap - FREE-FIRST: Uses free data sources only.
Return bootstrap status."""
Access Bootstrap - FREE-FIRST: Uses free data sources only.

    return BOOTSTRAP

def report_access_required(source, what_is_required, what_it_unlocks):
    """
Access Bootstrap - FREE-FIRST: Uses free data sources only.
Report access required for a source."""
Access Bootstrap - FREE-FIRST: Uses free data sources only.

    return {
        "SOURCE": source,
        "STATUS": "ACCESS_REQUIRED",
        "FREE": "YES",
        "PAID": "NO",
        "WHAT I NEED": what_is_required,
        "WHAT THIS UNLOCKS": what_it_unlocks
    }
