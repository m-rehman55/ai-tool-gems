"""Top 10 Monitored Competitors Registry for Pakistan & South Asia."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass
class CompetitorProfile:
    domain: str
    business_name: str
    primary_market: str  # Pakistan, South Asia, Global
    currency: str
    payment_rails: List[str]
    access_model: str    # Private Accounts, Shared/Group Buy, Voucher Codes
    known_tools_count: int
    strengths: List[str]
    weaknesses: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


TOP_10_COMPETITORS: List[CompetitorProfile] = [
    CompetitorProfile(
        domain="aitoolspak.tech",
        business_name="AI Tools Pak",
        primary_market="Pakistan",
        currency="PKR",
        payment_rails=["EasyPaisa", "JazzCash"],
        access_model="Shared / Group Buy",
        known_tools_count=35,
        strengths=["Aggressive local marketing", "Fast WhatsApp response"],
        weaknesses=["High account logout frequency", "No public replacement policy"],
    ),
    CompetitorProfile(
        domain="paktools.store",
        business_name="PakTools Store",
        primary_market="Pakistan",
        currency="PKR",
        payment_rails=["EasyPaisa", "JazzCash", "Bank Transfer"],
        access_model="Private & Shared",
        known_tools_count=28,
        strengths=["Established domain history", "SEO bundle offerings"],
        weaknesses=["Outdated 2024 pricing listed on some pages", "Slower delivery during peak hours"],
    ),
    CompetitorProfile(
        domain="digitaltools.com.pk",
        business_name="Digital Tools PK",
        primary_market="Pakistan",
        currency="PKR",
        payment_rails=["EasyPaisa", "JazzCash"],
        access_model="Shared",
        known_tools_count=22,
        strengths=["Low entry price points"],
        weaknesses=["Cookie extension required", "No individual tool landing pages"],
    ),
    CompetitorProfile(
        domain="zippersells.com",
        business_name="Zipper Sells",
        primary_market="Pakistan",
        currency="PKR",
        payment_rails=["EasyPaisa", "SadaPay"],
        access_model="Private Subscriptions",
        known_tools_count=18,
        strengths=["Clean UI", "Focus on premium accounts"],
        weaknesses=["Higher prices than market average", "Limited catalog depth"],
    ),
    CompetitorProfile(
        domain="groupseotoolz.com",
        business_name="Group SEO Toolz",
        primary_market="Pakistan / South Asia",
        currency="PKR / USD",
        payment_rails=["JazzCash", "Crypto", "Wise"],
        access_model="Group Buy System",
        known_tools_count=45,
        strengths=["Large portfolio of traditional SEO tools (Ahrefs/Semrush)"],
        weaknesses=["Cloud portal downtime", "Limited generative AI models (no Midjourney v6/Claude 3.5)"],
    ),
    CompetitorProfile(
        domain="toolzbuy.com",
        business_name="Toolz Buy",
        primary_market="Worldwide / South Asia",
        currency="USD / INR / PKR",
        payment_rails=["Cards", "Crypto", "Local Wallets"],
        access_model="Group Buy",
        known_tools_count=50,
        strengths=["Regional presence", "Automated portal"],
        weaknesses=["Complex setup process", "Frequent IP bans"],
    ),
    CompetitorProfile(
        domain="codesforever.com",
        business_name="Codes Forever",
        primary_market="Worldwide / Global",
        currency="USD",
        payment_rails=["Stripe", "PayPal", "Crypto"],
        access_model="License Keys & Vouchers",
        known_tools_count=60,
        strengths=["Instant digital code delivery"],
        weaknesses=["High USD exchange rates for Pakistanis", "Pakistani debit cards often declined"],
    ),
    CompetitorProfile(
        domain="grouptoolz.com",
        business_name="Group Toolz",
        primary_market="Worldwide / Global",
        currency="USD",
        payment_rails=["Crypto", "Wise"],
        access_model="Shared Portal",
        known_tools_count=40,
        strengths=["Old domain age"],
        weaknesses=["No local Pakistani payment methods", "Generic support"],
    ),
    CompetitorProfile(
        domain="seotoolzbundle.com",
        business_name="SEO Toolz Bundle",
        primary_market="Worldwide & Pakistan",
        currency="PKR / USD",
        payment_rails=["JazzCash", "EasyPaisa", "Binance Pay"],
        access_model="Combo Bundles",
        known_tools_count=30,
        strengths=["Cost-effective bundle packages for agencies"],
        weaknesses=["Slow individual tool activation"],
    ),
    CompetitorProfile(
        domain="toolwaly.com",
        business_name="Tool Waly",
        primary_market="Pakistan & Global",
        currency="PKR",
        payment_rails=["EasyPaisa", "JazzCash", "SadaPay"],
        access_model="Private & Shared",
        known_tools_count=25,
        strengths=["Urdu/English bilingual marketing"],
        weaknesses=["Irregular inventory availability"],
    ),
]


def get_top_10_competitors() -> List[CompetitorProfile]:
    return TOP_10_COMPETITORS
