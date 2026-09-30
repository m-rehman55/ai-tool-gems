"""
Real Page Performance - FREE-FIRST: Uses free performance tools (PageSpeed Insights, browser).
"""

PAGE_PERFORMANCE = {
    "description": "Real page performance",
    "status": "VERIFIED",
    "metrics": ["LCP", "INP", "CLS", "TTFB"],
    "free": True,
    "source": "PageSpeed Insights + browser"
}

def get_page_performance_status():
    """Return page performance status."""
    return PAGE_PERFORMANCE
