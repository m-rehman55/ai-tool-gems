"""
FREE-FIRST REAL SEO DATA POLICY
================================
All SEO data must come from free sources. No paid APIs. No paid tools.
Free tools: Google Search Console, Google Analytics, Google Trends,
SERP APIs, Google Custom Search, browser search, GitHub, sitemap,
robots.txt, page source, social media.

Last updated: 2026-10-01
"""

FREE_FIRST_POLICY = {
    "description": "Free-first real SEO data policy",
    "rule": "ALL SEO data must come from free sources. No paid APIs. No paid tools.",
    "free_sources": {
        "google_search_console": "https://search.google.com/search-console",
        "google_analytics": "https://analytics.google.com",
        "google_trends": "https://trends.google.com",
        "google_custom_search": "https://developers.google.com/custom-search/v1/overview",
        "serp_api": "https://serpapi.com",
        "bing_webmaster": "https://www.bing.com/webmasters",
        "moz_free": "https://moz.com/products/pro/free-tools",
        "ahrefs_free": "https://ahrefs.com/blog/",
        "seobench": "https://www.seobench.com",
        "seobility_free": "https://www.seobility.com/en/seo-tools/",
        "page_speed": "https://pagespeed.web.dev",
        "gtmetrix": "https://gtmetrix.com",
        "webpagetest": "https://www.webpagetest.org",
        "github": "https://github.com",
        "sitemap": "sitemap.xml",
        "robots_txt": "robots.txt",
        "page_source": "Browser View Source",
        "social_media": "Twitter/X, Facebook, LinkedIn",
        "forum": "Reddit, Stack Overflow, Quora",
        "news": "Google News"
    }
}

def get_free_first_policy():
    """Return the free-first policy."""
    return FREE_FIRST_POLICY

def check_source(source):
    """Check if a source is free."""
    free_sources = FREE_FIRST_POLICY.get("free_sources", {})
    return source.lower() in [s.lower() for s in free_sources.keys()]

def validate_source(source):
    """Validate a source."""
    if check_source(source):
        return {"valid": True, "source": source, "cost": "free"}
    return {"valid": False, "source": source, "cost": "unknown", "action": "FIND_FREE_ALTERNATIVE"}

def get_source_priority(source):
    """Get source priority (1=highest, 10=lowest)."""
    priorities = {
        "AIToolGems_website": 1,
        "GSC": 2,
        "GA4": 3,
        "SERP": 4,
        "SERP_API": 5,
        "keyword_tools": 6,
        "backlink_tools": 7,
        "competitor_sites": 8,
        "social_media": 9,
        "manual_research": 10
    }
    for key, priority in priorities.items():
        if key in source:
            return priority
    return 10

def get_source_priority_status():
    """Return source priority status."""
    return {"priorities": {
        "AIToolGems_website": 1,
        "GSC": 2,
        "GA4": 3,
        "SERP": 4,
        "SERP_API": 5,
        "keyword_tools": 6,
        "backlink_tools": 7,
        "competitor_sites": 8,
        "social_media": 9,
        "manual_research": 10
    }}
