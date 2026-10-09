"""
Final Report Format - FREE-FIRST: Uses free data sources only.
"""

FINAL_REPORT = {
    "description": "Final report format",
    "sections": ["Real SEO Data Engine Status", "Production", "Google Search Console", "Google Analytics", "SERP", "Keyword Intelligence", "Competitor Intelligence", "Backlinks", "Google Trends", "Data Provenance", "Fake-data protection", "Pakistan", "Telegram", "Deployment", "GitHub", "Real Data Collected", "Access Required", "Blockers", "Next Automated Collection"],
    "statuses": ["VERIFIED / FAILED", "CONNECTED / ACCESS_REQUIRED / ERROR", "CONNECTED / PARTIAL / ACCESS_REQUIRED", "VERIFIED / PARTIAL / ACCESS_REQUIRED", "CONNECTED / NOT_AVAILABLE", "CONNECTED / PARTIAL / NOT_AVAILABLE", "VERIFIED / NOT_DEPLOYED / BLOCKED"],
    "rule": "Return exactly. List actual counts only. If unavailable, use NOT_AVAILABLE."
}

def get_final_report_status():
    """Return final report status."""
    return FINAL_REPORT
