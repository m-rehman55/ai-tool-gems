"""
SEO Agent Learning System
"""

LEARNING = {
  "description": "HERMES learning system",
  "for_every_significant_change": [
    "expected result",
    "actual result",
    "difference",
    "lesson",
    "next action"
  ],
  "learn_from": [
    "success",
    "failure",
    "rollback",
    "ranking changes",
    "CTR changes",
    "traffic changes",
    "content decay",
    "competitor movements",
    "algorithm/search changes",
    "product changes"
  ],
  "status": "active"
}

def record_learning(expected, actual, difference, lesson, next_action):
    """Record a learning."""
    return {
        "expected_result": expected,
        "actual_result": actual,
        "difference": difference,
        "lesson": lesson,
        "next_action": next_action
    }

def get_learnings():
    """Return learning system status."""
    return LEARNING
