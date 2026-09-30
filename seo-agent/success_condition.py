"""
Success Condition - FREE-FIRST: Uses free data sources only.
Success Condition
"""

SUCCESS_CONDITION = {
  "description": "Success condition",
  "condition": "All REAL data sources are connected OR access blockers are clearly reported.",
  "rule": "Never hide real blockers behind fake data."
}

def get_success_condition():
    """Return success condition."""
    return SUCCESS_CONDITION
