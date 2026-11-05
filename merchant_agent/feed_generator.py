"""Google Merchant Center Feed Generator (XML & TSV).

Generates compliant Google Merchant Center product feeds for the Pakistan marketplace.
All prices are strictly in PKR, delivery is digital (0 PKR), and conditions are 'new'.
"""

from __future__ import annotations

import csv
import json
import re
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional
from xml.dom import minidom


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
    """Extracts catalog tools and generates Google Shopping feeds."""

    def __init__(self, project_dir: Optional[Path] = None):
        self.project_dir = project_dir or Path(".")
        self.feed_dir = self.project_dir / "data" / "merchant"
        self.feed_dir.mkdir(parents=True, exist_ok=True)

    def extract_catalog_items(self) -> List[MerchantProductItem]:
        """Extract tool details from app.js and static tool routes."""
        app_js = self.project_dir / "app.js"
        items: List[MerchantProductItem] = []

        if not app_js.exists():
            return self._fallback_catalog()

        text = app_js.read_text(encoding="utf-8")
        # Match tool blocks: id, name, price, brand, description
        pattern = r"\{\s*id:\s*['\"]([^'\"]+)['\"],\s*name:\s*['\"]([^'\"]+)['\"].*?price:\s*(\d+).*?category:\s*['\"]([^'\"]+)['\"]"
        matches = re.findall(pattern, text, re.DOTALL)

        seen_ids = set()
        for slug, name, price_str, cat in matches:
            if slug in seen_ids:
                continue
            seen_ids.add(slug)
            price_val = int(price_str)
            brand_map = {
                "chatgpt": "OpenAI", "gemini": "Google", "claude": "Anthropic",
                "midjourney": "Midjourney", "canva": "Canva", "cursor": "Anysphere",
                "github-copilot": "GitHub", "elevenlabs": "ElevenLabs", "runway": "Runway",
                "replit": "Replit", "notion": "Notion", "capcut": "Bytedance",
            }
            brand = brand_map.get(slug, name.split()[0])
            items.append(MerchantProductItem(
                sku_id=f"atg-{slug}",
                title=f"{name} 1-Month Subscription (Pakistan)",
                description=f"Verified {name} subscription in Pakistan. Includes instant WhatsApp activation, full replacement warranty, and domestic EasyPaisa/JazzCash checkout.",
                link=f"https://aitoolgems.tech/tools/{slug}/",
                image_link=f"https://aitoolgems.tech/assets/product-logos/{slug}.png",
                availability="in_stock",
                price_pkr=price_val,
                brand=brand,
            ))

        if not items:
            return self._fallback_catalog()
        return items

    def _fallback_catalog(self) -> List[MerchantProductItem]:
        return [
            MerchantProductItem(
                sku_id="atg-chatgpt",
                title="ChatGPT Plus 1-Month Subscription (Pakistan)",
                description="Verified ChatGPT Plus subscription in Pakistan with GPT-4o access, instant activation, and EasyPaisa/JazzCash checkout.",
                link="https://aitoolgems.tech/tools/chatgpt/",
                image_link="https://aitoolgems.tech/assets/product-logos/chatgpt.png",
                availability="in_stock",
                price_pkr=3500,
                brand="OpenAI",
            ),
            MerchantProductItem(
                sku_id="atg-claude",
                title="Claude Pro 1-Month Subscription (Pakistan)",
                description="Verified Claude Pro subscription in Pakistan with Sonnet 3.5 access, instant activation, and domestic payment support.",
                link="https://aitoolgems.tech/tools/claude/",
                image_link="https://aitoolgems.tech/assets/product-logos/claude.png",
                availability="in_stock",
                price_pkr=3800,
                brand="Anthropic",
            ),
        ]

    def generate_xml_feed(self, items: Optional[List[MerchantProductItem]] = None) -> Path:
        """Generate Google Merchant Center XML (RSS 2.0) feed."""
        items = items or self.extract_catalog_items()

        rss = ET.Element("rss", {"version": "2.0", "xmlns:g": "http://base.google.com/ns/1.0"})
        channel = ET.SubElement(rss, "channel")

        title = ET.SubElement(channel, "title")
        title.text = "AI Tool Gems Pakistan Product Feed"
        link = ET.SubElement(channel, "link")
        link.text = "https://aitoolgems.tech/"
        desc = ET.SubElement(channel, "description")
        desc.text = "Verified premium AI tool subscriptions in Pakistan with flat PKR pricing and instant domestic activation."

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
        items = items or self.extract_catalog_items()
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

