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
        "template_id": "product_chatgpt",
        "url": "https://aitoolgems.tech/tools/chatgpt/",
        "description": "ChatGPT Plus product page with PKR pricing and trust badges",
        "priority": "HIGH",
    },
    {
        "template_id": "product_claude",
        "url": "https://aitoolgems.tech/tools/claude/",
        "description": "Claude Pro product page with Sonnet 3.5 specs and domestic payment details",
        "priority": "HIGH",
    },
    {
        "template_id": "product_canva",
        "url": "https://aitoolgems.tech/tools/canva/",
        "description": "Canva Pro product page with annual team invite details",
        "priority": "HIGH",
    },
    {
        "template_id": "product_midjourney",
        "url": "https://aitoolgems.tech/tools/midjourney/",
        "description": "Midjourney v6.1 product page with Discord activation instructions",
        "priority": "HIGH",
    },
    {
        "template_id": "product_cursor",
        "url": "https://aitoolgems.tech/tools/cursor/",
        "description": "Cursor AI Pro product page with developer workflow specifications",
        "priority": "HIGH",
    },
    {
        "template_id": "prices_directory",
        "url": "https://aitoolgems.tech/prices/",
        "description": "Complete Pakistan AI tools price list table directory",
        "priority": "MEDIUM",
    },
    {
        "template_id": "guide_article",
        "url": "https://aitoolgems.tech/guides/students/",
        "description": "Long-form educational buyer's guide and comparison",
        "priority": "MEDIUM",
    },
    {
        "template_id": "category_hub",
        "url": "https://aitoolgems.tech/categories/ai-video/",
        "description": "AI Video Tools category hub and comparative selection guide",
        "priority": "MEDIUM",
    },
]


def get_representative_urls() -> List[str]:
    return [t["url"] for t in REPRESENTATIVE_TEMPLATES]

