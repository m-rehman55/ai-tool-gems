"""
Source Conflict Handling - FREE-FIRST: Uses free data sources only.

Source Conflict Handling
"""
Source Conflict Handling - FREE-FIRST: Uses free data sources only.


CONFLICT = {
  "description": "Source conflict handling",
  "rule": "If sources disagree, store CONFLICT and report sources, values, dates, methodology. The SEO agent may use the data only after applying a documented source-priority rule."
}

def handle_conflict(source_a, value_a, source_b, value_b, dates, methodology):
    """
Source Conflict Handling - FREE-FIRST: Uses free data sources only.
Handle source conflict."""
Source Conflict Handling - FREE-FIRST: Uses free data sources only.

    return {
        "CONFLICT": True,
        "source_a": source_a,
        "value_a": value_a,
        "source_b": source_b,
        "value_b": value_b,
        "dates": dates,
        "methodology": methodology
    }
