"""Duplicate-safe three-day Telegram campaign for GitHub-hosted execution."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import date, datetime, timedelta
from pathlib import Path

from .catalog import Product, load_products
from .config import Settings
from .content import ANGLES, OPENERS, POSTING_TIMES, SEGMENTS
from .telegram import TelegramClient
from .tracking import product_url, tracking_code


TRIAL_START = date.fromisoformat(os.getenv("ATG_TRIAL_START", "2026-09-12"))
TRIAL_DAYS = 3
LEDGER_PATH = Path(__file__).resolve().parent / "data" / "trial-ledger.json"


def _atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def _ledger(path: Path = LEDGER_PATH) -> dict:
    if not path.exists():
        return {"trial_start": TRIAL_START.isoformat(), "trial_days": TRIAL_DAYS, "claims": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _slot_product(day: date, slot: int) -> Product:
    products = load_products()
    offset = (day - TRIAL_START).days
    return products[(offset * 3 + slot) % len(products)]


def _caption(product: Product, segment: str, target: str, variant: str) -> str:
    best_for = ", ".join(product.best_for[:3])
    saving = f"Save Rs. {product.saving:,} vs our previous listing price.\n" if product.saving else ""
    if variant == "A":
        opening = f"💎 {product.name} for {segment}\n{OPENERS[segment]}"
    else:
        opening = f"✨ Looking for {best_for}? See the current {product.name} listing."
    return (
        f"{opening}\n\n"
        f"Best for: {best_for}\n"
        f"Price: Rs. {product.price:,} | {product.duration}\n"
        f"Access: {product.access} | Delivery: {product.delivery}\n"
        f"{saving}Replacement warranty: {product.warranty}\n\n"
        "Check availability and exact terms before payment:\n"
        f"{target}\n\n"
        "Independent reseller; not affiliated with or endorsed by the listed brand."
    )


def build_slot(settings: Settings, day: date, slot: int) -> dict:
    if slot not in (0, 1, 2):
        raise ValueError("Trial slot must be 0, 1, or 2")
    day_offset = (day - TRIAL_START).days
    if day_offset not in range(TRIAL_DAYS):
        raise ValueError(f"Date must be within {TRIAL_START} to {TRIAL_START + timedelta(days=TRIAL_DAYS - 1)}")
    product = _slot_product(day, slot)
    segment = SEGMENTS[(day.toordinal() + slot) % len(SEGMENTS)]
    angle = ANGLES[(day.toordinal() * 2 + slot) % len(ANGLES)]
    variant = "A" if (day.toordinal() + slot) % 2 == 0 else "B"
    code = tracking_code("telegram", product.id, day.strftime("%Y%m%d"), f"t{slot + 1}{variant}")
    target = product_url(settings.site_url, product.id, code)
    caption = _caption(product, segment, target, variant)
    scheduled = datetime.combine(day, POSTING_TIMES[slot], settings.timezone).isoformat(timespec="seconds")
    return {
        "key": f"{day.isoformat()}-slot-{slot + 1}", "date": day.isoformat(), "slot": slot,
        "scheduled_at": scheduled, "product_id": product.id, "product_name": product.name,
        "segment": segment, "angle": angle, "variant": variant, "caption": caption,
        "caption_hash": hashlib.sha256(caption.encode("utf-8")).hexdigest(),
        "tracking_code": code, "target_url": target,
    }


def trial_plan(settings: Settings) -> list[dict]:
    return [build_slot(settings, TRIAL_START + timedelta(days=day), slot)
            for day in range(TRIAL_DAYS) for slot in range(3)]


def claim_slot(settings: Settings, day: date, slot: int, payload_path: Path, ledger_path: Path = LEDGER_PATH) -> dict | None:
    payload = build_slot(settings, day, slot)
    ledger = _ledger(ledger_path)
    if payload["key"] in ledger["claims"]:
        return None
    ledger["claims"][payload["key"]] = {
        "status": "claimed", "claimed_at": datetime.now(settings.timezone).isoformat(timespec="seconds"),
        "product_id": payload["product_id"], "tracking_code": payload["tracking_code"],
    }
    _atomic_json(ledger_path, ledger)
    _atomic_json(payload_path, payload)
    return payload


def publish_payload(settings: Settings, payload_path: Path, ledger_path: Path = LEDGER_PATH) -> dict:
    if not settings.telegram_ready:
        raise RuntimeError("Telegram channel credentials are missing")
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    client = TelegramClient(settings.telegram_bot_token)
    response = client.send_with_retry(settings.telegram_channel_id, payload["caption"], payload["target_url"])
    ledger = _ledger(ledger_path)
    claim = ledger["claims"][payload["key"]]
    claim.update({
        "status": "published", "published_at": datetime.now(settings.timezone).isoformat(timespec="seconds"),
        "message_id": response["message_id"],
    })
    _atomic_json(ledger_path, ledger)
    if settings.owner_reports_ready:
        client.send_with_retry(
            settings.telegram_owner_chat_id,
            f"✅ Trial post published\n{payload['product_name']}\nSlot: {payload['key']}\nTracking: {payload['tracking_code']}",
            payload["target_url"],
        )
    return payload


def send_trial_report(settings: Settings, day: date, ledger_path: Path = LEDGER_PATH) -> bool:
    """Send one honest end-of-day report from data the bot can actually verify."""
    if not settings.owner_reports_ready:
        raise RuntimeError("Owner Telegram credentials are missing")
    ledger = _ledger(ledger_path)
    reports = ledger.setdefault("reports", {})
    if day.isoformat() in reports:
        return False
    claims = [row for key, row in ledger.get("claims", {}).items() if key.startswith(day.isoformat())]
    published = [row for row in claims if row.get("status") == "published"]
    client = TelegramClient(settings.telegram_bot_token)
    members = client.member_count(settings.telegram_channel_id) if settings.telegram_channel_id else 0
    codes = ", ".join(row["tracking_code"] for row in published) or "none"
    body = (
        f"📊 AI Tool Gems trial report — {day.isoformat()}\n\n"
        f"Telegram posts published: {len(published)}/3\n"
        f"Current channel members: {members}\n"
        f"Tracking codes: {codes}\n\n"
        "Clicks, WhatsApp inquiries, orders and revenue are not guessed. Count only real source codes "
        "received in customer WhatsApp messages, then add confirmed results to your campaign record."
    )
    client.send_with_retry(settings.telegram_owner_chat_id, body)
    reports[day.isoformat()] = {
        "sent_at": datetime.now(settings.timezone).isoformat(timespec="seconds"),
        "published_posts": len(published), "channel_members": members,
    }
    _atomic_json(ledger_path, ledger)
    return True
