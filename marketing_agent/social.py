"""Audience-led organic content for AI Tool Gems' owned social channels."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date, datetime, time
from pathlib import Path

from .catalog import Product, get_product, load_products
from .config import Settings
from .telegram import TelegramClient
from .tracking import deals_url, tracking_code


STATE_PATH = Path(__file__).resolve().parent / "data" / "social-state.json"
CAMPAIGN_EPOCH = date(2026, 9, 12)
SOCIAL_SLOTS = ("morning", "evening")


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

COMPANION_ROTATION = (
    "capcut", "canva", "chatgpt", "veo", "leonardo", "elevenlabs",
    "adobe", "figma", "lovable", "replit", "notion", "gamma", "n8n",
    "windows", "youtube", "linkedin", "nordvpn", "surfshark", "netflix",
)


def deals_for_slot(day: date, slot: str) -> tuple[Product, Product, Product]:
    """Return Gemini plus two unique companions for one of the day's two campaigns."""
    if slot not in SOCIAL_SLOTS:
        raise ValueError(f"Unsupported social slot: {slot}")
    products = {product.id: product for product in load_products()}
    gemini = products.get("gemini") or get_product("gemini")
    ordered = [products[product_id] for product_id in COMPANION_ROTATION if product_id in products]
    ordered.extend(
        product for product in products.values()
        if product.id != "gemini" and product.id not in COMPANION_ROTATION
    )
    if len(ordered) < 2:
        raise RuntimeError("The social catalog needs at least two products in addition to Gemini")
    slot_offset = SOCIAL_SLOTS.index(slot) * 2
    offset = ((day - CAMPAIGN_EPOCH).days * 4 + slot_offset) % len(ordered)
    return gemini, ordered[offset], ordered[(offset + 1) % len(ordered)]


def deals_of_the_day(day: date) -> tuple[Product, Product, Product]:
    """Backwards-compatible alias for the morning selection."""
    return deals_for_slot(day, "morning")


def deal_of_the_day(day: date) -> Product:
    """Return the rotating focus product used to select a relevant audience."""
    return deals_of_the_day(day)[1]


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


def hashtags_for(products: tuple[Product, ...], audience: AudienceAngle, platform: str, day: date) -> str:
    """Rotate a compact relevance bank; avoid spammy tags that do not target buyers."""
    index = max(0, (day - CAMPAIGN_EPOCH).days)
    focus = products[1] if len(products) > 1 else products[0]
    tags = ["AIToolGems", "AIToolsPakistan", "GeminiPakistan", _product_tag(focus)]
    tags.append(audience.hashtags[index % len(audience.hashtags)])
    category_tags = CATEGORY_TAGS.get(focus.category, ("DigitalTools",))
    tags.append(category_tags[index % len(category_tags)])
    tags.append(DISCOVERY_TAGS[index % len(DISCOVERY_TAGS)])
    limits = {"facebook": 3, "instagram": 6, "tiktok": 6}
    return " ".join(f"#{tag}" for tag in tags[: limits.get(platform, 5)])


def _deal_line(index: int, product: Product, detailed: bool = False) -> str:
    saving = f" | Save Rs. {product.saving:,}" if product.saving else ""
    line = (
        f"{index}. {product.name.upper()}\n"
        f"   PRICE: Rs. {product.price:,} | {product.duration}{saving}"
    )
    if detailed:
        line += f"\n   ACCESS: {product.access} | DELIVERY: {product.delivery} | WARRANTY: {product.warranty}"
    return line


def _deal_body(
    products: tuple[Product, ...],
    audience: AudienceAngle,
    slot: str,
    detailed: bool = False,
) -> str:
    rows = "\n\n".join(_deal_line(index, product, detailed) for index, product in enumerate(products, 1))
    return f"{audience.hook}\n\n{slot.upper()} PICKS — 3 HANDPICKED DEALS\n\n{rows}"


def _instagram(products: tuple[Product, ...], audience: AudienceAngle, url: str, day: date, slot: str) -> str:
    return (
        f"{slot.upper()} AI TOOL DEALS FOR PAKISTAN 🇵🇰\n\n"
        f"{_deal_body(products, audience, slot)}\n\n"
        "Gemini is included in every daily selection. Prices are listed clearly so you can compare first.\n\n"
        "📲 WHATSAPP: +92 323 6715731\n"
        f"View all 3 deals and order: {url}\n\n"
        f"{hashtags_for(products, audience, 'instagram', day)}\n\n"
        "Promotional listing by AI Tool Gems Pakistan. Independent reseller; brand names belong to their owners."
    )


def _facebook(products: tuple[Product, ...], audience: AudienceAngle, url: str, day: date, slot: str) -> str:
    return (
        f"{slot.upper()} — 3 DIGITAL TOOL DEALS\n\n"
        f"{_deal_body(products, audience, slot, detailed=True)}\n\n"
        "Compare the plan, access type, delivery estimate and warranty before ordering. "
        "Current availability and exact terms are confirmed before payment.\n\n"
        "WHATSAPP: +92 323 6715731\n"
        f"View all offers + order: {url}\n\n"
        f"{hashtags_for(products, audience, 'facebook', day)}\n\n"
        "Promotional listing by AI Tool Gems Pakistan. Independent reseller."
    )


