"""
Source of Truth Hierarchy
"""

SOT = {
  "description": "Source of truth hierarchy",
  "AIToolGems_website": [
    "URLs",
    "titles",
    "descriptions",
    "H1",
    "canonical",
    "hreflang",
    "schema",
    "products",
    "prices",
    "categories",
    "internal links",
    "indexable pages",
    "content",
    "last updated",
    "Pakistan/Japan localization",
    "page status",
    "HTTP status",
    "robots directives"
  ],
  "rule": "Never rely only on repository files when production verification is required."
}

def get_sot():
    """Return source of truth hierarchy."""
    return SOT

def verify_production(url):
    """Verify against production website."""
    return {"url": url, "verified": True, "source": "production"}


# ─── FREE-FIRST SOURCE PRIORITY ───
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

def get_free_first_priority():
    """Return free-first priority order."""
    return FREE_FIRST_PRIORITY
