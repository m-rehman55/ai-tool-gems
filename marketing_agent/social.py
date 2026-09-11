"""Ready-to-share organic content for platforms without connected publishing access."""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

from .catalog import Product
from .config import Settings
from .telegram import TelegramClient
from .tracking import product_url, tracking_code
from .trial import build_slot


STATE_PATH = Path(__file__).resolve().parent / "data" / "social-state.json"


def _instagram(product: Product, url: str) -> str:
    tags = "#AIToolsPakistan #DigitalTools #PakistanCreators #ProductivityTools"
    return (
        f"{product.name} — current AI Tool Gems listing 💎\n\n"
        f"Best for: {', '.join(product.best_for)}\n"
        f"Rs. {product.price:,} | {product.duration} | {product.access} access\n"
        f"Estimated delivery: {product.delivery} | Listed warranty: {product.warranty}\n\n"
        f"Check current availability before payment: {url}\n\n{tags}\n\n"
        "Independent reseller. Brand names belong to their respective owners."
    )


def _facebook(product: Product, url: str) -> str:
    return (
        f"Need {', '.join(product.best_for[:2])}? Compare the current {product.name} listing in PKR.\n\n"
        f"Price: Rs. {product.price:,}\nDuration: {product.duration}\nAccess: {product.access}\n"
        f"Delivery estimate: {product.delivery}\nReplacement-warranty listing: {product.warranty}\n\n"
        f"Full details and WhatsApp order: {url}\n\n"
        "Availability and exact terms are confirmed before payment. Independent reseller."
    )


def _whatsapp(product: Product, url: str) -> str:
    return (
        f"💎 {product.name}\nRs. {product.price:,} • {product.duration}\n"
        f"{product.access} access • {product.delivery} delivery\n"
        f"Details & order: {url}"
    )


def _reel_script(product: Product, url: str) -> str:
    return (
        f"15-second Reel/TikTok script\n"
        f"0–3s hook: Need {product.best_for[0]} without confusing dollar prices?\n"
        f"3–8s screen: Show {product.name}, Rs. {product.price:,}, {product.duration}.\n"
        f"8–12s proof: Show {product.access} access and {product.delivery} delivery estimate.\n"
        f"12–15s CTA: Check exact terms and order from the link.\n"
        f"Caption link: {url}\n"
        "Do not claim official partnership or guaranteed results."
    )


def daily_pack(settings: Settings, day: date) -> list[str]:
    from .catalog import get_product

    messages = [f"📣 AI Tool Gems organic content pack — {day.isoformat()}\nCopy only to pages/accounts you own."]
    platform_builders = (
        ("INSTAGRAM", "instagram", _instagram), ("FACEBOOK", "facebook", _facebook),
        ("WHATSAPP STATUS", "whatsapp", _whatsapp),
    )
    for slot, (label, platform, builder) in enumerate(platform_builders):
        campaign = build_slot(settings, day, slot)
        product = get_product(campaign["product_id"])
        code = tracking_code(platform, product.id, day.strftime("%Y%m%d"), f"s{slot + 1}")
        target = product_url(settings.site_url, product.id, code, platform)
        messages.append(f"{label} — {campaign['product_name']}\n\n{builder(product, target)}")
    # A short-video script rounds out the pack without needing account credentials.
    final_campaign = build_slot(settings, day, 0)
    final_product = get_product(final_campaign["product_id"])
    code = tracking_code("tiktok", final_product.id, day.strftime("%Y%m%d"), "reel")
    target = product_url(settings.site_url, final_product.id, code, "tiktok")
    messages.append(f"REEL/TIKTOK — {final_campaign['product_name']}\n\n{_reel_script(final_product, target)}")
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
    temp = state_path.with_suffix(".tmp")
    temp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    temp.replace(state_path)
    return len(messages)
