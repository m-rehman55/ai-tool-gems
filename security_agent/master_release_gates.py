"""
Master Release Gates Enforcement Module (Section 21).
Enforces the 7 mandatory release gates before any product page or commercial offer
can become release-eligible:

1. Resale/usage rights: Verified authorization or legitimate rights.
2. Offer accuracy: Exact plan, access, price, currency, term, stock and renewal facts.
3. Delivery and warranty: Realistic, evidenced customer-facing conditions.
4. Content quality: Original, useful, accurate and source-backed content.
5. Technical quality: Correct URL, canonical, HTTP status, sitemap and schema.
6. Analytics/privacy: Tested event handling and applicable privacy controls.
7. Human approval: Required owner review is recorded.

Rule 1: If any gate is unresolved -> keep HOLD.
Rule 2: If a hard gate fails -> use BLOCKED.
Rule 3: Never auto-approve a product just because a script or AI agent generated a page.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class GateStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    UNRESOLVED = "UNRESOLVED"


class ReleaseEligibility(str, Enum):
    RELEASE_ELIGIBLE = "RELEASE_ELIGIBLE"
    HOLD = "HOLD"
    BLOCKED = "BLOCKED"


HARD_FAIL_KEYWORDS = [
    "otp verification",
    "virtual number",
    "aged webmail",
    "aged accounts",
    "clone accounts",
    "fake engagement",
    "fake followers",
    "follower growth",
    "paypal verified",
    "bybit verified",
    "onlyfans balance",
    "mb bank voucher",
    "region limit resolution",
    "test placeholders",
]


@dataclass
class GateEvaluationResult:
    catalog_id: str
    product_name: str
    eligibility: ReleaseEligibility
    gates: Dict[str, GateStatus]
    blocking_reasons: List[str] = field(default_factory=list)
    unresolved_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "catalog_id": self.catalog_id,
            "product_name": self.product_name,
            "eligibility": self.eligibility.value,
            "gates": {k: v.value for k, v in self.gates.items()},
            "blocking_reasons": self.blocking_reasons,
            "unresolved_reasons": self.unresolved_reasons,
        }


class MasterReleaseGatesEngine:
    """Evaluates and enforces the 7 Master Release Gates across products and offers."""

    GATE_NAMES = [
        "resale_usage_rights",
        "offer_accuracy",
        "delivery_warranty",
        "content_quality",
        "technical_quality",
        "analytics_privacy",
        "human_approval",
    ]

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent

    def evaluate_product(self, row: Dict[str, Any]) -> GateEvaluationResult:
        """Evaluate a product record against all 7 gates."""
        cat_id = row.get("catalog_id", "").strip()
        name = row.get("canonical_parent_tool", "").strip() or row.get("name", "").strip()
        desc = (row.get("description", "") + " " + row.get("notes", "")).lower()

        # Hard failure checks (prohibited domains)
        combined_text = f"{cat_id} {name} {desc}".lower()
        blocking_reasons = []
        for kw in HARD_FAIL_KEYWORDS:
            if kw in combined_text:
                blocking_reasons.append(f"Hard policy gate violation: detected prohibited keyword '{kw}'")

        if blocking_reasons:
            return GateEvaluationResult(
                catalog_id=cat_id,
                product_name=name,
                eligibility=ReleaseEligibility.BLOCKED,
                gates={g: GateStatus.FAIL for g in self.GATE_NAMES},
                blocking_reasons=blocking_reasons,
            )

        # Gate evaluations
        gates: Dict[str, GateStatus] = {}
        unresolved_reasons = []

        # 1. Resale / Usage Rights
        resale_status = (row.get("resale_authorization_status") or row.get("gate_resale_rights") or "").strip().upper()
        if resale_status in ["PASS", "VERIFIED", "DIRECT_AUTHORIZED", "FAIR_USE_NOMINATIVE"]:
            gates["resale_usage_rights"] = GateStatus.PASS
        elif resale_status in ["FAIL", "PROHIBITED"]:
            gates["resale_usage_rights"] = GateStatus.FAIL
            blocking_reasons.append("Resale authorization failed or prohibited.")
        else:
            gates["resale_usage_rights"] = GateStatus.UNRESOLVED
            unresolved_reasons.append("Resale/usage rights pending formal verification.")

        # 2. Offer Accuracy
        offer_status = (row.get("offer_status") or row.get("gate_offer_truth") or "").strip().upper()
        price = str(row.get("retail_pkr") or row.get("price") or "").strip()
        if offer_status in ["PASS", "VERIFIED"] and price and price != "0":
            gates["offer_accuracy"] = GateStatus.PASS
        elif offer_status in ["BLOCKED", "FAIL"]:
            gates["offer_accuracy"] = GateStatus.FAIL
            blocking_reasons.append("Offer details failed accuracy audit.")
        else:
            gates["offer_accuracy"] = GateStatus.UNRESOLVED
            unresolved_reasons.append("Offer details (plan, price, currency, stock) unresolved.")

        # 3. Delivery and Warranty
        deliv = (row.get("delivery") or row.get("schema_shipping_delivery_match") or "").strip().lower()
        warr = (row.get("warranty") or "").strip().lower()
        if "physical" in deliv:
            gates["delivery_warranty"] = GateStatus.FAIL
            blocking_reasons.append("Invalid physical shipping schema on digital subscription.")
        elif ("whatsapp" in deliv or "payment confirmation" in deliv or "digital" in deliv) and warr:
            gates["delivery_warranty"] = GateStatus.PASS
        else:
            gates["delivery_warranty"] = GateStatus.UNRESOLVED
            unresolved_reasons.append("Evidenced delivery timing or replacement warranty unresolved.")

        # 4. Content Quality
        content_status = (row.get("content_review_status") or row.get("gate_content_quality") or "").strip().upper()
        if content_status in ["PASS", "APPROVED", "VERIFIED"]:
            gates["content_quality"] = GateStatus.PASS
        elif content_status in ["FAIL", "REJECTED"]:
            gates["content_quality"] = GateStatus.FAIL
            blocking_reasons.append("Content quality rejected or copied text detected.")
        else:
            gates["content_quality"] = GateStatus.UNRESOLVED
            unresolved_reasons.append("Content quality, sources, and comparison citations unresolved.")

        # 5. Technical Quality
        tech_status = (row.get("canonical_status") or row.get("gate_technical_indexability") or "").strip().upper()
        if tech_status in ["PASS", "VERIFIED", "CLEAN"]:
            gates["technical_quality"] = GateStatus.PASS
        elif tech_status in ["FAIL", "BROKEN"]:
            gates["technical_quality"] = GateStatus.FAIL
            blocking_reasons.append("Technical indexing or schema canonical failure.")
        else:
            gates["technical_quality"] = GateStatus.UNRESOLVED
            unresolved_reasons.append("Technical quality or sitemap indexability unresolved.")

        # 6. Analytics and Privacy
        ga4_status = (row.get("ga4_implementation_status") or row.get("gate_analytics_privacy") or "").strip().upper()
        if ga4_status in ["PASS", "VERIFIED", "CLEAN"]:
            gates["analytics_privacy"] = GateStatus.PASS
        elif ga4_status in ["FAIL", "PII_LEAK"]:
            gates["analytics_privacy"] = GateStatus.FAIL
            blocking_reasons.append("Analytics privacy violation or unverified order protocol.")
        else:
            gates["analytics_privacy"] = GateStatus.UNRESOLVED
            unresolved_reasons.append("Analytics event tracking and privacy consent unresolved.")

        # 7. Human Approval (STRICT: Never auto-approve)
        approver = (row.get("approved_by") or row.get("gate_human_approval") or "").strip()
        if approver and approver.lower() not in ["none", "pending", "unapproved", "ai_agent"]:
            gates["human_approval"] = GateStatus.PASS
        else:
            gates["human_approval"] = GateStatus.UNRESOLVED
            unresolved_reasons.append("Human approval by named owner is required. AI cannot auto-approve.")

        # Determine overall eligibility
        if any(v == GateStatus.FAIL for v in gates.values()) or blocking_reasons:
            eligibility = ReleaseEligibility.BLOCKED
        elif all(v == GateStatus.PASS for v in gates.values()):
            eligibility = ReleaseEligibility.RELEASE_ELIGIBLE
        else:
            eligibility = ReleaseEligibility.HOLD

        return GateEvaluationResult(
            catalog_id=cat_id,
            product_name=name,
            eligibility=eligibility,
            gates=gates,
            blocking_reasons=blocking_reasons,
            unresolved_reasons=unresolved_reasons,
        )

    def audit_register(self, register_path: Optional[Path] = None) -> List[GateEvaluationResult]:
        """Audit all rows in the master register CSV against the 7 gates."""
        path = register_path or (self.base_dir / "data" / "AIToolGems_175_Tool_Register_v2_2.csv")
        results = []
        if not path.exists():
            return results

        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                res = self.evaluate_product(row)
                results.append(res)

        return results
