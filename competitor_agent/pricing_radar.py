"""Competitor Pricing Radar & Parity Analysis Module."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ToolPriceComparison:
    tool_id: str
    tool_name: str
    aitoolgems_pkr: int
    competitor_prices: Dict[str, Optional[int]]  # domain -> price in PKR
    lowest_market_price: int
    highest_market_price: int
    price_position: str  # "COMPETITIVE", "PRICE_LEADER", "PREMIUM"
    notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


BENCHMARK_PRICES: List[ToolPriceComparison] = [
    ToolPriceComparison(
        tool_id="chatgpt",
        tool_name="ChatGPT Plus (GPT-4o)",
        aitoolgems_pkr=3500,
        competitor_prices={
            "aitoolspak.tech": 3800,
            "paktools.store": 3600,
            "digitaltools.com.pk": 3900,
            "zippersells.com": 4200,
        },
        lowest_market_price=3500,
        highest_market_price=4200,
        price_position="PRICE_LEADER",
        notes="AIToolGems offers lowest verified private-account price in Pakistan with instant activation.",
    ),
    ToolPriceComparison(
        tool_id="claude",
        tool_name="Claude Pro (Sonnet 3.5)",
        aitoolgems_pkr=3800,
        competitor_prices={
            "aitoolspak.tech": 4000,
            "paktools.store": 3900,
            "toolwaly.com": 4200,
        },
        lowest_market_price=3800,
        highest_market_price=4200,
        price_position="PRICE_LEADER",
        notes="Direct activation without US VPN requirement.",
    ),
    ToolPriceComparison(
        tool_id="midjourney",
        tool_name="Midjourney Standard Plan",
        aitoolgems_pkr=4000,
        competitor_prices={
            "aitoolspak.tech": 4500,
            "groupseotoolz.com": 3500,  # Shared group bot
            "paktools.store": 4200,
        },
        lowest_market_price=3500,
        highest_market_price=4500,
        price_position="COMPETITIVE",
        notes="AIToolGems provides private Discord bot invites vs shared public channels.",
    ),
    ToolPriceComparison(
        tool_id="canva",
        tool_name="Canva Pro Brand Kit",
        aitoolgems_pkr=1499,
        competitor_prices={
            "aitoolspak.tech": 1500,
            "paktools.store": 1600,
            "digitaltools.com.pk": 1200,  # Team invite
        },
        lowest_market_price=1200,
        highest_market_price=1600,
        price_position="COMPETITIVE",
        notes="Full lifetime replacement warranty included.",
    ),
]


def get_pricing_radar_report() -> List[ToolPriceComparison]:
    return BENCHMARK_PRICES

