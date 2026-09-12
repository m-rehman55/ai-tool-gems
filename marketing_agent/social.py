"""Audience-led organic content for AI Tool Gems' owned social channels."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path

from .catalog import Product, load_products
from .config import Settings
from .telegram import TelegramClient
from .tracking import product_url, tracking_code


STATE_PATH = Path(__file__).resolve().parent / "data" / "social-state.json"
CAMPAIGN_EPOCH = date(2026, 9, 12)


@dataclass(frozen=True)
class AudienceAngle:
    id: str
    label: str
    hook: str
    hashtags: tuple[str, ...]
    pakistan_time: time


AUDIENCES = {
    "students": AudienceAngle(
        "students",
        "university students and learners",
        "Assignments, research aur presentations ko smarter banana hai?",
        ("PakistanStudents", "UniversityLifePakistan", "StudySmart"),
        time(19, 30),
    ),
    "creators": AudienceAngle(
        "creators",
        "content creators and young professionals",
        "Content ko faster create aur polish karna hai?",
        ("PakistanCreators", "ContentCreatorsPakistan", "CreatorTools"),
        time(20, 30),
    ),
    "developers": AudienceAngle(
        "developers",
        "developers, freelancers and startup builders",
        "Coding, client work ya next MVP ko speed up karna hai?",
        ("DevelopersPakistan", "FreelancersPakistan", "BuildInPublicPakistan"),
        time(21, 0),
    ),
    "office": AudienceAngle(
        "office",
        "office teams and business professionals",
        "Office workload, documents aur team tasks ko simplify karna hai?",
        ("PakistanProfessionals", "OfficeProductivity", "WorkSmarter"),
        time(18, 30),
    ),
    "career": AudienceAngle(
        "career",
        "job seekers, sales teams and professionals",
        "Career, learning aur professional growth ko boost karna hai?",
        ("PakistanJobs", "CareerGrowthPakistan", "YoungProfessionals"),
        time(19, 0),
    ),
    "privacy": AudienceAngle(
        "privacy",
        "remote workers, travellers and privacy-conscious users",
        "Online privacy aur secure access ko simple rakhna hai?",
        ("DigitalPakistan", "OnlinePrivacy", "RemoteWorkPakistan"),
        time(20, 0),
    ),
    "entertainment": AudienceAngle(
        "entertainment",
        "students, families and entertainment fans",
        "Study ya work ke baad entertainment setup upgrade karna hai?",
        ("PakistanEntertainment", "StreamingPakistan", "DigitalLifestyle"),
        time(21, 30),
    ),
}

PRODUCT_AUDIENCES = {
    "chatgpt": ("students", "developers", "office"),
    "gemini": ("students", "office"),
    "veo": ("creators",),
    "leonardo": ("creators",),
    "elevenlabs": ("creators",),
    "canva": ("students", "creators"),
    "figma": ("developers", "creators"),
    "capcut": ("creators",),
    "adobe": ("creators",),
    "lovable": ("developers",),
    "gamma": ("students", "office"),
    "replit": ("developers", "students"),
    "n8n": ("developers", "office"),
    "notion": ("students", "office"),
    "nordvpn": ("privacy",),
    "surfshark": ("privacy",),
    "youtube": ("entertainment", "students"),
    "netflix": ("entertainment",),
    "linkedin": ("career",),
    "windows": ("office", "students"),
}

CATEGORY_TAGS = {
    "AI Assistants": ("AITools", "ArtificialIntelligence"),
    "AI Video": ("AIVideo", "VideoCreators"),
    "AI Voice": ("AIVoice", "VoiceOver"),
    "Design": ("DesignTools", "CreativePakistan"),
    "Development": ("CodingTools", "PakistanTech"),
    "Productivity": ("ProductivityTools", "DigitalProductivity"),
    "VPN & Security": ("CyberSafety", "PrivacyTools"),
    "Entertainment": ("DigitalEntertainment", "PakistanStreaming"),
    "Business": ("BusinessTools", "PakistanBusiness"),
    "Software": ("SoftwarePakistan", "PCPakistan"),
}

DISCOVERY_TAGS = (
    "DigitalPakistan",
    "TechPakistan",
    "AIPakistan",
    "FutureOfWorkPK",
)


def deal_of_the_day(day: date) -> Product:
    """Rotate the full catalog indefinitely with one consistent cross-platform deal."""
    products = load_products()
    return products[(day - CAMPAIGN_EPOCH).days % len(products)]


def audience_for(product: Product, day: date) -> AudienceAngle:
    """Pick a relevant audience deterministically so repeated product cycles test new angles."""
    choices = PRODUCT_AUDIENCES.get(product.id, ("creators", "students", "office"))
    cycle = max(0, (day - CAMPAIGN_EPOCH).days) // max(1, len(load_products()))
    return AUDIENCES[choices[cycle % len(choices)]]


def audience_candidates(product: Product) -> tuple[AudienceAngle, ...]:
    choices = PRODUCT_AUDIENCES.get(product.id, ("creators", "students", "office"))
    return tuple(AUDIENCES[choice] for choice in choices)


def _product_tag(product: Product) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]", "", product.name)
    return f"{cleaned}Pakistan"[:38]


def hashtags_for(product: Product, audience: AudienceAngle, platform: str, day: date) -> str:
    """Rotate a compact relevance bank; avoid spammy tags that do not target buyers."""
    index = max(0, (day - CAMPAIGN_EPOCH).days)
    tags = ["AIToolGems", "AIToolsPakistan", _product_tag(product)]
    tags.append(audience.hashtags[index % len(audience.hashtags)])
    category_tags = CATEGORY_TAGS.get(product.category, ("DigitalTools",))
    tags.append(category_tags[index % len(category_tags)])
    tags.append(DISCOVERY_TAGS[index % len(DISCOVERY_TAGS)])
    limits = {"facebook": 3, "instagram": 6, "tiktok": 6}
    return " ".join(f"#{tag}" for tag in tags[: limits.get(platform, 5)])


def _deal_body(product: Product, audience: AudienceAngle) -> str:
    saving = (
        f"\nLISTED SAVING: Rs. {product.saving:,} ({product.discount_percent}% vs old listed price)"
        if product.saving else ""
    )
    return (
        f"{audience.hook}\n\n"
        f"💎 {product.name.upper()}\n"
        f"PRICE: Rs. {product.price:,}\n"
        f"PLAN: {product.duration}\n"
        f"ACCESS: {product.access}\n"
        f"DELIVERY: {product.delivery}\n"
        f"BEST FOR: {', '.join(product.best_for)}"
        f"{saving}"
    )


def _instagram(product: Product, audience: AudienceAngle, url: str, day: date) -> str:
    return (
        "PAKISTAN AI TOOL DEAL 🇵🇰\n\n"
        f"{_deal_body(product, audience)}\n\n"
        "✅ Current availability and exact terms are confirmed before payment.\n"
        f"📲 View details and order: {url}\n\n"
        f"{hashtags_for(product, audience, 'instagram', day)}\n\n"
        "Promotional listing by AI Tool Gems Pakistan. Independent reseller; brand names belong to their owners."
    )


def _facebook(product: Product, audience: AudienceAngle, url: str, day: date) -> str:
    return (
        "TODAY'S DIGITAL TOOL DEAL\n\n"
        f"{_deal_body(product, audience)}\n"
        f"WARRANTY LISTING: {product.warranty}\n\n"
        "Availability, eligibility and exact access terms are checked before payment.\n"
        f"Details + WhatsApp order: {url}\n\n"
        f"{hashtags_for(product, audience, 'facebook', day)}\n\n"
        "Promotional listing by AI Tool Gems Pakistan. Independent reseller."
    )


def _whatsapp(product: Product, audience: AudienceAngle, url: str, day: date) -> str:
    saving = f"\nSAVE: Rs. {product.saving:,} ({product.discount_percent}%)" if product.saving else ""
    return (
        f"💎 {product.name}\n"
        f"PRICE: Rs. {product.price:,}\n"
        f"{saving.lstrip()}\n"
        f"{product.duration} • {product.access} access\n"
        f"Delivery: {product.delivery}\n"
        f"Best for: {', '.join(product.best_for)}\n"
        f"Details & order: {url}"
    )


def _tiktok(product: Product, audience: AudienceAngle, url: str, day: date) -> str:
    saving = f"\nLISTED SAVING: Rs. {product.saving:,} ({product.discount_percent}%)" if product.saving else ""
    return (
        f"{audience.hook}\n\n"
        f"💎 {product.name}\n"
        f"PRICE: Rs. {product.price:,} | {product.duration}{saving}\n"
        f"Best for: {', '.join(product.best_for)}\n"
        f"Details/order: {url}\n\n"
        f"{hashtags_for(product, audience, 'tiktok', day)}\n\n"
        "Promotional listing by AI Tool Gems Pakistan. Independent reseller. Check terms before payment."
    )


def _reel_script(product: Product, audience: AudienceAngle, url: str) -> str:
    return (
        "8-second Reel/TikTok plan\n"
        f"0–2s: {audience.hook}\n"
        f"2–5s: {product.name} + PRICE Rs. {product.price:,}\n"
        f"5–7s: {product.duration} + {product.access} access\n"
        "7–8s: View details / order on WhatsApp\n"
        f"Target audience: {audience.label}\n"
        f"Caption link: {url}\n"
        "Audio: original copyright-safe brand sound; no unlicensed music or guaranteed-result claims."
    )


def caption_for_platform(
    settings: Settings,
    day: date,
    platform: str,
    audience: AudienceAngle | None = None,
) -> str:
    """Build one tracked, audience-specific caption for the daily catalog product."""
    product = deal_of_the_day(day)
    audience = audience or audience_for(product, day)
    builders = {
        "instagram": _instagram,
        "facebook": _facebook,
        "whatsapp": _whatsapp,
        "tiktok": _tiktok,
    }
    if platform not in builders:
        raise ValueError(f"Unsupported social platform: {platform}")
    code = tracking_code(platform, product.id, day.strftime("%Y%m%d"), audience.id)
    target = product_url(settings.site_url, product.id, code, platform)
    return builders[platform](product, audience, target, day)


def daily_pack(settings: Settings, day: date) -> list[str]:
    product = deal_of_the_day(day)
    audience = audience_for(product, day)
    messages = [
        f"📣 AI Tool Gems campaign — {day.isoformat()}\n"
        f"Featured product: {product.name}\n"
        f"Audience: {audience.label}\n"
        f"Primary Pakistan posting window: {audience.pakistan_time.strftime('%H:%M')} PKT\n"
        "Automatic posts use original copyright-safe audio where video is scheduled."
    ]
    platform_builders = (
        ("INSTAGRAM", "instagram", _instagram),
        ("FACEBOOK", "facebook", _facebook),
        ("WHATSAPP STATUS", "whatsapp", _whatsapp),
    )
    for label, platform, builder in platform_builders:
        code = tracking_code(platform, product.id, day.strftime("%Y%m%d"), audience.id)
        target = product_url(settings.site_url, product.id, code, platform)
        messages.append(f"{label} — {product.name}\n\n{builder(product, audience, target, day)}")
    code = tracking_code("tiktok", product.id, day.strftime("%Y%m%d"), audience.id)
    target = product_url(settings.site_url, product.id, code, "tiktok")
    messages.append(
        f"TIKTOK/REEL — {product.name}\n\n{_tiktok(product, audience, target, day)}\n\n"
        f"{_reel_script(product, audience, target)}"
    )
    return messages


def send_daily_pack(settings: Settings, day: date, state_path: Path = STATE_PATH) -> int:
    state = {"sent_dates": {}}
    if state_path.exists():
        state = json.loads(state_path.read_text(encoding="utf-8"))
    sent_dates = state.setdefault("sent_dates", {})
    if day.isoformat() in sent_dates:
        return 0
    if not settings.owner_reports_ready:
        raise RuntimeError("Owner Telegram credentials are missing")
    client = TelegramClient(settings.telegram_bot_token)
    messages = daily_pack(settings, day)
    for message in messages:
        client.send_with_retry(settings.telegram_owner_chat_id, message)
    sent_dates[day.isoformat()] = {
        "sent_at": datetime.now(settings.timezone).isoformat(timespec="seconds"),
        "messages": len(messages),
    }
    state_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = state_path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    temporary.replace(state_path)
    return len(messages)
