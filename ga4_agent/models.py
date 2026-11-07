"""
models.py - Data Models for GA4 Analytics & Conversion Intelligence.

Defines:
- GA4SessionSummary: Pakistan traffic, channel grouping, landing page performance.
- GA4EcommerceFunnel: view_item -> select_item -> begin_checkout -> verified_purchase.
- OfflineVerifiedOrder: WhatsApp verified payment transaction with client_id provenance.
- OfflineRefund: Symmetrical refund record tied to a verified parent order.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


def validate_client_id(
    client_id: Optional[str],
    customer_phone_hash: Optional[str] = None
) -> Tuple[bool, Optional[str], str]:
    """
    Validates GA4 client_id and enforces provenance integrity.

    Returns:
        (is_valid, sanitized_client_id, provenance_or_reason)
    """
    if client_id is None:
        return True, None, "missing"

    c_id = str(client_id).strip()
    if not c_id:
        return True, None, "missing"

    lower = c_id.lower()

    # Reject email PII
    if "@" in c_id:
        return False, None, "rejected_email_pii"

    # Reject direct match or substring of phone hash
    if customer_phone_hash and (c_id in customer_phone_hash or customer_phone_hash in c_id):
        return False, None, "rejected_phone_hash_derivation"

    # Reject explicit PII / phone keywords in identifier
    for marker in ("phone", "hash", "email", "customer", "user", "mobile", "contact"):
        if marker in lower:
            return False, None, f"rejected_pii_marker_{marker}"

    # Enforce standard GA4 client_id regex (pseudo-random e.g. 123456789.123456789 or UUID)
    if not re.match(r"^[0-9a-zA-Z._-]{10,64}$", c_id):
        return False, None, "invalid_format_regex"

    return True, c_id, "browser_cookie"


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
    client_id: Optional[str] = None  # Validated GA4 _ga client_id
    client_id_provenance: str = "none"  # "browser_cookie", "none", "rejected"
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
        client_id_provenance: Optional[str] = None,
    ) -> OfflineVerifiedOrder:
        phone_hash = hashlib.sha256(raw_phone.strip().encode("utf-8")).hexdigest()[:16]
        now_iso = datetime.now(timezone.utc).isoformat()

        is_valid, validated_cid, prov = validate_client_id(client_id, phone_hash)
        if not is_valid:
            raise ValueError(
                f"Invalid client_id '{client_id}': {prov}. "
                "Deriving client_id from phone hash or PII is strictly prohibited."
            )

        final_provenance = client_id_provenance or prov

        return cls(
            transaction_id=transaction_id.strip(),
            tool_slug=tool_slug.strip().lower(),
            tool_name=tool_name.strip(),
            pkr_amount=float(pkr_amount),
            payment_rail=payment_rail.strip(),
            verified_at=now_iso,
            customer_phone_hash=phone_hash,
            client_id=validated_cid,
            client_id_provenance=final_provenance,
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
