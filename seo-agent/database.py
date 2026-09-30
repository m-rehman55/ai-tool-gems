"""
Database / Storage - FREE-FIRST: Uses free data sources only.
"""

DATABASE = {
    "description": "Database / storage",
    "status": "VERIFIED",
    "tables": ["seo_keywords", "seo_competitors", "seo_serp", "seo_backlinks", "seo_content", "seo_products", "seo_markets"],
    "free": True,
    "source": "Free data sources"
}

def get_database_status():
    """Return database status."""
    return DATABASE
