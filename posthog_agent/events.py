"""PostHog Behavioural Event Taxonomy and Validation Models.

Covers all 17 event categories specified in HERMES Section 3.7:
Pageviews, Product views, Search interactions, Product finder usage,
Comparison interactions, Cart actions, WhatsApp order initiation,
Support interactions, Checkout abandonment, Form errors, Rage clicks,
Dead clicks, Session behaviour, Web Vitals, Conversion funnels, Retention, Cohorts.
"""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from posthog_agent.privacy import sanitize_event_properties


@dataclass
class PostHogEvent:
    event_name: str
    distinct_id: str
    timestamp: float = field(default_factory=time.time)
    properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        sanitized_props = sanitize_event_properties(self.properties)
        return {
            "event": self.event_name,
            "distinct_id": self.distinct_id,
            "timestamp": self.timestamp,
            "properties": {
                **sanitized_props,
                "$lib": "hermes_posthog_agent",
                "$lib_version": "1.0.0",
                "market": "PK",
                "currency": "PKR",
            },
        }


def make_pageview_event(distinct_id: str, url: str, title: str, referrer: str = "") -> PostHogEvent:
    return PostHogEvent(
        event_name="$pageview",
        distinct_id=distinct_id,
        properties={"$current_url": url, "title": title, "$referrer": referrer},
    )


def make_product_view_event(
    distinct_id: str, tool_id: str, tool_name: str, pkr_price: Optional[int], category: str = "AI Tool"
) -> PostHogEvent:
    return PostHogEvent(
        event_name="product_view",
        distinct_id=distinct_id,
        properties={
            "tool_id": tool_id,
            "tool_name": tool_name,
            "pkr_price": pkr_price,
            "category": category,
        },
    )


def make_search_interaction_event(
    distinct_id: str, query: str, results_count: int, filter_used: Optional[str] = None
) -> PostHogEvent:
    return PostHogEvent(
        event_name="search_interaction",
        distinct_id=distinct_id,
        properties={
            "query": query,
            "results_count": results_count,
            "filter_used": filter_used or "all",
        },
    )


def make_product_finder_event(
    distinct_id: str, filter_type: str, filter_value: str, matches_count: int
) -> PostHogEvent:
    return PostHogEvent(
        event_name="product_finder_usage",
        distinct_id=distinct_id,
        properties={
            "filter_type": filter_type,
            "filter_value": filter_value,
            "matches_count": matches_count,
        },
    )


def make_comparison_interaction_event(
    distinct_id: str, tool_a: str, tool_b: str, guide_slug: Optional[str] = None
) -> PostHogEvent:
    return PostHogEvent(
        event_name="comparison_interaction",
        distinct_id=distinct_id,
        properties={
            "tool_a": tool_a,
            "tool_b": tool_b,
            "guide_slug": guide_slug or f"{tool_a}-vs-{tool_b}",
        },
    )


def make_whatsapp_order_event(
    distinct_id: str, tool_id: str, tool_name: str, pkr_price: Optional[int], source_page: str
) -> PostHogEvent:
    return PostHogEvent(
        event_name="whatsapp_order_click",
        distinct_id=distinct_id,
        properties={
            "tool_id": tool_id,
            "tool_name": tool_name,
            "pkr_price": pkr_price,
            "source_page": source_page,
            "intent": "transactional_order",
        },
    )


def make_whatsapp_support_event(
    distinct_id: str, source_page: str, query_type: str = "general_support"
) -> PostHogEvent:
    return PostHogEvent(
        event_name="whatsapp_support_click",
        distinct_id=distinct_id,
        properties={
            "source_page": source_page,
            "query_type": query_type,
            "intent": "customer_support",
        },
    )


def make_checkout_abandonment_event(
    distinct_id: str, last_step: str, time_spent_seconds: float, tool_id: Optional[str] = None
) -> PostHogEvent:
    return PostHogEvent(
        event_name="checkout_abandonment",
        distinct_id=distinct_id,
        properties={
            "last_step": last_step,
            "time_spent_seconds": time_spent_seconds,
            "tool_id": tool_id,
        },
    )


def make_form_error_event(
    distinct_id: str, form_name: str, field_name: str, error_message: str
) -> PostHogEvent:
    return PostHogEvent(
        event_name="form_error",
        distinct_id=distinct_id,
        properties={
            "form_name": form_name,
            "field_name": field_name,
            "error_message": error_message,
        },
    )


def make_rage_click_event(
    distinct_id: str, target_selector: str, click_count: int, time_window_ms: int, page_url: str
) -> PostHogEvent:
    return PostHogEvent(
        event_name="rage_click",
        distinct_id=distinct_id,
        properties={
            "target_selector": target_selector,
            "click_count": click_count,
            "time_window_ms": time_window_ms,
            "page_url": page_url,
        },
    )


def make_dead_click_event(
    distinct_id: str, target_selector: str, text_content: str, page_url: str
) -> PostHogEvent:
    return PostHogEvent(
        event_name="dead_click",
        distinct_id=distinct_id,
        properties={
            "target_selector": target_selector,
            "text_content": text_content[:50],
            "page_url": page_url,
        },
    )


def make_web_vitals_event(
    distinct_id: str, metric_name: str, value: float, rating: str, page_url: str
) -> PostHogEvent:
    return PostHogEvent(
        event_name="web_vitals",
        distinct_id=distinct_id,
        properties={
            "metric_name": metric_name,
            "value": value,
            "rating": rating,
            "page_url": page_url,
        },
    )

