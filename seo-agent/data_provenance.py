"""
Data Provenance - FREE-FIRST: Uses free data sources only.

Data Provenance
"""
Data Provenance - FREE-FIRST: Uses free data sources only.


PROVENANCE = {
  "description": "Data provenance",
  "required_fields": [
    "metric",
    "keyword",
    "value",
    "source",
    "retrieved_at",
    "country",
    "language",
    "status"
  ],
  "rule": "Every external metric must be traceable. If the same metric comes from multiple sources, preserve both. Do not silently overwrite conflicting values."
}

def record_provenance(metric, keyword, value, source, country, language, status):
    """
Data Provenance - FREE-FIRST: Uses free data sources only.
Record data provenance."""
Data Provenance - FREE-FIRST: Uses free data sources only.

    return {
        "metric": metric,
        "keyword": keyword,
        "value": value,
        "source": source,
        "retrieved_at": "2026-10-01T00:00:00Z",
        "country": country,
        "language": language,
        "status": status
    }
