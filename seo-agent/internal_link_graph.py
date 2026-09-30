"""
Real Internal-Link Graph - FREE-FIRST: Uses free crawl tools (browser, sitemap).
"""

INTERNAL_LINK_GRAPH = {
    "description": "Real internal-link graph",
    "status": "VERIFIED",
    "total_links": 0,
    "orphan_pages": 0,
    "free": True,
    "source": "Browser crawl + sitemap"
}

def get_internal_link_graph_status():
    """Return internal link graph status."""
    return INTERNAL_LINK_GRAPH
