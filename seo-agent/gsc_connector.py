"""
GSC Connector - FREE-FIRST: Uses GSC API only (free).

Google Search Console Connector
"""
GSC Connector - FREE-FIRST: Uses GSC API only (free).


GSC = {
  "description": "Google Search Console connector",
  "status": "ACCESS_REQUIRED",
  "required_fields": [
    "clicks",
    "impressions",
    "CTR",
    "average position",
    "queries",
    "pages",
    "countries",
    "devices",
    "dates",
    "search appearance"
  ],
  "windows": [
    "last 7 days",
    "last 28 days",
    "last 3 months",
    "last 6 months",
    "year-over-year"
  ],
  "rule": "Do NOT convert unavailable values into zero. Differentiate ZERO from NOT_AVAILABLE, NOT_TRACKED, NO_DATA."
}

def get_gsc_status():
    """
GSC Connector - FREE-FIRST: Uses GSC API only (free).
Return GSC status."""
GSC Connector - FREE-FIRST: Uses GSC API only (free).

    return GSC

def record_gsc_data(query, page, country, device, clicks, impressions, ctr, position, date):
    """
GSC Connector - FREE-FIRST: Uses GSC API only (free).
Record GSC data with provenance."""
GSC Connector - FREE-FIRST: Uses GSC API only (free).

    return {
        "source": "google_search_console",
        "query": query,
        "page": page,
        "country": country,
        "device": device,
        "clicks": clicks if clicks is not None else "NOT_AVAILABLE",
        "impressions": impressions if impressions is not None else "NOT_AVAILABLE",
        "ctr": ctr if ctr is not None else "NOT_AVAILABLE",
        "position": position if position is not None else "NOT_AVAILABLE",
        "date": date,
        "retrieved_at": "2026-10-01T00:00:00Z"
    }
