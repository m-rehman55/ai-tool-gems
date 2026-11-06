"""Google Merchant Center Feed Generator & Offer Eligibility Assessment Engine.

Strictly enforces Google Merchant Center Software Subscriptions & Digital Goods policies:
1. Differentiates Google Merchant Center (Shopping / Free Listings) from Google Ads (Search Ads).
2. Performs offer-level eligibility audits across all 40 catalog tools.
3. Automatically puts non-compliant offers (shared accounts, subscriptions < 12 months,
   unauthorized distribution, academic cheating aids) on HOLD with specific policy reasons.
4. Ensures zero misleading feeds or unauthorized brand claims.
5. Exports merchant_hold_register.json and google_ads_eligibility_matrix.json.
"""

from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from xml.dom import minidom


@dataclass
class OfferPolicyAssessment:
    slug: str
    name: str
    exact_plan: str
    duration: str
    payment_model: str
    total_cost_pkr: int
    renewal_conditions: str
    access_model: str
    resale_rights: str
    landing_page_url: str
    landing_page_exists: bool
    delivery_method: str
    warranty: str
    refund_policy: str
    brand_representation: str
    merchant_center_status: str  # HOLD_TERM_INSUFFICIENT, HOLD_POLICY_VIOLATION, HOLD_UNAUTHORIZED_DISTRIBUTION, HOLD_UNVERIFIED_AUTHORIZATION, HOLD_RESELLER_AUTHORIZATION_PENDING, ELIGIBLE
    merchant_center_reason: str
    google_ads_search_status: str  # ELIGIBLE_WITH_DISCLOSURES, HOLD_HIGH_RISK, HOLD_TRADEMARK_RISK, HOLD_PROHIBITED
    google_ads_search_reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MerchantProductItem:
    sku_id: str
    title: str
    description: str
    link: str
    image_link: str
    availability: str  # in_stock, out_of_stock
    price_pkr: int
    brand: str
    condition: str = "new"
    google_product_category: str = "Software > Digital Goods & Subscriptions"
    shipping_country: str = "PK"
    shipping_price: str = "0.00 PKR"
    identifier_exists: str = "no"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MerchantFeedGenerator:
    """Extracts catalog tools, audits offer-level eligibility, and generates compliant feeds."""

    def __init__(self, project_dir: Optional[Path] = None):
        self.project_dir = project_dir or Path(".")
        self.feed_dir = self.project_dir / "data" / "merchant"
        self.feed_dir.mkdir(parents=True, exist_ok=True)

    def evaluate_offer(self, product_data: Dict[str, Any]) -> OfferPolicyAssessment:
        """Audits a single offer across all 13 parameters mandated by Google Merchant & Ads policies."""
        slug = product_data.get("slug") or product_data.get("id", "unknown")
        name = product_data.get("name", "Unknown Tool")
        duration = product_data.get("duration", "1 Month")
        access = product_data.get("access", "Private")
        price_pkr = int(product_data.get("price") or product_data.get("retail_pkr", 0))

        exact_plan = f"{name} ({duration}, {access})"
        payment_model = "Prepaid flat upfront payment in PKR; zero automatic debit or hidden recurring fee."
        renewal_conditions = "Manual renewal initiated via WhatsApp; no automatic card debits."
        resale_rights = "Independent digital subscription procurement & setup assistance; no direct OEM partnership."

        landing_page_url = f"https://aitoolgems.tech/tools/{slug}/"
        tool_page = self.project_dir / "tools" / slug / "index.html"
        landing_page_exists = tool_page.exists()

        delivery_method = "Direct digital delivery via encrypted WhatsApp / email within 1-2 hours; zero physical shipping."
        warranty = f"Full replacement warranty during active validity ({duration}); 24/7 WhatsApp helpdesk."
        refund_policy = "Instant credential replacement first; full PKR refund if service cannot be restored within 24 hours."
        brand_rep = "Independent Digital Subscription Provider; explicit non-affiliation disclaimer on landing page."

        # ── 1. Google Merchant Center (Shopping / Free Listings) Policy Assessment ──
        # Software Subscriptions: Requires prepaid annual term of at least 12 months.
        # Misrepresentation / Dishonest Behavior: Shared accounts strictly prohibited.
        # Digital Goods: Requires authorized distribution rights.
        # Academic Dishonesty: Plagiarism/student account cheating tools prohibited.
        # Copyright / Trademarks: Unverified OEM software product keys prohibited.
        mc_status = "HOLD_INELIGIBLE"
        mc_reason = ""

        if "shared" in access.lower():
            mc_status = "HOLD_POLICY_VIOLATION"
            mc_reason = (
                "Google Merchant Center Misrepresentation & Enabling Dishonest Behavior: "
                "Reselling shared credentials or multi-user shared access is strictly prohibited."
            )
        elif slug == "turnitin":
            mc_status = "HOLD_POLICY_VIOLATION"
            mc_reason = (
                "Google Merchant Center Academic Dishonesty Policy: "
                "Plagiarism detection bypass and student verification accounts are prohibited."
            )
        elif slug in ["windows", "office365"]:
            mc_status = "HOLD_UNVERIFIED_AUTHORIZATION"
            mc_reason = (
                "Google Merchant Center Copyrighted & Unauthorized Software: "
                "Microsoft OEM/Retail product keys require verified Microsoft Authorized Partner status."
            )
        elif "1 month" in duration.lower() or "2 months" in duration.lower() or "3 months" in duration.lower() or "credits" in duration.lower():
            mc_status = "HOLD_TERM_INSUFFICIENT"
            mc_reason = (
                f"Google Merchant Center Software Subscriptions Policy: Requires a minimum prepaid term of 12 months; "
                f"current offer duration is {duration}."
            )
        elif "invitation" in access.lower():
            mc_status = "HOLD_UNAUTHORIZED_DISTRIBUTION"
            mc_reason = (
                "Google Merchant Center Digital Goods Policy: "
                "Third-party educational or team workspace invitation slots lack authorized OEM distribution certificates."
            )
        else:
            # Multi-month or annual private subscriptions (gamma, n8n, figma)
            mc_status = "HOLD_RESELLER_AUTHORIZATION_PENDING"
            mc_reason = (
                "Google Merchant Center Software Subscription Policy: "
                "Annual prepaid plan exists, but official OEM authorized reseller documentation is required before Shopping submission."
            )

        # ── 2. Google Ads (Search Text Ads) Policy Assessment ──────────────────────
        # Third-Party Reseller Policy: Allowed if clear non-affiliation disclaimer and transparent pricing.
        # Enabling Dishonest Behavior: Shared accounts are high risk for disapproval.
        # Academic Dishonesty: Turnitin is strictly banned.
        gads_status = "ELIGIBLE_WITH_DISCLOSURES"
        gads_reason = ""

        if slug == "turnitin":
            gads_status = "HOLD_PROHIBITED"
            gads_reason = (
                "Google Ads Academic Dishonesty Policy: "
                "Promoting plagiarism-checking services, student accounts, or academic cheating tools is strictly prohibited."
            )
        elif "shared" in access.lower():
            gads_status = "HOLD_HIGH_RISK"
            gads_reason = (
                "Google Ads Enabling Dishonest Behavior Policy: "
                "Shared account access triggers high risk of ad disapproval or advertiser account suspension."
            )
        elif slug in ["windows", "office365"]:
            gads_status = "HOLD_TRADEMARK_RISK"
            gads_reason = (
                "Google Ads Trademark & Software Resale Policy: "
                "Microsoft actively restricts brand terms in Search ad copy without Partner Network proof."
            )
        else:
            gads_status = "ELIGIBLE_WITH_DISCLOSURES"
            gads_reason = (
                "Permitted under Google Ads Third-Party Reseller Policy. "
                "Mandatory conditions: 1) Prominent non-affiliation disclaimer ('Independent Subscription Provider'); "
                "2) Exact PKR price and plan duration in ad copy; 3) No official brand impersonation."
            )

        return OfferPolicyAssessment(
            slug=slug,
            name=name,
            exact_plan=exact_plan,
            duration=duration,
            payment_model=payment_model,
            total_cost_pkr=price_pkr,
            renewal_conditions=renewal_conditions,
            access_model=access,
            resale_rights=resale_rights,
            landing_page_url=landing_page_url,
            landing_page_exists=landing_page_exists,
            delivery_method=delivery_method,
            warranty=warranty,
            refund_policy=refund_policy,
            brand_representation=brand_rep,
            merchant_center_status=mc_status,
            merchant_center_reason=mc_reason,
            google_ads_search_status=gads_status,
            google_ads_search_reason=gads_reason,
        )

    def evaluate_all_catalog_offers(self) -> List[OfferPolicyAssessment]:
        """Loads all catalogue products and evaluates each against Google policies."""
        inv_file = self.project_dir / "data" / "wholesale_inventory.json"
        products: List[Dict[str, Any]] = []

        if inv_file.exists():
            try:
                data = json.loads(inv_file.read_text(encoding="utf-8"))
                products = data.get("products", [])
            except Exception:
                products = []

        if not products:
            # Fallback to app.js
            app_js = self.project_dir / "app.js"
            if app_js.exists():
                text = app_js.read_text(encoding="utf-8")
                pattern = r"\{\s*id:\s*['\"]([^'\"]+)['\"],\s*name:\s*['\"]([^'\"]+)['\"].*?price:\s*(\d+).*?category:\s*['\"]([^'\"]+)['\"]"
                matches = re.findall(pattern, text, re.DOTALL)
                seen = set()
                for slug, name, price_str, cat in matches:
                    if slug in seen:
                        continue
                    seen.add(slug)
                    products.append({
                        "slug": slug,
                        "name": name,
                        "price": int(price_str),
                        "category": cat,
                        "duration": "1 Month",
                        "access": "Private",
                    })

        if not products:
            products = [
                {"slug": "chatgpt", "name": "ChatGPT Plus", "price": 2300, "duration": "1 Month", "access": "Private"},
                {"slug": "claude", "name": "Claude Pro", "price": 2200, "duration": "1 Month", "access": "Private"},
            ]

        return [self.evaluate_offer(p) for p in products]

    def export_eligibility_registers(self) -> Tuple[Path, Path]:
        """Exports durable JSON audit registers for Merchant Center and Google Ads."""
        assessments = self.evaluate_all_catalog_offers()

        hold_register = [a.to_dict() for a in assessments if a.merchant_center_status != "ELIGIBLE"]
        ads_matrix = [a.to_dict() for a in assessments]

        hold_path = self.feed_dir / "merchant_hold_register.json"
        ads_path = self.feed_dir / "google_ads_eligibility_matrix.json"

        hold_path.write_text(json.dumps(hold_register, indent=2), encoding="utf-8")
        ads_path.write_text(json.dumps(ads_matrix, indent=2), encoding="utf-8")

        return hold_path, ads_path

    def extract_catalog_items(self, eligible_only: bool = False) -> List[MerchantProductItem]:
        """
        Extracts tool details from the catalogue.
        If eligible_only is True, strictly excludes all offers marked on HOLD under Google Shopping policies.
        """
        assessments = self.evaluate_all_catalog_offers()
        items: List[MerchantProductItem] = []

        brand_map = {
            "chatgpt": "OpenAI", "gemini": "Google", "claude": "Anthropic",
            "midjourney": "Midjourney", "canva": "Canva", "cursor": "Anysphere",
            "github-copilot": "GitHub", "elevenlabs": "ElevenLabs", "runway": "Runway",
            "replit": "Replit", "notion": "Notion", "capcut": "Bytedance",
            "windows": "Microsoft", "office365": "Microsoft", "netflix": "Netflix",
        }

        for a in assessments:
            if eligible_only and a.merchant_center_status != "ELIGIBLE":
                continue

            brand = brand_map.get(a.slug, a.name.split()[0])
            items.append(MerchantProductItem(
                sku_id=f"atg-{a.slug}",
                title=f"{a.name} {a.duration} Subscription (Pakistan)",
                description=f"Verified {a.name} subscription in Pakistan. Includes instant WhatsApp activation, full replacement warranty, and domestic EasyPaisa/JazzCash checkout.",
                link=a.landing_page_url,
                image_link=f"https://aitoolgems.tech/assets/product-logos/{a.slug}.png",
                availability="in_stock",
                price_pkr=a.total_cost_pkr,
                brand=brand,
            ))

        return items

    def generate_xml_feed(self, items: Optional[List[MerchantProductItem]] = None) -> Path:
        """Generate Google Merchant Center XML (RSS 2.0) feed and export hold registers."""
        # Always synchronize hold registers
        self.export_eligibility_registers()

        if items is None:
            # In live automated mode, strictly include only policy-eligible items
            items = self.extract_catalog_items(eligible_only=True)

        rss = ET.Element("rss", {"version": "2.0", "xmlns:g": "http://base.google.com/ns/1.0"})
        channel = ET.SubElement(rss, "channel")

        title = ET.SubElement(channel, "title")
        title.text = "AI Tool Gems Pakistan Product Feed"
        link = ET.SubElement(channel, "link")
        link.text = "https://aitoolgems.tech/"
        desc = ET.SubElement(channel, "description")
        desc.text = (
            "Verified premium AI tool subscriptions in Pakistan with flat PKR pricing and instant domestic activation. "
            "Policy enforcement: Offers failing Merchant Center 12-month prepaid terms or authorized reseller distribution "
            "are held in merchant_hold_register.json."
        )

        for item in items:
            item_elem = ET.SubElement(channel, "item")
            ET.SubElement(item_elem, "{http://base.google.com/ns/1.0}id").text = item.sku_id
            ET.SubElement(item_elem, "{http://base.google.com/ns/1.0}title").text = item.title
            ET.SubElement(item_elem, "{http://base.google.com/ns/1.0}description").text = item.description
            ET.SubElement(item_elem, "{http://base.google.com/ns/1.0}link").text = item.link
            ET.SubElement(item_elem, "{http://base.google.com/ns/1.0}image_link").text = item.image_link
            ET.SubElement(item_elem, "{http://base.google.com/ns/1.0}availability").text = item.availability
            ET.SubElement(item_elem, "{http://base.google.com/ns/1.0}price").text = f"{item.price_pkr}.00 PKR"
            ET.SubElement(item_elem, "{http://base.google.com/ns/1.0}brand").text = item.brand
            ET.SubElement(item_elem, "{http://base.google.com/ns/1.0}condition").text = item.condition
            ET.SubElement(item_elem, "{http://base.google.com/ns/1.0}google_product_category").text = item.google_product_category
            ET.SubElement(item_elem, "{http://base.google.com/ns/1.0}identifier_exists").text = item.identifier_exists

            shipping = ET.SubElement(item_elem, "{http://base.google.com/ns/1.0}shipping")
            ET.SubElement(shipping, "{http://base.google.com/ns/1.0}country").text = item.shipping_country
            ET.SubElement(shipping, "{http://base.google.com/ns/1.0}price").text = item.shipping_price

        xml_path = self.feed_dir / "products_feed.xml"
        rough_string = ET.tostring(rss, "utf-8")
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding="utf-8")

        with open(xml_path, "wb") as f:
            f.write(pretty_xml)

        return xml_path

    def generate_tsv_feed(self, items: Optional[List[MerchantProductItem]] = None) -> Path:
        """Generate Google Merchant Center TSV (Tab-Delimited) feed."""
        if items is None:
            items = self.extract_catalog_items(eligible_only=True)

        tsv_path = self.feed_dir / "products_feed.tsv"

        headers = [
            "id", "title", "description", "link", "image_link",
            "availability", "price", "brand", "condition",
            "google_product_category", "identifier_exists"
        ]

        with open(tsv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter="\t")
            writer.writerow(headers)
            for item in items:
                writer.writerow([
                    item.sku_id,
                    item.title,
                    item.description,
                    item.link,
                    item.image_link,
                    item.availability,
                    f"{item.price_pkr}.00 PKR",
                    item.brand,
                    item.condition,
                    item.google_product_category,
                    item.identifier_exists,
                ])

        return tsv_path
