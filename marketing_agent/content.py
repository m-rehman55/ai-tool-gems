"""Deterministic, no-paid-LLM content engine with rotation and deduplication."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Iterable

from .catalog import Product, load_products
from .config import Settings
from .db import connect, utc_now
from .tracking import product_url, tracking_code


SEGMENTS = ("students", "creators", "developers", "professionals", "small businesses")
ANGLES = ("workflow", "local value", "use case", "comparison", "clear access")
POSTING_TIMES = (time(9, 15), time(13, 30), time(18, 45), time(20, 30))

OPENERS = {
    "students": "Study smarter without guessing the plan details.",
    "creators": "A cleaner creator workflow starts with the right tool.",
    "developers": "Ship faster with a tool matched to the actual workflow.",
    "professionals": "Upgrade your daily workflow with clear access terms.",
    "small businesses": "Give your team useful software without unclear pricing.",
}


@dataclass(frozen=True)
class Draft:
    product_id: str
    segment: str
    angle: str
    variant: str
    caption: str
    caption_hash: str
    tracking_code: str
    target_url: str
    scheduled_at: str


def _caption(product: Product, segment: str, angle: str, target_url: str, variant: str) -> str:
    best_for = ", ".join(product.best_for[:3])
    saving_line = f"Save Rs. {product.saving:,} against the previous listing price.\n" if product.saving else ""
    if variant == "A":
        lead = f"💎 {product.name} for {segment}\n{OPENERS[segment]}"
        details = (
            f"\n\nBest for: {best_for}\n"
            f"Price: Rs. {product.price:,} | {product.duration}\n"
            f"Access: {product.access} | Delivery: {product.delivery}\n"
            f"{saving_line}Replacement warranty: {product.warranty}"
        )
    else:
        lead = f"✨ Need {best_for}? Consider {product.name}."
        details = (
            f"\n\nRs. {product.price:,} for {product.duration}\n"
            f"{product.access} access • {product.delivery} delivery\n"
            f"{saving_line}Clear {product.warranty} replacement-warranty listing."
        )
    disclosure = (
        "\n\nCheck current availability and exact terms before payment:\n"
        f"{target_url}\n\n"
        "Independent reseller; not affiliated with or endorsed by the listed brand."
    )
    return f"{lead}{details}{disclosure}"[:3900]


def _least_used_products(settings: Settings, count: int, seed: str) -> list[Product]:
    products = load_products()
    random.Random(seed).shuffle(products)
    with connect(settings.database_path) as connection:
        usage = {
            row["product_id"]: row["uses"]
            for row in connection.execute("SELECT product_id, COUNT(*) AS uses FROM posts GROUP BY product_id")
        }
    return sorted(products, key=lambda product: usage.get(product.id, 0))[:count]


def build_drafts(settings: Settings, day: date, count: int | None = None) -> list[Draft]:
    amount = count or settings.posts_per_day
    products = _least_used_products(settings, amount, day.isoformat())
    drafts: list[Draft] = []
    for index, product in enumerate(products):
        segment = SEGMENTS[(day.toordinal() + index) % len(SEGMENTS)]
        angle = ANGLES[(day.toordinal() * 2 + index) % len(ANGLES)]
        variant = "A" if (day.toordinal() + index) % 2 == 0 else "B"
        code = tracking_code("telegram", product.id, day.strftime("%Y%m%d"), variant)
        target = product_url(settings.site_url, product.id, code)
        caption = _caption(product, segment, angle, target, variant)
        digest = hashlib.sha256(" ".join(caption.lower().split()).encode("utf-8")).hexdigest()
        local_dt = datetime.combine(day, POSTING_TIMES[index % len(POSTING_TIMES)], settings.timezone)
        drafts.append(Draft(
            product_id=product.id, segment=segment, angle=angle, variant=variant,
            caption=caption, caption_hash=digest, tracking_code=code,
            target_url=target, scheduled_at=local_dt.isoformat(timespec="seconds"),
        ))
    return drafts


def save_drafts(settings: Settings, drafts: Iterable[Draft], auto_approve: bool | None = None) -> tuple[int, int]:
    approved = settings.auto_approve if auto_approve is None else auto_approve
    inserted = duplicates = 0
    with connect(settings.database_path) as connection:
        for draft in drafts:
            try:
                connection.execute(
                    """
                    INSERT INTO posts(product_id,platform,segment,angle,variant,caption,caption_hash,
                      tracking_code,target_url,status,scheduled_at,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (draft.product_id, "telegram", draft.segment, draft.angle, draft.variant,
                     draft.caption, draft.caption_hash, draft.tracking_code, draft.target_url,
                     "scheduled" if approved else "draft", draft.scheduled_at, utc_now()),
                )
                inserted += 1
            except Exception as exc:
                if "UNIQUE constraint failed" not in str(exc):
                    raise
                duplicates += 1
    return inserted, duplicates


def generate_days(settings: Settings, start: date, days: int, auto_approve: bool | None = None) -> tuple[int, int]:
    inserted = duplicates = 0
    for offset in range(max(1, days)):
        campaign_day = start + timedelta(days=offset)
        with connect(settings.database_path) as connection:
            existing = connection.execute(
                "SELECT COUNT(*) FROM posts WHERE platform='telegram' AND substr(scheduled_at,1,10)=?",
                (campaign_day.isoformat(),),
            ).fetchone()[0]
        if existing:
            duplicates += existing
            continue
        day_inserted, day_duplicates = save_drafts(
            settings, build_drafts(settings, campaign_day), auto_approve
        )
        inserted += day_inserted
        duplicates += day_duplicates
    return inserted, duplicates
