"""
models.py - Data Models for GA4 Analytics & Conversion Intelligence.

Defines:
- GA4SessionSummary: Pakistan traffic, channel grouping, landing page performance.
- GA4EcommerceFunnel: view_item -> select_item -> begin_checkout -> verified_purchase.
- OfflineVerifiedOrder: WhatsApp verified payment transaction with deduplication ID.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class ChannelPerformance:
    channel: str  # "Organic Search", "Direct", "Referral", "AI Assistant", "Social"
    sessions: int
    users: int
    engagement_rate: float
    conversions: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LandingPagePerformance:
    path: str
    page_type: str  # "homepage", "product", "guide", "comparison", "prices", "deals"
    sessions: int
    active_users: int
    avg_engagement_time_sec: float
    order_clicks: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class GA4EcommerceFunnel:
    period: str
    product_views: int  # view_item
    product_selections: int  # select_item
    order_initiations: int  # whatsapp_order_click / begin_checkout
    verified_purchases: int  # verified purchases with payment confirmation
    currency: str = "PKR"
    total_revenue_pkr: float = 0.0

    @property
    def checkout_dropoff_pct(self) -> float:
        """Percentage of order initiations that did not complete payment."""
        if self.order_initiations <= 0:
            return 0.0
        completed = min(self.verified_purchases, self.order_initiations)
        return round(((self.order_initiations - completed) / self.order_initiations) * 100.0, 1)

    @property
    def overall_conversion_rate_pct(self) -> float:
        """Percentage of product views leading to verified purchases."""
        if self.product_views <= 0:
            return 0.0
        return round((self.verified_purchases / self.product_views) * 100.0, 2)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["checkout_dropoff_pct"] = self.checkout_dropoff_pct
        d["overall_conversion_rate_pct"] = self.overall_conversion_rate_pct
        return d


@dataclass
class OfflineVerifiedOrder:
    transaction_id: str  # e.g., "ATG-20261105-001"
    tool_slug: str
    tool_name: str
    pkr_amount: float
    payment_rail: str  # "EasyPaisa", "JazzCash", "SadaPay", "NayaPay", "Bank IBFT"
    verified_at: str
    customer_phone_hash: str  # SHA-256 masked phone number for privacy
    client_id: Optional[str] = None  # Recovered GA4 _ga client_id
    is_imported_to_ga4: bool = False
    imported_at: Optional[str] = None

    @classmethod
    def create(
        cls,
        transaction_id: str,
        tool_slug: str,
        tool_name: str,
        pkr_amount: float,
        payment_rail: str,
        raw_phone: str,
        client_id: Optional[str] = None,
    ) -> OfflineVerifiedOrder:
        phone_hash = hashlib.sha256(raw_phone.strip().encode("utf-8")).hexdigest()[:16]
        now_iso = datetime.now(timezone.utc).isoformat()
        return cls(
            transaction_id=transaction_id.strip(),
            tool_slug=tool_slug.strip().lower(),
            tool_name=tool_name.strip(),
            pkr_amount=float(pkr_amount),
            payment_rail=payment_rail.strip(),
            verified_at=now_iso,
            customer_phone_hash=phone_hash,
            client_id=client_id,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class OfflineRefund:
    transaction_id: str  # Original purchase transaction_id e.g. "ATG-20261105-001"
    refund_id: str       # Unique refund identifier e.g. "REF-20261106-001"
    tool_slug: str
    tool_name: str
    pkr_amount: float
    reason: str
    verified_at: str
    is_imported_to_ga4: bool = False
    imported_at: Optional[str] = None

    @classmethod
    def create(
        cls,
        transaction_id: str,
        refund_id: str,
        tool_slug: str,
        tool_name: str,
        pkr_amount: float,
        reason: str = "customer_request"
    ) -> OfflineRefund:
        now_iso = datetime.now(timezone.utc).isoformat()
        return cls(
            transaction_id=transaction_id.strip(),
            refund_id=refund_id.strip(),
            tool_slug=tool_slug.strip().lower(),
            tool_name=tool_name.strip(),
            pkr_amount=float(pkr_amount),
            reason=reason.strip(),
            verified_at=now_iso,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

