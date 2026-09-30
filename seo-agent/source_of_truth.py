"""
Source of Truth Hierarchy - FREE-FIRST: Uses free data sources only.
"""

SOT = {
    "description": "Source of truth hierarchy",
    "AIToolGems_website": ["URLs", "titles", "descriptions", "H1", "canonical", "hreflang", "schema", "products", "prices", "categories", "internal links", "indexable pages", "content"],
    "GSC": ["clicks", "impressions", "CTR", "average position", "queries", "pages", "countries", "devices"],
    "GA4": ["users", "sessions", "engaged sessions", "engagement rate", "landing pages", "traffic acquisition", "organic search traffic", "conversions"],
    "SERP": ["keyword", "position", "URL", "snippet", "features"],
    "keyword_tools": ["volume", "competition", "trend"],
    "backlink_tools": ["domain authority", "referring domains", "anchors"],
    "competitor_sites": ["pages", "keywords", "content"],
    "social_media": ["mentions", "shares"],
    "manual_research": ["notes", "observations"]
}

FREE_FIRST_PRIORITY = {
    "1 - AIToolGems_website": "AIToolGems_website",
    "2 - GSC": "GSC",
    "3 - GA4": "GA4",
    "4 - SERP": "SERP",
    "5 - SERP_API": "SERP_API",
    "6 - keyword_tools": "keyword_tools",
    "7 - backlink_tools": "backlink_tools",
    "8 - competitor_sites": "competitor_sites",
    "9 - social_media": "social_media",
    "10 - manual_research": "manual_research"
}

def get_source_priority_status():
    """Return source priority status."""
    return {"priorities": FREE_FIRST_PRIORITY}

def get_free_first_priority():
    """Return free-first priority order."""
    return FREE_FIRST_PRIORITY
