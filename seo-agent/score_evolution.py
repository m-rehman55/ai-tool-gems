"""
SEO Agent Score Evolution
"""

EVOLUTION = {
  "description": "SEO score evolution tracking",
  "track": [
    "previous score",
    "current score",
    "delta",
    "reason for change",
    "evidence",
    "remaining weaknesses"
  ],
  "rule": "Never inflate the score. A lower score is acceptable if the measurement system becomes more accurate.",
  "current_score": 42,
  "previous_score": 38,
  "delta": 4
}

def update_score(current, previous, reason, evidence):
    """Update SEO score."""
    delta = current - previous
    return {
        "previous_score": previous,
        "current_score": current,
        "delta": delta,
        "reason": reason,
        "evidence": evidence,
        "remaining_weaknesses": []
    }

def get_score():
    """Return current score evolution."""
    return EVOLUTION
