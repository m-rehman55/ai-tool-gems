"""
Automation Firewall - FREE-FIRST: Uses free data sources only.

Automation Firewall
"""
Automation Firewall - FREE-FIRST: Uses free data sources only.


AUTO_FIREWALL = {
  "description": "Automation firewall",
  "AUTO_SAFE": [
    "metadata formatting fixes",
    "broken internal links where destination is unambiguous",
    "missing alt text when source context is clear",
    "sitemap regeneration",
    "technical configuration corrections"
  ],
  "AUTO_FIX": [
    "evidence is strong",
    "rollback is available",
    "tests exist"
  ],
  "PR_REQUIRED": [
    "major content restructuring",
    "canonical strategy changes",
    "redirects",
    "product data changes",
    "international architecture changes",
    "significant internal-link restructuring"
  ],
  "HUMAN_REVIEW": [
    "uncertain search intent",
    "ambiguous competitor interpretation",
    "major pricing changes",
    "legal/trust claims",
    "uncertain product facts",
    "risky indexing changes"
  ]
}

def get_auto_firewall_status():
    """
Automation Firewall - FREE-FIRST: Uses free data sources only.
Return automation firewall status."""
Automation Firewall - FREE-FIRST: Uses free data sources only.

    return AUTO_FIREWALL

def classify_action(action):
    """
Automation Firewall - FREE-FIRST: Uses free data sources only.
Classify an action for automation firewall."""
Automation Firewall - FREE-FIRST: Uses free data sources only.

    safe = AUTO_FIREWALL.get("AUTO-SAFE", [])
    fix = AUTO_FIREWALL.get("AUTO-FIX", [])
    pr = AUTO_FIREWALL.get("PR-REQUIRED", [])
    human = AUTO_FIREWALL.get("HUMAN-REVIEW", [])
    if action in safe:
        return "AUTO-SAFE"
    if action in fix:
        return "AUTO-FIX"
    if action in pr:
        return "PR_REQUIRED"
    if action in human:
        return "HUMAN_REVIEW"
    return "HUMAN_REVIEW"