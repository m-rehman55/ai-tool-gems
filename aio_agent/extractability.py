"""
extractability.py - Evaluates HTML Document Extractability for Google AI Overviews & RAG Grounding.
Google's Gemini Search grounding systems pull facts directly from clean, crawlable HTML.
Audits:
- Presence of direct answer summary (<p class="quick-answer"> or .answer)
- Word count bounds for AI direct citations (35 to 75 words)
- Direct fact extractability (price in PKR, payment methods, delivery terms, warranty)
- Semantic heading hierarchy (single H1, structured H2/H3s)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple


@dataclass
class ExtractabilityReport:
    file_path: str
    url_slug: str
    has_h1: bool
    h1_count: int
    h1_text: str
    has_direct_answer: bool
    direct_answer_word_count: int
    has_pkr_price: bool
    has_payment_rails: bool
    has_warranty_info: bool
    has_delivery_terms: bool
    extractability_score: float  # 0 to 100
    recommendations: List[str] = field(default_factory=list)


class ExtractabilityAuditor:
    """Audits HTML files for Google AI Overviews extractability and RAG grounding readiness."""

    def audit_file(self, file_path: Path) -> ExtractabilityReport:
        content = file_path.read_text(encoding="utf-8")
        slug = file_path.parent.name if file_path.name == "index.html" else file_path.stem

        # 1. Heading structure
        h1_matches = re.findall(r"<h1[^>]*>(.*?)</h1>", content, re.IGNORECASE | re.DOTALL)
        h1_count = len(h1_matches)
        h1_text = re.sub(r"<[^>]+>", "", h1_matches[0]).strip() if h1_matches else ""

        # 2. Direct answer check
        qa_match = re.search(
            r'<(?:p|div|section)[^>]*(?:class=["\'][^"\']*(?:quick-answer|quick-summary|quick-answer-card|answer)[^"\']*["\'])[^>]*>(.*?)</(?:p|div|section)>',
            content,
            re.IGNORECASE | re.DOTALL,
        )
        has_direct_answer = bool(qa_match)
        da_words = 0
        if qa_match:
            da_clean = re.sub(r"<[^>]+>", " ", qa_match.group(1))
            da_words = len(da_clean.split())

        # 3. Factual signals (grounding tokens)
        has_pkr = bool(re.search(r"\b(?:Rs\.?|PKR)\s*[\d,]+", content, re.IGNORECASE))
        has_payments = bool(re.search(r"\b(?:EasyPaisa|JazzCash|SadaPay|Nayapay|Bank\s+IBFT)\b", content, re.IGNORECASE))
        has_warranty = bool(re.search(r"\b(?:warranty|replacement|guarantee)\b", content, re.IGNORECASE))
        has_delivery = bool(re.search(r"\b(?:delivery|confirmation|activation|dispatch)\b", content, re.IGNORECASE))

        # 4. Scoring calculation (Max 100)
        score = 0.0
        recs: List[str] = []

        # Single H1 (20 pts)
        if h1_count == 1:
            score += 20.0
        elif h1_count == 0:
            recs.append("Missing H1 heading tag.")
        else:
            score += 10.0
            recs.append(f"Multiple H1 headings detected ({h1_count}). Google recommends a single prominent H1.")

        # Direct Answer presence & length (30 pts)
        if has_direct_answer:
            if 35 <= da_words <= 75:
                score += 30.0
            elif da_words < 35:
                score += 15.0
                recs.append(f"Direct answer box is too brief ({da_words} words). Aim for 35-70 words for full AI snippet grounding.")
            else:
                score += 20.0
                recs.append(f"Direct answer box is too verbose ({da_words} words). Keep under 75 words to prevent truncation by AI Overviews.")
        else:
            recs.append("Add a standalone direct-answer summary box (<p class=\"quick-answer\">) below the H1.")

        # Fact Extractability (50 pts total: 15 pkr, 15 payment, 10 warranty, 10 delivery)
        if has_pkr:
            score += 15.0
        else:
            recs.append("Add explicit PKR pricing in visible HTML text to satisfy commercial RAG queries.")

        if has_payments:
            score += 15.0
        else:
            recs.append("Include verified local payment rails (EasyPaisa, JazzCash, SadaPay) for transactional search intent.")

        if has_warranty:
            score += 10.0
        else:
            recs.append("Explicitly state warranty terms to improve trustworthiness signals for AI evaluation.")

        if has_delivery:
            score += 10.0
        else:
            recs.append("Clarify delivery timeline or WhatsApp order verification flow.")

        return ExtractabilityReport(
            file_path=str(file_path),
            url_slug=slug,
            has_h1=h1_count > 0,
            h1_count=h1_count,
            h1_text=h1_text,
            has_direct_answer=has_direct_answer,
            direct_answer_word_count=da_words,
            has_pkr_price=has_pkr,
            has_payment_rails=has_payments,
            has_warranty_info=has_warranty,
            has_delivery_terms=has_delivery,
            extractability_score=round(score, 1),
            recommendations=recs,
        )
