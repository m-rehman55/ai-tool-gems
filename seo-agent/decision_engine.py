"""
SEO Agent Decision Engine
"""

DECISION_DIMENSIONS = {
  "confidence": "How confident we are in the data",
  "impact": "Expected SEO impact",
  "effort": "Implementation effort",
  "risk": "Risk of negative SEO impact",
  "evidence_quality": "Quality of evidence supporting the change",
  "affected_urls": "Number of URLs affected",
  "expected_result": "Expected outcome",
  "rollback_method": "How to rollback if needed"
}

DECISIONS = {
  "AUTO": "Low risk, high confidence, verified evidence",
  "PR": "Medium risk or medium confidence",
  "HUMAN": "High risk or low confidence",
  "MONITOR": "Watch and wait",
  "REJECT": "Too risky or no evidence"
}

def evaluate_action(action):
    """Evaluate an action and return decision."""
    confidence = action.get("confidence", "unknown")
    risk = action.get("risk", "unknown")
    impact = action.get("impact", "unknown")
    evidence = action.get("evidence_quality", "unknown")
    affected = action.get("affected_urls", 0)

    # High risk -> HUMAN or REJECT
    if risk == "high":
        if confidence == "low":
            return "REJECT"
        return "HUMAN"

    # Medium risk -> PR
    if risk == "medium":
        return "PR"

    # Low risk, high confidence -> AUTO
    if risk == "low" and confidence == "high":
        return "AUTO"

    # Default -> PR
    return "PR"

def calculate_score(action):
    """Calculate decision score."""
    scores = {"high": 3, "medium": 2, "low": 1, "unknown": 0}
    confidence_score = scores.get(action.get("confidence", "unknown"), 0)
    risk_score = scores.get(action.get("risk", "unknown"), 0)
    impact_score = scores.get(action.get("impact", "unknown"), 0)
    evidence_score = scores.get(action.get("evidence_quality", "unknown"), 0)

    return {
        "confidence": confidence_score,
        "risk": risk_score,
        "impact": impact_score,
        "evidence": evidence_score,
        "total": confidence_score + impact_score - risk_score - (0 if evidence_score > 1 else 2)
    }
