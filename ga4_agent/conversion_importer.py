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

from ga4_agent.models import OfflineVerifiedOrder

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
                    tool_slug=item["tool_slug"],
                    tool_name=item["tool_name"],
                    pkr_amount=float(item["pkr_amount"]),
                    payment_rail=item["payment_rail"],
                    verified_at=item["verified_at"],
                    customer_phone_hash=item["customer_phone_hash"],
                    client_id=item.get("client_id"),
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

    def build_measurement_protocol_payload(self, order: OfflineVerifiedOrder) -> Dict[str, Any]:
        """Formats the official GA4 Measurement Protocol purchase payload."""
        c_id = order.client_id or f"offline_{order.customer_phone_hash}"

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
        Marks orders as imported upon successful HTTP 204 or dry run.
        """
        api_secret = os.getenv("GA4_API_SECRET", "").strip()
        orders = self.load_orders()
        pending = [o for o in orders if not o.is_imported_to_ga4]

        if not pending:
            return {
                "status": "noop",
                "message": "Zero pending verified orders awaiting GA4 import.",
                "imported_count": 0,
            }

        imported_count = 0
        now_iso = datetime.now(timezone.utc).isoformat()
        results: List[Dict[str, Any]] = []

        for o in pending:
            payload = self.build_measurement_protocol_payload(o)
            if dry_run or not api_secret:
                o.is_imported_to_ga4 = True
                o.imported_at = now_iso
                imported_count += 1
                results.append({
                    "transaction_id": o.transaction_id,
                    "status": "dry_run" if dry_run else "simulated_no_api_secret",
                    "pkr_amount": o.pkr_amount,
                    "payload": payload,
                })
            else:
                endpoint = f"{GA4_MP_ENDPOINT}?measurement_id={MEASUREMENT_ID}&api_secret={api_secret}"
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
                except Exception as e:
                    logger.error(f"Failed dispatching offline conversion {o.transaction_id}: {e}")
                    results.append({"transaction_id": o.transaction_id, "status": "error", "error": str(e)})

        # Persist updated state
        self.orders_file.write_text(
            json.dumps([o.to_dict() for o in orders], indent=2),
            encoding="utf-8",
        )

        # Append to import log
        self._append_log(results)

        return {
            "status": "success",
            "imported_count": imported_count,
            "pending_remaining": len(orders) - imported_count,
            "results": results,
        }

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
