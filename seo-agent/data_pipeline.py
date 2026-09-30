"""
Real Data Acquisition Pipeline
"""

PIPELINE = {
  "description": "Real data acquisition pipeline",
  "stages": [
    "REAL SOURCES",
    "DATA CONNECTORS",
    "RAW DATA STORAGE",
    "NORMALIZATION",
    "VALIDATION",
    "SEO INTELLIGENCE",
    "OPPORTUNITY DETECTION",
    "RECOMMENDATION",
    "SAFE ACTION / PR",
    "DEPLOYMENT",
    "RE-CRAWL",
    "MEASUREMENT",
    "LEARNING"
  ],
  "provenance_required": [
    "value",
    "source",
    "source_url / source_identifier",
    "retrieved_at",
    "market",
    "country",
    "language",
    "device",
    "date_range",
    "confidence/status"
  ]
}

def get_pipeline():
    """Return the data pipeline."""
    return PIPELINE

def validate_provenance(data_point):
    """Validate data provenance."""
    required = ["value", "source", "retrieved_at", "market", "country", "confidence/status"]
    missing = [k for k in required if k not in data_point]
    return {"valid": len(missing) == 0, "missing": missing}
