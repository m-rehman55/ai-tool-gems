#!/usr/bin/env python3
"""
Content Planner & Brief Generator for AIToolGems
------------------------------------------------
Generates evidence-backed content briefs and specifications for missing
high-value Pakistani and worldwide AI keyword clusters:
- Integrates local transactional signals (PKR, EasyPaisa, JazzCash).
- Generates structured FAQ outlines for AI Search Engine discovery.
- Specifies required internal linking destinations.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from agent.keyword_research import KeywordTarget

@dataclass
class ContentBrief:
    slug: str
    target_url: str
    primary_keyword: str
    search_intent: str
    target_market: str
    h1_title: str
    meta_description_draft: str
    suggested_h2_sections: List[str]
    faq_questions: List[str]
    internal_link_targets: List[str]
    required_local_signals: List[str] = field(default_factory=lambda: [
        "PKR Pricing table",
        "EasyPaisa & JazzCash instant checkout route",
        "Official WhatsApp support contact (+92 323 6715731)",
        "Pakistani developer/freelancer context",
    ])

class ContentPlanner:
    """Plans high-intent content expansion without cannibalization."""

    def __init__(self, base_url: str = "https://aitoolgems.tech"):
        self.base_url = base_url.rstrip("/")

    def create_guide_brief(self, target: KeywordTarget) -> ContentBrief:
        kw = target.primary_keyword
        slug = kw.lower().replace(" ", "-").replace("?", "").replace("/", "")
        url = f"{self.base_url}/guides/{slug}/"

        h1 = f"{kw.title()} in Pakistan (Complete 2026 Guide)"
        meta_desc = f"Complete guide to {kw} in Pakistan. Learn authentic PKR pricing, EasyPaisa and JazzCash payment options, features, and instant setup for Pakistani users."

        h2_sections = [
            f"1. What is {kw.title()} and Why Pakistani Creators Need It",
            f"2. Official Pricing in PKR vs International USD Rates",
            f"3. How to Pay with EasyPaisa, JazzCash, or Local Bank Cards",
            f"4. Step-by-Step Activation and Verification Guide",
            f"5. Key Benefits for Freelancers and Developers in Pakistan",
            f"6. Frequently Asked Questions (FAQs)",
        ]

        faq_questions = [
            f"How much does {kw} cost in Pakistani Rupees (PKR)?",
            f"Can I buy {kw} using EasyPaisa or JazzCash?",
            f"How long does delivery take for Pakistani accounts?",
            f"Is this an authentic and private subscription?",
        ]

        internal_links = [
            f"{self.base_url}/",
            f"{self.base_url}/deals/",
            f"{self.base_url}/contact.html",
        ]

        return ContentBrief(
            slug=slug,
            target_url=url,
            primary_keyword=kw,
            search_intent=target.intent,
            target_market=target.market,
            h1_title=h1,
            meta_description_draft=meta_desc,
            suggested_h2_sections=h2_sections,
            faq_questions=faq_questions,
            internal_link_targets=internal_links,
        )
