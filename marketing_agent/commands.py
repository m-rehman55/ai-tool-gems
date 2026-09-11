"""Lightweight Telegram command menu and replies."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from .config import Settings
from .telegram import TelegramClient


STATE_PATH = Path(__file__).resolve().parent / "data" / "bot-state.json"


COMMANDS = [
    {"command": "catalog", "description": "Browse all 20 tools and prices"},
    {"command": "deals", "description": "See current PKR deals"},
    {"command": "contact", "description": "Order or ask on WhatsApp"},
    {"command": "help", "description": "How this bot works"},
]


def setup_bot(settings: Settings) -> None:
    client = TelegramClient(settings.telegram_bot_token)
    client.call("setMyCommands", {"commands": COMMANDS})
    client.call("setMyDescription", {
        "description": "Browse AI tools and digital subscriptions with PKR prices, clear access terms and direct WhatsApp support from AI Tool Gems Pakistan."
    })
    client.call("setMyShortDescription", {"short_description": "AI tools in PKR with direct WhatsApp ordering."})


def _load_state(path: Path = STATE_PATH) -> dict:
    if not path.exists():
        return {"last_update_id": 0, "updated_at": None}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_state(state: dict, path: Path = STATE_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def _reply(settings: Settings, client: TelegramClient, chat_id: str, command: str) -> None:
    website = settings.site_url + "/"
    deals = settings.site_url + "/deals/"
    whatsapp = f"https://wa.me/{settings.whatsapp_number}?text={quote('Hello AI Tool Gems, I need help choosing an AI tool.')}"
    if command in {"/start", "/help"}:
        text = (
            "Welcome to AI Tool Gems Pakistan 💎\n\n"
            "Use /catalog to browse all tools, /deals for current PKR offers, or /contact for human WhatsApp support.\n\n"
            "Availability and exact access terms are confirmed before payment. Independent reseller."
        )
        client.send_message(chat_id, text, website)
    elif command == "/catalog":
        client.send_message(chat_id, "Browse all 20 AI tools and digital subscriptions with PKR prices:", website)
    elif command == "/deals":
        client.send_message(chat_id, "See current AI Tool Gems offers, access types and delivery estimates:", deals)
    elif command == "/contact":
        client.send_message(chat_id, "Talk to the AI Tool Gems team on WhatsApp for availability and ordering:", whatsapp)
    else:
        client.send_message(chat_id, "I understand /catalog, /deals, /contact and /help. Choose a command from the menu.", website)


def process_updates(settings: Settings, state_path: Path = STATE_PATH) -> int:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")
    client = TelegramClient(settings.telegram_bot_token)
    state = _load_state(state_path)
    updates = client.updates(offset=int(state.get("last_update_id", 0)) + 1)
    handled = 0
    latest = int(state.get("last_update_id", 0))
    for update in updates:
        latest = max(latest, int(update["update_id"]))
        message = update.get("message") or {}
        chat = message.get("chat") or {}
        if chat.get("type") != "private":
            continue
        command = str(message.get("text") or "").strip().split()[0].lower()
        _reply(settings, client, str(chat["id"]), command)
        handled += 1
    if latest != int(state.get("last_update_id", 0)):
        _save_state({"last_update_id": latest, "updated_at": datetime.now(settings.timezone).isoformat(timespec="seconds")}, state_path)
    return handled
