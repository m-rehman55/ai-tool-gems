"""
Collection Schedule - FREE-FIRST: Uses free data sources only.

Collection Schedule
"""
Collection Schedule - FREE-FIRST: Uses free data sources only.


SCHEDULE = {
  "description": "Data collection schedule",
  "daily": [
    "production crawl",
    "GSC incremental data",
    "analytics data",
    "critical SERP keywords",
    "indexation checks",
    "price checks for tracked products",
    "critical competitor checks"
  ],
  "weekly": [
    "larger SERP set",
    "competitor pages",
    "content gaps",
    "internal-link graph",
    "backlink changes where provider permits",
    "technical audit"
  ],
  "monthly": [
    "complete keyword refresh",
    "competitor landscape",
    "content decay",
    "authority analysis",
    "market analysis",
    "SEO OS health review"
  ],
  "rule": "Do not collect data more frequently than the provider/API limits allow."
}

def get_schedule_status():
    """
Collection Schedule - FREE-FIRST: Uses free data sources only.
Return collection schedule status."""
Collection Schedule - FREE-FIRST: Uses free data sources only.

    return SCHEDULE
