"""
SEO Agent Firewall - Automated protection against destructive changes
"""

FIREWALL_RULES = {
  "mass_noindex": {
    "description": "Block mass noindex changes",
    "threshold": 10,
    "action": "block",
    "severity": "critical"
  },
  "mass_canonical_changes": {
    "description": "Block mass canonical changes",
    "threshold": 10,
    "action": "block",
    "severity": "critical"
  },
  "mass_redirects": {
    "description": "Block mass redirects",
    "threshold": 10,
    "action": "block",
    "severity": "critical"
  },
  "sitemap_destruction": {
    "description": "Block sitemap destruction",
    "threshold": 1,
    "action": "block",
    "severity": "critical"
  },
  "robots_destruction": {
    "description": "Block robots.txt destruction",
    "threshold": 1,
    "action": "block",
    "severity": "critical"
  },
  "locale_contamination": {
    "description": "Block PK/JP locale contamination",
    "threshold": 1,
    "action": "block",
    "severity": "critical"
  },
  "currency_contamination": {
    "description": "Block PKR/JPY currency contamination",
    "threshold": 1,
    "action": "block",
    "severity": "critical"
  },
  "schema_explosion": {
    "description": "Block schema spam",
    "threshold": 50,
    "action": "block",
    "severity": "high"
  },
  "mass_thin_pages": {
    "description": "Block mass thin page generation",
    "threshold": 10,
    "action": "block",
    "severity": "high"
  },
  "major_performance_regression": {
    "description": "Block major performance regression",
    "threshold": 20,
    "action": "block",
    "severity": "high"
  },
  "data_corruption": {
    "description": "Block data corruption",
    "threshold": 1,
    "action": "block",
    "severity": "critical"
  }
}

THRESHOLDS = {
    "mass_noindex": 10,
    "mass_canonical_changes": 10,
    "mass_redirects": 10,
    "sitemap_destruction": 1,
    "robots_destruction": 1,
    "locale_contamination": 1,
    "currency_contamination": 1,
    "schema_explosion": 50,
    "mass_thin_pages": 10,
    "major_performance_regression": 20,
    "data_corruption": 1
}

def check_rule(rule_name, count):
    """Check if a rule is triggered."""
    threshold = THRESHOLDS.get(rule_name, 0)
    return count >= threshold

def check_all(counts):
    """Check all firewall rules."""
    triggered = []
    for rule, count in counts.items():
        if check_rule(rule, count):
            triggered.append(rule)
    return triggered

def should_block(triggered_rules):
    """Check if changes should be blocked."""
    critical = ["mass_noindex", "mass_canonical_changes", "mass_redirects",
                "sitemap_destruction", "robots_destruction", "locale_contamination",
                "currency_contamination", "data_corruption"]
    for rule in triggered_rules:
        if rule in critical:
            return True
    return False

def alert(triggered_rules):
    """Generate alert for triggered rules."""
    return {"alert": "SEO FIREWALL TRIGGERED", "rules": triggered_rules}
