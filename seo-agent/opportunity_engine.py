"""
SEO Opportunity Scoring Engine — AIToolGems Pakistan
----------------------------------------------------
Scores findings and optimization candidates using the strict 6-dimensional matrix:
1. Confidence: High / Medium / Low (empirical evidence vs hypothesis)
2. Impact: High (top 3 ranking potential) / Medium (positions 4-10) / Low (CTR tweak)
3. Effort: Low (< 2h) / Medium (2-8h) / High (> 8h)
4. Risk: Low (reversible one-liner) / Medium (content edit) / High (URL/routing)
5. Evidence Quality: High (GSC data / live crawl) / Medium (trend pattern) / Low (assumption)
6. Decision: AUTO-SAFE / PR / HUMAN REVIEW / MONITOR / REJECT
Zero-budget, Google-compliant, never-fabricate policy.
"""

def score_opportunity(
    title: str,
    target_url: str,
    confidence: str,
    impact: str,
    effort: str,
    risk: str,
    evidence_quality: str,
    evidence_detail: str,
    expected_delta: str
) -> dict:
    """Calculates classification category based on risk, confidence, and effort."""
    c_upper = confidence.upper()
    i_upper = impact.upper()
    e_upper = effort.upper()
    r_upper = risk.upper()
    eq_upper = evidence_quality.upper()

    # Decision Matrix Rules
    if r_upper == "HIGH" or eq_upper == "LOW":
        decision = "HUMAN REVIEW"
    elif r_upper == "MEDIUM":
        decision = "PR"
    elif r_upper == "LOW" and c_upper == "HIGH" and e_upper == "LOW":
        decision = "AUTO-SAFE"
    elif i_upper == "LOW" and e_upper == "HIGH":
        decision = "MONITOR"
    else:
        decision = "PR"

    return {
        "title": title,
        "target_url": target_url,
        "confidence": confidence,
        "impact": impact,
        "effort": effort,
        "risk": risk,
        "evidence_quality": evidence_quality,
        "evidence_detail": evidence_detail,
        "expected_delta": expected_delta,
        "decision": decision
    }

OPPORTUNITY_ENGINE = {
    "description": "AIToolGems Pakistan Dynamic Opportunity Scoring Engine",
    "status": "VERIFIED",
    "market": "en-PK",
    "scoring_matrix": ["confidence", "impact", "effort", "risk", "evidence_quality"],
    "decision_classes": ["AUTO-SAFE", "PR", "HUMAN REVIEW", "MONITOR", "REJECT"],
    "free_first": True,
    "last_audit": "2026-10-11"
}

def get_opportunity_status() -> dict:
    """Return opportunity engine status."""
    return OPPORTUNITY_ENGINE
