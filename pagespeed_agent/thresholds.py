"""Official Google Core Web Vitals Thresholds and Classification.

Based on current Google Search Central and web.dev specifications (2026).
Distinguishes GOOD, NEEDS_IMPROVEMENT, and POOR categories.
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Tuple


class Rating(str, Enum):
    GOOD = "GOOD"
    NEEDS_IMPROVEMENT = "NEEDS_IMPROVEMENT"
    POOR = "POOR"
    UNKNOWN = "UNKNOWN"


# Threshold boundaries: (good_max, needs_improvement_max)
THRESHOLDS: Dict[str, Tuple[float, float]] = {
    # Real-User & Lab Core Web Vitals
    "lcp": (2500.0, 4000.0),       # Largest Contentful Paint (ms)
    "inp": (200.0, 500.0),         # Interaction to Next Paint (ms)
    "cls": (0.10, 0.25),           # Cumulative Layout Shift (unitless)
    # Supporting Diagnostic Metrics
    "fcp": (1800.0, 3000.0),       # First Contentful Paint (ms)
    "ttfb": (800.0, 1800.0),       # Time to First Byte (ms)
    "tbt": (200.0, 600.0),         # Total Blocking Time (ms)
    "speed_index": (3400.0, 5800.0) # Speed Index (ms)
}


def classify_metric(metric_name: str, value: float) -> Rating:
    """Classify metric value against official Google Web Vitals boundaries."""
    key = metric_name.lower().replace("-", "_")
    if key not in THRESHOLDS:
        return Rating.UNKNOWN

    good_max, needs_max = THRESHOLDS[key]
    if value <= good_max:
        return Rating.GOOD
    elif value <= needs_max:
        return Rating.NEEDS_IMPROVEMENT
    else:
        return Rating.POOR

