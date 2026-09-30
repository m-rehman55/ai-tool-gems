"""
SEO Agent Original Data Moat
"""

DATA_MOAT = {
  "description": "Original data moat",
  "improve": [
    "price index",
    "price history where genuinely recorded",
    "comparison database",
    "cost calculator",
    "research",
    "statistics",
    "market reports",
    "glossary",
    "buyer guides"
  ],
  "rule": "Original data should become a long-term SEO authority asset.",
  "status": "active"
}

def update_moat(asset):
    """Update a data moat asset."""
    valid_assets = ["price index", "price history", "comparison database", "cost calculator", "research", "statistics", "market reports", "glossary", "buyer guides"]
    if asset in valid_assets:
        return {"asset": asset, "status": "updated"}
    return {"asset": asset, "status": "invalid"}

def get_moat_status():
    """Return data moat status."""
    return DATA_MOAT