def _whatsapp(products: tuple[Product, ...], audience: AudienceAngle, url: str, day: date, slot: str) -> str:
    return (
        f"💎 {slot.upper()} — 3 AI TOOL DEALS\n\n"
        f"{_deal_body(products, audience, slot)}\n\n"
        "Order: +92 323 6715731\n"
        f"Details: {url}"
    )


def _tiktok(products: tuple[Product, ...], audience: AudienceAngle, url: str, day: date, slot: str) -> str:
    return (
        f"{slot.upper()} — 3 AI TOOL DEALS 🇵🇰\n\n"
        f"{_deal_body(products, audience, slot)}\n\n"
        "WhatsApp: +92 323 6715731\n"
        f"Details/order: {url}\n\n"
        f"{hashtags_for(products, audience, 'tiktok', day)}\n\n"
        "Promotional listing by AI Tool Gems Pakistan. Independent reseller. Check terms before payment."
    )


def _reel_script(products: tuple[Product, ...], audience: AudienceAngle, url: str, slot: str) -> str:
    if slot == "morning":
        return (
            "Morning photo-post plan\n"
            "One readable 4:5 card with all three official product logos and exact PKR prices.\n"
            f"Target audience: {audience.label}\n"
            f"Caption link: {url}\n"
            "No audio: this slot is intentionally a photo post."
        )
    return (
        f"Platform-paced photorealistic {slot} Reel/TikTok plan\n"
        f"Hook: {audience.hook}\n"
        f"Reveal 1: {products[0].name} — Rs. {products[0].price:,}\n"
        f"Reveal 2: {products[1].name} — Rs. {products[1].price:,}\n"
        f"Reveal 3: {products[2].name} — Rs. {products[2].price:,}\n"
        "Final scene: all three deals + pulsing WhatsApp +92 323 6715731\n"
        f"Target audience: {audience.label}\n"
        f"Caption link: {url}\n"
        "Motion: daily orbit/portal/radar/glass-card concept with kinetic price reveals.\n"
        "Audio: platform-shaped original commercial-safe soundbed. Native library trend music requires "
        "the destination platform's own editor and cannot be attached by Buffer automatic publishing."
    )


def caption_for_platform(
    settings: Settings,
    day: date,
    platform: str,
    audience: AudienceAngle | None = None,
    slot: str = "morning",
) -> str:
    """Build one tracked caption containing Gemini and two rotating offers."""
    products = deals_for_slot(day, slot)
    focus = products[1]
    audience = audience or audience_for(focus, day)
    builders = {
        "instagram": _instagram,
        "facebook": _facebook,
        "whatsapp": _whatsapp,
        "tiktok": _tiktok,
    }
    if platform not in builders:
        raise ValueError(f"Unsupported social platform: {platform}")
    campaign_id = "-".join(product.id for product in products)
    code = tracking_code(platform, campaign_id, day.strftime("%Y%m%d"), f"{slot}-{audience.id}")
    target = deals_url(settings.site_url, tuple(product.id for product in products), code, platform, slot)
    return builders[platform](products, audience, target, day, slot)


def daily_pack(settings: Settings, day: date) -> list[str]:
    messages = [
        f"📣 AI Tool Gems campaign — {day.isoformat()}\n"
        "Two campaigns: MORNING + EVENING\n"
        "Each campaign: Gemini Pro + two rotating deals\n"
        "Morning: rotating-layout photo. Evening: kinetic platform-paced video with commercial-safe audio."
    ]
    platform_builders = (
        ("INSTAGRAM", "instagram", _instagram),
        ("FACEBOOK", "facebook", _facebook),
        ("WHATSAPP STATUS", "whatsapp", _whatsapp),
    )
    for slot in SOCIAL_SLOTS:
        products = deals_for_slot(day, slot)
        audience = audience_for(products[1], day)
        for label, platform, builder in platform_builders:
            campaign_id = "-".join(product.id for product in products)
            code = tracking_code(platform, campaign_id, day.strftime("%Y%m%d"), f"{slot}-{audience.id}")
            target = deals_url(settings.site_url, tuple(product.id for product in products), code, platform, slot)
            messages.append(
                f"{slot.upper()} {label} — 3 DEALS\n\n"
                f"{builder(products, audience, target, day, slot)}"
            )
        campaign_id = "-".join(product.id for product in products)
        code = tracking_code("tiktok", campaign_id, day.strftime("%Y%m%d"), f"{slot}-{audience.id}")
        target = deals_url(settings.site_url, tuple(product.id for product in products), code, "tiktok", slot)
        media_label = "TIKTOK/PHOTO" if slot == "morning" else "TIKTOK/REEL"
        messages.append(
            f"{slot.upper()} {media_label} — 3 DEALS\n\n"
            f"{_tiktok(products, audience, target, day, slot)}\n\n"
            f"{_reel_script(products, audience, target, slot)}"
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


def send_automation_failure_alert(settings: Settings) -> None:
    if not settings.owner_reports_ready:
        raise RuntimeError("Owner Telegram credentials are missing")
    TelegramClient(settings.telegram_bot_token).send_with_retry(
        settings.telegram_owner_chat_id,
        "⚠️ AI Tool Gems social campaign needs attention.\n\n"
        "A daily check, media build, or Buffer publishing step failed. No automatic retry will create a duplicate. "
        "Open the latest GitHub Actions run, read the failed step, and reconnect only the affected channel if requested.\n\n"
        "Actions: https://github.com/m-rehman55/ai-tool-gems/actions",
    )
