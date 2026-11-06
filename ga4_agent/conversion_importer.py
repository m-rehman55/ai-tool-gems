"""
conversion_importer.py - Authorized Offline Conversion Importer & Server-Side Confirmation Workflow.

Strictly enforces HERMES Conversion Integrity:
1. NEVER records a purchase when a visitor merely clicks WhatsApp (treated strictly as begin_checkout).
2. ONLY records a confirmed purchase when domestic payment has been received and verified.
3. Uses immutable transaction IDs (e.g. ATG-YYYYMMDD-XXX) with strict deduplication.
4. Masks customer identifiers (SHA-256 phone hash) for strict privacy compliance.
5. Maintains PKR as the sole business reporting currency.
6. Formats GA4 Measurement Protocol payload (/mp/collect) for server-side ingestion.
"""

from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from ga4_agent.models import OfflineRefund, OfflineVerifiedOrder

logger = logging.getLogger("ga4_agent.conversion_importer")

MEASUREMENT_ID = "G-NQJCMDCLLP"
GA4_MP_ENDPOINT = "https://www.google-analytics.com/mp/collect"


class ConversionImporter:
    """Manages offline verified WhatsApp order records and server-side GA4 import."""

    def __init__(self, data_dir: Optional[Path] = None):
        base_dir = Path(__file__).resolve().parent.parent
        self.data_dir = data_dir or (base_dir / "data" / "orders")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.orders_file = self.data_dir / "verified_orders.json"
        self.refunds_file = self.data_dir / "verified_refunds.json"
        self.import_log_file = self.data_dir / "ga4_import_log.json"

    def load_orders(self) -> List[OfflineVerifiedOrder]:
        """Loads verified order history from persistent storage."""
        if not self.orders_file.exists():
            return []
        try:
            raw = json.loads(self.orders_file.read_text(encoding="utf-8"))
            return [
                OfflineVerifiedOrder(
                    transaction_id=item["transaction_id"],
                    tool_slug=item.get("tool_slug", ""),
                    tool_name=item.get("tool_name", ""),
                    pkr_amount=float(item.get("pkr_amount", 0.0)),
                    payment_rail=item.get("payment_rail") or item.get("payment_method", "Bank IBFT"),
                    verified_at=item.get("verified_at") or item.get("order_timestamp", datetime.now(timezone.utc).isoformat()),
                    customer_phone_hash=item.get("customer_phone_hash", ""),
                    client_id=item.get("client_id") or item.get("ga4_client_id"),
                    is_imported_to_ga4=bool(item.get("is_imported_to_ga4", False)),
                    imported_at=item.get("imported_at"),
                )
                for item in raw
            ]
        except Exception as e:
            logger.warning(f"Failed loading verified orders: {e}")
            return []

    def record_verified_payment(
        self,
        transaction_id: str,
        tool_slug: str,
        tool_name: str,
        pkr_amount: float,
        payment_rail: str,
        raw_phone: str,
        client_id: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Records a confirmed domestic payment transaction.
        Deduplicates by transaction_id: duplicate IDs are strictly rejected.
        """
        tid = transaction_id.strip()
        if not tid:
            return False, "Transaction ID cannot be empty."

        if pkr_amount <= 0:
            return False, "Order amount in PKR must be greater than zero."

        valid_rails = {"easypaisa", "jazzcash", "sadapay", "nayapay", "raast", "bank ibft", "bank transfer"}
        if payment_rail.lower() not in valid_rails:
            return False, f"Invalid domestic payment rail '{payment_rail}'. Must be EasyPaisa, JazzCash, SadaPay, etc."

        orders = self.load_orders()
        if any(o.transaction_id == tid for o in orders):
            return False, f"Duplicate transaction ID '{tid}' rejected. Deduplication enforced."

        new_order = OfflineVerifiedOrder.create(
            transaction_id=tid,
            tool_slug=tool_slug,
            tool_name=tool_name,
            pkr_amount=pkr_amount,
            payment_rail=payment_rail,
            raw_phone=raw_phone,
            client_id=client_id,
        )
        orders.append(new_order)

        self.orders_file.write_text(
            json.dumps([o.to_dict() for o in orders], indent=2),
            encoding="utf-8",
        )
        return True, f"Verified payment {tid} successfully recorded."

    def build_measurement_protocol_payload(self, order: OfflineVerifiedOrder) -> Optional[Dict[str, Any]]:
        """Formats the official GA4 Measurement Protocol purchase payload."""
        c_id = order.client_id
        if not c_id:
            logger.warning(
                f"Order {order.transaction_id} lacks a legitimately collected GA4 client_id. "
                "Deriving client_id from customer phone hash or PII is strictly prohibited."
            )
            return None

        return {
            "client_id": c_id,
            "non_personalized_ads": False,
            "events": [
                {
                    "name": "purchase",
                    "params": {
                        "transaction_id": order.transaction_id,
                        "value": order.pkr_amount,
                        "currency": "PKR",
                        "payment_type": order.payment_rail,
                        "items": [
                            {
                                "item_id": order.tool_slug,
                                "item_name": order.tool_name,
                                "item_category": "AI Tool Subscription",
                                "price": order.pkr_amount,
                                "quantity": 1,
                            }
                        ],
                    },
                }
            ],
        }

    def dispatch_offline_conversions(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Dispatches all unimported verified orders to GA4 Measurement Protocol.
        Marks orders as imported ONLY upon successful HTTP 200/204 response from GA4.
        Dry-run or missing API secret strictly NEVER mutates order imported state.
        """
        orders = self.load_orders()
        pending = [o for o in orders if not o.is_imported_to_ga4]

        if not pending:
            return {
                "status": "noop",
                "message": "Zero pending verified orders awaiting GA4 import.",
                "imported_count": 0,
            }

        # Case A: Dry run (Generate payload preview, DO NOT mutate state, DO NOT persist)
        if dry_run:
            results = []
            for o in pending:
                payload = self.build_measurement_protocol_payload(o)
                results.append({
                    "transaction_id": o.transaction_id,
                    "status": "dry_run",
                    "pkr_amount": o.pkr_amount,
                    "payload": payload,
                })
            return {
                "status": "dry_run",
                "imported_count": 0,
                "pending_remaining": len(pending),
                "results": results,
            }

        # Case B: Missing API secret (Return BLOCKED_MISSING_API_SECRET, preserve pending records unchanged)
        api_secret = (os.getenv("GA4_API_SECRET") or os.getenv("GA4_MEASUREMENT_SECRET") or "").strip()
        if not api_secret:
            logger.warning("GA4 import blocked: GA4_API_SECRET / GA4_MEASUREMENT_SECRET is missing.")
            return {
                "status": "BLOCKED_MISSING_API_SECRET",
                "message": "GA4 import blocked: Missing API secret. Order records remain pending.",
                "imported_count": 0,
                "pending_remaining": len(pending),
            }

        # Case C: Real request (Send to GA4 MP, mark imported ONLY on successful HTTP 200/204)
        imported_count = 0
        now_iso = datetime.now(timezone.utc).isoformat()
        results: List[Dict[str, Any]] = []
        endpoint = f"{GA4_MP_ENDPOINT}?measurement_id={MEASUREMENT_ID}&api_secret={api_secret}"

        for o in pending:
            payload = self.build_measurement_protocol_payload(o)
            if not payload:
                results.append({
                    "transaction_id": o.transaction_id,
                    "status": "skipped_missing_legitimate_client_id",
                    "message": "Order lacks legitimately collected client_id. Prohibited from deriving identifier from phone or PII.",
                })
                continue

            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                endpoint,
                data=data_bytes,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    # GA4 MP returns HTTP 204 No Content on success
                    if resp.status in (200, 204):
                        o.is_imported_to_ga4 = True
                        o.imported_at = now_iso
                        imported_count += 1
                        results.append({"transaction_id": o.transaction_id, "status": "sent", "http_code": resp.status})
                    else:
                        results.append({"transaction_id": o.transaction_id, "status": "failed_http", "http_code": resp.status})
            except Exception as e:
                sanitized_err = str(e).replace(api_secret, "***") if api_secret else str(e)
                logger.error(f"Failed dispatching offline conversion {o.transaction_id}: {sanitized_err}")
                results.append({"transaction_id": o.transaction_id, "status": "error", "error": sanitized_err})

        # Only persist updated state if at least one order was imported
        if imported_count > 0:
            self.orders_file.write_text(
                json.dumps([o.to_dict() for o in orders], indent=2),
                encoding="utf-8",
            )
            self._append_log(results)

        return {
            "status": "success" if imported_count > 0 else "dispatch_failed",
            "imported_count": imported_count,
            "pending_remaining": len(orders) - sum(1 for o in orders if o.is_imported_to_ga4),
            "results": results,
        }

    # Backward compatibility and prompt convenience alias
    import_verified_orders = dispatch_offline_conversions

    def _append_log(self, entries: List[Dict[str, Any]]) -> None:
        """Appends to durable GA4 import log."""
        log_data = []
        if self.import_log_file.exists():
            try:
                log_data = json.loads(self.import_log_file.read_text(encoding="utf-8"))
            except Exception:
                log_data = []
        log_data.extend(entries)
        self.import_log_file.write_text(json.dumps(log_data[-200:], indent=2), encoding="utf-8")

    def load_refunds(self) -> List[OfflineRefund]:
        """Loads verified refund records from persistent storage."""
        if not self.refunds_file.exists():
            return []
        try:
            raw = json.loads(self.refunds_file.read_text(encoding="utf-8"))
            return [
                OfflineRefund(
                    transaction_id=item["transaction_id"],
                    refund_id=item["refund_id"],
                    tool_slug=item.get("tool_slug", ""),
                    tool_name=item.get("tool_name", ""),
                    pkr_amount=float(item.get("pkr_amount", 0.0)),
                    reason=item.get("reason", "customer_request"),
                    verified_at=item.get("verified_at", datetime.now(timezone.utc).isoformat()),
                    is_imported_to_ga4=bool(item.get("is_imported_to_ga4", False)),
                    imported_at=item.get("imported_at"),
                )
                for item in raw
            ]
        except Exception as e:
            logger.warning(f"Failed loading verified refunds: {e}")
            return []

    def record_verified_refund(
        self,
        transaction_id: str,
        refund_id: str,
        tool_slug: str,
        tool_name: str,
        pkr_amount: float,
        reason: str = "customer_request",
    ) -> Tuple[bool, str]:
        """
        Records a confirmed refund for an existing transaction.
        Enforces refund_id uniqueness and validates positive amount.
        """
        rid = refund_id.strip()
        tid = transaction_id.strip()
        if not rid:
            return False, "Refund ID cannot be empty."
        if not tid:
            return False, "Transaction ID cannot be empty."
        if pkr_amount <= 0:
            return False, "Refund amount in PKR must be greater than zero."

        refunds = self.load_refunds()
        if any(r.refund_id == rid for r in refunds):
            return False, f"Duplicate refund ID '{rid}' rejected."

        new_refund = OfflineRefund.create(
            transaction_id=tid,
            refund_id=rid,
            tool_slug=tool_slug,
            tool_name=tool_name,
            pkr_amount=pkr_amount,
            reason=reason,
        )
        refunds.append(new_refund)

        self.refunds_file.write_text(
            json.dumps([r.to_dict() for r in refunds], indent=2),
            encoding="utf-8",
        )
        return True, f"Verified refund {rid} for transaction {tid} successfully recorded."

    def build_refund_payload(self, refund: OfflineRefund, client_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Formats the official GA4 Measurement Protocol refund payload."""
        c_id = client_id
        if not c_id:
            logger.warning(
                f"Refund {refund.refund_id} lacks a legitimately collected GA4 client_id. "
                "Deriving client_id or fabricating identifier is strictly prohibited."
            )
            return None

        return {
            "client_id": c_id,
            "non_personalized_ads": False,
            "events": [
                {
                    "name": "refund",
                    "params": {
                        "transaction_id": refund.transaction_id,
                        "value": refund.pkr_amount,
                        "currency": "PKR",
                        "items": [
                            {
                                "item_id": refund.tool_slug,
                                "item_name": refund.tool_name,
                                "item_category": "AI Tool Subscription",
                                "price": refund.pkr_amount,
                                "quantity": 1,
                            }
                        ],
                    },
                }
            ],
        }

    def dispatch_offline_refunds(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Dispatches all unimported verified refunds to GA4 Measurement Protocol.
        Marks refunds as imported ONLY upon successful HTTP 200/204 response from GA4.
        Dry-run or missing API secret strictly NEVER mutates refund imported state.
        """
        refunds = self.load_refunds()
        pending = [r for r in refunds if not r.is_imported_to_ga4]

        if not pending:
            return {
                "status": "noop",
                "message": "Zero pending verified refunds awaiting GA4 import.",
                "imported_count": 0,
            }

        # Lookup legitimate client_id from recorded orders
        orders_map = {o.transaction_id: o.client_id for o in self.load_orders() if o.client_id}

        # Case A: Dry run (Generate payload preview, DO NOT mutate state, DO NOT persist)
        if dry_run:
            results = []
            for r in pending:
                c_id = orders_map.get(r.transaction_id)
                payload = self.build_refund_payload(r, client_id=c_id)
                results.append({
                    "refund_id": r.refund_id,
                    "transaction_id": r.transaction_id,
                    "status": "dry_run",
                    "pkr_amount": r.pkr_amount,
                    "payload": payload,
                })
            return {
                "status": "dry_run",
                "imported_count": 0,
                "pending_remaining": len(pending),
                "results": results,
            }

        # Case B: Missing API secret (Return BLOCKED_MISSING_API_SECRET, preserve pending records unchanged)
        api_secret = (os.getenv("GA4_API_SECRET") or os.getenv("GA4_MEASUREMENT_SECRET") or "").strip()
        if not api_secret:
            logger.warning("GA4 refund dispatch blocked: GA4_API_SECRET / GA4_MEASUREMENT_SECRET is missing.")
            return {
                "status": "BLOCKED_MISSING_API_SECRET",
                "message": "GA4 refund dispatch blocked: Missing API secret. Refund records remain pending.",
                "imported_count": 0,
                "pending_remaining": len(pending),
            }

        # Case C: Real request (Send to GA4 MP, mark imported ONLY on successful HTTP 200/204)
        imported_count = 0
        now_iso = datetime.now(timezone.utc).isoformat()
        results: List[Dict[str, Any]] = []
        endpoint = f"{GA4_MP_ENDPOINT}?measurement_id={MEASUREMENT_ID}&api_secret={api_secret}"

        for r in pending:
            c_id = orders_map.get(r.transaction_id)
            payload = self.build_refund_payload(r, client_id=c_id)
            if not payload:
                results.append({
                    "refund_id": r.refund_id,
                    "transaction_id": r.transaction_id,
                    "status": "skipped_missing_legitimate_client_id",
                    "message": "Refund lacks legitimately collected client_id. Prohibited from fabricating identifier.",
                })
                continue

            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                endpoint,
                data=data_bytes,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status in (200, 204):
                        r.is_imported_to_ga4 = True
                        r.imported_at = now_iso
                        imported_count += 1
                        results.append({"refund_id": r.refund_id, "status": "sent", "http_code": resp.status})
                    else:
                        results.append({"refund_id": r.refund_id, "status": "failed_http", "http_code": resp.status})
            except Exception as e:
                sanitized_err = str(e).replace(api_secret, "***") if api_secret else str(e)
                logger.error(f"Failed dispatching offline refund {r.refund_id}: {sanitized_err}")
                results.append({"refund_id": r.refund_id, "status": "error", "error": sanitized_err})

        # Only persist updated state if at least one refund was imported
        if imported_count > 0:
            self.refunds_file.write_text(
                json.dumps([r.to_dict() for r in refunds], indent=2),
                encoding="utf-8",
            )
            self._append_log(results)

        return {
            "status": "success" if imported_count > 0 else "dispatch_failed",
            "imported_count": imported_count,
            "pending_remaining": len(refunds) - sum(1 for r in refunds if r.is_imported_to_ga4),
            "results": results,
        }

