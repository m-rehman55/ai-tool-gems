"""Verified Facts Loader and Truth Checker for AI Tool Gems Backlink Agent."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

PACKAGE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = PACKAGE_DIR / "config"
JSON_FACTS_PATHS = [PACKAGE_DIR / "verified_facts.json", CONFIG_DIR / "verified_facts.json"]
YAML_FACTS_PATHS = [PACKAGE_DIR / "verified_facts.yml", CONFIG_DIR / "verified_facts.yml"]


class VerifiedFacts:
    """Provides access to owner-approved facts and truth verification."""

    def __init__(self, data: Optional[Dict[str, Any]] = None):
        if data is None:
            data = self._load_default()
        self._data = data

    @classmethod
    def _load_default(cls) -> Dict[str, Any]:
        for p in JSON_FACTS_PATHS:
            if p.exists():
                return json.loads(p.read_text(encoding="utf-8"))
        for p in YAML_FACTS_PATHS:
            if p.exists():
                try:
                    import yaml  # type: ignore
                    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
                except ImportError:
                    pass
        raise FileNotFoundError(f"Verified facts not found in {PACKAGE_DIR}")

    @property
    def brand_name(self) -> str:
        return self._data.get("entity", {}).get("brand_name", "AI Tool Gems")

    @property
    def website_url(self) -> str:
        return self._data.get("entity", {}).get("website_url", "https://aitoolgems.tech")

    @property
    def primary_market(self) -> str:
        return self._data.get("scope", {}).get("primary_market", "Pakistan")

    @property
    def pricing_model(self) -> str:
        return self._data.get("scope", {}).get("pricing_model", "")

    @property
    def catalog_tools_count(self) -> int:
        return int(self._data.get("scope", {}).get("catalog_tools_count", 40))

    @property
    def verified_payment_rails_pk(self) -> List[str]:
        return list(self._data.get("verified_payment_rails", {}).get("pakistan", []))

    @property
    def disallowed_claims(self) -> List[str]:
        return list(self._data.get("disallowed_claims", []))

    def validate_copy(self, text: str) -> List[str]:
        """Adversarial check of proposed copy or pitch against disallowed claims."""
        violations = []
        lowered = text.lower()
        if "stripe" in lowered or "paypal" in lowered:
            violations.append("Disallowed gateway claimed (Stripe/PayPal)")
        if "credit card gateway" in lowered or "checkout via visa" in lowered:
            violations.append("Automated credit card gateway checkout claimed")
        if "reciprocal" in lowered or "badge" in lowered:
            violations.append("Reciprocal link/badge exchange mention")
        if "official partner of openai" in lowered or "endorsed by anthropic" in lowered:
            violations.append("Unauthorized partner endorsement claimed")
        return violations

    def as_dict(self) -> Dict[str, Any]:
        return dict(self._data)


_DEFAULT_FACTS: Optional[VerifiedFacts] = None


def get_verified_facts() -> VerifiedFacts:
    global _DEFAULT_FACTS
    if _DEFAULT_FACTS is None:
        _DEFAULT_FACTS = VerifiedFacts()
    return _DEFAULT_FACTS
