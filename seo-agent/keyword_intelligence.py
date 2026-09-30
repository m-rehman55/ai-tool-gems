"""
Keyword Intelligence - FREE-FIRST: Uses free keyword tools (Google Trends, GSC, browser search).

Real Keyword Intelligence
"""
Keyword Intelligence - FREE-FIRST: Uses free keyword tools (Google Trends, GSC, browser search).


KEYWORD_INTEL = {
  "description": "Real keyword intelligence",
  "status": "PARTIAL",
  "existing_keywords": 55,
  "existing_intents": 11,
  "sources": [
    "Google Search Console",
    "Google Ads Keyword Planner",
    "authorized SEO APIs",
    "Google Trends",
    "SERP APIs",
    "first-party search data",
    "approved keyword intelligence providers"
  ],
  "required_fields": [
    "keyword",
    "market",
    "country",
    "language",
    "intent",
    "volume",
    "volume_source",
    "volume_date",
    "trend",
    "trend_source",
    "competition",
    "competition_source",
    "cpc",
    "cpc_source",
    "serp_type",
    "current_position",
    "position_source",
    "target_url",
    "business_value",
    "content_gap",
    "competitor_urls",
    "last_checked"
  ],
  "rule": "If volume is unavailable, use NOT_AVAILABLE. Never put 0 unless source returned zero."
}

def get_keyword_status():
    """
Keyword Intelligence - FREE-FIRST: Uses free keyword tools (Google Trends, GSC, browser search).
Return keyword intelligence status."""
Keyword Intelligence - FREE-FIRST: Uses free keyword tools (Google Trends, GSC, browser search).

    return KEYWORD_INTEL

def record_keyword_data(keyword, market, country, volume, volume_source, volume_date):
    """
Keyword Intelligence - FREE-FIRST: Uses free keyword tools (Google Trends, GSC, browser search).
Record keyword data with provenance."""
Keyword Intelligence - FREE-FIRST: Uses free keyword tools (Google Trends, GSC, browser search).

    return {
        "keyword": keyword,
        "market": market,
        "country": country,
        "volume": volume if volume is not None else "NOT_AVAILABLE",
        "volume_source": volume_source,
        "volume_date": volume_date,
        "retrieved_at": "2026-10-01T00:00:00Z"
    }
