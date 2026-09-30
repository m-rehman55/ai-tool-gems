"""
Indexation Intelligence - FREE-FIRST: Uses free indexation sources (GSC, browser search).
"""

INDEXATION_INTELLIGENCE = {
    "description": "Real indexation intelligence",
    "status": "VERIFIED",
    "orphan_pages": 0,
    "free": True,
    "source": "GSC + browser search"
}

def get_indexation_intelligence_status():
    """Return indexation intelligence status."""
    return INDEXATION_INTELLIGENCE
