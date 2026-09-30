"""
Automation Firewall - FREE-FIRST: Uses free data sources only.
"""

AUTO_FIREWALL = {
    "description": "Automation firewall",
    "AUTO_SAFE": ["metadata formatting fixes", "broken internal links where destination is unambiguous", "missing alt text when source context is clear", "sitemap regeneration", "technical configuration corrections"],
    "AUTO_FIX": ["evidence is strong", "rollback is available", "tests exist"],
    "PR_REQUIRED": ["major content restructuring", "canonical strategy changes", "redirects", "product data changes", "international architecture changes", "significant internal-link restructuring"],
    "HUMAN_REVIEW": ["uncertain search intent", "ambiguous competitor interpretation", "major pricing changes", "legal/trust claims", "uncertain product facts", "risky indexing changes"]
}

def get_auto_firewall_status():
    """Return automation firewall status."""
    return AUTO_FIREWALL
