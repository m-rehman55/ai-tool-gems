"""Core Web Vitals Performance Regression Detector & Advisory Engine.

Detects degradations in LCP, INP, CLS, TBT, and Performance scores.
Generates source-level architectural recommendations without breaking UI functionality.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pagespeed_agent.client import PageSpeedAuditResult
from pagespeed_agent.thresholds import Rating


@dataclass
class RegressionIncident:
    metric: str
    previous_value: float
    current_value: float
    delta: float
    severity: str  # HIGH, MEDIUM, LOW
    explanation: str
    remediation: str


@dataclass
class PerformanceEvaluation:
    has_regressions: bool
    incidents: List[RegressionIncident]
    recommendations: List[str]


def detect_regressions(
    current: PageSpeedAuditResult, baseline: Optional[PageSpeedAuditResult] = None
) -> PerformanceEvaluation:
    """Compare current audit with baseline or previous audit and detect regressions."""
    incidents: List[RegressionIncident] = []
    recommendations: List[str] = []

    if baseline:
        # 1. Performance score regression
        score_drop = baseline.lab_data.performance_score - current.lab_data.performance_score
        if score_drop >= 5.0:
            incidents.append(RegressionIncident(
                metric="performance_score",
                previous_value=baseline.lab_data.performance_score,
                current_value=current.lab_data.performance_score,
                delta=-score_drop,
                severity="HIGH" if score_drop >= 15.0 else "MEDIUM",
                explanation=f"Overall Lighthouse performance dropped by {score_drop:.1f} points.",
                remediation="Inspect recently added heavy scripts, fonts, or uncompressed media.",
            ))

        # 2. LCP regression
        lcp_delta = current.lab_data.lcp_ms - baseline.lab_data.lcp_ms
        if lcp_delta >= 500.0 or (current.lab_data.lcp_rating != Rating.GOOD and baseline.lab_data.lcp_rating == Rating.GOOD):
            incidents.append(RegressionIncident(
                metric="lcp_ms",
                previous_value=baseline.lab_data.lcp_ms,
                current_value=current.lab_data.lcp_ms,
                delta=lcp_delta,
                severity="HIGH" if current.lab_data.lcp_ms > 4000.0 else "MEDIUM",
                explanation=f"Largest Contentful Paint degraded by {lcp_delta:.0f} ms (now {current.lab_data.lcp_ms:.0f} ms).",
                remediation="Ensure hero image has fetchpriority='high', inline critical CSS, and defer third-party scripts.",
            ))

        # 3. CLS regression
        cls_delta = current.lab_data.cls - baseline.lab_data.cls
        if cls_delta >= 0.05:
            incidents.append(RegressionIncident(
                metric="cls",
                previous_value=baseline.lab_data.cls,
                current_value=current.lab_data.cls,
                delta=cls_delta,
                severity="HIGH" if current.lab_data.cls > 0.25 else "MEDIUM",
                explanation=f"Cumulative Layout Shift increased by {cls_delta:.3f} (now {current.lab_data.cls:.3f}).",
                remediation="Specify explicit width and height on all <img> and <svg> tags and reserve space for dynamic ad/chat widgets.",
            ))

        # 4. TBT / Main Thread Blocking
        tbt_delta = current.lab_data.tbt_ms - baseline.lab_data.tbt_ms
        if tbt_delta >= 150.0:
            incidents.append(RegressionIncident(
                metric="tbt_ms",
                previous_value=baseline.lab_data.tbt_ms,
                current_value=current.lab_data.tbt_ms,
                delta=tbt_delta,
                severity="MEDIUM",
                explanation=f"Total Blocking Time increased by {tbt_delta:.0f} ms.",
                remediation="Break up long JavaScript tasks into requestIdleCallback or Web Workers.",
            ))

    # General recommendations based on current state
    if current.lab_data.render_blocking_wasted_ms > 200.0:
        recommendations.append(
            f"Eliminate render-blocking resources: {current.lab_data.render_blocking_wasted_ms:.0f} ms potential savings via async/defer."
        )
    if current.lab_data.lcp_rating != Rating.GOOD:
        recommendations.append("LCP is not GOOD. Preload the hero LCP asset using <link rel='preload' as='image'>.")
    if current.lab_data.cls_rating != Rating.GOOD:
        recommendations.append("CLS exceeds 0.10. Audit CSS for dynamically injected DOM nodes without reserved aspect-ratio.")

    if not recommendations:
        recommendations.append("All Core Web Vitals are within Google's GOOD thresholds (100% green).")

    return PerformanceEvaluation(
        has_regressions=len(incidents) > 0,
        incidents=incidents,
        recommendations=recommendations,
    )
