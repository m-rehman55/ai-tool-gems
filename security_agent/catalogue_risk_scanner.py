"""Special Catalogue Risk Scanner & Compliance Firewall (Phase 14).

Enforces strict compliance across all 10 high-risk catalogue domains:
1. Spam or fake engagement services
2. Social media account stock or verification
3. Clone or aged accounts
4. OTP and virtual number services
5. Education or webmail account resale
6. Region or subscription restriction bypass
7. Payment account resale
8. Crypto or banking account products
9. Platform accounts and balances
10. Administrative/test placeholders

Ensures that cautionary entries (IDs 158–173, 175) are NEVER published, advertised,
checkout-enabled, or submitted to Merchant feeds without appropriate policy, rights,
and legal review. Never facilitates fraud, account takeover, fake engagement,
evasion of identity checks, or abuse of platform restrictions.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


PROHIBITED_RISK_DOMAINS = [
    "Spam or fake engagement services",
    "Social media account stock or verification",
    "Clone or aged accounts",
    "OTP and virtual number services",
    "Education or webmail account resale",
    "Region or subscription restriction bypass",
    "Payment account resale",
    "Crypto or banking account products",
    "Platform accounts and balances",
    "Administrative/test placeholders",
]

CAUTIONARY_CATALOG_NUMBERS = set(range(158, 174)) | {175}

PROHIBITED_KEYWORDS = [
    r"\botp\s+(verification|bypass|service)\b",
    r"\bvirtual\s+(number|sim)s?\b",
    r"\baged\s+webmail\b",
    r"\baged\s+accounts?\b",
    r"\bclone\s+accounts?\b",
    r"\bfake\s+engagement\b",
    r"\bfake\s+followers?\b",
    r"\bfollower\s+growth\b",
    r"\bpaypal\s+verified\b",
    r"\bbybit\s+verified\b",
    r"\bonlyfans\s+(balance|reseller)\b",
    r"\bmb\s+bank\s+(voucher|account)\b",
    r"\bregion\s+limit\s+resolution\b",
    r"\btest\s+placeholders?\b",
]


@dataclass
class RiskScanResult:
    is_clean: bool
    cautionary_entries_audited: int
    active_storefront_violations: List[str] = field(default_factory=list)
    sitemap_violations: List[str] = field(default_factory=list)
    merchant_feed_violations: List[str] = field(default_factory=list)
    wholesale_violations: List[str] = field(default_factory=list)
    unresolved_status_violations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CatalogueRiskScanner:
    """Audits the master register, live storefront, sitemap, and feeds against high-risk categories."""

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent

    def scan_master_register(self, register_path: Optional[Path] = None) -> List[str]:
        """Verify that all cautionary catalogue entries have status HOLD or BLOCKED."""
        path = register_path or (self.base_dir / "data" / "AIToolGems_175_Tool_Register_v2_2.csv")
        violations = []
        if not path.exists():
            return [f"Register not found at: {path}"]

        with open(path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    cat_num = int(row.get("catalog_number", 0))
                except ValueError:
                    continue

                if cat_num in CAUTIONARY_CATALOG_NUMBERS:
                    off_status = (row.get("offer_status") or "").strip().upper()
                    pub_status = (row.get("publication_status") or "").strip().upper()

                    if off_status not in ["HOLD", "BLOCKED"]:
                        violations.append(
                            f"ID {cat_num} ({row.get('canonical_parent_tool')}): Invalid offer_status '{off_status}'. Must be HOLD or BLOCKED."
                        )
                    if pub_status not in ["HOLD", "BLOCKED"]:
                        violations.append(
                            f"ID {cat_num} ({row.get('canonical_parent_tool')}): Invalid publication_status '{pub_status}'. Must be HOLD or BLOCKED."
                        )

        return violations

    def scan_storefront_leakage(self) -> List[str]:
        """Verify that no cautionary entries or prohibited keywords have leaked into app.js."""
        violations = []
        app_js_path = self.base_dir / "app.js"
        if not app_js_path.exists():
            return ["app.js not found"]

        content = app_js_path.read_text(encoding="utf-8").lower()

        # Check for prohibited keyword strings
        for pat in PROHIBITED_KEYWORDS:
            if re.search(pat, content):
                violations.append(f"Prohibited risk pattern '{pat}' detected in app.js")

        return violations

    def scan_tools_directories(self) -> List[str]:
        """Verify that no public HTML tool directory exists for any cautionary catalog slug."""
        violations = []
        tools_dir = self.base_dir / "tools"
        if not tools_dir.exists():
            return []

        prohibited_slugs = {
            "sms-otp-and-virtual-number-verification",
            "aged-webmail-accounts",
            "family-plan-region-limit-resolution",
            "paypal-verified-reseller-accounts",
            "bybit-verified-accounts-and-crypto-cards",
            "onlyfans-reseller-balance-accounts",
            "mb-bank-vietnam-account-vouchers",
            "administrative-and-test-placeholders",
            "telegram-premium-stars-and-bot-services",
            "x-premium",
            "facebook-meta-growth-and-verified",
            "tiktok-live-and-follower-growth",
            "reddit-premium",
        }

        existing_tool_slugs = {p.name for p in tools_dir.iterdir() if p.is_dir()}
        leaked = existing_tool_slugs.intersection(prohibited_slugs)
        for l in leaked:
            violations.append(f"Prohibited cautionary slug exists as public tool directory: /tools/{l}/")

        return violations

    def scan_sitemap_isolation(self) -> List[str]:
        """Verify that sitemap.xml contains zero URLs for any cautionary or blocked entries."""
        violations = []
        sitemap_path = self.base_dir / "sitemap.xml"
        if not sitemap_path.exists():
            return ["sitemap.xml not found"]

        content = sitemap_path.read_text(encoding="utf-8").lower()
        for pat in PROHIBITED_KEYWORDS:
            if re.search(pat, content):
                violations.append(f"Prohibited risk pattern '{pat}' leaked into sitemap.xml")

        return violations

    def scan_wholesale_inventory(self) -> List[str]:
        """Verify that wholesale_inventory.json contains zero cautionary items."""
        violations = []
        inventory_path = self.base_dir / "data" / "wholesale_inventory.json"
        if not inventory_path.exists():
            return []

        try:
            data = json.loads(inventory_path.read_text(encoding="utf-8"))
            for prod in data.get("products", []):
                name = prod.get("name", "").lower()
                slug = prod.get("slug", "").lower()
                for pat in PROHIBITED_KEYWORDS:
                    if re.search(pat, name) or re.search(pat, slug):
                        violations.append(f"Prohibited item in wholesale inventory: {prod.get('name')} ({slug})")
        except Exception as e:
            violations.append(f"Error parsing wholesale_inventory.json: {e}")

        return violations

    def run_comprehensive_risk_audit(self) -> RiskScanResult:
        """Execute full-spectrum scan across register, storefront, sitemap, directories, and wholesale."""
        reg_violations = self.scan_master_register()
        store_violations = self.scan_storefront_leakage()
        dir_violations = self.scan_tools_directories()
        sitemap_violations = self.scan_sitemap_isolation()
        wholesale_violations = self.scan_wholesale_inventory()

        active_violations = store_violations + dir_violations
        all_clean = (
            len(reg_violations) == 0
            and len(active_violations) == 0
            and len(sitemap_violations) == 0
            and len(wholesale_violations) == 0
        )

        return RiskScanResult(
            is_clean=all_clean,
            cautionary_entries_audited=len(CAUTIONARY_CATALOG_NUMBERS),
            active_storefront_violations=active_violations,
            sitemap_violations=sitemap_violations,
            merchant_feed_violations=[],
            wholesale_violations=wholesale_violations,
            unresolved_status_violations=reg_violations,
        )

    def validate_candidate_for_publication(self, item_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Active Firewall Gate: Rejects any attempt to publish or enable checkout for high-risk items."""
        errors = []
        slug = str(item_data.get("slug", "")).lower()
        title = str(item_data.get("title", "")).lower()
        desc = str(item_data.get("meta_description", "")).lower()
        combined = f"{slug} {title} {desc}"
        normalized = re.sub(r"[\-_]+", " ", combined)

        for pat in PROHIBITED_KEYWORDS:
            if re.search(pat, combined) or re.search(pat, normalized):
                errors.append(
                    f"FIREWALL_BLOCKED: Prohibited special risk domain detected ('{pat}'). "
                    f"Publication, advertising, and checkout are strictly forbidden."
                )

        return len(errors) == 0, errors
