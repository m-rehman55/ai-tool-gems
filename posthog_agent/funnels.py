"""PostHog Conversion Funnel and Drop-Off Analysis Module.

Implements the 5-stage e-commerce funnel specified in HERMES Section 3.7:
Landing Page → Product View → Product Selection → WhatsApp Order → Payment Confirmation.
Calculates step-by-step conversion and drop-off, identifies bottlenecks,
and enforces A/B testing safety rules (zero commercial deception, sample size validation).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class FunnelStep:
    step_number: int
    step_name: str
    event_trigger: str
    unique_users: int
    conversion_from_previous_pct: float
    dropoff_pct: float


@dataclass
class FunnelReport:
    total_starters: int
    total_converters: int
    overall_conversion_pct: float
    steps: List[FunnelStep]
    bottleneck_step: Optional[str] = None
    diagnostics: List[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_starters": self.total_starters,
            "total_converters": self.total_converters,
            "overall_conversion_pct": round(self.overall_conversion_pct, 2),
            "bottleneck_step": self.bottleneck_step,
            "diagnostics": self.diagnostics or [],
            "steps": [asdict(s) for s in self.steps],
        }


def analyze_ecom_funnel(step_counts: Dict[str, int]) -> FunnelReport:
    """Analyze counts across the standard 5-stage funnel:

    Stage 1: Landing Page ($pageview)
    Stage 2: Product View (product_view / view_item)
    Stage 3: Product Selection (select_item)
    Stage 4: WhatsApp Order Initiation (whatsapp_order_click / begin_checkout)
    Stage 5: Payment Confirmation (purchase / verified order)
    """
    stages = [
        (1, "Landing Page", "$pageview", step_counts.get("landing_page", step_counts.get("$pageview", 0))),
        (2, "Product View", "product_view", step_counts.get("product_view", 0)),
        (3, "Product Selection", "select_item", step_counts.get("product_selection", step_counts.get("select_item", 0))),
        (4, "WhatsApp Order Initiation", "whatsapp_order_click", step_counts.get("whatsapp_order", step_counts.get("whatsapp_order_click", 0))),
        (5, "Payment Confirmation", "purchase", step_counts.get("payment_confirmation", step_counts.get("purchase", 0))),
    ]

    total_starters = stages[0][3]
    total_converters = stages[-1][3]
    overall_pct = (total_converters / total_starters * 100.0) if total_starters > 0 else 0.0

    steps: List[FunnelStep] = []
    prev_count = total_starters
    highest_dropoff = -1.0
    bottleneck = None
    diagnostics = []

    for num, name, trigger, count in stages:
        if num == 1:
            conv_prev = 100.0 if count > 0 else 0.0
            dropoff = 0.0
        else:
            conv_prev = (count / prev_count * 100.0) if prev_count > 0 else 0.0
            dropoff = 100.0 - conv_prev
            if dropoff > highest_dropoff and prev_count > 0:
                highest_dropoff = dropoff
                bottleneck = name

        steps.append(FunnelStep(
            step_number=num,
            step_name=name,
            event_trigger=trigger,
            unique_users=count,
            conversion_from_previous_pct=round(conv_prev, 2),
            dropoff_pct=round(dropoff, 2),
        ))
        prev_count = count

    if bottleneck:
        diagnostics.append(f"Highest drop-off detected at '{bottleneck}' ({round(highest_dropoff, 1)}% drop-off).")
        if bottleneck == "Product View":
            diagnostics.append("Recommendation: Enhance internal link visibility from homepage and price guides.")
        elif bottleneck == "Product Selection":
            diagnostics.append("Recommendation: Clarify PKR pricing, verified features, and replacement warranty on tool pages.")
        elif bottleneck == "WhatsApp Order Initiation":
            diagnostics.append("Recommendation: Check floating WhatsApp widget visibility and CTA clickability.")
        elif bottleneck == "Payment Confirmation":
            diagnostics.append("Recommendation: Verify response time on WhatsApp customer support and confirm domestic payment rails (EasyPaisa/JazzCash).")

    return FunnelReport(
        total_starters=total_starters,
        total_converters=total_converters,
        overall_conversion_pct=overall_pct,
        steps=steps,
        bottleneck_step=bottleneck,
        diagnostics=diagnostics,
    )


def validate_ab_experiment_policy(
    experiment_name: str,
    variants: List[str],
    sample_size_per_variant: int,
    involves_pricing_diff: bool = False,
    involves_policy_diff: bool = False,
) -> Dict[str, Any]:
    """Enforces strict safety rules for A/B testing:

    1. Never run experiments with differing commercial terms or prices (violates consumer trust).
    2. Minimum sample size threshold (1,000 users per variant) before drawing conclusions.
    """
    violations = []
    if involves_pricing_diff:
        violations.append("REJECTED: Pricing discrimination or varying commercial terms across variants is strictly prohibited.")
    if involves_policy_diff:
        violations.append("REJECTED: Differing return/replacement terms across variants is strictly prohibited.")
    if sample_size_per_variant < 1000:
        violations.append(f"INSUFFICIENT_POWER: Sample size ({sample_size_per_variant}) is below minimum statistical validity threshold (1,000 per variant).")

    is_safe = len(violations) == 0
    return {
        "experiment_name": experiment_name,
        "is_safe": is_safe,
        "status": "APPROVED" if is_safe else "REJECTED",
        "violations": violations,
    }

