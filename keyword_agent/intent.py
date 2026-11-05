"""
intent.py - 8-Way Search Intent Intelligence & Classification Engine.

Implements the 8 distinct search intents mandated by HERMES:
1. INFORMATIONAL: How-to, tutorials, prompts, guides, explanations.
2. COMMERCIAL_INVESTIGATION: Best, reviews, top, comparisons, features, pros and cons.
3. TRANSACTIONAL: Buy, purchase, price, cost, subscription, discount, license, pkr.
4. NAVIGATIONAL: Login, portal, sign in, official site, account, download app.
5. LOCAL: Pakistan, PKR, rupees, Lahore, Karachi, Islamabad, EasyPaisa, JazzCash, SadaPay.
6. COMPARISON: vs, versus, compare, alternative, difference between.
7. BRAND: aitoolgems, ai tool gems, aitoolgems.tech.
8. QUESTION: Question words (what, how, why, when, where, can i, is it, how much, kahan, kese).

Provides multi-label detection: each query has a primary intent and secondary intent tags.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class SearchIntentType(str, Enum):
    INFORMATIONAL = "informational"
    COMMERCIAL_INVESTIGATION = "commercial_investigation"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"
    LOCAL = "local"
    COMPARISON = "comparison"
    BRAND = "brand"
    QUESTION = "question"


@dataclass
class IntentClassificationResult:
    query: str
    primary_intent: SearchIntentType
    secondary_intents: List[SearchIntentType] = field(default_factory=list)
    confidence: float = 1.0
    matched_patterns: Dict[str, List[str]] = field(default_factory=dict)
    is_pakistan_local: bool = False
    is_commercial_or_transactional: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "primary_intent": self.primary_intent.value,
            "secondary_intents": [i.value for i in self.secondary_intents],
            "confidence": round(self.confidence, 2),
            "matched_patterns": self.matched_patterns,
            "is_pakistan_local": self.is_pakistan_local,
            "is_commercial_or_transactional": self.is_commercial_or_transactional,
        }


class IntentClassifier:
    """Classifies search intent with high precision across 8 dimensions."""

    # Brand identifiers
    BRAND_PATTERNS = [
        r"(?i)\b(aitoolgems|ai\s*tool\s*gems|aitoolgems\.tech)\b",
    ]

    # Question markers (English & Roman Urdu)
    QUESTION_PATTERNS = [
        r"(?i)^(how|what|why|when|where|which|who|can\s+i|is\s+it|does|do\s+we|how\s+much|how\s+many)\b",
        r"(?i)\b(how\s+to|what\s+is|why\s+choose|kahan\s+se|kese|kaise|kia\s+hai|kya\s+hai)\b",
        r"\?$",
    ]

    # Comparison markers
    COMPARISON_PATTERNS = [
        r"(?i)\b(vs\.?|versus|compare|comparison|alternative|alternatives|difference\s+between|better\s+than|or)\b",
    ]

    # Local Pakistani markers
    LOCAL_PATTERNS = [
        r"(?i)\b(pakistan|pakistani|lahore|karachi|islamabad|rawalpindi|faisalabad|peshawar|multan|quetta)\b",
        r"(?i)\b(easypaisa|jazzcash|sadapay|nayapay|raast|bank\s+ibft|in\s+pkr|in\s+rupees|rupees?|rs\.?)\b",
        r"(?i)\b(sasta|qimat|rate\s+in\s+pakistan)\b",
    ]

    # Transactional purchase markers
    TRANSACTIONAL_PATTERNS = [
        r"(?i)\b(buy|purchase|price|pricing|cost|subscribe|subscription|order|license|key|voucher|coupon|promo|discount|cheap|deal|rates?|fee)\b",
        r"(?i)\b(shared\s+account|private\s+account|activation|lifetime)\b",
    ]

    # Commercial investigation markers
    COMMERCIAL_PATTERNS = [
        r"(?i)\b(best|top|review|reviews|worth\s+it|features|pros\s+and\s+cons|overview|analysis|workflow|tools\s+for)\b",
    ]

    # Navigational markers
    NAVIGATIONAL_PATTERNS = [
        r"(?i)\b(login|log\s+in|sign\s+in|signin|portal|dashboard|official\s+site|official\s+website|app\s+download|download\s+apk|download\s+for\s+pc)\b",
    ]

    # Informational markers
    INFORMATIONAL_PATTERNS = [
        r"(?i)\b(tutorial|guide|documentation|docs|setup|prompts?|instructions?|steps|learn|tips|examples?|workflow)\b",
    ]

    @classmethod
    def classify(cls, query: str) -> IntentClassificationResult:
        """
        Evaluates query against all 8 intents and returns structured classification.
        Precedence hierarchy for primary intent:
        1. Brand (exact brand queries need dedicated brand handling)
        2. Transactional (direct commercial transaction is highest business value)
        3. Comparison (vs / comparison queries require comparison guides)
        4. Question (questions need direct AEO answer blocks)
        5. Commercial Investigation (best / review queries)
        6. Navigational (login / portal queries)
        7. Local (when purely geographic/currency focus without explicit transactional verb)
        8. Informational (fallback for exploratory queries)
        """
        q = query.strip()
        matched: Dict[SearchIntentType, List[str]] = {}

        def _test_patterns(patterns: List[str], intent_type: SearchIntentType):
            for pat in patterns:
                m = re.findall(pat, q)
                if m:
                    matched.setdefault(intent_type, []).append(pat)

        _test_patterns(cls.BRAND_PATTERNS, SearchIntentType.BRAND)
        _test_patterns(cls.QUESTION_PATTERNS, SearchIntentType.QUESTION)
        _test_patterns(cls.COMPARISON_PATTERNS, SearchIntentType.COMPARISON)
        _test_patterns(cls.LOCAL_PATTERNS, SearchIntentType.LOCAL)
        _test_patterns(cls.TRANSACTIONAL_PATTERNS, SearchIntentType.TRANSACTIONAL)
        _test_patterns(cls.COMMERCIAL_PATTERNS, SearchIntentType.COMMERCIAL_INVESTIGATION)
        _test_patterns(cls.NAVIGATIONAL_PATTERNS, SearchIntentType.NAVIGATIONAL)
        _test_patterns(cls.INFORMATIONAL_PATTERNS, SearchIntentType.INFORMATIONAL)

        detected_intents = list(matched.keys())
        is_pakistan = SearchIntentType.LOCAL in detected_intents

        # Determine primary intent
        primary: SearchIntentType
        if SearchIntentType.BRAND in detected_intents:
            primary = SearchIntentType.BRAND
        elif SearchIntentType.TRANSACTIONAL in detected_intents:
            primary = SearchIntentType.TRANSACTIONAL
        elif SearchIntentType.COMPARISON in detected_intents:
            primary = SearchIntentType.COMPARISON
        elif SearchIntentType.QUESTION in detected_intents:
            primary = SearchIntentType.QUESTION
        elif SearchIntentType.COMMERCIAL_INVESTIGATION in detected_intents:
            primary = SearchIntentType.COMMERCIAL_INVESTIGATION
        elif SearchIntentType.NAVIGATIONAL in detected_intents:
            primary = SearchIntentType.NAVIGATIONAL
        elif SearchIntentType.LOCAL in detected_intents:
            primary = SearchIntentType.LOCAL
        elif SearchIntentType.INFORMATIONAL in detected_intents:
            primary = SearchIntentType.INFORMATIONAL
        else:
            primary = SearchIntentType.INFORMATIONAL

        secondary = [i for i in detected_intents if i != primary]

        # Confidence is high if primary matches explicit lexical trigger
        confidence = 0.95 if detected_intents else 0.60
        is_commercial = primary in (
            SearchIntentType.TRANSACTIONAL,
            SearchIntentType.COMMERCIAL_INVESTIGATION,
            SearchIntentType.COMPARISON,
        ) or SearchIntentType.TRANSACTIONAL in secondary

        return IntentClassificationResult(
            query=q,
            primary_intent=primary,
            secondary_intents=secondary,
            confidence=confidence,
            matched_patterns={k.value: v for k, v in matched.items()},
            is_pakistan_local=is_pakistan,
            is_commercial_or_transactional=is_commercial,
        )
