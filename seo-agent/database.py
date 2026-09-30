"""
Database / Storage - FREE-FIRST: Uses free data sources only.

SEO Database / Storage
"""
Database / Storage - FREE-FIRST: Uses free data sources only.


DATABASE = {
  "description": "SEO data storage",
  "entities": [
    "seo_keywords",
    "serp_snapshots",
    "serp_results",
    "competitors",
    "competitor_pages",
    "competitor_keywords",
    "gsc_queries",
    "gsc_pages",
    "gsc_daily",
    "ga4_daily",
    "backlinks",
    "technical_crawls",
    "page_metrics",
    "content_opportunities",
    "cannibalization",
    "price_history",
    "source_registry",
    "data_collection_runs",
    "seo_actions"
  ],
  "rule": "Each record should include timestamps."
}

def get_database_status():
    """
Database / Storage - FREE-FIRST: Uses free data sources only.
Return database status."""
Database / Storage - FREE-FIRST: Uses free data sources only.

    return DATABASE
