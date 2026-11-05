"""Representative Templates and URLs for Performance Auditing."""

from __future__ import annotations

from typing import Dict, List

REPRESENTATIVE_TEMPLATES: List[Dict[str, str]] = [
    {
        "template_id": "homepage",
        "url": "https://aitoolgems.tech/",
        "description": "Primary landing page with 3D carousel, hero search, and category grid",
        "priority": "HIGH",
    },
    {
        "template_id": "product_tool",
        "url": "https://aitoolgems.tech/tools/chatgpt/",
        "description": "Individual tool product page with PKR pricing and trust badges",
        "priority": "HIGH",
    },
    {
        "template_id": "prices_directory",
        "url": "https://aitoolgems.tech/prices/",
        "description": "Complete Pakistan AI tools price list table",
        "priority": "MEDIUM",
    },
    {
        "template_id": "guide_article",
        "url": "https://aitoolgems.tech/guides/students/",
        "description": "Long-form educational buyer's guide and comparison",
        "priority": "MEDIUM",
    },
]


def get_representative_urls() -> List[str]:
    return [t["url"] for t in REPRESENTATIVE_TEMPLATES]

