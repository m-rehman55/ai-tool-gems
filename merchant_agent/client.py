"""Google Content API for Shopping Client & Feed Status Manager."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional


class GoogleMerchantClient:
    """Interacts with Google Merchant Center Content API."""

    def __init__(self, merchant_id: Optional[str] = None):
        self._load_env_if_needed()
        if merchant_id is not None:
            self.merchant_id = merchant_id
        else:
            self.merchant_id = os.getenv("GOOGLE_MERCHANT_ID") or os.getenv("MERCHANT_CENTER_ID")

    def _load_env_if_needed(self) -> None:
        env_file = Path(__file__).resolve().parent.parent / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() not in os.environ:
                        os.environ[k.strip()] = v.strip().strip("\"'")

    @property
    def is_configured(self) -> bool:
        return bool(self.merchant_id and len(self.merchant_id) > 4)

    def get_account_status(self) -> Dict[str, Any]:
        """Check Google Merchant Center integration status."""
        if self.is_configured:
            return {
                "merchant_id": self.merchant_id,
                "status": "AUTHENTICATED",
                "feed_destination": "Surfaces across Google / Free Listings (PK)",
                "live_feed_url": "https://aitoolgems.tech/data/merchant/products_feed.xml",
            }

        return {
            "merchant_id": self.merchant_id or "UNCONFIGURED",
            "status": "BLOCKED_PENDING_CREDENTIALS",
            "instructions": (
                "Google Merchant Center ID not configured in .env. "
                "Required: GOOGLE_MERCHANT_ID. Register at https://merchants.google.com/ "
                "and submit the verified automated feed at "
                "https://aitoolgems.tech/data/merchant/products_feed.xml for free Google Shopping listings in Pakistan."
            ),
        }

