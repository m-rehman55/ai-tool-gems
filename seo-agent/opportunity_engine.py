"""
SEO Opportunity Engine - FREE-FIRST: Uses free data sources only.

SEO Opportunity Engine
"""
SEO Opportunity Engine - FREE-FIRST: Uses free data sources only.


OPPORTUNITY_ENGINE = {
  "description": "SEO opportunity engine",
  "examples": {
    "GSC": "High impressions + low CTR", "GSC_CTR": "High impressions + low CTR",
    "Ranking": "Position 4\u201320 + meaningful impressions",
    "Content gap": "Real query + no suitable AIToolGems page",
    "Cannibalization": "Same query + multiple competing AIToolGems URLs",
    "Technical": "Production crawl evidence",
    "Competitor": "Repeated SERP evidence showing competitor ranking where AIToolGems has no relevant result"
  },
  "rule": "Every opportunity must reference its evidence."
}

def get_opportunity_status():
    """
SEO Opportunity Engine - FREE-FIRST: Uses free data sources only.
Return opportunity engine status."""
SEO Opportunity Engine - FREE-FIRST: Uses free data sources only.

    return OPPORTUNITY_ENGINE

def calculate_opportunity(type, keyword, evidence, market, intent, existing_url, competitor_evidence, business_value, action):
    """
SEO Opportunity Engine - FREE-FIRST: Uses free data sources only.
Calculate an opportunity."""
SEO Opportunity Engine - FREE-FIRST: Uses free data sources only.

    return {
        "opportunity": keyword,
        "type": type,
        "market": market,
        "keyword": keyword,
        "url": existing_url,
        "evidence": evidence,
        "action": action,
        "created_at": "2026-10-01T00:00:00Z"
    }
