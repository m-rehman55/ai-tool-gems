"""
SEO Opportunity Engine - FREE-FIRST: Uses free data sources only.
"""

OPPORTUNITY_ENGINE = {
    "description": "SEO opportunity engine",
    "examples": {"GSC": "High impressions + low CTR", "GSC_CTR": "High impressions + low CTR", "Ranking": "Position 4-20 + meaningful impressions", "Content gap": "Real query + no suitable AIToolGems page", "Cannibalization": "Same query + multiple competing AIToolGems URLs", "Technical": "Production crawl evidence", "Competitor": "Repeated SERP evidence showing competitor ranking where AIToolGems has no relevant result"},
    "rule": "Every opportunity must reference its evidence."
}

def get_opportunity_status():
    """Return opportunity engine status."""
    return OPPORTUNITY_ENGINE
