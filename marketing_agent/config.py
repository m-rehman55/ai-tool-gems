"""Configuration with a tiny dependency-free .env loader."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import timedelta, timezone, tzinfo
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


PACKAGE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PACKAGE_DIR.parent


def resolve_timezone(name: str) -> tzinfo:
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        if name == "Asia/Karachi":
            return timezone(timedelta(hours=5), name="Asia/Karachi")
        raise


def load_env(path: Path | None = None) -> None:
    env_path = path or PROJECT_DIR / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key:
            os.environ.setdefault(key, value)


@dataclass(frozen=True)
class Settings:
    database_path: Path
    site_url: str
    whatsapp_number: str
    timezone: tzinfo
    telegram_bot_token: str
    telegram_channel_id: str
    telegram_owner_chat_id: str
    posts_per_day: int
    auto_approve: bool

    @property
    def telegram_ready(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_channel_id)

    @property
    def owner_reports_ready(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_owner_chat_id)


def get_settings() -> Settings:
    load_env()
    db_default = PACKAGE_DIR / "data" / "marketing.db"
    posts = max(1, min(4, int(os.getenv("ATG_POSTS_PER_DAY", "3"))))
    return Settings(
        database_path=Path(os.getenv("ATG_DATABASE_PATH", str(db_default))).expanduser().resolve(),
        site_url=os.getenv("ATG_SITE_URL", "https://aitoolgems.tech").rstrip("/"),
        whatsapp_number="".join(c for c in os.getenv("ATG_WHATSAPP_NUMBER", "923476242709") if c.isdigit()),
        timezone=resolve_timezone(os.getenv("ATG_TIMEZONE", "Asia/Karachi")),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        telegram_channel_id=os.getenv("TELEGRAM_CHANNEL_ID", "").strip(),
        telegram_owner_chat_id=os.getenv("TELEGRAM_OWNER_CHAT_ID", "").strip(),
        posts_per_day=posts,
        auto_approve=os.getenv("ATG_AUTO_APPROVE", "false").lower() in {"1", "true", "yes"},
    )
